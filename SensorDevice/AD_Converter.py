from RaspberryPiDriver import GpioDriver

class AD_Converter():
    CHANNEL_DATA = [b'\x06\x00\x00', b'\x06\x40\x00', b'\x06\x80\x00', b'\x07\xc0\x00',
                    b'\x07\x00\x00', b'\x07\x40\x00', b'\x07\x80\x00', b'\x07\xc0\x00']
    def __init__(self, spi_channel):
        self.gpio = None
        self.ss = GpioDriver.SPICHANNEL[spi_channel]
        self.sclk = 11
        self.miso = 9
        self.mosi = 10
        self.spi_channel = spi_channel

    def set_gpio(self, gpio):
        self.gpio = gpio

    def get_ss(self):
        return self.ss

    def get_sclk(self):
        return self.sclk

    def get_miso(self):
        return self.miso

    def get_mosi(self):
        return self.mosi

    def setup(self):
        if self.gpio.setGpio() != True:
            return False
        if self.gpio.setSpi(self.spi_channel, 10000000, 0) != True:
            return False
        return True

    def read(self, ch):
        self.gpio.digitalWrite(self.ss, 0)
        num, returnData = self.gpio.spiDataRW(self.spi_channel,
            AD_Converter.CHANNEL_DATA[ch])
        self.gpio.digitalWrite(self.ss, 1)
        return ((returnData[1] & 0x0f) << 8) | returnData[2]

    def close(self):
        self.gpio.spiClose(self.spi_channel)
