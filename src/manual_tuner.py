from ctypes import alignment
from qt import *
from device_widgets import *
from servitor import KeyButton, RadioInfo, MeterInfo


class ManualTuner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet("""
            QWidget { font-size: 16pt; }
            QPushButton { 
                width: 160px; 
                height: 60px;
                max-width: 160px; 
                max-height: 60px;  
            } 
        """)
        # self.setBackgroundRole(QPalette.Base)
        # self.setAutoFillBackground(True)

        self.key = KeyButton()

        self.sensor = RFSensorWidget(self)
        self.switch = SW100Widget(self)
        self.caps = VariableCapacitorWidget(self)
        self.inds = VariableInductorWidget(self)

        with CHBoxLayout(self) as layout:
            # with CVBoxLayout(layout, 1) as vbox:
            #     vbox.addWidget(self.key)
            #     vbox.addWidget(QLabel(), 5)
            #     vbox.addWidget(HLine())
            #     vbox.addWidget(RadioInfo())
            #     vbox.addWidget(HLine())
            #     vbox.addWidget(MeterInfo())
            #     # vbox.addWidget(HLine())
            
            # layout.addWidget(VLine())
            
            with CVBoxLayout(layout, 2, alignment=Qt.AlignHCenter|Qt.AlignTop) as vbox:
                vbox.addWidget(RFSensorWidget())
                vbox.addWidget(HLine())
                vbox.addWidget(self.caps)
                vbox.addWidget(HLine())
                vbox.addWidget(self.inds)
