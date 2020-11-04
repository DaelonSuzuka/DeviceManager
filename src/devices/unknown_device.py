from devices import SerialDevice, JudiStandardMixin
from qt import *
from .judi_filter import JudiFilter
from .null_filter import NullFilter
import time
from enum import Enum


class DeviceStates(Enum):
    enumeration_pending = 1
    enumeration_succeeded = 2
    enumeration_failed = 3


class UnknownDevice(JudiStandardMixin, SerialDevice):
    profile_name = "no profile"

    _bauds = [9600, 19200, 38400, 115200, 230400, 460800]
    handshake_table = {b:{} for b in _bauds}
    checker_table = {b:[] for b in _bauds}

    @classmethod
    def register_autodetect_info(cls, profiles):
        for _, p in profiles.items():
            if hasattr(p, 'autodetect'):
                info = p.autodetect
                for baud in info['bauds']:
                    if 'handshake' in info:
                        cls.handshake_table[baud][p.profile_name] = info['handshake']
                    if 'checker' in info:
                        cls.checker_table[baud].append(info['checker'])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_tree.merge(self.common_message_tree)
        self.filter = NullFilter()

        self.state = DeviceStates.enumeration_pending
        self.bauds = iter(self._bauds)

        self.cache_name = f'autodetect_cache:{self.port}'
        baud, name = QSettings().value(self.cache_name, (9600, ''))

        if name in self.handshake_table[baud]:
            self.set_baud_rate(int(baud))
            self.handshake_table[baud][name](self.send)
        
        self.last_transmit_time = time.time()
        self.last_handshake_time = time.time()

        self.do_handshakes()

    def do_handshakes(self):
        self.handshake()
        handshakes = self.handshake_table[self.baud]
        for _, fn in handshakes.items():
            fn(self.send)
        self.last_handshake_time = time.time()

    def do_checks(self):
        self.judi_checker(self.filter.buffer)
        for fn in self.checker_table[self.baud]:
            if result := fn(self.filter.buffer):
                self.name = result
                break
        return bool(self.name)

    def judi_checker(self, buffer):
        jf = JudiFilter()
        for c in buffer:
            if jf.insert_char(c):
                self.recieve(jf.buffer)
                jf.reset()
        return self.name

    def message_completed(self):
        # override this to disable it
        pass

    def transmit_next_message(self):
        # override this to rate limit the tx'ing of handshakes
        if (time.time() - self.last_transmit_time) > 0.1:
            if super().transmit_next_message():
                self.last_handshake_time = time.time()
            self.last_transmit_time = time.time()

    def communicate(self):
        super().communicate()

        if (time.time() - self.last_handshake_time) > 0.5:
            if self.do_checks():
                QSettings().setValue(self.cache_name, (self.baud, self.name))
                self.state = DeviceStates.enumeration_succeeded
            else:
                self.filter.reset()
                try:
                    self.set_baud_rate(next(self.bauds))
                except StopIteration:
                    self.state = DeviceStates.enumeration_failed

                self.do_handshakes()