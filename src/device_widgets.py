from qt import *
from device_manager import DeviceManager


@DeviceManager.subscribe_to("VariableCapacitor")
class VariableCapacitorWidget(Widget):
    set_relays = Signal(int)

    def create_widgets(self):
        self.edit = QLineEdit()
        self.set_btn = QPushButton("Set")

        self.cup_btn = QPushButton("CUP", autoRepeat=True)
        self.cdn_btn = QPushButton("CDN", autoRepeat=True)
        self.max_btn = QPushButton("Max")
        self.min_btn = QPushButton("Min")
        self.bypass_btn = QPushButton("Bypass")
        self.input_btn = QPushButton("Input", checkable=True)
        self.output_btn = QPushButton("Output", checkable=True)

    def connect_signals(self):
        self.set_btn.clicked.connect(lambda: self.set_relays.emit(int(self.edit.text())))
        self.edit.returnPressed.connect(self.set_btn.clicked)

    def build_layout(self):
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Capacitors: "))
        hbox.addWidget(self.edit)
        hbox.addWidget(self.set_btn)
        gbox = QGroupBox("", layout=hbox)

        grid = QGridLayout(self)
        grid.setContentsMargins(10, 20, 10, 10)

        grid.addWidget(gbox, 0, 0, 2, 1)
        grid.addWidget(self.cup_btn, 0, 1)
        grid.addWidget(self.cdn_btn, 1, 1)
        grid.addWidget(self.max_btn, 0, 2)
        grid.addWidget(self.min_btn, 1, 2)
        grid.addWidget(self.bypass_btn, 0, 3)
        grid.addWidget(self.input_btn, 0, 4)
        grid.addWidget(self.output_btn, 1, 4)
        grid.setColumnStretch(5, 1)
        
        self.setEnabled(False)

    def connected(self, device):
        self.cup_btn.clicked.connect(device.relays_cup)
        self.cdn_btn.clicked.connect(device.relays_cdn)
        self.max_btn.clicked.connect(device.relays_max)
        self.min_btn.clicked.connect(device.relays_min)
        self.min_btn.clicked.connect(device.relays_min)

        self.bypass_btn.clicked.connect(device.set_bypass)
        
        self.input_btn.clicked.connect(device.set_input_relay)
        self.output_btn.clicked.connect(device.set_output_relay)

        self.set_relays.connect(device.set_caps)

        device.signals.capacitors.connect(lambda x: self.edit.setText(str(x)))
        device.signals.input.connect(self.input_btn.setChecked)
        device.signals.output.connect(self.output_btn.setChecked)

        self.setEnabled(True)

    def disconnected(self, guid):
        self.setEnabled(False)


@DeviceManager.subscribe_to("VariableInductor")
class VariableInductorWidget(Widget):
    set_relays = Signal(int)

    def create_widgets(self):
        self.input_btn = QPushButton("Input", checkable=True)
        self.output_btn = QPushButton("Output", checkable=True)

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

        grid = QGridLayout(self)
        grid.setContentsMargins(10, 20, 10, 10)

        grid.addWidget(gbox, 0, 0, 2, 1)
        grid.addWidget(self.lup_btn, 0, 1)
        grid.addWidget(self.ldn_btn, 1, 1)
        grid.addWidget(self.max_btn, 0, 2)
        grid.addWidget(self.min_btn, 1, 2)
        grid.addWidget(self.input_btn, 0, 3)
        grid.addWidget(self.output_btn, 1, 3)
        grid.setColumnStretch(5, 1)

        self.setEnabled(False)
        
    def connected(self, device):
        self.lup_btn.clicked.connect(device.relays_lup)
        self.ldn_btn.clicked.connect(device.relays_ldn)
        self.max_btn.clicked.connect(device.relays_max)
        self.min_btn.clicked.connect(device.relays_min)

        self.input_btn.clicked.connect(device.set_input_relay)
        self.output_btn.clicked.connect(device.set_output_relay)

        self.set_relays.connect(device.set_inds)

        device.signals.inductors.connect(lambda x: self.edit.setText(str(x)))
        device.signals.input.connect(self.input_btn.setChecked)
        device.signals.output.connect(self.output_btn.setChecked)
        
        self.setEnabled(True)

    def disconnected(self, guid):
        self.setEnabled(False)


@DeviceManager.subscribe_to("RFSensor")
class RFSensorWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rf_panel = RFPanel()

        grid = QGridLayout(self)
        grid.setContentsMargins(10, 20, 10, 10)

        grid.addWidget(self.rf_panel, 0, 0)
        grid.setRowStretch(2, 1)

        self.setEnabled(False)

    def connected(self, device):
        device.signals.forward.connect(lambda x: self.rf_panel.forward.setText(f"{x:10.2f}"))
        device.signals.reverse.connect(lambda x: self.rf_panel.reverse.setText(f"{x:10.2f}"))
        device.signals.phase.connect(lambda x: self.rf_panel.phase.setText(f"{x}"))
        device.signals.frequency.connect(lambda x: self.rf_panel.frequency.setText(f"{x}"))

        self.setEnabled(True)

    def disconnected(self, guid):
        self.setEnabled(False)


class RFPanel(QGroupBox):
    def __init__(self):
        super().__init__("RF Sensor")
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        
        # create widgets
        self.frequency = QLabel("?")
        self.forward = QLabel("?")
        self.phase = QLabel("?")
        self.reverse = QLabel("?")

        # create layout
        grid = QGridLayout(self)
        grid.addWidget(QLabel("Forward:"), 0, 0)
        grid.addWidget(self.forward, 0, 1)
        grid.addWidget(QLabel("Reverse:"), 0, 2)
        grid.addWidget(self.reverse, 0, 3)
        grid.addWidget(QLabel("Phase:"), 0, 4)
        grid.addWidget(self.phase, 0, 5)
        grid.addWidget(QLabel("Frequency:"), 0, 6)
        grid.addWidget(self.frequency, 0, 7)


@DeviceManager.subscribe_to("SW-100")
class SW100Widget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ant_btns = AntennaButtons()

        grid = QGridLayout(self)
        grid.setContentsMargins(10, 20, 10, 10)

        grid.addWidget(self.ant_btns, 0, 0)
        grid.setColumnStretch(5, 1)

        self.setEnabled(False)

    def connected(self, device):
        self.ant_btns.rx.clicked.connect(lambda: device.set_antenna("tx"))
        self.ant_btns.none.clicked.connect(lambda: device.set_antenna("none"))
        self.ant_btns.tx.clicked.connect(lambda: device.set_antenna("rx")) 

        device.signals.antenna.connect(self.ant_btns.select_antenna)

        self.setEnabled(True)

    def disconnected(self, guid):
        self.setEnabled(False)


class AntennaButtons(QGroupBox):
    def __init__(self):
        super().__init__("SW-100")
        
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