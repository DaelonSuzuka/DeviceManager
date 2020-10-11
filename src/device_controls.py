from qt import *
from device_manager import DeviceManager
from serial_monitor import SerialMonitorWidget
from command_palette import CommandPalette, Command


class DeviceTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, parent, device):
        super().__init__(parent)

        self.device = device
        self.guid = device.guid
        
        self.setText(0, device.profile_name)

        parts = device.port.split('link?')
        port = device.port if (len(parts) == 1) else parts[1]

        self.setText(1, port)


@DeviceManager.subscribe
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

        self.open_monitors = {}

    def device_added(self, device):
        if device.port[:5] == 'ws://':
            parent = self.remote_device_root
        else:
            parent = self.local_device_root

        self.nodes[device.guid] = DeviceTreeWidgetItem(parent, device)
        self.expandAll()

    def device_removed(self, guid):
        if guid in self.nodes:
            item = self.nodes[guid]
            parent = item.parent()
            index = parent.indexOfChild(item)
            parent.takeChild(index)

    def contextMenuEvent(self, event):
        pos = event.globalPos()
        item = self.itemAt(self.viewport().mapFromGlobal(pos))

        if item is self.local_device_root:
            menu = QMenu()
            menu.addAction(QAction('Add device', self))
            menu.addAction(QAction('Rescan ports', self))
            menu.addAction(QAction('Configure', self))
            menu.exec_(pos)

        if item is self.remote_device_root:
            menu = QMenu()
            menu.addAction(QAction('Add device', self))
            menu.addAction(QAction('Configure', self))
            menu.exec_(pos)

        if hasattr(item, 'device'):
            menu = QMenu()
            
            if hasattr(item.device, 'settings'):
                menu.addAction(QAction("Settings", self, triggered=lambda: self.open_settings(item)))

            if hasattr(item.device, 'widget'):
                menu.addAction(QAction("Open Device Controls", self, triggered=lambda: self.open_widget(item)))

            if hasattr(item.device, 'locate'):
                menu.addAction(QAction("Locate Device", self, triggered=item.device.locate))

            menu.addAction(QAction("Open Serial Monitor", self, triggered=lambda: self.open_monitor(item)))
            menu.addAction(QAction("Remove", self, triggered=lambda: self.remove_clicked(item)))
            menu.exec_(pos)

    def open_settings(self, item):
        if hasattr(item, 'device'):
            if hasattr(item.device, 'widget'):
                print('settings:', item.device.profile_name)

    def open_widget(self, item):
        if hasattr(item, 'device'):
            if hasattr(item.device, 'widget'):
                print('widget:', item.device.profile_name)

    def open_monitor(self, item):
        monitor = SerialMonitorWidget()
        monitor.setWindowTitle(item.device.title)
        item.device.connect_monitor(monitor)
        self.open_monitors[item.device.guid] = monitor
        monitor.show()

    def remove_clicked(self, item):
        if hasattr(item, 'device'):
            print('remove:', item.device.profile_name)


class DeviceControlsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        with CGridLayout(self) as grid:
            grid.addWidget(DeviceTree(self), 0, 0)


class DeviceControlsDockWidget(QDockWidget):
    def __init__(self, parent=None):
        super().__init__('Available Devices', parent=parent)
        self.setObjectName('DeviceControls')

        self.commands = [
            Command("Device List: Show device list", triggered=self._show, shortcut='Ctrl+D'),
            Command("Device List: Hide device list", triggered=self._hide),
        ]

        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)

        previous_location = QSettings().value('device_controls_location', Qt.RightDockWidgetArea)
        if previous_location == Qt.RightDockWidgetArea:
            self.starting_area = Qt.RightDockWidgetArea
        else:    
            self.starting_area = Qt.LeftDockWidgetArea
        self.dockLocationChanged.connect(lambda x: QSettings().setValue('device_controls_location', x))

        self.parent().addDockWidget(self.starting_area, self)

        self.closeEvent = lambda x: self._hide()
        if QSettings().value('device_controls_visible', 1) == 0:
            self.hide()

        self.setWidget(DeviceControlsWidget(self))

    def _show(self):
        self.show()
        QSettings().setValue('device_controls_visible', int(self.isVisible()))

    def _hide(self):
        self.hide()
        QSettings().setValue('device_controls_visible', int(self.isVisible()))

    def toggle_visibility(self):
        if self.isVisible():
            self._hide()
        else:
            self._show()

    def toggleViewAction(self):
        return QAction(
            'Available Devices', 
            self, 
            shortcut='Ctrl+D',
            checkable=True, 
            triggered=self.toggle_visibility
        )