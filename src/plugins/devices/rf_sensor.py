from devices import SerialDevice, CommonMessagesMixin
from qt import *


class Signals(QObject):
    forward = Signal(float)
    reverse = Signal(float)
    forward_watts = Signal(float)
    reverse_watts = Signal(float)
    match_quality = Signal(float)
    swr = Signal(float)
    frequency = Signal(int)
    phase = Signal(int)

    @property
    def message_tree(self):
        return {
            "update": {
                "forward": self.forward.emit,
                "reverse": self.reverse.emit,
                "match_quality": self.match_quality.emit,
                "forward_watts": self.forward_watts.emit,
                "reverse_watts": self.reverse_watts.emit,
                "swr": self.swr.emit,
                "frequency": self.frequency.emit,
                "phase": self.phase.emit,
            }
        }


class RFSensor(CommonMessagesMixin, SerialDevice):
    profile_name = "RFSensor"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)