from qtstrap import *
from codex import DeviceManager
from codex import SW4U


class SwitchControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.guid = ''
        self.switch = None

        self.setEnabled(False)

        self.label = QLabel('?')
        self.locate = QPushButton('Locate')

        with CGridLayout(self) as layout:
            layout.add(self.label)
            layout.add(self.locate)

    def connect_switch(self, switch: SW4U):
        self.switch = switch
        self.guid = switch.guid
        self.label.setText(switch.title)
        self.setEnabled(True)
        self.locate.clicked.connect(switch.locate)
        
    def disconnect_switch(self):
        self.switch = None
        self.guid = ''
        self.label.setText('?')
        self.setEnabled(False)


@DeviceManager.subscribe
class QuadSw4uApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.tab_name = 'Quad Switch'

        self.one = SwitchControls(self)
        self.two = SwitchControls(self)
        self.three = SwitchControls(self)
        self.four = SwitchControls(self)

        self.widgets = []
        with CGridLayout(self) as layout:
            self.widgets.append(layout.add(self.one, 0, 0))
            self.widgets.append(layout.add(self.two, 0, 1))
            self.widgets.append(layout.add(self.three, 1, 0))
            self.widgets.append(layout.add(self.four, 1, 1))

    def device_added(self, device):
        if device.profile_name == 'SW-4U':
            for widget in self.widgets:
                if widget.switch == None:
                    widget.connect_switch(device)
                    break

    def device_removed(self, guid):
        for widget in self.widgets:
            if widget.guid == guid:
                widget.disconnect_switch()
                break