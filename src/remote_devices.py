from qt import *
from devices import profiles
from device_manager import DeviceManager
import logging
import json
from urllib.parse import urlparse
import qtawesome as qta
from command_palette import CommandPalette, Command


import socket
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


class RemoteStatusWidget(QWidget):
    def __init__(self, *args, client=None, server=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName('NetworkStatusBarItem')
        
        self.client = None
        self.server = None

        if client:
            self.client = client
            client.socket.connected.connect(self.client_connected)
            client.socket.disconnected.connect(self.client_disconnected)
        if server:
            self.server = server

            
        self.commands = [
            Command('Device Client: Connect to', self, triggered=self.open_address_prompt),
        ]

        self.setAttribute(Qt.WA_AcceptTouchEvents, True)
    
        self.status = QLabel('Not Connected')
        self.icon_on = qta.icon('mdi.lan-connect', color='lightgray').pixmap(QSize(20, 20))
        self.icon_off = qta.icon('mdi.lan-disconnect', color='gray').pixmap(QSize(20, 20))
        self.icon = QLabel('')
        self.icon.setPixmap(self.icon_off)

        with CHBoxLayout(self, margins=(0, 0, 0, 0)) as layout:
            layout.add(self.icon)
            layout.add(self.status)
        
    def mousePressEvent(self, event):
        connect = QAction("Connect", self, triggered=self.connect_client)
        connect_to = QAction("Connect to", self, triggered=self.open_address_prompt)
        disconnect = QAction("Disconnect", self, triggered=self.disconnect_client)

        startup = QAction(
            "Connect at Startup", 
            self, 
            checkable=True, 
            checked=bool(self.client.connect_on_startup),
            triggered=self.client.toggle_connect_on_startup
        )

        menu = QMenu('', self)
        menu.addAction(connect)
        menu.addAction(connect_to)
        menu.addAction(disconnect)
        
        if self.client:
            menu.addSeparator()
            for address in self.client.previous_connections:
                menu.addAction(QAction(address, self, triggered=lambda a=address: self.connect_client(a)))
        
        menu.addSeparator()
        menu.addAction(startup)

        menu.exec_(event.globalPos())

    def client_connected(self):
        self.status.setText(self.client.current_connection)
        self.icon.setPixmap(self.icon_on)

    def client_disconnected(self):
        self.status.setText("Not Connected")
        self.icon.setPixmap(self.icon_off)

    def connect_client(self, address=None):
        if self.client:
            self.status.setText("Connecting...")
            self.client.disconnect_from_remote()
            self.client.connect_to_remote(address)

    def disconnect_client(self):
        self.client.disconnect_from_remote()

    def open_address_prompt(self):
        CommandPalette().open(
            placeholder='Enter new address',
            cb=self.connect_client
        )


@DeviceManager.subscribe
class DeviceClient(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.log = logging.getLogger(__name__ + '.client')

        self.linked_devices = {}
        self.remote_devices = {}
        self.remote_profiles = []
        
        connect = QSettings().value('connect_on_startup', False)
        self.connect_on_startup = connect == 'true'

        self.current_connection = QSettings().value('current_connection', '10.0.0.207')
        self.previous_connections = [
            'ldg.hopto.org',
            'daelon.hopto.org',
            '10.0.0.207',
        ]
        
        self.commands = [
            Command('Device Client: Connect', self, triggered=self.connect_to_remote),
            Command('Device Client: Disconnect', self, triggered=self.disconnect_from_remote),
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

        new_device = profiles[profile](port=port)
        self.linked_devices[guid] = new_device
        self.signals.add_device.emit(new_device)

    def unlink_all_devices(self):
        for _, device in self.linked_devices.items():
            self.signals.remove_device.emit(device.guid)

        self.linked_devices = {}


@DeviceManager.subscribe
class DeviceServer(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.log = logging.getLogger(__name__ + '.server')

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