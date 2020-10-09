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