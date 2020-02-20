import time
from RaspberryPiDriver import GpioDriver
from AD_Converter import AD_Converter

class SoilSensorDriver(object):
    def __init__(self, spi_channel):
        self.spi_channel = spi_channel
        self.ad = AD_Converter(spi_channel)
        self.dryThreshold = 4094
        self.waterThreshold = 2047

    def getSpiSS(self):
        return self.ad.get_ss()

    def getSpiSCLK(self):
        return self.ad.get_sclk()

    def getSpiMISO(self):
        return self.ad.get_miso()
        
    def getSpiMOSI(self):
        return self.ad.get_mosi()

    def setGpio(self, Gpio):
        self.ad.set_gpio(Gpio)

    def setUp(self):
        if self.ad.setup() != True:
            return False
        return True

    def read(self):
        adValue = self.ad.read(0)
        tempw1 = adValue - self.waterThreshold
        tempw2 = self.dryThreshold - self.waterThreshold
        templ1 = tempw1 * 100
        templ1 = templ1 / tempw2
        moisture = 100 - templ1
        if moisture > 100:
            moisture = 100
        if moisture < 0:
            moisture = 0
        return moisture

    def close(self):
        self.ad.close()

if __name__ == "__main__":
    soil = SoilSensorDriver(0)
    gpio = GpioDriver()
    soil.setGpio(gpio)
    if soil.setUp() == True:
        print("OK")
    else:
        print("Faield")
    while(1):
        print(soil.read())
        time.sleep(0.5)
    soil.close()
