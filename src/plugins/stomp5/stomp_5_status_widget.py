from qtstrap import *
from codex import DeviceManager


@DeviceManager.subscribe_to("Stomp 5")
class Stomp5StatusWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.status = QLabel("Not Connected")
        
        with CVBoxLayout(self, align='top') as layout:
            layout.add(self.status)
    
    def connected(self, device):
        self.status.setText('Connected')
        self.adapter = device.signals.adapter()
        self.adapter.button_pressed.connect(self.button_pressed)
        self.adapter.button_released.connect(self.button_released)

    def button_pressed(self, button):
        number = int(button) - 1
        self.pedals[number].press.run()
        self.pedals[number].state.setText('down')

    def button_released(self, button):
        number = int(button) - 1
        self.pedals[number].release.run()
        self.pedals[number].state.setText('up')