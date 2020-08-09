from qt import *
from devices import SerialDevice, profiles, profile_names
from serial.tools.list_ports import comports
from bundles import SigBundle, SlotBundle


class DeviceTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, parent, device):
        super().__init__(parent)

        self.device = device
        
        self.setText(0, device.profile_name)

        parts = device.port.split('link?')
        port = device.port if (len(parts) == 1) else parts[1]

        self.setText(1, port)


class DeviceTree(QTreeWidget):
    widget_requested = Signal(object)
    settings_requested = Signal(object)
    remove_requested = Signal(object)

    def __init__(self):
        super().__init__()
        self.setUniformRowHeights(True)
        self.setExpandsOnDoubleClick(False)
        self.setItemsExpandable(False)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setColumnCount(2)
        self.setColumnWidth(0,150)
        self.setHeaderLabels(['Name', 'Port'])
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.nodes = {}
        self.local_device_root = QTreeWidgetItem(self)
        self.local_device_root.setText(0, "Local Devices")
        self.remote_device_root = QTreeWidgetItem(self)
        self.remote_device_root.setText(0, "Remote Devices")

    def add_device(self, device):
        if device.port[:5] == 'ws://':
            parent = self.remote_device_root
        else:
            parent = self.local_device_root

        self.nodes[device.guid] = DeviceTreeWidgetItem(parent, device)
        self.expandAll()

    def remove_device(self, guid):
        if guid in self.nodes:
            item = self.nodes[guid]
            parent = item.parent()
            index = parent.indexOfChild(item)
            parent.takeChild(index)
        
    def contextMenuEvent(self, event):
        pos = event.globalPos()
        item = self.itemAt(self.viewport().mapFromGlobal(pos))

        menu = QMenu()
        menu.addAction(QAction("Settings", self, triggered=lambda: self.open_settings(pos)))
        menu.addAction(QAction("Widget", self, triggered=lambda: self.open_widget(pos)))
        menu.addAction(QAction("Remove", self, triggered=lambda: self.remove_clicked(pos)))
        print(menu.exec_(event.globalPos()))

    def open_settings(self, pos):
        item = self.itemAt(self.viewport().mapFromGlobal(pos))
        if hasattr(item, 'device'):
            print('settings:', item.device.profile_name)

    def open_widget(self, pos):
        item = self.itemAt(self.viewport().mapFromGlobal(pos))
        if hasattr(item, 'device'):
            if hasattr(item.device, 'widget'):
                print('widget:', item.device.profile_name)

    def remove_clicked(self, pos):
        item = self.itemAt(self.viewport().mapFromGlobal(pos))
        if hasattr(item, 'device'):
            print('remove:', item.device.profile_name)


class DeviceCreatorPanel(QWidget):
    def __init__(self):
        super().__init__()
        ports = ["DummyPort", "RemoteSerial", *[port.device for port in sorted(comports())]]
        self.profile = ComboBox(items=profile_names)
        self.port = ComboBox(editable=True, items=ports)
        self.add = QPushButton("Add")
        
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)

        grid.addWidget(QLabel("Available Profiles:"), 4, 0, 1, 3)
        grid.addWidget(self.profile, 5, 0, 1, 3)
        grid.addWidget(self.port, 6, 0, 1, 2)
        grid.addWidget(self.add, 6, 2)
        self.setLayout(grid)


class DeviceControls(QDockWidget):
    def __init__(self, client):
        super().__init__('Available Devices:')
        self.setObjectName('DeviceControls')
        self.signals = SigBundle({'add_device':[SerialDevice], 'remove_device': [str]})
        self.slots = SlotBundle({'device_added':[SerialDevice], 'device_removed': [str]})
        self.slots.link_to(self)

        self.client = client

        self.devices = {}
        self.widgets = {}

        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.starting_area = Qt.RightDockWidgetArea
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)
        self.closeEvent = lambda x: self.hide()
        self.dockLocationChanged.connect(lambda: QTimer.singleShot(0, self.adjust_size))

        self.device_tree = DeviceTree()

        self.setStyleSheet("""
            QPushButton { font-size: 10pt; } 
            QLabel { font-size: 10pt; } 
            QLineEdit { font-size: 10pt; } 
            QComboBox { font-size: 10pt; } 
            QListItem { font-size: 10pt; }
            DeviceListWidget { font-size: 10pt; }
        """)

        grid = QGridLayout()
        grid.addWidget(self.device_tree, 0, 0)
        self.setWidget(QWidget(layout=grid))

    def adjust_size(self):
        if self.isFloating():
            self.adjustSize()

    def toggleViewAction(self):
        action = super().toggleViewAction()
        action.setShortcut("Ctrl+D")
        return action

    def show_device_widget(self):
        for item in self.device_list.selectedItems():
            if hasattr(self.devices[item.guid], 'widget'):
                if item.guid not in self.widgets:
                    widget = self.devices[item.guid].widget
                    if isinstance(widget, QDockWidget):
                        widget.setParent(self.parent())
                        self.widgets[item.guid] = widget
                        # widget.setFloating(True)
                        # widget.show()
                        # self.parent().addDockWidget(widget)
                        
                        self.parent().addDockWidget(widget.starting_area, widget)

    def on_device_added(self, device):
        self.device_tree.add_device(device)
        self.devices[device.guid] = device

    def on_device_removed(self, guid):
        self.device_tree.remove_device(guid)
        self.devices.pop(guid)

        if guid in self.widgets:
            self.widgets[guid].deleteLater()
            self.widgets.pop(guid)