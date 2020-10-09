from qt import *
from device_manager import DeviceManager


class DummyLoadControls(Widget):
    def create_widgets(self):
        vbox = CVBoxLayout(self, margins=(0, 0, 0, 0))
        self.cup = vbox.add(QPushButton("CUP"))
        self.cdn = vbox.add(QPushButton("CDN"))
        self.lup = vbox.add(QPushButton("LUP"))
        self.ldn = vbox.add(QPushButton("LDN"))
        self.clear = vbox.add(QPushButton("Bypass"))