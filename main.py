#!/usr/bin/python3

from datetime import datetime
import serial
import os
import sys
import time
import dotenv

import paho.mqtt.client as mqtt
from picamera2 import Picamera2, Preview

from control import at_mqtt
from control import bme280_ctl
from control import i2c_power_controller

picam2 = Picamera2()

dotenv.load_dotenv()
# MQTT settings
CLIENT_ID = os.getenv('CLIENT_ID')
MY_NAME = os.getenv('MY_NAME')
# MQTT Broker settings
BROKER_ADDRESS = os.getenv('BROKER_ADDRESS')
BROKER_PORT = os.getenv('BROKER_PORT')

TEMPERATURE_TOPIC = f"{MY_NAME}/{CLIENT_ID}/temp"
HUMIDITY_TOPIC = f"{MY_NAME}/{CLIENT_ID}/humid"
PRESSURE_TOPIC = f'{MY_NAME}/{CLIENT_ID}/pressure'
YOLO_DATA_TOPIC = f'{MY_NAME}/{CLIENT_ID}/data'
RTC_TOPIC = f'{MY_NAME}/{CLIENT_ID}/rtc'
TIME_INTERVAL_TOPIC = f'{MY_NAME}/{CLIENT_ID}/interval'
TEST_DATA_TOPIC = f'{MY_NAME}/{CLIENT_ID}/test'


MAX_TRIES = 10

DATETIME_FORMAT = '%y/%m/%d,%H:%M:%S'

time_interval = None
last_received_time = None


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(RTC_TOPIC)
    client.subscribe(TIME_INTERVAL_TOPIC)


def on_message(client, userdata, msg):

    global last_received_time, time_interval
    print(f"Received message: {msg.payload.decode()}")
    if msg.topic == RTC_TOPIC:
        print(f"RTC message received: {msg.payload.decode()}")
        last_received_time = msg.payload.decode()
    elif msg.topic == TIME_INTERVAL_TOPIC:
        print(f"Time interval message received: {msg.payload.decode()}")
        time_interval = msg.payload.decode()


mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message


def all_exit():
    sys.exit(1)


if __name__ == '__main__':
    at_mqtt.init_module()
    num_tries = 0
    # Check network reachability
    while not at_mqtt.check_network_reachability():
        num_tries += 1
        if num_tries == MAX_TRIES:
            all_exit()
        time.sleep(3)

    time.sleep(10)

    # Read current time
    mqttc.connect(BROKER_ADDRESS, int(BROKER_PORT), 60)
    mqttc.loop_start()

    mqttc.subscribe(RTC_TOPIC)
    mqttc.subscribe(TIME_INTERVAL_TOPIC)

    time.sleep(5)

    curr_time = at_mqtt.read_clock()

    mqttc.unsubscribe(RTC_TOPIC)
    mqttc.unsubscribe(TIME_INTERVAL_TOPIC)

    if last_received_time is None or time_interval is None:
        print("No RTC or time interval received")
        with open("/home/pi/rtc.txt", "r") as f:
            last_received_time = f.read().strip()
        with open("/home/pi/time_interval.txt", "r") as f:
            time_interval = f.read().strip()

    mqttc.publish(RTC_TOPIC, last_received_time, qos=1, retain=True)
    mqttc.publish(TIME_INTERVAL_TOPIC, str(time_interval), qos=1, retain=True)

    with open("/home/pi/rtc.txt", "w") as f:
        f.write(last_received_time)
    with open("/home/pi/time_interval.txt", "w") as f:
        f.write(time_interval)

    last_sent_time = datetime.strptime(last_received_time, DATETIME_FORMAT)
    current_time = datetime.strptime(curr_time, DATETIME_FORMAT)
    time_diff = current_time - last_sent_time

    time_remaining = int(time_interval) * 3600 - time_diff.total_seconds()
    if time_remaining > 60:
        i2c_power_controller.set_time_command(int(time_remaining) * 1000000)
        all_exit()

    i2c_power_controller.set_time_command(int(time_interval) * 3600 * 1000000)


    preview_config = picam2.create_preview_configuration(main={"size": (1280, 960)})
    picam2.configure(preview_config)

    picam2.start()
    time.sleep(1)

    metadata = picam2.capture_file("/tmp/img.jpg")
    print(metadata)

    picam2.close()

    yolo_output = os.popen(f"/home/pi/onnx/build/main").read()

    time.sleep(5)
    # mqttc.reconnect()
    # time.sleep(3)

    mqttc.publish(RTC_TOPIC, curr_time, qos=1, retain=True)
    mqttc.publish(TEMPERATURE_TOPIC, str(bme280_ctl.get_temperature()), qos=1)
    mqttc.publish(HUMIDITY_TOPIC, str(bme280_ctl.get_humidity()), qos=1)
    mqttc.publish(PRESSURE_TOPIC, str(bme280_ctl.get_pressure()), qos=1)
    # mqttc.publish(TEST_DATA_TOPIC, "Hello World", qos=1, retain=True)
    mqttc.publish(YOLO_DATA_TOPIC, yolo_output, qos=1)

    time.sleep(5)
    mqttc.loop_stop()
    mqttc.disconnect()
