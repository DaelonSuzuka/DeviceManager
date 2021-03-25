from qt import *
from codex import DeviceManager


@DeviceManager.subscribe_to("judipedals")
class JudiPedalsControls(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.one = QPushButton(checkable=True)
        self.two = QPushButton(checkable=True)
        self.three = QPushButton(checkable=True)
        self.foud = QPushButton(checkable=True)
        
        layout = QHBoxLayout()

        layout.addWidget(self.one)
        layout.addWidget(self.two)
        layout.addWidget(self.three)
        layout.addWidget(self.foud)

        self.setWidget(QWidget(layout=layout))

    def connected(self, device):
        device.signals.button_pressed.connect(self.button_pressed)
        device.signals.button_released.connect(self.button_released)

    def button_pressed(self, button):
        if button == '1':
            self.one.setChecked(True)
        if button == '2':
            self.two.setChecked(True)
        if button == '3':
            self.three.setChecked(True)
        if button == '4':
            self.foud.setChecked(True)

    def button_released(self, button):
        if button == '1':
            self.one.setChecked(False)
        if button == '2':
            self.two.setChecked(False)
        if button == '3':
            self.three.setChecked(False)
        if button == '4':
            self.foud.setChecked(False)