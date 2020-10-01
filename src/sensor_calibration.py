from qt import *
from device_manager import DeviceManager
from device_widgets import *
from servitor import RadioInfo, MeterInfo
from dataclasses import dataclass


@dataclass
class Point:
    freq: str
    power: str
    meter_fwd: float = 0
    # meter_rev: float = 0
    # meter_swr: float = 0
    sensor_fwd: float = 0
    # sensor_rev: float = 0
    # sensor_swr: float = 0


@DeviceManager.subscribe
class CalibrationWorker(QObject):
    started = Signal()
    stopped = Signal()
    updated = Signal(int)
    finished = Signal(str)

    def __init__(self):
        super().__init__()

        self.devices = {}

        self.switch = None
        self.meter = None
        self.radio = None
        self.sensor = None

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.update())

        self.points = []
        self.current_point = 0

    def on_device_added(self, device):
        self.devices[device.guid] = device

    def on_device_removed(self, guid):
        self.devices.pop(guid)

    @Slot()
    def start(self, script):
        self.timer.start(200)

        self.points = []
        for freq in script['freqs']:
            for power in script['powers']:
                self.points.append(Point(freq, power))

        self.current_point = 0

        for _, device in self.devices.items():
            if device.profile_name == 'DTS-6':
                self.switch = device
                self.switch.set_antenna(1)
            if device.profile_name == 'TS-480':
                self.radio = device
            if device.profile_name == 'Alpha4510A':
                self.meter = device
                self.meter.signals.forward.connect(self.meter_forward)
            if device.profile_name == 'RFSensor':
                self.sensor = device
                self.sensor.signals.forward.connect(self.sensor_forward)

        self.started.emit()

    def meter_forward(self, forward):
        self.points[self.current_point].meter_fwd = forward

    def sensor_forward(self, forward):
        self.points[self.current_point].sensor_fwd = forward

    @Slot()
    def stop(self):
        self.timer.stop()

        self.switch = None
        self.meter = None
        self.radio = None
        self.sensor = None

        self.stopped.emit()

    def update(self):
        self.updated.emit(self.current_point)

        if self.current_point == len(self.points):
            self.stop()
            results = ''
            for p in self.points:
                results += str(p) + '\n'
            self.finished.emit(results)
            return

        self.radio.set_vfoA_frequency(int(self.points[self.current_point].freq))
        self.radio.set_power_level(int(self.points[self.current_point].power))

        self.current_point += 1


class CalibrationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet("""
            QWidget { font-size: 16pt; }
            QPushButton { 
                max-width: 2000px; 
                max-height: 2000px; 
            } 
        """)
        self.script = {
            'freqs': [
                "01800000",
                "03500000",
                "07000000",
                "10100000",
                # "14000000",
                # "18068000",
                # "21000000",
                # "24890000",
                # "28000000",
                # "50000000",
            ],
            'powers': [
                "005",
                "010",
                "015",
                "020",
                "025",
                "030",
                # "035",
                # "040",
                # "050",
                # "060",
                # "070",
                # "080",
                # "090",
                # "100",
            ]
        }
        
        self.thread = QThread()
        self.worker = CalibrationWorker()
        self.worker.moveToThread(self.thread)
        self.thread.start()
        self.worker.started.connect(self.worker_started)
        self.worker.stopped.connect(self.worker_stopped)

        self.start = QPushButton('start', clicked=self.start_worker)
        self.stop = QPushButton('stop', clicked=self.stop_worker, enabled=False)
        self.progress = QProgressBar()
        self.worker.updated.connect(self.progress.setValue)

        self.results = QTextEdit('')
        self.worker.finished.connect(self.results.setText)

        with CHBoxLayout(self) as layout:
            with CVBoxLayout(layout) as vbox:
                vbox.add(RadioInfo())
                vbox.add(HLine())
                vbox.add(MeterInfo())
                vbox.add(HLine())
                vbox.add(RFSensorWidget())
                vbox.add(QLabel(), 1)

            with CVBoxLayout(layout, 1) as vbox:
                with CHBoxLayout(vbox) as hbox:
                    hbox.add(self.start)
                    hbox.add(self.stop)
                vbox.add(self.progress)
                vbox.add(self.results, 1)

    def start_worker(self):
        self.worker.start(self.script)
        self.progress.setMaximum(len(self.script['freqs']) * len(self.script['powers']))

    def stop_worker(self):
        self.worker.stop()

    def worker_started(self):
        self.progress.setValue(0)
        self.start.setEnabled(False)
        self.stop.setEnabled(True)

    def worker_stopped(self):
        self.progress.setValue(0)
        self.start.setEnabled(True)
        self.stop.setEnabled(False)