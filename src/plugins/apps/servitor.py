from qt import *
from device_manager import DeviceManager
from plugins.widgets import *


class RadioControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        self.link = RadioInterfaceLinkButton()

        self.time.toggled.connect(self.timeout.set_suppressed)
        self.key.toggled.connect(self.timeout.set_running)
        self.timeout.timeout.connect(lambda: self.key.click())
        self.time.setChecked(True)

        with CHBoxLayout(self, margins=(0, 0, 0, 0)) as layout:
            layout.add(self.power_btns, 2)
            layout.add(VLine(), 1)
            layout.add(self.freq_btns, 2)
            layout.add(VLine(), 1)
            # layout.add(self.dummy_load, 1)
            # layout.add(VLine(), 1)

            with layout.vbox(2, margins=(0, 0, 0, 0)) as layout:
                with layout.hbox(1, margins=(0, 0, 0, 0)) as layout:
                    layout.add(self.time)
                    layout.add(self.link)
                    layout.add(self.mode)

                layout.add(self.key, 5)
                layout.add(self.timeout)

                with layout.hbox(1, margins=(0, 0, 0, 0)) as layout:
                    layout.add(self.bypass)
                    layout.add(self.memory_tune)
                    layout.add(self.full_tune)


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
        
        self.tab_name = 'Servitor'

        self.setBackgroundRole(QPalette.Base)
        self.setAutoFillBackground(True)

        self.radio = RadioControls(self)

        with CHBoxLayout(self) as layout:
            with layout.vbox(1, margins=(0, 0, 0, 0)):
                layout().setAlignment(Qt.AlignTop)
                layout.add(RadioInfo(self))
                layout.add(HLine())
                layout.add(MeterInfo(self))
                layout.add(HLine())
                layout.add(CalibrationTargetInfo(self))

            layout.add(VLine())

            with layout.vbox(4, margins=(0, 0, 0, 0)):
                layout.add(self.radio, 7)
                layout.add(HLine())
                layout.add(DTS6Controls(self), 1)

    def close(self):
        self.radio.timeout.timer.stop()