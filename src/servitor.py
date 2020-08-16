from qt import *
from functools import partial
from device_manager import DeviceManager
import qtawesome as qta
from style import qcolors


class RadioInfo(Widget):        
    def create_widgets(self):
        self.radio = None
        self.placeholder = "  ?  "

        self.power = QLabel("  ?  ")
        self.frequency = QLabel("  ?  ")
        self.mode = QLabel("  ?  ")
        
    def build_layout(self):
        grid = CGridLayout(self, contentsMargins=QMargins(0, 0, 0, 0))

        grid.add(QLabel("Kenwood TS-480"), 0, 0, 1, 2)
        grid.add(QLabel("Power:"), 1, 0)
        grid.add(self.power, 1, 1)
        grid.add(QLabel("Frequency:"), 2, 0)
        grid.add(self.frequency, 2, 1)
        grid.add(QLabel("Mode:"), 3, 0)
        grid.add(self.mode, 3, 1)

    def connect_radio(self, radio):
        if self.radio:
            return
        self.radio = radio
        
        radio.signals.power.connect(lambda s: self.power.setText(s))
        radio.signals.frequency.connect(lambda s: self.frequency.setText(s))
        radio.signals.mode.connect(lambda s: self.mode.setText(s))

    def disconnect_radio(self, guid):
        if self.radio.guid != guid:
            return
        self.radio = None
        
        self.power.setText("  ?  ")
        self.frequency.setText("  ?  ")
        self.mode.setText("  ?  ")


class MeterInfo(Widget):        
    def create_widgets(self):
        self.meter = None
        
        self.forward = QLabel("  ?  ")
        self.reverse = QLabel("  ?  ")
        self.swr = QLabel("  ?  ")
        self.frequency = QLabel("  ?  ")

    def build_layout(self):
        grid = CGridLayout(self, contentsMargins=QMargins(0, 0, 0, 0))

        grid.add(QLabel("Alpha 4510"), 0, 0, 1, 2)
        grid.add(QLabel("Forward:"), 1, 0)
        grid.add(self.forward, 1, 1)
        grid.add(QLabel("Reverse:"), 2, 0)
        grid.add(self.reverse, 2, 1)
        grid.add(QLabel("Frequency:"), 3, 0)
        grid.add(self.frequency, 3, 1)
        grid.add(QLabel("SWR:"), 4, 0)
        grid.add(self.swr, 4, 1)

    def connect_meter(self, meter):
        if self.meter:
            return
        self.meter = meter

        meter.signals.forward.connect(lambda s: self.forward.setText(s))
        meter.signals.reverse.connect(lambda s: self.reverse.setText(s))
        meter.signals.swr.connect(lambda s: self.swr.setText(s))
        meter.signals.frequency.connect(lambda s: self.frequency.setText(s))

    def disconnect_meter(self, guid):
        if self.meter.guid != guid:
            return
        self.meter = None

        self.forward.setText("  ?  ")
        self.reverse.setText("  ?  ")
        self.swr.setText("  ?  ")
        self.frequency.setText("  ?  ")


class InfoPanel(Widget):        
    def create_widgets(self):
        self.radio_info = RadioInfo()
        self.meter_info = MeterInfo()

    def build_layout(self):
        grid = CGridLayout(self, contentsMargins=QMargins(0, 0, 0, 0))

        grid.add(self.radio_info, 0, 0)
        grid.add(HLine(), 1, 0)
        grid.add(self.meter_info, 2, 0)
        
        grid.setRowStretch(5, 1)


class LockButton(ConfirmToggleButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setToolTip('Lock Power Output')
        self.icons = [
            qta.icon('fa.lock', color=qcolors.gray),
            qta.icon('fa.question-circle-o', color=qcolors.gray),
            qta.icon('fa.unlock-alt', color=qcolors.red)
        ]
        self.state = 0


class PowerButtons(Widget):
    power_changed = Signal(str)

    def create_widgets(self):
        self.power = '5'
        self.limit = True

        grid = CGridLayout(self, contentsMargins=QMargins(0, 0, 0, 0))
        self.btns = QButtonGroup()

        powers = ["200", "175", "150", "125", "100", "75", "50", "25", "10", "5"]
        for i, power in enumerate(powers):
            btn = QPushButton(power, checkable=True)
            self.btns.addButton(btn)
            grid.add(btn, i + 1, 0)
            btn.clicked.connect(lambda: self.btns.setExclusive(True))
            btn.clicked.connect(partial(self.update_power, btn.text()))

        self.lock = grid.add(LockButton(), 0, 0)
        self.lock.setIconSize(QSize(35, 35))

        grid.add(QPushButton(disabled=True), 0, 1)
        grid.add(QPushButton(disabled=True), 0, 2)
        grid.add(QPushButton('+', clicked=lambda: self.update_power(int(self.power) + 5)), 1, 1, 5, 2)
        grid.add(QPushButton('-', clicked=lambda: self.update_power(int(self.power) - 5)), 6, 1, 5, 2)

        self.lock.toggled.connect(lambda s: self.set_limit(not s))
        self.set_limit(True)

    def update_power(self, power):
        power = str(power)
        if self.limit:
            if int(power) > 100:
                power = '100'
        self.power_changed.emit(power)

    def set_power(self, power):
        self.power = power
        
        self.uncheck_all()
        self.select(power)

    def set_limit(self, limit):
        self.limit = limit
        if limit == True:
            self.update_power(self.power)
            
            for btn in self.btns.buttons():
                if int(btn.text()) > 100:
                    btn.setEnabled(False)

        else:
            for btn in self.btns.buttons():
                btn.setEnabled(True)

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


        grid = CGridLayout(self, contentsMargins=QMargins(0, 0, 0, 0))
        self.btns = QButtonGroup()

        band_names = ["50", "28", "24", "21", "18", "14", "10", "7", "3.4", "1.8"]
        for i, band in enumerate(band_names):
            btn = QPushButton(band + ' Mhz', checkable=True)
            self.btns.addButton(btn)
            grid.add(btn, i + 1, 0)
            btn.clicked.connect(lambda: self.btns.setExclusive(True))
            btn.clicked.connect(partial(self.set_frequency.emit, self.freqs[i]))
        
        grid.add(QPushButton(disabled=True), 0, 0)
        grid.add(QPushButton(disabled=True), 0, 1)
        grid.add(QPushButton(disabled=True), 0, 2)

        icon = qta.icon('mdi.arrow-up', color=qcolors.gray)
        self.up = QPushButton(icon, '', iconSize=QSize(80, 80))
        self.up.clicked.connect(lambda: self.uncheck_all())
        grid.add(self.up, 1, 1, 5, 2)

        icon = qta.icon('mdi.arrow-down', color=qcolors.gray)
        self.down = QPushButton(icon, '', iconSize=QSize(80, 80))
        self.down.clicked.connect(lambda: self.uncheck_all())
        grid.add(self.down, 6, 1, 5, 2)

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
        vbox = CVBoxLayout(self)
        self.cup = vbox.add(QPushButton("CUP"))
        self.cdn = vbox.add(QPushButton("CDN"))
        self.lup = vbox.add(QPushButton("LUP"))
        self.ldn = vbox.add(QPushButton("LDN"))
        self.clear = vbox.add(QPushButton("Bypass"))


class HeatButton(StateButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setToolTip('Thermal Protection')
        self.icons = [
            qta.icon('mdi.circle-outline', color='gray'),
            qta.icon('mdi.circle-slice-1', color=qcolors.silver),
            qta.icon('mdi.circle-slice-2', color=qcolors.silver),
            qta.icon('mdi.circle-slice-3', color=qcolors.yellow),
            qta.icon('mdi.circle-slice-4', color=qcolors.yellow),
            qta.icon('mdi.circle-slice-5', color=qcolors.orange),
            qta.icon('mdi.circle-slice-6', color=qcolors.orange),
            qta.icon('mdi.circle-slice-7', color=qcolors.red),
            qta.icon('mdi.circle-slice-8', color=qcolors.red),
            qta.icon('mdi.alert-circle-outline', color=qcolors.red),
        ]
        
        self.state = 0


class TimeoutButton(IconToggleButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setToolTip('Radio Timeout')
        self.icon_unchecked = qta.icon('mdi.timer', color='gray')
        self.icon_checked = qta.icon('mdi.timer-off', color=qcolors.red)
        self.update_icon()


class KeyButton(IconToggleButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIconSize(QSize(100, 100))
        self.setStyleSheet(""" :checked { border: 5px solid #FF4136; border-radius: 10px; } """)
        self.icon_checked = qta.icon('mdi.radio-tower', color=qcolors.silver)
        self.icon_unchecked = qta.icon('mdi.radio-tower', color='gray')
        self.update_icon()


class ModeComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QListView { 
                background-color: palette(button); 
            }
            QListView::item {
                min-height: 40px; 
                max-height: 80px; 
            }
        """)
        self.setView(QListView(self))
        self.addItems(['Mode'])
        self.setMinimumHeight(40)
        self.setMaximumHeight(100)

    def addItems(self, texts):
        super().addItems(['    ' + t for t in texts])

    def showPopup(self):
        super().showPopup()
        popup = self.findChild(QFrame)
        popup.move(popup.x(), self.mapToGlobal(self.rect().bottomLeft()).y())


class TimeoutBar(QProgressBar):
    timeout = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet('QProgressBar::chunk { background: grey; }')
        
        self.setTextVisible(False)
        self.timeout_max = 50000
        self.setMaximum(self.timeout_max)
        self.setValue(0)

        self.running = False
        self.suppressed = False
        self.current_power = 5

        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.update_timeout_bar())
        self.timer.start(20)

    def set_running(self, running):
        self.running = running

    def set_suppressed(self, suppressed):
        self.suppressed = suppressed

    def update_timeout_bar(self):
        val = self.value()

        if self.isEnabled():
            if self.running and not self.suppressed:
                if val < self.timeout_max:
                    if val + self.current_power > self.timeout_max:
                        self.setValue(self.timeout_max)
                    else:
                        self.setValue(val + self.current_power)

                if val >= self.timeout_max - 1:
                    self.timeout.emit()
                    self.setValue(0)
            else:
                if val > 0:
                    if (val - 500) < 0:
                        self.setValue(0)
                    else:
                        self.setValue(val - 500)


class RadioControls(Widget):
    def create_widgets(self):
        self.radio = None

        self.power_btns = PowerButtons()
        self.freq_btns = FrequencyButtons()
        self.dummy_load = DummyLoadControls(enabled=False)

        self.mode = ModeComboBox()

        self.heat = HeatButton()
        self.time = TimeoutButton()

        self.timeout = TimeoutBar()
        self.key = KeyButton()

        self.time.toggled.connect(self.timeout.set_suppressed)
        self.key.toggled.connect(self.timeout.set_running)
        self.timeout.timeout.connect(lambda: self.key.setChecked(False))

    def build_layout(self):
        with CHBoxLayout(self) as hbox:
            hbox.add(self.power_btns, 2)
            hbox.add(VLine(), 1)
            hbox.add(self.freq_btns, 2)
            hbox.add(VLine(), 1)
            hbox.add(self.dummy_load, 1)
            hbox.add(VLine(), 1)

            with CVBoxLayout(hbox, 2) as vbox:
                with CHBoxLayout(vbox, 1) as box:
                    box.add(QPushButton())
                    box.add(self.mode)

                vbox.add(self.key, 5)
                vbox.add(self.timeout)

                with CHBoxLayout(vbox, 1) as box:
                    box.add(self.heat)
                    box.add(QPushButton())
                    box.add(self.time)

    def set_power(self, power):
        self.timeout.current_power = int(power)

    def select_mode(self, mode):
        for i in range(self.mode.count()):
            if self.mode.itemText(i).lstrip(' ') == mode:
                self.mode.setCurrentIndex(i)
    
    def connect_radio(self, radio):
        if self.radio:
            return
        self.radio = radio

        radio.signals.power.connect(lambda s: self.power_btns.set_power(s))
        radio.signals.power.connect(lambda s: self.set_power(s))
        radio.signals.frequency.connect(lambda s: self.freq_btns.select(s))
        radio.signals.mode.connect(lambda s: self.select_mode(s))

        radio.signals.keyed.connect(lambda: self.key.setChecked(True))
        radio.signals.unkeyed.connect(lambda: self.key.setChecked(False))

        self.key.clicked.connect(radio.toggle_key)
        self.mode.activated.connect(lambda: radio.set_mode(self.mode.currentText().lstrip(' ')))

        self.freq_btns.up.clicked.connect(radio.band_up)
        self.freq_btns.down.clicked.connect(radio.band_down)
        self.freq_btns.set_frequency.connect(radio.set_vfoA_frequency)

        self.power_btns.power_changed.connect(radio.set_power_level)
        
        self.mode.clear()
        self.mode.addItems([m for m in radio.modes if m != ""])
        self.setEnabled(True)

    def disconnect_radio(self, guid):
        if self.radio.guid != guid:
            return
        self.radio = None

        self.setEnabled(False)
        self.mode.clear()
        self.mode.addItem("Mode")


class SwitchControls(Widget):
    def create_widgets(self):
        self.switch = None
        grid = CHBoxLayout(self)

        self.one = grid.add(QPushButton("Ant 1", checkable=True))
        self.two = grid.add(QPushButton("Ant 2", checkable=True))
        self.three = grid.add(QPushButton("Ant 3", checkable=True))
        self.four = grid.add(QPushButton("Ant 4", checkable=True))

        self.btns = QButtonGroup()
        self.btns.addButton(self.one)
        self.btns.addButton(self.two)
        self.btns.addButton(self.three)
        self.btns.addButton(self.four)

    def connect_switch(self, switch):
        if self.switch:
            return
        self.switch = switch

        self.setEnabled(True)

        self.one.clicked.connect(lambda: switch.select_antenna(1))
        self.two.clicked.connect(lambda: switch.select_antenna(2))
        self.three.clicked.connect(lambda: switch.select_antenna(3))
        self.four.clicked.connect(lambda: switch.select_antenna(4))

    def disconnect_switch(self, guid):
        if self.switch.guid != guid:
            return
        self.switch = None

        self.setEnabled(False)


class ControlPanel(Widget):        
    def create_widgets(self):
        self.radio = RadioControls(enabled=False)
        self.switch = SwitchControls(enabled=False)

    def build_layout(self):
        grid = CVBoxLayout(self)
        
        grid.add(self.radio, 4)
        grid.add(HLine())
        grid.add(self.switch, 1)


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

        self.info_panel.meter_info.connect_meter(meter)

    def disconnect_meter(self, guid):
        if self.meter.guid != guid:
            return
        self.meter = None

        self.info_panel.meter_info.disconnect_meter(guid)
        
    def connect_radio(self, radio):
        if self.radio:
            return
        self.radio = radio

        self.info_panel.radio_info.connect_radio(radio)
        self.control_panel.radio.connect_radio(radio)
        
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

        self.info_panel.radio_info.disconnect_radio(guid)
        self.control_panel.radio.disconnect_radio(guid)

    def connect_switch(self, switch):
        if self.switch:
            return
        self.switch = switch

        self.control_panel.switch.connect_switch(switch)

    def disconnect_switch(self, guid):
        if self.switch.guid != guid:
            return
        self.switch = None

        self.control_panel.switch.disconnect_switch(guid)

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
        self.setWindowIcon(QIcon(QPixmap(0, 0)))
        self.setWindowTitle('Servitor Controls')

        self.setWidget(ServitorWidget(self))