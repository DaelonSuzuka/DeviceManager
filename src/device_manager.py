from devices import SerialDevice, profiles, profile_names, UnknownDevice
from serial.tools.list_ports import comports
import time
import logging
from qt import *
from bundles import SigBundle, SlotBundle
from settings import Settings
import typing


class Settings(Settings):
    scan_period: int = 250
    update_period: int = 10
    startup: typing.List[str] = [
        'TS-480:/dev/ttyS0',
        'Alpha4510A:/dev/ttyUSB0',
        'DTS-4:/dev/ttyS2',
        'VariableDummyLoad:/dev/ttyS3',
    ]

settings = Settings().register('Devices')

class DeviceManager:
    def __init__(self):
        self.settings = settings
        self.log = logging.getLogger(__name__)
        self.log.info("Initializing DeviceManager...")

        self.signals = SigBundle({'device_added':[SerialDevice], 'device_removed': [str]})
        self.slots = SlotBundle({'add_device':[SerialDevice], 'remove_device': [str]})
        self.slots.link_to(self)

        self.devices = {}
        self.new_devices = []
        self.first_scan = True
        self.ports = []
        
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(lambda: self.scan())
        self.scan_timer.start(self.settings.scan_period())

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(lambda: self.update())
        self.update_timer.start(self.settings.update_period())

    def connect_to(self, things):
        for thing in things:
            if hasattr(thing, 'slots'):
                if hasattr(thing.slots, 'device_added') and hasattr(thing.slots, 'device_removed'):
                    self.signals.device_added.connect(thing.slots.device_added)
                    self.signals.device_removed.connect(thing.slots.device_removed)

            if hasattr(thing, 'signals'):
                if hasattr(thing.signals, 'add_device') and hasattr(thing.signals, 'remove_device'):
                    thing.signals.add_device.connect(self.slots.add_device)
                    thing.signals.remove_device.connect(self.slots.remove_device)

    def on_add_device(self, device):
        self.devices[device.guid] = device
        self.signals.device_added.emit(device)

    def on_remove_device(self, guid):
        self.signals.device_removed.emit(guid)
        self.devices[guid].close()
        self.devices.pop(guid)

    def scan(self):
        new_ports = [p.device for p in sorted(comports())]

        if self.first_scan:
            for p in new_ports:
                for string in self.settings.startup():
                    profile = string.split(':')[0]
                    port = string.split(':')[1]
                    if p == port:
                        self.on_add_device(profiles[profile](port=port))
                        self.ports.append(p)
            self.first_scan = False

        for port in [p for p in new_ports if p not in self.ports]:            
            self.log.debug(f"New device connected at ({port}), enumerating...")
            device = UnknownDevice(port=port)
            self.new_devices.append(device)

        for port in [p for p in self.ports if p not in new_ports]:            
            self.log.debug(f"Existing device removed from ({port}), cleaning up...")
            
            for k in self.devices.keys():
                if self.devices[k].port == port:
                    self.on_remove_device(self.devices[k].guid)
                    break

        self.ports = new_ports

    def update(self):
        for device in self.new_devices:
            device.communicate()

            if (time.time() - device.time_created) > 3:
                self.log.debug(f"Enumeration failed on ({device.port})")
                device.close()
                self.new_devices.remove(device)
                continue
        
            if device.guid:
                if device.name in profile_names:
                    device.close()
                    new_device = profiles[device.name](device=device)

                    self.log.debug(f"Enumeration succeeded on ({new_device.port})")

                    self.devices[new_device.guid] = new_device
                    self.new_devices.remove(device)

                    self.signals.device_added.emit(new_device)

        for guid in self.devices.keys():
            self.devices[guid].communicate()