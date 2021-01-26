from qt import *
from devices import DeviceManager


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
            with layout.hbox():
                with layout.vbox():
                    layout.add(QLabel("Forward:"))
                    layout.add(QLabel("Reverse:"))
                    layout.add(QLabel("SWR:"))
                    layout.add(QLabel("Frequency:"))
                    layout.add(QLabel("Temperature:"))
                with layout.vbox():
                    layout.add(self.forward)
                    layout.add(self.reverse)
                    layout.add(self.swr)
                    layout.add(self.frequency)
                    layout.add(self.temperature)

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