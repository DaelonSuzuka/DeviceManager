from devices import SerialDevice, CommonMessagesMixin
from qt import *


class Signals(QObject):
    @property
    def message_tree(self):
        return {}

class Protoboard(CommonMessagesMixin, SerialDevice):
    profile_name = "Protoboard"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)