from django.contrib import admin
from django.urls import path

from kodtjanst import views as kodverk_views


urlpatterns = [
    path("", kodverk_views.kodverk_view, name="kodverk"),
    path("kodverk_metadata/", kodverk_views.kodverk_metadata_view, name="kodverk_metadata"),
    path('login/', kodverk_views.login_view, name='login'),
    path('logout/', kodverk_views.logout_view, name='logout'),
    ]