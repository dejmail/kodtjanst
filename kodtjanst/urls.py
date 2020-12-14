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
    path("ajax/table_language_translations/", views.return_translation_text, name="translation_text"),
    path("kodverk_export_file/<kodverk_id>/", views.return_file_of_kodverk_and_kodtext, name="export_kodverk"),
    path("kodverk_verify_comment/", views.kodverk_verify_comment, name="verify_comment_form"),
    path("ajax/kodtext_elements/<kodverk_id>/", views.load_kodtext, name="load_kodtext"),

    ]