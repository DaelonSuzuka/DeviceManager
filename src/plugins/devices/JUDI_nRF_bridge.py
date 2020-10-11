from devices import SerialDevice, CommonMessagesMixin
from qt import *


class DTS6(CommonMessagesMixin, SerialDevice):
    profile_name = "JUDI-nRF-Bridge"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_tree.merge(self.common_message_tree)