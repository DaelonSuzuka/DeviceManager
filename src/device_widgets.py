from qt import *
from device_manager import DeviceManager


@DeviceManager.subscribe_to("VariableCapacitor")
class VariableCapacitorWidget(QWidget):
    set_relays = Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QPushButton { 
                width: 80px; 
                height: 34px; 
            } 
        """)
        
        self.edit = QLineEdit()
        self.set_btn = QPushButton("Set")
        self.set_btn.clicked.connect(lambda: self.set_relays.emit(int(self.edit.text())))
        self.edit.returnPressed.connect(self.set_btn.clicked)

        self.cup_btn = QPushButton("CUP", autoRepeat=True)
        self.cdn_btn = QPushButton("CDN", autoRepeat=True)
        self.max_btn = QPushButton("Max", checkable=True)
        self.min_btn = QPushButton("Min", checkable=True)
        self.bypass_btn = QPushButton("Bypass", checkable=True)
        self.input_btn = QPushButton("Input", checkable=True)
        self.output_btn = QPushButton("Output", checkable=True)

        with CHBoxLayout(self) as layout:
            gbox = QGroupBox("Capacitors:")
            layout.addWidget(gbox)
            with CVBoxLayout(gbox) as vbox:
                with CHBoxLayout(vbox) as hbox:
                    hbox.addWidget(self.edit)
                    hbox.addWidget(self.set_btn)
                with CHBoxLayout(vbox) as hbox:
                    hbox.addWidget(QPushButton())
                    hbox.addWidget(QPushButton())
                    hbox.addWidget(QPushButton())
                    hbox.addWidget(QPushButton())
                    hbox.addWidget(QPushButton())
                    hbox.addWidget(QPushButton())

            gbox = QGroupBox("Controls:")
            layout.addWidget(gbox)
            with CGridLayout(gbox) as grid:
                grid.addWidget(self.cup_btn, 0, 1)
                grid.addWidget(self.cdn_btn, 1, 1)
                grid.addWidget(self.max_btn, 0, 2)
                grid.addWidget(self.min_btn, 1, 2)
                grid.addWidget(self.bypass_btn, 0, 3)
                grid.addWidget(QPushButton(enabled=False), 1, 3)
                grid.addWidget(self.input_btn, 0, 4)
                grid.addWidget(self.output_btn, 1, 4)
            
        self.setEnabled(False)

    def caps_changed(self, caps):
        self.edit.setText(str(caps))
        if caps == 255:
            self.max_btn.setChecked(True)
        if caps == 0:
            self.min_btn.setChecked(True)
        if caps < 255:
            self.max_btn.setChecked(False)
        if caps > 0:
            self.min_btn.setChecked(False)

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

        device.signals.capacitors.connect(self.caps_changed)
        device.signals.input.connect(self.input_btn.setChecked)
        device.signals.output.connect(self.output_btn.setChecked)
        device.signals.bypass.connect(self.bypass_btn.setChecked)

        self.setEnabled(True)

    def disconnected(self, guid):
        self.setEnabled(False)


@DeviceManager.subscribe_to("VariableInductor")
class VariableInductorWidget(QWidget):
    set_relays = Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QPushButton { 
                width: 80px; 
                height: 34px; 
            } 
        """)

        self.edit = QLineEdit()
        self.set_btn = QPushButton("Set")
        self.set_btn.clicked.connect(lambda: self.set_relays.emit(int(self.edit.text())))
        self.edit.returnPressed.connect(self.set_btn.clicked)

        self.lup_btn = QPushButton("LUP", autoRepeat=True)
        self.ldn_btn = QPushButton("LDN", autoRepeat=True)
        self.max_btn = QPushButton("Max", checkable=True)
        self.min_btn = QPushButton("Min", checkable=True)
        self.input_btn = QPushButton("Input", checkable=True)
        self.output_btn = QPushButton("Output", checkable=True)

        with CHBoxLayout(self) as layout:
            gbox = QGroupBox("Inductors:")
            layout.addWidget(gbox)
            with CVBoxLayout(gbox) as vbox:
                with CHBoxLayout(vbox) as hbox:
                    hbox.addWidget(self.edit)
                    hbox.addWidget(self.set_btn)
                with CHBoxLayout(vbox) as hbox:
                    hbox.addWidget(QPushButton())
                    hbox.addWidget(QPushButton())
                    hbox.addWidget(QPushButton())
                    hbox.addWidget(QPushButton())
                    hbox.addWidget(QPushButton())
                    hbox.addWidget(QPushButton())
            
            gbox = QGroupBox("Controls:")
            layout.addWidget(gbox)
            with CGridLayout(gbox) as grid:
                grid.addWidget(self.lup_btn, 0, 1)
                grid.addWidget(self.ldn_btn, 1, 1)
                grid.addWidget(self.max_btn, 0, 2)
                grid.addWidget(self.min_btn, 1, 2)
                grid.addWidget(QPushButton(enabled=False), 0, 3)
                grid.addWidget(QPushButton(enabled=False), 1, 3)
                grid.addWidget(self.input_btn, 0, 4)
                grid.addWidget(self.output_btn, 1, 4)

        self.setEnabled(False)
        
    def inds_changed(self, inds):
        self.edit.setText(str(inds))
        if inds == 127:
            self.max_btn.setChecked(True)
        if inds == 0:
            self.min_btn.setChecked(True)
        if inds < 127:
            self.max_btn.setChecked(False)
        if inds > 0:
            self.min_btn.setChecked(False)

    def connected(self, device):
        self.lup_btn.clicked.connect(device.relays_lup)
        self.ldn_btn.clicked.connect(device.relays_ldn)
        self.max_btn.clicked.connect(device.relays_max)
        self.min_btn.clicked.connect(device.relays_min)

        self.input_btn.clicked.connect(device.set_input_relay)
        self.output_btn.clicked.connect(device.set_output_relay)

        self.set_relays.connect(device.set_inds)

        device.signals.inductors.connect(self.inds_changed)
        device.signals.input.connect(self.input_btn.setChecked)
        device.signals.output.connect(self.output_btn.setChecked)
        
        self.setEnabled(True)

    def disconnected(self, guid):
        self.setEnabled(False)


@DeviceManager.subscribe_to("RFSensor")
class RFSensorWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.forward = QLabel("?")
        self.reverse = QLabel("?")
        self.swr = QLabel("?")
        self.phase = QLabel("?")
        self.frequency = QLabel("?")

        with CVBoxLayout(self) as vbox:
            with CHBoxLayout(vbox) as hbox:
                hbox.addWidget(QLabel("Forward:"))
                hbox.addWidget(self.forward)
                hbox.addWidget(QLabel("Reverse:"))
                hbox.addWidget(self.reverse)
                hbox.addWidget(QLabel("SWR:"))
                hbox.addWidget(self.swr)

            with CHBoxLayout(vbox) as hbox:
                hbox.addWidget(QLabel("Phase:"))
                hbox.addWidget(self.phase)
                hbox.addWidget(QLabel("Frequency:"))
                hbox.addWidget(self.frequency)

        self.setEnabled(False)

    def connected(self, device):
        device.signals.forward.connect(lambda x: self.forward.setText(f"{x:10.2f}"))
        device.signals.reverse.connect(lambda x: self.reverse.setText(f"{x:10.2f}"))
        device.signals.phase.connect(lambda x: self.phase.setText(f"{x}"))
        device.signals.frequency.connect(lambda x: self.frequency.setText(f"{x}"))

        self.setEnabled(True)

    def disconnected(self, guid):
        self.setEnabled(False)


@DeviceManager.subscribe_to("SW-100")
class SW100Widget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.rx = QPushButton("RX", checkable=True)
        self.none = QPushButton("none", checkable=True, checked=True)
        self.tx = QPushButton("TX", checkable=True)

        with CVBoxLayout(self) as vbox:
            with CHBoxLayout(vbox) as hbox:
                hbox.addWidget(self.rx)
                hbox.addWidget(self.none)
                hbox.addWidget(self.tx)

        self.setEnabled(False)

    def connected(self, device):
        self.rx.clicked.connect(lambda: device.set_antenna("tx"))
        self.none.clicked.connect(lambda: device.set_antenna("none"))
        self.tx.clicked.connect(lambda: device.set_antenna("rx")) 

        device.signals.antenna.connect(self.select_antenna)

        self.setEnabled(True)

    def disconnected(self, guid):
        self.setEnabled(False)

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