#!/usr/bin/env python3

import csv

class VegetableCsv():
    def __init__(self):
        self.vegetable_info_name = "VegetableInfo.csv"
        self.vegetable_info = None
        self.vegetable_info_update()

    def createDatabase(self):
        with open(self.vegetable_info_name, 'w') as csvfile:
            writer = csv.writer(csvfile, lineterminator='\n', delimiter=',')
            writer.writerow(['NAME', 'HIGHSUITABLETEMPERATURE', 'LOWSUITABLETEMPERATURE', 
                            'HIGHGROWTHTEMPERATURE', 'LOWGROWTHTEMPERATURE', 
                            'NIGHTHIGHGROWTHTEMPERATURE', 'NIGHTLOWGROWTHTEMPERATURE', 
                            'HIGHHUMIDITY', 'LOWHUMIDITY', 'AMOUNTOFWATER', 'FRUITAMOUNTOFWATER',
                            'LOADINGTEMPERATURE',])
            # tomato
            writer.writerow(['tomato', 28, 25, 28, 23, 15, 10, 20, 0, 40, 30, 900])
            # eggplant
            writer.writerow(['eggplant', 30, 25, 30, 20, 18, 15, 80, 60, 20, 40, 1000])

    def vegetable_info_update(self):
        with open(self.vegetable_info_name) as csvfile:
            reader = csv.DictReader(csvfile)
            self.vegetable_info = [row for row in reader]

    def read_vegetable_info(self, index):
        return self.vegetable_info[index]
