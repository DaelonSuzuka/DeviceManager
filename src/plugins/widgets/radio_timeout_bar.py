from qt import *
from devices import DeviceManager
import qtawesome as qta
from style import qcolors


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