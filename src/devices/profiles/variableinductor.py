from devices import SerialDevice, DeviceWidget, CommonMessagesMixin
from qt import *


class Signals(QObject):
    inductors = Signal(int)
    input = Signal(bool)
    output = Signal(bool)

    @property
    def message_tree(self):
        return {
            "update": {
                "relays": {
                    "inductors": lambda s: self.inductors.emit(s),
                    "input": lambda s: self.input.emit(s),
                    "output": lambda s: self.output.emit(s),
                }
            }
        }


class VariableInductor(CommonMessagesMixin, SerialDevice):
    profile_name = "VariableInductor"
    max_inds = 127

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)

        self.inductors = 0
        self.signals.inductors.connect(lambda s: self.__setattr__("inductors", s))
        
        self.request_current_relays()

    def set_inds(self, value):
        self.send('{"command":{"set_inductors":%s}}' % (str(value)))

    def relays_max(self):
        self.send('{"command":{"set_inductors":127}}')

    def relays_min(self):
        self.send('{"command":{"set_inductors":0}}')

    def relays_lup(self):
        self.send('{"command":"lup"}')

    def relays_ldn(self):
        self.send('{"command":"ldn"}')
        
    def request_current_relays(self):
        self.send('{"request":"relays"}')

    def set_input_relay(self, state):
        self.send('{"command":{"input":%s}}' % (int(state)))

    def set_output_relay(self, state):
        self.send('{"command":{"output":%s}}' % (int(state)))
    
    @property
    def widget(self):
        w = VariableInductorWidget(self.title, self.guid)

        w.lup_btn.clicked.connect(self.relays_lup)
        w.ldn_btn.clicked.connect(self.relays_ldn)
        w.max_btn.clicked.connect(self.relays_max)
        w.min_btn.clicked.connect(self.relays_min)

        w.input_button.clicked.connect(self.set_input_relay)
        w.output_button.clicked.connect(self.set_output_relay)

        w.set_relays.connect(self.set_inds)

        self.signals.inductors.connect(lambda x: w.edit.setText(str(x)))
        self.signals.input.connect(w.input_button.setChecked)
        self.signals.output.connect(w.output_button.setChecked)

        return w


class VariableInductorWidget(DeviceWidget):
    set_relays = Signal(int)

    def create_widgets(self):
        self.input_button = QPushButton("Input", checkable=True)
        self.output_button = QPushButton("Output", checkable=True)

        self.lup_btn = QPushButton("LUP", autoRepeat=True)
        self.ldn_btn = QPushButton("LDN", autoRepeat=True)
        self.max_btn = QPushButton("Max")
        self.min_btn = QPushButton("Min")
        self.edit = QLineEdit()
        self.set_btn = QPushButton("Set")

    def connect_signals(self):
        self.set_btn.clicked.connect(lambda: self.set_relays.emit(int(self.edit.text())))
        self.edit.returnPressed.connect(self.set_btn.clicked)

    def build_layout(self):
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Inductors:  "))
        hbox.addWidget(self.edit)
        hbox.addWidget(self.set_btn)
        gbox = QGroupBox("", layout=hbox)

        grid = QGridLayout()
        grid.setContentsMargins(10, 20, 10, 10)

        grid.addWidget(gbox, 0, 0, 2, 1)
        grid.addWidget(self.lup_btn, 0, 1)
        grid.addWidget(self.ldn_btn, 1, 1)
        grid.addWidget(self.max_btn, 0, 2)
        grid.addWidget(self.min_btn, 1, 2)
        grid.addWidget(self.input_button, 0, 3)
        grid.addWidget(self.output_button, 1, 3)
        grid.setColumnStretch(5, 1)
        
        self.setWidget(QWidget(layout=grid))