from qtstrap import (
    QWidget,
    CFormLayout,
    QLabel,
    QSizePolicy,
)
from codex import DeviceManager


@DeviceManager.subscribe_to('PhaseTuner')
class PhaseTunerInfo(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.fields = {
            'freq:': QLabel('?'),
            'vMag:': QLabel('?'),
            'cMag:': QLabel('?'),
            'phase:': QLabel('?'),
            'sign:': QLabel('?'),
            '': QLabel(''),
            'caps:': QLabel('?'),
            'inds:': QLabel('?'),
            'z:': QLabel('?'),
        }

        with CFormLayout(self) as layout:
            layout += self.fields

    def rf_received(self, rf_data):
        for name, value in rf_data.items():
            if name + ':' in self.fields:
                if isinstance(value, int):
                    self.fields[name + ':'].setText(f'{value}')
                if isinstance(value, float):
                    self.fields[name + ':'].setText(f'{value:6.2f}')

    def connected(self, device):
        device.signals.rf_received.connect(self.rf_received)

        device.signals.capacitors.connect(lambda x: self.fields['caps:'].setText(f'{x}'))
        device.signals.inductors.connect(lambda x: self.fields['inds:'].setText(f'{x}'))
        device.signals.hiloz.connect(lambda x: self.fields['z:'].setText(f'{x}'))

        device.get_relays()

    def disconnected(self, guid):
        for field in self.fields:
            field.setText('?')
