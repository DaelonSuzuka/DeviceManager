from qt import *
from devices import DeviceManager
import appdirs
from pathlib import Path
from queue import Queue

ex = {
    "event":"match_tested",
    "time":3685169,
    "match":{
        "#":164,
        "relays":{
            "caps":18,
            "inds":5,
            "z":1
        },
        "rf":{
            "fwd":1152.97,
            "rev":1655.31,
            "swr":5880.61
        }
    }
}


initial_sql = """
CREATE TABLE IF NOT EXISTS tuner(
    DateTime TEXT,
    EventType TEXT,
    Time INT,
    MatchNumber INT,
    caps INT,
    inds INT,
    z INT,
    fwd FLOAT,
    rev FLOAT,
    swr FLOAT,
)
"""


@DeviceManager.subscribe
class TunerMonApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.tab_name = 'Tuner Monitor'
        
        # db_path = appdirs.user_data_dir("Device Manager", "LDG Electronics")
        # Path(db_path).mkdir(parents=True, exist_ok=True)
        # db_name = db_path + '/tuner.db'

        # db = QSqlDatabase.addDatabase('QSQLITE', 'tuner')
        # db.setDatabaseName(db_name)
        # db.open()

        # db.exec_(initial_sql)

        self.events = Queue()

        self.device_box = QComboBox(placeholderText="Select a device:")
        self.connect = QPushButton("Connect", clicked=self.connect_pressed)

        with CHBoxLayout(self) as layout:
            with layout.vbox(1):
                with layout.hbox():
                    layout.add(self.device_box, 1)
                    layout.add(self.connect)

    def event_recieved(self, msg):
        if msg['event'] == 'tune_start':
            self.events.clear()

        self.events.put(msg)

    def connect_pressed(self):
        guid = self.device_box.currentData()
        if guid in self.devices:
            self.devices[guid].signals.event.connect(self.event_recieved)

    def device_added(self, device):
        self.device_box.addItem(device.title, userData=device.guid)

    def device_removed(self, guid):
        for index in range(self.device_box.count()):
            if self.device_box.itemData(index) == guid:
                self.device_box.removeItem(index)