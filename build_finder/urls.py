# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 18:00:43 2020

@author: larry
"""

from django.urls import path

from . import views

app_name = 'build_finder'
urlpatterns = [
    # ex: /build_finder
    path('', views.index, name='index'),
    # ex: /build_finder/1
    path('<int:deck_id>/', views.detail, name='detail'),
]