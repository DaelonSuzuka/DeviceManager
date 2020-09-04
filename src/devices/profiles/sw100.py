from devices import SerialDevice, CommonMessagesMixin
from qt import *


class Signals(QObject):
    antenna = Signal(int)

    @property
    def message_tree(self):
        return {
            "update": {
                "antenna": self.antenna.emit
            }
        }


class SW100(CommonMessagesMixin, SerialDevice):
    profile_name = "SW-100"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)

        self.request_antenna()

    def set_antenna(self, ant: str):
        self.send('{"command":{"set_antenna":"%s"}}' % (ant))

    def request_antenna(self):
        self.send('{"request":"antenna"}')