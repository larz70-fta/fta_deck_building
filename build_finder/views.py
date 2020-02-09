# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 17:58:59 2020

@author: larry
"""

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Deck


def index(request):
    latest_decks_list = Deck.objects.order_by('-create_date')[:5]
    context = {
        'latest_decks_list': latest_decks_list,
        }
    return render(request, 'build_finder/index.html', context)

def detail(request, deck_id):
    deck = get_object_or_404(Deck, pk=deck_id)
    return render(request, 'build_finder/detail.html', {'deck': deck})