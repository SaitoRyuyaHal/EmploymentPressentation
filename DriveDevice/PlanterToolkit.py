#!/usr/bin/env python3

from VegetableDatabase import VegetableCsv
from AlarmClock import AlarmClock
from AlarmBle import AlarmBle
from MotorDriver import MotorDriver
from PidController import PidController
from TimeController import TimeController
from Switch import SwitchDriver
from WaterLevelSensor import WaterLevelSensor
from DisplayGraphPlot import DisplayGraphPlot
from RaspberryPiDriver import GpioDriver
from VegetableDatabase import VegetableCsv


class VegetableProfile():
    high_suitable_temperature = 0
    low_suitable_temperature = 0
    high_grow_temperature = 0
    low_grow_temperature = 0
    night_high_grow_temperature = 0
    night_low_grow_temperature = 0
    high_humidity = 0
    low_humidity = 0
    amount_of_water = 0
    fruit_amount_of_water = 0
    loading_temperature = 0
    watering=0
    update_flag = False
    def __init__(self):
        pass

    def is_update(self):
        return self.update_flag

    def get_profile(self):
        return {"HIGH_SUITABLE_TEMPERATURE": self.high_suitable_temperature,
                "LOW_SUITABLE_TEMPERATURE": self.low_suitable_temperature, 
                "HIHG_GROW_TEMPERATURE": self.high_grow_temperature,
                "LOW_GROW_TEMPERATURE": self.low_grow_temperature,
                "NIGHT_HIGH_GROW_TEMPERATURE": self.night_high_grow_temperature,
                "NIGHT_LOW_GROW_TEMPERATURE": self.night_low_grow_temperature,
                "HIGH_HUMIDITY": self.high_humidity, "LOW_HUMIDITY": self.low_humidity,
                "AMOUNT_OF_WATER": self.amount_of_water, 
                "FRUIT_AMOUNT_OF_WATER": self.fruit_amount_of_water,
                "LOADING_TEMPERATURE": self.loading_temperature,
                "WATERING": self.watering}

    def update(self, values):
        self.high_suitable_temperature = values[0]
        self.low_suitable_temperature = values[1]
        self.high_grow_temperature = values[2]
        self.low_grow_temperature = values[3]
        self.night_high_grow_temperature = values[4]
        self.night_low_grow_temperature = values[5]
        self.high_humidity = values[6]
        self.low_humidity = values[7]
        self.amount_of_water = values[8]
        self.fruit_amount_of_water = values[9]
        self.loading_temperature = values[10]
        self.watering = values[11]
        self.update_flag = True


class PlanterToolkit:
    def __init__(self):
        self.wp_cycle = 0.5
        self.wp_p_gain = 0.02
        self.wp_i_gain = 0.1
        self.wp_d_gain = 0.5
        self.soil_weight = 500
        self.pump_power = 0.666
        self.gpio = GpioDriver()
        self.gpio.setGpio()
        self.monitor = None
        self.vegetable_profile = None
        self.motor_driver = MotorDriver(18)
        self.motor_driver.set_gpio(self.gpio)
        self.motor_driver.setup()
        self.motor_driver.stop()

    def getVegetableProfile(self):
        if self.vegetable_profile is None:
            self.vegetable_profile = VegetableProfile()
        return self.vegetable_profile

    def getMonitor(self):
        if self.monitor is None:
            self.monitor = DisplayGraphPlot()
        return self.monitor

    def getAlarmClock(self):
        return AlarmClock()

    def getAlarmBle(self):
        return AlarmBle()

    def makeWaterLevel(self):
        water_level_sensor = WaterLevelSensor(0)
        water_level_sensor.set_gpio(self.gpio)
        water_level_sensor.setup()
        return water_level_sensor

    def makeWaterPumpPidController(self):
        return PidController(self.wp_cycle, self.wp_p_gain,
                             self.wp_i_gain, self.wp_d_gain)

    def makeWaterPumpTimeController(self):
        return TimeController(self.soil_weight, self.pump_power)

    def makeWaterPump(self):
        return self.motor_driver

    def makeDatabase(self):
        return VegetableCsv()

    def makeAdvertisingSwitch(self):
        switch = SwitchDriver(23)
        switch.setGpio(self.gpio)
        switch.setUp()
        return switch
