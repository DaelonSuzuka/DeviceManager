from qt import *


class DeviceWidget(QDockWidget):
    def __init__(self, title, guid=""):
        super().__init__(title)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.guid = guid
        
        self.setStyleSheet("DeviceWidget { border: 1px solid grey;}")
        
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.starting_area = Qt.BottomDockWidgetArea
        self.dockLocationChanged.connect(self.adjustSize)

        self.create_widgets()
        self.connect_signals()
        self.build_layout()

    def create_widgets(self):
        pass

    def connect_signals(self):
        pass

    def build_layout(self):
        pass