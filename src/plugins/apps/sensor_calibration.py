from qt import *
from device_manager import DeviceManager
from plugins.widgets import *
from dataclasses import dataclass
from collections import deque  
import numpy as np
import json
import pyqtgraph as pg
from .test_data2 import test_data


freqs = ["01800000", "03500000", "07000000", "10100000", "14000000", "18068000", "21000000", "24890000", "28000000", "50000000", ]
powers = ["005", "010", "015", "020", "025", "030", "035", "040", "050", "060", "070", "080", "090", "100", "110", "120", ]
data_fields = [
    'm_fwd', 'm_rev', 'm_swr', 'm_freq', 'm_temp',
    't_fwd_volts', 't_rev_volts', 't_mq', 
    't_fwd_watts', 't_rev_watts', 't_swr', 't_freq',
]

data_field_names = {
    'm_fwd': 'Meter: Forward Watts',
    'm_rev': 'Meter: Reverse Watts',
    'm_swr': 'Meter: SWR',
    'm_freq': 'Meter: Frequency',
    'm_temp': 'Meter: Temperature',
    't_fwd_volts': 'Target: Forward Volts',
    't_rev_volts': 'Target: Reverse Volts',
    't_mq': 'Target: Match Quality',
    't_fwd_watts': 'Target: Forward Watts',
    't_rev_watts': 'Target: Reverse Watts',
    't_swr': 'Target: SWR',
    't_freq': 'Target: Frequency',
}


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


class DataSelector(QWidget):
    selectionChanged = Signal()

    def __init__(self, name='', parent=None):
        super().__init__(parent=parent)
        self.name = name

        changed = self.selectionChanged
        
        self.on = PersistentCheckBox(f'{name}_on', changed=changed)
        self.freqs = PersistentListWidget(f'{name}_freqs', items=['none']+freqs, default=['none'], selectionMode=QAbstractItemView.ExtendedSelection, changed=changed)
        self.x = PersistentComboBox(f'{name}_x', items=data_fields, changed=changed)
        self.y = PersistentComboBox(f'{name}_y', items=data_fields, changed=changed)

        with CVBoxLayout(self) as vbox:
            with CHBoxLayout(vbox) as hbox:
                hbox.add(QLabel(name))
                hbox.add(QLabel(), 1)
                hbox.add(QLabel('On:'))
                hbox.add(self.on)
            with CHBoxLayout(vbox) as hbox:
                hbox.add(QLabel('X:'))
                hbox.add(self.x, 1)
            with CHBoxLayout(vbox) as hbox:
                hbox.add(QLabel('Y:'))
                hbox.add(self.y, 1)

    def get_params(self):
        if self.on.checkState() and self.x.currentText() != self.y.currentText():
            return (self.x.currentText(), self.y.currentText(), self.freqs.selected_items())
        return


class GraphTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        self.plot_layout = pg.GraphicsLayoutWidget()
        self.plots = [DataSelector(f'Plot {i}', self) for i in range(1, 7)]

        def normalize(x):
            x = np.asarray(x)
            return (x - x.min()) / (np.ptp(x))

        self.freq_colors = dict(zip(freqs, normalize([float(f) for f in freqs])))

        self.freqs = PersistentListWidget(
            'graph_freqs', items=freqs, selectionMode=QAbstractItemView.ExtendedSelection, changed=self.draw_plots)
        self.freq_tabs = PersistentTabWidget('graph_tabs')
        self.freq_tabs.addTab(self.freqs, 'all')
        for plot in self.plots:
            self.freq_tabs.addTab(plot.freqs, plot.name[5:])
        self.freq_tabs.restore_state()

        with CHBoxLayout(self) as hbox:
            with CVBoxLayout(hbox) as vbox:
                vbox.add(QLabel('Freqs'))
                vbox.add(self.freq_tabs, 1)
                vbox.add(self.plots)
            hbox.add(self.plot_layout, 1)

        self.data = {}
        self.set_data(test_data)

        for plot in self.plots:
            plot.selectionChanged.connect(self.draw_plots)

    def draw_plots(self):
        freqs = self.freqs.selected_items()
        plot_params = [plot.get_params() for plot in self.plots]
        self.plot_layout.clear()

        c = 0
        for params in plot_params:
            if params is None:
                continue

            plot_freqs = params[2]
            if 'none' in params[2]:
                plot_freqs = freqs

            title = plot_freqs
            labels = {'bottom':data_field_names[params[0]], 'left':data_field_names[params[1]]}
            plot = self.plot_layout.addPlot(title=title, labels=labels)
            plot.showGrid(x=True, y=True)
            plot.showButtons()
            plot.addLegend()
            plot.setMenuEnabled(enableMenu=True, enableViewBoxMenu='same')

            c += 1
            if c % 2 == 0:
                self.plot_layout.nextRow()

            for freq in plot_freqs:
                points = [p for p in self.data if p['freq'] == freq]
                x = [p[params[0]] for p in points]
                y = [p[params[1]] for p in points]
                plot.plot(x, y, pen=pg.hsvColor(self.freq_colors[freq]), name=freq)

    def set_data(self, data):
        self.data = data
        self.draw_plots()


@DeviceManager.subscribe
class SetupTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        self.target = QComboBox()
        self.master = QComboBox()

        self.script = {'freqs': [], 'powers': []}
        self.freqs = PersistentListWidget('cal_freqs', items=freqs, selectionMode=QAbstractItemView.ExtendedSelection)
        self.powers = PersistentListWidget('cal_powers', items=powers, selectionMode=QAbstractItemView.ExtendedSelection)

        with CHBoxLayout(self) as hbox:
            with CVBoxLayout(hbox) as vbox:
                vbox.add(RadioInfo())
                vbox.add(HLine())
                vbox.add(MeterInfo())
                vbox.add(HLine())
                vbox.add(CalibrationTargetInfo())
                vbox.add(QLabel(), 1)
            with CVBoxLayout(hbox) as vbox:
                vbox.add(QLabel('Freqs'))
                vbox.add(self.freqs)
                vbox.add(QLabel('Powers'))
                vbox.add(self.powers)
            hbox.add(QLabel(), 1)

    def get_script(self):
        self.script['freqs'] = [f.text() for f in self.freqs.selectedItems()]
        self.script['powers'] = [p.text() for p in self.powers.selectedItems()]
        return self.script

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


class ResultsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


@DeviceManager.subscribe
class CalibrationApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.tab_name = 'Calibration'
        self.setStyleSheet("""
            QWidget { font-size: 16pt; }
            QPushButton { 
                max-width: 2000px; 
                max-height: 2000px; 
            } 
        """)

        self.thread = QThread()
        self.worker = CalibrationWorker()
        self.worker.moveToThread(self.thread)
        self.thread.start()
        self.worker.started.connect(self.worker_started)
        self.worker.stopped.connect(self.worker_stopped)
        self.worker.finished.connect(self.worker_finished)

        self.start = QPushButton('Start', clicked=self.start_worker)
        self.stop = QPushButton('Stop', clicked=self.worker.stop, enabled=False)
        self.progress = QProgressBar()
        self.worker.updated.connect(self.progress.setValue)

        self.results = set_font_options(QTextEdit(''), {'setFamily': 'Courier New'})
        self.header = set_font_options(QTextEdit(''), {'setFamily': 'Courier New'})

        self.recalculate = QPushButton('Recalculate', clicked=lambda: self.rebuild_outputs())

        self.graphs = GraphTab()
        self.setup = SetupTab()

        tabs = {'setup': self.setup, 'results': self.results, 'header': self.header, 'graphs': self.graphs}
        self.tabs = PersistentTabWidget('calibration_tabs', tabs=tabs)

        with CHBoxLayout(self) as layout:
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

    def start_worker(self):
        self.worker.start(self.setup.get_script())

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

    def rebuild_outputs(self):
        try:
            results = json.loads(self.results.document().toPlainText())
            if results == {}:
                print('empty')
                return
            self.graphs.set_data(results)

            polys = self.calculate_polys(results)
            self.header.setText(self.create_poly_header(polys))
        except:
            pass

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