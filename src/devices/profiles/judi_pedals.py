from devices import SerialDevice, DeviceWidget, CommonMessagesMixin
from qt import *


class Signals(QObject):
    button_pressed = Signal(str)
    button_released = Signal(str)

    @property
    def message_tree(self):
        return {
            "update": {
                "button_pressed": self.button_pressed.emit,
                "button_released": self.button_released.emit
            }
        }


class JudiPedals(CommonMessagesMixin, SerialDevice):
    profile_name = "judipedals"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)

    @property
    def widget(self):
        w = JudiPedalsWidget(self.title, self.guid)

        self.signals.button_pressed.connect(w.button_pressed)
        self.signals.button_released.connect(w.button_released)

        return w


class JudiPedalsWidget(DeviceWidget):
    def build_layout(self):
        self.one = QPushButton(checkable=True)
        self.two = QPushButton(checkable=True)
        self.three = QPushButton(checkable=True)
        self.foud = QPushButton(checkable=True)
        
        layout = QHBoxLayout()

        layout.addWidget(self.one)
        layout.addWidget(self.two)
        layout.addWidget(self.three)
        layout.addWidget(self.foud)

        self.setWidget(QWidget(layout=layout))

    def button_pressed(self, button):
        if button == '1':
            self.one.setChecked(True)
        if button == '2':
            self.two.setChecked(True)
        if button == '3':
            self.three.setChecked(True)
        if button == '4':
            self.foud.setChecked(True)

    def button_released(self, button):
        if button == '1':
            self.one.setChecked(False)
        if button == '2':
            self.two.setChecked(False)
        if button == '3':
            self.three.setChecked(False)
        if button == '4':
            self.foud.setChecked(False)
