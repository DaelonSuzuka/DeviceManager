from qt import *
from devices import SerialDevice, CommonMessagesMixin


class Signals(QObject):
    input_high = Signal()
    input_low = Signal()
    output_high = Signal()
    output_low = Signal()

    @property
    def message_tree(self):
        return {
            "update": {
                "input": {
                    "high": self.input_high.emit,
                    "low": self.input_low.emit,
                },
                "output": {
                    "high": self.input_high.emit,
                    "low": self.input_low.emit,
                },
            }
        }


class RadioInterface(SerialDevice, CommonMessagesMixin):
    profile_name = "RadioInterface"

    def __init__(self, port=None, baud=9600, device=None):
        super().__init__(port=port, baud=baud, device=device)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)

    def set_output(self, state):
        self.send('{"command":{"set_output":"%s"}}' % (str(int(state))))