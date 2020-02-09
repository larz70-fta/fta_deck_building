from django.db import models
from django.utils import timezone
import datetime

# Create your models here.

class Deck(models.Model):
    deck_name = models.CharField(max_length=50)
    deck_author = models.CharField(max_length=50)
    create_date = models.DateTimeField()
    deck_description = models.CharField(max_length=500)
    card1 = models.CharField(max_length=100)
    card2 = models.CharField(max_length=100)
    card3 = models.CharField(max_length=100)
    card4 = models.CharField(max_length=100)
    card5 = models.CharField(max_length=100)
    card6 = models.CharField(max_length=100)
    card7 = models.CharField(max_length=100)
    card8 = models.CharField(max_length=100)
    card9 = models.CharField(max_length=100)
    card10 = models.CharField(max_length=100)
    
    def __str__(self):
        return self.deck_name
    
    def recent_decks(self):
        return self.create_date >= timezone.now() - datetime.timedelta(days = 7)


class Cards(models.Model):
    #question = models.ForeignKey(Question, on_delete=models.CASCADE)
    card_name = models.CharField(max_length=100)
    card_set = models.CharField(max_length=100)
    card_type = models.CharField(max_length=20)
    card_rarity = models.CharField(max_length=20)
    card_mana_cost = models.IntegerField()
    card_shield = models.IntegerField(default=0)
    card_image = models.CharField(max_length=20)
    
    def __str__(self):
        return self.card_name