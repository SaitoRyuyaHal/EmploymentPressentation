#!/usr/bin/env python3
#-*- coding:utf-8 -*-

class PidController():
    def __init__(self, p_gain, i_gain, d_gain, time_cycle):
        self.p_gain = p_gain
        self.i_gain = i_gain
        self.d_gain = d_gain
        self.time_cycle = time_cycle
        self.error_integral = 0
        self.diff = 0
        self.last_error = 0

    def feedback(self, target, input_value):
        error = target["AMOUNT_OF_WATER"] - input_value
        error_integral_step = error * self.time_cycle
        self.error_integral += error_integral_step
        error_diff = (error - self.last_error) / self.time_cycle
        self.last_error = error
        return self.p_gain * error + self.i_gain * self.error_integral + self.d_gain * error_diff
