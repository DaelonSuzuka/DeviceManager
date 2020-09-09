from ctypes import alignment
from qt import *
from device_widgets import *
from servitor import KeyButton, RadioInfo, MeterInfo


class ManualTuner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        stylesheet = """
            QPushButton { 
                width: 80px; 
                height: 35px;
                max-width: 80px; 
                max-height: 35px;  
            } 
            QLineEdit { 
                width: 80px; 
                height: 35px;
                max-width: 80px; 
                max-height: 35px;  
            } 
        """
        self.setStyleSheet('QWidget { font-size: 16pt; }')
        # self.setBackgroundRole(QPalette.Base)
        # self.setAutoFillBackground(True)

        self.key = KeyButton()

        self.sensor = RFSensorWidget(self)
        self.switch = SW100Widget(self)
        self.caps = VariableCapacitorWidget(self)
        self.caps.setStyleSheet(stylesheet)
        self.inds = VariableInductorWidget(self)
        self.inds.setStyleSheet(stylesheet)

        with CHBoxLayout(self) as layout:
            with CVBoxLayout(layout) as vbox:
                vbox.add(QLabel())
                vbox.add(self.key)
                vbox.add(HLine())
                vbox.add(RadioInfo())
                vbox.add(HLine())
                vbox.add(MeterInfo())
                vbox.addStretch(5)
            
            layout.add(VLine())
            
            with CVBoxLayout(layout) as vbox:
                vbox.add(RFSensorWidget())
                vbox.addStretch(1)
                vbox.add(HLine())
                with CHBoxLayout(vbox) as hbox:
                    hbox.add(self.caps)
                    hbox.add(VLine())
                    hbox.add(self.inds)
