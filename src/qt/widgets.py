from .qt import *

class ComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        # allow adding items to ComboBox at construction
        if 'items' in kwargs:
            items = kwargs.pop('items')

        super().__init__(*args, **kwargs)

        if 'items' in locals():
            self.addItems(items)

    @property
    def current(self):
        return self.currentText()

class DeviceListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.menu = QMenu()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda: self.menu.exec_(QCursor.pos()))

    def add_device(self, device):
        if isinstance(device, dict):
            item = QListWidgetItem(device['title'])
            item.port = device['port'] 
            item.guid = device['guid']
            item.title = device['title']
            item.profile_name = device['profile_name']
        else:
            item = QListWidgetItem(device.title)
            item.port = device.port 
            item.guid = device.guid
            item.title = device.title
            item.profile_name = device.profile_name

        self.addItem(item)

    def add_devices(self, devices):
        for device in devices:
            self.add_device(device)

    def remove_item(self, string):
        for item in self.findItems(string, Qt.MatchExactly):
            self.takeItem(self.row(item))

    def get_item(self, key="", value=""):
        for i in range(self.count()):
            item = self.item(i)
            if hasattr(item, key):
                if getattr(item, key) == value:
                    return item

    def remove_item_by_guid(self, guid):
        for i in range(self.count()):
            if self.item(i).guid == guid:
                self.takeItem(i)
                # TODO: AttributeError: 'NoneType' object has no attribute 'guid'

    def deselect_all(self):
        for i in range(self.count()):
            item = self.item(i).setSelected(False)


class CustomList(QListWidget):
    def remove_item(self, string):
        for item in self.findItems(string, Qt.MatchExactly):
            self.takeItem(self.row(item))

    def deselect_all(self):
        for item in self.selectedItems():
            item.setSelected(False)

class GroupBox(QGroupBox):
    def __init__(self, *args, **kwargs):
        if 'widget' in kwargs:
            widget = kwargs.pop('widget')

        super().__init__(*args, **kwargs)

        if 'widget' in locals():
            grid = QGridLayout()
            grid.addWidget(widget)
            self.setLayout(grid)


class Widget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_widgets()
        self.connect_signals()
        self.build_layout()

    def create_widgets(self):
        pass

    def connect_signals(self):
        pass

    def build_layout(self):
        pass


