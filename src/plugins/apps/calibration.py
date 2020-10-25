from qt import *
from device_manager import DeviceManager
from plugins.widgets import *
import numpy as np
import json
from .calibration_stuff import *


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

        self.progress = QProgressBar()
        self.worker.updated.connect(self.progress.setValue)

        self.results = set_font_options(QTextEdit(''), {'setFamily': 'Courier New'})
        self.header = set_font_options(QTextEdit(''), {'setFamily': 'Courier New'})

        self.graphs = GraphTab()
        self.setup = RunTab()
        self.setup.start.clicked.connect(self.start_worker)
        self.setup.stop.clicked.connect(self.worker.stop)

        self.results_tab = ResultsTab()

        tabs = {'Run': self.setup, 'results': self.results, 'results2': self.results_tab, 'header': self.header, 'graphs': self.graphs}
        self.tabs = PersistentTabWidget('calibration_tabs', tabs=tabs)

        with CVBoxLayout(self) as layout:
            with layout.hbox() as layout:
                layout.add(self.progress)
            layout.add(self.tabs, 1)

    def close(self):
        self.worker.stop()
        self.thread.terminate()

    def start_worker(self):
        self.worker.start(self.setup.get_script())

    def worker_started(self, steps):
        self.progress.setMaximum(steps)
        self.progress.setValue(0)
        self.setup.start.setEnabled(False)
        self.setup.stop.setEnabled(True)

    def worker_stopped(self):
        self.progress.setValue(0)
        self.setup.start.setEnabled(True)
        self.setup.stop.setEnabled(False)

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