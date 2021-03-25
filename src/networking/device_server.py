from qt import *
from codex import profiles
from codex import DeviceManager
import logging
import json
from urllib.parse import urlparse
from command_palette import Command


@DeviceManager.subscribe
class DeviceServer(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.log = logging.getLogger(__name__)

        self.commands = []

        self.server = QWebSocketServer('server-name', QWebSocketServer.NonSecureMode)
        self.client = None
        self.sockets = {}

        if self.server.listen(address=QHostAddress.Any, port=43000):
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

        for _, device in self.devices.items():
            self.send_later(json.dumps({"device_added":device.description}))

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

    def device_added(self, device):
        if self.client:
            self.send_later(json.dumps({"device_added":device.description}))

    def device_removed(self, guid):
        description = self.devices[guid].description

        if self.client:
            self.send_later(json.dumps({"device_removed":description}))