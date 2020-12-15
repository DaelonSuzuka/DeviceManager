from qt import *
from device_manager import DeviceManager
from plugins.widgets import *
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

        self.graphs = GraphTab()
        self.setup = RunTab()
        self.setup.start.clicked.connect(self.start_worker)
        self.setup.stop.clicked.connect(self.worker.stop)

        self.results_tab = ResultsTab()

        tabs = {'Run': self.setup, 'results': self.results_tab, 'graphs': self.graphs}
        self.tabs = PersistentTabWidget('calibration_tabs', tabs=tabs)

        with CVBoxLayout(self) as layout:
            with layout.hbox():
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
        if len(results) == 0 or len(results['data']) == 0:
            return

        self.results_tab.display_results(results)
        self.graphs.set_data(results['data'])