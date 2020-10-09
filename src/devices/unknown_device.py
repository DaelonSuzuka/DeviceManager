from devices import SerialDevice, CommonMessagesMixin

from qt import *


class UnknownDevice(CommonMessagesMixin, SerialDevice):
    profile_name = "no profile"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.message_tree.merge(self.common_message_tree)

        self.handshake()