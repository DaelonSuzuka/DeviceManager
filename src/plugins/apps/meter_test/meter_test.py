from itertools import product

from qtstrap import *
from qtstrap import (
    QWidget,
    QThread,
    QSpinBox,
    QPushButton,
    QProgressBar,
    QLabel,
    HLine,
    VLine,
    CHBoxLayout,
    CVBoxLayout,
)
from qtstrap.extras.settings_model import SettingsModel
from codex import DeviceManager
from plugins.widgets import *
from .worker import RelayWorker
import logging


class PlanSettings(SettingsModel):
    cap_min: int = 0
    cap_max: int = 32
    cap_step: int = 1
    ind_min: int = 0
    ind_max: int = 32
    ind_step: int = 1
    z_0: bool = True
    z_1: bool = True

    class Config:
        prefix = 'automation/plan'


class AutomationControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet('QProgressBar { border: 1px solid grey; }')

        self.plan = PlanSettings()

        with CHBoxLayout(self, margins=(0, 0, 0, 0)) as layout:
            with layout.vbox():
                with layout.hbox():
                    self.start = layout + QPushButton('\nStart\n')
                    self.stop = layout + QPushButton('\nStop\n', enabled=False)
                self.progress = layout + QProgressBar()
                with layout.hbox():
                    layout.add(QLabel('Points:'))
                    self.total_points = layout.add(QLabel('?'))
                layout.add(QLabel(), 1)

            layout.add(VLine())
            layout.add(VLine())
            layout.add(RadioPowerButtons())
            layout.add(VLine())
            layout.add(RadioBandButtons())
            layout.add(VLine())
            with layout.vbox():
                layout.add(RadioKeyButton())
                layout.add(QLabel(), 1)
            layout.add(QLabel(), 1)

        self.update_total_points()

    def target_updated(self, value, field):
        setattr(self.plan, field, value)
        self.update_total_points()

    def build_plan(self):
        # caps = range(self.plan.cap_min, self.plan.cap_max + 1, self.plan.cap_step)
        # inds = range(self.plan.ind_min, self.plan.ind_max + 1, self.plan.ind_step)
        # z = []
        # if self.plan.z_0:
        #     z.append(0)
        # if self.plan.z_1:
        #     z.append(1)
        # return list(product(z, caps, inds))

        ants = [
            1,
            2,
            3,
        ]
        freqs = [
            '01800000',
            '03500000',
            '07000000',
            '10100000',
            '14000000',
            '18068000',
            '21000000',
            '24890000',
            '28000000',
            '50000000',
        ]
        powers = [
            20,
            5,
            25,
            10,
            30,
            15,
            35,
            40,
            50,
            60,
            70,
            80,
            90,
            100,
            110,
            120,
            130,
            140,
            150,
            160,
            170,
            180,
            190,
            200,
        ]
        return list(product(ants, freqs, powers))

    def update_total_points(self):
        total = len(self.build_plan())
        self.total_points.setText(f'{total: 5}')

    def started(self, steps):
        self.progress.setMaximum(steps)
        self.progress.setValue(0)
        self.start.setEnabled(False)
        self.stop.setEnabled(True)

    def stopped(self):
        self.progress.setValue(0)
        self.start.setEnabled(True)
        self.stop.setEnabled(False)


class MeterTestApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.tab_name = 'Meter Tester'
        self.setStyleSheet("""
            QWidget { font-size: 16pt; }
            QPushButton { 
                max-width: 2000px; 
                max-height: 2000px; 
            } 
        """)
        self.setBackgroundRole(QPalette.Base)
        self.setAutoFillBackground(True)

        self.log = logging.getLogger(__name__)

        self.controls = AutomationControls()
        self.controls.start.clicked.connect(self.start_worker)
        self.controls.stop.clicked.connect(self.stop_worker)

        self.thread = QThread()
        self.worker = RelayWorker()
        self.worker.moveToThread(self.thread)
        self.thread.start()
        self.worker.started.connect(self.controls.started)
        self.worker.stopped.connect(self.controls.stopped)
        self.worker.finished.connect(self.worker_finished)
        self.worker.updated.connect(self.controls.progress.setValue)

        with CHBoxLayout(self) as layout:
            with layout.vbox(1):
                layout.add(RadioInfo())
                layout.add(HLine())
                layout.add(MeterInfo())
                layout.add(HLine())
                layout.add(MC200Info())
                layout.add(QLabel(), 1)
            layout.add(VLine())
            with layout.vbox(4):
                layout.add(self.controls, 7)
                layout.add(HLine())
                layout.add(DTS6Controls(self), 1)

    def close(self):
        self.worker.stop()
        self.thread.terminate()

    def start_worker(self):
        self.worker.start(self.controls.build_plan())

    def stop_worker(self):
        self.worker.stop()

    def worker_finished(self, results):
        self.controls.progress.setValue(self.controls.progress.maximum())
