# -*- coding: utf-8 -*-
from django.urls import path

from . import views

app_name = 'find_deck'
urlpatterns = [
    # ex: /find_deck
    path('', views.find_deck, name='find_deck'),
]
