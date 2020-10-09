from qt import *
from device_manager import DeviceManager
from plugins.widgets import *
from dataclasses import dataclass
from collections import deque  
import numpy as np


@dataclass
class Point:
    freq: str
    power: str


@dataclass
class Result:
    freq: str = ''
    power: str = ''

    meter_fwd: float = 0
    meter_rev: float = 0
    meter_swr: float = 0
    sensor_fwd: float = 0
    sensor_rev: float = 0
    sensor_swr: float = 0

    def __repr__(self):
        return f'({self.freq:8}, {self.power:3})meter: [F: {self.meter_fwd:6.2f}, R: {self.meter_rev:6.2f}, S: {self.meter_swr:6.2f}] sensor: [F: {self.sensor_fwd:8.2f}, R: {self.sensor_rev:8.2f}, S: {self.sensor_swr:8.2f}]'


class DataQueue:
    def __init__(self, keys, maxlen=10):
        self._data = {}

        for key in keys:
            self._data[key] = deque(maxlen=maxlen)

    def __getitem__(self, key):
        return self._data[key]

    def clear(self):
        for _, queue in self._data.items():
            queue.clear()

    def is_ready(self):
        for _, queue in self._data.items():
            if len(queue) != queue.maxlen:
                return False
        return True


@DeviceManager.subscribe
class CalibrationWorker(QObject):
    started = Signal()
    stopped = Signal()
    updated = Signal(int)
    finished = Signal(list)

    def __init__(self):
        super().__init__()

        self.switch = None
        self.meter = None
        self.radio = None
        self.sensor = None

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.update())

        self.points = []
        self.current_point = 0
        self.results = []

        self.num_of_samples = 10
        self.data = DataQueue(['m_fwd', 'm_rev', 'm_swr', 's_fwd', 's_rev', 's_swr'], maxlen=self.num_of_samples)

    def calculate_result(self) -> Result:
        result = Result()
        result.freq = self.points[self.current_point].freq
        result.power = self.points[self.current_point].power
        result.meter_fwd = sum(self.data['m_fwd']) / self.num_of_samples
        result.meter_rev = sum(self.data['m_rev']) / self.num_of_samples
        result.meter_swr = sum(self.data['m_swr']) / self.num_of_samples
        result.sensor_fwd = sum(self.data['s_fwd']) / self.num_of_samples
        result.sensor_rev = sum(self.data['s_rev']) / self.num_of_samples
        result.sensor_swr = sum(self.data['s_swr']) / self.num_of_samples

        return result

    @Slot()
    def start(self, script):
        self.timer.start(50)

        self.points = []
        self.results = []

        for freq in script['freqs']:
            for power in script['powers']:
                self.points.append(Point(freq, power))

        print(len(self.points))

        self.current_point = 0

        for _, device in self.devices.items():
            if device.profile_name == 'DTS-6':
                self.switch = device
            if device.profile_name == 'TS-480':
                self.radio = device
            if device.profile_name == 'Alpha4510A':
                self.meter = device
                self.meter.signals.forward.connect(lambda x: self.data['m_fwd'].append(float(x)))
                self.meter.signals.reverse.connect(lambda x: self.data['m_rev'].append(float(x)))
                self.meter.signals.swr.connect(lambda x: self.data['m_swr'].append(float(x)))
            if device.profile_name == 'RFSensor':
                self.sensor = device
                self.sensor.signals.forward.connect(lambda x: self.data['s_fwd'].append(float(x)))
                self.sensor.signals.reverse.connect(lambda x: self.data['s_rev'].append(float(x)))
                self.sensor.signals.match_quality.connect(lambda x: self.data['s_swr'].append(float(x)))

        self.started.emit()
        
        self.switch.set_antenna(1)
        self.radio.set_vfoA_frequency(int(self.points[self.current_point].freq))
        self.radio.set_power_level(int(self.points[self.current_point].power))
        self.radio.key()
        self.data.clear()

    @Slot()
    def stop(self):
        self.timer.stop()

        if self.radio:
            self.radio.unkey()

        self.switch = None
        self.meter = None
        self.radio = None
        self.sensor = None

        self.stopped.emit()
        self.finished.emit(self.results)

    def update(self):
        self.updated.emit(self.current_point)

        if self.data.is_ready():
            self.results.append(self.calculate_result())
            self.current_point += 1
            
            if self.current_point == len(self.points):
                self.stop()
                return

            self.radio.unkey()
            self.radio.set_vfoA_frequency(int(self.points[self.current_point].freq))
            self.radio.set_power_level(int(self.points[self.current_point].power))
            self.radio.key()

            self.data.clear()


freqs = ["01800000", "03500000", "07000000", "10100000", "14000000", "18068000", "21000000", "24890000", "28000000", "50000000", ]
powers = ["005", "010", "015", "020", "025", "030", "035", "040", "050", "060", "070", "080", "090", "100", ]

@DeviceManager.subscribe
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

        self.parent().tabs.addTab(self, 'Calibration')

        self.script = {'freqs': [], 'powers': []}

        self.freqs = QListWidget()
        self.freqs.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.freqs.addItems(freqs)
        self.freqs.selectAll()

        self.powers = QListWidget()
        self.powers.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.powers.addItems(powers)
        self.powers.selectAll()
        
        self.thread = QThread()
        self.worker = CalibrationWorker()
        self.worker.moveToThread(self.thread)
        self.thread.start()
        self.worker.started.connect(self.worker_started)
        self.worker.stopped.connect(self.worker_stopped)

        self.start = QPushButton('Start', clicked=self.start_worker)
        self.stop = QPushButton('Stop', clicked=self.worker.stop, enabled=False)
        self.progress = QProgressBar()
        self.worker.updated.connect(self.progress.setValue)

        self.target = QComboBox()
        self.master = QComboBox()

        self.polys = QTextEdit('')
        self.results = QTextEdit('')
        self.header = QTextEdit('')

        font = self.results.font()
        font.setFamily('Courier New')
        self.results.setFont(font)

        self.worker.finished.connect(self.worker_finished)

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
                    hbox.add(QLabel('Master:'))
                    hbox.add(self.master, 1)
                    hbox.add(QLabel('Target:'))
                    hbox.add(self.target, 1)
                    hbox.add(QLabel(), 1)
                    hbox.add(self.start)
                    hbox.add(self.stop)
                with CHBoxLayout(vbox) as hbox:
                    with CVBoxLayout(hbox) as vbox:
                        vbox.add(self.freqs)
                        vbox.add(self.powers)
                    with CVBoxLayout(hbox, 1) as vbox:
                        vbox.add(self.progress)
                        vbox.add(self.results, 1)
                        vbox.add(self.polys, 1)
                        vbox.add(self.header, 1)

    def device_added(self, device):
        self.target.addItem(device.title)
        self.master.addItem(device.title)

    def start_worker(self):
        self.script['freqs'] = [f.text() for f in self.freqs.selectedItems()]
        self.script['powers'] = [p.text() for p in self.powers.selectedItems()]
        self.worker.start(self.script)

    def worker_started(self):
        self.progress.setMaximum(len(self.script['freqs']) * len(self.script['powers']))
        self.progress.setValue(0)
        self.start.setEnabled(False)
        self.stop.setEnabled(True)

    def worker_stopped(self):
        self.progress.setValue(0)
        self.start.setEnabled(True)
        self.stop.setEnabled(False)

    def worker_finished(self, results):

        freqs = {p.freq for p in results}
        
        self.polys.setText('')
        polys = {"fwd": {}, "rev": {}}
        
        for freq in freqs:
            points = [p for p in results if p.freq == freq]
            x = [p.sensor_fwd for p in points]
            y = [p.meter_fwd for p in points]
            temp = np.poly1d(np.polyfit(x, y, 2))
            poly = {"a": 0, "b": 0, "c": 0}
            poly["a"] = round(temp[2], 10)
            poly["b"] = round(temp[1], 10)
            poly["c"] = round(temp[0], 10)

            polys['fwd'][freq] = poly

        for freq in freqs:
            points = [p for p in results if p.freq == freq]
            x = [p.sensor_rev for p in points]
            y = [p.meter_rev for p in points]
            temp = np.poly1d(np.polyfit(x, y, 2))
            poly = {"a": 0, "b": 0, "c": 0}
            poly["a"] = round(temp[2], 10)
            poly["b"] = round(temp[1], 10)
            poly["c"] = round(temp[0], 10)

            polys['rev'][freq] = poly


        self.polys.setText(str(polys))
        self.header.setText(self.create_poly_header(polys))

        s = ''
        for r in results:
            s += repr(r) + '\n'
        self.results.setText(s)

    def create_poly_header(self, polys):
        header = []

        # make sure the outputs are in order
        bands = [p for p in polys["fwd"]]
        bands.sort()

        header.append(
            "polynomial_t forwardCalibrationTable[NUM_OF_BANDS] = {\r\n")
        for band in bands:
            header.append("    {" + str(polys["fwd"][band]["a"]) + ", ")
            header.append(str(polys["fwd"][band]["b"]) + ", ")
            header.append(str(polys["fwd"][band]["c"]) + "},")
            header.append(" // " + band + "\r\n")
        header.append("};\r\n\r\n")

        header.append(
            "polynomial_t reverseCalibrationTable[NUM_OF_BANDS] = {\r\n")
        for band in bands:
            header.append("    {" + str(polys["rev"][band]["a"]) + ", ")
            header.append(str(polys["rev"][band]["b"]) + ", ")
            header.append(str(polys["rev"][band]["c"]) + "},")
            header.append(" // " + band + "\r\n")
        header.append("};\r\n\r\n")

        return ''.join(header)