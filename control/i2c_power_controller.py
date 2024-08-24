import smbus
import time
import os

bus = smbus.SMBus(1)
DEVICE_ADDR = 0x42


def send_sleep_command():
    # Send sleep command to the controller
    bus.write_byte(DEVICE_ADDR, 0x01)
    time.sleep(0.1)


def set_time_command(us):
    # Set the 64 bit time on the controller reverse order
    send_data = []
    for i in range(8):
        send_data.append(us & 0xFF)
        us >>= 8
    send_data.reverse()
    bus.write_i2c_block_data(DEVICE_ADDR, 0x02, send_data)
    time.sleep(0.1)
