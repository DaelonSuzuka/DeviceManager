from .serial_device import SerialDevice, CommonMessagesMixin
from .remote_serial import RemoteSerial

from .json_buffer import JSONBuffer
from .delimiter_buffer import DelimiterBuffer

from .console_device import ConsoleDevice
from .unknown_device import UnknownDevice

from plugins.devices import *

profiles = {p.profile_name: p for p in SerialDevice.__subclasses__()}

profile_names = sorted(profiles.keys())