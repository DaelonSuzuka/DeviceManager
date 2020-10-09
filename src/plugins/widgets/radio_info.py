from qt import *
from device_manager import DeviceManager


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