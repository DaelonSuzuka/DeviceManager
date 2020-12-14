from qt import *
from device_manager import DeviceManager
from functools import partial
from.lock_button import LockButton


@DeviceManager.subscribe_to("TS-480")
class RadioPowerButtons(QWidget):
    power_changed = Signal(str)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.power = '5'
        self.limit = True
        self.btns = QButtonGroup()

        powers = ["200", "175", "150", "125", "100", "75", "50", "25", "10", "5"]

        with CGridLayout(self, margins=(0, 0, 0, 0)) as layout:
            for i, power in enumerate(powers):
                btn = QPushButton(power, checkable=True)
                self.btns.addButton(btn)
                layout.add(btn, i + 1, 0)
                btn.clicked.connect(lambda: self.btns.setExclusive(True))
                btn.clicked.connect(partial(self.update_power, btn.text()))

            self.lock = layout.add(LockButton(iconSize=QSize(35, 35)), 0, 0)
            layout.add(QPushButton(disabled=True), 0, 1)
            layout.add(QPushButton(disabled=True), 0, 2)
            layout.add(QPushButton('+', clicked=lambda: self.update_power(int(self.power) + 5)), 1, 1, 5, 2)
            layout.add(QPushButton('-', clicked=lambda: self.update_power(int(self.power) - 5)), 6, 1, 5, 2)

        self.lock.toggled.connect(lambda s: self.set_limit(not s))
        self.set_limit(True)

    def connected(self, device):
        device.signals.power.connect(lambda s: self.set_power(s))
        self.power_changed.connect(device.set_power_level)

    def update_power(self, power):
        power = str(power)
        if self.limit:
            if int(power) > 100:
                power = '100'
        self.power_changed.emit(power)

    def set_power(self, power):
        self.power = power
        
        self.uncheck_all()
        self.select(power)

    def set_limit(self, limit):
        self.limit = limit
        if limit == True:
            self.update_power(self.power)
            
            for btn in self.btns.buttons():
                if int(btn.text()) > 100:
                    btn.setEnabled(False)

        else:
            for btn in self.btns.buttons():
                btn.setEnabled(True)

    def uncheck_all(self):
        self.btns.setExclusive(False)
        for btn in self.btns.buttons():
            btn.setChecked(False)

    def select(self, power):
        for btn in self.btns.buttons():
            if btn.text() == power:
                btn.setChecked(True)
                self.btns.setExclusive(True)
                return