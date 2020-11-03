from devices import SerialDevice, CommonMessagesMixin
from qt import *
from .judi_filter import JudiFilter
from .null_filter import NullFilter
import time
from enum import Enum


class DeviceStates(Enum):
    enumeration_pending = 1
    enumeration_succeeded = 2
    enumeration_failed = 3


class UnknownDevice(CommonMessagesMixin, SerialDevice):
    profile_name = "no profile"

    _bauds = [9600, 19200, 38400, 115200, 230400, 460800]
    handshake_table = {b:[] for b in _bauds}
    checker_table = {b:[] for b in _bauds}

    @classmethod
    def register_autodetect_info(cls, profiles):
        for _, p in profiles.items():
            if hasattr(p, 'autodetect'):
                info = p.autodetect
                for baud in info['bauds']:
                    if 'handshake' in info:
                        cls.handshake_table[baud].append(info['handshake'])
                    if 'checker' in info:
                        cls.checker_table[baud].append(info['checker'])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_tree.merge(self.common_message_tree)
        self.filter = NullFilter()

        self.bauds = iter(self._bauds)

        self.state = DeviceStates.enumeration_pending
        self.do_handshakes()

    def do_handshakes(self):
        for fn in self.handshake_table[self.baud]:
            if command := fn():
                self.send(command)
        self.handshake()
        self.last_handshake_time = time.time()

    def judi_checker(self, buffer):
        jf = JudiFilter()
        for c in buffer:
            if jf.insert_char(c):
                self.recieve(jf.buffer)
                jf.reset()
        return self.name

    def message_completed(self):
        # override the super's method and disable it
        pass

    def communicate(self):
        super().communicate()

        if (time.time() - self.last_handshake_time) > 0.5:
            self.judi_checker(self.filter.buffer)
            for fn in self.checker_table[self.baud]:
                if result := fn(self.filter.buffer):
                    self.name = result
                    break
            if self.name == '':
                self.filter.reset()

                try:
                    self.set_baud_rate(next(self.bauds))
                except StopIteration:
                    self.state = DeviceStates.enumeration_failed

                self.do_handshakes()
            
        if self.name != '':
            self.state = DeviceStates.enumeration_succeeded