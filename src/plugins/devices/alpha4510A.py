from devices import SerialDevice
from qt import *
from bundles import SigBundle

start_string = '$APW'
end_string = '*FF'


class MeterBuffer:
    def __init__(self):
        self.buffer = ""
        self.depth = 0

    def reset(self):
        self.buffer = ""
        self.depth = 0

    def insert_char(self, c):
        self.buffer += c

    def completed(self):
        if end_string in self.buffer and start_string not in self.buffer:
            self.buffer = ""

        if end_string in self.buffer:
            return True

        return False


class Alpha4510A(SerialDevice):
    profile_name = "Alpha4510A"

    def __init__(self, port=None, baud=38400, device=None):
        super().__init__(port=port, baud=baud, device=device)
        self.msg = MeterBuffer()
        signals = {
            'forward': [str], 
            'reverse': [str], 
            'swr': [str], 
            'temperature': [str], 
            'frequency': [str], 
            'mode': [str],
            'update': [dict]
        }
        self.signals = SigBundle(signals)

        self.last_results = {}

    def recieve(self, string):
        results = string.split(",")[1:-1]

        if len(results) == 5:
            self.last_results['forward'] = results[0]
            self.last_results['reverse'] = results[1]
            self.last_results['swr'] = results[2]
            self.last_results['temperature'] = results[3]
            self.last_results['frequency'] = results[4]

            self.signals.update.emit(self.last_results)
            self.signals.forward.emit(results[0])
            self.signals.reverse.emit(results[1])
            self.signals.swr.emit(results[2])
            self.signals.temperature.emit(results[3])
            self.signals.frequency.emit(results[4])