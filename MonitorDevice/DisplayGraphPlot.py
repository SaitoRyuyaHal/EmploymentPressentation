#!/usr/bin/env python3

from ST7735LcdDriver import ST7735
import matplotlib.pyplot as plt
from matplotlib import dates
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from datetime import datetime
import numpy as np


class DisplayGraphPlot():
    def __init__(self):
        self.width = 128
        self.height = 160
        self.soil_value = 0
        self.temperature = 0
        self.disp = ST7735(25, 0, rst=4)
        self.disp.begin()
        self.disp.clear((0, 0, 0))
        self.big_font = ImageFont.truetype("/usr/share/fonts/truetype/anonymous-pro/Anonymous Pro B.ttf", 15)
        self.middle_font = ImageFont.truetype("/usr/share/fonts/truetype/anonymous-pro/Anonymous Pro B.ttf", 13)
        self.small_font = ImageFont.truetype("/usr/share/fonts/truetype/anonymous-pro/Anonymous Pro B.ttf", 10)
    
    def displaySoilGraph(self, value):
        draw = self.disp.draw()
        draw.rectangle((30, 155, 43, 110), outline=(0, 0, 0), fill=(0, 0, 0))

        self.disp.display()
        self.draw_rotated_text("PLANTER OBSERVATION SYSTEM", (5, 20), 90, self.small_font, fill=(255, 255, 255))
        self.draw_rotated_text("SOIL", (20, 130), 90, self.small_font, fill=(255, 255, 255))
        self.soil_value = value
        self.draw_rotated_text(str(self.soil_value), (30, 110), 90, self.middle_font, fill=(255, 255, 255))
        self.draw_rotated_text("INSPECTOR", (80, 80), 90, self.big_font, fill=(252, 241, 19))
        self.disp.display()

    def displayTemperatureAndHumidityGraph(self, temperature, humidity):
        draw = self.disp.draw()
        draw.rectangle((30, 80, 43, 20), outline=(0, 0, 0), fill=(0, 0, 0))
        draw.rectangle((55, 80, 67, 20), outline=(0, 0, 0), fill=(0, 0, 0))
        self.disp.display()

        self.draw_rotated_text("TEMPERATURE", (20, 35), 90, self.small_font, fill=(255, 255, 255))
        self.temperature = temperature
        self.draw_rotated_text(str(self.temperature), (30, 35), 90, self.middle_font, fill=(255, 255, 255))
        self.draw_rotated_text("HUMIDITY", (45, 45), 90, self.small_font, fill=(255, 255, 255))
        self.humidity = humidity
        self.draw_rotated_text(str(self.humidity), (55, 35), 90, self.middle_font, fill=(255, 255, 255))

    def draw_rotated_text(self, text, position, angle, font, fill=(255,255,255)):
        draw = ImageDraw.Draw(self.disp.buffer)
        width, height = draw.textsize(text, font=font)
        textimage = Image.new('RGBA', (width, height), (0,0,0,0))
        textdraw = ImageDraw.Draw(textimage)
        textdraw.text((0,0), text, font=font, fill=fill)
        rotated = textimage.rotate(angle, expand=1)
        self.disp.buffer.paste(rotated, position, rotated)

    def draw_rotated_image(self, image, position, size, angle):
        width, height = size
        draw = ImageDraw.Draw(self.disp.buffer)
        rotated = image.rotate(angle, expand=1)
        rotated = rotated.resize((width, height))
        self.disp.buffer.paste(rotated, position, rotated)

    def stop(self):
        self.disp.stop()
