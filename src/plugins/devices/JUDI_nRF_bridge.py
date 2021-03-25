from codex import SerialDevice, JudiStandardMixin
from qt import *


class DTS6(JudiStandardMixin, SerialDevice):
    profile_name = "JUDI-nRF-Bridge"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_tree.merge(self.common_message_tree)