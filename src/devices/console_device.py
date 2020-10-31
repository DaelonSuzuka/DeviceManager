from qt import *
from devices import SerialDevice, NullFilter


class ConsoleDevice(SerialDevice):
    profile_name = "ConsoleDevice"

    def __init__(self, port=None, baud=115200, device=None):
        super().__init__(port=port, baud=baud, device=device)

        self.filter = NullFilter()
        self.message_tree = None
        self.w = None

    def recieve(self, string):
        """ do something when a complete string is captured in self.communicate() """
        self.log.debug(f"RX: {string}")
        self.base_signals.send.emit(string)
        
    def message_completed(self):
        self.recieve(self.filter.buffer)
        self.filter.reset()