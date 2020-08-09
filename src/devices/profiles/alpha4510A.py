from devices import SerialDevice, DeviceWidget
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

        self.last_results['forward'] = results[0]
        self.last_results['reverse'] = results[1]
        self.last_results['swr'] = results[2]
        self.last_results['temperature'] = results[3]
        self.last_results['frequency'] = results[4]

        #TODO: IndexError sometimes 
        self.signals.update.emit(self.last_results)
        self.signals.forward.emit(results[0])
        self.signals.reverse.emit(results[1])
        self.signals.swr.emit(results[2])
        self.signals.temperature.emit(results[3])
        self.signals.frequency.emit(results[4])

    @property
    def widget(self):
        w = Alpha4510AWidget(self.title, self.guid)

        # connect signals
        self.signals.forward.connect(lambda s: w.forward.setText(str(s)))
        self.signals.reverse.connect(lambda s: w.reverse.setText(str(s)))
        self.signals.swr.connect(lambda s: w.swr.setText(str(s)))
        self.signals.temperature.connect(lambda s: w.temperature.setText(str(s)))
        self.signals.frequency.connect(lambda s: w.frequency.setText(str(s)))

        return w


class Alpha4510AWidget(DeviceWidget):
    def create_widgets(self):
        self.forward = QLabel("?")
        self.reverse = QLabel("?")
        self.swr = QLabel("?")
        self.temperature = QLabel("?")
        self.frequency = QLabel("?")

    def build_layout(self):
        grid = QGridLayout()
        grid.setContentsMargins(10, 20, 10, 10)

        grid.addWidget(QLabel("Forward:"), 0, 1)
        grid.addWidget(self.forward, 0, 2)
        grid.addWidget(QLabel("Reverse:"), 1, 1)
        grid.addWidget(self.reverse, 1, 2)
        grid.addWidget(QLabel("SWR:"), 2, 1)
        grid.addWidget(self.swr, 2, 2)
        grid.addWidget(QLabel("Frequency:"), 3, 1)
        grid.addWidget(self.frequency, 3, 2)

        grid.setColumnStretch(5, 1)
        
        self.setWidget(QWidget(layout=grid))