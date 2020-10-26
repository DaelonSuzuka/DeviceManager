from qt import *
from device_manager import DeviceManager
from collections import deque
from dataclasses import dataclass
import numpy as np


@dataclass
class Point:
    freq: str
    power: str


class DataQueue:
    def __init__(self, keys, stabilize=[], maxlen=10):
        self._data = {}
        self.stabilize=stabilize
        self.reject_count = 0

        for key in keys:
            self._data[key] = deque(maxlen=maxlen)

    def __getitem__(self, key):
        return self._data[key]

    def clear(self):
        for _, queue in self._data.items():
            queue.clear()
        self.reject_count = 0

    def is_ready(self):
        for _, queue in self._data.items():
            if len(queue) != queue.maxlen:
                return False
        return True

    def is_ready(self):
        for name, queue in self._data.items():
            if len(queue) == queue.maxlen:
                if name in self.stabilize:
                    if ((max(queue) - min(queue)) / np.median(queue)) > self.stabilize[name]:
                        queue.popleft()
                        self.reject_count += 1
                        return False
            else:
                return False
            
        return True

    def get_data(self):
        result = {}
        for name, queue in self._data.items():
            result['_reject_count'] = self.reject_count
            result[name] = np.mean(queue)
            result[f'{name}_raw'] = list(queue)

        return result


@DeviceManager.subscribe
class CalibrationWorker(QObject):
    started = Signal(int)
    stopped = Signal()
    updated = Signal(int)
    finished = Signal(list)

    def __init__(self):
        super().__init__()

        self.switch = None
        self.meter = None
        self.radio = None
        self.target = None
        self.target_description = {}
        
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.update())

        self.points = []
        self.current_point = 0
        self.results = []
        self.script = []

        fields = [
            'm_fwd', 'm_rev', 'm_swr', 'm_freq', 'm_temp',
            't_fwd_volts', 't_rev_volts', 't_mq', 
            't_fwd_watts', 't_rev_watts', 't_swr', 't_freq',
        ]
        self.data = DataQueue(fields, stabilize={'m_freq':0.01})

    @Slot()
    def start(self, script):
        self.timer.start(50)

        self.points = []
        self.results = []
        self.script = script

        for freq in script['freqs']:
            for power in script['powers']:
                self.points.append(Point(freq, power))

        self.current_point = 0

        for _, device in self.devices.items():
            if device.profile_name == 'DTS-6':
                self.switch = device
            if device.profile_name == 'TS-480':
                self.radio = device
            if device.profile_name == 'Alpha4510A':
                self.meter = device
                signals = device.signals
                self.meter.signals.forward.connect(lambda x: self.data['m_fwd'].append(float(x)))
                self.meter.signals.reverse.connect(lambda x: self.data['m_rev'].append(float(x)))
                self.meter.signals.swr.connect(lambda x: self.data['m_swr'].append(float(x)))
                self.meter.signals.frequency.connect(lambda x: self.data['m_freq'].append(float(x)))
                self.meter.signals.temperature.connect(lambda x: self.data['m_temp'].append(float(x)))
            if device.profile_name == 'CalibrationTarget':
                self.target = device
                signals = device.signals
                signals.forward_volts.connect(lambda x: self.data['t_fwd_volts'].append(float(x)))
                signals.reverse_volts.connect(lambda x: self.data['t_rev_volts'].append(float(x)))
                signals.match_quality.connect(lambda x: self.data['t_mq'].append(float(x)))
                signals.forward.connect(lambda x: self.data['t_fwd_watts'].append(float(x)))
                signals.reverse.connect(lambda x: self.data['t_rev_watts'].append(float(x)))
                signals.swr.connect(lambda x: self.data['t_swr'].append(float(x)))
                signals.frequency.connect(lambda x: self.data['t_freq'].append(float(x)))
                signals.handshake_recieved.connect(lambda s: self.target_description_ready())

        self.started.emit(len(self.points))
        
        self.target.send('version -j\n')
        self.target.send('calibrate\n')
        self.switch.set_antenna(1)
        self.radio.set_vfoA_frequency(int(self.points[self.current_point].freq))
        self.radio.set_power_level(int(self.points[self.current_point].power))
        self.radio.key()
        self.data.clear()

    def target_description_ready(self):
        self.target_description = self.target.description

    @Slot()
    def stop(self):
        self.timer.stop()

        if self.radio:
            self.radio.unkey()

        if self.target:
            self.target.send('\03')

        self.switch = None
        self.meter = None
        self.radio = None
        self.target = None

        self.stopped.emit()

        results = {}
        results['data'] = self.results
        results['script'] = self.script
        results['device'] = self.target_description
        self.target_description = {}

        self.finished.emit(results)

    def update(self):
        self.updated.emit(self.current_point)

        if self.data.is_ready():
            result = self.data.get_data()
            result['freq'] = self.points[self.current_point].freq
            result['power'] = self.points[self.current_point].power
            
            self.results.append(result)
            self.current_point += 1
            
            if self.current_point == len(self.points):
                self.stop()
                return

            self.radio.unkey()
            self.radio.set_vfoA_frequency(int(self.points[self.current_point].freq))
            self.radio.set_power_level(int(self.points[self.current_point].power))
            self.radio.key()

            self.data.clear()