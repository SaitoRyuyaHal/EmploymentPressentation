#!/usr/bin/env python3

import datetime


class TextCreator():
    def __init__(self):
        self.drive_state_name = ['stop', 'run', 'water_add']
        self.connect_state_name = ["Connect", "Disconnect"] 

    def water_pump_state(self, drive_state, now):
        time_now = now.strftime("%Y-%m-%d %H:%M:%S: ")
        drive_state_text = "water pump state: " + self.drive_state_name[drive_state]
#        return "{0}<br>&nbsp;&nbsp;&nbsp;&nbsp;{1}<br>".format(time_now, drive_state_text)
        return time_now, drive_state_text

    def soil_moisture_warning(self, soil, now, low_flag):
        time_now = now.strftime("%Y-%m-%d %H:%M:%S: ")
        if low_flag == 0:
            soil_text = "soil moisture is low: " + str(soil)
        elif low_flag == 1:
            soil_text = "soil moisutre is success: " + str(soil)

        #return "{0}<br>&nbsp;&nbsp;&nbsp;&nbsp;{1}<br>".format(time_now, soil_text)
        return time_now, soil_text

    def temp_high_low_warning(self, temp, now, high_low_flag):
        time_now = now.strftime("%Y-%m-%d %H:%M:%S: ")
        if high_low_flag == 0:
            temp_text = "temperature is high: " + str(temp)
        elif high_low_flag == 1:
            temp_text = "temperature is low: " + str(temp)
        elif high_low_flag == 2:
            temp_text = "temperature is success: " + str(temp)

        #return "{0}<br>&nbsp;&nbsp;&nbsp;&nbsp;{1}<br>".format(time_now, temp_text)
        return time_now, temp_text
        
    def humidity_high_low_warning(self, humidity, now, high_low_flag):
        time_now = now.strftime("%Y-%m-%d %H:%M:%S: ")
        if high_low_flag == 0:
            humidity_text = "humidity is high: " + str(humidity)
        elif high_low_flag == 1:
            humidity_text = "humidity is low: " + str(humidity)
        elif high_low_flag == 2:
            humidity_text = "humidity is success: " + str(humidity)

        #return "{0}<br>&nbsp;&nbsp;&nbsp;&nbsp;{1}<br>".format(time_now, humidity_text)
        return time_now, humidity_text
        

    def connect_state_text(self, name, state, now):
        time_now = now.strftime("%Y-%m%d %H:%M:%S: ")
        if state is True:
            text = "{0} state: {1}".format(name, "Connect")
            text = "{0}<br>&nbsp;&nbsp;&nbsp;&nbsp;{1}<br>".format(time_now, text)
            text = "<span style=\" color: green;\">{0}</span>".format(text)
        else:
            text = "{0} state: {1}".format(name, "DisConnect")
            text = "{0}<br>&nbsp;&nbsp;&nbsp;&nbsp;{1}<br>".format(time_now, text)
            text = "<span style=\" color: red;\">{0}</span>".format(text)
        return text
