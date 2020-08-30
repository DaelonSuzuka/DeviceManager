from devices import SerialDevice, DeviceWidget, CommonMessagesMixin
from qt import *


class JudiPedals(CommonMessagesMixin, SerialDevice):
    profile_name = "judipedals"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_tree.merge(self.common_message_tree)

    @property
    def widget(self):
        w = JudiPedalsWidget(self.title, self.guid)
        return w


class JudiPedalsWidget(DeviceWidget):
    def build_layout(self):
        grid = QGridLayout()
        grid.addWidget(QLabel("Under Construction..."))
        self.setWidget(QWidget(layout=grid))