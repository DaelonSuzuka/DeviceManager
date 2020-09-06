from devices import SerialDevice, CommonMessagesMixin
from qt import *


class Signals(QObject):
    inductors = Signal(int)
    input = Signal(bool)
    output = Signal(bool)

    @property
    def message_tree(self):
        return {
            "update": {
                "relays": {
                    "inductors": lambda s: self.inductors.emit(s),
                    "input": lambda s: self.input.emit(s),
                    "output": lambda s: self.output.emit(s),
                }
            }
        }


class VariableInductor(CommonMessagesMixin, SerialDevice):
    profile_name = "VariableInductor"
    max_inds = 127

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)

        self.inductors = 0
        self.signals.inductors.connect(lambda s: self.__setattr__("inductors", s))
        
        self.request_current_relays()

    def set_inds(self, value):
        self.send('{"command":{"set_inductors":%s}}' % (str(value)))

    def relays_max(self):
        self.send('{"command":{"set_inductors":127}}')

    def relays_min(self):
        self.send('{"command":{"set_inductors":0}}')

    def relays_lup(self):
        self.send('{"command":"lup"}')

    def relays_ldn(self):
        self.send('{"command":"ldn"}')
        
    def request_current_relays(self):
        self.send('{"request":"current_relays"}')

    def set_input(self, state):
        self.send('{"command":{"set_input":%s}}' % (int(state)))

    def set_output(self, state):
        self.send('{"command":{"set_output":%s}}' % (int(state)))