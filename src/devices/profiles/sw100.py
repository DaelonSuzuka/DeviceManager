from devices import SerialDevice, DeviceWidget, CommonMessagesMixin
from functools import partial
from qt import *


class Signals(QObject):
    antenna = Signal(int)

    @property
    def message_tree(self):
        return {
            "update": {
                "antenna": self.antenna.emit
            }
        }


class SW100(CommonMessagesMixin, SerialDevice):
    profile_name = "SW-100"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)

        self.request_antenna()

    def set_antenna(self, ant: str):
        self.send('{"command":{"set_antenna":"%s"}}' % (ant))

    def request_antenna(self):
        self.send('{"request":"antenna"}')
    
    @property
    def widget(self):
        w = SW100Widget(self.title, self.guid)

        # connect signals
        w.ant_btns.rx.clicked.connect(lambda: self.set_antenna("tx"))
        w.ant_btns.none.clicked.connect(lambda: self.set_antenna("none"))
        w.ant_btns.tx.clicked.connect(lambda: self.set_antenna("rx")) 

        self.signals.antenna.connect(w.ant_btns.select_antenna)
        
        return w


class SW100Widget(DeviceWidget):
    def create_widgets(self):
        self.ant_btns = AntennaButtons()

    def build_layout(self):
        grid = QGridLayout()
        grid.setContentsMargins(10, 20, 10, 10)

        grid.addWidget(self.ant_btns, 0, 0)
        grid.setColumnStretch(5, 1)
        
        self.setWidget(QWidget(layout=grid))


class AntennaButtons(QGroupBox):
    def __init__(self):
        super().__init__("Select Antenna")
        
        # create widgets
        self.rx = QPushButton("RX", checkable=True)
        self.none = QPushButton("none", checkable=True)
        self.none.setChecked(True)
        self.tx = QPushButton("TX", checkable=True)

        # create layout
        hbox = QHBoxLayout(self)
        hbox.addWidget(self.rx)
        hbox.addWidget(self.none)
        hbox.addWidget(self.tx)

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