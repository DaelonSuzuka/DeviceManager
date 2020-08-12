from devices import SerialDevice
from qt import *
import logging



class NewlineBuffer:
    def __init__(self):
        self.buffer = ""
        self.depth = 0

    def reset(self):
        self.buffer = ""
        self.depth = 0

    def insert_char(self, c):
        print(c)
        self.buffer += c

    def completed(self):
        if '\n' in self.buffer:
            print('got newline')
            return True

        return False


class Signals(QObject):
    antenna = Signal(int)


class DTS4(SerialDevice):
    profile_name = "DTS-4"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.msg = NewlineBuffer()
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