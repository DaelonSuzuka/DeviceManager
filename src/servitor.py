from qt import *
from functools import partial
from device_manager import DeviceManager
import qtawesome as qta
from style import qcolors
from device_widgets import *


@DeviceManager.subscribe_to("TS-480")
class RadioInfo(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.power = QLabel("  ?  ")
        self.frequency = QLabel("  ?  ")
        self.mode = QLabel("  ?  ")
        
        with CVBoxLayout(self) as layout:
            layout.add(QLabel('Kenwood TS-480:'))
            with CHBoxLayout(layout) as hbox:
                with CVBoxLayout(hbox) as vbox:
                    vbox.addWidget(QLabel("Power:"))
                    vbox.addWidget(QLabel("Frequency:"))
                    vbox.addWidget(QLabel("Mode:"))
                with CVBoxLayout(hbox) as vbox:
                    vbox.addWidget(self.power)
                    vbox.addWidget(self.frequency)
                    vbox.addWidget(self.mode)

    def connected(self, device):
        device.signals.power.connect(lambda s: self.power.setText(s))
        device.signals.frequency.connect(lambda s: self.frequency.setText(s))
        device.signals.mode.connect(lambda s: self.mode.setText(s))
        QTimer.singleShot(50, self.get_initial_radio_state)

    def get_initial_radio_state(self):
        self.device.get_power_level()
        self.device.get_mode()
        self.device.get_vfoA_frequency()

    def disconnected(self, guid):
        self.power.setText("  ?  ")
        self.frequency.setText("  ?  ")
        self.mode.setText("  ?  ")


@DeviceManager.subscribe_to("Alpha4510A")
class MeterInfo(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.forward = QLabel("  ?  ")
        self.reverse = QLabel("  ?  ")
        self.swr = QLabel("  ?  ")
        self.frequency = QLabel("  ?  ")

        with CVBoxLayout(self) as layout:
            layout.add(QLabel('Alpha4510A:'))
            with CHBoxLayout(layout) as hbox:
                with CVBoxLayout(hbox) as vbox:
                    vbox.addWidget(QLabel("Forward:"))
                    vbox.addWidget(QLabel("Reverse:"))
                    vbox.addWidget(QLabel("SWR:"))
                    vbox.addWidget(QLabel("Frequency:"))
                with CVBoxLayout(hbox) as vbox:
                    vbox.addWidget(self.forward)
                    vbox.addWidget(self.reverse)
                    vbox.addWidget(self.swr)
                    vbox.addWidget(self.frequency)

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
class PowerButtons(QWidget):
    power_changed = Signal(str)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.power = '5'
        self.limit = True
        self.btns = QButtonGroup()

        powers = ["200", "175", "150", "125", "100", "75", "50", "25", "10", "5"]

        with CGridLayout(self, margins=(0, 0, 0, 0)) as grid:
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
class FrequencyButtons(QWidget):
    set_frequency = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.freqs = [
            "50000000", "28000000", "24890000", "21000000", "18068000",
            "14000000", "10100000", "07000000", "03500000", "01800000"
        ]
        band_names = ["50", "28", "24", "21", "18", "14", "10", "7", "3.4", "1.8"]
        self.btns = QButtonGroup()

        with CGridLayout(self, margins=(0, 0, 0, 0)) as grid:
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
        vbox = CVBoxLayout(self, margins=(0, 0, 0, 0))
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


class RadioControls(Widget):
    def create_widgets(self):
        self.setStyleSheet('QProgressBar { border: 1px solid grey; }')

        self.power_btns = PowerButtons()
        self.freq_btns = FrequencyButtons()
        self.dummy_load = DummyLoadControls()

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
        with CHBoxLayout(self, margins=(0, 0, 0, 0)) as hbox:
            hbox.add(self.power_btns, 2)
            hbox.add(VLine(), 1)
            hbox.add(self.freq_btns, 2)
            hbox.add(VLine(), 1)
            # hbox.add(self.dummy_load, 1)
            # hbox.add(VLine(), 1)

            with CVBoxLayout(hbox, 2, margins=(0, 0, 0, 0)) as vbox:
                with CHBoxLayout(vbox, 1, margins=(0, 0, 0, 0)) as box:
                    box.add(self.time)
                    box.add(QPushButton(disabled=True))
                    box.add(self.mode)

                vbox.add(self.key, 5)
                vbox.add(self.timeout)

                with CHBoxLayout(vbox, 1, margins=(0, 0, 0, 0)) as box:
                    # box.add(self.heat)
                    box.add(self.bypass)
                    box.add(self.memory_tune)
                    box.add(self.full_tune)


@DeviceManager.subscribe_to("DTS-6")
class SwitchControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        with CHBoxLayout(self, margins=(0, 0, 0, 0)) as grid:
            self.one = grid.add(QPushButton("Ant 1", checkable=True))
            self.two = grid.add(QPushButton("Ant 2", checkable=True))
            self.three = grid.add(QPushButton("Ant 3", checkable=True))
            self.four = grid.add(QPushButton("Ant 4", checkable=True))
            self.five = grid.add(QPushButton("Ant 5", checkable=True))
            self.six = grid.add(QPushButton("Ant 6", checkable=True))

        self.btns = QButtonGroup()
        self.btns.addButton(self.one)
        self.btns.addButton(self.two)
        self.btns.addButton(self.three)
        self.btns.addButton(self.four)
        self.btns.addButton(self.five)
        self.btns.addButton(self.six)
        
    def antenna_changed(self, antenna):
        if antenna == 0:
            self.one.setChecked(False)
            self.two.setChecked(False)
            self.three.setChecked(False)
            self.four.setChecked(False)
        if antenna == 1:
            self.one.setChecked(True)
        if antenna == 2:
            self.two.setChecked(True)
        if antenna == 3:
            self.three.setChecked(True)
        if antenna == 4:
            self.four.setChecked(True)
        if antenna == 5:
            self.five.setChecked(True)
        if antenna == 6:
            self.six.setChecked(True)

    def connected(self, device):
        self.one.clicked.connect(lambda: device.set_antenna(1))
        self.two.clicked.connect(lambda: device.set_antenna(2))
        self.three.clicked.connect(lambda: device.set_antenna(3))
        self.four.clicked.connect(lambda: device.set_antenna(4))
        self.five.clicked.connect(lambda: device.set_antenna(5))
        self.six.clicked.connect(lambda: device.set_antenna(6))

        device.signals.antenna.connect(self.antenna_changed)

        device.get_antenna()


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
        
        self.parent().tabs.addTab(self, 'Servitor')

        self.setBackgroundRole(QPalette.Base)
        self.setAutoFillBackground(True)

        self.radio = RadioControls(self)

        with CHBoxLayout(self) as hbox:
            with CVBoxLayout(hbox, 1, margins=(0, 0, 0, 0)) as vbox:
                vbox.setAlignment(Qt.AlignTop)
                vbox.add(RadioInfo(self))
                vbox.add(HLine())
                vbox.add(MeterInfo(self))
                vbox.add(HLine())
                vbox.add(RFSensorWidget(self))

            hbox.addWidget(VLine())

            with CVBoxLayout(hbox, 4, margins=(0, 0, 0, 0)) as vbox:
                vbox.add(self.radio, 7)
                vbox.add(HLine())
                vbox.add(SwitchControls(self), 1)


class ServitorSubWindow(QMdiSubWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(QPixmap(0, 0)))
        self.setWindowTitle('Servitor Controls')

        self.setWidget(ServitorWidget(self))