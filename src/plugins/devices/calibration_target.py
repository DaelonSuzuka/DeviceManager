from devices import SerialDevice, CommonMessagesMixin
from qt import *


class Signals(QObject):
    forward_volts = Signal(float)
    reverse_volts = Signal(float)
    match_quality = Signal(float)
    forward = Signal(float)
    reverse = Signal(float)
    swr = Signal(float)
    frequency = Signal(int)

    @property
    def message_tree(self):
        return {
            "update": {
                "forward_volts": self.forward_volts.emit,
                "reverse_volts": self.reverse_volts.emit,
                "match_quality": self.match_quality.emit,
                "forward": self.forward.emit,
                "reverse": self.reverse.emit,
                "swr": self.swr.emit,
                "frequency": self.frequency.emit,
            }
        }


class CalibrationTarget(CommonMessagesMixin, SerialDevice):
    profile_name = "CalibrationTarget"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)