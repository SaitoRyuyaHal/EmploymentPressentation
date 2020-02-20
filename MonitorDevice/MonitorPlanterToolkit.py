#!/usr/bin/env python3


from AlarmClock import AlarmClock
from AlarmBle import AlarmBle
from VegetableDatabase import VegetableCsv
from TextCreator import TextCreator
from ObserverPattern import Observer


class ConnectStates:
    def __init__(self):
        self.connect_states = {
            "water_pump": False, 
            "fertilizer": False,
            "sensor": False}

    def get_connect_states(self):
        return self.connect_states


    def set_connect_states(self, name, state):
        self.connect_states[name] = state


class PlanterToolkit:
    def __init__(self):
        self.vegetable_info = 0
        self.data_base = VegetableCsv()
        self.connect_states = ConnectStates()

    def setVegetableInfo(self, value):
        self.vegetable_info = value

    def getVegetableProfile(self):
        return self.data_base.read_vegetable_info(self.vegetable_info)
    
    def getDataBase(self):
        return self.data_base

    def getVegetableInfo(self):
        return self.vegetable_info

    def getAlarmClock(self):
        return AlarmClock()

    def getAlarmBle(self):
        return AlarmBle()

    def getConnectStates(self):
        return self.connect_states

    def getWaterPumpGraph(self):
        return self.water_pump_graph_observer

    def createTextCreator(self):
        return TextCreator()

