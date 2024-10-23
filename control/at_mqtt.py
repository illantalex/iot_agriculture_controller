import time
import os
import re
import serial

# Replace with your serial port and baud rate
SERIAL_PORT = '/dev/ttyUSB1'
BAUD_RATE = 9600

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=None)

GET_RTC = 'AT+CCLK?'
pattern = r'\d{2}/\d{2}/\d{2},\d{2}:\d{2}:\d{2}'

def init_module():
    send_at_command("ATE0")


def check_network_reachability() -> bool:
    try:
        status, response = send_at_command('AT+CGREG?')
        if '+CGREG: 0,5' in response:
            print("Network registered and reachable.")
            return True
        else:
            print("Error: Network not reachable.")
            return False
    except Exception as e:
        print(f'Error: {e}')
        return False
    try:
        status, response = send_at_command('AT+CSQ')
        if '+CSQ: ' in response:
            # Extract signal quality
            signal_quality = int(response.split(' ')[1].split(',')[0])
            if signal_quality > 0 and signal_quality <= 31:
                print(f"Signal quality is {signal_quality}.")
                return True
            else:
                print("Error: No signal detected.")
                return False
        else:
            print("Error: No signal detected.")
            return False
    except Exception as e:
        print(f'Error: {e}')
        return False


def read_clock():
    ser.write((GET_RTC + '\r\n').encode())
    time.sleep(2)
    response = ser.read(ser.in_waiting).decode()
    print(f'Sent: {GET_RTC}\nResponse: {response}')
    # return response without +CCLK: and OK
    match = re.search(pattern, response)
    if match:
        response = match.group()
    else:
        response = None
    print("Clock response:", response)
    return response


def send_at_command(command, delay=1) -> (bool, str):
    ser.write((command + '\r\n').encode())
    while True:
        time.sleep(1)
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode()
            break
    print(f'Sent: {command}\nResponse: {response}')
    if 'CMQTTCONNLOST' in response:
        mqtt_reconnect()
        return (True, response)
    if 'ERROR' in response:
        return (False, response)
    return (True, response)
