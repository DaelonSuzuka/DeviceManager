from devices import SerialDevice, DeviceWidget, CommonMessagesMixin
from qt import *


class Signals(QObject):
    capacitors = Signal(int)
    input = Signal(int)
    output = Signal(int)
    
    @property
    def message_tree(self):
        return {
            "update": {
                "relays": {
                    "capacitors": self.capacitors.emit,
                    "input": self.input.emit,
                    "output": self.output.emit,
                }
            }
        }


class VariableCapacitor(CommonMessagesMixin, SerialDevice):
    profile_name = "VariableCapacitor"
    max_caps = 255

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)

        self.capacitors = 0
        self.signals.capacitors.connect(lambda i: self.__setattr__("capacitors", i))

        # startup messages
        self.request_current_relays()

    def set_caps(self, value):
        self.send('{"command":{"set_capacitors":%s}}' % (str(value)))

    def relays_max(self):
        self.send('{"command":{"set_capacitors":255}}')

    def relays_min(self):
        self.send('{"command":{"set_capacitors":0}}')

    def relays_cup(self):
        self.send('{"command":"cup"}')

    def relays_cdn(self):
        self.send('{"command":"cdn"}')

    def request_current_relays(self):
        self.send('{"request":"relays"}')

    def set_input_relay(self, state):
        self.send('{"relays":{"input":%s}}' % (int(state)))

    def set_output_relay(self, state):
        self.send('{"relays":{"output":%s}}' % (int(state)))

    @property
    def widget(self):
        w = VariableCapacitorWidget(self.title, self.guid)

        # connect signals
        w.input_button.clicked.connect(self.set_input_relay)
        w.output_button.clicked.connect(self.set_output_relay)

        w.cup_btn.clicked.connect(self.relays_cup)
        w.cdn_btn.clicked.connect(self.relays_cdn)
        w.max_btn.clicked.connect(self.relays_max)
        w.min_btn.clicked.connect(self.relays_min)

        w.set_relays.connect(self.set_caps)

        self.signals.capacitors.connect(lambda x: w.edit.setText(str(x)))
        self.signals.input.connect(w.input_button.setChecked)
        self.signals.output.connect(w.output_button.setChecked)

        return w


class VariableCapacitorWidget(DeviceWidget):
    set_relays = Signal(int)

    def create_widgets(self):
        self.input_button = QPushButton("Input", checkable=True)
        self.output_button = QPushButton("Output", checkable=True)

        self.cup_btn = QPushButton("CUP", autoRepeat=True)
        self.cdn_btn = QPushButton("CDN", autoRepeat=True)
        self.max_btn = QPushButton("Max")
        self.min_btn = QPushButton("Min")
        self.edit = QLineEdit()
        self.set_btn = QPushButton("Set")

    def connect_signals(self):
        self.set_btn.clicked.connect(lambda: self.set_relays.emit(int(self.edit.text())))
        self.edit.returnPressed.connect(self.set_btn.clicked)

    def build_layout(self):
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Capacitors: "))
        hbox.addWidget(self.edit)
        hbox.addWidget(self.set_btn)
        gbox = QGroupBox("", layout=hbox)

        grid = QGridLayout()
        grid.setContentsMargins(10, 20, 10, 10)

        grid.addWidget(gbox, 0, 0, 2, 1)
        grid.addWidget(self.cup_btn, 0, 1)
        grid.addWidget(self.cdn_btn, 1, 1)
        grid.addWidget(self.max_btn, 0, 2)
        grid.addWidget(self.min_btn, 1, 2)
        grid.addWidget(self.input_button, 0, 3)
        grid.addWidget(self.output_button, 1, 3)
        grid.setColumnStretch(5, 1)

        self.setWidget(QWidget(layout=grid))