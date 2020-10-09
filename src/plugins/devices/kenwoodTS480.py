from devices import SerialDevice
from qt import *
from bundles import SigBundle


class RadioBuffer:
    def __init__(self):
        self.buffer = ""
        self.depth = 0

    def reset(self):
        self.buffer = ""
        self.depth = 0

    def insert_char(self, c):
        self.buffer += c

    def completed(self):
        if ';' in self.buffer:
            return True

        return False


class TS480(SerialDevice):
    profile_name = "TS-480"
    modes = ["", "LSB", "USB", "CW", "FM", "AM", "CWR", "", "FSR"]
    max_power_level = 200
    min_power_level = 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        signals = {
            'swr': [str],
            'frequency': [str],
            'power': [str],
            'mode': [str],
            'keyed': [],
            'unkeyed': [],
        }
        self.signals = SigBundle(signals)
        self.msg = RadioBuffer()

        try:
            self.ser.responder = TS480Responder()
        except AttributeError:
            pass

        self.message_table = {
            'PC': lambda s: self.signals.power.emit(s.lstrip("0")),
            'FA': lambda s: self.signals.frequency.emit(s.lstrip("0")),
            'MD': lambda s: self.signals.mode.emit(self.modes[int(s)]),
            'IF': lambda s: self.status(s),
        }

        self.power = 0
        self.signals.power.connect(lambda s: self.__setattr__("power", int(s)))
        self.frequency = ""
        self.signals.frequency.connect(lambda s: self.__setattr__("frequency", s))

        self.check_id()
        self.check_id()
        self.check_status()
    
    def send(self, string):
        # append ";" to every command, so we don't have to keep repeating it
        string = string.rstrip(';') + ';'
        super().send(string)

    def recieve(self, string):
        self.log.debug(f"RX: {string}")

        key = string[:2]
        value = string[2:-1]
        table = self.message_table

        if key in table.keys() and callable(table[key]):
            table[key](value)

    def status(self, s):
        if s[26:27] == '1':
            self.signals.keyed.emit()
        elif s[26:27] == '0':
            self.signals.unkeyed.emit()

    def close(self):
        self.unkey()
        self.unkey()
        super().close()

    def check_id(self):
        self.send("ID")

    def check_status(self):
        self.send("IF")

    def toggle_key(self, state):
        if state:
            self.key()
        else:
            self.unkey()

    def key(self):
        self.send("TX0")
        QTimer.singleShot(50, self.check_status)

    def unkey(self):
        self.send("RX")
        QTimer.singleShot(50, self.check_status)

    def set_mode(self, mode):
        self.send("MD" + str(self.modes.index(mode)))
        self.get_mode()

    def get_mode(self):
        self.send("MD")

    def band_up(self):
        self.send("BU")
        self.get_vfoA_frequency()
        self.get_mode()

    def band_down(self):
        self.send("BD")
        self.get_vfoA_frequency()
        self.get_mode()

    def set_vfoA_frequency(self, frequency):
        self.send("FA" + str(frequency).rjust(11, '0'))
        self.get_vfoA_frequency()
        self.get_mode()

    def get_vfoA_frequency(self):
        self.send("FA")

    def increase_power_level(self):
        self.set_power_level(self.power + 5)

    def decrease_power_level(self):
        self.set_power_level(self.power - 5)

    def set_power_level(self, power):
        power = int(power)
        # valid power settings are multiples of 5, between 5 and 200
        if (power > self.max_power_level) or (power < self.min_power_level) or (power % 5 != 0):
            return

        command = "PC" + str(power).rjust(3, '0')
        self.send(command)
        self.get_power_level()

    def get_power_level(self):
        self.send("PC")


class TS480Responder:
    def __init__(self):
        self.table = {
            "ID": "ID020;",
            "PC": self._pc,
            "FA": self._fa,
            "MD": self._md,
            "BU": self._bu,
            "BD": self._bd,
            'IF': self._if,
            'TX': self._tx,
            'RX': self._rx,
        }
        self.power = 5
        self.keyed = False
        self.frequency = 14000000
        self.mode = 3
        self.freqs = [
            1800000, 3500000, 7000000, 10100000, 14000000,
            18068000, 21000000, 24890000, 28000000, 50000000,
        ]

    def respond(self, string):
        key = string[:2]
        if key in self.table.keys():
            if callable(self.table[key]):
                return self.table[key](string)
            else:
                return self.table[key]
                
        return ""

    def _if(self, string):
        return f'IF000{self.frequency}      000000000{int(self.keyed)}{self.mode}0000000;'

    def _tx(self, string):
        self.keyed = True
        return ""

    def _rx(self, string):
        self.keyed = False
        return ""

    def _pc(self, string):
        if string == "PC;":
            return f"PC{str(self.power).rjust(3, '0')};"
        
        self.power = int(string[2:-1].lstrip('0'))
        return ""

    def _fa(self, string):
        if string == "FA;":
            return f"FA{str(self.frequency).rjust(11, '0')};"

        self.frequency = int(string[2:-1].lstrip('0'))
        return ""

    def _md(self, string):
        if string == "MD;":
            return f"MD{self.mode};"
        
        self.mode = int(string[2:-1])
        return ""
        
    def _bu(self, string):
        i = self.freqs.index(self.frequency)
        self.frequency = self.freqs[i + 1]
        return ""

    def _bd(self, string):
        i = self.freqs.index(self.frequency)
        self.frequency = self.freqs[i - 1]
        return ""