from qt import *
from device_widgets import *


class ManualTuner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.sensor = RFSensorWidget(self)
        self.switch = SW100Widget(self)
        self.caps = VariableCapacitorWidget(self)
        self.inds = VariableInductorWidget(self)

        with CGridLayout(self) as grid:
            grid.setRowStretch(2, 1)

            grid.addWidget(self.sensor, 0, 0)
            grid.addWidget(self.switch, 0, 1)
            grid.addWidget(self.caps, 1, 0)
            grid.addWidget(self.inds, 1, 1)
