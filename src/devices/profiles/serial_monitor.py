from qt import *
from devices import SerialDevice, DeviceWidget
from pyte import HistoryScreen, Screen, Stream
from serial import SerialException

class NullBuffer:
    def __init__(self):
        self.buffer = ""

    def reset(self):
        self.buffer = ""

    def insert_char(self, c):
        self.buffer += c

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

    def communicate(self):
        """ Handle comms with the serial port. Call this often, from an event loop or something. """
        if not self.active:
            return

        # serial transmit
        try:
            if not self.queue.empty():
                self.ser.write(self.queue.get().encode())
        except SerialException as e:
            self.log.exception(e)

        # serial recieve
        try:
            while self.ser.in_waiting:
                self.msg.insert_char(self.ser.read(1).decode())
        except Exception as e:
            name = ''
            if hasattr(self, 'profile_name'):
                name = self.profile_name
                
            self.log.exception(f"{name}: {self.port} | {e}")

        # handle completed message
        if self.msg.completed():
            msg = self.msg.buffer
            self.recieve(msg)
            self.msg.reset()

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
        self.setAcceptRichText(True)

        self.screen = Screen(80, 20, history=500)
        self.stream = Stream(self.screen)
        self.setText("\n".join(self.screen.display))

    def keyPressEvent(self, event: PySide2.QtGui.QKeyEvent):
        self.tx.emit(event.text())

    def rx(self, string):
        self.stream.feed(string)
        self.setText("\n".join(self.screen.display))


class SerialMonitorDockWidget(DeviceWidget):
    def build_layout(self):
        grid = QGridLayout()
        
        self.monitor = SerialMonitorWidget()
        grid.addWidget(self.monitor)

        self.setWidget(QWidget(layout=grid))
