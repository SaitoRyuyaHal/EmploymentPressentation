#!/usr/bin/env python3
# -*-coding:utf-8 -*-

import dbus
import dbus.exceptions
import dbus.service

import array
import pigpio
import time
import sys
import xml.etree.ElementTree as ET

from BleApi import *
from ObserverPattern import Observer, Observable
from VegetableDatabase import VegetableCsv
from DisplayGraphPlot import DisplayGraphPlot
from RaspberryPiDriver import GpioDriver
from AlarmBle import BleListener
from PlanterToolkit import PlanterToolkit


SENSOR_DEVICE = "dev_B8_27_EB_97_96_9F"
state_machine = None


class DriveDeviceAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, "peripheral")
        self.add_local_name("DeviceDrive")


class ServiceClient():
    def __init__(self, bus, UUID):
        self.service = None
        self.bus = bus
        self.uuid = UUID

    def process_service(self, service_path, chrc_paths):
        service = self.bus.get_object(BLUEZ_SERVICE_NAME, service_path)
        service_props = service.GetAll(GATT_SERVICE_IFACE,
                                       dbus_interface=DBUS_PROP_IFACE)

        uuid = service_props['UUID']

        if uuid != self.uuid:
            return False

        print('Service found: ' + service_path)

        for chrc_path in chrc_paths:
            self.process_chrc(chrc_path)

        self.service = (service, service_props, service_path)

        return True

    def process_chrc(self, chrc_path):
        pass

    def start_client(self):
        pass

    def isService(self):
        return self.service is not None

    def generic_error_cb(self, error):
        print('D-Bus call failed: ' + str(error))
        state_machine.disconnect()
        while True:
            if state_machine.connecting() == True:
                break
        state_machine.connect()


class GattServer(dbus.service.Object):
    def __init__(self, bus, pt):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        self.device_drive_service = DeviceDriveService(bus, 0, pt)
        self.add_service(self.device_drive_service)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        print('GetManagedObjects')

        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()

        return response

class GattClient:
    def __init__(self, bus, pt):
        self.bus = bus
        self.server_services = [] 
        self.pt = pt
        self.vegetable_info = None
        self.environment_service_client = EnvironmentServiceClient(
            bus, ENVIRONMENT_UUID, pt)
        self.add_server_service(self.environment_service_client)
        self.chrcs = []
        self.om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'), DBUS_OM_IFACE)
        self.om.connect_to_signal('InterfacesRemoved', self.interfaces_removed_cb)
        self.om.connect_to_signal("InterfaceAdded", self.interfaces_added_cb)
        print('Getting objects...')
        self.objects = self.om.GetManagedObjects()
        self.list_characteristics_found()
        self.list_service_found()
        self.start_client()

    def add_server_service(self, service):
        self.server_services.append(service)

    def list_characteristics_found(self):
        for path, interfaces in self.objects.items():
            if GATT_CHRC_IFACE not in interfaces.keys():
                continue
            self.chrcs.append(path)

    def list_service_found(self):
        for path, interfaces in self.objects.items():
            if GATT_SERVICE_IFACE not in interfaces.keys():
                continue

            chrc_paths = [d for d in self.chrcs if d.startswith(path + "/")]

            for service in self.server_services:
                if service.process_service(path, chrc_paths):
                    break

        for service in self.server_services:
            if not service.isService():
                print('No Environment Service found')
                sys.exit(1)

    def start_client(self):
        for service in self.server_services:
            service.start_client()

    def interfaces_added_cb(self, object_path, interfaces):
        if not self.server_services:
            return

    def interfaces_removed_cb(self, object_path, interfaces):
        if not self.server_services:
            return

        for service in self.server_services:
            if object_path == service.service[2]:
                print('Service was removed')
                state_machine.disconnect()
                while True:
                    if state_machine.connecting() == True:
                        break
                state_machine.connect()


class DeviceDriveService(Service):
    DEVICEDRIVE_UUID = "166d8288-25e7-113a-978f-2e728ce88125"
    
    def __init__(self, bus, index, pt):
        Service.__init__(self, bus, index, self.DEVICEDRIVE_UUID, True)
        self.water_supply_characteristic_observer = WaterSupplyCharacteristic(
                                                    bus, 0, self)
        self.vegetable_profile = VegetableProfileCharacteristic(bus, 1, self, pt)
        self.add_characteristic(self.water_supply_characteristic_observer)
        self.add_characteristic(self.vegetable_profile)


class WaterLevelDisplayObserver(Observer):
    def __init__(self, pt):
        Observer.__init__(self)
        self.water_tank_remaining = 0
        self.monitor = pt.getMonitor()

    def update(self, model):
        self.water_tank_remaining = model.last_water_tank_remaining
        self.notify_water_level_display()

    def notify_water_level_display(self):
        self.monitor.displayWaterLevel(self.water_tank_remaining)
        print("Water tank Remaining: {0}".format(self.water_tank_remaining))


class WaterSupplyObservable(Observable):
    def __init__(self, pt):
        self.pt = pt
        Observable.__init__(self)
        alarm_ble = pt.getAlarmBle()
        alarm_clock = pt.getAlarmClock()
        self.motor = pt.makeWaterPump()
        self.motor.stop()
        self.pump_controller = pt.makeWaterPumpTimeController()
        self.water_level = pt.makeWaterLevel()
        self.soil = 0
        self.drive_state = 0
        self.water_tank_remaining = 0
        self.last_drive_state = 0
        self.last_water_tank_remaining = 0
        self.motor_speed = 0
        self.last_motor_speed = 0
        self._water_supply_id = alarm_clock.add(500, self.check)
        self.listener = BleListener(self)
        alarm_ble.add_soil(self.listener)

    def setChanged(self):
        self.last_drive_state = self.drive_state
        self.last_water_tank_remaining = self.water_tank_remaining
        self.last_motor_speed = self.motor_speed

    def SupplyOrder(self):
        if self.drive_state != 2:
            print("Please Water Tank Charge")
            print("Water Supply Stop")
            self.motor_speed = 0
            self.motor.stop()
            self.pump_controller.reset()
            self.drive_state = 2
            self.setChanged()
            self.notifyObservers()

    def AutomaticWaterSupplyOrder(self):
        vegetable_profile = self.pt.getVegetableProfile()
        if vegetable_profile.is_update() is True:
            profile = vegetable_profile.get_profile()
            motor_speed = self.pump_controller.feedback(
                    profile, self.soil)
            if motor_speed < 0:
                motor_speed = 0
            elif motor_speed > 100:
                motor_speed = 100
            self.motor_speed = motor_speed
            self.motor.forward(motor_speed)

            if motor_speed != 0 and self.drive_state != 1:
                print("Water Supply Run")
                self.drive_state = 1
                self.setChanged()
                self.notifyObservers()
            elif motor_speed == 0 and self.drive_state != 0:
                print("Water Supply Stop")
                self.motor.stop()
                self.pump_controller.reset()
                self.drive_state = 0
                self.setChanged()
                self.notifyObservers()

            if self.last_water_tank_remaining != self.water_tank_remaining or \
               self.last_motor_speed != self.motor_speed:
                print("Motor Speed: {0}".format(self.motor_speed))
                self.setChanged()
                self.notifyObservers()

    def check(self):
        self.soil = self.listener.read()
        self.water_tank_remaining = self.water_level.read()
        self.pump_controller.run()
        if self.water_tank_remaining == 0:
            self.SupplyOrder()
        else:
            self.AutomaticWaterSupplyOrder()
        return True


class WaterSupplyCharacteristic(Observer, Characteristic):
    WATERSUPPLY_UUID = "166d85ee-25e7-11ea-978f-2e728ce88125"

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.WATERSUPPLY_UUID,
            ['notify'],
            service)
        Observer.__init__(self)
        self.notifying = False
        self.drive_state_name = ["Stop", "Run", "Water_Add"]
        self.water_tank_remaining = 0
        self.motor_speed = 0
        self.drive_state = 0
    
    def update(self, model):
        self.drive_state = model.last_drive_state
        self.water_tank_remaining = model.last_water_tank_remaining
        self.motor_speed = model.last_motor_speed
        self.notify_watersupply()

    def notify_watersupply(self):
        if not self.notifying:
            return
        print("Water Tank Remaining: " + repr(self.water_tank_remaining))
        motor_speed = int(self.motor_speed * 100)
        high_motor_speed = (motor_speed >> 8) & 0xff
        low_motor_speed = (motor_speed & 0xff)
        self.PropertiesChanged(
                GATT_CHRC_IFACE,
                {'Value': [dbus.Byte(self.drive_state),
                           dbus.Byte(self.water_tank_remaining),
                           dbus.Byte(high_motor_speed),
                           dbus.Byte(low_motor_speed)]}, [])

    def ReadValue(self, options):
        motor_speed = int(self.motor_speed * 100)
        high_motor_speed = (motor_speed >> 8) & 0xff
        low_motor_speed = (motor_speed & 0xff)
        return [dbus.Byte(self.drive_state),
                dbus.Byte(self.water_tank_remaining),
                dbus.Byte(high_motor_speed),
                dbus.Byte(low_motor_speed)]

    def StartNotify(self):
        if self.notifying:
            print("Already notifying, nothing to do")
            return
        self.notifying = True
        self.notify_watersupply()

    def StopNotify(self):
        if not self.notifying:
            print("Not notifying, nothing to do")
            return
        self.notifying = False

        
class VegetableProfileCharacteristic(Characteristic):
    VEGETABLEPROFILE_UUID = "166d8760-25e7-11ea-978f-2e728ce88125"

    def __init__(self, bus, index, service, pt):
        Characteristic.__init__(
            self, bus, index,
            self.VEGETABLEPROFILE_UUID,
            ['write'],
            service)
        self.pt = pt
        self.values = None

    def WriteValue(self, value, options):
        vegetable_profile = self.pt.getVegetableProfile()
        print("Vegetable Profile WriteValue Called")

        if len(value) != 24:
            raise InvalidValueLengthException()

        values = []
        for i in range(0, 24, 2):
            values.append((value[i] << 8)|value[i+1])

        vegetable_profile.update(values)
        profile = vegetable_profile.get_profile()
        print("Vegetable Profile: " + repr(profile))


class SoilCharacteristicObserver(Observer):
    def __init__(self, pt):
        super().__init__()
        self.soil = 0
        self.monitor = pt.getMonitor()

    def update(self, model):
        self.soil = model.last_soil
        self.monitor.displaySoilGraph(self.soil)
        self.print_soil()

    def print_soil(self):
        print('\tSoil Value: ' + str(self.soil))


class TemperatureAndHumidityCharacteristicObserver(Observer):
    def __init__(self, pt):
        super().__init__()
        self.temperature = 0
        self.humidity = 0
        self.monitor = pt.getMonitor()

    def update(self, model):
        self.temperature = model.last_temperature
        self.humidity = model.last_humidity
        self.monitor.displayTemperatureAndHumidityGraph(self.temperature, self.humidity)
        self.print_temperature()

    def print_temperature(self):
        print('\tTemperature Value:' + str(self.temperature))
        print('\tHumidity Value:' + str(self.humidity))


class SoilCharacteristicObservable(Observable):
    def __init__(self, pt):
        super().__init__()
        alarm_ble = pt.getAlarmBle()
        self.soil = 0
        self.last_soil = 0
        self.listener = BleListener(self)
        alarm_ble.add_soil(self.listener)

    def setChanged(self):
        self.last_soil = self.soil

    def check(self):
        self.soil = self.listener.read()
        if self.soil != self.last_soil:
            self.setChanged()
            self.notifyObservers()


class TemperatureAndHumidityCharacteristicObservable(Observable):
    def __init__(self, pt):
        super().__init__()
        alarm_ble = pt.getAlarmBle()
        self.temperature = 0
        self.last_temperature = 0
        self.humidity = 0
        self.last_humidity = 0
        self.listener = BleListener(self)
        alarm_ble.add_temp_and_humidity(self.listener)

    def setChanged(self):
        self.last_temperature = self.temperature
        self.last_humidity = self.humidity

    def check(self):
        value = self.listener.read()
        self.temperature = value["temperature"]
        self.humidity = value["humidity"]
        if self.temperature != self.last_temperature or self.humidity != self.last_humidity:
            self.setChanged()
            self.notifyObservers()


class EnvironmentServiceClient(ServiceClient):
    def __init__(self, bus, UUID, pt):
        super().__init__(bus, UUID)
        self.pt = pt
        self.alarm_ble = pt.getAlarmBle()
        self.environment_temperature_chrc = None
        self.environment_soil_chrc = None
        self.temperature_signal = None
        self.soil_signal = None
        self.soil = 0

    def process_chrc(self, chrc_path):
        chrc = self.bus.get_object(BLUEZ_SERVICE_NAME, chrc_path)
        chrc_props = chrc.GetAll(GATT_CHRC_IFACE,
                                 dbus_interface=DBUS_PROP_IFACE)

        uuid = chrc_props['UUID']

        if uuid == TEMPERATURE_UUID:
            self.environment_temperature_chrc = (chrc, chrc_props)
        elif uuid == SOIL_UUID:
            self.environment_soil_chrc = (chrc, chrc_props)
        else:
            print('Unrecognized characteristic: ' + uuid)

        return True

    def soil_changed_cb(self, iface, changed_props, invalidated_props): 
        if iface != GATT_CHRC_IFACE:
            return

        if not len(changed_props):
            return

        value = changed_props.get('Value', None)
        if not value:
            return 

        soil_value = float(((value[0] << 8) | value[1]) / 10 )
        self.alarm_ble.wakeup_soil(soil_value)

    def soil_read(self):
        if self.environment_soil_chrc is None:
            return 
        self.environment_soil_chrc[0].ReadValue({}, reply_handler=self.soil_read_cb,
                                                  error_handler=self.generic_error_cb,
                                                  dbus_interface=GATT_CHRC_IFACE)
        return self.soil

    def soil_read_cb(self, value):
        if len(value) != 2:
            print('Invalid environment sensor location value: ' + repr(value))
            return

        self.soil = float(((value[0] << 8) | value[1])/10)

    def temperature_changed_cb(self, iface, changed_props, invalidated_props): 
        if iface != GATT_CHRC_IFACE:
            return

        if not len(changed_props):
            return

        value = changed_props.get('Value', None)
        if not value:
            return 

        temperature = float(((value[0] << 8) | value[1]) / 10)
        humidity = float(((value[2] << 8) | value[3]) / 10)
        values = {"temperature": temperature, "humidity": humidity}
        self.alarm_ble.wakeup_temp_and_humidity(values)

    def start_client(self):
        self.environment_temperature_iface = dbus.Interface(self.environment_temperature_chrc[0], DBUS_PROP_IFACE)
        self.temperature_signal = self.environment_temperature_iface.connect_to_signal("PropertiesChanged", self.temperature_changed_cb)

        self.environment_temperature_chrc[0].StartNotify(reply_handler=self.temperature_start_notify_cb,
                                                    error_handler=self.generic_error_cb,
                                                    dbus_interface=GATT_CHRC_IFACE)

        self.environment_soil_iface = dbus.Interface(self.environment_soil_chrc[0], DBUS_PROP_IFACE)
        self.soil_signal = self.environment_soil_iface.connect_to_signal("PropertiesChanged", self.soil_changed_cb)

        self.environment_soil_chrc[0].StartNotify(reply_handler=self.soil_start_notify_cb,
                                             error_handler=self.generic_error_cb,
                                             dbus_interface=GATT_CHRC_IFACE)

    def temperature_start_notify_cb(self):
        print("Temperature notifications enabled")

    def soil_start_notify_cb(self):
        print("Soil notifications enabled")

    def temperature_sensor_val_cb(self, value):
        print("Temperature Value: {0}".format(value))
        if len(value) != 4:
            print('Invalid environment sensor location value: ' + repr(value))
            return

        print("Temperature value: " + str(float(((value[0] << 8) | value[1])/10)))
        print("Humidity value: " + str(float(((value[2] << 8) | value[3])/10)))


class DeviceDriveController:
    def __init__(self, pt):
        pt.getAlarmClock()
        database = pt.makeDatabase()
        database.createDatabase()
        self.pt = pt
        self.bus = dbus.SystemBus()
        self.service_manager = None
        self.remote_device = None
        self.adapter = self.find_adapter(self.bus)
        self.advertising_observable = None
        self.advertising_observer = None

        # Observable Pattern Create
        self.advertising_observable = AdvertisingSwitchStateObservable(self.pt)
        self.temp_observable = TemperatureAndHumidityCharacteristicObservable(self.pt)
        self.soil_observable = SoilCharacteristicObservable(self.pt)
        self.water_supply_observable = WaterSupplyObservable(self.pt)

        # Observer Pattern Create and add Observer
        self.set_observer()
        print("Observable Set")
        motor = self.pt.makeWaterPump()
        motor.stop()

    def set_observer(self):
        self.water_level_display_observer = WaterLevelDisplayObserver(self.pt)
        self.water_supply_observable.addObserver(self.water_level_display_observer)
        self.temp_characteristic_observer = \
            TemperatureAndHumidityCharacteristicObserver(self.pt)
        self.temp_observable.addObserver(self.temp_characteristic_observer)
        self.soil_characteristic_observer = SoilCharacteristicObserver(self.pt)
        self.soil_observable.addObserver(self.soil_characteristic_observer)

    def find_adapter(self, bus):
        remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                                   DBUS_OM_IFACE)
        objects = remote_om.GetManagedObjects()

        for o, props in objects.items():
            if GATT_MANAGER_IFACE in props.keys():
                return o
        return None

    def adapter_powered_on(self):
        print("Powered_On")
        adapter_props = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE_NAME,
                                                           self.adapter),
                                       "org.freedesktop.DBus.Properties")
        adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

    def adapter_powered_off(self):
        print("Powered_Off")
        adapter_props = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE_NAME,
                                                           self.adapter),
                                       "org.freedesktop.DBus.Properties")
        adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(0))

    def register_app_cb(self):
        print("GATT application registered")

    def register_app_error_cb(self, error):
        alarm_clock = self.pt.getAlarmClock()
        print("Failed to register application: " + str(error))
        alarm_clock.stop()

    def run(self):
        adapter = self.find_adapter(self.bus)
        self.adapter = adapter
        self.adapter_powered_on()
        self.server = GattServer(self.bus, self.pt)
        self.water_supply_observable.addObserver(
            self.server.device_drive_service.water_supply_characteristic_observer)
        self.client = GattClient(self.bus, self.pt)

        self.advertising_observer = AdvertisingObserver(self.bus)
        self.advertising_observable.addObserver(self.advertising_observer)

        if not adapter:
            print('GattManager1 interface not found')
            return
        self.service_manager = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                GATT_MANAGER_IFACE)

        self.service_manager.RegisterApplication(self.server.get_path(), {},
                                            reply_handler=self.register_app_cb,
                                            error_handler=self.register_app_error_cb)
        alarm_clock = self.pt.getAlarmClock()
        alarm_clock.run()

    def remove_observer(self):
        self.advertising_observable.removeObserver(self.advertising_observer)
        self.water_supply_observable.removeObserver(
            self.server.device_drive_service.water_supply_characteristic_observer)

    def stop(self):
        self.remove_observer()
        if self.remote_device is not None:
            self.remote_device.Disconnect()
        alarm_clock = self.pt.getAlarmClock()
        alarm_clock.stop()
        self.bus.close()

    def request(self):
        self.bus = dbus.SystemBus()
        if self.device_connect(self.bus, SENSOR_DEVICE) == True:
            time.sleep(2)
            return True
        return False

    def device_connect(self, bus, device_id):
        device_search_flag = False
        object_path = "/org/bluez/hci0"
        remote_it = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, object_path),
                                   DBUS_IT_IFACE)
        xml = ET.fromstring(str(remote_it.Introspect()))
        for i in xml:
            if i.tag == "node":
                if i.attrib["name"] == device_id:
                    print(i.attrib["name"])
                    object_path += "/" + device_id
        print(object_path)
        self.remote_device = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME,
                                            object_path), BLUEZ_DEVICE_IFACE)
        try:
            print("Connect...")
            self.remote_device.Connect()
            print("Connect Success")
            return True
        except Exception as e:
            print("Not Connect: {0}".format(e))
            self.remote_device.Disconnect()
            return False


class DriveDevice:
    def __init__(self, drive_device_controller, pt):
        self.pt = pt
        self.communicationState = CommunicationDriveDeviceState()
        self.waitState = WaitDriveDeviceState()
        self.state = self.waitState
        self.controller = drive_device_controller

    def set_wait(self):
        self.state = self.waitState

    def set_communication(self):
        self.state = self.communicationState

    def isCommunicationState(self):
        return self.state == self.communicationState

    def isWaitState(self):
        return self.state == self.WaitState

    def connect(self):
        monitor = self.pt.getMonitor()
        monitor.displayConnectDevice(1)
        print("StateMachine: Connect")
        self.state.connect(self)

    def disconnect(self):
        monitor = self.pt.getMonitor()
        monitor.displayConnectDevice(0)
        print("StateMachine: Disconnect")
        self.state.disconnect(self)

    def connecting(self):
        print("StateMachine: Connecting")
        return self.state.connecting(self)

    def run(self):
        print("StateMachineAction: Run")
        self.controller.run()

    def stop(self):
        print("StateMachineAction: Stop")
        self.controller.stop()

    def request(self):
        print("StateMachineAction: Request")
        return self.controller.request()


class DriveDeviceState:
    def __init__(self):
        pass

    def connect(self, device_drive):
        pass

    def disconnect(self, device_drive):
        device_drive.set_wait()
        device_drive.stop()

    def connecting(self, device_drive):
        pass


class CommunicationDriveDeviceState(DriveDeviceState):
    def __init__(self):
        super().__init__()

    def connect(self, device_drive):
        pass

    def disconnect(self, device_drive):
        device_drive.set_wait()
        device_drive.stop()

    def connecting(self, device_drive):
        return True


class WaitDriveDeviceState(DriveDeviceState):
    def __init__(self):
        super().__init__()

    def connect(self, device_drive):
        device_drive.set_communication()
        device_drive.run()

    def disconnect(self, device_drive):
        pass

    def connecting(self, device_drive):
        device_drive.set_wait()
        if device_drive.request() == True:
            return True
        else:
            return False


class AdvertisingSwitchStateObservable(Observable):
    def __init__(self, pt):
        super().__init__()
        self.pt = pt
        self.alarm_clock = self.pt.getAlarmClock()
        self.switch = pt.makeAdvertisingSwitch()
        self._switch_check_id = self.alarm_clock.add(1000, self.check)
        self._switch_chattering_id = self.alarm_clock.add(80, self.switch.sampling)
        self.switch_state = 0
        self.last_switch_state = 0

    def remove(self):
        self.alarm_clock.remove(self._switch_check_id)
        self.alarm_clock.remove(self._switch_chattering_id)

    def setChanged(self):
        self.last_switch_state = self.switch_state

    def check(self):
        self.switch_state = self.switch.read()
        if self.last_switch_state != self.switch_state:
            self.setChanged()
            self.notifyObservers()
        return True


class AdvertisingObserver(Observer):
    def __init__(self, bus):
        super().__init__()
        self.switch_state = 0
        self.bus = bus
        self.adapter = self.find_adapter(bus)
        if self.adapter is None:
            return
        self.adapter_powered_on()
        self.ad_manager = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter),
                                    LE_ADVERTISING_MANAGER_IFACE)
        self.advertisement = DriveDeviceAdvertisement(bus, 1)

    def update(self, model):
        self.switch_state = model.last_switch_state
        self.notify_advertising()

    def notify_advertising(self):
        if self.switch_state == 1:
            print("Advertisement: {0}".format(self))
            self.ad_manager.RegisterAdvertisement(self.advertisement.get_path(), {},
                                                  reply_handler=self.register_ad_cb,
                                                  error_handler=self.register_ad_error_cb)
            print("RegisterAdvertisement")
        else:
            try:
                self.ad_manager.UnregisterAdvertisement(self.advertisement)
            except Exception as e:
                print("Advertisement not start")
            print("UnRegisterAdvertisement")

    def adapter_powered_on(self):
        adapter_props = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE_NAME,
                                                           self.adapter),
                                       "org.freedesktop.DBus.Properties")
        adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

    def adapter_powered_off(self):
        adapter_props = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE_NAME,
                                                           self.adapter),
                                       "org.freedesktop.DBus.Properties")
        adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(0))

    def register_ad_cb(self):
        print('Advertisement registered')

    def register_ad_error_cb(self, error):
        print('Failed to register advertisement: ' + str(error))
        alarm_clock = self.pt.getAlarmClock()
        alarm_clock.stop()

    def find_adapter(self, bus):
        remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                                   DBUS_OM_IFACE)
        objects = remote_om.GetManagedObjects()

        for o, props in objects.items():
            if LE_ADVERTISING_MANAGER_IFACE in props:
                return o

        print("LEAdvertisingManager1 interface not found")
        return None


class DriveDeviceGattMain:
    def __init__(self):
        global state_machine
        self.pt = PlanterToolkit()
        self.device_controller = DeviceDriveController(self.pt)
        print("Tool ok")
        state_machine = DriveDevice(self.device_controller, self.pt)

    def __enter__(self):
        print("DriveDeviceGatt Start")
        return self

    def main(self):
        while True:
            if state_machine.connecting():
                break
        print("Connect OK")
        state_machine.connect()

    def __exit__(self, exc_type, exc_value, traceback):
        print("ExcType: {0}".format(exc_type))
        print("ExcValue: {0}".format(exc_value))
        print("Traceback: {0}".format(traceback))
        state_machine.disconnect()
        GpioDriver().close()
        print("DriveDeviceGatt End")


if __name__ == '__main__':
    with DriveDeviceGattMain() as main:
        main.main()
