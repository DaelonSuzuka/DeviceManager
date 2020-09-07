from qt import *
from device_manager import DeviceManager


@DeviceManager.subscribe_to("VariableCapacitor")
class VariableCapacitorWidget(QWidget):
    set_relays = Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setStyleSheet("""
            QPushButton { 
                width: 80px; 
                height: 34px;
                max-width: 80px; 
                max-height: 34px;  
            } 
        """)
        
        self.edit = QLineEdit()
        self.set_btn = QPushButton("Set")
        self.set_btn.clicked.connect(lambda: self.set_relays.emit(int(self.edit.text())))
        self.edit.returnPressed.connect(self.set_btn.clicked)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMaximum(127)
        self.slider.installEventFilter(self)

        self.cup_btn = QPushButton("CUP", autoRepeat=True)
        self.cdn_btn = QPushButton("CDN", autoRepeat=True)
        self.max_btn = QPushButton("Max", checkable=True)
        self.min_btn = QPushButton("Min", checkable=True)
        self.bypass_btn = QPushButton("Bypass", checkable=True)
        self.input_btn = QPushButton("Input", checkable=True)
        self.output_btn = QPushButton("Output", checkable=True)

        with CHBoxLayout(self) as layout:
            gbox = QGroupBox("Capacitors:")
            gbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            layout.add(gbox)
            with CVBoxLayout(gbox) as vbox:
                with CHBoxLayout(vbox) as hbox:
                    hbox.add(self.edit)
                    hbox.add(self.set_btn)

                vbox.add(self.slider)

                with CHBoxLayout(vbox) as hbox:
                    hbox.add(QPushButton('4', clicked=lambda: self.set_relays.emit(4)))
                    hbox.add(QPushButton('8', clicked=lambda: self.set_relays.emit(8)))
                    hbox.add(QPushButton('16', clicked=lambda: self.set_relays.emit(16)))
                    hbox.add(QPushButton('32', clicked=lambda: self.set_relays.emit(32)))
                    hbox.add(QPushButton('64', clicked=lambda: self.set_relays.emit(64)))
                    hbox.add(QPushButton('128', clicked=lambda: self.set_relays.emit(128)))
                    hbox.add(QPushButton('255', clicked=lambda: self.set_relays.emit(255)))

            gbox = QGroupBox("Controls:")
            gbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            layout.add(gbox)
            with CGridLayout(gbox) as grid:
                grid.add(self.cup_btn, 0, 1)
                grid.add(self.cdn_btn, 1, 1)
                grid.add(self.max_btn, 0, 2)
                grid.add(self.min_btn, 1, 2)
                grid.add(self.bypass_btn, 0, 3)
                grid.add(QPushButton(enabled=False), 1, 3)
                grid.add(self.input_btn, 0, 4)
                grid.add(self.output_btn, 1, 4)

    def eventFilter(self, watched: PySide2.QtCore.QObject, event: PySide2.QtCore.QEvent) -> bool:
        if watched == self.slider and event.type() == QEvent.MouseButtonRelease:
            self.set_relays.emit(self.slider.value())
        return False

    def caps_changed(self, caps):
        self.edit.setText(str(caps))
        self.slider.setValue(caps)
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

        self.bypass_btn.clicked.connect(device.set_bypass)
        self.input_btn.clicked.connect(device.set_input)
        self.output_btn.clicked.connect(device.set_output)

        self.set_relays.connect(device.set_caps)

        device.signals.capacitors.connect(self.caps_changed)
        device.signals.input.connect(self.input_btn.setChecked)
        device.signals.output.connect(self.output_btn.setChecked)
        device.signals.bypass.connect(self.bypass_btn.setChecked)


@DeviceManager.subscribe_to("VariableInductor")
class VariableInductorWidget(QWidget):
    set_relays = Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setStyleSheet("""
            QPushButton { 
                width: 80px; 
                height: 34px; 
                max-width: 80px; 
                max-height: 34px; 
            } 
        """)

        self.edit = QLineEdit()
        self.set_btn = QPushButton("Set")
        self.set_btn.clicked.connect(lambda: self.set_relays.emit(int(self.edit.text())))
        self.edit.returnPressed.connect(self.set_btn.clicked)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMaximum(127)
        self.slider.installEventFilter(self)

        self.lup_btn = QPushButton("LUP", autoRepeat=True)
        self.ldn_btn = QPushButton("LDN", autoRepeat=True)
        self.max_btn = QPushButton("Max", checkable=True)
        self.min_btn = QPushButton("Min", checkable=True)
        self.input_btn = QPushButton("Input", checkable=True)
        self.output_btn = QPushButton("Output", checkable=True)

        with CHBoxLayout(self) as layout:
            gbox = QGroupBox("Inductors:")
            gbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            layout.add(gbox)
            with CVBoxLayout(gbox) as vbox:
                with CHBoxLayout(vbox) as hbox:
                    hbox.add(self.edit)
                    hbox.add(self.set_btn)

                vbox.add(self.slider)

                with CHBoxLayout(vbox) as hbox:
                    hbox.add(QPushButton('0', clicked=lambda: self.set_relays.emit(0)))
                    hbox.add(QPushButton('4', clicked=lambda: self.set_relays.emit(4)))
                    hbox.add(QPushButton('8', clicked=lambda: self.set_relays.emit(8)))
                    hbox.add(QPushButton('16', clicked=lambda: self.set_relays.emit(16)))
                    hbox.add(QPushButton('32', clicked=lambda: self.set_relays.emit(32)))
                    hbox.add(QPushButton('64', clicked=lambda: self.set_relays.emit(64)))
                    hbox.add(QPushButton('127', clicked=lambda: self.set_relays.emit(127)))
            
            gbox = QGroupBox("Controls:")
            gbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            layout.add(gbox)
            with CGridLayout(gbox) as grid:
                grid.add(self.lup_btn, 0, 1)
                grid.add(self.ldn_btn, 1, 1)
                grid.add(self.max_btn, 0, 2)
                grid.add(self.min_btn, 1, 2)
                grid.add(QPushButton(enabled=False), 0, 3)
                grid.add(QPushButton(enabled=False), 1, 3)
                grid.add(self.input_btn, 0, 4)
                grid.add(self.output_btn, 1, 4)

    def eventFilter(self, watched: PySide2.QtCore.QObject, event: PySide2.QtCore.QEvent) -> bool:
        if watched == self.slider and event.type() == QEvent.MouseButtonRelease:
            self.set_relays.emit(self.slider.value())
        return False
        
    def inds_changed(self, inds):
        self.edit.setText(str(inds))
        self.slider.setValue(inds)
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
        self.setStyleSheet("""
            QPushButton { 
                width: 80px; 
                height: 34px; 
                max-width: 80px; 
                max-height: 34px; 
            } 
        """)
        
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