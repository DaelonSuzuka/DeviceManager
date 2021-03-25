from qt import *
from codex import DeviceManager


@DeviceManager.subscribe_to("CalibrationTarget")
class CalibrationTargetInfo(QWidget):
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
            layout.add(QLabel('CalibrationTarget:'))
            with layout.hbox():
                with layout.vbox():
                    layout.add(QLabel("Forward:"))
                    layout.add(QLabel("Reverse:"))
                    layout.add(QLabel("SWR:"))
                    layout.add(QLabel("Frequency:"))
                    layout.add(QLabel())
                    layout.add(QLabel("Forward Volts:"))
                    layout.add(QLabel("Reverse Volts:"))
                    layout.add(QLabel("Match Quality:"))
                with layout.vbox():
                    layout.add(self.forward)
                    layout.add(self.reverse)
                    layout.add(self.swr)
                    layout.add(self.frequency)
                    layout.add(QLabel())
                    layout.add(self.forward_volts)
                    layout.add(self.reverse_volts)
                    layout.add(self.match_quality)
    
    def connected(self, device):
        device.signals.forward_volts.connect(lambda x: self.forward_volts.setText(f"{x:6.2f}"))
        device.signals.reverse_volts.connect(lambda x: self.reverse_volts.setText(f"{x:6.2f}"))
        device.signals.match_quality.connect(lambda x: self.match_quality.setText(f"{x:6.2f}"))
        device.signals.forward.connect(lambda x: self.forward.setText(f"{x:6.2f}"))
        device.signals.reverse.connect(lambda x: self.reverse.setText(f"{x:6.2f}"))
        device.signals.swr.connect(lambda x: self.swr.setText(f"{x:6.2f}"))
        device.signals.frequency.connect(lambda x: self.frequency.setText(f"{x}"))

    def disconnected(self, guid):
        self.forward.setText("?")
        self.reverse.setText("?")
        self.swr.setText("?")
        self.forward_volts.setText("?")
        self.reverse_volts.setText("?")
        self.match_quality.setText("?")
        self.frequency.setText("?")