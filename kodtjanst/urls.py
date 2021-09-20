from django.contrib import admin
from django.urls import path, re_path, include
import debug_toolbar

from kodtjanst import views
from .rss_feed import SenasteKodverkFlöde, ÄndringariKodverkFlöde


urlpatterns = [
    path("", views.kodverk_sok, name="kodverk_sok"),
    
    path("kodtext/as-json/", views.return_kodtext_as_json, name="kodtext_json"),
    path("kodtext-table-translations/", views.return_translation_text, name="translation_text"),

    path("kodverk/metadata-och-kodtext/<kodverk_id>/", views.kodverk_komplett_metadata, name="kodverk_komplett_metadata"),
    path("kodverk/download/<kodverk_id>/", views.return_file_of_kodverk_and_kodtext, name="export_kodverk"),
    path("kodverk/kommentar/", views.kodverk_verify_comment, name="verify_comment_form"),
    path("kodverk/historik/<str:id>/", views.show_kodverk_history, name="show_kodverk_history"),
    path("kodverk/previous-codeconcept-values/", views.previous_codeconcept_values_json, name="json_codeconcept_values"),
    path("kodverk/alla", views.all_kodverk_and_kodtext_as_json, name="alla_kodverk"),
    re_path(r'kodverk/delta/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/',views.content_changes_from_date, name="content_changes_from_date"),
    path('kodverk/rss/senaste', SenasteKodverkFlöde(), name="recently_published_kodverk"),
    path('kodverk/rss/andringar', ÄndringariKodverkFlöde(), name="recently_changed_kodverk"),

    path("admin/ajax/kodtext-elements/<kodverk_id>/", views.load_kodtext, name="load_kodtext"),

    path('unread_comments/', views.return_number_of_recent_comments, name='unread_comments'),
    ]