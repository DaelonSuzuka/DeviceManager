from qt import *
from codex import DeviceManager


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
        self.down_btn = QPushButton("DN", autoRepeat=True)
        self.clear_btn = QPushButton("CLR")
        self.input_btn = QPushButton("IN", checkable=True)
        self.output_btn = QPushButton("OUT", checkable=True)

        with CVBoxLayout(self) as layout:
            gbox = QGroupBox("Variable Inductor:")
            gbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            layout.add(gbox)
            with CVBoxLayout(gbox) as vbox:
                with CHBoxLayout(vbox, alignment=Qt.AlignLeft) as hbox:
                    hbox.add(self.edit)
                    hbox.add(self.set_btn)
                    hbox.add(self.up_btn)
                    hbox.add(self.down_btn)
                    hbox.add(self.clear_btn)
                    hbox.add(self.input_btn)
                    hbox.add(self.output_btn)

                vbox.add(HLine())
                vbox.add(self.slider)

                with CHBoxLayout(vbox) as hbox:
                    hbox.add(QPushButton('0', clicked=lambda: self.set_relays.emit(0)))
                    hbox.add(QPushButton('4', clicked=lambda: self.set_relays.emit(4)))
                    hbox.add(QPushButton('8', clicked=lambda: self.set_relays.emit(8)))
                    hbox.add(QPushButton('16', clicked=lambda: self.set_relays.emit(16)))
                    hbox.add(QPushButton('32', clicked=lambda: self.set_relays.emit(32)))
                    hbox.add(QPushButton('64', clicked=lambda: self.set_relays.emit(64)))
                    hbox.add(QPushButton('127', clicked=lambda: self.set_relays.emit(127)))

    def eventFilter(self, watched: PySide2.QtCore.QObject, event: PySide2.QtCore.QEvent) -> bool:
        if watched == self.slider and event.type() == QEvent.MouseButtonRelease:
            self.set_relays.emit(self.slider.value())
        return False
        
    def inds_changed(self, inds):
        self.edit.setText(str(inds))
        self.slider.setValue(inds)

    def connected(self, device):
        self.up_btn.clicked.connect(device.relays_lup)
        self.down_btn.clicked.connect(device.relays_ldn)
        self.clear_btn.clicked.connect(lambda: self.set_relays.emit(0))
        self.input_btn.clicked.connect(device.set_input)
        self.output_btn.clicked.connect(device.set_output)

        self.set_relays.connect(device.set_inds)

        device.signals.inductors.connect(self.inds_changed)
        device.signals.input.connect(self.input_btn.setChecked)
        device.signals.output.connect(self.output_btn.setChecked)
        device.request_current_relays()