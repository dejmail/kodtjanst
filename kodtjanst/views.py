import re
import logging
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

from .models import Kodverk, Kodtext, ExternaKodtext, ValidatedBy, CommentedKodverk
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

def retur_general_sök(url_parameter):
    cursor = connection.cursor()
    ''' need to reduce the number of fields being returned, we are not using all of them,
    but this also affects the parsing as it is position based, so need to be careful'''
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
                        OR kodtjanst_kodverk.nyckelord LIKE "%{url_parameter}%"\
                        OR kodtjanst_kodtext.kodtext LIKE "%{url_parameter}%"\
                        OR kodtjanst_kodtext.annan_kodtext LIKE "%{url_parameter}%"\
                        OR kodtjanst_kodtext.definition LIKE "%{url_parameter}%")
                        AND kodtjanst_kodverk.status = 'Beslutad';'''

    clean_statement = re.sub(RE_PATTERN, ' ', sql_statement)
    cursor.execute(clean_statement)
    result = cursor.fetchall()
    
    return result

def retur_komplett_förklaring_custom_sql(url_parameter):

    cursor = connection.cursor()
    sql_statement = f'''SELECT syfte,\
                            beskrivning_av_informationsbehov,\
                            identifier,\
                            titel_på_kodverk,\
                            ägare_till_kodverk,\
                            version,\
                            hämtnings_källa,\
                            version_av_källa,\
                            kategori,\
                            instruktion_för_kodverket,\
                            kodverk_variant,\
                            status,\
                            uppdateringsintervall,\
                            mappning_för_rapportering,\
                            ansvarig_förvaltare,\
                            datum_skapat,\
                            senaste_ändring,\
                            giltig_från,\
                            giltig_tom,\
                            ändrad_av_id,\
                            ansvarig_id,\
                            urval_referens_id\
                            nyckelord\
                        FROM kodtjanst_kodverk\
                        LEFT JOIN kodtjanst_nyckelord\
                            on kodtjanst_kodverk.id = kodtjanst_nyckelord.kodverk_from_id\
                        WHERE kodtjanst_kodverk.id = {url_parameter};'''
    clean_statement = re.sub(RE_PATTERN, ' ', sql_statement)
    cursor.execute(clean_statement)
    result = cursor.fetchall()
    
    return result


def return_kodtext_related_to_kodverk(url_parameter):

    cursor = connection.cursor()
    sql_statement = f'''SELECT * from kodtjanst_kodtext WHERE kodtjanst_kodtext.kodverk_id = {url_parameter};'''
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


def kodverk_sok(request):
    url_parameter = request.GET.get("q")
        
    if request.is_ajax():
        
        #mäta_sök_träff(sök_term=url_parameter,sök_data=return_list_dict, request=request)
        kodverk_column_names = ['id',
                                'titel_på_kodverk',
                                'syfte']
        sql_search = retur_general_sök(url_parameter)
        search_result = attach_column_names_to_search_result(sql_search, kodverk_column_names)
        # search_result = highlight_search_term_i_definition(url_parameter, search_result)
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

def kodverk_komplett_metadata(request):

    url_parameter = request.GET.get("q")
    
    if request.is_ajax():
        if url_parameter:
            exact_kodverk_request = retur_komplett_förklaring_custom_sql(url_parameter)
            #kodverk_full = extract_columns_from_query_and_return_set(exact_kodverk_request, 0, 0)
            
            #domän_full = extract_columns_from_query_and_return_set(exact_term_request, -2, 0)
            
            result_column_names = ['syfte',
                              'beskrivning_av_informationsbehov',
                              'identifier',
                              'titel_på_kodverk',
                              'ägare_till_kodverk',
                              'version',
                              'hämtnings_källa',
                              'version_av_källa',
                              'kategori',
                              'instruktion_för_kodverket',
                              'kodverk_variant',
                              'status',
                              'uppdateringsintervall',
                              'mappning_för_rapportering',
                              'ansvarig_förvaltare',
                              'datum_skapat',
                              'senaste_ändring',
                              'giltig_från',
                              'giltig_tom',
                              'ändrad_av_id',
                              'ansvarig_id',
                             'urval_referens_id']

            #kodverk_column_names = result_column_names[:-5]
            
            return_list_dict = []
            
            for return_result in exact_kodverk_request:
                return_list_dict.append(dict(zip(result_column_names, return_result)))
            
            kodtext_search_result = return_kodtext_related_to_kodverk(url_parameter)
            kodtext_column_names = ['annan_kodtext',
                                    'datum_skapat',
                                    'definition',
                                    'extra_data',
                                    'kod',
                                    'kodtext',
                                    'kodverk',
                                    'kommentar',
                                    'position',
                                    'senaste_ändring',
                                    'status',
                                    'ändrad_av']

            kodtext_dict = attach_column_names_to_search_result(kodtext_search_result,kodtext_column_names)
            
            template_context = {'kodverk_full': return_list_dict[0],
                                'kodverk_id' : url_parameter,
                                'kodtext_full' : kodtext_dict}
                                
            
            html = render_to_string(template_name="kodverk_komplett_metadata.html", context=template_context)
        
            return render(request, "kodverk_komplett_metadata.html", context=template_context)
    else:
        kodverk = Kodverk.objects.none()
    return render(request, "kodverk.html", {'kodverk': kodverk})


def extract_columns_from_query_and_return_set(search_result, start, stop):

    reduced_list = []
    for record in search_result:
        if start==0:
            reduced_list.append(record[:stop])
        elif stop==0:
            reduced_list.append(record[start:])
        else:
            reduced_list.append(record[start:stop])
    
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
                            "sPrevious": "Förre",
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

        kodverk_worksheet = workbook.add_worksheet('Metadata')
        
        kodtext_worksheet = workbook.add_worksheet('Kod+Kodtext')
        
        kodverk_columns = ['titel_på_kodverk',
                           'syfte',
                           'beskrivning_av_informationsbehov',
                           'status',
                           'identifier',
                           'ägare_till_kodverk',
                           'version',
                           'hämtnings_källa',
                           'version_av_källa',
                           'kategori',
                           'instruktion_för_kodverket',
                           'kodverk_variant',
                           'uppdateringsintervall',
                           'mappning_för_rapportering',
                           'ansvarig',
                           'ansvarig_förvaltare',
                           'extra_data',            
                           'användning_av_kodverk',
                           'giltig_från',
                           'giltig_tom',
                           'datum_skapat',
                           'senaste_ändring']

        kodtext_columns = ['kod',
                           'kodtext',
                           'annan_kodtext',
                           'definition']
        
        row_num = 0
        for col_num in range(len(kodverk_columns)):
            kodverk_worksheet.write(row_num, col_num, kodverk_columns[col_num], bold)

        for col_num in range(len(kodtext_columns)):
            kodtext_worksheet.write(row_num, col_num, kodtext_columns[col_num], bold)

        kodverk = Kodverk.objects.filter(id=kodverk_id).values('titel_på_kodverk',
                                                                'syfte',
                                                                'beskrivning_av_informationsbehov',
                                                                'status',
                                                                'identifier',
                                                                'ägare_till_kodverk',
                                                                'version',
                                                                'hämtnings_källa',
                                                                'version_av_källa',
                                                                'kategori',
                                                                'instruktion_för_kodverket',
                                                                'kodverk_variant',
                                                                'uppdateringsintervall',
                                                                'mappning_för_rapportering',
                                                                'ansvarig',
                                                                'ansvarig_förvaltare',
                                                                'extra_data',            
                                                                'användning_av_kodverk',
                                                                'giltig_från',
                                                                'giltig_tom',
                                                                'datum_skapat',
                                                                'senaste_ändring')
        date_columns = ['giltig_från',
                       'giltig_tom',
                       'datum_skapat',
                       'senaste_ändring']
        
        date_format = workbook.add_format({'num_format': 'YYYY-MM-DD'})

        row_num += 1
        for col_num, (kodverk_metadata, metadata_value) in enumerate(kodverk[0].items()):
            if type(metadata_value) == dict :
                metadata_value = str(metadata_value)
            if kodverk_metadata in date_columns:
                kodverk_worksheet.write(row_num, col_num, metadata_value, date_format)    
            else:
                kodverk_worksheet.write(row_num, col_num, metadata_value)

        kodtexter = Kodtext.objects.filter(kodverk_id=kodverk_id).values('kod','kodtext','annan_kodtext','definition')
        
        row_num = 1
        for kodtext in kodtexter:
            for col_num, (kodtext_attr, kodtext_value) in enumerate(kodtext.items()):
                if type(kodtext_value) == dict:
                    kodtext_value = str(kodtext_value)
                kodtext_worksheet.write(row_num, col_num, kodtext_value)
            row_num += 1      
        
        filename = kodverk.values()[0].get('titel_på_kodverk') + '.xlsx'
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
                kommentera_kodverk.comment_kontext = form.cleaned_data.get('kommentar_kontext')
                kommentera_kodverk.comment_epost = form.cleaned_data.get('epost')
                kommentera_kodverk.comment_name = form.cleaned_data.get('namn')                
                kommentera_kodverk.comment_telefon = form.cleaned_data.get('telefon')              
                
                kommentera_kodverk.save()

                return HttpResponse('''<div class="alert alert-success">
                                    Tack för dina synpunkter.
                                    </div>''')
            else:
                print('formisnotvalid') 
                set_trace()
        
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