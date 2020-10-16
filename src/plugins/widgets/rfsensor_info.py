from qt import *
from device_manager import DeviceManager


@DeviceManager.subscribe_to("RFSensor")
class RFSensorWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        self.forward = QLabel("?")
        self.reverse = QLabel("?")
        self.swr = QLabel("?")
        self.forward_volts = QLabel("?")
        self.reverse_volts = QLabel("?")
        self.match_quality = QLabel("?")
        self.frequency = QLabel("?")

        with CVBoxLayout(self) as layout:
            layout.add(QLabel('RFSensor:'))
            with CHBoxLayout(layout) as hbox:
                with CVBoxLayout(hbox) as vbox:
                    vbox.addWidget(QLabel("Forward:"))
                    vbox.addWidget(QLabel("Reverse:"))
                    vbox.addWidget(QLabel("SWR:"))
                    vbox.addWidget(QLabel("Frequency:"))
                    vbox.addWidget(QLabel())
                    vbox.addWidget(QLabel("Forward Volts:"))
                    vbox.addWidget(QLabel("Reverse Volts:"))
                    vbox.addWidget(QLabel("Match Quality:"))
                with CVBoxLayout(hbox) as vbox:
                    vbox.addWidget(self.forward)
                    vbox.addWidget(self.reverse)
                    vbox.addWidget(self.swr)
                    vbox.addWidget(self.frequency)
                    vbox.addWidget(QLabel())
                    vbox.addWidget(self.forward_volts)
                    vbox.addWidget(self.reverse_volts)
                    vbox.addWidget(self.match_quality)
    
    def connected(self, device):
        device.signals.forward_volts.connect(lambda x: self.forward_volts.setText(f"{x:.2f}"))
        device.signals.reverse_volts.connect(lambda x: self.reverse_volts.setText(f"{x:.2f}"))
        device.signals.match_quality.connect(lambda x: self.match_quality.setText(f"{x:.2f}"))
        device.signals.forward.connect(lambda x: self.forward.setText(f"{x:.2f}"))
        device.signals.reverse.connect(lambda x: self.reverse.setText(f"{x:.2f}"))
        device.signals.swr.connect(lambda x: self.swr.setText(f"{x:.2f}"))
        device.signals.frequency.connect(lambda x: self.frequency.setText(f"{x}"))

    def disconnected(self, guid):
        self.forward.setText("?")
        self.reverse.setText("?")
        self.swr.setText("?")
        self.forward_volts.setText("?")
        self.reverse_volts.setText("?")
        self.match_quality.setText("?")
        self.frequency.setText("?")