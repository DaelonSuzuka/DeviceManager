from qtstrap import *
from codex import DeviceManager


@DeviceManager.subscribe_to("DTS-6")
class DTS6Controls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        with CHBoxLayout(self, margins=(0, 0, 0, 0)) as layout:
            self.one = layout.add(QPushButton("Ant 1", checkable=True))
            self.two = layout.add(QPushButton("Ant 2", checkable=True))
            self.three = layout.add(QPushButton("Ant 3", checkable=True))
            self.four = layout.add(QPushButton("Ant 4", checkable=True))
            self.five = layout.add(QPushButton("Ant 5", checkable=True))
            self.six = layout.add(QPushButton("Ant 6", checkable=True))

        self.btns = QButtonGroup()
        self.btns.addButton(self.one)
        self.btns.addButton(self.two)
        self.btns.addButton(self.three)
        self.btns.addButton(self.four)
        self.btns.addButton(self.five)
        self.btns.addButton(self.six)
        
    def antenna_changed(self, antenna):
        if antenna == 0:
            self.one.setChecked(False)
            self.two.setChecked(False)
            self.three.setChecked(False)
            self.four.setChecked(False)
        if antenna == 1:
            self.one.setChecked(True)
        if antenna == 2:
            self.two.setChecked(True)
        if antenna == 3:
            self.three.setChecked(True)
        if antenna == 4:
            self.four.setChecked(True)
        if antenna == 5:
            self.five.setChecked(True)
        if antenna == 6:
            self.six.setChecked(True)

    def connected(self, device):
        self.one.clicked.connect(lambda: device.set_antenna(1))
        self.two.clicked.connect(lambda: device.set_antenna(2))
        self.three.clicked.connect(lambda: device.set_antenna(3))
        self.four.clicked.connect(lambda: device.set_antenna(4))
        self.five.clicked.connect(lambda: device.set_antenna(5))
        self.six.clicked.connect(lambda: device.set_antenna(6))

        device.signals.antenna.connect(self.antenna_changed)

        device.get_antenna()