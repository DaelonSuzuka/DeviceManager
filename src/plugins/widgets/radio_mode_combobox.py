from qtstrap import *
from codex import DeviceManager


@DeviceManager.subscribe_to("TS-480")
class RadioModeComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QListView { 
                background-color: palette(button); 
            }
            QListView::item {
                min-height: 40px; 
                max-height: 80px; 
            }
        """)
        self.setView(QListView(self))
        self.addItems(['Mode'])
        self.setMinimumHeight(40)
        self.setMaximumHeight(100)

    def connected(self, device):
        self.activated.connect(lambda: device.set_mode(self.currentText().lstrip(' ')))
        device.signals.mode.connect(lambda s: self.select_mode(s))
        self.clear()
        self.addItems([m for m in device.modes if m != ""])

    def disconected(self):
        self.clear()
        self.addItem("Mode")

    def addItems(self, texts):
        super().addItems(['    ' + t for t in texts])

    def select_mode(self, mode):
        for i in range(self.count()):
            if self.itemText(i).lstrip(' ') == mode:
                self.setCurrentIndex(i)

    def showPopup(self):
        super().showPopup()
        popup = self.findChild(QFrame)
        popup.move(popup.x(), self.mapToGlobal(self.rect().bottomLeft()).y())