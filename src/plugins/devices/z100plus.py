from devices import SerialDevice, JudiStandardMixin
from qt import *


class Signals(QObject):
    event = Signal(dict)


class Z100Plus(JudiStandardMixin, SerialDevice):
    profile_name = "Z-100Plus"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.common_message_tree)
        self.message_tree.merge({
            "update": {
                "event": self.event.emit
            }
        })

        self.signals.event.connect(print)