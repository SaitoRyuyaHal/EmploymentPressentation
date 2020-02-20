#!/usr/bin/env python3

soil_listener = set()
temp_and_humidity_listener = set()
water_supply_listener = set()
drive_state_listener = set()
water_pump_state_listener = set()
interfaces_removed_listener = set()

class AlarmBle:
    def __init__(self, refresh=False):
        if refresh:
            global soil_listener
            global temp_and_humidity_listener
            global water_supply_listener
            global drive_state_listener
            global water_pump_state_listener
            soil_listener = set()
            temp_and_humidity_listener = set()
            water_supply_listener = set()
            drive_state_listener = set()
            water_pump_state_listener = set()

    def add_soil(self, BleListener):
        soil_listener.add(BleListener)

    def add_temp_and_humidity(self, BleListener):
        temp_and_humidity_listener.add(BleListener)

    def add_water_supply(self, BleListener):
        water_supply_listener.add(BleListener)

    def add_drive_state(self, BleListener):
        drive_state_listener.add(BleListener)

    def add_water_pump_state(self, BleListener):
        water_pump_state_listener.add(BleListener)

    def wakeup_soil(self, value):
        for listener in soil_listener:
            listener.wakeup(value)

    def wakeup_temp_and_humidity(self, value):
        for listener in temp_and_humidity_listener:
            listener.wakeup(value)

    def wakeup_water_supply(self, value):
        for listener in water_supply_listener:
            listener.wakeup(value)

    def wakeup_drive_state(self, value):
        for listener in drive_state_listener:
            listener.wakeup(value)

    def wakeup_water_pump_state(self, value):
        for listener in water_pump_state_listener:
            listener.wakeup(value)

class BleListener:
    def __init__(self, invocation_class):
        self.__value = 0
        self.invocation_class = invocation_class

    def wakeup(self, value):
        self.__value = value
        self.invocation_class.check()

    def read(self):
        return self.__value
