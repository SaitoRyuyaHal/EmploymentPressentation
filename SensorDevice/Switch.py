#!/usr/bin/python3
# -*- coding:utf-8 -*-

from RaspberryPiDriver import GpioDriver
import time
try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject
mainloop = None

class SwitchDriver:
    def __init__(self, pinNumber):
        self.pinNumber = pinNumber
        self.gpio = None
        self.sampling_count = 0
        self.switch_on = 0b00001110
        self.switch_off = 0b00000000
        self.switch_state = 0

    def setGpio(self, gpio):
        self.gpio = gpio

    def setUp(self):
        if self.gpio.setGpio() != True:
            return False
        self.gpio.setMode(self.pinNumber, GpioDriver.INPUT)
        self.gpio.setPullUpDown(self.pinNumber, GpioDriver.PUD_UP)
        return True

    def sampling(self):
        self.sampling_count |= self.gpio.digitalRead(self.pinNumber)
        self.sampling_count = (self.sampling_count << 1) & 0xff
        self.sampling_flag = False
        return True

    def read(self):
        if (self.sampling_count & 0x0f) == self.switch_on:
            self.switch_state = 1
            self.sampling_count = 0
        elif (self.sampling_count & 0x0f) == self.switch_off:
            self.switch_state = 0
            self.sampling_count = 0
        return self.switch_state

switch = None

def switch_print():
    state = switch.read()
    print(state)
    return True


if __name__ == "__main__":
    switch = SwitchDriver(26)
    switch.setGpio(GpioDriver())
    switch.setUp()
    GObject.timeout_add(50, switch.sampling)
    GObject.timeout_add(500, switch_print)
    mainloop = GObject.MainLoop()

    try:
        mainloop.run()
    except Exception as e:
        mainloop.quit()


