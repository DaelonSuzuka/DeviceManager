from qt import *
from devices import SerialDevice, DeviceWidget
from vt102 import screen, stream


class NullBuffer:
    def __init__(self):
        self.buffer = ""

    def reset(self):
        self.buffer = ""

    def insert_char(self, c):
        self.buffer = c

    def completed(self):
        if self.buffer:
            return True 
        return False


class SerialMonitor(SerialDevice):
    profile_name = "SerialMonitor"

    def __init__(self, port=None, baud=115200, device=None):
        super().__init__(port=port, baud=baud, device=device)

        self.msg = NullBuffer()
        self.message_tree = None
        self.w = None

    def recieve(self, string):
        self.log.debug(f"RX: {string}")

    @property
    def widget(self):
        if self.w is None:
            self.w = SerialMonitorDockWidget(self.title, self.guid)
            self.connect_monitor(self.w.monitor)
        
        return self.w


class SerialMonitorWidget(QTextEdit):
    tx = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)
        self.st = stream()
        self.sc = screen((40, 120))
        self.sc.attach(self.st)

    def keyPressEvent(self, event: PySide2.QtGui.QKeyEvent):
        self.tx.emit(event.text())

    def rx(self, string):
        self.st.process(string)

        lines = [l for l in self.sc.display]

         
        self.setText("\n".join(lines))


class SerialMonitorDockWidget(DeviceWidget):
    def build_layout(self):
        grid = QGridLayout()
        
        self.monitor = SerialMonitorWidget()
        grid.addWidget(self.monitor)

        self.setWidget(QWidget(layout=grid))
