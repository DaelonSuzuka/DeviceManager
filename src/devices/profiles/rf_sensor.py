from devices import SerialDevice, CommonMessagesMixin
from qt import *


class Signals(QObject):
    forward = Signal(float)
    reverse = Signal(float)
    swr = Signal(float)
    frequency = Signal(int)

    @property
    def message_tree(self):
        return {
            "update": {
                "forward": self.forward.emit,
                "reverse": self.reverse.emit,
                "swr": self.swr.emit,
                "frequency": self.frequency.emit,
            }
        }


class RFSensor(CommonMessagesMixin, SerialDevice):
    profile_name = "RFSensor"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)