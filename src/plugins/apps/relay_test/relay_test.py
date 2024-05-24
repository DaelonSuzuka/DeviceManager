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
from codex import DeviceManager
from plugins.widgets import *
from .worker import RelayWorker
import logging


@DeviceManager.subscribe_to('PhaseTuner')
class RelayControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        with CVBoxLayout(self, margins=(0, 0, 0, 0)) as layout:
            self.bypass_btn = layout.add(QPushButton('\nbypass\n'))
            with layout.hbox():
                self.cup_btn = layout.add(QPushButton('\nCUP\n', autoRepeat=True))
                self.cdn_btn = layout.add(QPushButton('\nCDN\n', autoRepeat=True))
            with layout.hbox():
                self.lup_btn = layout.add(QPushButton('\nLUP\n', autoRepeat=True))
                self.ldn_btn = layout.add(QPushButton('\nLDN\n', autoRepeat=True))
            with layout.hbox():
                self.hiz_btn = layout.add(QPushButton('\nHiZ\n'))
                self.loz_btn = layout.add(QPushButton('\nLoZ\n'))
            layout.add(QLabel(), 1)

    def connected(self, device):
        self.bypass_btn.clicked.connect(device.bypass)
        self.cup_btn.clicked.connect(device.relays_cup)
        self.cdn_btn.clicked.connect(device.relays_cdn)
        self.lup_btn.clicked.connect(device.relays_lup)
        self.ldn_btn.clicked.connect(device.relays_ldn)
        self.hiz_btn.clicked.connect(lambda: device.set_relays(z=1))
        self.loz_btn.clicked.connect(lambda: device.set_relays(z=0))

class AutomationControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet('QProgressBar { border: 1px solid grey; }')

        self.plan = {
            'cap_min': 0,
            'cap_max': 31,
            'ind_min': 0,
            'ind_max': 31,
            'z_0': True,
            'z_1': True,
        }

        with CHBoxLayout(self, margins=(0, 0, 0, 0)) as layout:
            with layout.vbox():
                with layout.hbox():
                    self.start = layout + QPushButton('\nStart\n')
                    self.stop = layout + QPushButton('\nStop\n', enabled=False)
                self.progress = layout + QProgressBar()
                with layout.hbox():
                    self.cap_min = layout + QSpinBox(maximum=255, valueChanged=lambda x: self.target_updated(x, 'cap_min'))
                    self.cap_max = layout + QSpinBox(
                        maximum=255,
                        value=self.plan['cap_max'],
                        valueChanged=lambda x: self.target_updated(x, 'cap_max'),
                    )
                with layout.hbox():
                    self.ind_min = layout + QSpinBox(maximum=127, valueChanged=lambda x: self.target_updated(x, 'ind_min'))
                    self.ind_max = layout + QSpinBox(
                        maximum=127,
                        value=self.plan['ind_max'],
                        valueChanged=lambda x: self.target_updated(x, 'ind_max'),
                    )
                with layout.hbox():
                    self.z_0 = layout + QPushButton('0', checkable=True, checked=True, toggled=lambda x: self.target_updated(x, 'z_0'))
                    self.z_1 = layout + QPushButton('1', checkable=True, checked=True, toggled=lambda x: self.target_updated(x, 'z_1'))
                with layout.hbox():
                    layout.add(QLabel('Points:'))
                    self.total_points = layout.add(QLabel('?'))
                layout.add(QLabel(), 1)

            layout.add(VLine())
            self.relays = layout.add(RelayControls())
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
        self.plan[field] = value
        self.update_total_points()

    def build_plan(self):
        caps = range(self.plan['cap_min'], self.plan['cap_max'])
        inds = range(self.plan['ind_min'], self.plan['ind_max'])
        z = []
        if self.plan['z_0']:
            z.append(0)
        if self.plan['z_1']:
            z.append(1)
        return list(product(z, caps, inds))

    def update_total_points(self):
        total = len(self.build_plan())
        self.total_points.setText(f'{total: 5}')

    def started(self, steps):
        self.progress.setMaximum(steps)
        self.progress.setValue(0)
        self.start.setEnabled(False)
        self.stop.setEnabled(True)
        self.cap_min.setEnabled(False)
        self.cap_max.setEnabled(False)
        self.ind_min.setEnabled(False)
        self.ind_max.setEnabled(False)
        self.z_0.setEnabled(False)
        self.z_1.setEnabled(False)

    def stopped(self):
        self.progress.setValue(0)
        self.start.setEnabled(True)
        self.stop.setEnabled(False)
        self.cap_min.setEnabled(True)
        self.cap_max.setEnabled(True)
        self.ind_min.setEnabled(True)
        self.ind_max.setEnabled(True)
        self.z_0.setEnabled(True)
        self.z_1.setEnabled(True)


class RelayTestApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.tab_name = 'Relay Tester'
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
                layout.add(PhaseTunerInfo())
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
