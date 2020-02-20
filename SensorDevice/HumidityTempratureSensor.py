import time
from RaspberryPiDriver import GpioDriver


class HumidityTemperatureDriver:
    def __init__(self, sensorPin):
        self.gpio = None
        self.sensorPin = sensorPin
        self.high_tick = 0
        self.bit = 40
        self.temperature = 0
        self.humidity = 0
        self.last_temperature = 0
        self.last_humidity = 0
        self.either_edge_cb = None

    def getGpio(self):
        return self.sensorPin

    def getGpioVal(self):
        return self.gpio.getMode(self.sensorPin)

    def getGpioMode(self):
        return self.gpio.getVal(self.sensorPin)

    def setGpio(self, Gpio):
        self.gpio = Gpio

    def setUp(self):
        if self.gpio.setGpio() != True:
            return False
        self.gpio.setPullUpDown(self.sensorPin, GpioDriver.PUD_OFF)
        self.gpio.setWatchDog(self.sensorPin, 0)
        self.register_callbacks()
        return True

    def register_callbacks(self):
        self.either_edge_cb = self.gpio.setCallbackFunc(
            self.sensorPin,
            GpioDriver.EITHER_EDGE,
            self.either_edge_callback
        )

    def either_edge_callback(self, gpio, level, tick):
        level_handlers = {
            GpioDriver.FALLING_EDGE: self._edge_FALL,
            GpioDriver.RISING_EDGE: self._edge_RISE,
            GpioDriver.EITHER_EDGE: self._edge_EITHER
        }
        handler = level_handlers[level]
        diff = self.gpio.tickDiff(self.high_tick, tick)
        handler(tick, diff)

    def _edge_RISE(self, tick, diff):
        val = 0
        if diff >= 50:
            val = 1
        if diff >= 200:
            self.checksum = 256

        if self.bit >= 40:
            self.bit = 40
        elif self.bit >= 32:
            self.checksum = (self.checksum << 1) + val
            if self.bit == 39:
                self.gpio.setWatchDog(self.sensorPin, 0)
                total = self.humidity + self.temperature
                if not (total & 255) == self.checksum:
                    try:
                        raise Exception
                    except Exception as e:
                        pass
        elif 16 <= self.bit < 24:
            self.temperature = (self.temperature << 1) + val
        elif 0 <= self.bit < 8:
            self.humidity = (self.humidity << 1) + val
        else:
            pass
        self.bit += 1

    def _edge_FALL(self, tick, diff):
        self.high_tick = tick
        if diff <= 250000:
            return
        self.bit = -2
        self.checksum = 0
        self.last_temperature = self.temperature
        self.last_humidity = self.last_humidity
        self.temperature = 0
        self.humidity = 0
        
    def _edge_EITHER(self, tick, diff):
        self.gpio.setWatchDog(self.sensorPin, 0)

    def read(self):
        self.gpio.setMode(self.sensorPin, GpioDriver.OUTPUT)
        self.gpio.digitalWrite(self.sensorPin, 0)
        time.sleep(0.017)
        self.gpio.setMode(self.sensorPin, GpioDriver.INPUT)
        self.gpio.setWatchDog(self.sensorPin, 200)
        time.sleep(0.2)

    def dataResponse(self):
        self.read()
        response = {
            'humidity': self.humidity,
            'temperature': self.temperature
        }
        return response

    def close(self):
        self.gpio.setWatchDog(self.sensorPin, 0)
        if self.either_edge_cb:
            self.either_edge_cb.cancel()
            self.either_edge_cb = None

    def __iter__(self):
        return self

    def __next__(self):
        self.read()
        response = {
            'humidity': self.humidity,
            'temperature': self.temperature
        }
        return response

if __name__ == "__main__":
    sensor = HumidityTemperatureDriver(16)
    gpio = GpioDriver()
    sensor.setGpio(gpio)
    sensor.setUp()
    for d in sensor:
        print("temperature: {}".format(d['temperature']))
        print("humidity: {}".format(d['humidity']))
        time.sleep(1)
    sensor.close()
