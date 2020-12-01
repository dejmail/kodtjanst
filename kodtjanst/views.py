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

from .forms import UserLoginForm
from .models import Kodverk, Kodtext, MappadTillKodtext

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
    sql_statement = f'''SELECT kodtjanst_kodverk.id,\
                               kodtjanst_kodverk.titel_på_kodverk,\
                               kodtjanst_kodverk.nyckelord,\
                               kodtjanst_kodverk.status,\
                               kodtjanst_kodverk.syfte,\
                               kodtjanst_ämne.domän_namn,\
                               kodtjanst_kodtext.kod,\
                               kodtjanst_kodtext.kodtext,\
                               kodtjanst_kodtext.annan_kodtext,\
                               kodtjanst_kodtext.definition\
                        FROM kodtjanst_kodverk\
                            LEFT JOIN kodtjanst_kodtext\
                                ON kodtjanst_kodtext.kodverk_id = kodtjanst_kodverk.id\
                            LEFT JOIN kodtjanst_ämne\
                                ON kodtjanst_kodverk.id = kodtjanst_ämne.kodverk_id\
                        WHERE (kodtjanst_kodverk.titel_på_kodverk LIKE "%{url_parameter}%")\
                        OR (kodtjanst_kodverk.syfte LIKE "%{url_parameter}%")\
                        OR (kodtjanst_kodverk.nyckelord LIKE "%{url_parameter}%")\
                        OR (kodtjanst_kodtext.kodtext LIKE "%{url_parameter}%")\
                        OR (kodtjanst_kodtext.annan_kodtext LIKE "%{url_parameter}%")\
                        OR (kodtjanst_kodtext.definition LIKE "%{url_parameter}%");'''

    clean_statement = re.sub(RE_PATTERN, ' ', sql_statement)
    #logger.debug(clean_statement)
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
                        FROM kodtjanst_kodverk\
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
                    #logger.debug(f'found string with search value - {value}')
                    #set_trace()
                    return_string = ''.join([value[0:match.start()],'<mark>', value[match.start():match.end()], '</mark>', value[match.end():]])
                    #print(return_string)
                    #result_dict_list[idx][key] = return_string
                    result_dict_list[idx].update({key : return_string})
    #print(result_dict_list)
    return result_dict_list


def kodverk_sok(request):
    url_parameter = request.GET.get("q")
    
    #print('entering the kodverk_sök function')
    
    if request.is_ajax():
        
        #data_dict, return_list_dict = hämta_data_till_begrepp_view(url_parameter)
        #mäta_sök_träff(sök_term=url_parameter,sök_data=return_list_dict, request=request)
        kodverk_column_names = ['id',
                            'titel_på_kodverk',
                            'nyckelord',
                            'status',
                            'syfte',
                            'domän_namn',
                            'kod',
                            'kodtext',
                            'annan_kodtext',
                            'definition']
        sql_search = retur_general_sök(url_parameter)
        search_result = attach_column_names_to_search_result(sql_search, kodverk_column_names)
        # search_result = highlight_search_term_i_definition(url_parameter, search_result)
        html = render_to_string(
            template_name="kodverk_partial_result.html", context={'kodverk': search_result,                                                            
                                                            'searched_for_term' : url_parameter})

        return JsonResponse(data=html, safe=False)
        #html = render_to_string(
        #   template_name="kodverk_partial_result.html", context={'kodverk': data_dict,
                                                               #'synonym' : return_synonym_list_dict,
        #                                                       'searched_for_term' : url_parameter}
    #)
    #    return html#, render(request, "term-results-partial.html", context=data_dict)

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
                                'hämtnings_källa'
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
                                'ändrad_av',
                                'ansvarig',
                                'urval_referens',]

            #kodverk_column_names = result_column_names[:-5]
            
            return_list_dict = []
            
            for return_result in exact_kodverk_request:
                return_list_dict.append(dict(zip(result_column_names, return_result)))
            

        # domän_column_names = result_column_names[-2:]
        # return_domän_list_dict = []
        # for return_result in domän_full:
        #     return_domän_list_dict.append(dict(zip(domän_column_names, return_result)))

        # mäta_förklaring_träff(sök_term=url_parameter, request=request)

        #status_färg_dict = {'begrepp' :färg_status_dict.get(return_list_dict[0].get('status'))}
            
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
                                #'domän_full' : return_domän_list_dict,
                                #'färg_status' : status_färg_dict}
            
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

import json
def return_kodtext_as_json(request):

    url_parameter = request.GET.get("q")
    
    if (request.is_ajax()) or (request.method == 'GET'):
    
        kodtext = Kodtext.objects.filter(kodverk_id=int(url_parameter))
               
        post_kodtext = serializers.serialize('json', kodtext)
   
        return HttpResponse(post_kodtext)