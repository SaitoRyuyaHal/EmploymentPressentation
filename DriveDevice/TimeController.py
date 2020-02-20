#!/usr/bin/env python3

import datetime
import schedule
import time


class TimeController():
    def __init__(self, soil_weight, pump_power):
        self.pump_start_flag = False
        self.pump_run_flag = False
        self.soil_weight = soil_weight
        self.pump_power = pump_power
        self.pump_run_flag = False
        self.pump_cycle_time = 0
        self.pump_run_start_time = None
        self.pump_run_end_time = None
        self.day_pump_run_count = None
        self.pump_run_times = list()

    def run(self):
        schedule.run_pending()
    
    def pump_run(self):
        self.pump_run_flag = True

    def feedback(self, target, input_value):
        if self.day_pump_run_count is None:
            self.day_pump_run_count = target["WATERING"]
            for i in range(1, self.day_pump_run_count+1):
                self.pump_run_times.append(str(6 + (i*3)))
            for i in self.pump_run_times:
                schedule.every().day.at("{0}:30".format(i.zfill(2))).do(self.pump_run)

        if self.pump_run_flag is False:
            return 0

        error = (target["AMOUNT_OF_WATER"] - input_value) / 100
        if error <= 0:
            return 0
        water_volume = ((self.soil_weight * error) / (1 - error))
        self.pump_cycle_time = water_volume / self.pump_power
        if self.pump_start_flag is False:
            self.pump_start_flag = True
            self.pump_run_start_time = datetime.datetime.now()
            time_data = datetime.timedelta(
                seconds=int(self.pump_cycle_time), 
                microseconds=int(self.pump_cycle_time*100))
            self.pump_run_end_time = self.pump_run_start_time + time_data
        now_time = datetime.datetime.now()
        if now_time < self.pump_run_end_time:
            return 100
        else:
            self.pump_start_flag = False
            self.pump_run_flag = False
            return 0

    def reset(self):
        self.pump_start_flag = False


if __name__ == "__main__":
    controller = TimeController(500, 66.6)
    while True:
        try:
            schedule.run_pending()
            profile = {"WATERING": 3, "AMOUNT_OF_WATER": 40}
            print(controller.feedback(profile, 0))
            print(datetime.datetime.now())
        except Exception as e:
            print(e)
            break
    


