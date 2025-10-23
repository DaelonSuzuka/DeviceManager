from qtstrap import *
from qtstrap import (
    QWidget,
    CFormLayout,
    QLabel,
)
from codex import DeviceManager

from plugins.devices.calibration_target import CalibrationTarget


@DeviceManager.subscribe_to('CalibrationTarget')
class CalibrationTargetInfo(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.fields = {
            'fwdV:': QLabel('?'),
            'revV:': QLabel('?'),
            'matchQ:': QLabel('?'),
            'fwd:': QLabel('?'),
            'rev:': QLabel('?'),
            'swr:': QLabel('?'),
            'freq:': QLabel('?'),
        }

        with CFormLayout(self) as layout:
            layout += ('CalibrationTarget:', QLabel())
            layout += self.fields

    def target_rf_received(self, rf_data: dict[str, float | int]):
        for name, value in rf_data.items():
            if name + ':' in self.fields:
                if isinstance(value, int):
                    self.fields[name + ':'].setText(f'{value}')
                if isinstance(value, float):
                    self.fields[name + ':'].setText(f'{value:6.2f}')

    def connected(self, device: CalibrationTarget):
        device.signals.rf_received.connect(self.target_rf_received)

    def disconnected(self, guid):
        for label, field in self.fields.items():
            field.setText('?')
