from ctypes import alignment
from qt import *
from plugins.widgets import *


class TunerButtons(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QPushButton { 
                max-width: 2000px; 
                max-height: 2000px; 
                min-width: 200px; 
                min-height: 200px; 
            } 
        """)

        self.upper_left = QPushButton(checkable=True)
        self.upper_left.setIconSize(QSize(100, 100))
        self.upper_left.setIcon(QIcon('img/upper_left.png'))
        self.upper_right = QPushButton(checkable=True)
        self.upper_right.setIconSize(QSize(100, 100))
        self.upper_right.setIcon(QIcon('img/upper_right.png'))
        self.bottom_left = QPushButton(checkable=True)
        self.bottom_left.setIconSize(QSize(100, 100))
        self.bottom_left.setIcon(QIcon('img/bottom_left.png'))
        self.bottom_right = QPushButton(checkable=True)
        self.bottom_right.setIconSize(QSize(100, 100))
        self.bottom_right.setIcon(QIcon('img/bottom_right.png'))

        self.buttons = QButtonGroup()
        self.buttons.addButton(self.upper_left)
        self.buttons.addButton(self.upper_right)
        self.buttons.addButton(self.bottom_left)
        self.buttons.addButton(self.bottom_right)

        with CGridLayout(self) as layout:
            layout.add(self.upper_left, 0, 0)
            layout.add(self.upper_right, 0, 1)
            layout.add(self.bottom_left, 1, 0)
            layout.add(self.bottom_right, 1, 1)


class ManualTunerApp(QWidget):
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

        self.parent().tabs.addTab(self, 'Manual Tuner')

        self.key = RadioKeyButton()

        self.sensor = RFSensorWidget()
        self.chart = RFSensorChartWidget()

        self.switch = SW100Widget()
        self.caps = VariableCapacitorWidget()
        self.caps.setStyleSheet(stylesheet)
        self.inds = VariableInductorWidget()
        self.inds.setStyleSheet(stylesheet)

        with CHBoxLayout(self) as layout:
            with CVBoxLayout(layout) as vbox:
                vbox.add(self.key)
                vbox.addStretch(5)
                vbox.add(HLine())
                vbox.add(RadioInfo())
                vbox.add(HLine())
                vbox.add(MeterInfo())
            
            layout.add(VLine())
            
            with CVBoxLayout(layout) as vbox:
                with CHBoxLayout(vbox, 1) as hbox:
                    hbox.add(RFSensorWidget())
                    hbox.add(self.chart)
                # vbox.add(RFSensorWidget())
                # vbox.add(self.chart, 1)
                # vbox.add(FlatRFSensorWidget(self))
                
                vbox.add(HLine())
                with CHBoxLayout(vbox) as hbox:
                    with CVBoxLayout(hbox) as vbox:
                        vbox.add(self.caps)
                        vbox.add(HLine())
                        vbox.add(self.inds)

                    hbox.add(VLine())
                    hbox.add(TunerButtons(self))

