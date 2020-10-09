from qt import *
from device_manager import DeviceManager
from functools import partial


@DeviceManager.subscribe_to("TS-480")
class RadioBandButtons(QWidget):
    set_frequency = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.freqs = [
            "50000000", "28000000", "24890000", "21000000", "18068000",
            "14000000", "10100000", "07000000", "03500000", "01800000"
        ]
        band_names = ["50", "28", "24", "21", "18", "14", "10", "7", "3.4", "1.8"]
        self.btns = QButtonGroup()

        with CGridLayout(self, margins=(0, 0, 0, 0)) as grid:
            for i, band in enumerate(band_names):
                btn = QPushButton(band + ' Mhz', checkable=True)
                self.btns.addButton(btn)
                grid.add(btn, i + 1, 0)
                btn.clicked.connect(lambda: self.btns.setExclusive(True))
                btn.clicked.connect(partial(self.set_frequency.emit, self.freqs[i]))
            
            grid.add(QPushButton(disabled=True), 0, 0)
            grid.add(QPushButton(disabled=True), 0, 1)
            grid.add(QPushButton(disabled=True), 0, 2)

            self.up = grid.add(QPushButton('^', clicked=lambda: self.uncheck_all()), 1, 1, 5, 2)
            self.down = grid.add(QPushButton('v', clicked=lambda: self.uncheck_all()), 6, 1, 5, 2)

    def connected(self, device):
        device.signals.frequency.connect(lambda s: self.select(s))
        self.up.clicked.connect(device.band_up)
        self.down.clicked.connect(device.band_down)
        self.set_frequency.connect(device.set_vfoA_frequency)

    def uncheck_all(self):
        self.btns.setExclusive(False)
        for btn in self.btns.buttons():
            btn.setChecked(False)

    def select(self, power):
        for btn in self.btns.buttons():
            if btn.text().lstrip('0') == power:
                btn.setChecked(True)
                self.btns.setExclusive(True)
                return
