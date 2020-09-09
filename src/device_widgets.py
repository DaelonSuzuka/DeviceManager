from ctypes import alignment
from qt import *
from device_manager import DeviceManager


@DeviceManager.subscribe_to("VariableCapacitor")
class VariableCapacitorWidget(QWidget):
    set_relays = Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        self.edit = QLineEdit()
        self.edit.setAlignment(QtCore.Qt.AlignCenter)
        self.set_btn = QPushButton("Set")
        self.set_btn.clicked.connect(lambda: self.set_relays.emit(int(self.edit.text())))
        self.edit.returnPressed.connect(self.set_btn.clicked)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMaximum(255)
        self.slider.installEventFilter(self)

        self.up_btn = QPushButton("UP", autoRepeat=True)
        self.dn_btn = QPushButton("DN", autoRepeat=True)
        self.clear_btn = QPushButton("CLR")
        self.input_btn = QPushButton("IN", checkable=True)
        self.output_btn = QPushButton("OUT", checkable=True)
        self.shunt_btn = QPushButton("Shunt", checkable=True)

        with CVBoxLayout(self) as layout:
            gbox = QGroupBox("Variable Capacitor:")
            gbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            layout.add(gbox)
            with CVBoxLayout(gbox) as vbox:
                vbox.add(self.slider)

                with CHBoxLayout(vbox) as hbox:
                    hbox.add(QPushButton('0', clicked=lambda: self.set_relays.emit(0)))
                    hbox.add(QPushButton('4', clicked=lambda: self.set_relays.emit(4)))
                    hbox.add(QPushButton('8', clicked=lambda: self.set_relays.emit(8)))
                    hbox.add(QPushButton('16', clicked=lambda: self.set_relays.emit(16)))
                    hbox.add(QPushButton('32', clicked=lambda: self.set_relays.emit(32)))
                    hbox.add(QPushButton('64', clicked=lambda: self.set_relays.emit(64)))
                    hbox.add(QPushButton('128', clicked=lambda: self.set_relays.emit(128)))
                    hbox.add(QPushButton('255', clicked=lambda: self.set_relays.emit(255)))

                vbox.add(HLine())

                with CHBoxLayout(vbox, alignment=Qt.AlignLeft) as hbox:
                    hbox.add(self.up_btn)
                    hbox.add(self.dn_btn)
                    hbox.add(self.clear_btn)
                    hbox.add(self.input_btn)
                    hbox.add(self.output_btn)
                    hbox.add(self.shunt_btn)
                    hbox.add(self.edit)
                    hbox.add(self.set_btn)

    def eventFilter(self, watched: PySide2.QtCore.QObject, event: PySide2.QtCore.QEvent) -> bool:
        if watched == self.slider and event.type() == QEvent.MouseButtonRelease:
            self.set_relays.emit(self.slider.value())
        return False

    def caps_changed(self, caps):
        self.edit.setText(str(caps))
        self.slider.setValue(caps)

    def connected(self, device):
        self.up_btn.clicked.connect(device.relays_cup)
        self.dn_btn.clicked.connect(device.relays_cdn)

        self.input_btn.clicked.connect(device.set_input)
        self.output_btn.clicked.connect(device.set_output)
        self.shunt_btn.clicked.connect(device.set_bypass)

        self.set_relays.connect(device.set_caps)

        device.signals.capacitors.connect(self.caps_changed)
        device.signals.input.connect(self.input_btn.setChecked)
        device.signals.output.connect(self.output_btn.setChecked)
        device.signals.bypass.connect(self.shunt_btn.setChecked)


@DeviceManager.subscribe_to("VariableInductor")
class VariableInductorWidget(QWidget):
    set_relays = Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.edit = QLineEdit()
        self.edit.setAlignment(QtCore.Qt.AlignCenter)
        self.set_btn = QPushButton("Set")
        self.set_btn.clicked.connect(lambda: self.set_relays.emit(int(self.edit.text())))
        self.edit.returnPressed.connect(self.set_btn.clicked)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMaximum(127)
        self.slider.installEventFilter(self)

        self.up_btn = QPushButton("UP", autoRepeat=True)
        self.dn_btn = QPushButton("DN", autoRepeat=True)
        self.clear_btn = QPushButton("CLR")
        self.input_btn = QPushButton("IN", checkable=True)
        self.output_btn = QPushButton("OUT", checkable=True)

        with CVBoxLayout(self) as layout:
            gbox = QGroupBox("Variable Inductor:")
            gbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            layout.add(gbox)
            with CVBoxLayout(gbox) as vbox:
                vbox.add(self.slider)

                with CHBoxLayout(vbox) as hbox:
                    hbox.add(QPushButton('0', clicked=lambda: self.set_relays.emit(0)))
                    hbox.add(QPushButton('4', clicked=lambda: self.set_relays.emit(4)))
                    hbox.add(QPushButton('8', clicked=lambda: self.set_relays.emit(8)))
                    hbox.add(QPushButton('16', clicked=lambda: self.set_relays.emit(16)))
                    hbox.add(QPushButton('32', clicked=lambda: self.set_relays.emit(32)))
                    hbox.add(QPushButton('64', clicked=lambda: self.set_relays.emit(64)))
                    hbox.add(QPushButton('127', clicked=lambda: self.set_relays.emit(127)))

                vbox.add(HLine())

                with CHBoxLayout(vbox, alignment=Qt.AlignLeft) as hbox:
                    hbox.add(self.up_btn)
                    hbox.add(self.dn_btn)
                    hbox.add(self.clear_btn)
                    hbox.add(self.input_btn)
                    hbox.add(self.output_btn)
                    hbox.add(self.edit)
                    hbox.add(self.set_btn)

    def eventFilter(self, watched: PySide2.QtCore.QObject, event: PySide2.QtCore.QEvent) -> bool:
        if watched == self.slider and event.type() == QEvent.MouseButtonRelease:
            self.set_relays.emit(self.slider.value())
        return False
        
    def inds_changed(self, inds):
        self.edit.setText(str(inds))
        self.slider.setValue(inds)

    def connected(self, device):
        self.up_btn.clicked.connect(device.relays_lup)
        self.dn_btn.clicked.connect(device.relays_ldn)

        self.input_btn.clicked.connect(device.set_input)
        self.output_btn.clicked.connect(device.set_output)

        self.set_relays.connect(device.set_inds)

        device.signals.inductors.connect(self.inds_changed)
        device.signals.input.connect(self.input_btn.setChecked)
        device.signals.output.connect(self.output_btn.setChecked)


@DeviceManager.subscribe_to("RFSensor")
class RFSensorWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        self.forward = QLabel("?")
        self.reverse = QLabel("?")
        self.swr = QLabel("?")
        self.phase = QLabel("?")
        self.frequency = QLabel("?")

        with CHBoxLayout(self) as hbox:
            with CVBoxLayout(hbox) as vbox:
                vbox.addWidget(QLabel("Forward:"))
                vbox.addWidget(QLabel("Reverse:"))
                vbox.addWidget(QLabel("SWR:"))
                vbox.addWidget(QLabel("Phase:"))
                vbox.addWidget(QLabel("Frequency:"))
            hbox.addWidget(QLabel())
            hbox.addWidget(QLabel())
            hbox.addWidget(QLabel())
            with CVBoxLayout(hbox) as vbox:
                vbox.addWidget(self.forward)
                vbox.addWidget(self.reverse)
                vbox.addWidget(self.swr)
                vbox.addWidget(self.phase)
                vbox.addWidget(self.frequency)
    
    def connected(self, device):
        device.signals.forward.connect(lambda x: self.forward.setText(f"{x:.2f}"))
        device.signals.reverse.connect(lambda x: self.reverse.setText(f"{x:.2f}"))
        device.signals.swr.connect(lambda x: self.swr.setText(f"{x:.2f}"))
        device.signals.phase.connect(lambda x: self.phase.setText(f"{x}"))
        device.signals.frequency.connect(lambda x: self.frequency.setText(f"{x}"))

    def disconnected(self, guid):
        self.forward.setText("?")
        self.reverse.setText("?")
        self.swr.setText("?")
        self.phase.setText("?")
        self.frequency.setText("?")


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