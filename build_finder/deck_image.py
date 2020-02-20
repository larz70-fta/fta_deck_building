# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 10:25:22 2020

@author: larry
"""

import numpy as np
import urllib
import cv2

import math

def url_to_image(url):
    # download the image, convert to numpy
    # then read into opencv format
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    
    return image

deck = ["https://mtgpq.info/assets/packs/grn/404939.png",
        "https://mtgpq.info/assets/packs/grn/91755.png",
        "https://mtgpq.info/assets/packs/grn/402511.png",
        "https://mtgpq.info/assets/packs/grn/402506.png"]

deck_image = np.zeros((276, 300, 3), dtype="uint8")
for i in range(4):
    #print ("loading card image: ", card)
    card_image = url_to_image(deck[i])
    
    # take the top half, reduce by 50% and then combine (275,150)
    # 275, 150 and then only even numbered rows and columns
    temp_image = card_image[0:275:2, 0:300:2]
    
    row = math.floor(i / 2) * 138
    col = (i % 2) * 150
    deck_image[row:(row + 138),col:(col + 150)] = temp_image
    
cv2.imwrite("deck.png", deck_image)
    
    #cv2.imshow("Image", card_image)
    #cv2.waitKey(0)
    
resp = urllib.request.urlopen(deck[0])
image_np = np.asarray(bytearray(resp.read()), dtype="uint8")
