from qtstrap import *
from codex import SubscriptionManager


@SubscriptionManager.subscribe
class Stomp5StatusWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setEnabled(False)

        self.stomp = None
        self.radio = None
        self.switch = None

        self.status = QLabel("Not Connected")
        self.state = [QLabel('^') for i in range(5)]

        with CVBoxLayout(self, align='top') as layout:
            layout.add(self.status)
            layout.add(HLine())
            with layout.hbox():
                layout.add(self.state)

    def device_added(self, device):
        if device.profile_name == 'Stomp 5':
            self.setEnabled(True)
            self.status.setText('Connected')
            if self.stomp:
                self.stomp.kill()
                self.stomp.deleteLater()
            self.stomp = device.signals.adapter()
            self.stomp.button_pressed.connect(self.button_pressed)
            self.stomp.button_released.connect(self.button_released)

        if device.profile_name == 'TS-480':
            self.radio = device

        if device.profile_name == 'DTS-6':
            self.switch = device

    def device_removed(self, guid):
        pass

    def button_pressed(self, button):
        number = int(button) - 1
        
        self.state[number].setText('v')

        if self.radio:
            if number == 0:
                self.radio.band_up()
            if number == 1:
                self.radio.band_down()
            if number == 4:
                self.radio.key()

        if self.switch:
            if number == 2:
                self.switch.set_antenna('1')
            if number == 3:
                self.switch.set_antenna('2')

    def button_released(self, button):
        number = int(button) - 1

        self.state[number].setText('^')

        
        if self.radio:
            if number == 4:
                self.radio.unkey()