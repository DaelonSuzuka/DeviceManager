from qt import *
from device_manager import DeviceManager
from serial_monitor import SerialMonitorWidget
from servitor import KeyButton, RadioInfo, MeterInfo


@DeviceManager.subscribe
class DiagnosticWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QPushButton { 
                max-width: 2000px; 
                max-height: 2000px; 
            } 
        """)
        self.devices = {}
        self.device_box = QComboBox(placeholderText="Select a device:")
        self.connect = QPushButton("Connect", clicked=self.connect_clicked)
        self.tabs = QTabWidget()

        with CHBoxLayout(self) as layout:
            with CVBoxLayout(layout, 1) as left_side:
                with CHBoxLayout(left_side) as row_1:
                    row_1.addWidget(QPushButton())
                    row_1.addWidget(QPushButton())
                    row_1.addWidget(QPushButton())
                    row_1.addWidget(KeyButton())
                # with CHBoxLayout(left_side) as row_2:
                #     row_2.addWidget(QPushButton())
                #     row_2.addWidget(QPushButton())
                #     row_2.addWidget(QPushButton())
                #     row_2.addWidget(QPushButton())
                left_side.addWidget(RadioInfo())
                left_side.addWidget(MeterInfo())
                left_side.addStretch(1)

            with CVBoxLayout(layout, 1) as right_side:
                with CHBoxLayout(right_side) as row_1:
                    row_1.addWidget(self.device_box, 1)
                    row_1.addWidget(self.connect)
                right_side.addWidget(self.tabs)

    def connect_clicked(self):
        guid = self.device_box.itemData(self.device_box.currentIndex())
        device = self.devices[guid]
        if device is not None:
            monitor = SerialMonitorWidget(rows=50)
            device.connect_monitor(monitor)
            self.tabs.addTab(monitor, f'{device.profile_name} <{device.port.split("?")[-1]}>')
    
    def on_device_added(self, device):
        if device.guid not in self.devices:
            self.devices[device.guid] = device
            self.device_box.addItem(device.title, userData=device.guid)

    def on_device_removed(self, guid):
        if guid in self.devices:
            for index in range(self.device_box.count()):
                if self.device_box.itemData(index) == guid:
                    self.device_box.removeItem(index)
            self.devices.pop(guid)