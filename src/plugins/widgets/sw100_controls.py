from qt import *
from device_manager import DeviceManager


@DeviceManager.subscribe_to("SW-100")
class SW100Widget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        self.rx = QPushButton("RX", checkable=True)
        self.none = QPushButton("none", checkable=True, checked=True)
        self.tx = QPushButton("TX", checkable=True)

        with CVBoxLayout(self) as vbox:
            with CHBoxLayout(vbox) as hbox:
                hbox.addWidget(QLabel(""), 1)
                hbox.addWidget(self.rx)
                hbox.addWidget(self.none)
                hbox.addWidget(self.tx)
                hbox.addWidget(QLabel(""), 1)

    def connected(self, device):
        self.rx.clicked.connect(lambda: device.set_antenna("tx"))
        self.none.clicked.connect(lambda: device.set_antenna("none"))
        self.tx.clicked.connect(lambda: device.set_antenna("rx")) 
        device.signals.antenna.connect(self.select_antenna)

    def select_antenna(self, antenna):
        self.rx.setChecked(False)
        self.none.setChecked(False)
        self.tx.setChecked(False)

        if antenna == 0:
            self.none.setChecked(True)
        elif antenna == 1:
            self.rx.setChecked(True)
        elif antenna == 2:
            self.tx.setChecked(True)