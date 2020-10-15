from devices import SerialDevice, DelimiterBuffer
from qt import *


class Signals(QObject):
    forward = Signal(float)
    reverse = Signal(float)
    swr = Signal(float)
    temperature = Signal(float)
    frequency = Signal(float)
    mode = Signal(str)
    update = Signal(str)


class Alpha4510A(SerialDevice):
    profile_name = "Alpha4510A"

    def __init__(self, port=None, baud=38400, device=None):
        super().__init__(port=port, baud=baud, device=device)
        self.msg = DelimiterBuffer(start='$APW', end='*FF')
        self.signals = Signals()

        self.last_results = {}

    def recieve(self, string):
        results = string.split(",")[1:-1]

        if len(results) == 5:
            self.last_results['forward'] = float(results[0])
            self.last_results['reverse'] = float(results[1])
            self.last_results['swr'] = float(results[2])
            self.last_results['temperature'] = float(results[3])
            self.last_results['frequency'] = float(results[4])

            self.signals.update.emit(self.last_results)
            self.signals.forward.emit(float(results[0]))
            self.signals.reverse.emit(float(results[1]))
            self.signals.swr.emit(float(results[2]))
            self.signals.temperature.emit(float(results[3]))
            self.signals.frequency.emit(float(results[4]))