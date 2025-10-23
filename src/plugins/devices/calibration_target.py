from codex import JudiStandardMixin, SerialDevice
from qtstrap import *


class Signals(QObject):
    rf_received = Signal(dict)
    handshake_received = Signal(dict)

    @property
    def message_tree(self):
        return {'update': {'rf': self.rf_received.emit}}


class CalibrationTarget(JudiStandardMixin, SerialDevice):
    profile_name = 'CalibrationTarget'

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
            'port': self.port,
        }
