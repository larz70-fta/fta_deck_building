import slack

from .models import Cards

from django.db.models import Q

import pandas as pd
import numpy as np

def iko_cards_and_rate():
    common_rate = 1 - (1 - .9796) ** (1 / 5)
    uncommon_rate = 1 - (1 - .9158) ** (1 / 5)
    rare_rate = 1 - (1 - .7486) ** (1 / 25)
    mythic_rate = 1 - (1 - .3029) ** (1 / 25)
    masterpiece_rate = 1 - (1 - .0178) ** (1 / 25)

    common_count = 65
    uncommon_count = 60
    rare_count = 40
    mythic_count = 30
    masterpiece_count = 15

    common_cards = (Cards.objects.filter(Q(card_rarity__exact = 'Common') & Q(card_set__exact = 'IKO')))
    uncommon_cards = (Cards.objects.filter(Q(card_rarity__exact = 'Uncommon') & Q(card_set__exact = 'IKO')))
    rare_cards = (Cards.objects.filter(Q(card_rarity__exact = 'Rare') & Q(card_set__exact = 'IKO')))
    mythic_cards = (Cards.objects.filter(Q(card_rarity__exact = 'Mythic') & Q(card_set__exact = 'IKO')))
    masterpiece_cards = (Cards.objects.filter(Q(card_rarity__exact = 'Masterpiece') & Q(card_set__exact = 'IKO')))

    card_num_array = []
    card_rate_array = []
    for card in common_cards:
        card_num_array.append([card.card_name, card.card_rarity])
        card_rate_array.append(common_rate/common_count)
    for card in uncommon_cards:
        card_num_array.append([card.card_name, card.card_rarity])
        card_rate_array.append(uncommon_rate/uncommon_count)
    for card in rare_cards:
        card_num_array.append([card.card_name, card.card_rarity])
        card_rate_array.append(rare_rate/rare_count)
    for card in mythic_cards:
        card_num_array.append([card.card_name, card.card_rarity])
        card_rate_array.append(mythic_rate/mythic_count)
    for card in masterpiece_cards:
        card_num_array.append([card.card_name, card.card_rarity])
        card_rate_array.append(masterpiece_rate/masterpiece_count)

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

    return(card_num_array, card_rate_array)

def iko_sim(plsim, n, gr_n):

    card_num_array, card_rate_array = iko_cards_and_rate()

    cards = np.array(card_num_array)
    rate = np.array(card_rate_array)

    # randomize n number of cards
    booster_pack = choices(np.arange(len(cards)), weights=rate, k=n)

    for i in booster_pack:
        plsim.loc[i,'amt'] = plsim.loc[i,'amt'] + 1

    if gr_n > 0:
        rare_card_num_array = card_num_array[125:182]
        rare_card_rate_array = card_rate_array[125:182]

        gr_cards = np.array(rare_card_num_array)
        gr_rate = np.array(rare_card_rate_array)
    
        booster_pack = choices(np.arange(len(gr_cards)), weights = gr_rate, k=gr_n)

        for i in booster_pack:
            plsim.loc[i+125,'amt'] = plsim.loc[i+125,'amt'] + 1

    return(plsim, cards, rate)    

def sim_until_mythics_pulled(plsim, n_mythics):
    card_num_array, card_rate_array = iko_cards_and_rate()

    cards = np.array(card_num_array)
    rate = np.array(card_rate_array)

    # randomize n number of cards
    booster_pack = choices(np.arange(len(cards)), weights=rate, k=n)
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
