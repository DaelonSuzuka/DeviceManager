from qt import *
from functools import partial
from device_manager import DeviceManager


class RadioInfo(Widget):        
    def create_widgets(self):
        self.power = QLabel("  ?  ")
        self.frequency = QLabel("  ?  ")
        self.mode = QLabel("  ?  ")
        
    def build_layout(self):
        grid = QGridLayout(self, contentsMargins=QMargins(0, 0, 0, 0))

        grid.addWidget(QLabel("Kenwood TS-480"), 0, 0, 1, 2)
        grid.addWidget(QLabel("Power:"), 1, 0)
        grid.addWidget(self.power, 1, 1)
        grid.addWidget(QLabel("Frequency:"), 2, 0)
        grid.addWidget(self.frequency, 2, 1)
        grid.addWidget(QLabel("Mode:"), 3, 0)
        grid.addWidget(self.mode, 3, 1)


class MeterInfo(Widget):        
    def create_widgets(self):
        self.forward = QLabel("  ?  ")
        self.reverse = QLabel("  ?  ")
        self.swr = QLabel("  ?  ")
        self.frequency = QLabel("  ?  ")

    def build_layout(self):
        grid = QGridLayout(self, contentsMargins=QMargins(0, 0, 0, 0))

        grid.addWidget(QLabel("Alpha 4510"), 0, 0, 1, 2)
        grid.addWidget(QLabel("Forward:"), 1, 0)
        grid.addWidget(self.forward, 1, 1)
        grid.addWidget(QLabel("Reverse:"), 2, 0)
        grid.addWidget(self.reverse, 2, 1)
        grid.addWidget(QLabel("Frequency:"), 3, 0)
        grid.addWidget(self.frequency, 3, 1)
        grid.addWidget(QLabel("SWR:"), 4, 0)
        grid.addWidget(self.swr, 4, 1)
        

class TunerInfo(Widget):        
    def create_widgets(self):
        self.forward = QLabel("  ?  ")
        self.forward_watts = QLabel("  ?  ")
        self.reverse = QLabel("  ?  ")
        self.reverse_watts = QLabel("  ?  ")
        self.swr = QLabel("  ?  ")
        self.frequency = QLabel("  ?  ")

    def build_layout(self):
        grid = QGridLayout(self, contentsMargins=QMargins(0, 0, 0, 0))

        grid.addWidget(QLabel("Forward Watts:"), 0, 1)
        grid.addWidget(self.forward_watts, 0, 2)
        grid.addWidget(QLabel("Forward:"), 1, 1)
        grid.addWidget(self.forward, 1, 2)
        grid.addWidget(QLabel("Reverse Watts:"), 2, 1)
        grid.addWidget(self.reverse_watts, 2, 2)
        grid.addWidget(QLabel("Reverse:"), 3, 1)
        grid.addWidget(self.reverse, 3, 2)
        grid.addWidget(QLabel("SWR:"), 4, 1)
        grid.addWidget(self.swr, 4, 2)
        grid.addWidget(QLabel("Frequency:"), 5, 1)
        grid.addWidget(self.frequency, 5, 2)


class InfoPanel(Widget):        
    def create_widgets(self):
        self.radio_info = RadioInfo()
        self.meter_info = MeterInfo()
        self.tuner_info = TunerInfo()

    def build_layout(self):
        grid = QGridLayout(self, contentsMargins=QMargins(0, 0, 0, 0))

        grid.addWidget(self.radio_info, 0, 0)
        grid.addWidget(HLine(), 1, 0)
        grid.addWidget(self.meter_info, 2, 0)
        # grid.addWidget(HLine(), 3, 0)
        # grid.addLayout(self.tuner_info, 4, 0)
        
        grid.setRowStretch(5, 1)


class PowerButtons(Widget):
    set_power = Signal(str)

    def create_widgets(self):
        powers = ["200", "175", "150", "125", "100", "75", "50", "25", "10", "5"]

        self.btns = QButtonGroup()
        for power in powers:
            self.btns.addButton(QPushButton(power, checkable=True))

        self.up = QPushButton("Power Up")
        self.down = QPushButton("Power Down")

    def connect_signals(self):
        self.up.clicked.connect(lambda: self.uncheck_all())
        self.down.clicked.connect(lambda: self.uncheck_all())
        
        for btn in self.btns.buttons():
            btn.clicked.connect(lambda: self.btns.setExclusive(True))
            btn.clicked.connect(partial(self.set_power.emit, btn.text()))

    def build_layout(self):
        grid = QGridLayout(self, contentsMargins=QMargins(0, 0, 0, 0))
        
        for i, btn in enumerate(self.btns.buttons()):
            grid.addWidget(btn, i, 0)
        grid.addWidget(self.up, 0, 1, 5, 1)
        grid.addWidget(self.down, 5, 1, 5, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 2)

    def uncheck_all(self):
        self.btns.setExclusive(False)
        for btn in self.btns.buttons():
            btn.setChecked(False)

    def select(self, power):
        for btn in self.btns.buttons():
            if btn.text() == power:
                btn.setChecked(True)
                self.btns.setExclusive(True)
                return


class FrequencyButtons(Widget):
    set_frequency = Signal(str)

    def create_widgets(self):
        self.freqs = [
            "50000000", "28000000", "24890000", "21000000", "18068000",
            "14000000", "10100000", "07000000", "03500000", "01800000"
        ]

        band_names = [
            "50 Mhz", "28 Mhz", "24 Mhz", "21 Mhz", "18 Mhz",
            "14 Mhz", "10 Mhz", "7 Mhz", "3.4 Mhz", "1.8 Mhz"
        ]

        self.btns = QButtonGroup()
        for band in band_names:
            self.btns.addButton(QPushButton(band, checkable=True))

        self.up = QPushButton("Band Up")
        self.down = QPushButton("Band Up")

    def connect_signals(self):
        self.up.clicked.connect(lambda: self.uncheck_all())
        self.down.clicked.connect(lambda: self.uncheck_all())
        
        for i, btn in enumerate(self.btns.buttons()):
            btn.clicked.connect(lambda: self.btns.setExclusive(True))
            btn.clicked.connect(partial(self.set_frequency.emit, self.freqs[i]))

    def build_layout(self):
        grid = QGridLayout(self, contentsMargins=QMargins(0, 0, 0, 0))
        
        for i, btn in enumerate(self.btns.buttons()):
            grid.addWidget(btn, i, 0)

        grid.addWidget(self.up, 0, 1, 5, 1)
        grid.addWidget(self.down, 5, 1, 5, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 2)

    def uncheck_all(self):
        self.btns.setExclusive(False)
        for btn in self.btns.buttons():
            btn.setChecked(False)

    def select(self, power):
        for btn in self.btns.buttons():
            if btn.text().lstrip('0') == power:
                btn.setChecked(True)
                self.btns.setExclusive(True)
                return


class DummyLoadControls(Widget):
    def create_widgets(self):
        self.cup = QPushButton("CUP")
        self.cdn = QPushButton("CDN")
        self.lup = QPushButton("LUP")
        self.ldn = QPushButton("LDN")
        self.clear = QPushButton("Bypass")
        
    def build_layout(self):
        vbox = QVBoxLayout(self, contentsMargins=QMargins(0, 0, 0, 0))
        
        vbox.addWidget(self.cup)
        vbox.addWidget(self.cdn)
        vbox.addWidget(self.lup)
        vbox.addWidget(self.ldn)
        vbox.addWidget(self.clear)


class RadioControls(Widget):
    def create_widgets(self):
        self.power_btns = PowerButtons()
        self.freq_btns = FrequencyButtons()
        self.dummy_load = DummyLoadControls()

        self.mode = QComboBox()
        self.mode.addItems(['Mode'])
        self.mode.setMinimumHeight(100)
        self.mode.setStyleSheet("QComboBox { padding-left: 20px; }")

        self.menu = QPushButton('Key Settings')

        self.key = QPushButton("Toggle Key", checkable=True)
        self.key.setStyleSheet(""" :checked { border: 5px solid red; border-radius: 10px; } """)

        self.lock = QPushButton("Lock", checkable=True)

        self.timeout = QProgressBar()
        self.timeout.setTextVisible(False)
        self.timeout.setStyleSheet('QProgressBar::chunk { background: grey; }')
        self.timeout_max = 10000
        self.timeout.setMaximum(self.timeout_max)
        self.timeout.setValue(0)

        self.timeout_timer = QTimer()
        self.timeout_timer.timeout.connect(lambda: self.update_timeout_bar())
        self.timeout_timer.start(100)
        self.current_power = 5

    def build_layout(self):
        hbox = QHBoxLayout(self, contentsMargins=QMargins(0, 0, 0, 0))

        hbox.addWidget(self.power_btns, 2)
        hbox.addWidget(VLine(), 1)
        hbox.addWidget(self.freq_btns, 2)
        hbox.addWidget(VLine(), 1)
        hbox.addWidget(self.dummy_load, 1)
        hbox.addWidget(VLine(), 1)

        vbox = QVBoxLayout(contentsMargins=QMargins(0, 0, 0, 0))
        hbox.addLayout(vbox, 2)

        vbox.addWidget(self.mode, 1)
        vbox.addWidget(self.menu, 1)
        vbox.addWidget(self.key, 4)
        vbox.addWidget(self.timeout, 1)

    def update_timeout_bar(self):
        val = self.timeout.value()

        if self.timeout.isEnabled():
            if self.key.isChecked():
                if val < self.timeout_max:
                    if val + self.current_power > self.timeout_max:
                        self.timeout.setValue(self.timeout_max)
                    else:
                        self.timeout.setValue(val + self.current_power)

                if val >= self.timeout_max - 1:
                    self.key.clicked.emit()
                    self.timeout.setValue(0)
                    # self.key.setChecked(False)
                    # self.key.setEnabled(False)
                    # self.key.setStyleSheet(self.key_stylesheet_overheated)
            else:
                if val > 0:
                    if (val - self.current_power) < 0:
                        self.timeout.setValue(0)
                    else:
                        self.timeout.setValue(val - 50)

                # if val == 0:
                #     self.key.setEnabled(True)
                    # self.key.setStyleSheet("")
                    # self.key.setStyleSheet(self.key_stylesheet_normal)

    def set_power(self, power):
        self.current_power = int(power)

    def select_mode(self, mode):
        for i in range(self.mode.count()):
            if self.mode.itemText(i) == mode:
                self.mode.setCurrentIndex(i)


class SwitchControls(Widget):
    def create_widgets(self):
        self.one = QPushButton("Ant 1", checkable=True)
        self.two = QPushButton("Ant 2", checkable=True)
        self.three = QPushButton("Ant 3", checkable=True)
        self.four = QPushButton("Ant 4", checkable=True)

        self.btns = QButtonGroup()
        self.btns.addButton(self.one)
        self.btns.addButton(self.two)
        self.btns.addButton(self.three)
        self.btns.addButton(self.four)

    def build_layout(self):
        grid = QGridLayout(self, contentsMargins=QMargins(0, 0, 0, 0))
        
        grid.addWidget(self.one, 0, 0)
        grid.addWidget(self.two, 0, 1)
        grid.addWidget(self.three, 0, 2)
        grid.addWidget(self.four, 0, 3)


class ControlPanel(Widget):        
    def create_widgets(self):
        self.radio = RadioControls()
        self.switch = SwitchControls()

        self.radio.setEnabled(False)
        self.switch.setEnabled(False)

    def build_layout(self):
        grid = QGridLayout(self, contentsMargins=QMargins(0, 0, 0, 0))
        
        grid.addWidget(self.radio, 0, 0)
        grid.setRowStretch(0, 4)
        grid.addWidget(HLine(), 1, 0)
        grid.addWidget(self.switch, 2, 0)
        grid.setRowStretch(2, 1)


@DeviceManager.subscribe
class ServitorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget { font-size: 16pt; }
            QPushButton { 
                max-width: 2000px; 
                max-height: 2000px; 
            } 
        """)

        self.devices = {}
        self.radio = None
        self.meter = None
        self.switch = None
        self.dummy_load = None

        self.info_panel = InfoPanel()
        self.control_panel = ControlPanel()

        grid = QGridLayout(self)

        grid.addWidget(self.info_panel, 0, 0)
        grid.setColumnStretch(0, 2)
        grid.addWidget(VLine(), 0, 1)
        grid.addWidget(self.control_panel, 0, 2)
        grid.setColumnStretch(2, 7)

    def connect_meter(self, meter):
        if self.meter:
            return
        self.meter = meter

        meter.signals.forward.connect(lambda s: self.info_panel.meter_info.forward.setText(s))
        meter.signals.reverse.connect(lambda s: self.info_panel.meter_info.reverse.setText(s))
        meter.signals.swr.connect(lambda s: self.info_panel.meter_info.swr.setText(s))
        meter.signals.frequency.connect(lambda s: self.info_panel.meter_info.frequency.setText(s))

    def disconnect_meter(self, guid):
        if self.meter.guid != guid:
            return
        self.meter = None

        self.info_panel.meter_info.forward.setText("  ?  ")
        self.info_panel.meter_info.reverse.setText("  ?  ")
        self.info_panel.meter_info.swr.setText("  ?  ")
        self.info_panel.meter_info.frequency.setText("  ?  ")
        
    def connect_radio(self, radio):
        if self.radio:
            return
        self.radio = radio

        radio.signals.power.connect(lambda s: self.info_panel.radio_info.power.setText(s))
        radio.signals.power.connect(lambda s: self.control_panel.radio.power_btns.select(s))
        radio.signals.power.connect(lambda s: self.control_panel.radio.set_power(s))
        radio.signals.frequency.connect(lambda s: self.info_panel.radio_info.frequency.setText(s))
        radio.signals.frequency.connect(lambda s: self.control_panel.radio.freq_btns.select(s))
        radio.signals.mode.connect(lambda s: self.info_panel.radio_info.mode.setText(s))
        radio.signals.mode.connect(lambda s: self.control_panel.radio.select_mode(s))

        radio.signals.keyed.connect(lambda: self.control_panel.radio.key.setChecked(True))
        radio.signals.unkeyed.connect(lambda: self.control_panel.radio.key.setChecked(False))

        self.control_panel.radio.key.clicked.connect(radio.toggle_key)
        self.control_panel.radio.mode.activated.connect(lambda: radio.set_mode(self.control_panel.radio.mode.currentText()))

        self.control_panel.radio.freq_btns.up.clicked.connect(radio.band_up)
        self.control_panel.radio.freq_btns.down.clicked.connect(radio.band_down)
        self.control_panel.radio.freq_btns.set_frequency.connect(radio.set_vfoA_frequency)

        self.control_panel.radio.power_btns.up.clicked.connect(radio.increase_power_level)
        self.control_panel.radio.power_btns.down.clicked.connect(radio.decrease_power_level)
        self.control_panel.radio.power_btns.set_power.connect(radio.set_power_level)
        
        self.control_panel.radio.mode.clear()
        self.control_panel.radio.mode.addItems([m for m in radio.modes if m != ""])
        self.control_panel.radio.setEnabled(True)
        
        if not self.switch:
            self.control_panel.switch.setEnabled(False)

        radio.unkey()
        radio.get_power_level()
        radio.get_mode()
        radio.get_vfoA_frequency()

    def disconnect_radio(self, guid):
        if self.radio.guid != guid:
            return
        self.radio = None

        self.control_panel.radio.setEnabled(False)
        self.info_panel.radio_info.power.setText("  ?  ")
        self.info_panel.radio_info.frequency.setText("  ?  ")
        self.info_panel.radio_info.mode.setText("  ?  ")
        
        self.control_panel.radio.mode.clear()
        self.control_panel.radio.mode.addItem("Mode")

    def connect_switch(self, switch):
        if self.switch:
            return
        self.switch = switch

        self.control_panel.switch.setEnabled(True)

        self.control_panel.switch.one.clicked.connect(lambda: switch.select_antenna(1))
        self.control_panel.switch.two.clicked.connect(lambda: switch.select_antenna(2))
        self.control_panel.switch.three.clicked.connect(lambda: switch.select_antenna(3))
        self.control_panel.switch.four.clicked.connect(lambda: switch.select_antenna(4))

        switch.read_antenna()
        switch.read_antenna()

    def disconnect_switch(self, guid):
        if self.switch.guid != guid:
            return
        self.switch = None

        self.control_panel.switch.setEnabled(False)

    def on_device_added(self, device):
        self.devices[device.guid] = device

        if device.profile_name == "Alpha4510A":
            self.connect_meter(device)

        if device.profile_name == "TS-480":
            self.connect_radio(device)

        if device.profile_name == "DTS-4":
            self.connect_switch(device)

    def on_device_removed(self, guid):
        if self.devices[guid].profile_name == "Alpha4510A":
            self.disconnect_meter(guid)

        if self.devices[guid].profile_name == "TS-480":
            self.disconnect_radio(guid)

        if self.devices[guid].profile_name == "DTS-4":
            self.disconnect_switch(guid)

        self.devices.pop(guid)


class ServitorSubWindow(QMdiSubWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(QPixmap(1,1)))
        self.setWindowTitle('Servitor Controls')

        self.setWidget(ServitorWidget(self))