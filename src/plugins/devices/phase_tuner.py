from codex import SerialDevice, JudiStandardMixin
from qtstrap import *


class Signals(QObject):
    capacitors = Signal(int)
    inductors = Signal(int)
    hiloz = Signal(int)

    v_mag = Signal(float)
    c_mag = Signal(float)
    phase = Signal(float)
    phase_sign = Signal(int)
    frequency = Signal(int)

    v_mag_volts = Signal(float)
    c_mag_volts = Signal(float)
    phase_degree = Signal(int)
    phase_radian = Signal(int)
    module_Z = Signal(float)
    apparent_Power = Signal(float)
    swr = Signal(int)

    rf_received = Signal(dict)
    handshake_received = Signal(dict)

    @property
    def message_tree(self):
        return {
            'update': {
                'relays': {
                    'caps': self.capacitors.emit,
                    'inds': self.inductors.emit,
                    'z': self.hiloz.emit,
                },
                'rf': self.rf_received.emit
            }
        }


class PhaseTuner(JudiStandardMixin, SerialDevice):
    profile_name = 'PhaseTuner'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)

    @property
    def description(self):
        return {
            'profile_name': self.profile_name,
            'guid': self.guid,
            'port': self.port,
            'title': self.title,
            'product_name': self.name,
            'serial_number': self.guid,
            # "firmware_version":self.firmware_version,
            # "protocol_version":self.protocol_version,
        }

    def get_rf(self):
        self.send({'request': 'rf'})

    def relays_cup(self):
        self.send({'command': 'cup'})

    def relays_cdn(self):
        self.send({'command': 'cdn'})

    def relays_lup(self):
        self.send({'command': 'lup'})

    def relays_ldn(self):
        self.send({'command': 'ldn'})

    def bypass(self):
        self.set_relays(0, 0, 0)

    def get_relays(self):
        self.send({'request': 'relays'})

    def set_relays(self, caps=None, inds=None, z=None):
        payload = {}
        if caps is not None:
            payload['caps'] = caps
        if inds is not None:
            payload['inds'] = inds
        if z is not None:
            payload['z'] = z

        self.send({'command': 'set_relays', 'relays': payload})
