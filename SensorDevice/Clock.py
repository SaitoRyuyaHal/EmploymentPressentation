#!/usr/bin/python3
# -*- coding:utf-8 -*-

import signal
import time

class AlarmClock:
    wake = []
    timer = []
    timer_count = []
    def __init__(self):
        pass

    def reset(self):
        AlarmClock.wake = []
        AlarmClock.timer = []
        AlarmClock.timer_count = []

    def wakeEvery(self, timer, wake_func):
        AlarmClock.wake.append(wake_func)
        AlarmClock.timer.append(timer)
        AlarmClock.timer_count.append(0)

    def wake_up(self, arg1, arg2):
        for i in range(len(AlarmClock.wake)):
            if AlarmClock.timer_count[i] == AlarmClock.timer[i]:
                AlarmClock.wake[i]()
                AlarmClock.timer_count[i] = 0
            AlarmClock.timer_count[i] += 1

    def start(self):
        signal.signal(signal.SIGALRM, self.wake_up)
        signal.setitimer(signal.ITIMER_REAL, 0.01, 0.01)

    def stop(self):
        signal.alarm(0)


if __name__ == "__main__":
    def func():
        print("HELLO")
    def func2():
        print("World")
    al = AlarmClock()
    al.wakeEvery(10, func)
    al.wakeEvery(30, func2)
    al.start()

    while True:
        time.sleep(1)
