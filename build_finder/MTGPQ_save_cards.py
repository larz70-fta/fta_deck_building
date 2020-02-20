# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 16:29:53 2019

@author: larry
"""

import pyautogui
import math
import time

import pandas as pd
from PIL import Image
import pytesseract
            
def save_ss(x,y,width,height, card_number):
    fb=pyautogui.screenshot(region=(x,y,width,height))
    #save
    fb.save("static/build_finder/images/" + str(card_number) + '.png')
    
x = 16
y = 111
width = 198
height = 100
x_offset = 200
y_offset = 114.3

card_base_number = 20000
n = 234

for i in range(n):
    card_number = card_base_number + i+1
    save_ss(x + ((i%2)* x_offset), 
            y + (math.floor((i%10)/2) * y_offset), 
            width, height, card_number)
    if ((card_number) % 10 == 0):
        # click next
        pyautogui.click(360, 713)
        time.sleep(3)
        

#save_ss(115, 111, width, height, 11191)
        
        
# read in new cards:
def take_ss_then_ocr(x,y,width,height):
    im=pyautogui.screenshot(region=(x,y,width,height))
    
    bw_im = Image.new("RGB",(width, height), "white")
    pixels = bw_im.load()
    for i in range(width):
        for j in range(height):
            pixel = im.getpixel((i,j))
            red=pixel[0]
            green=pixel[1]
            blue=pixel[2]
            
            if (red > 200 and green > 200 and blue > 200):
                pixels[i,j] = (0,0,0) 
    
    #bw_im.show()
    text=pytesseract.image_to_string(bw_im, config='--psm 6 --oem 1') 
    return(text)

pytesseract.pytesseract.tesseract_cmd = r'D:\Windows.old\Program Files (x86)\Tesseract-OCR\tesseract'

cards_df = pd.DataFrame()
for i in range(234):
    card_name = take_ss_then_ocr(115, 250, 300, 65) 
    # replace \n with a space
    card_name = card_name.replace('\n',' ')
    cards_data = pd.DataFrame({'name': [card_name]})

    cards_df = cards_df.append(cards_data, ignore_index=True)
    #swipe left
    pyautogui.moveTo(415,250)
    pyautogui.dragTo(115,250, duration=0.5)
    time.sleep(0.5)
        
cards_df.to_csv('THB.csv', header=False, index=False)
