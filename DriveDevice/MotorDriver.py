#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time
from RaspberryPiDriver import GpioDriver

class MotorDriver():
    def __init__(self, pwm):
        self.pwm = pwm
        self.gpio = None

    def set_gpio(self, gpio):
        self.gpio = gpio

    def setup(self):
        if self.gpio.setGpio() != True:
            return False
        self.gpio.setMode(self.pwm, GpioDriver.OUTPUT)
        self.gpio.digitalWrite(self.pwm, 0)
        return True

    def forward(self, duty):
        self.gpio.hardware_PWM(self.pwm, 1, int(duty*10000))

    def stop(self):
        self.gpio.digitalWrite(self.pwm, 0)


if __name__ == "__main__":
    gpio = GpioDriver()
    motor = MotorDriver(18)
    motor.set_gpio(gpio)
    motor.setup()
    motor.forward(100)
    time.sleep(1)
    motor.stop()
