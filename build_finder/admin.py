from django.contrib import admin

# Register your models here.

from .models import Deck
from .models import Cards

class DeckAdmin(admin.ModelAdmin):
    fields=['deck_name', 'deck_author', 'create_date', 'deck_description',
            'deck_PW', 'game_version', 'deck_video_link',
            'card1', 'card2', 'card3', 'card4', 'card5',
            'card6', 'card7', 'card8', 'card9', 'card10']
    list_display = ('deck_name', 'deck_author', 'deck_description')
    list_filter = ['deck_author']
    search_fields = ['deck_name']

class CardAdmin(admin.ModelAdmin):
    fields=['card_name', 'card_number', 'card_text', 'card_set',
            'card_rarity', 'card_type', 'card_color', 'card_cost',
            'card_power', 'card_toughness', 'card_shield',
            'card_image']
    list_display = ('card_name', 'card_set', 'card_rarity', 'card_type', 'card_cost', 'card_text')
    list_filter = ['card_set']
    search_fields = ['card_name']

admin.site.register(Deck, DeckAdmin)
admin.site.register(Cards, CardAdmin)
