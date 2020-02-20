# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 17:58:59 2020

@author: larry
"""

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Deck
from .models import Cards

from django.db.models import Q
import pandas as pd


def index(request):
    name_query = request.GET.get('n')
    author_query = request.GET.get('a')
    card_query = request.GET.get('c')
    
    if name_query is None:
        d = Deck.objects.filter(id__gt=0)
    else:
        d = Deck.objects.filter(Q(deck_name__icontains=name_query))
    
    if author_query is not None:
        d = d.filter(Q(deck_author__icontains=author_query))
    
    if card_query is not None:
        c = Cards.objects.filter(Q(card_name__icontains=card_query))
        d = Deck.objects.filter(Q(card1__in=c) |
                                Q(card2__in=c) |
                                Q(card3__in=c) |
                                Q(card4__in=c) |
                                Q(card5__in=c) |
                                Q(card6__in=c) |
                                Q(card7__in=c) |
                                Q(card8__in=c) |
                                Q(card9__in=c) |
                                Q(card10__in=c)
                                )
        
    latest_decks_list = d.order_by('-create_date')[:20]
    context = {
        'latest_decks_list': latest_decks_list,
        }
    return render(request, 'build_finder/index.html', context)

def detail(request, deck_name):
    #deck = get_object_or_404(Deck, pk=deck_id)
    if deck_name.isnumeric():
        pk_id = int(deck_name)
    else:
        decks = Deck.objects.filter(deck_name__icontains=deck_name)
        if len(decks) > 0:
            pk_id = decks[0].id
        else:
            pk_id = 0
        
    deck = get_object_or_404(Deck, pk=pk_id)    
    
    card_list = [deck.card1, deck.card2, deck.card3, deck.card4, deck.card5,
                  deck.card6, deck.card7, deck.card8, deck.card9, deck.card10]
    cards = Cards.objects.filter(card_name__in = card_list)
    context = {
        'deck': deck,
        'cards': cards,
        }
    return render(request, 'build_finder/detail.html', context)

def search(request):
    name_query = request.GET.get('n')
    
    if name_query is None:
        decks = Deck.objects.filter(id__gt=0)
    else:
        if name_query.isnumeric():
            pk_id = int(name_query)
        else:    
            decks = Deck.objects.filter(Q(deck_name__icontains=name_query))
            if len(decks) > 0:
                pk_id = decks[0].id
            else:
                pk_id = 0
        
    deck = get_object_or_404(Deck, pk=pk_id)    

    card_list = [deck.card1, deck.card2, deck.card3, deck.card4, deck.card5,
                  deck.card6, deck.card7, deck.card8, deck.card9, deck.card10]
    cards = Cards.objects.filter(card_name__in = card_list)
        
    context = {
        'deck': deck,
        'cards': cards,
        }
    return render(request, 'build_finder/mtgpq_deck_search.html', context)

