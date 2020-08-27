from qt import *
from devices import SerialDevice, DeviceWidget
from serial import SerialException
from serial_monitor import SerialMonitorWidget


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


class RadioInterface(SerialDevice):
    profile_name = "RadioInterface"

    def __init__(self, port=None, baud=9600, device=None):
        super().__init__(port=port, baud=baud, device=device)

        self.msg = NullBuffer()
        self.message_tree = None
        self.w = None

    def recieve(self, string):
        """ do something when a complete string is captured in self.communicate() """
        self.log.debug(f"RX: {string}")
        self.base_signals.send.emit(string)
        
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