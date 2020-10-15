from qt import *
from device_manager import DeviceManager
from plugins.widgets import *
from dataclasses import dataclass
from collections import deque  
import numpy as np
import json
import pyqtgraph as pg
from .test_data import test_data


@dataclass
class Point:
    freq: str
    power: str


class DataQueue:
    def __init__(self, keys, stabilize=[], maxlen=10):
        self._data = {}
        self.stabilize=stabilize
        self.reject_count = 0

        for key in keys:
            self._data[key] = deque(maxlen=maxlen)

    def __getitem__(self, key):
        return self._data[key]

    def clear(self):
        for _, queue in self._data.items():
            queue.clear()
        self.reject_count = 0

    def is_ready(self):
        for _, queue in self._data.items():
            if len(queue) != queue.maxlen:
                return False
        return True

    def is_ready(self):
        for name, queue in self._data.items():
            if len(queue) == queue.maxlen:
                if name in self.stabilize:
                    if ((max(queue) - min(queue)) / np.median(queue)) > self.stabilize[name]:
                        queue.popleft()
                        self.reject_count += 1
                        return False
            else:
                return False
            
        return True

    def get_data(self):
        result = {}
        for name, queue in self._data.items():
            result['_reject_count'] = self.reject_count
            result[name] = np.mean(queue)
            result[f'{name}_raw'] = list(queue)

        return result


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
        self.target = None

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.update())

        self.points = []
        self.current_point = 0
        self.results = []

        fields = [
            'm_fwd', 'm_rev', 'm_swr', 'm_freq', 'm_temp',
            't_fwd_volts', 't_rev_volts', 't_mq', 
            't_fwd_watts', 't_rev_watts', 't_swr', 't_freq',
        ]
        self.data = DataQueue(fields, stabilize={'m_freq':0.01})

    @Slot()
    def start(self, script):
        self.timer.start(50)

        self.points = []
        self.results = []

        for freq in script['freqs']:
            for power in script['powers']:
                self.points.append(Point(freq, power))

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
                self.meter.signals.frequency.connect(lambda x: self.data['m_freq'].append(float(x)))
                self.meter.signals.temperature.connect(lambda x: self.data['m_temp'].append(float(x)))
            if device.profile_name == 'CalibrationTarget':
                self.target = device
                self.target.signals.forward_volts.connect(lambda x: self.data['t_fwd_volts'].append(float(x)))
                self.target.signals.reverse_volts.connect(lambda x: self.data['t_rev_volts'].append(float(x)))
                self.target.signals.match_quality.connect(lambda x: self.data['t_mq'].append(float(x)))
                self.target.signals.forward.connect(lambda x: self.data['t_fwd_watts'].append(float(x)))
                self.target.signals.reverse.connect(lambda x: self.data['t_rev_watts'].append(float(x)))
                self.target.signals.swr.connect(lambda x: self.data['t_swr'].append(float(x)))
                self.target.signals.frequency.connect(lambda x: self.data['t_freq'].append(float(x)))

        self.started.emit()
        
        self.target.send('calibrate\n')
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

        if self.target:
            self.target.send('\03')

        self.switch = None
        self.meter = None
        self.radio = None
        self.target = None

        self.stopped.emit()
        self.finished.emit(self.results)

    def update(self):
        self.updated.emit(self.current_point)

        if self.data.is_ready():
            result = self.data.get_data()
            result['freq'] = self.points[self.current_point].freq
            result['power'] = self.points[self.current_point].power
            
            self.results.append(result)
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
powers = ["005", "010", "015", "020", "025", "030", "035", "040", "050", "060", "070", "080", "090", "100", "110", "120", ]


class GraphTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        self.graph = pg.PlotWidget()
        self.freqs = QListWidget()
        self.freqs.itemSelectionChanged.connect(self.freq_changed)

        self.x_axis = QListWidget()
        self.y_axis = QListWidget()

        with CHBoxLayout(self) as hbox:
            with CVBoxLayout(hbox) as vbox:
                vbox.add(self.freqs)
                vbox.add(self.x_axis)
                vbox.add(self.y_axis)
            hbox.add(self.graph, 1)

        self.data = {}
        self.set_data(test_data)

    def freq_changed(self):
        print(self.freqs.currentItem().text())

    # def plot_data(self, x, y):

    def set_data(self, data):
        self.data = data
        
        self.freqs.clear()
        freqs = sorted({p['freq'] for p in data})
        self.freqs.addItems(freqs)

        fields = sorted({f for f in data[0].keys()})

        self.x_axis.clear()
        self.y_axis.clear()
        self.x_axis.addItems(fields)
        self.y_axis.addItems(fields)


@DeviceManager.subscribe
class CalibrationApp(QWidget):
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

        self.results = QTextEdit('')
        self.header = QTextEdit('')
        self.recalculate = QPushButton('Recalculate', clicked=lambda: self.rebuild_header())

        self.graphs = GraphTab()

        self.setup = QWidget(self)
        with CHBoxLayout(self.setup) as hbox:
            with CVBoxLayout(hbox) as vbox:
                vbox.add(self.freqs)
                vbox.add(self.powers)
            hbox.add(QLabel(), 1)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.setup, 'setup')
        self.tabs.addTab(self.results, 'results')
        self.tabs.addTab(self.header, 'header')
        self.tabs.addTab(self.graphs, 'graph')

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
                vbox.add(CalibrationTargetInfo())
                vbox.add(QLabel(), 1)

            with CVBoxLayout(layout, 1) as vbox:
                with CHBoxLayout(vbox) as hbox:
                    hbox.add(self.progress)
                    hbox.add(self.recalculate)
                    hbox.add(self.start)
                    hbox.add(self.stop)
                vbox.add(self.tabs, 1)

    def close(self):
        self.worker.stop()
        self.thread.terminate()

    def device_added(self, device):
        self.target.clear()
        self.target.addItems(device.title for _, device in self.devices.items())
        self.master.clear()
        self.master.addItems(device.title for _, device in self.devices.items())

    def device_removed(self, guid):
        self.target.clear()
        self.target.addItems(device.title for _, device in self.devices.items())
        self.master.clear()
        self.master.addItems(device.title for _, device in self.devices.items())

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
        if len(results) == 0:
            return

        s = json.dumps(results, indent=4, sort_keys=True)
        self.results.setText(s)
        self.graphs.set_data(results)

        polys = self.calculate_polys(results)
        self.header.setText(self.create_poly_header(polys))

    def rebuild_header(self):
        results = json.loads(self.results.document().toPlainText())

        polys = self.calculate_polys(results)
        self.header.setText(self.create_poly_header(polys))

    def calculate_polys(self, results):
        freqs = {p['freq'] for p in results}
        polys = {"fwd": {}, "rev": {}}
        
        for freq in freqs:
            points = [p for p in results if p['freq'] == freq]
            x = [p['t_fwd_volts'] for p in points]
            y = [p['m_fwd'] for p in points]
            temp = np.poly1d(np.polyfit(x, y, 2))
            poly = {"a": 0, "b": 0, "c": 0}
            poly["a"] = round(temp[2], 10)
            poly["b"] = round(temp[1], 10)
            poly["c"] = round(temp[0], 10)

            polys['fwd'][freq] = poly

        for freq in freqs:
            points = [p for p in results if p['freq'] == freq]
            x = [p['t_rev_volts'] for p in points]
            y = [p['m_rev'] for p in points]
            temp = np.poly1d(np.polyfit(x, y, 2))
            poly = {"a": 0, "b": 0, "c": 0}
            poly["a"] = round(temp[2], 10)
            poly["b"] = round(temp[1], 10)
            poly["c"] = round(temp[0], 10)

            polys['rev'][freq] = poly
        
        return polys

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