from slack_utils.decorators import slack_command

from .models import Deck
from .models import Cards
from django.db.models import Q

import urllib.request as urllib

import numpy as np
import cv2

import io
import math

def url_to_image(url):
    # download the image, convert to numpy
    # then read into opencv format
    resp = urllib.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    return image



@slack_command('/fd')
def fd_command(text, **kwargs):
    # remove * mrkdwn format ... for now.
    text = text.replace("*","")

    # Get the parameters from text
    # values are pipe delimited
    # format: Deck Name|Author
    params = text.split('|')
    # remove leading and trailing spaces
    for i in range(len(params)):
        params[i] = params[i].strip()
    # retrieve the cards
    c = []

    if (len(params) > 1):
        decks = Deck.objects.filter(Q(deck_name__icontains=params[0]) &
                                    Q(deck_author__icontains=params[1]))
    else:
        decks = Deck.objects.filter(Q(deck_name__icontains=params[0]))


    if len(decks) > 0:
        if len(decks) == 1:
            pk_id = decks[0].id
            deck = Deck.objects.get(id = pk_id)
            card_list = [deck.card1, deck.card2, deck.card3, deck.card4, deck.card5,
                      deck.card6, deck.card7, deck.card8, deck.card9, deck.card10]
            cards = Cards.objects.filter(card_name__in = card_list)
            message = '*' + deck.deck_name + '* was created by *' + deck.deck_author
            message = message + '* for *' + deck.deck_PW + '* using the following cards: \n' 
            for card in cards:
                message = message + card.card_name + '|'
        else:
            message = "%d decks found matching the name: \n" %len(decks)
            for deck in decks:
                message = message + '*' + deck.deck_name + '* by ' + deck.deck_author + '\n'
       
    else:
        message='Deck not found'

    #return message
    return { "response_type": "in_channel", 
             "text": message
            }


@slack_command('/find_deck')
def find_deck_command(text, **kwargs):
    # replace * with space
    text = text.replace("*","")
    
    # Get the parameters from text
    # values are pipe delimited
    # format: Deck Name|Author
    params = text.split('|')
    # remove leading and trailing spaces
    for i in range(len(params)):
        params[i] = params[i].strip()


    # kwargs contain the rest of the data
    slack_data = []
    for key, value in kwargs.items():
        slack_data.append("%s == %s" %(key, value))

    filepath = "fta_deck_building//static//build_finder//images//temp/"
    kwargs_file = filepath + 'kwargs.txt'
    f = open(kwargs_file, 'w+')
    f.write("text = %s\n" %text)
    for lines in slack_data:
        f.write("%s\n" %lines)
    f.close()

    if (len(params) > 1):
        decks = Deck.objects.filter(Q(deck_name__icontains=params[0]) &
                                    Q(deck_author__icontains=params[1]))
    else:
        decks = Deck.objects.filter(Q(deck_name__icontains=params[0]))

    if len(decks) > 0:
        if len(decks) > 1:
            # list matching decks
            message = "%d decks found matching the name: \n" %len(decks)
            for deck in decks:
                message = message + '*' + deck.deck_name + '* by ' + deck.deck_author + '\n'
            return { "response_type": "in_channel", 
                     "text": message
                    }
        else:
            pk_id = decks[0].id
            deck = Deck.objects.get(id = pk_id)
            card_list = [deck.card1, deck.card2, deck.card3, deck.card4, deck.card5,
                         deck.card6, deck.card7, deck.card8, deck.card9, deck.card10]
            cards = Cards.objects.filter(card_name__in = card_list)
            message = '*' + deck.deck_name + '* was created by *' + deck.deck_author
            message = message + '* for *' + deck.deck_PW + '* using the following cards: \n' 
            root_url = 'https://ftamtgpq.pythonanywhere.com/'
            image_url = ['', '', '', '', '', '', '', '', '', '']
            deck_image = np.zeros((500, 396, 3), dtype="uint8")
            for i in range(10):
                image_url[i] = root_url + cards[i].card_image
                image = url_to_image(image_url[i])
                row = math.floor(i / 2) * 100
                col = (i % 2) * 198
                deck_image[row:(row + 100),col:(col + 198)] = image

            filename = str(deck.id) + ".png"
            full_filename = filepath + filename
            cv2.imwrite(full_filename, deck_image)
            static_temp_url = "static/build_finder/images/temp/"
            deck_image_url = root_url + static_temp_url + filename
            if (deck.deck_video_link[:4] == "http"):
                video_link = deck.deck_video_link
            else:
                video_link = "No gameplay video available yet."

        # debug code to look at kwargs
        kwargs_file = filepath + 'kwargs.txt'
        f = open(kwargs_file, 'w+')
        for lines in slack_data:
            f.write("%s\n" %lines)
        f.close()

    else:
        return { "response_type": "ephemeral", "text": 'Deck not found' }

    return { "response_type": "in_channel",
            "blocks": [ 
                    { "type": "section", 
                      "text": { 
                        "type": "mrkdwn",
                        "text": message } 
                    },
                    { "type": "image", 
                      "image_url": deck_image_url,
                      "alt_text": deck.deck_name
                    },
                    { "type": "section", 
                      "text": { 
                        "type": "mrkdwn",
                        "text": deck.deck_description } 
                    },
                    { "type": "section", 
                      "text": { 
                        "type": "mrkdwn",
                        "text": video_link } 
                    }
                ] 
            }


@slack_command('/save_deck')
def save_deck_command(text, **kwargs):
    # save deck
    # Get the values from text
    # values are pipe delimited
    # format: Author|Name|PW|Description|card1|card2|...card10
    params = text.split('|')
    # remove leading and trailing spaces
    for i in range(len(params)):
        params[i] = params[i].strip()
    # retrieve the cards
    c = []
    for i in range(10):
        card = Cards.objects.filter(card_name__iexact = params[i + 4])
        if (len(card) == 0):
            card = Cards.objects.filter(card_name__icontains = params[i + 4])
        if len(card) == 1:
            c.append(card[0])
        elif len(card) > 1:
            message = "More than 1 matching card found with name %s." %params[i + 4]
            return { "response_type": "ephemeral", "text": message }
        else:
            message = "%s card not found." %params[i + 4]
            return { "response_type": "ephemeral", "text": message }

    d = Deck(deck_author = params[0], deck_name = params[1], deck_PW = params[2], deck_description = params[3], 
            card1 = c[0], card2 = c[1], card3 = c[2], card4 = c[3], card5 = c[4],
            card6 = c[5], card7 = c[6], card8 = c[7], card9 = c[8], card10 = c[9])
    try: 
        d.save()
    except:
        return { "response_type": "ephemeral", "text": "Failed to save deck :(. Contact Larz." }

    return { "response_type": "in_channel", "text": "Deck saved." }

@slack_command('/update_deck')
def update_deck_command(text, **kwargs):
    # save deck
    # Get the values from text
    # values are pipe delimited
    # format: Name|New Name|New PW|New Description|card1|card2|...card10
    params = text.split('|')
    number_of_params = len(params)
    # remove leading and trailing spaces
    for i in range(number_of_params):
        params[i] = params[i].strip()

    # retrieve the deck,  Only 1 deck must match the query
    d = Deck.objects.filter(deck_name__icontains = params[0])
    if (len(d) == 0):
        return { "response_type": "ephemeral", "text": "Deck not found." }
    elif (len(d) > 1):
        return { "response_type": "ephemeral", "text": "More than 1 matching deck found." }

    d = Deck.objects.get(id = d[0].id)
    if (number_of_params > 1 and params [1] != ""):
        d.deck_name = params[1]
    if (number_of_params > 2 and params[2] != ""):
        d.deck_PW = params[2]
    if ( number_of_params > 3 and params[3] != ""):
        d.deck_description = params[3]
    if (number_of_params > 4):
        # retrieve the cards
        c = []
        for i in range(10):
            card = Cards.objects.filter(card_name__iexact = params[i + 4])
            if (len(card) == 0):
                card = Cards.objects.filter(card_name__icontains = params[i + 4])
            if len(card) > 0:
                c.append(card[0])
            elif len(card) > 1:
                message = "More than 1 matching card found with name %s." %params[i + 4]
                return { "response_type": "ephemeral", "text": message }
            else:
                message = "%s card not found." %params[i + 4]
                return { "response_type": "ephemeral", "text": message }

        d.card1 = c[0]
        d.card2 = c[1]
        d.card3 = c[2]
        d.card4 = c[3]
        d.card5 = c[4]
        d.card6 = c[5]
        d.card7 = c[6]
        d.card8 = c[7]
        d.card9 = c[8]
        d.card10 = c[9]

    try: 
        d.save()
    except:
        return { "response_type": "ephemeral", "text": "Failed to update deck :(. Contact Larz." }

    return { "response_type": "in_channel", "text": "Deck updated." }

@slack_command('/decks_with')
def decks_with_command(text, **kwargs):
    cards = Cards.objects.filter(card_name__icontains = text)
    message = ""
    if (len(cards) > 0):
        for card in cards:
            message = message + "*" + card.card_name + "*"
            decks = Deck.objects.filter(Q(card1__card_name=card) | Q(card2__card_name=card) |
                    Q(card3__card_name=card) | Q(card4__card_name=card) | Q(card5__card_name=card) |
                    Q(card6__card_name=card) | Q(card7__card_name=card) | Q(card8__card_name=card) |
                    Q(card9__card_name=card) | Q(card10__card_name=card)
                    )
            if (len(decks) > 0):
                message = message + " can be found in decks: \n"
                for deck in decks:
                    message = message + "*" + deck.deck_name + "* by " + deck.deck_author + "\n"
            else:
                message = message + " is not in any decks right now.\n"
                     
    else:
        message = "Card not found."

    return { "response_type": "in_channel", "text": message }

@slack_command('/recently_added_decks')
def recently_added_decks_command(text, **kwargs):
    try: 
        limit = int(text)
    except:
        return { "response_type": "ephemeral", "text": "Send a valid number to limit the results." }

    d = Deck.objects.all().order_by('-create_date')[:limit]
    message = ""
    for i in range(len(d)):
        message = message + "*" + d[i].deck_name + "* by " + d[i].deck_author + "\n"

    return { "response_type": "in_channel", "text": message }
