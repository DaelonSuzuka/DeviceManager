from qt import *
from device_manager import DeviceManager
from .constants import *
from plugins.widgets import *


@DeviceManager.subscribe
class RunTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        self.target = QComboBox()
        self.master = QComboBox()

        self.start = QPushButton('Start')
        self.stop = QPushButton('Stop', enabled=False)

        self.script = {'freqs': [], 'powers': []}
        self.freqs = PersistentListWidget('cal_freqs', items=freqs, selectionMode=QAbstractItemView.ExtendedSelection)
        self.powers = PersistentListWidget('cal_powers', items=powers, selectionMode=QAbstractItemView.ExtendedSelection)

        with CHBoxLayout(self) as layout:
            with layout.vbox() as layout:
                layout.add(RadioInfo())
                layout.add(HLine())
                layout.add(MeterInfo())
                layout.add(HLine())
                layout.add(CalibrationTargetInfo())
                layout.add(QLabel(), 1)
            with layout.vbox() as layout:
                with layout.hbox() as layout:
                    layout.add(self.start)
                    layout.add(self.stop)
                layout.add(QLabel('Freqs'))
                layout.add(self.freqs)
                layout.add(QLabel('Powers'))
                layout.add(self.powers)
            layout.add(QLabel(), 1)

    def get_script(self):
        self.script['freqs'] = [f.text() for f in self.freqs.selectedItems()]
        self.script['powers'] = [p.text() for p in self.powers.selectedItems()]
        return self.script

    def device_added(self, device):
        self.target.clear()
        self.target.addItems(device.title for _, device in self.devices.items())
        self.master.clear()
        self.master.addItems(device.title for _, device in self.devices.items())

    def device_removed(self, guid):
        self.target.clear()
        self.target.addItems(device.title for _, device in self.devices.items())
        self.master.clear()
        self.master.addItems(device.title for _, device in self.devices.items())
