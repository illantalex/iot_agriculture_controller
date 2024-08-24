import fcntl
import struct
import sys

# Define device file name
DEVICE_FILE_NAME = "/dev/bme280"

# Define constants for _IOC macro
_IOC_NRBITS = 8
_IOC_TYPEBITS = 8
_IOC_SIZEBITS = 14
_IOC_DIRBITS = 2

_IOC_NRSHIFT = 0
_IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
_IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS
_IOC_DIRSHIFT = _IOC_SIZESHIFT + _IOC_SIZEBITS

_IOC_NONE = 0
_IOC_WRITE = 1
_IOC_READ = 2

# Define _IOC and _IOR macros
def _IOC(dir, type, nr, size):
    return (dir << _IOC_DIRSHIFT) | (ord(type) << _IOC_TYPESHIFT) | (nr << _IOC_NRSHIFT) | (size << _IOC_SIZESHIFT)

def _IOR(type, nr, size):
    return _IOC(_IOC_READ, type, nr, size)

# Calculate size of long int
size_of_long_int = struct.calcsize('l')

# Define ioctl commands using the calculated values
IOCTL_GET_TEMPERATURE = _IOR('t', 1, size_of_long_int)
IOCTL_GET_HUMIDITY = _IOR('h', 2, size_of_long_int)
IOCTL_GET_PRESSURE = _IOR('p', 3, size_of_long_int)

fd = os.open(DEVICE_FILE_NAME, os.O_RDWR)

def ioctl_read_long(command):
    buf = struct.pack('l', 0)
    try:
        buf = fcntl.ioctl(fd, command, buf)
        return struct.unpack('l', buf)[0]
    except Exception as e:
        print(f"ioctl error with command {hex(command)}: {e}")
        return None


def get_temperature():
    temperature = ioctl_read_long(fd, IOCTL_GET_TEMPERATURE)
    if temperature is not None:
        return temperature / 100.0


def get_humidity():
    humidity = ioctl_read_long(fd, IOCTL_GET_HUMIDITY)
    if humidity is not None:
        return humidity / 1024.0


def get_pressure():
    pressure = ioctl_read_long(fd, IOCTL_GET_PRESSURE)
    if pressure is not None:
        return pressure / 256.0
