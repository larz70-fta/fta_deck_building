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
    # ex: /build_finder/deckbot_action
    path('deckbot_action/', views.deckbot_action, name='deckbot_action'),
    # ex: /build_finder/<name of deck>
    path('<str:deck_name>/', views.detail, name='detail'),
]
