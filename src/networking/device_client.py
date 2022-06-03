from qtstrap import *
from qtstrap.extras.command_palette import Command
from qtpy.QtWebSockets import *
from codex import DeviceManager
import logging
from urllib.parse import urlparse
import json
from .utils import get_ip


@DeviceManager.subscribe
class DeviceClient(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.log = logging.getLogger(__name__)

        self.linked_devices = {}
        self.remote_devices = {}
        self.remote_profiles = []
        
        self.connect_on_startup = QSettings().value('connect_on_startup', False) == 'true'
        self.current_connection = QSettings().value('current_connection', '10.0.0.207')
        default_previous_connections = ['ldg.hopto.org', 'daelon.hopto.org', '10.0.0.207']
        self.previous_connections = QSettings().value('previous_connections', default_previous_connections)
        
        self.commands = [
            Command('Device Client: Connect', triggered=self.connect_to_remote),
            Command('Device Client: Disconnect', triggered=self.disconnect_from_remote),
        ]

        self.socket = QWebSocket()
        self.socket.connected.connect(lambda: self.log.info("Connected to server"))
        self.socket.textMessageReceived.connect(self.process_message)

        self.socket.disconnected.connect(self.unlink_all_devices)

    def on_subscribed(self):
        if self.connect_on_startup:
            if urlparse(self.current_connection).path != urlparse(get_ip()).path:
                self.connect_to_remote()

    def device_added(self, device):
        if device.port == "RemoteSerial":
            for k in self.remote_devices.keys():
                if device.profile_name == self.remote_devices[k]['profile_name']:
                    print("found")

    def connect_to_remote(self, address=None):
        if address is not None:
            self.current_connection = address
            QSettings().setValue('current_connection', self.current_connection)
            if address not in self.previous_connections:
                self.previous_connections.append(address)

        self.open_socket()

    def disconnect_from_remote(self):
        self.close_socket()

    def toggle_connect_on_startup(self):
        self.connect_on_startup = not self.connect_on_startup
            
        QSettings().setValue('connect_on_startup', self.connect_on_startup)

    def open_socket(self):
        url = f'ws://{self.current_connection}:43000/control'
        self.log.info(f"Attempting to connect to server at: {QUrl(url)}")
        self.socket.open(QUrl(url))

    def close_socket(self):
        self.log.info(f"Closing socket")
        self.socket.close()

    def send_message(self, message):
        self.log.debug(f"TX: {message}")
        self.socket.sendTextMessage(message)

    def process_message(self, message):
        self.log.debug(f"RX: {message}")

        try:
            msg = json.loads(message)
        except:
            return
        
        if 'device_added' in msg.keys():
            device = msg["device_added"]
            self.remote_devices[device['guid']] = device
            self.link_to_remote_device(self.current_connection, device['guid'])

        if 'device_removed' in msg.keys():
            device = msg["device_removed"]
            self.remote_devices.pop(device['guid'])

    def link_to_remote_device(self, url, guid):
        device = self.remote_devices[guid]
        address = f'{url}:43000'

        port = f"RemoteSerial:{address}/link?{device['port']}"
        profile = device['profile_name']

        new_device = DeviceManager.profiles()[profile](port=port)
        self.linked_devices[guid] = new_device
        self.signals.add_device.emit(new_device)

    def unlink_all_devices(self):
        for _, device in self.linked_devices.items():
            self.signals.remove_device.emit(device.guid)

        self.linked_devices = {}