# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 17:58:59 2020

@author: larry
"""

#from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

import slack
from slack_utils.decorators import slack_view

from .models import Deck
from .models import Cards

from django.db.models import Q

from .slack import generate_deck_image as gen_image
from .slack import search_decks
from .slack import format_deck_search_result_message as format_block

import os
import json

import requests

def build_modal_view(callback_id, deck_name, description):
    view = {
        "type": "modal",
        "callback_id" : callback_id,
        "title": {
            "type": "plain_text",
            "text": "Create or Modify a Deck"
        },
        "submit": {
	    "type": "plain_text",
	    "text": "Save",
	    "emoji": True
	},
	"close": {
	    "type": "plain_text",
	    "text": "Cancel",
	    "emoji": True
	},
        "notify_on_close": True
    }

    block = []
    if deck_name != "":
        d = Deck.objects.get(deck_name__exact = deck_name)
        author = d.deck_author
        PW = d.deck_PW
        description = d.deck_description
        video_link = d.deck_video_link
        c = []
        c.append(d.card1.card_name)
        c.append(d.card2.card_name)
        c.append(d.card3.card_name)
        c.append(d.card4.card_name)
        c.append(d.card5.card_name)
        c.append(d.card6.card_name)
        c.append(d.card7.card_name)
        c.append(d.card8.card_name)
        c.append(d.card9.card_name)
        c.append(d.card10.card_name)

        block.append(
            {
                "type": "input",
                "block_id": "deck_name_block",
	        "element": {
	            "type": "plain_text_input",
	            "action_id": "deck_name",
                    "initial_value": deck_name,
		    "placeholder": {
		        "type": "plain_text",
			"text": "What is the name of your deck?"
			}
	            },
	        "label": {
	            "type": "plain_text",
	            "text": "Deck Name"
	            }
	    })
        block.append(
            {
	        "type": "input",
                "block_id": "deck_author_block",
		"element": {
		    "type": "plain_text_input",
		    "action_id": "deck_author",
                    "initial_value": author,
		    "placeholder": {
		        "type": "plain_text",
			"text": "Who created the deck?"
			}
		    },
		"label": {
	            "type": "plain_text",
		    "text": "Deck Author"
		    }
	    })
        block.append(
            {
		"type": "input",
                "block_id": "deck_PW_block",
		"element": {
		    "type": "plain_text_input",
		    "action_id": "deck_PW",
                    "initial_value": PW,
		    "placeholder": {
		        "type": "plain_text",
			"text": "Which planeswalker is this deck for?"
			}
	            },
		"label": {
		    "type": "plain_text",
		    "text": "Planeswalker"
		    }
	    })
        block.append(
            {
	        "type": "input",
                "block_id": "deck_description_block",
	        "element": {
		    "type": "plain_text_input",
                    "action_id" : "deck_description",
                    "initial_value": description,
		    "multiline": True
		    },
		"label": {
		    "type": "plain_text",
		    "text": "Deck Description",
		    "emoji": True
		    }
            })

        for i in range(10):
            block_id = "deck_card%d_block" %(i+1)
            action_id = "deck_card%d" %(i+1)
            label_text = "Card #%d" %(i+1)
            block.append({
                "type": "input",
                "block_id": block_id,
                "element": {
                    "type": "plain_text_input",
                    "action_id": action_id,
                    "initial_value": c[i],
                    },
                "label": {
                    "type": "plain_text",
                    "text": label_text
                    }
                })

        block.append({
	        "type": "input",
                "block_id": "video_link_block",
	        "element": {
		    "type": "plain_text_input",
                    "action_id" : "video_link",
                    "initial_value": video_link
		    },
		"label": {
		    "type": "plain_text",
		    "text": "Gameplay Video Link",
		    "emoji": True
		    }
            })
        view["private_metadata"] = str(d.id)
    else:
        block.append(
            {
                "type": "input",
                "block_id": "deck_name_block",
	        "element": {
	            "type": "plain_text_input",
	            "action_id": "deck_name",
                    "initial_value": deck_name,
		    "placeholder": {
		        "type": "plain_text",
			"text": "What is the name of your deck?"
			}
	            },
	        "label": {
	            "type": "plain_text",
	            "text": "Deck Name"
	            }
	    })
        block.append(
            {
	        "type": "input",
                "block_id": "deck_author_block",
		"element": {
		    "type": "plain_text_input",
		    "action_id": "deck_author",
		    "placeholder": {
		        "type": "plain_text",
			"text": "Who created the deck?"
			}
		    },
		"label": {
	            "type": "plain_text",
		    "text": "Deck Author"
		    }
	    })
        block.append(
            {
		"type": "input",
                "block_id": "deck_PW_block",
		"element": {
		    "type": "plain_text_input",
		    "action_id": "deck_PW",
		    "placeholder": {
		        "type": "plain_text",
			"text": "Which planeswalker is this deck for?"
			}
	            },
		"label": {
		    "type": "plain_text",
		    "text": "Planeswalker"
		    }
	    })
        block.append(
            {
	        "type": "input",
                "block_id": "deck_description_block",
	        "element": {
		    "type": "plain_text_input",
                    "action_id" : "deck_description",
                    "initial_value": description,
		    "multiline": True
		    },
		"label": {
		    "type": "plain_text",
		    "text": "Deck Description",
		    "emoji": True
		    }
            })

        for i in range(10):
            block_id = "deck_card%d_block" %(i+1)
            action_id = "deck_card%d" %(i+1)
            label_text = "Card #%d" %(i+1)
            placeholder_text = "What is card #%d?" %(i+1)
            block.append({
                "type": "input",
                "block_id": block_id,
                "element": {
                    "type": "plain_text_input",
                    "action_id": action_id,
		    "placeholder": {
		        "type": "plain_text",
			"text": placeholder_text
			}
                    },
                "label": {
                    "type": "plain_text",
                    "text": label_text
                    }
                })

        block.append({
	        "type": "input",
                "block_id": "video_link_block",
	        "element": {
		    "type": "plain_text_input",
                    "action_id" : "video_link",
                    "initial_value": "None",
		    "placeholder": {
		        "type": "plain_text",
			"text": "Is there a link to a game play video?"
			}
		    },
		"label": {
		    "type": "plain_text",
		    "text": "Gameplay Video Link",
		    "emoji": True
		    }
            })
        view["private_metadata"] = "0"



    view["blocks"] = block

    return(view)

def build_modal_view_from_state_values(state_values, deck_id_str):
    view = {
        "type": "modal",
        "callback_id" : "mod_deck",
        "title": {
            "type": "plain_text",
            "text": "Create or Modify a Deck"
        },
        "submit": {
	    "type": "plain_text",
	    "text": "Save",
	    "emoji": True
	},
	"close": {
	    "type": "plain_text",
	    "text": "Cancel",
	    "emoji": True
	},
        "notify_on_close": True
    }
    view["private_metadata"] = deck_id_str

    block = []
    block.append(
            {
                "type": "input",
                "block_id": "deck_name_block",
	        "element": {
	            "type": "plain_text_input",
	            "action_id": "deck_name",
                    "initial_value": state_values["deck_name_block"]["deck_name"]["value"],
		    "placeholder": {
		        "type": "plain_text",
			"text": "What is the name of your deck?"
			}
	            },
	        "label": {
	            "type": "plain_text",
	            "text": "Deck Name"
	            }
	    })
    block.append(
            {
	        "type": "input",
                "block_id": "deck_author_block",
		"element": {
		    "type": "plain_text_input",
		    "action_id": "deck_author",
                    "initial_value": state_values["deck_author_block"]["deck_author"]["value"],
		    "placeholder": {
		        "type": "plain_text",
			"text": "Who created the deck?"
			}
		    },
		"label": {
	            "type": "plain_text",
		    "text": "Deck Author"
		    }
	    })
    block.append(
            {
		"type": "input",
                "block_id": "deck_PW_block",
		"element": {
		    "type": "plain_text_input",
		    "action_id": "deck_PW",
                    "initial_value": state_values["deck_PW_block"]["deck_PW"]["value"],
		    "placeholder": {
		        "type": "plain_text",
			"text": "Which planeswalker is this deck for?"
			}
	            },
		"label": {
		    "type": "plain_text",
		    "text": "Planeswalker"
		    }
	    })
    block.append(
            {
	        "type": "input",
                "block_id": "deck_description_block",
	        "element": {
		    "type": "plain_text_input",
                    "action_id" : "deck_description",
                    "initial_value": state_values["deck_description_block"]["deck_description"]["value"],
		    "multiline": True
		    },
		"label": {
		    "type": "plain_text",
		    "text": "Deck Description",
		    "emoji": True
		    }
            })

    for i in range(10):
        block_id = "deck_card%d_block" %(i+1)
        action_id = "deck_card%d" %(i+1)
        label_text = "Card #%d" %(i+1)
        block.append({
                "type": "input",
                "block_id": block_id,
                "element": {
                    "type": "plain_text_input",
                    "action_id": action_id,
                    "initial_value": state_values[block_id][action_id]["value"],
                    },
                "label": {
                    "type": "plain_text",
                    "text": label_text
                    }
                })

    block.append({
	        "type": "input",
                "block_id": "video_link_block",
	        "element": {
		    "type": "plain_text_input",
                    "action_id" : "video_link",
                    "initial_value": state_values["video_link_block"]["video_link"]["value"],
		    "placeholder": {
		        "type": "plain_text",
			"text": "Is there a link to a game play video?"
			}
		    },
		"label": {
		    "type": "plain_text",
		    "text": "Gameplay Video Link",
		    "emoji": True
		    }
            })

    view["blocks"] = block

    return(view)

def validate_deck_submission(cards, deck_info):
    valid = True
    # check deck_id if this is an insert (zero) or an update (non-zero)
    deck_id = deck_info[0]
    if (deck_id == "0"):
        # this is a new deck, check if the name already exists
        d = Deck.objects.filter(deck_name__exact=deck_info[2])
        if (len(d) > 0):
            valid = False
            message = ":x: :mustread: *_A deck already exists with that name.  Please give your deck a different name._* :mustread:"

    if valid:
        c = []
        for card_name in cards:
            card = Cards.objects.filter(card_name__iexact = card_name)
            if (len(card) == 1):
                valid = True
                c.append(card[0])
            else:
                card = Cards.objects.filter(card_name__icontains = card_name)
                if len(card) == 1:
                    valid = True
                    c.append(card[0])
                elif len(card) > 1:
                    valid = False
                    message = ":x: :mustread: *_More than 1 matching card found with name %s._* :mustread:" %card_name
                    break
                else:
                    valid = False
                    message = ":x: :mustread: *_%s card not found._* :mustread:" %card_name
                    break

    if valid:
        # check deck_id if this is an insert (zero) or an update (non-zero)
        if (deck_id == "0"):
            d = Deck(deck_author = deck_info[1], deck_name = deck_info[2],
                    deck_PW = deck_info[3], deck_description = deck_info[4],
                    card1 = c[0], card2 = c[1], card3 = c[2], card4 = c[3], card5 = c[4],
                    card6 = c[5], card7 = c[6], card8 = c[7], card9 = c[8], card10 = c[9],
                    deck_video_link = deck_info[5])
        else:
            d = Deck.objects.get(id = int(deck_id))
            d.deck_author = deck_info[1]
            d.deck_name = deck_info[2]
            d.deck_PW = deck_info[3]
            d.deck_description = deck_info[4]
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
            d.deck_video_link = deck_info[5]

        try:
            d.save()
        except:
            message = ":x: :mustread: *_Deck is valid but something went wrong :(. Contact Larz._* :mustread:"
            return(message, "0")
        message = ":heavy_check_mark:All the cards are valid. The deck has been saved."
        gen_image(c, d.id)
        deck_id = str(d.id)
    return(message, deck_id)

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

    latest_decks_list = d.order_by('-create_date')
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

    cards = [deck.card1, deck.card2, deck.card3, deck.card4, deck.card5,
                  deck.card6, deck.card7, deck.card8, deck.card9, deck.card10]
    #cards = Cards.objects.filter(card_name__in = card_list)
    context = {
        'deck': deck,
        'cards': cards,
        }
    return render(request, 'build_finder/detail.html', context)

@slack_view
def deckbot_action(request, *args, **kwargs):
    # your logic
    filepath = "fta_deck_building//static//build_finder//images//temp/"
    save_file = filepath + 'deckbot_action.txt'
    f = open(save_file, 'w+')
    f.write("Request follows: \n")
    f.write(str(request))
    f.write("\n")

    payload = json.loads(request.POST.get("payload"))
    f.write(str(payload))
    f.write("\n")

    response_update = {}

    msg_type = payload["type"]
    # if this is a message_action, create the modal view
    FTA_SLACK_TOKEN = os.getenv("FTA_SLACK_TOKEN")
    client = slack.WebClient(token=FTA_SLACK_TOKEN)
    if msg_type == "message_action":
        # get block if it exists and present existing deck.  otherwise, get text and create new deck.
        message = payload["message"]

        deck_name = ""
        if "blocks" in message.keys():
            for block in message["blocks"]:
                if block["type"] == "image":
                    deck_name = block["alt_text"]
                    deck_description = ""
                    break
        if deck_name == "":
            if "text" in message.keys():
                deck_description = message["text"]
            else:
                deck_description = ""

        f.write("deck name is %s\n" %deck_name)
        response_view = client.views_open(
            trigger_id = payload["trigger_id"],
            view = build_modal_view(payload["callback_id"], deck_name, deck_description)
            )
        f.write("response follows\n")
        f.write(str(response_view))

    elif msg_type == "view_submission":
        # retrieve all input values.  Validate the cards and return with a message to save the deck
        view = payload["view"]
        cards = []
        for i in range(10):
        # validate the cards
            field_name = "deck_card%d" %(i+1)
            block_id = field_name + "_block"
            cards.append(view["state"]["values"][block_id][field_name]["value"])

        f.write("cards validated...\n")
        f.write(str(cards))

        deck_id = view["private_metadata"]
        deck_author = view["state"]["values"]["deck_author_block"]["deck_author"]["value"]
        deck_name = view["state"]["values"]["deck_name_block"]["deck_name"]["value"]
        deck_PW = view["state"]["values"]["deck_PW_block"]["deck_PW"]["value"]
        deck_description = view["state"]["values"]["deck_description_block"]["deck_description"]["value"]
        deck_video_link = view["state"]["values"]["video_link_block"]["video_link"]["value"]
        deck_info = [deck_id, deck_author, deck_name, deck_PW, deck_description, deck_video_link]
        message, deck_id = validate_deck_submission(cards,deck_info)

        f.write("\n" + message + "\n")

        #update view

        response_update = {
                  "response_action": "update",
                  "view": {
                      "type": "modal",
                      "title": {
                          "type": "plain_text",
                          "text": "Create or Modify a Deck"
                      },
	          "close": {
	              "type": "plain_text",
	              "text": "Close",
	              "emoji": True
	              },
                  "private_metadata": deck_id,
                  "blocks": [
                      {
                          "type": "section",
                          "text": {
                              "type": "mrkdwn",
                              "text": message
                          }
                      },
    # add a button to go back and re-edit
                      {
                          "type": "actions",
                          "block_id": "back_to_edit_block",
	                  "elements": [ {
			              "type": "button",
			              "action_id": "back_to_edit",
			              "text": {
				              "type": "plain_text",
				              "text": "Back to Edit"
				              }
			              } ]
                      } ]
                  }
        }
    elif msg_type == "block_actions":
        # Restore the modal with the original/edited fields
        # Or if invoked via previous/next button of deck search, then update search results

        #update view
        if "view" in payload:
            view = build_modal_view_from_state_values(payload["view"]["state"]["values"], payload["view"]["private_metadata"])
            response_view = client.views_update(
                    view = view,
                    view_id = payload["container"]["view_id"]
                )

            f.write("response follows\n")
            f.write(str(response_view))
        else:
            if "message" in payload and "actions" in payload:
                actions = payload["actions"]
                search_text = actions[0]["value"]
                tokens = search_text.split(" ")
                page = int(tokens.pop())
                text = ""
                for token in tokens:
                    text = text + " " + token
                decks = search_decks(text, "search_fields")
                block = format_block(decks, text, page)
                #client.chat_update(
                #        channel = payload["channel"]["id"],
                #        ts = payload["message"]["ts"],
                #        blocks = block,
                #        as_user = False
                #        )
                f.write("Updated deck search results for %s page %d.\n" %(text, page))
                f.write("Channel %s.\n" %(payload["channel"]["id"]))
                f.write("Timestamp %s.\n" %(payload["message"]["ts"]))
                f.write("Response url is %s\n" %(payload["response_url"]))
                f.write("Blocks %s.\n" %(block))

                #update search results with new page
                response = requests.post(payload["response_url"],
                                         json = {"replace_original": "true",
                                                 "blocks": block})
                f.write("Post to response url status code is %d" %response.status_code)
                #response_update = {"replace_original": "true",
                #        "blocks":  block
                #        }

    f.close()
    return JsonResponse(response_update)

