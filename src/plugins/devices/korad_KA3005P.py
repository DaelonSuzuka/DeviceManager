from devices import SerialDevice
from qt import *


class Signals(QObject):
    pass


class KoradKA3005P(SerialDevice):
    profile_name = "KoradKA3005P"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()

    # what does this do?
    def get_status(self):
        self.send("STATUS?")

    def get_idn(self):
        self.send("*IDN?")

    def turn_on(self):
        self.send("OUT1")

    def turn_off(self):
        self.send("OUT0")

    def recall_memory(self, bank):
        self.send("RCL%s" % bank)

    def save_memory(self, bank):
        self.send("SAV%s" % bank)

    def turn_on_OCP(self):
        self.send("OCP1")

    def turn_off_OCP(self):
        self.send("OCP0")

    def turn_on_OVP(self):
        self.send("OVP1")

    def turn_off_OVP(self):
        self.send("OVP0")

    def set_current(self, channel, value):
        self.send("ISET%s:%s" % ( channel, value))

    def set_voltage(self, channel, value):
        self.send("VSET%s:%s" % ( channel, value))

    def get_stored_current(self, channel):
        self.send("ISET" + str(channel))

    def get_stored_voltage(self, channel):
        self.send("VSET" + str(channel))

    def get_output_current(self, channel):
        self.send("IOUT" + str(channel))

    def get_output_voltage(self, channel):
        self.send("VOUT" + str(channel))