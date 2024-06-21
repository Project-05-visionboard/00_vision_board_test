# Edge Impulse - OpenMV Image Classification Example

# 说明：来自https://edgeimpulse.com/ 的 vangaovh/nuble_again 项目中 deployment V3

import sensor, image, time, os, tf, uos, gc
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

sensor.reset()                         # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565)    # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)      # Set frame size to QVGA (320x240)
sensor.set_windowing((240, 240))       # Set 240x240 window.
sensor.skip_frames(time=2000)          # Let the camera adjust.

net = None
labels = None

try:
    # load the model, alloc the model file on the heap if we have at least 64K free after loading
    net = tf.load("trained.tflite", load_to_fb=uos.stat('trained.tflite')[6] > (gc.mem_free() - (64*1024)))
except Exception as e:
    print(e)
    raise Exception('Failed to load "trained.tflite", did you copy the .tflite and labels.txt file onto the mass-storage device? (' + str(e) + ')')

try:
    labels = [line.rstrip('\n') for line in open("labels.txt")]
except Exception as e:
    raise Exception('Failed to load "labels.txt", did you copy the .tflite and labels.txt file onto the mass-storage device? (' + str(e) + ')')

found_0_count = 0
found_2_count = 0
clock = time.clock()
while(True):
    clock.tick()

    img = sensor.snapshot()

    # default settings just do one detection... change them to search the image...
    for obj in net.classify(img, min_scale=1.0, scale_mul=0.8, x_overlap=0.5, y_overlap=0.5):
        print("**********\nPredictions at [x=%d,y=%d,w=%d,h=%d]" % obj.rect())
        img.draw_rectangle(obj.rect())
        # This combines the labels and confidence values into a list of tuples
        predictions_list = list(zip(labels, obj.output()))

        for i in range(len(predictions_list)):
            print("%s = %f" % (predictions_list[i][0], predictions_list[i][1]))

            if (predictions_list[i][0] == '0') & (predictions_list[i][1] > 0.9) :
                continue_data_0 = continue_data_0 + 1
                if continue_data_0 > 10:
                    continue_data_0 = 0
                    found_0_count = found_0_count +1
                    found_0_str = str(found_0_count)
                    ret = userfunc.mqtt_publish('found 0 times = '+ found_0_str)
            elif (predictions_list[i][0] == '0') & (predictions_list[i][1] < 0.9):
                continue_data_0 = 0
            
            if (predictions_list[i][0] == '2') & (predictions_list[i][1] > 0.9) :
                continue_data_2 = continue_data_2 + 1
                if continue_data_2 > 10:
                    continue_data_2 = 0
                    found_2_count = found_2_count +1
                    found_2_str = str(found_2_count)
                    ret = userfunc.mqtt_publish('found 2 times = '+ found_2_str)
            elif (predictions_list[i][0] == '2') & (predictions_list[i][1] < 0.9):
                continue_data_2 = 0

    print(clock.fps(), "fps")
