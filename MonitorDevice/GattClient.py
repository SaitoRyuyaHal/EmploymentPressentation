#!/usr/bin/env python3
#-*- coding:utf-8-*-

import dbus
import sys
import qdarkstyle
import datetime
import time
import xml.etree.ElementTree as ET
import ApplicationWindow
import DayDisplayDialog
import DebugDialog

from dbus.mainloop.glib import DBusGMainLoop
from ObserverPattern import Observer, Observable
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtCore import *
from BleApi import *
from AlarmBle import BleListener
from MonitorPlanterToolkit import PlanterToolkit

SENSOR_DEVICE = "dev_B8_27_EB_97_96_9F"
DRIVE_DEVICE =  "dev_B8_27_EB_E4_94_AA"


class GattClient():
    def __init__(self, bus, pt, form):
        self.bus = bus
        self.pt = pt
        self.form = form
        self.server_services = [] 
        self.database_helper = self.pt.getDataBase()
        self.database_helper.createDatabase()
        self.environment_service_client = EnvironmentServiceClient(
                bus, ENVIRONMENT_UUID, self.pt)
        self.vegetable_info_service_client = VegetableInfoServiceClient(
                bus, VEGETABLEINFO_UUID, self.pt)
        self.device_drive_service_client = DeviceDriveServiceClient(
                bus, DEVICEDRIVE_UUID, self.pt)
        self.add_service(self.environment_service_client)
        self.add_service(self.vegetable_info_service_client)
        self.add_service(self.device_drive_service_client)
        self.chrcs = []
        self.om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'), DBUS_OM_IFACE)
        self.om.connect_to_signal('InterfacesRemoved', self.interfaces_removed_cb)
        self.om.connect_to_signal('InterfacesAdded', self.interfaces_added_cb)
        self.objects = self.om.GetManagedObjects()
        self.list_characteristics_found()
        self.list_service_found()
        self.vegetable_info_setup()
        self.start_client()

    def vegetable_info_setup(self):
        vegetable_profile = self.pt.getVegetableProfile()
        vegetable_info = self.pt.getVegetableInfo()
        self.vegetable_info_service_client.write_vegetable_info(vegetable_info)
        self.device_drive_service_client.write_vegetable_profile(vegetable_profile)

    def add_service(self, service):
        self.server_services.append(service)

    def list_characteristics_found(self):
        # List characteristics found
        for path, interfaces in self.objects.items():
            if GATT_CHRC_IFACE not in interfaces.keys():
                continue
            self.chrcs.append(path)

    def list_service_found(self):
        # List sevices found
        for path, interfaces in self.objects.items():
            if GATT_SERVICE_IFACE not in interfaces.keys():
                continue

            chrc_paths = [d for d in self.chrcs if d.startswith(path + "/")]

            for service in self.server_services:
                if service.process_service(path, chrc_paths):
                    break

        for service in self.server_services:
            if not service.isService():
                print("List Service Not Found")
                state_machine.disconnect()

    def start_client(self):
        for service in self.server_services:
            service.start_client()

    def state_machine_stop_process(self):
        state_machine.disconnect()
        while True:
            if state_machine.connecting():
                break
        state_machine.connect()
        
    def interfaces_added_cb(self, object_path, interfaces):
        if not self.server_services:
            return


    def interfaces_removed_cb(self, object_path, interfaces):
        if not self.server_services:
            return
        connect_states = self.pt.getConnectStates()
        text_creator = self.pt.createTextCreator()
        now = datetime.datetime.now()

        for service in self.server_services:
            if object_path == service.service[2]:
                print(service.__class__.__name__)
                if service.__class__.__name__ == "EnvironmentServiceClient":
                    text = text_creator.connect_state_text("sensor", False, now)
                    self.form.ui.textBrowser_state.append(text)
                    connect_states.set_connect_states("sensor", False)
                if service.__class__.__name__ == " VegetableInfoServiceClient":
                    text = text_creator.connect_state_text("fertilizer", False, now)
                    self.form.ui.textBrowser_state.append(text)
                    connect_states.set_connect_states("fertilizer", False)
                if service.__class__.__name__ == "DeviceDriveServiceClient":
                    text = text_creator.connect_state_text("water_pump", False, now)
                    self.form.ui.textBrowser_state.append(text)
                    connect_states.set_connect_states("water_pump", False)
                print("Service was removed")
                state_machine.disconnect()


class ServiceClient():
    def __init__(self, bus, UUID, pt):
        self.service = None
        self.bus = bus
        self.uuid = UUID
        self.pt = pt

    def process_service(self, service_path, chrc_paths):
        service = self.bus.get_object(BLUEZ_SERVICE_NAME, service_path)
        service_props = service.GetAll(GATT_SERVICE_IFACE,
                                       dbus_interface=DBUS_PROP_IFACE)

        uuid = service_props['UUID']

        if uuid != self.uuid:
            return False


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

    def state_machine_stop_process(self):
        while True:
            if state_machine.connecting():
                break
        state_machine.connect()

    def generic_error_cb(self, error):
        print("D-Bus call failed: " + str(error))
        self.state_machine_stop_process()


class TemperatureAndHumidityDatabaseWriteObserver(Observer):
    def __init__(self, pt):
        super().__init__()
        self.pt = pt
        self.temperature = 0
        self.humidity = 0
        self.time = 0
        self.data_base = self.pt.getDataBase()

    def update(self, model):
        self.temperature = model.last_temperature
        self.humidity = model.last_humidity
        self.time = datetime.datetime.now()
        self.data_base_write_update()

    def data_base_write_update(self):
        self.data_base.writeTemperatureAndHumidity(
                self.temperature, self.humidity, self.time)


class IntegralTemperatureDatabaseWriteObserver(Observer):
    def __init__(self, pt):
        super().__init__()
        self.pt = pt
        self.integral_temp = 0
        self.time = 0
        self.data_base = self.pt.getDataBase()

    def update(self, model):
        self.integral_temp = model.last_integral_temp
        self.time = model.last_time
        self.integral_temperature_update()

    def integral_temperature_update(self):
        self.data_base.writeIntegralTemperature(self.integral_temp, self.time)
        self.data_base.update()


class IntegralTemperatureObservable(Observable):
    def __init__(self, pt):
        super().__init__()
        self.pt = pt
        alarm_clock = pt.getAlarmClock()
        self.integral_temp = 0
        self.last_integral_temp = 0
        self.temps = None
        self.time = 0
        self.last_time = 0
        self.average_temp = 5
        alarm_clock.add(86400000, self.check)
        self.data_base = self.pt.getDataBase()

    def setChanged(self):
        integral_temps = self.data_base.readIntegralTemperatureIndex(-1)
        if integral_temps is not None:
            last_integral = float(integral_temps["TEMPERATURE"])
            self.last_integral_temp = self.integral_temp + last_integral
        else:
            self.last_integral_temp = self.integral_temp
        self.last_time = self.time

    def check(self):
        end_time = datetime.datetime.now()
        self.time = end_time
        start_time = end_time - datetime.timedelta(days=1)
        self.temps = self.data_base.readTemperatureAndHumidity()
        l = [i['TEMPERATURE'] for i in self.temps if start_time <= datetime.datetime.strptime(i['TIME'], '%Y-%m-%d %H:%M:%S.%f') < end_time]

        sum_temp = 0
        for i in l:
            sum_temp += float(i)
        self.integral_temp = sum_temp / len(l)
        if self.integral_temp > self.average_temp:
            self.setChanged()
            self.notifyObservers()
        return True


class SoilDatabaseWriteObserver(Observer):
    def __init__(self, pt):
        super().__init__()
        self.pt = pt
        self.soil = 0
        self.time = 0
        self.data_base = self.pt.getDataBase()

    def update(self, model):
        self.soil = model.soil
        self.time = datetime.datetime.now()
        self.integral_temperature_update()

    def integral_temperature_update(self):
        self.data_base.writeSoil(self.soil, self.time)


class SoilCharacteristicObservable(Observable):
    def __init__(self, pt):
        super().__init__()
        self.pt = pt
        self.soil = 0
        self.last_soil = 0
        self.count = 0
        alarm_ble = self.pt.getAlarmBle()
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
        self.pt = pt
        self.temperature = 0
        self.last_temperature = 0
        self.humidity = 0
        self.last_humidity = 0
        alarm_ble = self.pt.getAlarmBle()
        self.listener = BleListener(self)
        alarm_ble.add_temp_and_humidity(self.listener)

    def setChanged(self):
        self.last_temperature = self.temperature
        self.last_humidity = self.humidity

    def check(self):
        value = self.listener.read()
        self.temperature = value["temperature"]
        self.humidity = value["humidity"]
        if self.temperature != self.last_temperature or \
           self.humidity != self.last_humidity:
            self.setChanged()
            self.notifyObservers()


class EnvironmentServiceClient(ServiceClient):
    def __init__(self, bus, UUID, pt):
        super().__init__(bus, UUID, pt)
        self.environment_temperature_chrc = None
        self.environment_soil_chrc = None
        self.alarm_ble = self.pt.getAlarmBle()

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
        self.environment_temperature_chrc[0].ReadValue(
            {}, reply_handler=self.temperature_sensor_val_cb,
            error_handler=self.generic_error_cb, dbus_interface=GATT_CHRC_IFACE)
        self.environment_temperature_iface = dbus.Interface(
            self.environment_temperature_chrc[0], DBUS_PROP_IFACE)
        self.environment_temperature_iface.connect_to_signal(
            "PropertiesChanged", self.temperature_changed_cb)
        self.environment_temperature_chrc[0].StartNotify(
            reply_handler=self.temperature_start_notify_cb,
            error_handler=self.generic_error_cb, dbus_interface=GATT_CHRC_IFACE)
        self.environment_soil_iface = dbus.Interface(
            self.environment_soil_chrc[0], DBUS_PROP_IFACE)
        self.environment_soil_iface.connect_to_signal(
            "PropertiesChanged", self.soil_changed_cb)
        self.environment_soil_chrc[0].StartNotify(
            reply_handler=self.soil_start_notify_cb, 
            error_handler=self.generic_error_cb, dbus_interface=GATT_CHRC_IFACE)

    def temperature_start_notify_cb(self):
        print("Temperature notifications enabled")

    def soil_start_notify_cb(self):
        print("Soil notifications enabled")

    def temperature_sensor_val_cb(self, value):
        if len(value) != 4:
            print('Invalid environment sensor location value: ' + repr(value))
            return

        print("Temperature value: " + str(float(((value[0] << 8) | value[1])/10)))
        print("Humidity value: " + str(float(((value[2] << 8) | value[3])/10)))


class VegetableInfoServiceClient(ServiceClient):
    def __init__(self, bus, UUID, pt):
        super().__init__(bus, UUID, pt)
        self.pt = pt
        self.vegetable_register_chrc = None
        self.vegetable_info = 0

    def process_chrc(self, chrc_path):
        chrc = self.bus.get_object(BLUEZ_SERVICE_NAME, chrc_path)
        chrc_props = chrc.GetAll(GATT_CHRC_IFACE,
                                 dbus_interface=DBUS_PROP_IFACE)

        uuid = chrc_props['UUID']

        if uuid == VEGETABLEREGISTER_UUID:
            self.vegetable_register_chrc = (chrc, chrc_props)
        else:
            print('Unrecognized characteristic: ' + uuid)

        return True

    def start_client(self):
        self.vegetable_register_chrc[0].ReadValue(
            {}, reply_handler=self.vegetable_info_val_cb,
            error_handler=self.generic_error_cb, dbus_interface=GATT_CHRC_IFACE)

    def vegetable_info_write_cb(self):
        print("Vegetable Info write")

    def vegetable_info_val_cb(self, value):
        if len(value) != 2:
            print('Invalid vegetable location value: ' + repr(value))
            return
        self.vegetable_info = int((value[0] << 8) | value[1])
        print("Vegetable Info value: " + str(self.vegetable_info))

    def write_vegetable_info(self, info):
        high_value = (info >> 8) & 0xff
        low_value =  (info & 0xff)
        self.vegetable_register_chrc[0].WriteValue(
            [high_value, low_value], {}, reply_handler=self.vegetable_info_write_cb, 
            error_handler=self.generic_error_cb, dbus_interface=GATT_CHRC_IFACE)

    def read_vegetable_info(self):
        self.vegetable_register_chrc[0].ReadValue(
            {}, reply_handler=self.vegetable_info_val_cb,
            error_handler=self.generic_error_cb, dbus_interface=GATT_CHRC_IFACE)
        return self.vegetable_info


class WaterSupplyQtObserver(Observer):
    def __init__(self):
        super().__init__()
        self.water_tank_remaining = 0
        self.ui = None

    def set_ui(self, ui):
        self.ui = ui

    def update(self, model):
        self.water_tank_remaining = model.last_water_tank_remaining
        self.notify_qt_progressbar()

    def notify_qt_progressbar(self):
        tank_remaining_percent = 0
        if self.water_tank_remaining == 0:
            tank_remaining_percent = 0
        elif self.water_tank_remaining == 1:
            tank_remaining_percent = 25
        elif self.water_tank_remaining == 2:
            tank_remaining_percent = 50
        else:
            tank_remaining_percent = 80
        self.ui.progressBar_tank_capacity.setValue(tank_remaining_percent)
        

class WaterSupplyObservable(Observable):
    def __init__(self, pt):
        super().__init__()
        self.pt = pt
        self.water_tank_remaining = 0
        self.last_water_tank_remaining = 0
        alarm_ble = self.pt.getAlarmBle()
        self.listener = BleListener(self)
        alarm_ble.add_water_supply(self.listener)

    def setChanged(self):
        self.last_water_tank_remaining = self.water_tank_remaining

    def check(self):
        self.water_tank_remaining = self.listener.read()
        if self.water_tank_remaining != self.last_water_tank_remaining:
            self.setChanged()
            self.notifyObservers()


class TemperatureHighLowQtObserver(Observer):
    def __init__(self, pt):
        self.pt = pt
        vegetable_profile = self.pt.getVegetableProfile()
        super().__init__()
        self.temp = 0
        self.ui = None
        self.high_temp = float(vegetable_profile["HIGHSUITABLETEMPERATURE"])
        self.low_temp = float(vegetable_profile["LOWSUITABLETEMPERATURE"])
        self.high_low_flag = -1
        self.data_base = self.pt.getDataBase()
        self.text_creator = self.pt.createTextCreator()

    def set_ui(self, ui):
        self.ui = ui

    def update(self, model):
        self.temp = model.last_temperature
        self.temp_high_low_browser()

    def temp_high_low_browser(self):
        if self.temp > self.high_temp and self.high_low_flag != 0:
            self.high_low_flag = 0
        elif self.temp < self.low_temp and self.high_low_flag != 1:
            self.high_low_flag = 1
        elif self.low_temp < self.temp < self.high_temp and self.high_low_flag != 2:
            self.high_low_flag = 2
        else:
            return
        now = datetime.datetime.now()
        text = self.text_creator.temp_high_low_warning(
            self.temp, now, self.high_low_flag)
        self.data_base.writeLog(text[1], now)
        text = "{0}<br>&nbsp;&nbsp;&nbsp;&nbsp;{1}<br>".format(text[0], text[1])
        if self.high_low_flag == 0:
            text = "<span style=\" color: #ff8c00;\">{0}</span>".format(text)
        elif self.high_low_flag == 1:
            text = "<span style=\" color: #6495ed;\">{0}</span>".format(text)
        else:
            text = "<span style=\" color: #00ff7f;\">{0:^10}</span>".format(text)
        self.ui.textBrowser_state.append(text)


class HumidityHighLowQtObserver(Observer):
    def __init__(self, pt):
        super().__init__()
        self.pt = pt
        self.humidity = 0
        self.ui = None
        vegetable_profile = self.pt.getVegetableProfile()
        self.high_humidity = float(vegetable_profile["HIGHHUMIDITY"])
        self.low_humidity = float(vegetable_profile["LOWHUMIDITY"])
        self.high_low_flag = -1
        self.data_base = self.pt.getDataBase()
        self.text_creator = self.pt.createTextCreator()

    def set_ui(self, ui):
        self.ui = ui

    def update(self, model):
        self.humidity = model.last_humidity
        self.humidity_high_low_browser()

    def humidity_high_low_browser(self):
        if self.humidity > self.high_humidity and self.high_low_flag != 0:
            self.high_low_flag = 0
        elif self.humidity < self.low_humidity and self.high_low_flag != 1:
            self.high_low_flag = 1
        elif self.low_humidity < self.humidity < self.high_humidity and \
             self.high_low_flag != 2:
            self.high_low_flag = 2
        else:
            return
        now = datetime.datetime.now()
        text = self.text_creator.humidity_high_low_warning(
            self.humidity, now, self.high_low_flag)
        self.data_base.writeLog(text[1], now)
        text = "{0}<br>&nbsp;&nbsp;&nbsp;&nbsp;{1}<br>".format(text[0], text[1])
        if self.high_low_flag == 0:
            text = "<span style=\" color: #ff8c00;\">{0}</span>".format(text)
        elif self.high_low_flag == 1:
            text = "<span style=\" color: #6495ed;\">{0}</span>".format(text)
        else:
            text = "<span style=\" color: #00ff7f;\">{0}</span>".format(text)
        self.ui.textBrowser_state.append(text)


class SoilMoistureLowLevelQtObserver(Observer):
    def __init__(self, pt):
        super().__init__()
        self.pt = pt
        self.soil = None
        vegetable_profile = self.pt.getVegetableProfile()
        self.low_soil = float(vegetable_profile["AMOUNTOFWATER"])
        self.low_flag = -1
        self.ui = None
        self.data_base = self.pt.getDataBase()
        self.text_creator = self.pt.createTextCreator()

    def set_ui(self, ui):
        self.ui = ui

    def update(self, model):
        self.soil = model.last_soil
        self.notify_qt_soil_low_browser()

    def notify_qt_soil_low_browser(self):
        if self.soil < self.low_soil and self.low_flag != 0:
            self.low_flag = 0
        elif self.soil >= self.low_soil and self.low_flag != 1:
            self.low_flag = 1
        else:
            return
        now = datetime.datetime.now()
        text = self.text_creator.soil_moisture_warning(self.soil, now, self.low_flag)
        self.data_base.writeLog(text[1], now)
        text = "{0}<br>&nbsp;&nbsp;&nbsp;&nbsp;{1}<br>".format(text[0], text[1])
        if self.low_flag == 0:
            text = "<span style=\" color: #6495ed;\">{0}</span>".format(text)
        else:
            text = "<span style=\" color: #00ff7f;\">{0}</span>".format(text)
        self.ui.textBrowser_state.append(text)


class DriveStateQtObserver(Observer):
    def __init__(self, pt):
        super().__init__()
        self.drive_state = 0
        self.ui = None
        self.pt = pt
        self.data_base = self.pt.getDataBase()
        self.text_creator = self.pt.createTextCreator()

    def set_ui(self, ui):
        self.ui = ui

    def update(self, model):
        self.drive_state = model.last_drive_state
        self.notify_qt_state_browser()

    def notify_qt_state_browser(self):
        now = datetime.datetime.now()
        text = self.text_creator.water_pump_state(self.drive_state, now)
        self.data_base.writeLog(text[1], now)
        text = "{0}<br>&nbsp;&nbsp;&nbsp;&nbsp;{1}<br>".format(text[0], text[1])
        self.ui.textBrowser_state.append(text)


class DriveStateObservable(Observable):
    def __init__(self, pt):
        super().__init__()
        self.pt = pt
        self.drive_state = 0
        self.last_drive_state = 0
        alarm_ble = self.pt.getAlarmBle()
        self.listener = BleListener(self)
        alarm_ble.add_drive_state(self.listener)

    def setChanged(self):
        self.last_drive_state = self.drive_state

    def check(self):
        self.drive_state = self.listener.read()
        if self.drive_state != self.last_drive_state:
            self.setChanged()
            self.notifyObservers()


class WaterPumpStateDatabaseWriteObserver(Observer):
    def __init__(self, pt):
        super().__init__()
        self.pt = pt
        self.motor_speed = 0
        self.time = 0
        self.data_base = self.pt.getDataBase()

    def update(self, model):
        self.motor_speed = model.last_motor_speed
        self.time = datetime.datetime.now()
        self.data_base_write_update()

    def data_base_write_update(self):
        self.data_base.writeWaterPumpSpeed(self.motor_speed, self.time)


class WaterPumpStateObservable(Observable):
    def __init__(self, pt):
        super().__init__()
        self.pt = pt
        self.motor_speed = 0
        self.last_motor_speed = 0
        self.listener = BleListener(self)
        alarm_ble = self.pt.getAlarmBle()
        alarm_ble.add_water_pump_state(self.listener)

    def setChanged(self):
        self.last_motor_speed = self.motor_speed

    def check(self):
        self.motor_speed = self.listener.read()
        if self.motor_speed != self.last_motor_speed:
            self.setChanged()
            self.notifyObservers()


class DeviceDriveServiceClient(ServiceClient):
    def __init__(self, bus, UUID, pt):
        super().__init__(bus, UUID, pt)
        self.water_supply_chrc = None
        self.vegetable_profile_chrc = None
        self.alarm_ble = self.pt.getAlarmBle()

    def process_chrc(self, chrc_path):
        chrc = self.bus.get_object(BLUEZ_SERVICE_NAME, chrc_path)
        chrc_props = chrc.GetAll(GATT_CHRC_IFACE,
                                 dbus_interface=DBUS_PROP_IFACE)

        uuid = chrc_props['UUID']

        if uuid == WATERSUPPLY_UUID:
            self.water_supply_chrc = (chrc, chrc_props)
        elif uuid == VEGETABLEPROFILE_UUID:
            self.vegetable_profile_chrc = (chrc, chrc_props)
        else:
            print('Unrecognized characteristic: ' + uuid)

        return True

    def vegetable_profile_write_cb(self):
        print("Vegetable Profile write")

    def write_vegetable_profile(self, profile):
        values = []
        name_flag = False
        for value in profile.values():
            if name_flag is False:
                name_flag = True
                continue
            values.append(dbus.Byte((int(value) >> 8) & 0xff))
            values.append(dbus.Byte(int(value) & 0xff))
        self.vegetable_profile_chrc[0].WriteValue(
            values, {}, reply_handler=self.vegetable_profile_write_cb,
            error_handler=self.generic_error_cb, dbus_interface=GATT_CHRC_IFACE)

    def water_supply_changed_cb(self, iface, changed_props, invalidated_props):
        if iface != GATT_CHRC_IFACE:
            return

        if not len(changed_props):
            return

        value = changed_props.get('Value', None)
        if not value:
            return

        drive_state = value[0]
        self.alarm_ble.wakeup_drive_state(drive_state)
        water = value[1]
        self.alarm_ble.wakeup_water_supply(water)
        motor_speed = float(((value[2] << 8) | value[3]) / 100)
        self.alarm_ble.wakeup_water_pump_state(motor_speed)

    def water_supply_notify_cb(self):
        print("Water Supply notifications enabled")

    def water_supply_val_cb(self, value):
        if len(value) != 4:
            print('Invalid environment sensor location value: ' + repr(value))
            return

        print("WaterPump value: " + str(value))

    def start_client(self):
        self.water_supply_chrc[0].ReadValue(
            {}, reply_handler=self.water_supply_val_cb,
            error_handler=self.generic_error_cb, dbus_interface=GATT_CHRC_IFACE)
        self.water_supply_chrc_iface = dbus.Interface(
            self.water_supply_chrc[0], DBUS_PROP_IFACE)
        self.water_supply_chrc_iface.connect_to_signal(
            "PropertiesChanged", self.water_supply_changed_cb)
        self.water_supply_chrc[0].StartNotify(reply_handler=self.water_supply_notify_cb,
                                              error_handler=self.generic_error_cb,
                                              dbus_interface=GATT_CHRC_IFACE)


class TemperatureAndHumidityQtObserver(Observer):
    def __init__(self):
        super().__init__()
        self.temperature = 0
        self.humidity = 0
        self.ui = None

    def set_ui(self, ui):
        self.ui = ui

    def update(self, model):
        self.temperature = model.last_temperature
        self.humidity = model.last_humidity
        self.qt_temperature()

    def qt_temperature(self):
        self.ui.label_temp.setText(str(self.temperature)+'℃')
        self.ui.label_humidity.setText(str(self.humidity)+'%')


class SoilQtBarObserver(Observer):
    def __init__(self):
        super().__init__()
        self.soil = 0
        self.ui = None

    def set_ui(self, ui):
        self.ui = ui

    def update(self, model):
        self.soil = model.last_soil
        self.qt_progressbar_soil()

    def qt_progressbar_soil(self):
        self.ui.progressBar_soil.setValue(self.soil)


class IntegralTemperatureQtLcdNumberObserver(Observer):
    def __init__(self, pt):
        super().__init__()
        self.integral_temp = 0
        self.ui = None
        self.pt = pt
        self.data_base = self.pt.getDataBase()

    def set_ui(self, ui):
        self.ui = ui
        date = self.data_base.readIntegralTemperatureIndex(-1)
        if date is not None:
            integral_temp = date["TEMPERATURE"]
            integral_temp = float(integral_temp)
            self.ui.lcdNumber_integral_temp.display(round(integral_temp, 1))

    def update(self, model):
        self.integral_temp = model.last_integral_temp
        self.qt_lcd_integral_temp()

    def qt_lcd_integral_temp(self):
        self.ui.lcdNumber_integral_temp.display(round(self.integral_temp, 1))


class IntegralTemperatureQtGraphObserver(Observer):
    def __init__(self):
        super().__init__()
        self.integral_temp = 0
        self.time = 0
        self.ui = None
        
    def set_ui(self, ui):
        self.ui = ui

    def update(self, model):
        self.integral_temp = model.last_integral_temp
        self.time = model.last_time
        self.qt_graph_integral_temp()

    def qt_graph_integral_temp(self):
        self.ui.MultiMqlWidget.update_plot_date(
            self.integral_temp, self.time)


class SoilQtGraphObserver(Observer):
    def __init__(self):
        super().__init__()
        self.soil = 0
        self.time = 0
        self.ui = None

    def set_ui(self, ui):
        self.ui = ui

    def update(self, model):
        self.soil = model.last_soil
        self.time = datetime.datetime.now()
        self.qt_graph_soil()

    def qt_graph_soil(self):
        self.ui.SoilMqlWidget.update_plot_date(self.soil, self.time)


class MyForm(QDialog):
    def __init__(self, pt, parent=None):
        super(MyForm, self).__init__(parent)
        self.pt = pt
        self.ui = ApplicationWindow.Ui_Form()
        self.ui.setupUi(self)
        self.ui.pushButton_graph.clicked.connect(
            self.graph_dialog)
        self.ui.pushButton_debug.clicked.connect(
            self.debug_dialog)
        self.ui.pushButton_connect.clicked.connect(
            self.connect)
        self.ui.pushButton_close.clicked.connect(
            self.close_dialog)
        self.update_vegetable_profile_standard()

    def close_dialog(self):
        print("Close Application")
        state_machine.disconnect()
        sys.exit(0)
    
    def connect(self):
        global state_machine
        state_machine.disconnect()
        while True:
            if state_machine.connecting():
                break
        state_machine.connect()

    def update_vegetable_profile_standard(self):
        vegetable_profile = self.pt.getVegetableProfile()
        self.ui.label_soil_standard.setText(
            str(vegetable_profile["AMOUNTOFWATER"]) + "%")
        self.ui.label_integral_temp_standard.setText(
            str(vegetable_profile["LOADINGTEMPERATURE"]) + "℃")
        self.ui.label_temp_standard.setText(
            str(vegetable_profile["HIGHSUITABLETEMPERATURE"]) + "℃")
        self.ui.label_humidity_standard.setText(
            str(vegetable_profile["HIGHHUMIDITY"]) + "%")

    def graph_dialog(self):
        dialog = GraphDialogForm()
        if dialog.exec():
            pass

    def debug_dialog(self):
        dialog = DebugDialogForm(self.pt)
        if dialog.exec():
            pass


class GraphDialogForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = DayDisplayDialog.Ui_Dialog()
        self.ui.setupUi(self)




class DebugDialogForm(QDialog):
    def __init__(self, pt, parent=None):
        super().__init__(parent)
        self.pt = pt
        self.ui = DebugDialog.Ui_Dialog()
        self.ui.setupUi(self)
        connect_states = self.pt.getConnectStates()
        states = connect_states.get_connect_states()
        self.ui.label_water_connect.setText(self.connect_text(states["water_pump"]))
        self.ui.label_water_connect.setStyleSheet(self.connect_color(states["water_pump"]))
        self.ui.label_fertilizer_connect.setText(self.connect_text(states["fertilizer"]))
        self.ui.label_fertilizer_connect.setStyleSheet(self.connect_color(states["fertilizer"]))
        self.ui.label_sensor_connect.setText(self.connect_text(states["sensor"]))
        self.ui.label_sensor_connect.setStyleSheet(self.connect_color(states["sensor"]))

    def connect_color(self, state):
        if state is True:
            return "QLabel { color: green;  background-color: white;}"
        else:
            return "QLabel { color: red;  background-color: white;}"

    def connect_text(self, state):
        if state is True:
            return "接続"
        else:
            return "切断"


class MonitorDeviceController:
    def __init__(self, pt, form):
        self.pt = pt
        self.form = form

        # Observable Pattern Create
        self.temp_observable = TemperatureAndHumidityCharacteristicObservable(pt)
        self.soil_observable = SoilCharacteristicObservable(pt)
        self.water_supply_observable = WaterSupplyObservable(pt)
        self.drive_state_observable = DriveStateObservable(pt)
        self.water_pump_state_observable = WaterPumpStateObservable(pt)
        self.integral_temp_observable = IntegralTemperatureObservable(pt)

        # Observer Pattern Create and add Observer
        self.water_pump_state_observable.addObserver(
            WaterPumpStateDatabaseWriteObserver(pt))
        self.integral_temp_observable.addObserver(
            IntegralTemperatureDatabaseWriteObserver(pt))
        self.temp_observable.addObserver(TemperatureAndHumidityDatabaseWriteObserver(pt))
        self.soil_observable.addObserver(SoilDatabaseWriteObserver(pt))
        self.set_ui_observer()
        self.drive_remote_device = None
        self.sensor_remote_device = None
        self.bus = dbus.SystemBus()
        self.remote_device = None
        self.adapter = self.find_adapter(self.bus)
        self.adapter_powered_on()

    def set_ui_observer(self):
        self.temp_observer = TemperatureAndHumidityQtObserver()
        self.temp_observer.set_ui(self.form.ui)
        self.temp_observable.addObserver(self.temp_observer)
        self.temp_high_low_temp_observer = TemperatureHighLowQtObserver(self.pt)
        self.temp_high_low_temp_observer.set_ui(self.form.ui)
        self.temp_observable.addObserver(self.temp_high_low_temp_observer)
        self.humidity_high_low_observer = HumidityHighLowQtObserver(self.pt)
        self.humidity_high_low_observer.set_ui(self.form.ui)
        self.temp_observable.addObserver(self.humidity_high_low_observer)
        self.soil_observer = SoilQtBarObserver()
        self.soil_observer.set_ui(self.form.ui)
        self.soil_observable.addObserver(self.soil_observer)
        self.graph_soil_observer = SoilQtGraphObserver()
        self.graph_soil_observer.set_ui(self.form.ui)
        self.soil_observable.addObserver(self.graph_soil_observer)
        self.soil_high_low_observer = SoilMoistureLowLevelQtObserver(self.pt)
        self.soil_high_low_observer.set_ui(self.form.ui)
        self.soil_observable.addObserver(self.soil_high_low_observer)
        self.water_supply_qt_observer = WaterSupplyQtObserver()
        self.water_supply_qt_observer.set_ui(self.form.ui)
        self.water_supply_observable.addObserver(self.water_supply_qt_observer)
        self.drive_state_qt_observer = DriveStateQtObserver(self.pt)
        self.drive_state_qt_observer.set_ui(self.form.ui)
        self.drive_state_observable.addObserver(self.drive_state_qt_observer)
        self.integral_temp_qt_graph_observer = IntegralTemperatureQtGraphObserver()
        self.integral_temp_qt_graph_observer.set_ui(self.form.ui)
        self.integral_temp_observable.addObserver(self.integral_temp_qt_graph_observer)
        self.integral_temp_qt_lcd_observer = IntegralTemperatureQtLcdNumberObserver(
                self.pt)
        self.integral_temp_qt_lcd_observer.set_ui(self.form.ui)
        self.integral_temp_observable.addObserver(self.integral_temp_qt_lcd_observer)

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

    def run(self):
        self.adapter = self.find_adapter(self.bus)
        self.adapter_powered_on()
        self.client = GattClient(self.bus, self.pt, self.form) 

    def stop(self):
        if self.sensor_remote_device is not None:
            self.sensor_remote_device.Disconnect()
        if self.drive_remote_device is not None:
            self.drive_remote_device.Disconnect()

    def request(self):
        states = self.pt.getConnectStates()
        text_creator = self.pt.createTextCreator()
        now = datetime.datetime.now()
        connect_flag, remote_device = self.device_connect(self.bus, SENSOR_DEVICE)
        self.sensor_remote_device = remote_device
        if connect_flag == True:
            states.set_connect_states("sensor", True)
            text = text_creator.connect_state_text("sensor", True, now)
            self.form.ui.textBrowser_state.append(text)
            connect_flag, remote_device = self.device_connect(self.bus, DRIVE_DEVICE)
            self.drive_remote_device = remote_device
            if connect_flag == True:
                states.set_connect_states("water_pump", True)
                text = text_creator.connect_state_text("water_pump", True, now)
                self.form.ui.textBrowser_state.append(text)
                states.set_connect_states("fertilizer", True)
                text = text_creator.connect_state_text("fertilizer", True, now)
                self.form.ui.textBrowser_state.append(text)
                time.sleep(2)
                return True
        return False

    def device_connect(self, bus, device_id):
        object_path = "/org/bluez/hci0"
        remote_it = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, object_path),
                                   DBUS_IT_IFACE)
        xml = ET.fromstring(str(remote_it.Introspect()))
        for i in xml:
            if i.tag == "node":
                if i.attrib["name"] == device_id:
                    object_path += "/" + device_id
        print(object_path)
        self.remote_device = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME,
                                            object_path), BLUEZ_DEVICE_IFACE)
        try:
            print("Connect...")
            self.remote_device.Connect()
            print("Connect Success")
            return True, self.remote_device
        except Exception as e:
            print("Not Connect: {0}".format(e))
            self.remote_device.Disconnect()
            return False, self.remote_device


class MonitorDevice:
    def __init__(self, monitor_device_controller):
        self.communicationState = CommunicationMonitorDeviceState()
        self.waitState = WaitMonitorDeviceState()
        self.state = self.waitState
        self.controller = monitor_device_controller

    def set_wait(self):
        self.state = self.waitState

    def set_communication(self):
        self.state = self.communicationState

    def isCommunicationState(self):
        return self.state == self.communicationState

    def isWaitState(self):
        return self.state == self.WaitState

    def connect(self):
        print("StateMachine: Connect")
        self.state.connect(self)

    def disconnect(self):
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


class MonitorDeviceState:
    def __init__(self):
        pass

    def connect(self, device_drive):
        pass

    def disconnect(self, device_drive):
        device_drive.set_wait()
        device_drive.stop()

    def connecting(self, device_drive):
        pass


class CommunicationMonitorDeviceState(MonitorDeviceState):
    def __init__(self):
        super().__init__()

    def connect(self, device_drive):
        pass

    def disconnect(self, device_drive):
        device_drive.set_wait()
        device_drive.stop()

    def connecting(self, device_drive):
        return True


class WaitMonitorDeviceState(MonitorDeviceState):
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


class MonitorDeviceGattMain:
    def __init__(self):
        global state_machine
        DBusGMainLoop(set_as_default=True)
        pt = PlanterToolkit()
        self.app_qt = QApplication(sys.argv)
        dark_sheet = qdarkstyle.load_stylesheet_pyqt5()
        self.app_qt.setStyleSheet(dark_sheet)
        self.form = MyForm(pt)
        self.device_controller = MonitorDeviceController(pt, self.form)
        state_machine = MonitorDevice(self.device_controller)

    def __enter__(self):
        return self

    def run(self):
        while True:
            if state_machine.connecting():
                break
        state_machine.connect()

    def main(self):
        self.form.showFullScreen()
        self.run()
        flag = self.app_qt.exec_()
        sys.exit(flag)

    def __exit__(self, exc_type, exc_value, traceback):
        print("ExcType: {0}".format(exc_type))
        print("ExcValue: {0}".format(exc_value))
        print("Traceback: {0}".format(traceback))
        state_machine.disconnect()


if __name__ == '__main__':
    with MonitorDeviceGattMain() as main:
        main.main()
