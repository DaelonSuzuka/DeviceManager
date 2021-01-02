from devices import SerialDevice, profiles, profile_names, UnknownDevice, DeviceStates
from serial.tools.list_ports import comports
import time
import logging
from qt import *
from bundles import SigBundle, SlotBundle


# servitor-prime
startup = [
    'CalibrationTarget:/dev/ttyS4:115200',
    # 'ConsoleDevice:/dev/ttyS4',
    'ConsoleDevice:/dev/ttyS5',
]


class DeviceManager(QObject):
    signals = {
        'add_device':[SerialDevice],
        'remove_device': [str]
    }
    slots = {
        'device_added': [SerialDevice], 
        'device_removed': [str],
        'subscribed': [None],
    }
    new_subscribers = []

    @classmethod
    def subscribe(cls, target):
        old_init = target.__init__

        def get_added():
            def on_device_added(self, device):
                self.devices[device.guid] = device
                if hasattr(self, 'device_added'):
                    self.device_added(device)
            return on_device_added

        def get_removed():
            def on_device_removed(self, guid):
                if hasattr(self, 'device_removed'):
                    self.device_removed(guid)
                self.devices.pop(guid)
            return on_device_removed

        def new_init(obj, *args, **kwargs):
            old_init(obj, *args, **kwargs)
            
            obj.signals = SigBundle(cls.signals)
            obj.slots = SlotBundle(cls.slots)
            obj.slots.link_to(obj)
            
            obj.devices = {}
            
            cls.new_subscribers.append(obj)

        target.on_device_added = get_added()
        target.on_device_removed = get_removed()

        target.__init__ = new_init

        return target

    @classmethod
    def subscribe_to(cls, device_name):

        def get_added():
            def on_device_added(self, device):
                if device.profile_name == device_name:
                    if self.device:
                        return
                    self.device = device
                    self.setEnabled(True)
                    if hasattr(self, 'connected'):
                        self.connected(device)
            return on_device_added

        def get_removed():
            def on_device_removed(self, guid):
                if self.device is None or self.device.guid != guid:
                    return
                self.device = None
                self.setEnabled(False)
                if hasattr(self, 'disconnected'):
                    self.disconnected(guid)
            return on_device_removed

        def decorator(target):
            target.on_device_added = get_added()
            target.on_device_removed = get_removed()

            old_init = target.__init__

            def new_init(obj, *args, **kwargs):
                old_init(obj, *args, **kwargs)
                
                obj.slots = SlotBundle(cls.slots)
                obj.slots.link_to(obj)

                obj.device = None
                obj.setEnabled(False)
                
                cls.new_subscribers.append(obj)

            target.__init__ = new_init

            return target
        return decorator

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.log = logging.getLogger(__name__)
        self.log.info("Initializing DeviceManager...")

        self.signals = SigBundle({'device_added':[SerialDevice], 'device_removed': [str]})
        self.slots = SlotBundle({'add_device':[SerialDevice], 'remove_device': [str]})
        self.slots.link_to(self)

        self.subscribers = []

        self.devices = {}
        self.new_devices = []
        self.first_scan = True
        self.ports = []
        
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(lambda: self.scan())
        self.scan_timer.start(250)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(lambda: self.update())
        self.update_timer.start(1)
        
        self.check_for_new_subscribers()

        UnknownDevice.register_autodetect_info(profiles)

    def close(self):
        self.scan_timer.stop()
        self.update_timer.stop()
        for _, device in self.devices.items():
            device.close()

    def check_for_new_subscribers(self):
        for new_sub in self.new_subscribers:
            if new_sub not in self.subscribers:
                self.connect_subscriber(new_sub)
                
            self.new_subscribers.remove(new_sub)

    def connect_subscriber(self, subscriber):
        if hasattr(subscriber, 'slots'):
            if hasattr(subscriber.slots, 'device_added') and hasattr(subscriber.slots, 'device_removed'):
                self.signals.device_added.connect(subscriber.slots.device_added)
                self.signals.device_removed.connect(subscriber.slots.device_removed)
                
                for device in self.devices:
                    subscriber.slots.device_added(self.devices[device])
        
            if hasattr(subscriber.slots, 'subscribed'):
                subscriber.slots.subscribed()

        if hasattr(subscriber, 'signals'):
            if hasattr(subscriber.signals, 'add_device') and hasattr(subscriber.signals, 'remove_device'):
                subscriber.signals.add_device.connect(self.slots.add_device)
                subscriber.signals.remove_device.connect(self.slots.remove_device)

    def on_add_device(self, device):
        self.devices[device.guid] = device
        self.signals.device_added.emit(device)

    def on_remove_device(self, guid):
        self.signals.device_removed.emit(guid)
        self.devices[guid].close()
        self.devices.pop(guid)

    def scan(self):
        self.check_for_new_subscribers()

        new_ports = [p.device for p in sorted(comports())]

        if self.first_scan:
            for p in new_ports:
                for string in startup:
                    parts = string.split(':')
                    profile = parts[0]
                    port = parts[1]
                    baud = parts[2] if len(parts) == 3 else None

                    if p == port:
                        if baud:
                            self.on_add_device(profiles[profile](port=port, baud=baud))
                        else:
                            self.on_add_device(profiles[profile](port=port))
                        self.ports.append(p)
            self.first_scan = False

        for port in [p for p in new_ports if p not in self.ports]:
            # dumb work around for program crashing on my desktop
            if port not in ['COM1', 'COM3']:
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

            if device.state == DeviceStates.enumeration_failed:
                self.log.debug(f"Enumeration failed on ({device.port})")
                device.close()
                self.new_devices.remove(device)
        
            elif device.state == DeviceStates.enumeration_succeeded:
                if device.name in profile_names:
                    device.close()
                    new_device = profiles[device.name](device=device)

                    self.log.debug(f"Enumeration succeeded on ({new_device.port})")

                    self.devices[new_device.guid] = new_device
                    self.new_devices.remove(device)

                    self.signals.device_added.emit(new_device)

        for guid in self.devices.keys():
            self.devices[guid].communicate()