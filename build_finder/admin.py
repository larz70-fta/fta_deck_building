from django.contrib import admin

# Register your models here.

from .models import Deck

class DeckAdmin(admin.ModelAdmin):
    fields=['deck_name', 'deck_author', 'create_date', 'deck_description',
            'deck_PW', 'game_version', 'deck_video_link',
            'card1', 'card2', 'card3', 'card4', 'card5',
            'card6', 'card7', 'card8', 'card9', 'card10']
    list_display = ('deck_name', 'deck_author', 'deck_description')
    list_filter = ['deck_author']
    search_fields = ['deck_name']

admin.site.register(Deck, DeckAdmin)
