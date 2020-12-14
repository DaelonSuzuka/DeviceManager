from devices import SerialDevice, JudiStandardMixin
from qt import *


class Signals(QObject):
    capacitors = Signal(int)
    inductors = Signal(int)
    hiloz = Signal(int)
    antenna = Signal(str)
    forward = Signal(float)
    forward_watts = Signal(float)
    reverse = Signal(float)
    reverse_watts = Signal(float)
    match_quality = Signal(float)
    swr = Signal(float)
    frequency = Signal(int)

    @property
    def message_tree(self):
        return {
            "update": {
                "relays": {
                    "capacitors": self.capacitors.emit,
                    "inductors": self.inductors.emit,
                    "hiloz": self.hiloz.emit,
                },
                "antenna": self.antenna.emit,
                "rf": {
                    "forward": self.forward.emit,
                    "forward_watts": self.forward_watts.emit,
                    "reverse": self.reverse.emit,
                    "reverse_watts": self.reverse_watts.emit,
                    "match_quality": self.match_quality.emit,
                    "swr": self.swr.emit,
                    "frequency": self.frequency.emit,
                },
            },
        }


class AT600ProII(JudiStandardMixin, SerialDevice):
    profile_name = "AT-600ProII"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)

    def full_tune(self):
        """Attempt to recall memories, full tune if none are found."""
        self.send('{"command":{"tune":"full"}}')

    def memory_tune(self):
        """Attempt to recall memories, quit if none are found."""
        self.send('{"command":{"tune":"memory"}}')

    def force_tune(self):
        """Full tune without attempting to recall memories"""
        self.send('{"command":{"tune":"force"}}')

    def select_antenna(self, antenna):
        self.send('{"command":{"select_antenna":%s}}' % antenna)

    def set_relays(self, caps=None, inds=None, z=None):
        cmd = '{"command":{"set_relays":{'
        if caps:
            cmd += '"caps":%s' % (caps)
        if inds:
            cmd += '"inds":%s' % (inds)
        if z:
            cmd += '"z":%s' % (z)
        cmd += "}}}"
        self.send(cmd)

    def set_threshold(self, threshold):
        self.send('{"command":{"set_threshold":"%s"}}' % (threshold))

    def set_auto_mode(self, state):
        self.send('{"command":{"set_auto":"%s"}}' % (state))

    def set_scale(self, scale):
        self.send('{"command":{"set_scale":"%s"}}' % (scale))

    def relays_cup(self):
        self.send('{"command":"cup"}')

    def relays_cdn(self):
        self.send('{"command":"cdn"}')

    def relays_lup(self):
        self.send('{"command":"lup"}')

    def relays_ldn(self):
        self.send('{"command":"ldn"}')