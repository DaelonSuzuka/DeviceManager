from qt import *
from codex import DeviceManager
import appdirs
from pathlib import Path
from queue import Queue
import pyqtgraph as pg


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

        self.events = []
        self.plot_layout = pg.GraphicsLayoutWidget()
        title = 'Tuning Data'
        labels = {'bottom':'Caps', 'left':'Inds'}
        self.plot = self.plot_layout.addPlot(title=title, labels=labels)

        self.device_box = QComboBox(placeholderText="Select a device:")
        self.connect = QPushButton("Connect", clicked=self.connect_pressed)

        with CHBoxLayout(self) as layout:
            with layout.vbox(1):
                with layout.hbox():
                    layout.add(self.device_box, 1)
                    layout.add(self.connect)
                layout.add(self.plot_layout)

    def update_plot(self):
        x = []
        y = []

        for e in self.events:
            if 'match' in e:
                if e['match']['relays']['z']:
                    x.append(e['match']['relays']['caps'])
                else:
                    x.append(-e['match']['relays']['caps'])
                y.append(e['match']['relays']['inds'])

        self.plot.plot(x, y)             

    def event_received(self, msg):
        if msg['event'] == 'tune_start':
            self.events = []
            # self.plot_layout.clear()
            # self.plot.plot([0, 132], [0, 0])

        self.events.append(msg)
        self.update_plot()

    def connect_pressed(self):
        guid = self.device_box.currentData()
        if guid in self.devices:
            self.devices[guid].signals.event.connect(self.event_received)

    def device_added(self, device):
        self.device_box.addItem(device.title, userData=device.guid)

        if device.profile_name == 'Z-100Plus':
            device.signals.event.connect(self.event_received)

    def device_removed(self, guid):
        for index in range(self.device_box.count()):
            if self.device_box.itemData(index) == guid:
                self.device_box.removeItem(index)