#!/usr/bin/env python3
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop

mainloop = None

class AlarmClock:
    def __init__(self, refresh=False):
        global mainloop
        if mainloop is None or refresh is True:
            mainloop = GLib.MainLoop()
            DBusGMainLoop(set_as_default=True)

    def run(self):
        mainloop.run()

    def stop(self):
        mainloop.quit()

    def add(self, time, func):
        return GLib.timeout_add(time, func)

    def remove(self, func):
        GLib.source_remove(func)
