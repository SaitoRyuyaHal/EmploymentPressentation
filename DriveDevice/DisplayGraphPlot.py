#!/usr/bin/env python3

from ST7735LcdDriver import ST7735
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from datetime import datetime

SOIL_COLOR = (124, 252, 0)
TEMPERATURE_COLOR = (71, 99, 255)
HUMIDITY_COLOR = (235, 206, 135)
WATER_COLOR = (252, 241, 19)


class DisplayGraphPlot():
    def __init__(self):
        self.width = 128
        self.height = 160
        self.soil_value = 0
        self.temperature = 0
        self.disp = ST7735(16, 1, rst=26)
        self.disp.begin()
        self.disp.clear((0, 0, 0))
        self.big_font = ImageFont.truetype("/usr/share/fonts/truetype/anonymous-pro/Anonymous Pro B.ttf", 15)
        self.middle_font = ImageFont.truetype("/usr/share/fonts/truetype/anonymous-pro/Anonymous Pro B.ttf", 13)
        self.small_font = ImageFont.truetype("/usr/share/fonts/truetype/anonymous-pro/Anonymous Pro B.ttf", 10)
        self.draw_rotated_text("PLANTER OBSERVATION SYSTEM", (5, 20), 90, self.small_font, fill=(255, 255, 255))
        self.draw_rotated_text("SOIL", (20, 130), 90, self.small_font, fill=SOIL_COLOR)
        self.draw_rotated_text("%", (30, 100), 90, self.small_font, fill=SOIL_COLOR)
        self.draw_rotated_text("TEMPERATURE", (20, 35), 90, self.small_font, fill=TEMPERATURE_COLOR)
        self.draw_rotated_text("HUMIDITY", (45, 45), 90, self.small_font, fill=HUMIDITY_COLOR)
        self.draw_rotated_text("%", (55, 20), 90, self.small_font, fill=HUMIDITY_COLOR)
        self.draw_rotated_text("WaterLevel", (80, 100), 90, self.small_font, fill=WATER_COLOR)
        self.draw_rotated_text("DeviceState", (80, 20), 90, self.small_font, fill=WATER_COLOR)
        self.disp.display()
    
    def displaySoilGraph(self, value):
        draw = self.disp.draw()
        draw.rectangle((30, 155, 43, 109), outline=(0, 0, 0), fill=(0, 0, 0))
        self.soil_value = value
        self.draw_rotated_text(str(self.soil_value), (30, 110), 90, self.middle_font, fill=SOIL_COLOR)
        self.disp.display()

    def displayTemperatureAndHumidityGraph(self, temperature, humidity):
        draw = self.disp.draw()
        draw.rectangle((30, 80, 43, 20), outline=(0, 0, 0), fill=(0, 0, 0))
        draw.rectangle((55, 70, 67, 30), outline=(0, 0, 0), fill=(0, 0, 0))

        self.temperature = temperature
        self.draw_rotated_text(str(self.temperature), (30, 35), 90, self.middle_font, fill=TEMPERATURE_COLOR)
        self.humidity = humidity
        self.draw_rotated_text(str(self.humidity), (55, 35), 90, self.middle_font, fill=HUMIDITY_COLOR)
        self.disp.display()

    def displayWaterLevel(self, value):
        draw = self.disp.draw()
        draw.rectangle((95, 130, 108, 90), outline=(0, 0, 0), fill=(0, 0, 0))
        water_level_text = ""
        if value == 0:
            water_level_text = "Empty"
        elif value == 1:
            water_level_text = "Low"
        elif value == 2:
            water_level_text = "Middle"
        else:
            water_level_text = "High"
        self.draw_rotated_text(water_level_text, (95, 100), 90, self.small_font, fill=WATER_COLOR)
        self.disp.display()

    def displayConnectDevice(self, value):
        draw = self.disp.draw()
        draw.rectangle((95, 70, 108, 20), outline=(0, 0, 0), fill=(0, 0, 0))
        connect_device_text = ""
        if value == 0:
            connect_device_text = "Disconnect"
        else:
            connect_device_text = "Connect"
        self.draw_rotated_text(connect_device_text,
                               (95, 20), 90, self.small_font, fill=WATER_COLOR)
        self.disp.display()


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

    def close(self):
        self.disp.close()


if __name__ == "__main__":
    display = DisplayGraphPlot()
    display.displaySoilGraph(20)
    display.displayTemperatureAndHumidityGraph(30, 50)
    display.displayWaterLevel(1)
    display.displayWaterLevel(2)
    display.displayWaterLevel(1)
    display.displayConnectDevice(0)
    display.displayConnectDevice(1)
    display.close()
