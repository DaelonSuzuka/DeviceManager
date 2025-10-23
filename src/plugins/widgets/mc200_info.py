from qtstrap import (
    QWidget,
    CFormLayout,
    QLabel,
    QSizePolicy,
)
from codex import DeviceManager

from plugins.devices.mc200 import MC200


@DeviceManager.subscribe_to('MC-200')
class MC200Info(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.fields = {
            'fwdV:': QLabel('?'),
            'revV:': QLabel('?'),
            'fwd:': QLabel('?'),
            'rev:': QLabel('?'),
            'swr:': QLabel('?'),
        }

        with CFormLayout(self) as layout:
            layout += ('MC-200:', QLabel())
            layout += self.fields

    def target_rf_received(self, rf_data: dict[str, float | int]):
        for name, value in rf_data.items():
            if name + ':' in self.fields:
                if isinstance(value, int):
                    self.fields[name + ':'].setText(f'{value}')
                if isinstance(value, float):
                    self.fields[name + ':'].setText(f'{value:6.2f}')

    def connected(self, device: MC200):
        device.signals.rf_received.connect(self.target_rf_received)

    def disconnected(self, guid):
        for label, field in self.fields.items():
            field.setText('?')
