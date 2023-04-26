import re
import logging
from datetime import date
from django.shortcuts import render, HttpResponse, get_object_or_404
from django.contrib import admin
from django.core import serializers
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.core import serializers

from django.db.models import (
    Q, 
    Case, 
    When,
    Value,
    IntegerField
)

from .models import Kodverk, Kodtext, ExternaKodtext, CommentedKodverk, CodeableConceptAttributes, ArbetsKommentar, ValidatedBy
from .forms import VerifyKodverk, KommenteraKodverk

from io import BytesIO
import xlsxwriter

import json
from pdb import set_trace

logger = logging.getLogger(__name__)

RE_PATTERN = re.compile(r'\s+')

def retur_alla_kodverk(url_parameter):

    queryset = Kodverk.objects.filter(status='Aktiv').values('id','titel_på_kodverk','syfte','länk','kodverk_variant')

    return queryset

def retur_general_sök(url_parameter):

    queryset = Kodverk.objects.filter(Q(status='Aktiv'),
                                      Q(titel_på_kodverk__icontains=url_parameter) |
                                      Q(syfte__icontains=url_parameter) | 
                                      Q(beskrivning_av_innehållet__icontains=url_parameter) |
                                      Q(användning_av_kodverk__icontains=url_parameter) |
                                      Q(nyckelord__nyckelord__icontains=url_parameter) |
                                      Q(kodtext__kodtext__icontains=url_parameter) |
                                      Q(kodtext__annan_kodtext__icontains=url_parameter) |
                                      Q(kodtext__definition__icontains=url_parameter)).distinct()
    
    return queryset


def sort_results_according_to_search_term(queryset, search_term):
    
    """Returns a sorted list based on "column" from list-of-dictionaries data.

    Arguments: 
    queryset {queryset} -- queryset containing terms to be returned to the UI
    url_parameter {str} -- The str with which to split each term with
    :return: Sorted queryset with annotayion
    :rtype: queryset
    """

    qs = queryset.annotate(
    position=Case(
        When(Q(titel_på_kodverk__iexact=search_term), then=Value(1)),
        When(Q(titel_på_kodverk__istartswith=search_term), then=Value(2)),
        When(Q(titel_på_kodverk__icontains=search_term), then=Value(3)), 
        When(Q(beskrivning_av_innehållet__icontains=search_term), then=Value(4)),
        default=Value(5), output_field=IntegerField()
        )
    )
    qs = qs.order_by('position')

    return qs

def return_codesets_by_letter(url_parameter):

    vgrkv_filter = Kodverk.objects.filter(Q(status='Aktiv'),Q(titel_på_kodverk__istartswith=f'VGRKV_{url_parameter}')).distinct()
    letter_filter = Kodverk.objects.filter(Q(status='Aktiv'),Q(titel_på_kodverk__istartswith=url_parameter)).distinct()

    queryset = vgrkv_filter | letter_filter
    
    return queryset


def get_codeset_by_id(url_parameter):

    queryset = Kodverk.objects.get(
        id=url_parameter
        )
    
    return queryset

def get_kodtext_related_to_kodverk(url_parameter):

    queryset = Kodtext.objects.filter(
        Q(kodverk_id=url_parameter),
        ~Q(status='Publicera ej')
        ).order_by('position')

    return queryset

def return_external_kodtext_related_to_kodverk(url_parameter):

    queryset = ExternaKodtext.objects.filter(
        kodverk_id=url_parameter
        ).values(
            'id',
            'mappad_id',
            'mappad_text',
            'resolving_url'
            )

    return queryset

def return_kommentar_related_to_kodverk(url_parameter):

    queryset = ArbetsKommentar.objects.filter(
        kodverk_id=url_parameter
        ).values(
            'id',
            'kommentar'
            )

    return queryset

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
            if entry[0].get(field) is not None:
                result_list_of_dictionaries[index][field] = format_html(entry[0].get(field))
    return result_list_of_dictionaries

def kodverk_sok(request):
    url_parameter = request.GET.get("q")
    filter = request.GET.get("filter")

    if request.is_ajax():
        
        if url_parameter == '*all':
            queryset = retur_alla_kodverk(url_parameter)
        else:
            queryset = retur_general_sök(url_parameter)

        queryset = sort_results_according_to_search_term(
            queryset=queryset,
            search_term=url_parameter
            )

        html = render_to_string(
            template_name="kodverk_partial_result.html", context={
                'kodverk': queryset,
                'searched_for_term' : url_parameter
                }
                )
        
        if filter == 'True':
            
            queryset = return_codesets_by_letter(url_parameter)

            html = render_to_string(
                template_name="kodverk_partial_result.html", context={
                    'kodverk': queryset,
                    'searched_for_term' : url_parameter
                    }
                    )

        return HttpResponse(html)
    
    else:
        kodverk = Kodverk.objects.none()
    return render(request, "kodverk.html", {})

def convert_list_of_tuples_to_string(tuple_list, start=None, stop=None, single_position=None):

    '''
    Returns concatenated, command separated string of contents of an arbitrary 
    slicing range from of a tuple of tuples or lists of lists or just one 
    position within each list or tuple.
    '''
    
    if len(tuple_list) == 0:
        return ''
    if tuple(tuple_list)[0][0] is None:
        return ''
    if single_position is not None:
        return ', '.join([i[single_position] for i in tuple_list])
    elif (start is not None) and (stop is not None):
        return ', '.join([i[start:stop] for i in tuple_list])


def get_codeset(request, kodverk_id):
    
    data = list(get_kodtext_related_to_kodverk(kodverk_id).values(
        'id',
        'kod',
        'kodtext',
        'definition',
        'position',
        'extra_data')
        )

    return JsonResponse(data, safe=False)

def format_rim_urls(rim_links: dict) -> list:

    if rim_links:
        formated_text = []
        rim_urls = rim_links.get('rim-url')
        rim_url_text = rim_links.get('rim-url-text')
        for index, url in enumerate(rim_urls):
            formated_text.append(f"""<a href="{url}">{rim_url_text[index].replace('  ',' ')}</a>""")
        
        return [format_html(i) for i in formated_text]
    else:
        return None

def return_komplett_metadata(request, kodverk_id):

    if kodverk_id:

        kodverk_qs = get_codeset_by_id(kodverk_id)
        rim_url_list = format_rim_urls(
                    kodverk_qs.extra_data)

        template_context = {
            'kodverk': kodverk_qs,
            'kodverk_id' : kodverk_id,
            'rim_url' : rim_url_list,
            'kommentar' : return_kommentar_related_to_kodverk(kodverk_id)
            }

        if kodverk_qs.kodverk_variant == "VGR codeable concept":
            template_context['external_kodtext'] = kodverk_qs.externakodtext_set.all()       

        return template_context
    else:
        return None

def kodverk_komplett_metadata(request, kodverk_id):
    
    if request.is_ajax():
        
        template_context = return_komplett_metadata(request, kodverk_id)
        return render(request, "kodverk_komplett_metadata.html", context=template_context)

    elif request.method == 'GET':
        template_context = return_komplett_metadata(request, kodverk_id)        
        return render(request, "kodverk_komplett_metadata_get.html", context=template_context)
    else:
        kodverk = Kodverk.objects.none()
        return render(request, "kodverk.html", {'kodverk': kodverk})

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
                          "None" : "Ingen",
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
                                   Ingen fil hittades med inskickat siffran.
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
                           'definition',
                           'extra_data']
        
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

        kodtext_set = get_kodtext_related_to_kodverk(kodverk_id)
        
        row_num = 1
        for kodtext in kodtext_set:
            for col_num, kodtext_attr in enumerate(kodtext_columns):
                try:
                    if kodtext_attr in kodtext_columns:
                        kodtext_value = getattr(kodtext, kodtext_attr)
                        if type(kodtext_value) == dict:
                            kodtext_value = str(kodtext_value)
                        else:
                            kodtext_value = getattr(kodtext, kodtext_attr)
                        kodtext_worksheet.write(
                            row_num, 
                            col_num, 
                            kodtext_value
                        )
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

    ägare = CodeableConceptAttributes.objects.filter(kodverk_from__status="Aktiv")
    
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
    suggestion_dict = []

    kodverk_fields = ['id','titel_på_kodverk', 'beskrivning_av_innehållet', 'identifierare', 'version', 'giltig_från', 'giltig_tom', 'uppdateringsintervall','status', 'användning_av_kodverk','länk']
    kodtext_fields = ['id','kod', 'kodtext','annan_kodtext', 'definition', 'position', 'kommentar']
    externa_kodtext_fields = ['mappad_id', 'mappad_text', 'resolving_url']
    codeableconcept_fields = ['ägare_till_kodverk', 'ansvarig_förvaltare','källa', 'version_av_källa']

    for idx, entry in enumerate(kodverk):
        suggestion_dict.append({'metadata' : {attr:getattr(entry, attr) for attr in kodverk_fields if attr in kodverk_fields}})

        suggestion_dict[idx]['codeable_concept'] = []
        for concept in entry.codeableconceptattributes_set.values():
            suggestion_dict[idx]['codeable_concept'].append({attr:value for attr,value in concept.items() if attr in codeableconcept_fields})
        
        suggestion_dict[idx]['nyckelord'] = []
        nyckelord = [i.get('nyckelord') for i in entry.nyckelord_set.values() if i is not None]
        if len(nyckelord) > 0:
            suggestion_dict[idx]['nyckelord'] = nyckelord
        
        suggestion_dict[idx]['kodverk'] = []
        if entry.kodtext_set.values():
            for kodtext in entry.kodtext_set.values():
                suggestion_dict[idx]['kodverk'].append({attr:value for attr,value in kodtext.items() if attr in kodtext_fields})
        elif entry.externakodtext_set.all():
            for extern_kodtext in entry.externakodtext_set.all():
                suggestion_dict[idx]['kodverk'].append({attr:getattr(extern_kodtext, attr) for attr in externa_kodtext_fields})
        else:
            suggestion_dict[idx]['kodverk'].append({'message' : 'No kodtext associated'})

    
    sorted_date_list = sorted([i.senaste_ändring for i in kodverk], reverse=True)

    last_modified = {'Last-Modified': sorted_date_list[0].strftime('%Y-%m-%d %H:%M:%S')}

    response =  JsonResponse(suggestion_dict, safe=False, json_dumps_params={'ensure_ascii': False})
    response['Last-Modified'] = last_modified

    return response

def all_kodverk_and_kodtext_as_json(request):

    kodverk = Kodverk.objects.all().filter(Q(status="Aktiv"),
                                           Q(kodverk_variant='VGR kodverk'))
    
    response = structure_kodverk_queryset_as_json(kodverk)

    return response

def content_changes_from_date(request, year, month, day):

    queryset = Kodverk.objects.prefetch_related('kodtext_set').filter(status="Aktiv").filter(senaste_ändring__gte=date(int(year), int(month), int(day)))
    
    response = structure_kodverk_queryset_as_json(queryset)

    return response

def show_kodverk_history(request, pk):

    kodtext_history_qs = Kodtext.history.filter(kodverk__id=pk)
    kodverk_history_qs = Kodverk.history.filter(id=pk)

    kodverk_changes = []
    for history in kodverk_history_qs:
        if history.prev_record:
            kodverk_changes.append([history.history_date, history.diff_against(history.prev_record)])

    for history in kodtext_history_qs:
        if history.prev_record:
            kodverk_changes.append([history.history_date, history.diff_against(history.prev_record)])

    return render(request, "kodverk_historik_detaljer.html", 
                          {"history": kodverk_changes,
                           "kodverk" : kodverk_history_qs.first().titel_på_kodverk,
                           "url" : get_object_or_404(Kodverk, pk=kodverk_history_qs.first().id)})
