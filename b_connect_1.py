# This work is licensed under the MIT license.
# Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE
#
# Connect Example
#
# This example shows how to connect to a WiFi network.

import network
import time
import userfunc

SSID = "rtthread"  # Network SSID
KEY = "12345678"  # Network key

# Init wlan module and connect to network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)

while not wlan.isconnected():
    print('Trying to connect to "{:s}"...'.format(SSID))
    time.sleep_ms(1000)

# We should have a valid IP now via DHCP
print("WiFi Connected ", wlan.ifconfig())

userfunc.mqtt_start()

count = 0
while True:
    time.sleep_ms(1000)
    count = count +1
    send_data = str(count)
    ret = userfunc.mqtt_publish(send_data)
    print(send_data)

