from slack_utils.decorators import slack_command
from slack_utils.decorators import slack_receiver
import slack

from .models import Deck
from .models import Cards
from .models import Combo
from django.db.models import Q

import urllib.request as urllib

import numpy as np
from random import choices
import cv2

import os
import math

from datetime import datetime
from datetime import timedelta

import pandas as pd
import requests
from bs4 import BeautifulSoup

SLACK_TOKEN = os.getenv("FTA_SLACK_TOKEN")

def url_to_image(url):
    # download the image, convert to numpy
    # then read into opencv format
    resp = urllib.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    return image


def generate_deck_image(cards, deck_id):
    root_url = 'https://ftamtgpq.pythonanywhere.com/'
    image_url = ['', '', '', '', '', '', '', '', '', '']
    deck_image = np.zeros((500, 396, 3), dtype="uint8")
    for i in range(10):
        image_url[i] = root_url + cards[i].card_image
        image = url_to_image(image_url[i])
        row = math.floor(i / 2) * 100
        col = (i % 2) * 198
        deck_image[row:(row + 100),col:(col + 198)] = image

    filepath = "fta_deck_building//static//build_finder//images//temp/"
    filename = str(deck_id) + ".png"
    full_filename = filepath + filename
    cv2.imwrite(full_filename, deck_image)
    static_temp_url = "static/build_finder/images/temp/"
    deck_image_url = root_url + static_temp_url + filename
    return(deck_image_url)

def search_decks(text, search_type):
    # replace * with space
    text = text.replace("*","")
    text = text.replace("|"," ")

    params = list(filter(None, text.split(' ')))

    if search_type == "search_fields":
        decks = Deck.objects.all()
        for param in params:
            d = Deck.objects.filter(Q(deck_PW__icontains = param) |
                                    Q(deck_author__icontains = param) |
                                    Q(deck_name__icontains = param)
                                   )
            decks = decks.intersection(d)
    elif search_type == "search_cards":
        decks = Deck.objects.none()
        cards = Cards.objects.none()
        for word in params:
            c = Cards.objects.filter(card_name__icontains = word)
            cards = cards.union(c)

        if (len(cards) > 0):
            for card in cards:
                d = Deck.objects.filter(Q(card1__card_name=card) | Q(card2__card_name=card) |
                    Q(card3__card_name=card) | Q(card4__card_name=card) | Q(card5__card_name=card) |
                    Q(card6__card_name=card) | Q(card7__card_name=card) | Q(card8__card_name=card) |
                    Q(card9__card_name=card) | Q(card10__card_name=card)
                    )
                decks = decks.union(d)
    elif search_type == "both":
        decks = Deck.objects.all()
        for word in params:
            d = Deck.objects.filter(Q(deck_PW__icontains = word) |
                                    Q(deck_author__icontains = word) |
                                    Q(deck_name__icontains = word)
                                   )
            decks = decks.intersection(d)

        cards = Cards.objects.none()
        for word in params:
            c = Cards.objects.filter(card_name__icontains = word)
            cards = cards.union(c)

        if (len(cards) > 0):
            for card in cards:
                d = Deck.objects.filter(Q(card1__card_name=card) | Q(card2__card_name=card) |
                    Q(card3__card_name=card) | Q(card4__card_name=card) | Q(card5__card_name=card) |
                    Q(card6__card_name=card) | Q(card7__card_name=card) | Q(card8__card_name=card) |
                    Q(card9__card_name=card) | Q(card10__card_name=card)
                    )
                decks = decks.union(d)
    else :
        decks = Deck.objects.none()

    return(decks)

def format_deck_search_result_message(decks, text, page):
    # format search result with a max of 5 decks per page.
    start = 0 + 5*(page-1)
    end = start + 5
    if start >= len(decks):
        start = math.floor((len(decks)-1)/5) * 5
        # adjust page number
        end = start + 5
        page = end / 5
    if end > len(decks):
        end = len(decks)
    blocks = []
    total_pages = math.ceil(len(decks)/5)
    message = "%d decks found matching the name %s \nPage %d of %d" %(len(decks), text, page, total_pages)
    blocks.append({'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': message
            }})
    for i in range(start, end):
        deck = decks[i]

        formatted_deck_name = deck.deck_name.replace(" ", "%20")
        deck_url = "https://ftamtgpq.pythonanywhere.com/build_finder/%s" %formatted_deck_name
        message = "*<%s|%s>*\nAuthor: %s\nPW(s): %s\n" %(deck_url, deck.deck_name, deck.deck_author, deck.deck_PW)

        # check if deck image exists. if it doesn't create image
        filepath = "fta_deck_building//static//build_finder//images//temp/"
        filename = str(deck.id) + ".png"
        full_filename = filepath + filename
        if not os.path.exists(full_filename):
            # create deck image
            card_list = [deck.card1, deck.card2, deck.card3, deck.card4, deck.card5,
                         deck.card6, deck.card7, deck.card8, deck.card9, deck.card10]
            generate_deck_image(card_list, deck.id)

        root_url = 'https://ftamtgpq.pythonanywhere.com/'
        static_temp_url = "static/build_finder/images/temp/"
        filename = str(deck.id) + ".png"
        deck_image_url = root_url + static_temp_url + filename

        blocks.append({'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': message
                },
                'accessory': {
                    'type': 'image',
                    'image_url': deck_image_url,
                    'alt_text': deck.deck_description}
                })
        blocks.append({'type': 'divider'})
    # add previous or next results button
    if start > 0 or end < len(decks):
        action = {'type': 'actions'}
        elements = []
        if start > 0:
            # add previous button
            elements.append({'type': 'button',
                'text': {
                    'type': 'plain_text',
                    'emoji': True,
                    'text': 'Previous'
                    },
                'value': text + " " + str(page-1)
                })
        if end < len(decks):
            # add next button
            elements.append({'type': 'button',
                'text': {
                    'type': 'plain_text',
                    'emoji': True,
                    'text': 'Next'
                    },
                'value': text + " " + str(page+1)
                })
        action['elements'] = elements
        blocks.append(action)

    return(blocks)

def write_to_debug_file(file_name, content):
    filepath = "fta_deck_building//static//build_finder//images//temp/"
    fn = filepath + file_name
    f = open(fn, 'w')
    f.write(content)
    f.close()

def pad(text, pad):
    padding = ' ' * pad
    text = (text + padding)[0:20]
    return(text)

def iko_sim(plsim, n, gr_n):
    common_rate = 1 - (1 - .9796) ** (1 / 5)
    uncommon_rate = 1 - (1 - .9158) ** (1 / 5)
    rare_rate = 1 - (1 - .7486) ** (1 / 25)
    mythic_rate = 1 - (1 - .3029) ** (1 / 25)
    masterpiece_rate = 1 - (1 - .0178) ** (1 / 25)

    common_cards = (Cards.objects.filter(Q(card_rarity__exact = 'Common') & Q(card_set__exact = 'IKO')))
    uncommon_cards = (Cards.objects.filter(Q(card_rarity__exact = 'Uncommon') & Q(card_set__exact = 'IKO')))
    rare_cards = (Cards.objects.filter(Q(card_rarity__exact = 'Rare') & Q(card_set__exact = 'IKO')))
    mythic_cards = (Cards.objects.filter(Q(card_rarity__exact = 'Mythic') & Q(card_set__exact = 'IKO')))
    masterpiece_cards = (Cards.objects.filter(Q(card_rarity__exact = 'Masterpiece') & Q(card_set__exact = 'IKO')))

    card_num_array = []
    card_rate_array = []
    for card in common_cards:
        card_num_array.append([card.card_name, card.card_rarity])
        card_rate_array.append(common_rate/65)
    for card in uncommon_cards:
        card_num_array.append([card.card_name, card.card_rarity])
        card_rate_array.append(uncommon_rate/60)
    for card in rare_cards:
        card_num_array.append([card.card_name, card.card_rarity])
        card_rate_array.append(rare_rate/40)
    for card in mythic_cards:
        card_num_array.append([card.card_name, card.card_rarity])
        card_rate_array.append(mythic_rate/30)
    for card in masterpiece_cards:
        card_num_array.append([card.card_name, card.card_rarity])
        card_rate_array.append(masterpiece_rate/15)

    # set exclusives rate to zero
    #rares
    card_rate_array[125] = 0
    card_rate_array[126] = 0
    card_rate_array[127] = 0
    card_rate_array[128] = 0
    card_rate_array[132] = 0
    card_rate_array[134] = 0
    card_rate_array[136] = 0
    card_rate_array[142] = 0
    card_rate_array[152] = 0
    card_rate_array[159] = 0
    card_rate_array[164] = 0
    card_rate_array[166] = 0
    card_rate_array[168] = 0
    card_rate_array[170] = 0
    card_rate_array[171] = 0
    card_rate_array[173] = 0
    card_rate_array[174] = 0
    card_rate_array[177] = 0
    #mythics
    card_rate_array[202] = 0
    card_rate_array[206] = 0
    card_rate_array[208] = 0
    card_rate_array[212] = 0
    card_rate_array[217] = 0

    cards = np.array(card_num_array)
    rate = np.array(card_rate_array)

    # randomize n number of cards
    booster_pack = choices(np.arange(len(cards)), weights=rate, k=n)
#    message = ""
#    dup_count = 0
#    for i in booster_pack:
#        if (plsim.loc[i,'amt'] == 0):
#            if i > 124:
#                message = message + "*New %s - %s *\n" %(cards[i][1], cards[i][0])
#        else:
#            if i > 124:
#                message = message + "Dup %s - %s \n" %(cards[i][1], cards[i][0])
#            dup_count = dup_count + 1
#    if len(booster_pack) > 0:
#        message = "%sOpened %d duplicates.\n" %(message, dup_count)

    # id new and dup ones and update inventory
    for i in booster_pack:
        plsim.loc[i,'amt'] = plsim.loc[i,'amt'] + 1

    if gr_n > 0:
        #message = message + "Guaranteed Rare: \n"
        rare_card_num_array = card_num_array[125:182]
        rare_card_rate_array = card_rate_array[125:182]

        gr_cards = np.array(rare_card_num_array)
        gr_rate = np.array(rare_card_rate_array)
        # adjust rates so that they sum up to 1
        # rate = rate / sum(rate)
        # rate[len(rate)-1] = 1 - sum(rate[0:len(rate)-1])

        booster_pack = choices(np.arange(len(gr_cards)), weights = gr_rate, k=gr_n)
#        for i in booster_pack:
#            if (plsim.loc[i+125,'amt'] == 0):
#                message = message + "*New %s - %s *\n" %(gr_cards[i][1], gr_cards[i][0])
#            else:
#                message = message + "Dup %s - %s \n" %(gr_cards[i][1], gr_cards[i][0])

        for i in booster_pack:
            plsim.loc[i+125,'amt'] = plsim.loc[i+125,'amt'] + 1

    return(plsim, cards, rate)

def format_bp_sim_inventory_message(plsim, cards, rate):
    # show inventory
    c_arr = plsim.loc[0:64,]
    u_arr = plsim.loc[65:124,]
    r_arr = plsim.loc[125:182,]
    m_arr = plsim.loc[183:217,]
    mp_arr = plsim.loc[218:232,]
    c_count = len(c_arr[c_arr.amt > 0])
    u_count = len(u_arr[u_arr.amt > 0])
    r_count = len(r_arr[r_arr.amt > 0])
    m_count = len(m_arr[m_arr.amt > 0])
    mp_count = len(mp_arr[mp_arr.amt > 0])
    c_dup = c_arr.amt.sum() - c_count
    u_dup = u_arr.amt.sum() - u_count
    r_dup = r_arr.amt.sum() - r_count
    m_dup = m_arr.amt.sum() - m_count
    mp_dup = mp_arr.amt.sum() - mp_count

    orbs_count = c_dup * 15 + u_dup * 30 + r_dup * 150 + m_dup * 750 + mp_dup * 3750
    crystals_count = plsim.amt[233]
    PPs_bought = plsim.amt[234]

    message = ""
    message = message + "Inventory: \n"
    message = message + '```    Common  Uncommon  Rare  Mythic  Masterpiece  Crystals Spent\n'
    message = "%s    %6d %9d %5d %7d %12d %15d \n" %(message, c_count, u_count, r_count, m_count, mp_count, crystals_count)
    message = message + '```\n'

    message = message + "Duplicates: \n"
    message = message + '```    Common  Uncommon  Rare  Mythic  Masterpiece     Orbs\n'
    message = "%s    %6d %9d %5d %7d %12d %8d  \n" %(message, c_dup, u_dup, r_dup, m_dup, mp_dup, orbs_count)
    message = message + '```\n'

    # display rates:
    total_count = plsim.loc[0:232,'amt'].sum() - PPs_bought
    c_rate = (c_count + c_dup) / total_count * 100
    u_rate = (u_count + u_dup) / total_count * 100
    r_rate = (r_count + r_dup - PPs_bought) / total_count * 100
    m_rate = (m_count + m_dup) / total_count * 100
    mp_rate = (mp_count + mp_dup) / total_count * 100

    common_rate = 1 - (1 - .9796) ** (1 / 5)
    uncommon_rate = 1 - (1 - .9158) ** (1 / 5)
    rare_rate = 1 - (1 - .7486) ** (1 / 25)
    mythic_rate = 1 - (1 - .3029) ** (1 / 25)
    masterpiece_rate = 1 - (1 - .0178) ** (1 / 25)

    message = message + "Actual Rates over Advertised Rates (in percent): \n"
    message = message + '```             Common  Uncommon  Rare  Mythic  Masterpiece\n'
    message = "%s Actual:     %6.2f %9.2f %5.2f %7.2f %12.2f \n" %(message, c_rate, u_rate, r_rate, m_rate, mp_rate)
    message = "%s Advertised: %6.2f %9.2f %5.2f %7.2f %12.2f \n" %(message, common_rate*100, uncommon_rate*100,
            rare_rate*100, mythic_rate*100, masterpiece_rate*100)
    message = message + '```\n'

    message = message + "Mythics owned: \n"
    for i in range(183,218):
        if (plsim.loc[i,'amt'] > 0):
            if (plsim.loc[i,'amt'] == 1):
                message = message + "     %s - pulled once \n" %(cards[i][0])
            else:
                message = message + "     %s - pulled %s times \n" %(cards[i][0], plsim.loc[i,'amt'])

    message = message + "Masterpieces owned: \n"
    for i in range(218,233):
        if (plsim.loc[i,'amt'] > 0):
            if (plsim.loc[i,'amt'] == 1):
                message = message + "     %s - pulled once \n" %(cards[i][0])
            else:
                message = message + "     %s - pulled %s times \n" %(cards[i][0], plsim.loc[i,'amt'])

    return(message)

@slack_command('/fd')
def fd_command(text, **kwargs):
    decks = search_decks(text, "search_fields")

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
            block = format_deck_search_result_message(decks, text, 1)
            return {"response_type": "in_channel",
                    "blocks": block
                    }

    else:
        message='Deck not found'

    #return message
    return { "response_type": "in_channel",
             "text": message
            }

def get_all_decks(text, index):
    # replace * with space
    text = text.replace("*","")
    text = text.replace("|"," ")

    #params = text.split('|')
    # remove leading and trailing spaces
    #for i in range(len(params)):
        #params[i] = params[i].strip()


    params = list(filter(None, text.split(' ')))
    # remove leading and trailing spaces
    #for i in range(len(params)):
    #    params[i] = params[i].strip()

    decks = Deck.objects.all()
    for param in params:
        d = Deck.objects.filter(Q(deck_PW__icontains = param) |
                                Q(deck_author__icontains = param) |
                                Q(deck_name__icontains = param)
                               )
        decks = decks.intersection(d)

    #if (len(params) > 0):
    #if (len(params) == 2):
        #decks = Deck.objects.filter(Q(deck_name__icontains=params[0]) &
                                    #Q(deck_author__icontains=params[1]))
    #elif (len(params) == 3):
        #decks = Deck.objects.filter(Q(deck_name__icontains=params[0]) &
                                    #Q(deck_author__icontains=params[1]) &
                                    #Q(deck_PW__icontains=params[2]))
    #else:
        #decks = Deck.objects.filter(Q(deck_name__icontains=params[0]))

    if len(decks) > 0:
        message = "Deck %d of %d \n" %(index + 1, len(decks))

        pk_id = decks[index].id
        deck = Deck.objects.get(id = pk_id)
        #card_list = [deck.card1, deck.card2, deck.card3, deck.card4, deck.card5,
        #             deck.card6, deck.card7, deck.card8, deck.card9, deck.card10]
        #cards = Cards.objects.filter(card_name__in = card_list)
        message = message + '*' + deck.deck_name + '* was created by *' + deck.deck_author
        message = message + '* for *' + deck.deck_PW + '* using the following cards: \n'

        root_url = 'https://ftamtgpq.pythonanywhere.com/'
        static_temp_url = "static/build_finder/images/temp/"
        filename = str(deck.id) + ".png"
        deck_image_url = root_url + static_temp_url + filename

        if (deck.deck_video_link[:4] == "http"):

            video_link = deck.deck_video_link
        else:
            video_link = "No gameplay video available yet."

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

def perform_deck_pagination(client, event_data, conv):
    debug_text = "Pagination conv data is: \n %s \n" %str(conv)
    write_to_debug_file("deck_pagination_conv.txt", debug_text)

    debug_text = "chat user is: %s \n" %(conv["user"])
    debug_text = debug_text + "text is: %s \n" %(conv["text"])
    if (conv["user"] == "UTXGRH21Y"):
        message = conv["text"]
        # don't split on 'deck' because the deck name might contain the word deck itself
        # use rfind instead to find the last instance of word 'deck' and extract the deck name and num from it
        deck_loc = message.rfind('deck')

        if deck_loc != -1:
            deck_name = message[0:deck_loc - 1]
            deck_num = message[deck_loc + 5:len(message)].split(" of ")
            if len(deck_num) == 2:
                if (deck_num[0].isnumeric() and deck_num[1].isnumeric()):

                    debug_text = debug_text + "deck_name is: %s \n" %deck_name
                    debug_text = debug_text + "deck_index is: %d \n" %int(deck_num[0])
                    debug_text = debug_text + "deck_count is: %d \n" %int(deck_num[1])

                    debug_text = debug_text + "chat message timestamp is: %s \n" %event_data["item"]["ts"]

                    # update the message.:
                    #message = conv["text"]
                    #message_words = message.split(" deck ")
                    #deck_name = message_words[0]
                    #deck_num = message_words[1].split(" of ")
                    deck_index = int(deck_num[0]) - 1
                    deck_count = int(deck_num[1])

                    if (event_data["reaction"] == "arrow_left"):
                        deck_index = deck_index - 1
                        if (deck_index == -1):
                            deck_index = deck_count - 1
                    if (event_data["reaction"] == "arrow_right"):
                        deck_index = deck_index + 1
                        if deck_index == deck_count:
                            deck_index = 0

                    # update the message.
                    message = "%s deck %d of %d" %(deck_name, deck_index+1, deck_count)
                    get_result = get_all_decks(deck_name, deck_index)
                    client.chat_update(
                            channel = event_data["item"]["channel"],
                            ts = event_data["item"]["ts"],
                            text = message,
                            blocks = get_result["blocks"]
                            )

    write_to_debug_file("deck_pagination.txt", debug_text)


@slack_command('/find_deck')
def find_deck_command(text, **kwargs):
    # replace * with space
    text = text.replace("*","")
    text = text.replace("|"," ")

    # Get the parameters from text
    # values are pipe delimited
    # format: Deck Name|Author
    #params = text.split('|')
    # remove leading and trailing spaces
    #for i in range(len(params)):
        #params[i] = params[i].strip()


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

    params = list(filter(None, text.split(' ')))
    # remove leading and trailing spaces
    #for i in range(len(params)):
    #    params[i] = params[i].strip()

    decks = Deck.objects.all()
    for param in params:
        d = Deck.objects.filter(Q(deck_PW__icontains = param) |
                                Q(deck_author__icontains = param) |
                                Q(deck_name__icontains = param)
                               )
        decks = decks.intersection(d)
    #if (len(params) > 1):
        #decks = Deck.objects.filter(Q(deck_name__icontains=params[0]) &
                                    #Q(deck_author__icontains=params[1]))
    #else:
        #decks = Deck.objects.filter(Q(deck_name__icontains=params[0]))

    if len(decks) > 0:
        if len(decks) > 1:
            # list matching decks
            message = "%d decks found matching the name: \n" %len(decks)
            for deck in decks:
                formatted_deck_name = deck.deck_name.replace(" ", "%20")
                deck_url = "https://ftamtgpq.pythonanywhere.com/build_finder/%s" %formatted_deck_name
                message = "%s *<%s|%s>* by %s for %s\n" %(message, deck_url, deck.deck_name, deck.deck_author, deck.deck_PW)
            return { "response_type": "in_channel",
                     "text": message
                    }
        else:
            pk_id = decks[0].id
            deck = Deck.objects.get(id = pk_id)
            card_list = [deck.card1, deck.card2, deck.card3, deck.card4, deck.card5,
                         deck.card6, deck.card7, deck.card8, deck.card9, deck.card10]
            #cards = Cards.objects.filter(card_name__in = card_list)
            message = '*' + deck.deck_name + '* was created by *' + deck.deck_author
            message = message + '* for *' + deck.deck_PW + '* using the following cards: \n'

            # check if deck image exists. if it doesn't create image
            filepath = "fta_deck_building//static//build_finder//images//temp/"
            filename = str(deck.id) + ".png"
            full_filename = filepath + filename
            if not os.path.exists(full_filename):
                # create deck image
                generate_deck_image(card_list, deck.id)

            root_url = 'https://ftamtgpq.pythonanywhere.com/'
            static_temp_url = "static/build_finder/images/temp/"
            filename = str(deck.id) + ".png"
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
        return { "response_type": "in_channel", "text": 'Deck not found' }

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
        cn = params[i + 4].split("//")[0].strip()
        card = Cards.objects.filter(card_name__iexact = cn)
        if (len(card) == 0):
            card = Cards.objects.filter(card_name__icontains = cn)
        if len(card) == 1:
            c.append(card[0])
        elif len(card) > 1:
            message = "More than 1 matching card found with name %s." %cn
            return { "response_type": "ephemeral", "text": message }
        else:
            message = "%s card not found." %cn
            return { "response_type": "ephemeral", "text": message }

    d = Deck(deck_author = params[0], deck_name = params[1], deck_PW = params[2], deck_description = params[3],
            card1 = c[0], card2 = c[1], card3 = c[2], card4 = c[3], card5 = c[4],
            card6 = c[5], card7 = c[6], card8 = c[7], card9 = c[8], card10 = c[9])

    try:
        d.save()
    except:
        return { "response_type": "ephemeral", "text": "Failed to save deck :(. Contact Larz." }

    # generate and save deck_image
    generate_deck_image(c, d.id)
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

    # generate and save deck_image
    generate_deck_image(c, d.id)
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
                    formatted_deck_name = deck.deck_name.replace(" ", "%20")
                    deck_url = "https://ftamtgpq.pythonanywhere.com/build_finder/%s" %formatted_deck_name
                    message = "%s *<%s|%s>* by %s for %s\n" %(message, deck_url, deck.deck_name, deck.deck_author, deck.deck_PW)
            else:
                message = message + " is not in any decks right now.\n"

    else:
        message = "Card not found."

    return { "response_type": "in_channel", "text": message }

@slack_command('/show_decks_with')
def show_decks_with_command(text, **kwargs):
    text = text.replace("*","")
    text = text.replace("|"," ")
    words = list(filter(None, text.split(' ')))

    decks = Deck.objects.all()
    for word in words:
        d = Deck.objects.filter(Q(deck_PW__icontains = word) |
                                Q(deck_author__icontains = word) |
                                Q(deck_name__icontains = word)
                               )
        decks = decks.intersection(d)

    cards = Cards.objects.none()
    for word in words:
        c = Cards.objects.filter(card_name__icontains = word)
        cards = cards.union(c)

    if (len(cards) > 0):
        for card in cards:
            d = Deck.objects.filter(Q(card1__card_name=card) | Q(card2__card_name=card) |
                Q(card3__card_name=card) | Q(card4__card_name=card) | Q(card5__card_name=card) |
                Q(card6__card_name=card) | Q(card7__card_name=card) | Q(card8__card_name=card) |
                Q(card9__card_name=card) | Q(card10__card_name=card)
                )
            decks = decks.union(d)

    message = ""
    if (len(decks) == 0):
        message = "Deck not found."
    else:
        message = message + " can be found in decks: \n"
        for deck in decks:
            formatted_deck_name = deck.deck_name.replace(" ", "%20")
            deck_url = "https://ftamtgpq.pythonanywhere.com/build_finder/%s" %formatted_deck_name
            message = "%s *<%s|%s>* by %s for %s\n" %(message, deck_url, deck.deck_name, deck.deck_author, deck.deck_PW)

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

@slack_receiver('reaction_added')
def on_reaction_added(event_data, **kwargs):
    # your logic
    # kwargs contain the rest of the data
    slack_data = []
    for key, value in kwargs.items():
        slack_data.append("%s == %s" %(key, value))

    filepath = "fta_deck_building//static//build_finder//images//temp/"
    kwargs_file = filepath + 'reaction_added.txt'
    f = open(kwargs_file, 'w+')
    f.write("Event data follows:\n")
    f.write(str(event_data))
    f.write("\n")
    for lines in slack_data:
        f.write("%s\n" %lines)
    f.close()

    client = slack.WebClient(token=SLACK_TOKEN)

    # get message history, if user is not the bot id = UTXGRH21Y
    if (event_data["user"] != "UTXGRH21Y" and
            (   event_data["reaction"] == "arrow_left" or
                event_data["reaction"] == "arrow_right")
            ):
        conv = client.conversations_history(
            channel = event_data["item"]["channel"],
            latest = event_data["item"]["ts"],
            limit = 1,
            inclusive = 1
            )

        # debug conversation history
        # conversation must be created by bot and has the form <deck_name> deck x of y
        conv_file = filepath + 'conv_reaction_added.txt'
        f = open(conv_file, 'w+')
        f.write("Conversation data follows:\n")
        f.write(str(conv))
        f.write("\n")

        # conversations_history only returns the parent message
        # if the {{ }} command was given inside a thread, we'll need to look at the history
        # and find the thread containing the bot's output message

        # get the first (and should be only) message in conv
        conv_msg = conv["messages"][0]

        # check if this is the message matching the event_ts
        if conv_msg["ts"] != event_data["item"]["ts"]:
            # go through the history (right now, just hope that we get it the first time)
            # TODO - keep looking through all available history
            conv_hist = client.conversations_history(
                channel = event_data["item"]["channel"]
                )

            #look for the thread
            thread_found = False
            for msg in conv_hist["messages"]:
                if "reply_count" in msg.keys():
                    if msg["reply_count"] > 0:
                        f.write("Found a message with a thread. \n")
                        f.write("message_type: %s, ts: %s, text: %s \n" %(msg["type"], msg["ts"], msg["text"]))
                        thread = client.conversations_replies(
                            channel = event_data["item"]["channel"],
                            ts = msg["ts"]
                            )
                        #print(thread)
                        for reply in thread["messages"]:
                            f.write("message_type: %s, ts: %s, text: %s \n" %(reply["type"], reply["ts"], reply["text"]))
                            if reply["ts"] == event_data["item"]["ts"]:
                                f.write("Thread %s found. \n" %event_data["item"]["ts"])
                                thread_found = True
                                break
                if thread_found:
                    break

            # if thread, get the bot's reply

            f.write("Thread reply data follows:\n")
            f.write(str(reply))
            f.write("\n")
            f.close()

            perform_deck_pagination(client, event_data, reply)

        else:
            f.write("Not in thread, conv_msg follows:\n")
            f.write(str(conv_msg))
            f.write("\n")
            f.close()
            perform_deck_pagination(client, event_data, conv_msg)

        #f.close()

@slack_receiver('reaction_removed')
def on_reaction_removed(event_data, **kwargs):
    # your logic
    # kwargs contain the rest of the data
    slack_data = []
    for key, value in kwargs.items():
        slack_data.append("%s == %s" %(key, value))

    filepath = "fta_deck_building//static//build_finder//images//temp/"
    kwargs_file = filepath + 'reaction_removed.txt'
    f = open(kwargs_file, 'w+')
    f.write("Event data follows:\n")
    f.write(str(event_data))
    f.write("\n")
    for lines in slack_data:
        f.write("%s\n" %lines)
    f.close()

    client = slack.WebClient(token=SLACK_TOKEN)

    # get message history, if user is not the bot id = UTXGRH21Y
    if (event_data["user"] != "UTXGRH21Y" and
            (   event_data["reaction"] == "arrow_left" or
                event_data["reaction"] == "arrow_right")
            ):
        conv = client.conversations_history(
            channel = event_data["item"]["channel"],
            latest = event_data["item"]["ts"],
            limit = 1,
            inclusive = 1
            )

        # conversations_history only returns the parent message
        # if the {{ }} command was given inside a thread, we'll need to look at the history
        # and find the thread containing the bot's output message

        # debug conversation history
        conv_file = filepath + 'conv_reaction_removed.txt'
        f = open(conv_file, 'w+')
        f.write("Conversation data follows:\n")
        f.write(str(conv))
        f.write("\n")

        # get the first (and should be only) message in conv
        conv_msg = conv["messages"][0]

        # check if this is the message matching the event_ts
        if conv_msg["ts"] != event_data["item"]["ts"]:
            # go through the history (right now, just hope that we get it the first time)
            # TODO - keep looking through all available history
            conv_hist = client.conversations_history(
                channel = event_data["item"]["channel"]
                )

            #look for the thread
            thread_found = False
            for msg in conv_hist["messages"]:
                if "reply_count" in msg.keys():
                    if msg["reply_count"] > 0:
                        f.write("Found a message with a thread. \n")
                        f.write("message_type: %s, ts: %s, text: %s \n" %(msg["type"], msg["ts"], msg["text"]))
                        thread = client.conversations_replies(
                            channel = event_data["item"]["channel"],
                            ts = msg["ts"]
                            )
                        #print(thread)
                        for reply in thread["messages"]:
                            f.write("message_type: %s, ts: %s, text: %s \n" %(reply["type"], reply["ts"], reply["text"]))
                            if reply["ts"] == event_data["item"]["ts"]:
                                f.write("Thread %s found. \n" %event_data["item"]["ts"])
                                thread_found = True
                                break
                if thread_found:
                    break

            # if thread, get the bot's reply

            f.write("Thread reply data follows:\n")
            f.write(str(reply))
            f.write("\n")
            f.close()

            perform_deck_pagination(client, event_data, reply)

        else:
            f.write("Not in thread, conv_msg follows:\n")
            f.write(str(conv_msg))
            f.write("\n")
            f.close()
            perform_deck_pagination(client, event_data, conv_msg)

        #f.close()

@slack_receiver('app_mention')
def on_app_mention(event_data, **kwargs):
    # your logic
    # kwargs contain the rest of the data
    slack_data = []
    for key, value in kwargs.items():
        slack_data.append("%s == %s" %(key, value))

    filepath = "fta_deck_building//static//build_finder//images//temp/"
    kwargs_file = filepath + 'app_mention.txt'
    f = open(kwargs_file, 'w+')
    f.write("Event data follows:\n")
    f.write(str(event_data))
    f.write("\n")
    for lines in slack_data:
        f.write("%s\n" %lines)
    f.close()

    # Read text and get the words after deck
    client = slack.WebClient(token=SLACK_TOKEN)
    # check for {{ }}
    event_text = event_data["text"]
    start = event_text.find("{{")
    if start != -1:
        end = event_text.find("}}")

        deck_name = event_text[start+2:end]
        get_result = get_all_decks(deck_name, 0)
        if "blocks" in get_result.keys():
            result_message = get_result["blocks"][0]["text"]["text"]
            result_index = result_message.split(" ")
            message = "%s deck %s of %s" %(deck_name, result_index[1], result_index[3])
            block = get_result["blocks"]
            if "thread_ts" in event_data.keys():
                message_response = client.chat_postMessage(
                        channel=event_data["channel"],
                        text = message,
                        thread_ts = event_data["thread_ts"],
                        blocks = block
                        )
            else:
                message_response = client.chat_postMessage(
                        channel=event_data["channel"],
                        text = message,
                        blocks = block
                        )
            if int(result_index[3]) > 1:
                # Add arrow emojis
                client.reactions_add(
                    channel=event_data["channel"],
                    name = "arrow_left",
                    timestamp = message_response["ts"]
                    )
                client.reactions_add(
                    channel=event_data["channel"],
                    name = "arrow_right",
                    timestamp = message_response["ts"]
                    )
        else:
            message_response = client.chat_postMessage(
                    channel=event_data["channel"],
                    #response_type="ephemeral",
                    text = get_result["text"]
                    )

@slack_receiver('message.im')
def on_message_im(event_data, **kwargs):
    # your logic
    # kwargs contain the rest of the data
    slack_data = []
    for key, value in kwargs.items():
        slack_data.append("%s == %s" %(key, value))

    #filepath = "fta_deck_building//static//build_finder//images//temp/"
    #kwargs_file = filepath + 'message_im.txt'
    #f = open(kwargs_file, 'w+')
    #f.write("Event data follows:\n")
    #f.write(str(event_data))
    #f.write("\n")
    #f.write("Kwargs data follows\n")
    #for lines in slack_data:
        #f.write("%s\n" %lines)
    #f.close()

    fname = "message_im.txt"
    debug_text = "Event data follows:\n"
    debug_text = debug_text + (str(event_data)) + "\n" + "Kwargs data follows\n"
    for lines in slack_data:
        debug_text = debug_text + lines + "\n"
    write_to_debug_file(fname, debug_text)

    # Read text and get the words after deck
    client = slack.WebClient(token=SLACK_TOKEN)
    # check for {{ }}
    event_text = event_data["text"]
    add_arrow_emojis = False
    start = event_text.find("{{")
    if start != -1:
        end = event_text.find("}}")

        deck_name = event_text[start+2:end]
        get_result = get_all_decks(deck_name, 0)
        if "blocks" in get_result.keys():
            result_message = get_result["blocks"][0]["text"]["text"]
            result_index = result_message.split(" ")
            message = "%s deck %s of %s" %(deck_name, result_index[1], result_index[3])
            block = get_result["blocks"]
            if int(result_index[3]) > 1:
                add_arrow_emojis = True
            message_response = client.chat_postMessage(
                    channel=event_data["channel"],
                    text = message,
                    blocks = block
                    )
            if (add_arrow_emojis):
                client.reactions_add(
                    channel=event_data["channel"],
                    name = "arrow_left",
                    timestamp = message_response["ts"]
                    )
                client.reactions_add(
                    channel=event_data["channel"],
                    name = "arrow_right",
                    timestamp = message_response["ts"]
                    )
        else:
            message_response = client.chat_postMessage(
                    channel=event_data["channel"],
                    #response_type="ephemeral",
                    text = get_result["text"]
                    )


    #message_response = client.chat_postMessage(
            #channel=event_data["channel"],
            #text = message,
            #blocks = block
            #)

    # if get all decks returned more than 1 result, add arrow left and right emojis
    #if (add_arrow_emojis):
        #client.reactions_add(
            #channel=event_data["channel"],
            #name = "arrow_left",
            #timestamp = message_response["ts"]
            #)
        #client.reactions_add(
            #channel=event_data["channel"],
            #name = "arrow_right",
            #timestamp = message_response["ts"]
            #)

@slack_command('/show_cards')
def show_cards_command(text, **kwargs):
    cards = Cards.objects.filter(card_name__icontains = text)

    debug_content = ""
    message = ""
    root_url = 'https://ftamtgpq.pythonanywhere.com/'
    blocks = []
    if (len(cards) > 0):
        if (len(cards) > 10):
            return { "response_type": "in_channel", "text": "Too many cards to display.  Limit is 10." }
        for card in cards:
            message = message + "*" + card.card_name + "* \n"

            # check if deck image exists. if it doesn't send a message for now
            filepath = "fta_deck_building//static//build_finder//images//full/"
            filename = str(card.card_number) + ".png"
            full_filename = filepath + filename
            debug_content = debug_content + "Full filename is: %s \n" %full_filename
            if os.path.exists(full_filename):
                debug_content = debug_content + "Full image file exists. \n"
                asset_path = "/static/build_finder/images/full/"
                card_image_url = root_url + asset_path + filename
            else:
                debug_content = debug_content + "Full image file does not exist. \n"
                card_image_url = root_url + card.card_image

            debug_content = debug_content + "Card image url is: %s \n" %card_image_url
            write_to_debug_file("Show_cards_debug.txt", debug_content)

            blocks.append({ "type": "image",
                            "image_url": card_image_url,
                            "alt_text": card.card_name
                          }
                         )
    else:
        return { "response_type": "in_channel", "text": "Card not found." }

    #return { "response_type": "in_channel", "text": message }
    response = { "response_type": "in_channel",
            "blocks": blocks
            }
    return response

@slack_command('/combo_add')
def combo_add_command(text, **kwargs):
    # save deck
    # Get the values from text
    # values are pipe delimited
    # format: Card|card1|card2|card3|Description
    # allow '+' as delimiter also
    text = text.replace('+', '|')
    params = text.split('|')
    # remove leading and trailing spaces
    if len(params) < 2:
        message = "Missing combo card."
        return { "response_type": "in_channel", "text": message }
    for i in range(len(params)):
        params[i] = params[i].strip()

    # retrieve the cards
    c = []
    description = ""
    for i in range(len(params)):
        if (i < 4):
            cn = params[i].split("//")[0].strip()
            if (cn != ""):
                card = Cards.objects.filter(card_name__iexact = cn)
                if (len(card) == 0):
                    card = Cards.objects.filter(card_name__icontains = cn)
                if len(card) == 1:
                    c.append(card[0])
                elif len(card) > 1:
                    message = "More than 1 matching card found with name %s." %cn
                    return { "response_type": "ephemeral", "text": message }
                else:
                    message = "%s card not found." %cn
                    return { "response_type": "ephemeral", "text": message }
        else:
            description = params[i]

    combo = Combo(card = c[0], combo_card1 = c[1], combo_description = description)
    if (len(c) > 2):
        combo.combo_card2 = c[2]
    if (len(c) > 3):
        combo.combo_card3 = c[3]

    try:
        combo.save()
    except:
        return { "response_type": "ephemeral", "text": "Failed to save combo :(. Contact Larz." }

    return { "response_type": "in_channel", "text": "Combo saved." }

@slack_command('/combos_with')
def combos_with_command(text, **kwargs):
    cards = Cards.objects.filter(card_name__icontains = text)
    message = ""
    if (len(cards) > 0):
        for card in cards:
            message = message + "*" + card.card_name + "*"
            combos = Combo.objects.filter(Q(card__card_name=card) | Q(combo_card1__card_name=card) |
                    Q(combo_card2__card_name=card) | Q(combo_card3__card_name=card)
                    )
            if (len(combos) > 0):
                message = message + " combos were found: \n"
                for combo in combos:
                    message = message + "*COMBO #%d:* " %combo.id
                    message = message + combo.card.card_name
                    message = message + " + " + combo.combo_card1.card_name
                    if (combo.combo_card2 is not None):
                        message = message + " + " + combo.combo_card2.card_name
                    if (combo.combo_card3 is not None):
                        message = message + " + " + combo.combo_card3.card_name
                    if (combo.combo_description is not None):
                        message = message + " | " + combo.combo_description
                    message = message + "\n"
            else:
                message = message + " is not in any combos right now.\n"

    else:
        message = "Card not found."

    return { "response_type": "in_channel", "text": message }
    #return { "response_type": "in_channel", "text": { "type": "mrkdwn", "text": message } }

@slack_command('/combo_list')
def combo_list_command(text, **kwargs):
    try:
        limit = int(text)
    except:
        return { "response_type": "ephemeral", "text": "Send a valid number to limit the results." }

    combos = Combo.objects.all().order_by('-create_date')[:limit]
    message = ""
    for combo in combos:
        message = message + "*COMBO #%d:* " %combo.id
        message = message + combo.card.card_name
        message = message + " + " + combo.combo_card1.card_name
        if (combo.combo_card2 is not None):
            message = message + " + " + combo.combo_card2.card_name
        if (combo.combo_card3 is not None):
            message = message + " + " + combo.combo_card3.card_name
        if (combo.combo_description is not None):
            message = message + " | " + combo.combo_description
        message = message + "\n"

    return { "response_type": "in_channel", "text": message }
    #return { "response_type": "in_channel", "text": { "type": "mrkdwn", "text": message } }



@slack_command('/max_charge')
def max_charge_command(text, **kwargs):

    url = 'https://forums.d3go.com/discussion/82840/mtgpq-sneak-peek-july-2020-edition'
    response = requests.get(url)
    sp = BeautifulSoup(response.text, features="html.parser")

    filepath = "fta_deck_building//static//build_finder//images//temp/"
    filename = filepath + "MTGPQ_Events.csv"
    events = pd.read_csv(filename, index_col = None)

    event_abbrev = text.upper()

    debug = event_abbrev + "\n"

    event_locs = []
    lines = sp.find_all('p')
    for i in range(len(lines)):
        line = lines[i]
        event = line.text.split(":")
        event_name = event[0].split(" - ")
        event_name = event_name[0].replace("\xa0"," ").rstrip().lstrip()
        if event_abbrev == "ALL":
            ev = events[(events.event == event_name)]
        else:
            ev = events[(events.event == event_name) &
                    (events.abbrev == event_abbrev)]
        if (len(ev) == 1):
            event_idx_loc = ev.index[0]
            sp_event_idx_loc = i
            start_idx_loc = 0
            end_idx_loc = 0

            # get start time and end time locations
            search_word = "Start Time"
            keep_searching = True
            j = i + 1
            while keep_searching and j < len(lines):
                line = lines[j].text
                colon_loc = line.find(":")
                if colon_loc != -1:
                    if line[0:colon_loc] == search_word:
                        start_idx_loc = j
                        keep_searching = False
                j = j + 1

            search_word = "End Time"
            keep_searching = True
            while keep_searching and j < len(lines):
                line = lines[j].text
                colon_loc = line.find(":")
                if colon_loc != -1:
                    if line[0:colon_loc] == search_word:
                        end_idx_loc = j
                        keep_searching = False
                j = j + 1
            if start_idx_loc == 0 or end_idx_loc == 0:
                return { "response_type": "in_channel", "text": "Could not find event start and end time." }
            else:
                # don't append if a duplicate, i.e., full event name is the same
                Dup = False
                for event_loc in event_locs:
                    if lines[event_loc[1]].text == lines[i].text:
                        Dup = True
                if not Dup:
                    event_locs.append([event_idx_loc, sp_event_idx_loc, start_idx_loc, end_idx_loc])

    if (len(event_locs) == 0):
        return { "response_type": "in_channel", "text": "Event not found or not scheduled." }

    message = ""
    for event_loc in event_locs:
        full_event_name = lines[event_loc[1]].text
        full_event_name = full_event_name.replace('\xa0',' ')
        nodes = int(events.loc[event_loc[0], 'nodes'])
        initial_charge = int(events.loc[event_loc[0], 'initial_charges'])
        max_charge = int(events.loc[event_loc[0], 'max_charges'])
        hours_refresh = int(events.loc[event_loc[0], 'recharge_time'])
        refresh = timedelta(hours = hours_refresh)

        message = message + "Event: %s - %d nodes, %d initial charge(s), %d max, %d-hour refresh \n" %(full_event_name, nodes, initial_charge, max_charge, hours_refresh)

        debug = debug + lines[i].text + "\n" + message + "\n" + str(i)
        write_to_debug_file('max_charge_event.txt', debug + message)

        # get start time and end time
        line = lines[event_loc[2]].text
        colon_loc = line.find(":")

        start_time = datetime.strptime(line[colon_loc+2:colon_loc+18],
                                       '%m/%d/%Y %H:%M')

        line = lines[event_loc[3]].text
        colon_loc = line.find(":")

        end_time = datetime.strptime(line[colon_loc+2:colon_loc+18],
                                       '%m/%d/%Y %H:%M')

        current_time = datetime.utcnow()

        hours_to_start = start_time - current_time
        days_to_start = math.floor(hours_to_start.total_seconds() / 60 / 60 / 24)
        minutes_to_start = math.floor(hours_to_start.total_seconds() / 60) % 60
        hours_to_start = math.floor(hours_to_start.total_seconds() / 60 / 60 - days_to_start * 24)

        if start_time > current_time:
            message = "%s Time to start: %d day(s) %d hour(s) and %d minute(s) \n" %(
                message, days_to_start, hours_to_start, minutes_to_start)

        time_to_max_charge = start_time + refresh * (max_charge - initial_charge)

        hours_to_max_charge = time_to_max_charge - current_time
        days_to_max_charge = math.floor(hours_to_max_charge.total_seconds() / 60 / 60 / 24)
        minutes_to_max_charge = math.floor(hours_to_max_charge.total_seconds() / 60) % 60
        hours_to_max_charge = math.floor(hours_to_max_charge.total_seconds() / 60 / 60 - days_to_max_charge * 24)

        if time_to_max_charge > current_time:
            message = "%s Time to max charge: %d day(s) %d hour(s) and %d minute(s) \n" %(
                message, days_to_max_charge, hours_to_max_charge, minutes_to_max_charge)

        hours_to_end_time = end_time - current_time
        days_to_end_time = math.floor(hours_to_end_time.total_seconds() / 60 / 60 / 24)
        minutes_to_end_time = math.floor(hours_to_end_time.total_seconds() / 60) % 60
        hours_to_end_time = math.floor(hours_to_end_time.total_seconds() / 60 / 60 - days_to_end_time * 24)

        if end_time > current_time:
            message = "%s Time to end of event: %d day(s) %d hour(s) and %d minute(s) \n" %(
                message, days_to_end_time, hours_to_end_time, minutes_to_end_time)
        else:
            message = message + "This event has ended. \n"

        message = message + "\n"

    write_to_debug_file('max_charge.txt', debug + "\n" + message)
    return { "response_type": "in_channel", "text": message }

@slack_command('/coalition_rank')
def coalition_rank_command(text, **kwargs):
    return { "response_type": "in_channel", "text": "Use /fta_rank command instead."}
    filepath = "fta_deck_building//static//build_finder//images//temp/"
    filename = filepath + "fta_event_scores.csv"
    fta_pd = pd.read_csv(filename, index_col=0)

    message = ""
    params = list(filter(None, text.split(' ')))

    if (len(params[0].split('last')) > 1):
        lastn = int(params[0].split('last')[1])
        # limit to last 52 events
        if lastn > 52:
            lastn = 52
        ev_and_dt = fta_pd[['event', 'event_date']].drop_duplicates()
        plist = fta_pd[fta_pd.index < ev_and_dt.index[lastn]]
    else:
        plist = fta_pd[fta_pd.event_type == params[0].upper()]
        if (len(plist) > 0):
            plist = plist[plist.player_name != 'nan']
            ev_and_dt = plist[['event', 'event_date']].drop_duplicates()
            # use only the last 5 events
            plist = plist[plist.index < ev_and_dt.index[5]]
        else:
            message = "Event Type not found or invalid, try PVP-S, PVP-L, PVE-S, or PVE-L \n"
            message = message + "You can also try lastn where n is the number of previous events, max of 52. \n"
            message = message + "Example, /coalition_rank last10 Larz70. \n"
            return { "response_type": "in_channel", "text": message}

    player_avg = plist[['player_name', 'score']].groupby(by='player_name').mean().sort_values(ascending = False, by='score')
    player_count = plist[['player_name', 'score']].groupby(by='player_name').count().sort_values(ascending = False, by='score')
    player_rank = player_avg.rank(ascending = False, method = 'min')

    perf_rank = player_rank.merge(player_avg, how = "inner", left_index = True, right_index = True)
    perf_rank = perf_rank.merge(player_count, how = "inner", left_index = True, right_index = True)
    #perf_rank.rename(columns = {"score_x": "Rank", "score_y": "Average", "score": "#ofEvents"})

    val = perf_rank.values
    idx = perf_rank.index

    if len(params) > 1:
        try:
            pl_index = perf_rank.index.get_loc(params[1])
        except KeyError:
            message = "Player not found"
            return { "response_type": "in_channel", "text": message}
        # show player scores
        message = message + '```' + plist[plist.player_name == params[1]].to_string(index=False, justify="left") + '```\n'
    else: pl_index = 0

    if pl_index > 4:
        start = pl_index - 4
    else:
        start = 0
    end = start + 10

    message = message + '```     %-4s %-21s %-9s %-6s \n' %("Rank", "Player_Name", "Average", "Events")
    i = start
    while ((i < end) and (i < len(val))):
       message = "%s     %4d %-20s %8.4f%% %5d \n" %(message, val[i][0], pad(idx[i], 20), val[i][1] * 100, val[i][2])
       i = i + 1

    message = message + '```'
    write_to_debug_file('coalition_rank.txt', message)

    return { "response_type": "in_channel", "text": message}

@slack_command('/fta_rank')
def fta_rank_command(text, **kwargs):
    message = ""

    filepath = "fta_deck_building//static//build_finder//images//temp/"
    filename = filepath + "fta_event_scores.csv"
    fta_pd = pd.read_csv(filename, index_col=0)
    filename = filepath + "FtA_checkin.csv"
    vote_pd = pd.read_csv(filename, index_col=0)
    #filename = filepath + "FtA Check In - Directory.csv"
    #directory = pd.read_csv(filename)

    ev_sc = pd.merge(vote_pd, fta_pd, how = "right", on=["event", "event_date", "player_name"])

    debug_text = "size of score/vote join: %s" %len(ev_sc)
    write_to_debug_file("ev_sc_debug.txt", debug_text)

    params = text.split(',')
    voted = 0
    pname = ""
    evname = ""
    evtype = ""
    lastn = 5
    rklim = 10
    evmin = 1
    scoremin = 0
    invalid_parameter = False

    for param in params:
        try:
            key, value = param.split("=")
        except ValueError:
            invalid_parameter = True
        if key.strip() == "voted":
            try:
                voted = int(value)
            except ValueError:
                invalid_parameter = True
            if voted < 0 or voted > 6:
                invalid_parameter = True
        elif key.strip() == "player":
            pname = value
        elif key.strip() == "event":
            evname = value.upper().strip()
        elif key.strip() == "event_type":
            evtype = value.upper().strip()
        elif key.strip() == "lastN":
            lastn = int(value)
        elif key.strip() == "rankN":
            rklim = int(value)
        elif key.strip() == "event_min":
            evmin = int(value)
        elif key.strip() == "score_min":
            scoremin = float(value)
        else:
            invalid_parameter = True

        if invalid_parameter:
            message = "Invalid parameter.  Valid parameters are voted=, player=, event=, event_type=, lastN=, rankN=, and event_min= \n"
            message = message + "For help with parameter, type ?rank. \n"
            message = message + "Example, /fta_rank voted=1,lastN=10,event_type=PVP-S \n"
            message = message + "     will give you the ranking of players who voted 'All In' in the last 10 PVP-S events. \n"
            return { "response_type": "in_channel", "text": message}

    if evtype != "":
        ev_sc = ev_sc[ev_sc.event_type == evtype]
    if evname != "":
        ev_sc = ev_sc[ev_sc.event == evname]

    if (len(ev_sc) > 0):
        ev_and_dt = ev_sc[['event', 'event_date']].drop_duplicates()
        if len(ev_and_dt) > lastn:
            plist = ev_sc[ev_sc.index < ev_and_dt.index[lastn]]
        else:
            plist = ev_sc
    else:
        message = "Combination of Event and/or Event Type not found, try PVP-S, PVP-L, PVE-S, or PVE-L for event_type \n"
        message = message + "You can also try lastN where N is the number of previous events, max of 52. \n"
        message = message + "Example, /fta_rank voted=1,lastN=10,event_type=PVP-S \n"
        return { "response_type": "in_channel", "text": message}

    if voted != 0:
        plist = plist[plist.vote == voted]
    if scoremin > 0:
        plist = plist[plist.score >= scoremin]
        if len(plist) == 0:
            message = "Minimum Score may have been set too high.  Use a value between 0 and 1."
            return { "response_type": "in_channel", "text": message}

    player_avg = plist[['player_name', 'score']].groupby(by='player_name').mean().sort_values(ascending = False, by='score')
    player_count = plist[['player_name', 'score']].groupby(by='player_name').count().sort_values(ascending = False, by='score')
    player_count.columns = ['count']

    perf_count = player_avg.merge(player_count, how = "inner", left_index = True, right_index = True)
    perf_count = perf_count[perf_count['count'] >= evmin]

    player_rank = perf_count.rank(ascending = False, method = 'min')
    player_rank.columns = ['rank', 'x']

    perf_rank = player_rank.merge(perf_count, how = "inner", left_index = True, right_index = True)
    perf_rank = perf_rank.sort_values(by=['rank', 'count', 'player_name'], ascending=[True, False, True])

    if pname != "":
        try:
            pl_index = perf_rank.index.get_loc(pname.lower().strip())
        except KeyError:
            message = "Player not found"
            return { "response_type": "in_channel", "text": message}
        # show player scores
        message = message + "%s game scores: \n " %pname
        message = message + '```' + plist[plist.player_name == pname.lower().strip()].to_string(index=False, justify="left") + '```\n'
    else: pl_index = -1

    #plist_size = len(perf_rank)
    if pl_index >= round(rklim / 2):
        start = pl_index - round(rklim/2) + 1
    else:
        start = 0
    end = start + rklim

    checkin_vote = ['', 'All In', 'Progression+', 'Progression', 'Busy', 'Rival Coalition', 'New Player']
    if pname == "":
        parameter_settings = "Top %d players who voted %s and played in at least %d event(s) of the last %d %s %s events." %(
                rklim, checkin_vote[voted], evmin, lastn, evname, evtype)
    else:
        parameter_settings = "Rank of %s and %d other players near him who voted %s and played in at least %d event(s) of the last %d %s %s events." %(
                pname, rklim, checkin_vote[voted], evmin, lastn, evname, evtype)
    if scoremin > 0:
        parameter_settings = parameter_settings + " Minimum score of: %5.4f.\n" %scoremin
    else:
        parameter_settings = parameter_settings + "\n"

    message = message + parameter_settings
    message = message + '```     %-4s %-21s %-9s %-6s \n' %("Rank", "Player_Name", "Average", "Events")
    i = start
    while ((i < end) and (i < len(perf_rank))):
        player_name = perf_rank.index[i]
        if i == pl_index:
            message = "%s***  %4d %-20s %8.4f%% %5d  *** \n" %(message,
                    perf_rank.loc[player_name, 'rank'],
                    player_name,
                    perf_rank.loc[player_name, 'score'],
                    perf_rank.loc[player_name, 'count'])
        else:
            message = "%s     %4d %-20s %8.4f%% %5d \n" %(message,
                    perf_rank.loc[player_name, 'rank'],
                    player_name,
                    perf_rank.loc[player_name, 'score'],
                    perf_rank.loc[player_name, 'count'])
        i = i + 1

    message = message + '```'
    write_to_debug_file('coalition_rank.txt', message)

    return { "response_type": "in_channel", "text": message}

@slack_command('/iko')
def iko_command(text, **kwargs):
    # randomize n number of cards
    if text.upper() == 'BP':
        n = 5
        cost = 80
    elif text.upper() == 'PP':
        n = 25
        cost = 320
    elif text.upper() == 'SP':
        n = 15
        cost = 200
    else:
        n = 0
        cost = 0

    # get player's inventory
    userid = kwargs['user_id']
    filepath = "fta_deck_building//static//build_finder//images//temp/"
    filename = filepath + "IKO_sim_" + userid + ".csv"

    if os.path.exists(filename):
        plsim = pd.read_csv(filename, index_col = 0)
    else:
        # if new user, create inventory
        inv = np.arange(235)
        amt = np.zeros((235),dtype = int)
        plsim = pd.DataFrame({'inv': inv,
                              'amt': amt},
                              columns = ['inv', 'amt'])

    common_rate = 1 - (1 - .9796) ** (1 / 5)
    uncommon_rate = 1 - (1 - .9158) ** (1 / 5)
    rare_rate = 1 - (1 - .7486) ** (1 / 25)
    mythic_rate = 1 - (1 - .3029) ** (1 / 25)
    masterpiece_rate = 1 - (1 - .0178) ** (1 / 25)

    common_cards = (Cards.objects.filter(Q(card_rarity__exact = 'Common') & Q(card_set__exact = 'IKO')))
    uncommon_cards = (Cards.objects.filter(Q(card_rarity__exact = 'Uncommon') & Q(card_set__exact = 'IKO')))
    rare_cards = (Cards.objects.filter(Q(card_rarity__exact = 'Rare') & Q(card_set__exact = 'IKO')))
    mythic_cards = (Cards.objects.filter(Q(card_rarity__exact = 'Mythic') & Q(card_set__exact = 'IKO')))
    masterpiece_cards = (Cards.objects.filter(Q(card_rarity__exact = 'Masterpiece') & Q(card_set__exact = 'IKO')))

    card_num_array = []
    card_rate_array = []
    for card in common_cards:
        card_num_array.append([card.card_name, card.card_rarity])
        card_rate_array.append(common_rate/65)
    for card in uncommon_cards:
        card_num_array.append([card.card_name, card.card_rarity])
        card_rate_array.append(uncommon_rate/60)
    for card in rare_cards:
        card_num_array.append([card.card_name, card.card_rarity])
        card_rate_array.append(rare_rate/40)
    for card in mythic_cards:
        card_num_array.append([card.card_name, card.card_rarity])
        card_rate_array.append(mythic_rate/30)
    for card in masterpiece_cards:
        card_num_array.append([card.card_name, card.card_rarity])
        card_rate_array.append(masterpiece_rate/15)

    # set exclusives rate to zero
    #rares
    card_rate_array[125] = 0
    card_rate_array[126] = 0
    card_rate_array[127] = 0
    card_rate_array[128] = 0
    card_rate_array[132] = 0
    card_rate_array[134] = 0
    card_rate_array[136] = 0
    card_rate_array[142] = 0
    card_rate_array[152] = 0
    card_rate_array[159] = 0
    card_rate_array[164] = 0
    card_rate_array[166] = 0
    card_rate_array[168] = 0
    card_rate_array[170] = 0
    card_rate_array[171] = 0
    card_rate_array[173] = 0
    card_rate_array[174] = 0
    card_rate_array[177] = 0
    #mythics
    card_rate_array[202] = 0
    card_rate_array[206] = 0
    card_rate_array[208] = 0
    card_rate_array[212] = 0
    card_rate_array[217] = 0

    cards = np.array(card_num_array)
    rate = np.array(card_rate_array)
    # adjust rates so that they sum up to 1
    # rate = rate / sum(rate)
    # rate[len(rate)-1] = 1 - sum(rate[0:len(rate)-1])

    booster_pack = choices(np.arange(len(cards)), weights=rate, k=n)
    message = ""
    dup_count = 0
    for i in booster_pack:
        if (plsim.loc[i,'amt'] == 0):
            if i > 124:
                message = message + "*New %s - %s *\n" %(cards[i][1], cards[i][0])
        else:
            if i > 124:
                message = message + "Dup %s - %s \n" %(cards[i][1], cards[i][0])
            dup_count = dup_count + 1
    if len(booster_pack) > 0:
        message = "%sOpened %d duplicates.\n" %(message, dup_count)

    # id new and dup ones and update inventory
    for i in booster_pack:
        plsim.loc[i,'amt'] = plsim.loc[i,'amt'] + 1

    if text.upper() == "PP":
        message = message + "Guaranteed Rare: \n"
        rare_card_num_array = card_num_array[125:182]
        rare_card_rate_array = card_rate_array[125:182]

        gr_cards = np.array(rare_card_num_array)
        gr_rate = np.array(rare_card_rate_array)
        # adjust rates so that they sum up to 1
        # rate = rate / sum(rate)
        # rate[len(rate)-1] = 1 - sum(rate[0:len(rate)-1])

        booster_pack = choices(np.arange(len(gr_cards)), weights = gr_rate, k=1)
        for i in booster_pack:
            if (plsim.loc[i+125,'amt'] == 0):
                message = message + "*New %s - %s *\n" %(gr_cards[i][1], gr_cards[i][0])
            else:
                message = message + "Dup %s - %s \n" %(gr_cards[i][1], gr_cards[i][0])

        for i in booster_pack:
            plsim.loc[i+125,'amt'] = plsim.loc[i+125,'amt'] + 1

    # update crystals and PP cost
    plsim.loc[233, 'amt'] = plsim.loc[233, 'amt'] + cost
    if text.upper() == 'PP':
        plsim.loc[234, 'amt'] = plsim.loc[234, 'amt'] + 1

    # show inventory
    c_arr = plsim.loc[0:64,]
    u_arr = plsim.loc[65:124,]
    r_arr = plsim.loc[125:182,]
    m_arr = plsim.loc[183:217,]
    mp_arr = plsim.loc[218:232,]
    c_count = len(c_arr[c_arr.amt > 0])
    u_count = len(u_arr[u_arr.amt > 0])
    r_count = len(r_arr[r_arr.amt > 0])
    m_count = len(m_arr[m_arr.amt > 0])
    mp_count = len(mp_arr[mp_arr.amt > 0])
    c_dup = c_arr.amt.sum() - c_count
    u_dup = u_arr.amt.sum() - u_count
    r_dup = r_arr.amt.sum() - r_count
    m_dup = m_arr.amt.sum() - m_count
    mp_dup = mp_arr.amt.sum() - mp_count

    crystals_count = plsim.amt[233]
    PPs_bought = plsim.amt[234]
    orbs_count = c_dup * 15 + u_dup * 30 + r_dup * 150 + m_dup * 750 + mp_dup * 3750

    message = message + "Inventory: \n"
    message = message + '```    Common  Uncommon  Rare  Mythic  Masterpiece  Crystals Spent\n'
    message = "%s    %6d %9d %5d %7d %12d %15d \n" %(message, c_count, u_count, r_count, m_count, mp_count, crystals_count)
    message = message + '```\n'

    message = message + "Duplicates: \n"
    message = message + '```    Common  Uncommon  Rare  Mythic  Masterpiece     Orbs\n'
    message = "%s    %6d %9d %5d %7d %12d %8d  \n" %(message, c_dup, u_dup, r_dup, m_dup, mp_dup, orbs_count)
    message = message + '```\n'

    # display rates:
    total_count = plsim.loc[0:232,'amt'].sum() - PPs_bought
    c_rate = (c_count + c_dup) / total_count * 100
    u_rate = (u_count + u_dup) / total_count * 100
    r_rate = (r_count + r_dup - PPs_bought) / total_count * 100
    m_rate = (m_count + m_dup) / total_count * 100
    mp_rate = (mp_count + mp_dup) / total_count * 100
    #c_debug = rate[0] * 65 / np.sum(rate) * 100
    #u_debug = rate[65] * 60 / np.sum(rate) * 100
    #r_debug = rate[129] * 40 / np.sum(rate) * 100
    #m_debug = rate[183] * 30 / np.sum(rate) * 100
    #mp_debug = rate[218] * 15 / np.sum(rate) * 100
    message = message + "Actual Rates over Advertised Rates (in percent): \n"
    message = message + '```             Common  Uncommon  Rare  Mythic  Masterpiece\n'
    message = "%s Actual:     %6.2f %9.2f %5.2f %7.2f %12.2f \n" %(message, c_rate, u_rate, r_rate, m_rate, mp_rate)
    message = "%s Advertised: %6.2f %9.2f %5.2f %7.2f %12.2f \n" %(message, common_rate*100, uncommon_rate*100,
            rare_rate*100, mythic_rate*100, masterpiece_rate*100)
    #message = "%s Debug rate: %6.2f %9.2f %5.2f %7.2f %12.2f \n" %(message, c_debug, u_debug, r_debug, m_debug, mp_debug)
    message = message + '```\n'

    if text.lower() == "startover":
        plsim.amt = 0
        message = message + "Data will be erased.\n"
    elif text.lower() == "mythics":
        message = message + "Mythics owned: \n"
        for i in range(183,218):
            if (plsim.loc[i,'amt'] > 0):
                if (plsim.loc[i,'amt'] == 1):
                    message = message + "     %s - pulled once \n" %(cards[i][0])
                else:
                    message = message + "     %s - pulled %s times \n" %(cards[i][0], plsim.loc[i,'amt'])
    elif text.lower() == "mps":
        message = message + "Masterpieces owned: \n"
        for i in range(218,233):
            if (plsim.loc[i,'amt'] > 0):
                if (plsim.loc[i,'amt'] == 1):
                    message = message + "     %s - pulled once \n" %(cards[i][0])
                else:
                    message = message + "     %s - pulled %s times \n" %(cards[i][0], plsim.loc[i,'amt'])

    plsim.to_csv(filename)

    return { "response_type": "in_channel", "text": message}

@slack_command('/ikop2w')
def ikop2w_command(text, **kwargs):
    try:
        dollar_amt = int(text)
    except ValueError:
        return { "response_type": "in_channel", "text": "Invalid amount."}

    crystals_count = math.floor(dollar_amt / 100) * 3000
    PPs_bought = math.floor(crystals_count / 320)
    message = "Buying %d crystals and opening %d PPs.\n" %(crystals_count, PPs_bought)

    inv = np.arange(235)
    amt = np.zeros((235),dtype = int)
    plsim = pd.DataFrame({'inv': inv,
                          'amt': amt},
                          columns = ['inv', 'amt'])

    plsim, cards, rate = iko_sim(plsim, PPs_bought * 25, PPs_bought)
    plsim.amt[233] = crystals_count
    plsim.amt[234] = PPs_bought

    message = message + format_bp_sim_inventory_message(plsim, cards, rate)

    return { "response_type": "in_channel", "text": message}

@slack_command('/ikof2p')
def ikof2p_command(text, **kwargs):
    try:
        months_played = int(text)
    except ValueError:
        return { "response_type": "in_channel", "text": "Invalid number of months."}

    crystals_count = -600 * months_played
    BPs_earned = 20 * months_played
    jewels_earned = 400 * months_played
    PPs_bought = 0
    message = "%d crystals spent, %d BPs opened, and %d jewels earned.\n" %(crystals_count, BPs_earned, jewels_earned)

    inv = np.arange(235)
    amt = np.zeros((235),dtype = int)
    plsim = pd.DataFrame({'inv': inv,
                          'amt': amt},
                          columns = ['inv', 'amt'])

    plsim, cards, rate = iko_sim(plsim, BPs_earned * 5, PPs_bought )
    plsim.amt[233] = crystals_count
    plsim.amt[234] = PPs_bought

    message = message + format_bp_sim_inventory_message(plsim, cards, rate)

    return { "response_type": "in_channel", "text": message}

