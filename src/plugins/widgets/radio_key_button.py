from qt import *
from devices import DeviceManager
import qtawesome as qta
from style import qcolors


@DeviceManager.subscribe_to("TS-480")
class RadioKeyButton(IconToggleButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIconSize(QSize(100, 100))
        self.setStyleSheet(""" :checked { border: 5px solid #FF4136; border-radius: 10px; } """)
        self.icon_checked = qta.icon('mdi.radio-tower', color=qcolors.silver)
        self.icon_unchecked = qta.icon('mdi.radio-tower', color='gray')
        self.update_icon()

    def connected(self, device):
        device.signals.keyed.connect(lambda: self.setChecked(True))
        device.signals.unkeyed.connect(lambda: self.setChecked(False))
        self.clicked.connect(device.toggle_key)