from qt import *
from bundles import SigBundle, SlotBundle


class Worker(QObject):
    def __init__(self):
        super().__init__()
        signals = {
            'started': [], 
            'stopped': [], 
            'updated': [int]
        }
        slots = {
            'start': [], 
            'stop': [], 
            'reset': []
        }

        self.signals = SigBundle(signals)
        self.slots = SlotBundle(slots)

        self.slots.link_to(self)
        self.slots.link('start', self.start)
        self.count = 0

    def start(self):
        print('starting')
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.update())
        self.timer.start(1000)

    def on_stop(self):
        self.timer.stop()

    def on_reset(self):
        self.count = 0
        self.signals.updated.emit(self.count)

    def update(self):
        print(self.count)
        self.count += 1
        self.signals.updated.emit(self.count)


class WorkerControls(QDockWidget):
    def __init__(self):
        super().__init__('Worker Controls')
        self.setObjectName('WorkerControls')
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.start()

        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.starting_area = Qt.RightDockWidgetArea
        self.closeEvent = lambda x: self.hide()
        self.dockLocationChanged.connect(self.adjustSize)

        self.create_widgets()
        self.connect_signals()
        self.build_layout()

    def create_widgets(self):
        self.count = QLabel("?")
        self.start = QPushButton("start")
        self.stop = QPushButton("stop")
        self.reset = QPushButton("reset")

    def connect_signals(self):
        self.worker.signals.updated.connect(lambda i: self.count.setText(str(i)))
        self.start.clicked.connect(self.worker.slots.start)
        self.stop.clicked.connect(self.worker.slots.stop)
        self.reset.clicked.connect(self.worker.slots.reset)

    def build_layout(self):
        self.setStyleSheet("""
            QPushButton { font-size: 10pt; } 
            QLabel { font-size: 10pt; } 
            QLineEdit { font-size: 10pt; } 
            QComboBox { font-size: 10pt; } 
            QListItem { font-size: 10pt; }
            DeviceListWidget { font-size: 10pt; }
        """)
        grid = QGridLayout()
        grid.setContentsMargins(0, 10, 0, 10)
        grid.setColumnStretch(2, 1)

        grid.addWidget(QLabel("multi-thread signal/slot connection example"), 0, 0, 1, 6)
        grid.addWidget(QLabel("count:"), 1, 0)
        grid.addWidget(self.count, 1, 1)
        grid.addWidget(self.start, 1, 3)
        grid.addWidget(self.stop, 1, 4)
        grid.addWidget(self.reset, 1, 5)

        self.setWidget(QWidget(layout=grid))