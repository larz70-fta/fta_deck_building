from django.db import models
from django.utils import timezone
import datetime

# Create your models here.


class Cards(models.Model):
    #question = models.ForeignKey(Question, on_delete=models.CASCADE)
    card_name = models.CharField(max_length=100)
    card_number = models.IntegerField(default=0)
    card_text = models.CharField(max_length=256, null = True)
    card_set = models.CharField(max_length=100)
    card_rarity = models.CharField(max_length=20)
    card_type = models.CharField(max_length=20)
    card_color = models.CharField(max_length=20, null = True)
    card_cost = models.IntegerField(default=0)
    card_power = models.IntegerField(default=0, null = True)
    card_toughness = models.IntegerField(null = True)
    card_shield = models.IntegerField(null = True)
    card_image = models.CharField(max_length=100)
    
    def __str__(self):
        return self.card_name
    
    # how to save a name without spaces, punctuations and special characters
    # re.sub('[^A-Za-z0-9]+', '', <string variable>)
    
class Deck(models.Model):
    deck_name = models.CharField(max_length=50)
    deck_author = models.CharField(max_length=50)
    create_date = models.DateTimeField(default=timezone.now())
    game_version = models.CharField(max_length=10, default="1.0")
    deck_description = models.CharField(max_length=500)
    deck_PW = models.CharField(max_length=100, default="All")
    deck_video_link = models.CharField(max_length=100, default="None")
    card1 = models.ForeignKey(Cards, on_delete=models.CASCADE,
                              related_name="%(app_label)s_%(class)s_card1")
    card2 = models.ForeignKey(Cards, on_delete=models.CASCADE,
                              related_name="%(app_label)s_%(class)s_card2")
    card3 = models.ForeignKey(Cards, on_delete=models.CASCADE,
                              related_name="%(app_label)s_%(class)s_card3")
    card4 = models.ForeignKey(Cards, on_delete=models.CASCADE,
                              related_name="%(app_label)s_%(class)s_card4")
    card5 = models.ForeignKey(Cards, on_delete=models.CASCADE,
                              related_name="%(app_label)s_%(class)s_card5")
    card6 = models.ForeignKey(Cards, on_delete=models.CASCADE,
                              related_name="%(app_label)s_%(class)s_card6")
    card7 = models.ForeignKey(Cards, on_delete=models.CASCADE,
                              related_name="%(app_label)s_%(class)s_card7")
    card8 = models.ForeignKey(Cards, on_delete=models.CASCADE,
                              related_name="%(app_label)s_%(class)s_card8")
    card9 = models.ForeignKey(Cards, on_delete=models.CASCADE,
                              related_name="%(app_label)s_%(class)s_card9")
    card10 = models.ForeignKey(Cards, on_delete=models.CASCADE,
                              related_name="%(app_label)s_%(class)s_card10")
    
    def __str__(self):
        return self.deck_name
    
    def recent_decks(self):
        return self.create_date >= timezone.now() - datetime.timedelta(days = 7)

