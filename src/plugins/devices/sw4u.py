from codex import SerialDevice, JudiStandardMixin
from qtstrap import *
from functools import partial
import logging


class Signals(QObject):
    antenna = Signal(int)
    forward = Signal(float)
    reverse = Signal(float)
    frequency = Signal(int)
    auto = Signal(int)
    auto_table = Signal(dict)

    @property
    def message_tree(self):
        return {
            "update": {
                "auto": self.auto.emit,
                "auto_table": self.auto_table.emit,
                "antenna": self.antenna.emit,
                "frequency": self.frequency.emit,
            }
        }


class SW4U(JudiStandardMixin, SerialDevice):
    profile_name = "SW-4U"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)

        # startup messages
        self.get_antenna()
        self.get_auto_table()
        self.get_auto_mode()

    def set_antenna(self, ant):
        self.send('{"command":{"set_antenna":"%s"}}' % (ant))

    def get_antenna(self):
        self.send('{"request":"antenna"}')

    def set_auto_mode(self, state):
        self.send('{"command":{"set_auto":"%s"}}' % (state))

    def get_auto_mode(self):
        self.send('{"request":"auto"}')

    def toggle_auto_mode(self, state):
        if state:
            self.set_auto_mode("on")
        else:
            self.set_auto_mode("off")

    def set_auto_table(self, band, ant):
        self.send('{"command":{"set_auto_table":{"%s":%s}}}' % (band, ant))

    def get_auto_table(self):
        self.send('{"request":"auto_table"}')

