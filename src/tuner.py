from qt import *
from device_manager import DeviceManager
from bundles import SigBundle, SlotBundle


class TuningWorker(QObject):
    def __init__(self):
        super().__init__()
        signals = {
            'started': [], 
            'stopped': [list], 
        }
        slots = {
            'start': [object, object, object], 
            'stop': [],
            'recieve': [dict],
        }

        self.signals = SigBundle(signals)
        self.slots = SlotBundle(slots, link_to=self)

        self.history = {}
        self.plan = []
        
        self.caps = None
        self.inds = None
        self.sensor = None
        self.prev = None
        self.index = 0

    def on_start(self, caps, inds, sensor):
        self.caps = caps
        self.inds = inds
        self.sensor = sensor
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.update())
        self.timer.start(100)
        
        self.caps.set_caps(0) 
        self.inds.set_inds(0)
        self.caps.set_input_relay(True)
        self.caps.set_output_relay(False)
        self.inds.set_input_relay(True)
        self.inds.set_output_relay(True)

        self.step = 5
        self.index = 0
        self.prev = None
        
        self.history = {}
        self.plan = []
        self.last_results = {}

        for C in range(0, self.caps.max_caps, self.step):
            for L in range(0, self.inds.max_inds, self.step):
                self.plan.append((C, L))

    def on_stop(self):
        self.timer.stop()
        self.signals.stopped.emit(self.history)

    def update(self):
        if self.prev:
            self.history[self.prev] = str(self.last_results)

        try:
            C, L = self.plan[self.index]
            self.index += 1

            self.caps.set_caps(C) 
            self.inds.set_inds(L)

            self.prev = (C, L)
        except IndexError:
            pass

    def on_recieve(self, results):
        self.last_results = results


@DeviceManager.subscribe
class Tuner(QObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.caps = None
        self.inds = None
        self.sensor = None

        self.thread = QThread()
        self.worker = TuningWorker()
        self.worker.moveToThread(self.thread)
        self.thread.start()
        self.worker.signals.stopped.connect(self.on_tuning_stopped)

        self.history = {}

        self.loop = QtCore.QEventLoop()

        self.controls = TunerControls()
        self.controls.tune.clicked.connect(self.begin_tuning)
        self.controls.stop.clicked.connect(self.stop_tuning)
        self.controls.stop.clicked.connect(self.loop.quit)

    def begin_tuning(self):
        self.sensor.signals.update.connect(self.worker.slots.recieve)
        self.worker.slots.start(self.caps, self.inds, self.sensor)
        
        self.controls.cup.setEnabled(False)
        self.controls.cdn.setEnabled(False)
        self.controls.lup.setEnabled(False)
        self.controls.ldn.setEnabled(False)

    def stop_tuning(self):        
        self.worker.slots.stop()

        self.controls.cup.setEnabled(True)
        self.controls.cdn.setEnabled(True)
        self.controls.lup.setEnabled(True)
        self.controls.ldn.setEnabled(True)

    def on_tuning_stopped(self, results):
        string = '\n'.join([f'{k}: {v}' for k, v in results.items()])
        text = QTextEdit(text=string)
        layout=QVBoxLayout()
        layout.addWidget(text)
        self.dialog = QDialog(layout=layout)
        self.dialog.setMinimumSize(1000, 1000)
        self.dialog.show()

    def on_device_added(self, device):
        if device.profile_name == "VariableCapacitor":
            if self.caps is None:
                self.caps = device
                self.controls.cup.setEnabled(True)
                self.controls.cdn.setEnabled(True)
                self.controls.cup.clicked.connect(self.caps.relays_cup)
                self.controls.cdn.clicked.connect(self.caps.relays_cdn)

        if device.profile_name == "VariableInductor":
            if self.inds is None:
                self.inds = device
                self.controls.lup.setEnabled(True)
                self.controls.ldn.setEnabled(True)
                self.controls.lup.clicked.connect(self.inds.relays_lup)
                self.controls.ldn.clicked.connect(self.inds.relays_ldn)

        if device.profile_name == "Alpha4510A":
            if self.sensor is None:
                self.sensor = device

    def on_device_removed(self, guid):
        if self.caps and self.caps.guid == guid:
            self.caps = None
            self.controls.cup.setEnabled(False)
            self.controls.cdn.setEnabled(False)

        if self.inds and self.inds.guid == guid:
            self.inds = None
            self.controls.lup.setEnabled(False)
            self.controls.ldn.setEnabled(False)

        if self.sensor and self.sensor.guid == guid:
            self.sensor = None
            

class TunerControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        self.setStyleSheet("""
            QPushButton { 
                font-size: 16pt; 
                min-height: 100px; 
                max-height: 200px; 
                min-width: 100px; 
                max-width: 200px; 
            } 
        """)
        
        self.create_widgets()
        self.connect_signals()
        self.build_layout()

    def create_widgets(self):
        self.tune = QPushButton("Tune")
        self.reset = QPushButton("Reset")
        self.stop = QPushButton("Stop", enabled=False)
        self.cup = QPushButton("C Up", enabled=False)
        self.cdn = QPushButton("C Dn", enabled=False)
        self.lup = QPushButton("L Up", enabled=False)
        self.ldn = QPushButton("L Dn", enabled=False)

    def connect_signals(self):
        self.tune.clicked.connect(self.tune_clicked)
        self.stop.clicked.connect(self.stop_clicked)

    def build_layout(self):
        layout = QHBoxLayout(self, margins=(10, 10, 10, 10), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        layout.addWidget(self.cup)
        layout.addWidget(self.cdn)
        layout.addWidget(self.lup)
        layout.addWidget(self.ldn)
        layout.addWidget(self.tune)
        layout.addWidget(self.stop)

    def tune_clicked(self):
        self.tune.setEnabled(False)
        self.stop.setEnabled(True)

    def stop_clicked(self):
        self.stop.setEnabled(False)
        self.tune.setEnabled(True)