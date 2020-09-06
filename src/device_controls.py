from qt import *
from device_manager import DeviceManager
from serial_monitor import SerialMonitorWidget


class DeviceTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, parent, device):
        super().__init__(parent)

        self.device = device
        self.guid = device.guid
        
        self.setText(0, device.profile_name)

        parts = device.port.split('link?')
        port = device.port if (len(parts) == 1) else parts[1]

        self.setText(1, port)


class DeviceTree(QTreeWidget):
    widget_requested = Signal(object)
    settings_requested = Signal(object)
    remove_requested = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
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

    def add_node(self, device):
        if device.port[:5] == 'ws://':
            parent = self.remote_device_root
        else:
            parent = self.local_device_root

        self.nodes[device.guid] = DeviceTreeWidgetItem(parent, device)
        self.expandAll()

    def remove_node(self, guid):
        if guid in self.nodes:
            item = self.nodes[guid]
            parent = item.parent()
            index = parent.indexOfChild(item)
            parent.takeChild(index)

    def contextMenuEvent(self, event):
        pos = event.globalPos()
        item = self.itemAt(self.viewport().mapFromGlobal(pos))

        if hasattr(item, 'device'):
            menu = QMenu()
            menu.addAction(QAction("Settings", self, triggered=lambda: self.open_settings(item)))

            if hasattr(item.device, 'widget'):
                menu.addAction(QAction("Show Control Widget", self, triggered=lambda: self.open_widget(item)))

            if hasattr(item.device, 'locate'):
                menu.addAction(QAction("Locate Device", self, triggered=item.device.locate))

            menu.addAction(QAction("Open Serial Monitor", self, triggered=lambda: self.open_monitor(item)))
            menu.addAction(QAction("Remove", self, triggered=lambda: self.remove_clicked(item)))
            menu.exec_(pos)

    def open_settings(self, item):
        if hasattr(item, 'device'):
            print('settings:', item.device.profile_name)

    def open_widget(self, item):
        if hasattr(item, 'device'):
            if hasattr(item.device, 'widget'):
                self.parent().show_device_widget(item)

    def open_monitor(self, item):
        monitor = SerialMonitorWidget()
        monitor.setWindowTitle(item.device.title)
        item.device.connect_monitor(monitor)
        monitor.show()

    def remove_clicked(self, item):
        if hasattr(item, 'device'):
            print('remove:', item.device.profile_name)


@DeviceManager.subscribe
class DeviceControlsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('DeviceControls')

        self.devices = {}
        self.widgets = {}

        self.device_tree = DeviceTree(self)

        grid = QGridLayout(self)
        grid.addWidget(self.device_tree, 0, 0)

    def show_device_widget(self, item):
        if hasattr(self.devices[item.guid], 'widget'):
            if item.guid not in self.widgets:
                widget = self.devices[item.guid].widget
                if isinstance(widget, QDockWidget):
                    widget.setParent(self.parent().parent())
                    self.widgets[item.guid] = widget
                    self.parent().parent().addDockWidget(widget.starting_area, widget)

    def on_device_added(self, device):
        if device.guid not in self.devices:
            self.device_tree.add_node(device)
            self.devices[device.guid] = device

    def on_device_removed(self, guid):
        if guid in self.devices:
            self.devices.pop(guid)
            self.device_tree.remove_node(guid)

        if guid in self.widgets:
            self.widgets[guid].deleteLater()
            self.widgets.pop(guid)


class DeviceControlsDockWidget(QDockWidget):
    def __init__(self, parent=None):
        super().__init__('Available Devices:', parent=parent)
        self.setObjectName('DeviceControls')

        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.starting_area = Qt.RightDockWidgetArea
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)
        self.closeEvent = lambda x: self.hide()
        self.dockLocationChanged.connect(lambda: QTimer.singleShot(0, self.adjust_size))

        self.parent().addDockWidget(self.starting_area, self)
        # self.hide()

        self.setWidget(DeviceControlsWidget(self))

    def adjust_size(self):
        if self.isFloating():
            self.adjustSize()

    def toggleViewAction(self):
        action = super().toggleViewAction()
        action.setShortcut("Ctrl+D")
        return action