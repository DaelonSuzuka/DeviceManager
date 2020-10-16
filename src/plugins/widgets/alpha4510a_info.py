from qt import *
from device_manager import DeviceManager


@DeviceManager.subscribe_to("Alpha4510A")
class MeterInfo(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.forward = QLabel("  ?  ")
        self.reverse = QLabel("  ?  ")
        self.swr = QLabel("  ?  ")
        self.frequency = QLabel("  ?  ")
        self.temperature = QLabel("  ?  ")

        with CVBoxLayout(self) as layout:
            layout.add(QLabel('Alpha4510A:'))
            with CHBoxLayout(layout) as hbox:
                with CVBoxLayout(hbox) as vbox:
                    vbox.addWidget(QLabel("Forward:"))
                    vbox.addWidget(QLabel("Reverse:"))
                    vbox.addWidget(QLabel("SWR:"))
                    vbox.addWidget(QLabel("Frequency:"))
                    vbox.addWidget(QLabel("Temperature:"))
                with CVBoxLayout(hbox) as vbox:
                    vbox.addWidget(self.forward)
                    vbox.addWidget(self.reverse)
                    vbox.addWidget(self.swr)
                    vbox.addWidget(self.frequency)
                    vbox.addWidget(self.temperature)

    def connected(self, device):
        device.signals.forward.connect(lambda x: self.forward.setText(f'{x:6.2f}'))
        device.signals.reverse.connect(lambda x: self.reverse.setText(f'{x:6.2f}'))
        device.signals.swr.connect(lambda x: self.swr.setText(f'{x:6.2f}'))
        device.signals.frequency.connect(lambda x: self.frequency.setText(f'{x:6.2f}'))
        device.signals.temperature.connect(lambda x: self.temperature.setText(f'{x:6.2f}'))

    def disconnected(self, guid):
        self.forward.setText("  ?  ")
        self.reverse.setText("  ?  ")
        self.swr.setText("  ?  ")
        self.frequency.setText("  ?  ")
        self.temperature.setText("  ?  ")