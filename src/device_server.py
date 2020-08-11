from qt import *
from devices import SerialDevice, profiles, profile_names
from device_manager import DeviceManager
import time
import logging
import json
from urllib.parse import urlparse
from serial.tools.list_ports import comports
from bundles import SigBundle, SlotBundle
from settings import Settings
from command_palette import Command


class Settings(Settings):
    name: str = 'server'
    secure: bool = False
    autostart: bool = True
    listen_port: int = 43000


settings = Settings().register('Server')


@DeviceManager.subscribe
class DeviceServer(QObject):
    def __init__(self):
        super().__init__()
        self.settings = settings
        self.log = logging.getLogger(__name__)
        self.devices = {}

        self.commands = [
            Command("Device Server: Foo", self),
            Command("Device Server: Bar", self),
            Command("Device Server: Baz", self),
            Command("Device Server: Fizz", self),
            Command("Device Server: Buzz", self),
        ]

        if self.settings.secure():
            mode = QWebSocketServer.SecureMode
        else:
            mode = QWebSocketServer.NonSecureMode

        self.server = QWebSocketServer(self.settings.name(), mode)
        self.client = None
        self.sockets = {}

        if self.settings.autostart():
            self.start_server()

    def start_server(self):
        if self.server.listen(address=QHostAddress.Any, port=self.settings.listen_port()):
            self.log.info(f"Device server listening at: {self.server.serverAddress().toString()}:{str(self.server.serverPort())}")
        else:
            self.log.info('Failed to start device server.')
        self.server.newConnection.connect(self.on_new_connection)
        self.server.newConnection.connect(lambda: self.log.info(f'socket connected'))

    def on_new_connection(self):
        socket = self.server.nextPendingConnection()
        socket.disconnected.connect(lambda: self.log.info("socket disconnected"))
        url = urlparse(socket.resourceName())

        if url.path == "/control":
            self.client_socket_connected(socket)
        elif url.path == "/link":
            self.device_socket_connected(socket)
            
    def device_socket_connected(self, socket):
        url = urlparse(socket.resourceName())

        for guid in self.devices.keys():
            if self.devices[guid].port == url.query:
                self.devices[guid].connect_socket(socket)
                self.sockets[url.query] = socket
                return
        socket.close()

    def client_socket_connected(self, socket):
        self.client = socket
        self.client.textMessageReceived.connect(self.processTextMessage)
        self.client.disconnected.connect(lambda: self.client.deleteLater())

        ports = sorted([port.device for port in comports()])
        devices = [self.devices[k].description for k in self.devices.keys()]

        self.send_later(json.dumps({"ports":ports}))
        self.send_later(json.dumps({"devices":devices}))
        self.send_later(json.dumps({"profiles":profile_names}))

    def processTextMessage(self, message):
        self.log.debug(f"RX: {message}")

        try: 
            msg = json.loads(message)
        except:
            return

        if 'create_device' in msg.keys():
            profile = msg['create_device']['profile']
            port = msg['create_device']['port']
            device = profiles[profile](port)
            self.signals.inject.emit(device)

        if 'remove_device' in msg.keys():
            guid = msg['remove_device']['guid']
            self.signals.destroy.emit(guid)

    def send_later(self, message):
        QTimer.singleShot(10, lambda: self.client.sendTextMessage(message))

    def on_device_added(self, device):
        self.devices[device.guid] = device

        if self.client:
            self.send_later(json.dumps({"device_added":device.description}))

    def on_device_removed(self, guid):
        description = self.devices[guid].description
        self.devices.pop(guid)

        if self.client:
            self.send_later(json.dumps({"device_removed":description}))