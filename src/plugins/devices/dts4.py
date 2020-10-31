from devices import SerialDevice, NewlineFilter
from qt import *


class Signals(QObject):
    antenna = Signal(int)


class DTS4(SerialDevice):
    profile_name = "DTS-4"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter = NewlineFilter()
        self.signals = Signals()

    def __init__(self, port=None, baud=115200, device=None):
        super().__init__(port=port, baud=baud, device=device)

    def select_antenna(self, antenna):
        self.send(f"ant set {antenna}\r\n")
        self.read_antenna()

    def read_antenna(self):
        self.send("ant read\r\n")
    
    def recieve(self, string):
        print(string)