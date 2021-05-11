from django.contrib import admin
from django.urls import path

from kodtjanst import views


urlpatterns = [
    path("", views.kodverk_sok, name="kodverk_sok"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("kodverk/metadata-och-kodtext/", views.kodverk_komplett_metadata, name="kodverk_komplett_metadata"),
    path("kodtext/as-json/", views.return_kodtext_as_json, name="kodtext_json"),
    path("kodtext-table-translations/", views.return_translation_text, name="translation_text"),
    path("kodverk/download/<kodverk_id>/", views.return_file_of_kodverk_and_kodtext, name="export_kodverk"),
    path("kodverk/kommentar/", views.kodverk_verify_comment, name="verify_comment_form"),
    path("admin/ajax/kodtext-elements/<kodverk_id>/", views.load_kodtext, name="load_kodtext"),
    path("kodverk/previous-codeconcept-values/", views.previous_codeconcept_values_json, name="json_codeconcept_values"),
    path("kodverk/alla", views.all_kodverk_and_kodtext_as_json, name="alla_kodverk"),
    path('unread_comments/', views.return_number_of_recent_comments, name='unread_comments'),


    ]