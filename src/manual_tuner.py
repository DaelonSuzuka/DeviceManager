from ctypes import alignment
from qt import *
from device_widgets import *
from servitor import KeyButton, RadioInfo, MeterInfo


class ManualTuner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet("""
            QWidget { font-size: 16pt; }
        """)
        # self.setBackgroundRole(QPalette.Base)
        # self.setAutoFillBackground(True)

        self.key = KeyButton()

        self.sensor = RFSensorWidget(self)
        self.switch = SW100Widget(self)
        self.caps = VariableCapacitorWidget(self)
        self.inds = VariableInductorWidget(self)

        with CHBoxLayout(self) as layout:
            with CVBoxLayout(layout, 1) as vbox:
                with CHBoxLayout(vbox) as hbox:
                    hbox.addWidget(self.key)
                vbox.addWidget(HLine())
                vbox.addWidget(RadioInfo(), 1)
                vbox.addWidget(HLine())
                vbox.addWidget(MeterInfo(), 1)
            
            layout.addWidget(VLine())
            
            with CVBoxLayout(layout, 2, alignment=Qt.AlignLeft) as vbox:
                vbox.addWidget(self.sensor)
                vbox.addWidget(HLine())
                vbox.addWidget(self.switch)
                vbox.addWidget(HLine())
                vbox.addWidget(self.caps)
                vbox.addWidget(HLine())
                vbox.addWidget(self.inds)
