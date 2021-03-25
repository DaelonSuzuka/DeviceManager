from qt import *
from codex import DeviceManager


@DeviceManager.subscribe_to("VariableDummyLoad")
class DummyLoadControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        with CVBoxLayout(self, margins=(0, 0, 0, 0)) as layout:
            self.cup = layout.add(QPushButton("CUP"))
            self.cdn = layout.add(QPushButton("CDN"))
            self.lup = layout.add(QPushButton("LUP"))
            self.ldn = layout.add(QPushButton("LDN"))
            self.clear = layout.add(QPushButton("Bypass"))