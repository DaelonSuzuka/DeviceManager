from qtstrap import *
from codex import DeviceManager
from serial_monitor import SerialMonitorWidget


@DeviceManager.subscribe
class DiagnosticApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QPushButton { 
                max-width: 2000px; 
                max-height: 2000px; 
            } 
        """)

        self.tab_name = 'Diagnostics'

        self.device_box = QComboBox(placeholderText="Select a device:")
        self.connect = QPushButton("Connect", clicked=self.connect_clicked)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.cloae_tab)

        with CHBoxLayout(self) as layout:
            with layout.vbox(1):
                with layout.hbox():
                    layout.add(self.device_box, 1)
                    layout.add(self.connect)
                layout.add(self.tabs)

    def connect_clicked(self):
        guid = self.device_box.itemData(self.device_box.currentIndex())
        device = self.devices[guid]
        if device is not None:
            monitor = SerialMonitorWidget(self.tabs)
            device.connect_monitor(monitor)
            self.tabs.addTab(monitor, f'{device.profile_name} <{device.port.split("?")[-1]}>')

    def cloae_tab(self, index):
        self.tabs.widget(index).deleteLater()
        self.tabs.removeTab(index)
    
    def device_added(self, device):
        self.device_box.addItem(device.title, userData=device.guid)

    def device_removed(self, guid):
        for index in range(self.device_box.count()):
            if self.device_box.itemData(index) == guid:
                self.device_box.removeItem(index)