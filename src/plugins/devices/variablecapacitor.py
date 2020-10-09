from devices import SerialDevice, CommonMessagesMixin
from qt import *


class Signals(QObject):
    capacitors = Signal(int)
    input = Signal(int)
    output = Signal(int)
    bypass = Signal(int)
    
    @property
    def message_tree(self):
        return {
            "update": {
                "relays": {
                    "capacitors": self.capacitors.emit,
                    "input": self.input.emit,
                    "output": self.output.emit,
                    "bypass": self.bypass.emit,
                }
            }
        }


class VariableCapacitor(CommonMessagesMixin, SerialDevice):
    profile_name = "VariableCapacitor"
    max_caps = 255

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)

        self.capacitors = 0
        self.signals.capacitors.connect(lambda i: self.__setattr__("capacitors", i))

        # startup messages
        self.request_current_relays()

    def set_caps(self, value):
        self.send('{"command":{"set_capacitors":%s}}' % (str(value)))

    def relays_max(self):
        self.send('{"command":{"set_capacitors":255}}')

    def relays_min(self):
        self.send('{"command":{"set_capacitors":0}}')

    def relays_cup(self):
        self.send('{"command":"cup"}')

    def relays_cdn(self):
        self.send('{"command":"cdn"}')

    def request_current_relays(self):
        self.send('{"request":"current_relays"}')

    def set_input(self, state):
        self.send('{"command":{"set_input":%s}}' % (int(state)))

    def set_output(self, state):
        self.send('{"command":{"set_output":%s}}' % (int(state)))

    def set_bypass(self, state):
        self.send('{"command":{"set_bypass":%s}}' % (int(state)))