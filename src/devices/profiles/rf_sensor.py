from devices import SerialDevice, DeviceWidget, CommonMessagesMixin
from qt import *
from functools import partial


class Signals(QObject):
    forward = Signal(float)
    reverse = Signal(float)
    swr = Signal(float)
    frequency = Signal(int)

    @property
    def message_tree(self):
        return {
            "update": {
                "forward": self.forward.emit,
                "reverse": self.reverse.emit,
                "swr": self.swr.emit,
                "frequency": self.frequency.emit,
            }
        }


class RFSensor(CommonMessagesMixin, SerialDevice):
    profile_name = "RFSensor"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)

    @property
    def widget(self):
        w = RFSensorWidget(self.title, self.guid)
        
        # connect signals
        self.signals.forward.connect(lambda x: w.rf_panel.forward.setText(f"{x:10.2f}"))
        self.signals.reverse.connect(lambda x: w.rf_panel.reverse.setText(f"{x:10.2f}"))

        return w

class RFSensorWidget(DeviceWidget):
    def create_widgets(self):
        self.rf_panel = RFPanel()

    def build_layout(self):
        grid = QGridLayout()
        grid.setContentsMargins(10, 20, 10, 10)

        grid.addWidget(self.rf_panel, 0, 0)
        grid.setRowStretch(2, 1)
        
        self.setWidget(QWidget(layout=grid))


class RFPanel(QGroupBox):
    def __init__(self):
        super().__init__("RF")
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        
        # create widgets
        self.frequency = QLabel("?")
        self.forward = QLabel("?")
        self.reverse = QLabel("?")

        # create layout
        grid = QGridLayout(self)
        grid.addWidget(QLabel("Forward:"), 0, 0)
        grid.addWidget(self.forward, 0, 1)
        grid.addWidget(QLabel("Reverse:"), 0, 2)
        grid.addWidget(self.reverse, 0, 3)
        grid.addWidget(QLabel("Frequency:"), 0, 4)
        grid.addWidget(self.frequency, 0, 5)