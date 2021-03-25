from codex import SerialDevice, JudiStandardMixin
from qt import *


class Signals(QObject):
    forward_volts = Signal(float)
    reverse_volts = Signal(float)
    match_quality = Signal(float)
    forward = Signal(float)
    reverse = Signal(float)
    swr = Signal(float)
    frequency = Signal(int)
    handshake_received = Signal(dict)

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


class CalibrationTarget(JudiStandardMixin, SerialDevice):
    profile_name = "CalibrationTarget"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)

    @property
    def description(self):
        return {
            "profile_name":self.profile_name,
            "guid":self.guid,
            "port":self.port,
            "title":self.title,
            "product_name":self.name,
            "serial_number":self.guid,
            # "firmware_version":self.firmware_version,
            # "protocol_version":self.protocol_version,
            "port":self.port,
        }