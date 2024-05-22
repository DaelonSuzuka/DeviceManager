from qtstrap import *
from codex import DeviceManager
from plugins.widgets import *
from .worker import RelayWorker
import logging
import json


@DeviceManager.subscribe
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
        self.log = logging.getLogger(__name__)

        self.thread = QThread()
        self.worker = RelayWorker()
        self.worker.moveToThread(self.thread)
        self.thread.start()
        self.worker.started.connect(self.worker_started)
        self.worker.stopped.connect(self.worker_stopped)
        self.worker.finished.connect(self.worker_finished)

        self.progress = QProgressBar()
        self.worker.updated.connect(self.progress.setValue)

        self.start = QPushButton('Start')
        self.start.clicked.connect(self.start_worker)
        self.stop = QPushButton('Stop', enabled=False)
        self.stop.clicked.connect(self.stop_worker)

        self.cup_btn = QPushButton('CUP', autoRepeat=True)
        self.cdn_btn = QPushButton('CDN', autoRepeat=True)
        self.lup_btn = QPushButton('LUP', autoRepeat=True)
        self.ldn_btn = QPushButton('LDN', autoRepeat=True)
        self.hiz_btn = QPushButton('HiZ')
        self.loz_btn = QPushButton('LoZ')

        self.bypass_btn = QPushButton('bypass')

        with CHBoxLayout(self) as layout:
            layout.add(self.progress)
            with layout.vbox():
                layout.add(RadioInfo())
                layout.add(HLine())
                layout.add(MeterInfo())
                layout.add(HLine())
                layout.add(PhaseTunerInfo())
                layout.add(QLabel(), 1)
            with layout.vbox():
                with layout.hbox():
                    layout.add(self.start)
                    layout.add(self.stop)
                layout.add(self.bypass_btn)
                with layout.hbox():
                    layout.add(self.cup_btn)
                    layout.add(self.lup_btn)
                with layout.hbox():
                    layout.add(self.cdn_btn)
                    layout.add(self.ldn_btn)
                with layout.hbox():
                    layout.add(self.hiz_btn)
                    layout.add(self.loz_btn)
                layout.add(QLabel(), 1)
            with layout.vbox():
                layout.add(RadioKeyButton())
                layout.add(QLabel(), 1)
            layout.add(QLabel(), 1)

    def device_added(self, device):
        if device.profile_name == 'PhaseTuner':
            self.bypass_btn.clicked.connect(device.bypass)
            self.cup_btn.clicked.connect(device.relays_cup)
            self.cdn_btn.clicked.connect(device.relays_cdn)
            self.lup_btn.clicked.connect(device.relays_lup)
            self.ldn_btn.clicked.connect(device.relays_ldn)
            self.hiz_btn.clicked.connect(lambda: device.set_relays(z=1))
            self.loz_btn.clicked.connect(lambda: device.set_relays(z=0))
            device.get_relays()
            device.get_rf()

    def close(self):
        self.worker.stop()
        self.thread.terminate()

    def start_worker(self):
        self.worker.start()

    def stop_worker(self):
        self.worker.stop()

    def worker_started(self, steps):
        self.progress.setMaximum(steps)
        self.progress.setValue(0)
        self.start.setEnabled(False)
        self.stop.setEnabled(True)

    def worker_stopped(self):
        self.progress.setValue(0)
        self.start.setEnabled(True)
        self.stop.setEnabled(False)

    def worker_finished(self, results):
        self.progress.setValue(self.progress.maximum())
        if len(results) == 0 or len(results['data']) == 0:
            return
