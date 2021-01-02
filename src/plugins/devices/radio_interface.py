from qt import *
from devices import SerialDevice, JudiStandardMixin


class Signals(QObject):
    input_changed = Signal(str)
    output_changed = Signal(str)

    @property
    def message_tree(self):
        return {
            "update": {
                "input": self.input_changed.emit,
                "output": self.output_changed.emit,
            }
        }


class RadioInterface(SerialDevice, JudiStandardMixin):
    profile_name = "RadioInterface"

    def __init__(self, port=None, baud=9600, device=None):
        super().__init__(port=port, baud=baud, device=device)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)

    def set_output(self, state):
        self.send('{"command":{"set_output":"%s"}}' % (str(int(state))))