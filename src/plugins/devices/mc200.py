from codex import SerialDevice, JudiStandardMixin
from qtstrap import *


class Signals(QObject):
    rf_received = Signal(dict)
    handshake_received = Signal(dict)

    @property
    def message_tree(self):
        return {'update': {'rf': self.rf_received.emit}}


class MC200(JudiStandardMixin, SerialDevice):
    profile_name = 'MC-200'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)
        self.log.setLevel('INFO')

    def get_rf(self):
        self.send({'request': 'rf'})
