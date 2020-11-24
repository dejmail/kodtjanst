from django.contrib import admin
from django.urls import path

from kodtjanst import views


urlpatterns = [
    path("", views.kodverk_sok, name="kodverk_sok"),
    #path("kodverk_sök/", views.kodverk_sök, name="kodverk_sök"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("kodverk_komplett_metadata/", views.kodverk_komplett_metadata, name="kodverk_komplett_metadata"),
    ]