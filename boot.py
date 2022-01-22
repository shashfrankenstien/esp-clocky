# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import network
import machine
boot = machine.reset
wifi = network.WLAN(network.STA_IF)
def wifi_connect(ssid, password):
    global wifi
    if not wifi.isconnected():
        print('connecting to network...')
        wifi.active(True)
        wifi.connect(ssid, password)
        while not wifi.isconnected():
            pass
    print('network config:', wifi.ifconfig())

wifi_connect('0_RedWilly', 'TG1672GE25912')
from ntptime import settime
settime()


def touch(filename, code):
	with open(filename, 'w') as f:
		f.write(code)
