#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time
from RaspberryPiDriver import GpioDriver
from AD_Converter import AD_Converter

class WaterLevelSensor():
    def __init__(self, spi_channel):
        self.ad = AD_Converter(spi_channel)
        self.spi_channel = spi_channel
        self.empty_threshold = 1000
        self.middle_threshold = 1500
        self.full_threshold = 2000

    def set_gpio(self, gpio):
        self.ad.set_gpio(gpio)

    def setup(self):
        if self.ad.setup() !=True:
            return False
        return True

    def read(self):
        adValue = self.ad.read(0)
        if adValue < self.empty_threshold:
            water_level = 0
        elif  self.empty_threshold <= adValue <= self.middle_threshold:
            water_level = 1
        elif self.middle_threshold < adValue <= self.full_threshold:
            water_level = 2
        else:
            water_level = 3
        return water_level

    def close(self):
        self.ad.close()


if __name__ == "__main__":
    water = WaterLevelSensor(0)
    gpio = GpioDriver()
    water.set_gpio(gpio)
    if water.setup() == True:
        print("OK")
    else:
        print("Failed")
    while(1):
        print(water.read())
        time.sleep(1)
    water.close()
