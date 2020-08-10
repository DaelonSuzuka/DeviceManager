from re import sub
from qt import *
from devices import SerialDevice, profiles
from device_manager import DeviceManager
import time
import logging
import json
from serial.tools.list_ports import comports
from bundles import SigBundle, SlotBundle
from settings import Settings
import typing
from urllib.parse import urlparse
import qtawesome as qta
from command_palette import CommandPalette


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


class Settings(Settings):
    connect_on_startup: bool = False
    address: str = '73.86.101.13'
    port: int = 43000
    previous_connections: typing.List[str] = [
        '10.0.0.207',
        '73.86.101.13',
        '127.0.0.1'
    ]
    link_on_connect: typing.List[str] = [
        'TS-480',
        'Alpha4510A',
        'VariableCapacitor',
        'VariableInductor',
        'DTS-4',
    ]


settings = Settings().register('Client')


class StatusBarWidget(QWidget):
    open_socket = Signal()
    close_socket = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName('NetworkStatusBarItem')
        
        self.setAttribute(Qt.WA_AcceptTouchEvents, True)
    
        self.status = QLabel('Not Connected')
        self.address = QLabel(settings.address())
        self.icon_on = qta.icon('mdi.lan-connect', color='lightgray').pixmap(QSize(20, 20))
        self.icon_off = qta.icon('mdi.lan-disconnect', color='gray').pixmap(QSize(20, 20))
        self.icon = QLabel('')
        self.icon.setPixmap(self.icon_off)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.icon)
        hbox.addWidget(QLabel('Status:'))
        hbox.addWidget(self.status)
        hbox.addWidget(self.address)
        self.setLayout(hbox)
        
        self.act_connect = QAction("Connect", self, triggered=self.open)
        self.act_disconnect = QAction("Disconnect", self, triggered=self.close)
        self.act_startup = QAction("Connect at Startup", self, checkable=True, triggered=self.startup)
        self.act_startup.setChecked(settings.connect_on_startup())
        self.act_address = QAction("Set Address", self, triggered=self.set_address)
        self.act_settings = QAction("Network Settings", self, triggered=lambda: print('Settings'))

        menu = QMenu()
        menu.addAction(self.act_connect)
        menu.addAction(self.act_disconnect)
        settings_menu = QMenu('Settings')
        settings_menu.addAction(self.act_startup)
        settings_menu.addAction(self.act_address)
        settings_menu.addAction(self.act_settings)
        menu.addMenu(settings_menu)
        self.menu = menu

        CommandPalette().register_action('Set Address', self.set_address)

    #     self.installEventFilter(self)

    # def eventFilter(self, watched: PySide2.QtCore.QObject, event: PySide2.QtCore.QEvent) -> bool:
    #     types = [ QEvent.TouchBegin, QEvent.TouchCancel, QEvent.TouchEnd, QEvent.TouchUpdate ]

    #     if event.type() in types:
    #         if event.type() in [QEvent.TouchBegin, QEvent.TouchUpdate]:
    #             event.accept()
    #             return True
    #         elif event.type() == QEvent.TouchEnd:
    #             event.accept()
    #             pos = event.touchPoints()[0].screenPos().toPoint()
    #             print(pos)
    #             self.menu.exec_(pos)
    #             return True

    #     return super().eventFilter(watched, event)

    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())

    def socket_connected(self):
        self.status.setText("Connected")
        self.icon.setPixmap(self.icon_on)

    def socket_disconnected(self):
        self.status.setText("Not Connected")
        self.icon.setPixmap(self.icon_off)

    def open(self):
        self.status.setText("Connecting...")
        self.open_socket.emit()

    def close(self):
        self.close_socket.emit()

    def startup(self):
        settings.connect_on_startup = self.act_startup.isChecked()

    def set_address(self):
        oct = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        regexp = QRegExp(f"^{oct}\\.{oct}\\.{oct}\\.{oct}$")
        CommandPalette().open(
            placeholder='Enter a new IP Address',
            cb=self.address_result,
            # mask='000.000.000.000; ',
            validator=QRegExpValidator(regexp)
        )

    def address_result(self, result):
        self.address.setText(result)


@DeviceManager.subscribe
class DeviceClient(QObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings
        self.log = logging.getLogger(__name__)

        self.devices = {}
        self.linked_devices = {}
        self.remote_devices = {}
        self.remote_profiles = []

        self.socket = QWebSocket()
        self.socket.connected.connect(lambda: self.log.info("Connected to server"))
        self.socket.textMessageReceived.connect(self.process_message)

        self.socket.disconnected.connect(self.unlink_all_devices)
        
        self.status_widget = StatusBarWidget()
        self.socket.connected.connect(self.status_widget.socket_connected)
        self.socket.disconnected.connect(self.status_widget.socket_disconnected)
        self.status_widget.open_socket.connect(self.open_socket)
        self.status_widget.close_socket.connect(self.close_socket)

    def on_subscribed(self):
        if self.settings.connect_on_startup():
            if urlparse(self.settings.address()).path != urlparse(get_ip()).path:
                self.open_socket()

    def on_device_added(self, device):
        self.devices[device.guid] = device

        if device.port == "RemoteSerial":
            for k in self.remote_devices.keys():
                if device.profile_name == self.remote_devices[k]['profile_name']:
                    print("found")

    def on_device_removed(self, guid):
        self.devices.pop(guid)

    def open_socket(self):
        url = f'ws://{self.settings.address()}:{self.settings.port()}/control'
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

        if 'profiles' in msg.keys():
            profiles = sorted(msg["profiles"])
            self.remote_profiles = profiles

        if 'port' in msg.keys():
            port = msg["port"]
            self.controls.port_box.addItem(port)

        if 'ports' in msg.keys():
            ports = msg["ports"]
        
        if 'device_added' in msg.keys():
            device = msg["device_added"]

            self.remote_devices[device['guid']] = device
            self.link_to_remote_device(self.settings.address, device['guid'])

        if 'device_removed' in msg.keys():
            device = msg["device_removed"]

            self.remote_devices.pop(device['guid'])

        if 'devices' in msg.keys():
            devices = msg["devices"]

            self.remote_devices = {d['guid']:d for d in devices}
            for device in devices:
                self.link_to_remote_device(self.settings.address, device['guid'])

    def link_to_remote_device(self, url, guid):
        device = self.remote_devices[guid]
        address = f'{url}:{self.settings.port}'

        port = f"RemoteSerial:{address}/link?{device['port']}"
        profile = device['profile_name']

        new_device = profiles[profile](port=port)
        self.linked_devices[guid] = new_device
        self.signals.add_device.emit(new_device)

    def unlink_all_devices(self):
        for _, device in self.linked_devices.items():
            self.signals.remove_device.emit(device.guid)