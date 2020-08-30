from qt import *
from functools import partial
from device_manager import DeviceManager
import qtawesome as qta
from style import qcolors


@DeviceManager.subscribe_to("TS-480")
class RadioInfo(Widget):        
    def create_widgets(self):
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

    def connected(self, device):
        device.signals.power.connect(lambda s: self.power.setText(s))
        device.signals.frequency.connect(lambda s: self.frequency.setText(s))
        device.signals.mode.connect(lambda s: self.mode.setText(s))

        device.get_power_level()
        device.get_mode()
        device.get_vfoA_frequency()

    def disconnected(self, guid):
        self.power.setText("  ?  ")
        self.frequency.setText("  ?  ")
        self.mode.setText("  ?  ")


@DeviceManager.subscribe_to("Alpha4510A")
class MeterInfo(Widget):        
    def create_widgets(self):
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

    def connected(self, device):
        device.signals.forward.connect(lambda s: self.forward.setText(s))
        device.signals.reverse.connect(lambda s: self.reverse.setText(s))
        device.signals.swr.connect(lambda s: self.swr.setText(s))
        device.signals.frequency.connect(lambda s: self.frequency.setText(s))

    def disconnected(self, guid):
        self.forward.setText("  ?  ")
        self.reverse.setText("  ?  ")
        self.swr.setText("  ?  ")
        self.frequency.setText("  ?  ")


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


@DeviceManager.subscribe_to("TS-480")
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

        self.lock = grid.add(LockButton(iconSize=QSize(35, 35)), 0, 0)
        grid.add(QPushButton(disabled=True), 0, 1)
        grid.add(QPushButton(disabled=True), 0, 2)
        grid.add(QPushButton('+', clicked=lambda: self.update_power(int(self.power) + 5)), 1, 1, 5, 2)
        grid.add(QPushButton('-', clicked=lambda: self.update_power(int(self.power) - 5)), 6, 1, 5, 2)

        self.lock.toggled.connect(lambda s: self.set_limit(not s))
        self.set_limit(True)

    def connected(self, device):
        device.signals.power.connect(lambda s: self.set_power(s))
        self.power_changed.connect(device.set_power_level)

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


@DeviceManager.subscribe_to("TS-480")
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

        self.up = grid.add(QPushButton('^', clicked=lambda: self.uncheck_all()), 1, 1, 5, 2)
        self.down = grid.add(QPushButton('v', clicked=lambda: self.uncheck_all()), 6, 1, 5, 2)

    def connected(self, device):
        device.signals.frequency.connect(lambda s: self.select(s))
        self.up.clicked.connect(device.band_up)
        self.down.clicked.connect(device.band_down)
        self.set_frequency.connect(device.set_vfoA_frequency)

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
        vbox = CVBoxLayout(self, contentsMargins=QMargins(0, 0, 0, 0))
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


@DeviceManager.subscribe_to("RadioInterface")
class FullTuneButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setText('Full Tune')
        self.setCheckable(True)

        self.timer = QTimer(self, timeout=self.uncheck)
        self.toggled.connect(self.on_toggle)

        self.peers = []

    def register(self, *buttons):
        for button in buttons:
            self.peers.append(button)

    def on_toggle(self, state):
        if state == True:
            if self.device is not None:
                self.device.set_output(True)

            self.timer.start(3000)
            self.setEnabled(False)
            for button in self.peers:
                button.setEnabled(False)

    def uncheck(self):
        self.device.set_output(False)
        self.timer.stop()
        self.setChecked(False)
        self.setEnabled(True)
        for button in self.peers:
            button.setEnabled(True)


@DeviceManager.subscribe_to("RadioInterface")
class MemoryTuneButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setText('Mem Tune')
        self.setCheckable(True)

        self.timer = QTimer(self, timeout=self.uncheck)
        self.toggled.connect(self.on_toggle)

        self.peers = []

    def register(self, *buttons):
        for button in buttons:
            self.peers.append(button)

    def on_toggle(self, state):
        if state == True:
            if self.device is not None:
                self.device.set_output(True)

            self.timer.start(1500)
            self.setEnabled(False)
            for button in self.peers:
                button.setEnabled(False)

    def uncheck(self):
        self.device.set_output(False)
        self.timer.stop()
        self.setChecked(False)
        self.setEnabled(True)
        for button in self.peers:
            button.setEnabled(True)


@DeviceManager.subscribe_to("RadioInterface")
class BypassButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setText('Bypass')
        self.setCheckable(True)

        self.timer = QTimer(self, timeout=self.uncheck)
        self.toggled.connect(self.on_toggle)

        self.peers = []

    def register(self, *buttons):
        for button in buttons:
            self.peers.append(button)


    def on_toggle(self, state):
        if state == True:
            if self.device is not None:
                self.device.set_output(True)

            self.timer.start(250)
            self.setEnabled(False)
            for button in self.peers:
                button.setEnabled(False)

    def uncheck(self):
        self.device.set_output(False)
        self.timer.stop()
        self.setChecked(False)
        self.setEnabled(True)
        for button in self.peers:
            button.setEnabled(True)


@DeviceManager.subscribe_to("TS-480")
class KeyButton(IconToggleButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIconSize(QSize(100, 100))
        self.setStyleSheet(""" :checked { border: 5px solid #FF4136; border-radius: 10px; } """)
        self.icon_checked = qta.icon('mdi.radio-tower', color=qcolors.silver)
        self.icon_unchecked = qta.icon('mdi.radio-tower', color='gray')
        self.update_icon()

    def connected(self, device):
        device.signals.keyed.connect(lambda: self.setChecked(True))
        device.signals.unkeyed.connect(lambda: self.setChecked(False))
        self.clicked.connect(device.toggle_key)


@DeviceManager.subscribe_to("TS-480")
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

    def connected(self, device):
        self.activated.connect(lambda: device.set_mode(self.currentText().lstrip(' ')))
        device.signals.mode.connect(lambda s: self.select_mode(s))
        self.clear()
        self.addItems([m for m in device.modes if m != ""])

    def disconected(self):
        self.clear()
        self.addItem("Mode")

    def addItems(self, texts):
        super().addItems(['    ' + t for t in texts])

    def select_mode(self, mode):
        for i in range(self.count()):
            if self.itemText(i).lstrip(' ') == mode:
                self.setCurrentIndex(i)

    def showPopup(self):
        super().showPopup()
        popup = self.findChild(QFrame)
        popup.move(popup.x(), self.mapToGlobal(self.rect().bottomLeft()).y())


@DeviceManager.subscribe_to("TS-480")
class TimeoutBar(QProgressBar):
    timeout = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet('QProgressBar::chunk { background: grey; }')
        
        self.setTextVisible(False)
        self.default_maximum = 35000
        self.setMaximum(self.default_maximum)
        self.setValue(0)

        self.running = False
        self.suppressed = False
        self.current_power = 5
        self.step = 5

        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.update_timeout_bar())
        self.timer.start(50)

    def connected(self, device):
        device.signals.power.connect(lambda s: self.set_power(s))

    def set_power(self, power):
        self.current_power = int(power)

        self.step = (self.current_power / 2) + 10

    def set_running(self, running):
        self.running = running

    def set_suppressed(self, suppressed):
        self.suppressed = suppressed

    def update_timeout_bar(self):
        val = self.value()

        if self.isEnabled():
            if self.running and not self.suppressed:
                if val < self.maximum():
                    if val + self.step > self.maximum():
                        self.setValue(self.maximum())
                    else:
                        self.setValue(val + self.step)

                if val >= self.maximum() - 1:
                    self.timeout.emit()
            else:
                if val > 0:
                    if (val - 500) < 0:
                        self.setValue(0)
                    else:
                        self.setValue(val - 500)


@DeviceManager.subscribe_to("TS-480")
class RadioControls(Widget):
    def create_widgets(self):
        self.setStyleSheet('QProgressBar { border: 1px solid grey; }')

        self.power_btns = PowerButtons()
        self.freq_btns = FrequencyButtons()
        self.dummy_load = DummyLoadControls(enabled=False)

        self.mode = ModeComboBox()

        self.heat = HeatButton()
        self.time = TimeoutButton()

        self.bypass = BypassButton()
        self.memory_tune = MemoryTuneButton()
        self.full_tune = FullTuneButton()

        self.bypass.register(self.memory_tune, self.full_tune)
        self.memory_tune.register(self.bypass, self.full_tune)
        self.full_tune.register(self.bypass, self.memory_tune)

        self.timeout = TimeoutBar()
        self.key = KeyButton()

        self.time.toggled.connect(self.timeout.set_suppressed)
        self.key.toggled.connect(self.timeout.set_running)
        self.timeout.timeout.connect(lambda: self.key.click())

    def build_layout(self):
        margins = { 'contentsMargins': QMargins(0, 0, 0, 0) }

        with CHBoxLayout(self, **margins) as hbox:
            hbox.add(self.power_btns, 2)
            hbox.add(VLine(), 1)
            hbox.add(self.freq_btns, 2)
            hbox.add(VLine(), 1)
            # hbox.add(self.dummy_load, 1)
            # hbox.add(VLine(), 1)

            with CVBoxLayout(hbox, 2, **margins) as vbox:
                with CHBoxLayout(vbox, 1, **margins) as box:
                    box.add(self.time)
                    box.add(QPushButton(disabled=True))
                    box.add(self.mode)

                vbox.add(self.key, 5)
                vbox.add(self.timeout)

                with CHBoxLayout(vbox, 1, **margins) as box:
                    # box.add(self.heat)
                    box.add(self.bypass)
                    box.add(self.memory_tune)
                    box.add(self.full_tune)

    def connected(self, device):
        self.setEnabled(True)
        
        device.unkey()

    def disconnected(self, guid):
        self.setEnabled(False)


@DeviceManager.subscribe_to("DTS-4")
class SwitchControls(Widget):
    def create_widgets(self):
        self.switch = None
        grid = CHBoxLayout(self, contentsMargins=QMargins(0, 0, 0, 0))

        self.one = grid.add(QPushButton("Ant 1", checkable=True))
        self.two = grid.add(QPushButton("Ant 2", checkable=True))
        self.three = grid.add(QPushButton("Ant 3", checkable=True))
        self.four = grid.add(QPushButton("Ant 4", checkable=True))

        self.btns = QButtonGroup()
        self.btns.addButton(self.one)
        self.btns.addButton(self.two)
        self.btns.addButton(self.three)
        self.btns.addButton(self.four)
        
    def connected(self, device):
        self.setEnabled(True)

        self.one.clicked.connect(lambda: device.select_antenna(1))
        self.two.clicked.connect(lambda: device.select_antenna(2))
        self.three.clicked.connect(lambda: device.select_antenna(3))
        self.four.clicked.connect(lambda: device.select_antenna(4))

    def disconnected(self, guid):
        self.setEnabled(False)


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
        self.setBackgroundRole(QPalette.Base)
        self.setAutoFillBackground(True)

        self.radio = RadioControls(enabled=False)
        self.switch = SwitchControls(enabled=False)
        self.radio_info = RadioInfo()
        self.meter_info = MeterInfo()

        margins = { 'contentsMargins': QMargins(0, 0, 0, 0) }

        with CHBoxLayout(self) as hbox:
            with CVBoxLayout(hbox, 1, **margins) as vbox:
                vbox.setAlignment(Qt.AlignTop)
                vbox.add(self.radio_info)
                vbox.add(HLine())
                vbox.add(self.meter_info)

            hbox.addWidget(VLine())

            with CVBoxLayout(hbox, 4, **margins) as vbox:
                vbox.add(self.radio, 4)
                vbox.add(HLine())
                vbox.add(self.switch, 1)


class ServitorSubWindow(QMdiSubWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(QPixmap(0, 0)))
        self.setWindowTitle('Servitor Controls')

        self.setWidget(ServitorWidget(self))