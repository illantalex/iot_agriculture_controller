# Agrognomic plants monitoring system

This repository contains the code for the Agrognomic project that is running on the Raspberry Pi device.

## This code has the following functions

- Reading the RTC time from the 4G Cat 1 modem (SIMCOM A7672)
- Accepting the last sent RTC time and needed time interval by corresponding MQTT topics (in order to assure regular sending of data)
- Capture an image (can be ill plants or some bad weeds) and send it for detection by the YOLOv8 ONNX network (done in the onnx folder by the C++ program), save the detections data
- Get temperature, humidity and atmospheric pressure from the BME280 sensor using this driver (https://github.com/illantalex/bme280-driver)
- Send all the obtained data to the corresponding MQTT topics
- Send needed sleep time by i2c to the ESP8285 sleep controller (https://github.com/illantalex/device_sleep_control)
- Send a command to the sleep controller to start the powersafe sleep mode
