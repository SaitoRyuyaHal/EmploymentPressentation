#!/usr/bin/python3
# -*- coding:utf-8 -*-

from ObserverPattern import Observer, Observable
from HumidityTempratureSensor import HumidityTemperatureDriver
from Clock import AlarmClock
from RaspberryPiDriver import GpioDriver
from LcdDriver import LcdDriver
from SoilSensor import SoilSensorDriver


class TemperatureObserver(Observer):
    def __init__(self):
        self.value = {"temperature": 0, "humidity": 0}
        self.monitor = None

    def setMonitor(self, monitor):
        self.monitor = monitor

    def update(self, model):
        self.value["temperature"] = model.templastValue
        self.value["humidity"] = model.humiditylastValue
        self.monitor.displayTempAndHumidity(self.value["temperature"], self.value["humidity"])

    def getTemperature(self):
        return self.value["temperature"]

    def getHumidity(self):
        return self.value["humidity"]


class TemperatureSensorObservable(Observable):
    def __init__(self):
        super().__init__()
        self.sensor = None
        self.templastValue = 0
        self.humiditylastValue = 0
        self.tempValue = 0
        self.humidityValue = 0
        self.values_size = 3
        self.tempValues = [0] * self.values_size
        self.humidityValues = [0] * self.values_size
        self.valuesCount = 0
        self.zeroCount = 0
        self.alrm = AlarmClock()
        self.alrm.wakeEvery(10, self.wakeUp)
        self.wakeUpFlag = False

    def start(self):
        self.alrm.start()

    def setSensor(self, sensor):
        self.sensor = sensor
        self.sensor.setUp()

    def setChanged(self):
        self.templastValue = self.tempValue
        self.humiditylastValue = self.humidityValue

    def wakeUp(self):
        self.wakeUpFlag = True

    def check(self):
        if self.wakeUpFlag is True:
            value = self.sensor.dataResponse()        
            if value['humidity'] != 0 and value['temperature'] != 0:
                self.tempValues[self.valuesCount] = value['temperature']
                self.humidityValues[self.valuesCount] = value['humidity']
                if self.valuesCount >= self.values_size - 1:
                    self.tempValue = 0
                    self.humidityValue = 0
                    for i in range(self.values_size):
                        self.tempValue += self.tempValues[i]
                        self.humidityValue += self.humidityValues[i]
                    self.tempValue = self.tempValue / self.values_size
                    self.humidityValue = self.humidityValue / self.values_size
                    if self.humidityValue != self.humiditylastValue or self.tempValue != self.templastValue:
                        self.setChanged()
                        self.notifyObservers()
                self.valuesCount = (self.valuesCount + 1) % self.values_size
            else:
                self.zeroCount += 1
                if self.zeroCount >= 20 * self.values_size:
                    self.setChanged()
                    self.notifyObservers()
                    self.zeroCount = 0
            self.wakeUpFlag = False


class SoilSensorObserver(Observer):
    def __init__(self):
        self.monitor = None
        self.value = 0

    def setMonitor(self, monitor):
        self.monitor = monitor

    def update(self, model):
        self.value = model.soillastValue
        self.monitor.displaySoil(self.value)

    def getSoil(self):
        return self.value


class SoilSensorObservable(Observable):
    def __init__(self):
        super().__init__()
        self.sensor = None
        self.soillastValue = 0
        self.values_size = 7
        self.valuesCount = 0
        self.soilValues = [0] * self.values_size
        self.soilValue = 0
        self.alrm = AlarmClock()
        self.alrm.wakeEvery(20, self.wakeUp)
        self.wakeUpFlag = False

    def start(self):
        self.alrm.start()

    def setSensor(self, sensor):
        self.sensor = sensor
        self.sensor.setUp()

    def setChanged(self):
        self.soillastValue = self.soilValue

    def wakeUp(self):
        self.wakeUpFlag = True

    def check(self):
        if self.wakeUpFlag is True:
            value = self.sensor.read()
            self.soilValues[self.valuesCount] = value
            if self.valuesCount >= self.values_size - 1:
                for i in range(self.values_size):
                    self.soilValue +=  self.soilValues[i]
                self.soilValue = self.soilValue / self.values_size
                if self.soilValue != self.soillastValue:
                    self.setChanged()
                    self.notifyObservers()
            self.valuesCount = (self.valuesCount + 1) % self.values_size
            self.wakeUpFlag = False


class MonitoringScreen:
    def __init__(self):
        self.tempObserver = TemperatureObserver()
        self.tempObserver.setMonitor(self)
        self.soilObserver = SoilSensorObserver()
        self.soilObserver.setMonitor(self)
        self.observable = None
        self.monitor = None

    def setMonitor(self, monitor):
        self.monitor = monitor
        self.monitor.setUp()
        self.monitor.init()
        self.monitor.clearScreen()

    def addTempObserver(self, observable):
        observable.addObserver(self.tempObserver)

    def addSoilObserver(self, observable):
        observable.addObserver(self.soilObserver)

    def displayTempAndHumidity(self, temp, humidity):
        temp = round(temp, 1)
        humidity = round(humidity, 1)
        temp_str =     "Temperature: "
        humidity_str = "Humidity   : "
        self.monitor.stringWrite(temp_str+str(temp), (0, 0))
        self.monitor.stringWrite(humidity_str+str(humidity), (1, 0))

    def displaySoil(self, soil):
        soil = str(int(soil))
        soil_str = "SoilMoisture: "
        self.monitor.stringWrite(soil_str+soil.rjust(3, ' '), (2, 0))

if __name__ == "__main__":
    gpio = GpioDriver()
    soil_observable = SoilSensorObservable()
    soil_sensor = SoilSensorDriver(0)
    soil_sensor.setGpio(gpio)
    temp_observable = TemperatureSensorObservable()
    temp_sensor = HumidityTemperatureDriver(27)
    temp_sensor.setGpio(gpio)
    lcd = LcdDriver(1, 23)
    lcd.setGpio(gpio)
    soil_observable.setSensor(soil_sensor)
    temp_observable.setSensor(temp_sensor)
    monitor = MonitoringScreen()
    monitor.setMonitor(lcd)
    monitor.addSoilObserver(soil_observable)
    monitor.addTempObserver(temp_observable)
    temp_observable.start()
    soil_observable.start()
    while True:
        temp_observable.check()
        soil_observable.check()

