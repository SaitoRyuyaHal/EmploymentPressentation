import pigpio

class GpioDriver(object):
    # DEFINE
    SPICHANNEL = {0:8, 1:7} 
    OUTPUT = pigpio.OUTPUT
    INPUT = pigpio.INPUT
    PUD_OFF = pigpio.PUD_OFF
    PUD_UP = pigpio.PUD_UP
    PUD_DOWN = pigpio.PUD_DOWN
    EITHER_EDGE = pigpio.EITHER_EDGE
    RISING_EDGE = pigpio.RISING_EDGE
    FALLING_EDGE = pigpio.FALLING_EDGE
    # MEDIATOR 
    pinStatDict = {}
    pinValDict = {}
    pi = None
    spiDict = {}
    spiSpeed = {}
    i2cDict = {}
    i2cAddress = {}
    pullStateDict = {}
    watchdog_sec = {}
    callback = {}
    def __init__(self):
        pass

    def setGpio(self):
        if GpioDriver.pi is None:
            GpioDriver.pi = pigpio.pi()
        if not GpioDriver.pi.connected:
            return False
        return True

    def close(self):
        for i in GpioDriver.spiDict.keys():
            GpioDriver.pi.spi_close(GpioDriver.spiDict[i])
        GpioDriver.pi.stop()
        GpioDriver.pi = None
        GpioDriver.pinStatDict = {}
        GpioDriver.pinValDict = {}
        GpioDriver.spiDict = {}
        GpioDriver.spiSpeed = {}
        GpioDriver.i2cDict = {}
        GpioDriver.i2cAddress = {}
        GpioDriver.pullStateDict = {}
        GpioDriver.watchdog_sec = {}
        GpioDriver.callback = {}

    def init(self):
        GpioDriver.pi = pigpio.pi()
        GpioDriver.pinStatDict = {}
        GpioDriver.pinValDict = {}
        GpioDriver.spiDict = {}
        GpioDriver.spiSpeed = {}
        GpioDriver.i2cDict = {}
        GpioDriver.i2cAddress = {}
        GpioDriver.pullStateDict = {}
        GpioDriver.watchdog_sec = {}
        GpioDriver.callback = {}
        
    def setMode(self, pinNumber, pinStatus):
        GpioDriver.pi.set_mode(pinNumber, pinStatus)
        GpioDriver.pinStatDict[pinNumber] = pinStatus

    def setPullUpDown(self, pinNumber, pullState):
        GpioDriver.pi.set_pull_up_down(pinNumber, pullState)
        GpioDriver.pullStateDict[pinNumber] = pullState

    def setWatchDog(self, pinNumber, watch_dog_msec):
        GpioDriver.pi.set_watchdog(pinNumber, watch_dog_msec)
        GpioDriver.watchdog_sec[pinNumber] = watch_dog_msec

    def setCallbackFunc(self, pinNumber, trigger, callback_func):
        GpioDriver.pi.callback(pinNumber, trigger, callback_func)
        GpioDriver.callback[pinNumber] = callback_func

    def getWatchDog(self, pinNumber):
        return GpioDriver.watchdog_sec[pinNumber]

    def getMode(self, pinNumber):
        return GpioDriver.pinStatDict[pinNumber]

    def getVal(self, pinNumber):
        return GpioDriver.pinValDict[pinNumber]

    def getPullState(self, pinNumber):
        return GpioDriver.pullStateDict[pinNumber]

    def hardware_PWM(self, pinNumber, hz, duty):
        GpioDriver.pi.hardware_PWM(pinNumber, hz, duty)

    def setSpi(self, channel, speed, mode_flag):
        GpioDriver.spiDict[channel] = GpioDriver.pi.spi_open(channel, speed, mode_flag)
        GpioDriver.spiSpeed[channel] = speed
        return True

    def closeSpi(self, channel):
        GpioDriver.pi.spi_close(GpioDriver.spiDict[channel])

    def getSpiMps(self, channel):
        return GpioDriver.spiSpeed[channel]

    def getCallbackFunc(self, pinNumber):
        return GpioDriver.callback[pinNumber]

    def digitalWrite(self, pin, pin_val):
        GpioDriver.pi.write(pin, pin_val)
        GpioDriver.pinValDict[pin] = pin_val

    def digitalRead(self, pin):
        pin_val = GpioDriver.pi.read(pin)
        GpioDriver.pinValDict[pin] = pin_val
        return pin_val

    def spiDataWrite(self, channel, data):
        GpioDriver.pi.spi_write(GpioDriver.spiDict[channel], data)

    def spiDataRead(self, channel, count):
        return GpioDriver.pi.spi_read(GpioDriver.spiDict[channel], count)

    def spiDataRW(self, channel, dataList):
        count, rx_data = GpioDriver.pi.spi_xfer(GpioDriver.spiDict[channel], dataList)
        return (count, rx_data)

    def spiClose(self, channel):
        GpioDriver.pi.spi_close(GpioDriver.spiDict[channel])

    def tickDiff(self, t1, t2):
        return pigpio.tickDiff(t1, t2)

    def setI2C(self, i2c_number, i2c_address):
        GpioDriver.i2cDict[i2c_number] = GpioDriver.pi.i2c_open(i2c_number, i2c_address, 0)
        GpioDriver.i2cAddress[i2c_number] = i2c_address

    def getAddressI2C(self, i2c_number):
        return GpioDriver.i2cAddress[i2c_number]

    def writeI2C(self, i2c_number, data):
        GpioDriver.pi.i2c_write_byte(GpioDriver.i2cDict[i2c_number], data)

    def readI2C(self, i2c_number):
        return GpioDriver.pi.i2c_read_byte(GpioDriver.i2cDict[i2c_number])

    def closeI2C(self, i2c_number):
        GpioDriver.pi.i2c_close(self.i2cDict[i2c_number])
        GpioDriver.i2cDict[i2c_number] = None
        GpioDriver.i2cAddress[i2c_number] = None
