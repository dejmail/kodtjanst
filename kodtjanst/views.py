import re
import logging
from datetime import datetime, date
from kodtjanst.logging import setup_logging


from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.core import serializers
from django.urls import path 
from django.db import connection, transaction
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q


from .models import Kodverk, Kodtext, ExternaKodtext, ValidatedBy, CommentedKodverk, CodeableConceptAttributes
from .forms import UserLoginForm, VerifyKodverk, KommenteraKodverk


from io import BytesIO
import xlsxwriter


import json
from pdb import set_trace

from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout
)

logger = logging.getLogger(__name__)

RE_PATTERN = re.compile(r'\s+')

@login_required
def home(request):
    return render(request, "home.html", {})

def login_view(request):
    next = request.GET.get('next')
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        #set_trace()
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request,user)
            if next:
                return redirect(next)
            else:
                return redirect('/')

        context = {'login_form' : form}
    
    else:
        context = {'login_form' : UserLoginForm()}
        
    return render(request, "login.html", context)

def logout_view(request):
    logout(request)
    return redirect('/')

def retur_alla_kodverk(url_parameter):

    cursor = connection.cursor()
    sql_statement = f'''SELECT DISTINCT kodtjanst_kodverk.id,\
                               kodtjanst_kodverk.titel_på_kodverk,\
                               kodtjanst_kodverk.syfte\
                            FROM kodtjanst_kodverk\
                            LEFT JOIN kodtjanst_kodtext\
                                ON kodtjanst_kodtext.kodverk_id = kodtjanst_kodverk.id\
                            LEFT JOIN kodtjanst_validatedby\
                                ON kodtjanst_kodverk.id = kodtjanst_validatedby.kodverk_id\
                            LEFT JOIN kodtjanst_nyckelord\
                                on kodtjanst_kodverk.id = kodtjanst_nyckelord.kodverk_from_id\
                            WHERE kodtjanst_kodverk.status = 'Beslutad';'''

    clean_statement = re.sub(RE_PATTERN, ' ', sql_statement)

    cursor.execute(clean_statement)
    result = cursor.fetchall()
    
    return result


def retur_general_sök(url_parameter):
    cursor = connection.cursor()
    ''' 
    need to reduce the number of fields being returned, we are not using all of them,
    but this also affects the parsing as it is position based, so need to be careful
    '''

    sql_statement = f'''SELECT DISTINCT kodtjanst_kodverk.id,\
                               kodtjanst_kodverk.titel_på_kodverk,\
                               kodtjanst_kodverk.syfte\
                            FROM kodtjanst_kodverk\
                            LEFT JOIN kodtjanst_kodtext\
                                ON kodtjanst_kodtext.kodverk_id = kodtjanst_kodverk.id\
                            LEFT JOIN kodtjanst_validatedby\
                                ON kodtjanst_kodverk.id = kodtjanst_validatedby.kodverk_id\
                            LEFT JOIN kodtjanst_nyckelord\
                                on kodtjanst_kodverk.id = kodtjanst_nyckelord.kodverk_from_id\
                        WHERE (kodtjanst_kodverk.titel_på_kodverk LIKE "%{url_parameter}%"\
                        OR kodtjanst_kodverk.syfte LIKE "%{url_parameter}%"\
                        OR kodtjanst_kodverk.beskrivning_av_innehållet  LIKE "%{url_parameter}%"\
                        OR kodtjanst_nyckelord.nyckelord LIKE "%{url_parameter}%"\
                        OR kodtjanst_kodtext.kodtext LIKE "%{url_parameter}%"\
                        OR kodtjanst_kodtext.annan_kodtext LIKE "%{url_parameter}%"\
                        OR kodtjanst_kodtext.definition LIKE "%{url_parameter}%")
                        AND kodtjanst_kodverk.status = 'Aktiv';'''

    clean_statement = re.sub(RE_PATTERN, ' ', sql_statement)

    cursor.execute(clean_statement)
    result = cursor.fetchall()
    
    return result

def retur_komplett_förklaring_custom_sql(url_parameter):

    cursor = connection.cursor()
    sql_statement = f'''SELECT syfte,\
                            beskrivning_av_innehållet ,\
                            identifierare,\
                            titel_på_kodverk,\
                            ägare_till_kodverk,\
                            version,\
                            källa,\
                            version_av_källa,\
                            kategori,\
                            användning_av_kodverk,\
                            status,\
                            uppdateringsintervall,\
                            ansvarig_förvaltare,\
                            senaste_ändring,\
                            giltig_från,\
                            giltig_tom,\
                            ändrad_av_id,\
                            ansvarig_id,\
                            urval_referens_id,\
                            underlag,\
                            länk_till_underlag,\
                            kodtjanst_nyckelord.nyckelord\
                        FROM kodtjanst_kodverk\
                        LEFT JOIN kodtjanst_nyckelord\
                            on kodtjanst_kodverk.id = kodtjanst_nyckelord.kodverk_from_id\
                        LEFT JOIN kodtjanst_codeableconceptattributes\
                            on kodtjanst_kodverk.id = kodtjanst_codeableconceptattributes.kodverk_from_id\
                        WHERE kodtjanst_kodverk.id = {url_parameter};'''
    clean_statement = re.sub(RE_PATTERN, ' ', sql_statement)
    cursor.execute(clean_statement)
    result = cursor.fetchall()
    
    
#underlaginstruktion_för_kodverket,\
#mappning_för_rapportering,\


    return result


def return_kodtext_related_to_kodverk(url_parameter):

    cursor = connection.cursor()
    sql_statement = f'''SELECT id,
                               annan_kodtext,
                               definition,
                               kod,
                               kodtext,
                               position                            
                               from kodtjanst_kodtext WHERE kodtjanst_kodtext.kodverk_id = {url_parameter};'''
    cursor.execute(sql_statement)
    result = cursor.fetchall()

    return result


def attach_column_names_to_search_result(search_result, search_column_names):

    return_list_dict = []
    for return_result in search_result:
        return_list_dict.append(dict(zip(search_column_names, return_result)))
    
    return return_list_dict

def highlight_search_term_i_definition(search_term, result_dict_list):
    
    for idx, result in enumerate(result_dict_list):
        for key, value in result.items():
            if value is None:
                pass
            else:
                match = re.match(search_term, value, flags=re.IGNORECASE)
                if match:
                    
                    return_string = ''.join([value[0:match.start()],'<mark>', value[match.start():match.end()], '</mark>', value[match.end():]])
                    result_dict_list[idx].update({key : return_string})
    return result_dict_list

def make_dictionary_field_html_safe(result_list_of_dictionaries=[], fields=[]):

    for index, entry in enumerate(result_list_of_dictionaries):
        for field in fields:
            if entry.get(f'{field}') is not None:
                result_list_of_dictionaries[index].update({f'{field}' : format_html(entry.get(f'{field}'))})
    return result_list_of_dictionaries

def kodverk_sok(request):
    url_parameter = request.GET.get("q")
        
    if request.is_ajax():

        kodverk_column_names = ['id',
                        'titel_på_kodverk',
                        'syfte']

        if url_parameter == '*all':
            sql_search = retur_alla_kodverk(url_parameter)
        else:
            sql_search = retur_general_sök(url_parameter)
        
        #mäta_sök_träff(sök_term=url_parameter,sök_data=return_list_dict, request=request)
        
        search_result = attach_column_names_to_search_result(sql_search, kodverk_column_names)
        # search_result = highlight_search_term_i_definition(url_parameter, search_result)
        search_result = make_dictionary_field_html_safe(search_result, fields=['syfte'])

        html = render_to_string(
            template_name="kodverk_partial_result.html", context={'kodverk': search_result,                                                            
                                                                  'searched_for_term' : url_parameter})

        return JsonResponse(data=html, safe=False)

    # elif request.method == 'GET':
    #     data_dict, return_list_dict = hämta_data_till_begrepp_view(url_parameter)
    #     return render(request, "term-results-partial.html", context=data_dict)

    # elif request.method=='GET':
    #     return render(request, "term_forklaring.html", context=template_context)
    
    else:
        kodverk = Kodverk.objects.none()
    return render(request, "kodverk.html", {})

def convert_list_of_tuples_to_string(tuple_list, start=None, stop=None, single_position=None):

    '''
    Returns concatenated, command separated string of contents of an arbitrary 
    slicing range from of a tuple of tuples or lists of lists or just one 
    position within each list or tuple.
    '''
    
    if tuple(tuple_list)[0][0] is None:
        return ''
    if single_position is not None:
        return ', '.join([i[single_position] for i in tuple_list])
    elif (start is not None) and (stop is not None):
        return ', '.join([i[start:stop] for i in tuple_list])

def return_komplett_metadata(request, url_parameter):

    if url_parameter:
        exact_kodverk_request = retur_komplett_förklaring_custom_sql(url_parameter)
        
        nyckelord = extract_columns_from_query_and_return_set(search_result=exact_kodverk_request, 
                                                                start=-1, 
                                                                stop=0)

        nyckelord_string = convert_list_of_tuples_to_string(nyckelord, single_position=0)
        
        codeconcept_attributes = extract_columns_from_query_and_return_set(search_result=exact_kodverk_request, 
                                                                            ind_items=[4,6,7,12])

        codeconcept_column_names = ['ägare_till_kodverk',
                                    'källa',
                                    'version_av_källa', 
                                    'ansvarig_förvaltare']

        codeconcept_dict = attach_column_names_to_search_result(codeconcept_attributes,codeconcept_column_names)

        #set_trace()

        result_column_names = ['syfte',
                            'beskrivning_av_innehållet',
                            'identifierare',
                            'titel_på_kodverk',
                            'ägare_till_kodverk',
                            'version',
                            'källa',
                            'version_av_källa',
                            'kategori',
                            'användning_av_kodverk',
                            'status',
                            'uppdateringsintervall',
                            'ansvarig_förvaltare',
                            'senaste_ändring',
                            'giltig_från',
                            'giltig_tom',
                            'ändrad_av_id',
                            'ansvarig_id',
                            'urval_referens_id',
                            'underlag',
                            'länk_till_underlag',
                            'nyckelord'
                            ]
        
        return_list_dict = []
        
        for return_result in exact_kodverk_request:
            return_list_dict.append(dict(zip(result_column_names, return_result)))
        
        kodtext_search_result = return_kodtext_related_to_kodverk(url_parameter)

        kodtext_column_names = ['id',
                               'annan_kodtext',
                               'definition',
                               'kod',
                               'kodtext',
                               'position']

        kodtext_dict = attach_column_names_to_search_result(kodtext_search_result,kodtext_column_names)

        if all([kodtext['position'] for kodtext in kodtext_dict]):
            kodtext_dict = sorted(kodtext_dict, key = lambda i: i['position'])
        elif all([kodtext['kod'] for kodtext in kodtext_dict]):
            kodtext_dict = sorted(kodtext_dict, key = lambda i: i['kod'])
        else:
            kodtext_dict = sorted(kodtext_dict, key = lambda i: i['kodtext'])
        

        kodtext_dict = make_dictionary_field_html_safe(kodtext_dict, fields=['definition','kodtext'])        

        return_list_dict = make_dictionary_field_html_safe(return_list_dict, fields=['syfte', 'beskrivning_av_innehållet', 'länk_till_underlag'])           

        template_context = {'kodverk_full': return_list_dict[0],
                            'kodverk_id' : url_parameter,
                            'kodtext_full' : kodtext_dict,
                            'nyckelord' : nyckelord_string,
                            'codeconcept' : codeconcept_dict} 
        
        html = render_to_string(template_name="kodverk_komplett_metadata.html", context=template_context)

        return template_context
    else:
        return None

def kodverk_komplett_metadata(request):

    url_parameter = request.GET.get("q")
    
    if request.is_ajax():
        template_context = return_komplett_metadata(request, url_parameter) 
        return render(request, "kodverk_komplett_metadata.html", context=template_context)
    elif request.method == 'GET':
        template_context = return_komplett_metadata(request, url_parameter) 
        return render(request, "kodverk_komplett_metadata_direct_get.html", context=template_context)
    else:
        kodverk = Kodverk.objects.none()
        return render(request, "kodverk.html", {'kodverk': kodverk})


def extract_columns_from_query_and_return_set(search_result, **kwargs):

    reduced_list = []
    for record in search_result:
        if kwargs.get('ind_items'):
            temp_list = []
            for i in kwargs.get('ind_items'):
                temp_list.append(record[i])
            reduced_list.append(temp_list)
        if kwargs.get('start')==0:
            reduced_list.append(record[:kwargs.get('stop')])
        elif kwargs.get('stop')==0:
            reduced_list.append(record[kwargs.get('start'):])
        elif kwargs.get('start') and kwargs.get('stop'):
            reduced_list.append(record[kwargs.get('start'):kwargs.get('stop')])
   
    reduced_set = set([tuple(i) for i in reduced_list])
    return reduced_set

def return_kodtext_as_json(request):

    url_parameter = request.GET.get("q")
    
    if (request.is_ajax()) or (request.method == 'GET'):
    
        kodtext = Kodtext.objects.filter(kodverk_id=int(url_parameter))
               
        post_kodtext = serializers.serialize('json', kodtext)
   
        return HttpResponse(post_kodtext)

def return_translation_text(request):

    translation_string =  {"sEmptyTable": "Inga data",
                          "sInfoThousands": ".",
                          "sInfo": "Visar _START_ till _END_ av _TOTAL_ resultat",
                          "sLengthMenu": "_MENU_ Antal rader",
                            "sInfoEmpty": "0 Visar 0 av 0 resultat",
                          "sLoadingRecords": "Kodtext laddar...",
                          "sProcessing": "Arbetar...",
                          "sSearch": "Sök",
                          "sZeroRecords": "Inga resultat",
                          "oPaginate": {
                            "sFirst": "Första",
                            "sPrevious": "Föregående",
                            "sNext": "Nästa",
                            "sLast": "Sista"}
                        }

    return JsonResponse(translation_string)

def return_file_of_kodverk_and_kodtext(request, kodverk_id):

    if kodverk_id is None:
        return HttpResponse('''<div class="alert alert-success">
                                   Sök parameter saknas, problem med inskickning.
                                   </div>''')
    
    if (request.is_ajax()) or (request.method == 'GET'):

        
        output_memory_file = BytesIO()
        workbook = xlsxwriter.Workbook(output_memory_file, {'in_memory' : True})
        bold = workbook.add_format({'bold': True})
        text_wrap = workbook.add_format()
        text_wrap.set_text_wrap()

        kodverk_worksheet = workbook.add_worksheet('Metadata')
        
        kodtext_worksheet = workbook.add_worksheet('Kod+Kodtext')
        
        kodverk_columns = {'kodverk' : ['titel_på_kodverk',
                                        'syfte',
                                        'beskrivning_av_innehållet',
                                        'status',
                                        'identifierare',
                                        'version',
                                        'kategori',
                                        'kodverk_variant',
                                        'uppdateringsintervall',
                                        'extra_data',            
                                        'användning_av_kodverk',
                                        'giltig_från',
                                        'giltig_tom',
                                        'datum_skapat',
                                        'senaste_ändring'],
                       'codeconcept' : ['källa',
                                        'version_av_källa',
                                        'ansvarig_förvaltare',
                                        'ägare_till_kodverk'],
                         'sökord' : ['nyckelord']}

        kodtext_columns = ['kod',
                           'kodtext',
                           'annan_kodtext',
                           'definition']
        
        col_num = 0

        all_columns = [col for col in kodverk_columns.values() for col in col]
        for row_num in range(len(all_columns)):
            kodverk_worksheet.write(row_num, col_num, all_columns[row_num], bold)

        row_num=0
        for col_num in range(len(kodtext_columns)):
            kodtext_worksheet.write(row_num, col_num, kodtext_columns[col_num], bold)

        kodverk_set = Kodverk.objects.prefetch_related().get(id=kodverk_id)
        
        codeconcepts = kodverk_set.codeableconceptattributes_set.all()
        sökord = kodverk_set.nyckelord_set.all()
        
        date_columns = ['giltig_från',
                       'giltig_tom',
                       'datum_skapat',
                       'senaste_ändring']
        
        date_format = workbook.add_format({'num_format': 'YYYY-MM-DD'})
        length = len(kodverk_set.titel_på_kodverk)
        kodverk_worksheet.set_column(1, 1, length)
        kodverk_worksheet.set_column(0, 0, length)

        col_num = 1
        
        for row_num, column in enumerate(all_columns):
            for kodverk_metadata, columns in kodverk_columns.items():

                if (kodverk_metadata == "kodverk") and (column in columns):                    
                    metadata_value = getattr(kodverk_set, column)                    
                    if column in date_columns:                        
                        kodverk_worksheet.write(row_num, col_num, metadata_value, date_format)
                    elif (column in ['syfte', 'beskrivning_av_innehållet']):
                        kodverk_worksheet.write(row_num, col_num, metadata_value, text_wrap)
                    else:
                        try:                    
                            kodverk_worksheet.write(row_num, col_num, metadata_value)
                        except TypeError as e:
                            logger.debug(f'problem writing to kodverk worksheet - {e}')

                if kodverk_metadata == "codeconcept" and (column in columns):
                    metadata_value = []                    
                    for single_record in codeconcepts:
                        metadata_value.append(getattr(single_record, column, ''))                    
                    try:
                        kodverk_worksheet.write(row_num, col_num, ', '.join(metadata_value))
                    except TypeError as e:
                        logger.debug(f'problem writing to kodverk worksheet - {e}')
                    del metadata_value

                if kodverk_metadata == "sökord"  and (column in columns):
                    metadata_value = []                    
                    for single_record in sökord:
                        metadata_value.append(getattr(single_record, column))                    
                    try:    
                        kodverk_worksheet.write(row_num, col_num, ', '.join(filter(None, metadata_value)))
                    except TypeError as e:
                        logger.debug(f'problem writing to kodverk worksheet - {e}')
                    del metadata_value

        kodtexter = Kodtext.objects.filter(kodverk_id=kodverk_id).values('kod','kodtext','annan_kodtext','definition')
        
        row_num = 1
        for kodtext in kodtexter:
            for col_num, (kodtext_attr, kodtext_value) in enumerate(kodtext.items()):
                if type(kodtext_value) == dict:
                    kodtext_value = str(kodtext_value)
                try:
                    kodtext_worksheet.write(row_num, col_num, kodtext_value)
                except TypeError as e:
                    logger.debug(f'problem writing to kodtext worksheet - {e}')
            row_num += 1      
        
        filename = kodverk_set.titel_på_kodverk + '.xlsx'
        filename = filename.replace(' ','_')
        
        workbook.close()
        output_memory_file.seek(0)

        response = HttpResponse(output_memory_file.getvalue())
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        return response

def kodverk_verify_comment(request):

    url_parameter = request.GET.get("q")
    
    if request.method == 'GET':
        form_id= request.GET.get("value")
        
        
        if form_id == "comment":
            form = KommenteraKodverk(initial={'kodverk': url_parameter})
            return render(request,'commentForm.html', {'kommentera': form})
        elif form_id =="verify":
            
            form = VerifyKodverk(initial={'kodverk': url_parameter})
            return render(request,'verifyForm.html', {'verify': form})
    
    elif request.method == 'POST':
        
        form_id = request.get_raw_uri().split('=')[-1]
        
        if form_id == "comment":
            print('processing comment form', form_id)
            form = KommenteraKodverk(request.POST)
            
            if form.is_valid():
                
                kommentera_kodverk = CommentedKodverk()
                kommentera_kodverk.kodverk = Kodverk(id=form.cleaned_data.get("kodverk"))
                kommentera_kodverk.kommentar = form.cleaned_data.get('kommentar')
                kommentera_kodverk.epost = form.cleaned_data.get('epost')
                kommentera_kodverk.namn = form.cleaned_data.get('namn')                
                kommentera_kodverk.kontakt = form.cleaned_data.get('kontakt')
                kommentera_kodverk.status = 'Nytt'
                
                kommentera_kodverk.save()

                return HttpResponse('''<div class="alert alert-success">
                                    Tack för dina synpunkter.
                                    </div>''')
            else:
                print('formisnotvalid')
        
        else:
            form=VerifyKodverk(request.POST)
            
            if form.is_valid():
                
                new_verify = ValidatedBy()
                new_verify.kodverk = Kodverk(id=form.cleaned_data.get("kodverk"))
                new_verify.domän_kontext=form.cleaned_data.get("kontext")
                new_verify.domän_stream=form.cleaned_data.get("stream")
                new_verify.domän_telefon=form.cleaned_data.get("telefon")
                new_verify.domän_epost=form.cleaned_data.get("epost")
                new_verify.save() 
                
                return HttpResponse('''<div class="alert alert-success">
                                        Tack för dina synpunkter.
                                        </div>''') 
          
    else:
        return render(request, 'kodverk_komplett_metadata.html', {})
    
def load_kodtext(request, kodverk_id):
    
    kodtext = Kodtext.objects.filter(kodverk_id=kodverk_id).order_by('kodtext', 'kod').values("id","kod", "kodtext")
    if kodtext is not None:
        
        return render(request, 
                      'admin/kodtext_dropdown_list_options.html', 
                      {'kodtexter': kodtext}, status=200)
    else:

        kodtext = [{"kod" : "Inga kod" , "kodtext" : "Inga kodtexter"},]
    
        return render(request, 
                      'admin/kodtext_dropdown_list_options.html', 
                      {'kodtexter': kodtext}, status=200)

def previous_codeconcept_values_json(request):

    ägare = CodeableConceptAttributes.objects.filter(kodverk_from__status="Beslutad")
    
    suggestion_dict = {}
    fields = ['källa','version_av_källa','ansvarig_förvaltare','ägare_till_kodverk']
    for entry in ägare.values():
        for key,value in entry.items():
            if (key in fields) and (value is not None):
                if suggestion_dict.get(key) is None:
                    suggestion_dict[key] = [value]
                else:
                    suggestion_dict[key].append(value)

    for key,values in suggestion_dict.items():
        suggestion_dict[key] = list(set(values))

    return JsonResponse(suggestion_dict, safe=False)


def return_number_of_recent_comments(request):
    
    if request.method == 'GET':
        total_comments = CommentedKodverk.objects.all()
        status_list = [i.get('status') for i in total_comments.values()]
        
        return JsonResponse({'unreadcomments' : len(status_list)-status_list.count("Klart"),
                             'totalcomments' : len(status_list)})

def structure_kodverk_queryset_as_json(queryset):

    kodverk = queryset

    suggestion_dict = {}
    kodverk_fields = ['titel_på_kodverk', 'syfte', 'beskrivning_av_innehållet', 'identifierare', 'version', 'giltig_från', 'giltig_tom', 'uppdateringsintervall','status']
    kodtext_fields = ['kod', 'kodtext','annan_kodtext', 'definition', 'position', 'kommentar']
    codeableconcept_fields = ['ägare_till_kodverk', 'ansvarig_förvaltare','källa', 'version_av_källa']

    for index, entry in enumerate(kodverk, start=1):
        
        if suggestion_dict.get(index) is None:
            suggestion_dict[index] = {}

        if suggestion_dict[index].get('metadata') is None:
            suggestion_dict[index]['metadata'] = {}

        if suggestion_dict[index].get('kodverk') is None:
            suggestion_dict[index]['kodverk'] = {}

        if suggestion_dict[index].get('metadata') is not None:
            suggestion_dict[index]['metadata'] = {attr:getattr(entry, attr) for attr in kodverk_fields if attr in kodverk_fields}
            suggestion_dict[index]['metadata']['codeable_concept'] = {}
            
            for codeconcept_idx, codeableconcept in enumerate(entry.codeableconceptattributes_set.values(), 1):
                #set_trace()
                suggestion_dict[index]['metadata']['codeable_concept'][codeconcept_idx] = {key:value for key,value in codeableconcept.items() if key in codeableconcept_fields}
                # {attr:getattr(entry, attr) for attr in codeableconcept if attr in codeableconcept_fields}

            nyckelord = [i.get('nyckelord') for i in entry.nyckelord_set.values() if i is not None]
            if len(nyckelord) > 0:
                suggestion_dict[index]['metadata']['sökord'] = nyckelord

        if suggestion_dict[index].get('kodverk') is not None:
            for kodtext_number, kodtext in enumerate(entry.kodtext_set.values(), 1):
                suggestion_dict[index]['kodverk'][kodtext_number] = {attr:value for attr,value in kodtext.items() if attr in kodtext_fields} 
    
    sorted_date_list = sorted([i[0] for i in kodverk.all().values_list('senaste_ändring')], reverse=True)
    
    last_modified = {'Last-Modified': sorted_date_list[0].strftime('%Y-%m-%d %H:%M:%S')}

    response =  JsonResponse(suggestion_dict, safe=False, json_dumps_params={'ensure_ascii': False})
    response['Last-Modified'] = last_modified

    return response

def all_kodverk_and_kodtext_as_json(request):

    kodverk = Kodverk.objects.prefetch_related('kodtext_set').filter(status="Aktiv")

    response = structure_kodverk_queryset_as_json(kodverk)

    return response

def content_changes_from_date(request, year, month, day):

    queryset = Kodverk.objects.prefetch_related('kodtext_set').filter(status="Aktiv").filter(senaste_ändring__gte=date(int(year), int(month), int(day)))
    
    response = structure_kodverk_queryset_as_json(queryset)

    return response