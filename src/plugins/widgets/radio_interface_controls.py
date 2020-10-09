from qt import *
from device_manager import DeviceManager


@DeviceManager.subscribe_to("RadioInterface")
class FullTuneButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setText('Full Tune')
        self.setCheckable(True)

        self.timer = QTimer(self, timeout=self.uncheck)
        self.toggled.connect(self.on_toggle)

        self.peers = []

    def register(self, *buttons):
        for button in buttons:
            self.peers.append(button)

    def on_toggle(self, state):
        if state == True:
            if self.device is not None:
                self.device.set_output(True)

            self.timer.start(3000)
            self.setEnabled(False)
            for button in self.peers:
                button.setEnabled(False)

    def uncheck(self):
        self.device.set_output(False)
        self.timer.stop()
        self.setChecked(False)
        self.setEnabled(True)
        for button in self.peers:
            button.setEnabled(True)


@DeviceManager.subscribe_to("RadioInterface")
class MemoryTuneButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setText('Mem Tune')
        self.setCheckable(True)

        self.timer = QTimer(self, timeout=self.uncheck)
        self.toggled.connect(self.on_toggle)

        self.peers = []

    def register(self, *buttons):
        for button in buttons:
            self.peers.append(button)

    def on_toggle(self, state):
        if state == True:
            if self.device is not None:
                self.device.set_output(True)

            self.timer.start(1500)
            self.setEnabled(False)
            for button in self.peers:
                button.setEnabled(False)

    def uncheck(self):
        self.device.set_output(False)
        self.timer.stop()
        self.setChecked(False)
        self.setEnabled(True)
        for button in self.peers:
            button.setEnabled(True)


@DeviceManager.subscribe_to("RadioInterface")
class BypassButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setText('Bypass')
        self.setCheckable(True)

        self.timer = QTimer(self, timeout=self.uncheck)
        self.toggled.connect(self.on_toggle)

        self.peers = []

    def register(self, *buttons):
        for button in buttons:
            self.peers.append(button)

    def on_toggle(self, state):
        if state == True:
            if self.device is not None:
                self.device.set_output(True)

            self.timer.start(250)
            self.setEnabled(False)
            for button in self.peers:
                button.setEnabled(False)

    def uncheck(self):
        self.device.set_output(False)
        self.timer.stop()
        self.setChecked(False)
        self.setEnabled(True)
        for button in self.peers:
            button.setEnabled(True)