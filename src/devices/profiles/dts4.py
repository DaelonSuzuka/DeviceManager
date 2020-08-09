from devices import SerialDevice
from qt import *
import logging


class DTS4(SerialDevice):
    profile_name = "DTS-4"

    def __init__(self, port=None, baud=115200, device=None):
        super().__init__(port=port, baud=baud, device=device)

    def select_antenna(self, antenna):
        self.send(f"\r\nant set {antenna}\r\n")

    def read_antenna(self):
        self.send("\r\nant read\r\n")