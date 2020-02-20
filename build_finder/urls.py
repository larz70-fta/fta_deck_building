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
    # ex: /build_finder/mtgpq_deck_search
    path('mtgpq_deck_search/', views.search, name='mtgpq_deck_search'),
    # ex: /build_finder/DeckFinderBot
    path('deckfinderbot/', views.search, name='deckfinderbot'),
    # ex: /build_finder/<name of deck>
    path('<str:deck_name>/', views.detail, name='detail'),
]