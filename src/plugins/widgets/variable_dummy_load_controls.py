from qt import *
from device_manager import DeviceManager


@DeviceManager.subscribe_to("VariableDummyLoad")
class DummyLoadControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        with CVBoxLayout(self, margins=(0, 0, 0, 0)) as vbox:
            self.cup = vbox.add(QPushButton("CUP"))
            self.cdn = vbox.add(QPushButton("CDN"))
            self.lup = vbox.add(QPushButton("LUP"))
            self.ldn = vbox.add(QPushButton("LDN"))
            self.clear = vbox.add(QPushButton("Bypass"))