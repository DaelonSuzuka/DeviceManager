from qt import *
from devices import DeviceManager


@DeviceManager.subscribe
class TunerMonApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.tab_name = 'Tuner Monitor'

        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('tunerlog')
        db.open()
        # db.exec_(initial_sql)

        self.device_box = QComboBox(placeholderText="Select a device:")
        self.connect = QPushButton("Connect")

        with CHBoxLayout(self) as layout:
            with layout.vbox(1):
                with layout.hbox():
                    layout.add(self.device_box, 1)
                    layout.add(self.connect)

    def device_added(self, device):
        self.device_box.addItem(device.title, userData=device.guid)

    def device_removed(self, guid):
        for index in range(self.device_box.count()):
            if self.device_box.itemData(index) == guid:
                self.device_box.removeItem(index)