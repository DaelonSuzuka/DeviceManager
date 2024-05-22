from qtstrap import *
from qtstrap import (
    QWidget,
    CFormLayout,
    QLabel,
)
from codex import DeviceManager


@DeviceManager.subscribe_to("CalibrationTarget")
class CalibrationTargetInfo(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        with CFormLayout(self) as layout:
            layout += ('CalibrationTarget:', QLabel())

            self.forward = layout + ("Forward:", QLabel("?"))
            self.reverse = layout + ("Reverse:", QLabel("?"))
            self.swr = layout + ("SWR:", QLabel("?"))
            self.forward_volts = layout + ("Frequency:", QLabel("?"))
            layout += ('', QLabel())
            self.reverse_volts = layout + ("Forward Volts:", QLabel("?"))
            self.match_quality = layout + ("Reverse Volts:", QLabel("?"))
            self.frequency = layout + ("Match Quality:", QLabel("?"))
    
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