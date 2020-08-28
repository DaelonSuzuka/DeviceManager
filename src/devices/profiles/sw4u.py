from devices import SerialDevice, DeviceWidget, CommonMessagesMixin
from qt import *
from functools import partial
import logging


class Signals(QObject):
    antenna = Signal(int)
    forward = Signal(float)
    reverse = Signal(float)
    frequency = Signal(int)
    auto = Signal(int)
    auto_table = Signal(dict)

    @property
    def message_tree(self):
        return {
            "update": {
                "auto": self.auto.emit,
                "auto_table": self.auto_table.emit,
                "antenna": self.antenna.emit,
                "frequency": self.frequency.emit,
            }
        }


class SW4U(CommonMessagesMixin, SerialDevice):
    profile_name = "SW-4U"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)

        # startup messages
        self.get_antenna()
        self.get_auto_table()
        self.get_auto_mode()

    def set_antenna(self, ant):
        self.send('{"command":{"set_antenna":"%s"}}' % (ant))

    def get_antenna(self):
        self.send('{"request":"antenna"}')

    def set_auto_mode(self, state):
        self.send('{"command":{"set_auto":"%s"}}' % (state))

    def get_auto_mode(self):
        self.send('{"request":"auto"}')

    def toggle_auto_mode(self, state):
        if state:
            self.set_auto_mode("on")
        else:
            self.set_auto_mode("off")

    def set_auto_table(self, band, ant):
        self.send('{"command":{"set_auto_table":{"%s":%s}}}' % (band, ant))

    def get_auto_table(self):
        self.send('{"request":"auto_table"}')

    @property
    def widget(self):
        w = SW4UWidget(self.title, self.guid)

        # connect signals
        self.signals.antenna.connect(w.ant_btns.select)
        self.signals.auto.connect(lambda i: w.auto_btns.auto.setChecked(bool(i)))
        self.signals.auto_table.connect(w.auto_btns.popup.update)
        self.signals.frequency.connect(lambda s: w.rf_panel.frequency.setText(str(s)))
        
        self.get_antenna()
        self.get_auto_table()
        self.get_auto_mode()

        w.ant_btns.set_antenna.connect(lambda i: self.set_antenna(str(i)))
        w.auto_btns.auto.clicked.connect(self.toggle_auto_mode)
        w.auto_btns.popup.set_auto_table.connect(self.set_auto_table)

        return w


class SW4UWidget(DeviceWidget):
    def create_widgets(self):
        self.ant_btns = AntennaButtons()
        self.rf_panel = RFPanel()
        self.auto_btns = AutoButtons()

    def connect_signals(self):
        pass

    def build_layout(self):
        self.setStyleSheet("""
            QGroupBox { font: 20px}
            QLabel { font: 20px}
            QPushButton { font: 20px}
        """)

        grid = QGridLayout()
        grid.setContentsMargins(10, 20, 10, 10)

        grid.addWidget(self.rf_panel, 0, 0, 1, 2)
        grid.addWidget(self.auto_btns, 0, 2, 1, 2)
        grid.addWidget(self.ant_btns, 1, 0, 1, 3)        
        
        self.setWidget(QWidget(layout=grid))

    def select(self, antenna):
        for i, button in enumerate(self.ant_btns.buttons()):
            if i == antenna:
                button.setChecked(True)


class RFPanel(QGroupBox):
    def __init__(self):
        super().__init__("RF")
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        
        # widgets
        self.frequency = QLabel("?")

        # layout
        grid = QGridLayout(self)
        grid.addWidget(QLabel("Frequency:"), 0, 4)
        grid.addWidget(self.frequency, 0, 5)


class AntennaButtons(QGroupBox):    
    set_antenna = Signal(int)

    def __init__(self):
        super().__init__("Select Antenna")
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.group = QButtonGroup()

        # widgets and layout
        grid = QGridLayout(self)
        for i, name in enumerate(["None", "One", "Two", "Three", "Four",]):
            button = QPushButton(name, clicked=partial(self.set_antenna.emit, i), checkable=True)
            self.group.addButton(button)
            grid.addWidget(button, 0, i)

    def select(self, antenna):
        for i, button in enumerate(self.group.buttons()):
            if i == antenna:
                button.setChecked(True)


class AutoButtons(QGroupBox):
    def __init__(self):
        super().__init__("Auto Mode")
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        
        # widgets
        self.auto = QPushButton("Auto", checkable=True)
        self.edit = QPushButton("Edit")
        self.popup = AutoTablePopup()

        self.edit.clicked.connect(lambda: self.show_popup())

        # layout
        grid = QGridLayout(self)
        grid.addWidget(self.auto, 0, 0)
        grid.addWidget(self.edit, 0, 1)
        grid.setColumnStretch(5, 1)
    
    def show_popup(self):
        self.popup.center()
        self.popup.show()


class AutoTablePopup(QWidget):
    set_auto_table = Signal(str, int)

    def __init__(self):
        super().__init__()
        # widgets
        self.bands = [
            "1.8 MHz / 160 Meters",
            "3.5 MHz / 80 Meters",
            "7 MHz / 40 Meters",
            "10 MHz / 30 Meters",
            "14 MHz / 20 Meters",
            "18 MHz / 17 Meters",
            "21 MHz / 15 Meters",
            "24 MHz / 12 Meters",
            "28 MHz / 10 Meters",
            "50  MHz / 6 Meters",
        ]
        self.ants = [i for i in range(5)]
        self.radio_buttons = [[None for a in self.ants] for b in range(len(self.bands))]
        self.button_groups = [QButtonGroup() for b in range(len(self.bands))]
        
        # layout
        grid = QGridLayout(self)
        for i, band in enumerate(self.bands):
            grid.addWidget(QLabel(f"{band}: "), i, 0)

            for j, ant in enumerate(self.ants):
                radio = QRadioButton(str(ant))
                radio.clicked.connect(partial(self.set_auto_table.emit, str(i), ant))
                
                self.button_groups[i].addButton(radio)
                self.radio_buttons[i][j] = radio
                grid.addWidget(radio, i, j + 1)

    def update(self, table):
        # print(table)
        # print(self.radio_buttons)
        for k, v in table.items():
            self.radio_buttons[int(k)][int(v)].setChecked(True)

    def center(self):
        screen = QtGui.QGuiApplication.screenAt(QtGui.QCursor().pos())
        fg = self.frameGeometry()
        fg.moveCenter(screen.geometry().center())
        self.move(fg.topLeft())