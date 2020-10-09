from qt import *
from device_manager import DeviceManager
from plugins.widgets import *


class RadioControls(Widget):
    def create_widgets(self):
        self.setStyleSheet('QProgressBar { border: 1px solid grey; }')

        self.power_btns = RadioPowerButtons()
        self.freq_btns = RadioBandButtons()
        self.dummy_load = DummyLoadControls()

        self.mode = RadioModeComboBox()

        self.heat = HeatButton()
        self.time = TimeoutButton()

        self.bypass = BypassButton()
        self.memory_tune = MemoryTuneButton()
        self.full_tune = FullTuneButton()

        self.bypass.register(self.memory_tune, self.full_tune)
        self.memory_tune.register(self.bypass, self.full_tune)
        self.full_tune.register(self.bypass, self.memory_tune)

        self.timeout = TimeoutBar()
        self.key = RadioKeyButton()

        self.time.toggled.connect(self.timeout.set_suppressed)
        self.key.toggled.connect(self.timeout.set_running)
        self.timeout.timeout.connect(lambda: self.key.click())

    def build_layout(self):
        with CHBoxLayout(self, margins=(0, 0, 0, 0)) as hbox:
            hbox.add(self.power_btns, 2)
            hbox.add(VLine(), 1)
            hbox.add(self.freq_btns, 2)
            hbox.add(VLine(), 1)
            # hbox.add(self.dummy_load, 1)
            # hbox.add(VLine(), 1)

            with CVBoxLayout(hbox, 2, margins=(0, 0, 0, 0)) as vbox:
                with CHBoxLayout(vbox, 1, margins=(0, 0, 0, 0)) as box:
                    box.add(self.time)
                    box.add(QPushButton(disabled=True))
                    box.add(self.mode)

                vbox.add(self.key, 5)
                vbox.add(self.timeout)

                with CHBoxLayout(vbox, 1, margins=(0, 0, 0, 0)) as box:
                    box.add(self.bypass)
                    box.add(self.memory_tune)
                    box.add(self.full_tune)


class ServitorApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget { font-size: 16pt; }
            QPushButton { 
                max-width: 2000px; 
                max-height: 2000px; 
            } 
        """)
        
        self.parent().tabs.addTab(self, 'Servitor')

        self.setBackgroundRole(QPalette.Base)
        self.setAutoFillBackground(True)

        self.radio = RadioControls(self)

        with CHBoxLayout(self) as hbox:
            with CVBoxLayout(hbox, 1, margins=(0, 0, 0, 0)) as vbox:
                vbox.setAlignment(Qt.AlignTop)
                vbox.add(RadioInfo(self))
                vbox.add(HLine())
                vbox.add(MeterInfo(self))
                vbox.add(HLine())
                vbox.add(RFSensorWidget(self))

            hbox.addWidget(VLine())

            with CVBoxLayout(hbox, 4, margins=(0, 0, 0, 0)) as vbox:
                vbox.add(self.radio, 7)
                vbox.add(HLine())
                vbox.add(DTS6Controls(self), 1)

    def close(self):
        self.radio.timeout.timer.stop()