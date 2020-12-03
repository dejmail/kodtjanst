from django.contrib import admin
from django.urls import path

from kodtjanst import views


urlpatterns = [
    path("", views.kodverk_sok, name="kodverk_sok"),
    #path("kodverk_sök/", views.kodverk_sök, name="kodverk_sök"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("kodverk_komplett_metadata/", views.kodverk_komplett_metadata, name="kodverk_komplett_metadata"),
    path("kodtext_json/", views.return_kodtext_as_json, name="kodtext_json"),
    path("table_language_translations/", views.return_translation_text, name="translation_text"),
    path("kodverk_export_file/", views.return_file_of_kodverk_and_kodtext, name="export_kodverk"),
    ]