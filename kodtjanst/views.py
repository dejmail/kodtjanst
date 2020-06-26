from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.urls import path 
from django.db import connection, transaction

from .forms import UserLoginForm
from .models import Kodverk, Kodtext, MappadTillKodtext

from pdb import set_trace

from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout
)

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
    sql_statement = f'''SELECT kodtjanst_kodverk.rubrik_på_kodverk,\
                                nyckelord,\
                                status,\
                                syfte,\
                                kodtjanst_ämne.domän_namn AS dömän_namn,\
                                kodtjanst_kodtext.kodtext,\
                                kodtjanst_kodtext.annan_kodtext,\
                                kodtjanst_kodtext.definition,\
                        FROM kodtjanst_kodverk\
                            LEFT JOIN kodtjanst_kodtext\
                                ON kodtjanst_kodtext.id = kodtjanst_koverkid\
                            LEFT JOIN kodtjanst_ämne\
                                ON kodtjanst_kodverk.id = kodtjanst_ämne_id\
                        WHERE (kodtjanst_kodverk.rubrik_på_kodverk LIKE "%{url_parameter}%")\
                        OR (kodtjanst_kodverk.syfte LIKE "%{url_parameter}%")\
                        OR (kodtjanst_kodverk.nyckelord LIKE "%{url_parameter}%"\
                        OR (kodtjanst_kodtext.kodtext LIKE "%{url_parameter}%"\
                        OR (kodtjanst_kodtext.annan_kodtext LIKE "%{url_parameter}%"\
                        OR (kodtjanst_kodtext.definition LIKE "%{url_parameter}%";'''
    
    # column_names = ['begrepp_id',
    #                 'definition',
    #                 'term',
    #                 'begrepp_status', 
    #                 'synonym_begrepp_id',
    #                 'synonym',
    #                 'synonym_status']

    clean_statement = re.sub(re_pattern, ' ', sql_statement)
    cursor.execute(clean_statement)
    result = cursor.fetchall()
    
    return result

def kodverk_view(request):

    url_parameter = request.GET.get("q")
    
    if request.is_ajax():
        #data_dict, return_list_dict = hämta_data_till_begrepp_view(url_parameter)
        #mäta_sök_träff(sök_term=url_parameter,sök_data=return_list_dict, request=request)
        data_dict = retur_general_sök(url_parameter)
        return JsonResponse(data=data_dict, safe=False)

    # elif request.method == 'GET':
    #     data_dict, return_list_dict = hämta_data_till_begrepp_view(url_parameter)
    #     return render(request, "term-results-partial.html", context=data_dict)

    # elif request.method=='GET':
    #     return render(request, "term_forklaring.html", context=template_context)
    
    else:
        kodverk = Kodverk.objects.none()
    return render(request, "kodverk.html", {})

def kodverk_metadata_view(request):
    return render(request, "kodverk_metadata_view.html", context)