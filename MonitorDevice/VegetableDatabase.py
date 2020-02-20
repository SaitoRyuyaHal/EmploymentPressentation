#!/usr/bin/env python3

import csv
import datetime

class VegetableCsv():
    def __init__(self):
        self.vegetable_info_name = "VegetableInfo.csv"
        self.integral_temperature = "IntegralTemperature.csv"
        self.temperature = "Temperature.csv"
        self.log = "Log.csv"
        self.soil = "SoilMoisture.csv"
        self.water_pump_state = "WaterPumpState.csv"
        self.integral_temperature_reader = CsvRowReader(self.integral_temperature)
        self.integral_temperature_reader.read_row(0)
        self.temperature_and_humidity_reader = CsvRowReader(self.temperature)
        self.waterpump_speed_reader = CsvRowReader(self.water_pump_state)
        self.soil_reader = CsvRowReader(self.soil)
        self.vegetable_info = None
        self.vegetable_info_update()

    def createDatabase(self):
        with open(self.vegetable_info_name, 'w') as csvfile:
            writer = csv.writer(csvfile, lineterminator='\n', delimiter=',')
            writer.writerow(['NAME', 'HIGHSUITABLETEMPERATURE', 'LOWSUITABLETEMPERATURE', 
                            'HIGHGROWTHTEMPERATURE', 'LOWGROWTHTEMPERATURE', 
                            'NIGHTHIGHGROWTHTEMPERATURE', 'NIGHTLOWGROWTHTEMPERATURE', 
                            'HIGHHUMIDITY', 'LOWHUMIDITY', 'AMOUNTOFWATER', 'FRUITAMOUNTOFWATER',
                            'LOADINGTEMPERATURE','WATERING'])
            # tomato
            writer.writerow(['tomato', 28, 25, 28, 23, 15, 10, 20, 0, 40, 30, 900, 3])
            # eggplant
            writer.writerow(['eggplant', 30, 25, 30, 20, 18, 15, 80, 60, 20, 40, 1000, 1])

    def update(self):
        self.integral_temperature_reader = CsvRowReader(self.integral_temperature)
        self.temperature_and_humidity_reader = CsvRowReader(self.temperature)
        self.soil_reader = CsvRowReader(self.soil)

    def writeTemperatureAndHumidity(self, temp, humidity, now):
        with open(self.temperature, 'a') as csvfile:
            writer = csv.writer(csvfile, lineterminator='\n', delimiter=',')
            writer.writerow([now, temp, humidity])

    def readTemperatureAndHumidity(self):
        if self.temperature_and_humidity_reader.length() <= 0:
            return None

        l = []
        for i in range(self.temperature_and_humidity_reader.length()):
            l.append(self.temperature_and_humidity_reader.read_row(i))
        return l

    def writeIntegralTemperature(self, value, now):
        with open(self.integral_temperature, 'a') as csvfile:
            writer = csv.writer(csvfile, lineterminator='\n', delimiter=',')
            writer.writerow([now, value])

    def readIntegralTemperature(self):
        if self.integral_temperature_reader.length() <= 0:
            return None

        l = []
        for i in range(self.integral_temperature_reader.length()):
            l.append(self.integral_temperature_reader.read_row(i))
        return l

    def readIntegralTemperatureIndex(self, index):
        if self.integral_temperature_reader.length() <= 0:
            return None
        return self.integral_temperature_reader.read_row(index)

    def writeLog(self, value, now):
        with open(self.log, 'a') as csvfile:
            writer = csv.writer(csvfile, lineterminator='\n', delimiter=',')
            writer.writerow([now, value])

    def readLog(self):
        with open(self.log) as csvfile:
            reader = csv.DictReader(csvfile)
            l = [row for row in reader]
        return l

    def writeSoil(self, value, now):
        with open(self.soil, 'a') as csvfile:
            writer = csv.writer(csvfile, lineterminator='\n', delimiter=',')
            writer.writerow([now, value])

    def writeWaterPumpSpeed(self, value, now):
        with open(self.water_pump_state, 'a') as csvfile:
            writer = csv.writer(csvfile, lineterminator='\n', delimiter=',')
            writer.writerow([now, value])
        

    def vegetable_info_update(self):
        with open(self.vegetable_info_name) as csvfile:
            reader = csv.DictReader(csvfile)
            self.vegetable_info = [row for row in reader]

    def read_vegetable_info(self, index):
        return self.vegetable_info[index]

    def __day_list_create(self, reader, day):
        yeasterday = datetime.timedelta(hours=24)
        day_list = []
        for i in range(reader.length()):
            row = reader.read_row(i)
            time_data = datetime.datetime.strptime(row['TIME'],
                                       '%Y-%m-%d %H:%M:%S.%f')
            if day-yeasterday <= time_data < day:
                day_list.append(row)
        return day_list

    def read_day_temperature_and_humidity(self, day):
        if self.temperature_and_humidity_reader.length() <= 0:
            return None

        return self.__day_list_create(self.temperature_and_humidity_reader, day)

    def read_day_soil(self, day):
        if self.soil_reader.length() <= 0:
            return None

        return self.__day_list_create(self.soil_reader, day)

    def read_day_waterpump_speed(self, day):
        if self.waterpump_speed_reader.length() <= 0:
            return None

        return self.__day_list_create(self.waterpump_speed_reader, day)


class CsvRowReader:
    def __init__(self, path):
        f = open(path, 'r')
        self.file = f
        self.reader = csv.DictReader(f)
        self.offset_list = []
        while True:
            self.offset_list.append(f.tell())
            line = f.readline()
            if line == '':
                break
        self.offset_list.pop()
        self.num_rows = len(self.offset_list)

    def length(self):
        return len(self.offset_list) - 1

    def __del__(self):
        self.file.close()

    def read_row(self, idx):
        self.file.seek(self.offset_list[idx])
        return next(self.reader)
