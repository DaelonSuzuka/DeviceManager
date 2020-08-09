from .serial_device import SerialDevice, CommonMessagesMixin
from .device_widget import DeviceWidget
from .remote_serial import RemoteSerial

from .profiles import *

profiles = {p.profile_name: p for p in SerialDevice.__subclasses__()}

profile_names = sorted(profiles.keys())