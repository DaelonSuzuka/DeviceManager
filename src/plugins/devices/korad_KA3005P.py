from devices import SerialDevice
from qt import *


class KoradKA3005P(SerialDevice):
    profile_name = "KoradKA3005P"

    def __init__(self, **kwargs):
        super().__init__(**kwargs) 

    # what does this do?
    def get_status(self):
        self.command("STATUS?")
        return ord(self.ser.read(1))

    def get_idn(self):
        return self.feedback_command("*IDN?")

    def turn_on(self):
        self.command("OUT1")

    def turn_off(self):
        self.command("OUT0")

    def recall_memory(self,bank):
        self.command("RCL%s" % bank)

    def save_memory(self,bank):
        self.command("SAV%s" % bank)

    def turn_on_OCP(self):
        self.command("OCP1")

    def turn_off_OCP(self):
        self.command("OCP0")

    def turn_on_OVP(self):
        self.command("OVP1")

    def turn_off_OVP(self):
        self.command("OVP0")

    #  def set_tracking_mode(value = :independent)
    #    mode = [:independent, :series, :parallel].index(value)
    #    mode ? command("TRACK#{mode}") : raise(Exception.new("UnknownModeException"))
    #  end

    def set_current(self, channel, value):
        self.command("ISET%s:%s" % ( channel, value))

    def set_voltage(self, channel, value):
        self.command("VSET%s:%s" % ( channel, value))

    def get_stored_current(self, channel):
        return self.feedback_command("ISET" + str(channel))

    def get_stored_voltage(self, channel):
        return self.feedback_command("VSET" + str(channel))

    def get_output_current(self, channel):
        return self.feedback_command("IOUT" + str(channel))

    def get_output_voltage(self, channel):
        return self.feedback_command("VOUT" + str(channel))


if __name__ == "__main__":
    korad = KoradKA3005P()
    korad.name = "powersupply"
    korad.port = '/dev/ttyS5'
    korad.baud = 9600
    korad.set_voltage(1,7)
    print(korad.get_idn())