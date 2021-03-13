from devices import SerialDevice, JudiStandardMixin
from qt import *


# class Signals(QObject):
#     antenna = Signal(int)

#     @property
#     def message_tree(self):
#         return {
#             "update": {
#                 "antenna": self.antenna.emit
#             }
#         }


class Z100Plus(JudiStandardMixin, SerialDevice):
    profile_name = "Z-100Plus"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.signals = Signals()
        # self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)