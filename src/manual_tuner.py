from qt import *
from device_widgets import *
from servitor import KeyButton, RadioInfo, MeterInfo


class ManualTuner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet("""
            QWidget { font-size: 16pt; }
            QPushButton { 
                max-width: 2000px; 
                max-height: 2000px; 
            } 
        """)

        self.key = KeyButton()

        self.sensor = RFSensorWidget(self)
        self.switch = SW100Widget(self)
        self.caps = VariableCapacitorWidget(self)
        self.inds = VariableInductorWidget(self)

        with CGridLayout(self) as grid:
            with CVBoxLayout() as vbox:
                grid.addLayout(vbox, 0, 0, 2, 1)
                with CHBoxLayout(vbox) as hbox:
                    hbox.addWidget(QPushButton())
                    hbox.addWidget(self.key)
                vbox.addWidget(HLine())
                vbox.addWidget(RadioInfo(), 1)
                vbox.addWidget(HLine())
                vbox.addWidget(MeterInfo(), 1)
            
            grid.addWidget(VLine(), 0, 1, 2, 1)

            grid.addWidget(self.sensor, 0, 2)
            grid.addWidget(self.switch, 0, 3)
            grid.addWidget(self.caps, 1, 2)
            grid.addWidget(self.inds, 1, 3)
