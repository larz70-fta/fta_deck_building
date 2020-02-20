# -*- coding: utf-8 -*-
from rest_framework import serializers
from build_finder.models import Deck

class DeckNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Deck 
        fields = ('deck_name')

class DeckImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Deck 
        fields = ('deck_name', 'deck_author', 'card1', 'card2', 'card3',
                  'card4', 'card5', 'card6', 'card7', 'card8', 'card9', 'card10')