from devices import SerialDevice, CommonMessagesMixin
from qt import *


class Signals(QObject):
    antenna = Signal(int)
    
    @property
    def message_tree(self):
        return {
            "update": {
                "antenna": self.antenna.emit,
            }
        }

class DTS6(CommonMessagesMixin, SerialDevice):
    profile_name = "DTS-6"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)

    def set_antenna(self, ant):
        self.send('{"command":{"set_antenna":"%s"}}' % (ant))

    def get_antenna(self):
        self.send('{"request":"antenna"}')