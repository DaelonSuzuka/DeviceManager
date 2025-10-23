import json
from collections import deque
from copy import deepcopy
from dataclasses import dataclass

import numpy as np
from codex import DeviceManager
from qtstrap import *

from plugins.devices.alpha4510A import Alpha4510A
from plugins.devices.calibration_target import CalibrationTarget
from plugins.devices.dts6 import DTS6
from plugins.kenwood_ts480.kenwoodTS480 import TS480


@dataclass
class Point:
    freq: str
    power: str


class DataQueue:
    def __init__(self, keys, stabilize: dict[str, float] = {}, maxlen=10):
        self.stabilize = stabilize
        self.reject_count = 0

        self._data: dict[str, deque] = {}
        for key in keys:
            self._data[key] = deque(maxlen=maxlen)

    def __getitem__(self, key):
        return self._data[key]

    def clear(self):
        for _, queue in self._data.items():
            queue.clear()
        self.reject_count = 0

    def is_ready(self):
        for name, queue in self._data.items():
            if len(queue) == queue.maxlen:
                if name in self.stabilize:
                    x = np.median(queue)
                    if x != 0:
                        if ((max(queue) - min(queue)) / x) > self.stabilize[name]:
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
    finished = Signal(dict)

    def __init__(self):
        super().__init__()

        self.switch: DTS6
        self.meter: Alpha4510A
        self.radio: TS480
        self.target: CalibrationTarget
        self.target_description = {}

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.update())

        self.points = []
        self.current_point = 0
        self.results = []
        self.script = []

        fields = [
            # meter
            'm_fwd',
            'm_rev',
            'm_swr',
            'm_freq',
            'm_temp',
            # target
            't_fwd_volts',
            't_rev_volts',
            't_mq',
            't_fwd_watts',
            't_rev_watts',
            't_swr',
            't_freq',
        ]
        self.data = DataQueue(fields, stabilize={'m_fwd': 0.1, 'm_rev': 0.05, 't_fwd': 0.1})

    def alpha_rf_received(self, rf_data):
        self.data['m_fwd'].append(float(rf_data.get('forward', 0.0)))
        self.data['m_rev'].append(float(rf_data.get('reverse', 0.0)))
        self.data['m_swr'].append(float(rf_data.get('swr', 0.0)))
        self.data['m_freq'].append(float(rf_data.get('temperature', 0.0)))
        self.data['m_temp'].append(int(rf_data.get('frequency', 0)))

    def target_rf_received(self, rf_data):
        self.data['t_fwd_volts'].append(float(rf_data.get('fwdV', 0.0)))
        self.data['t_rev_volts'].append(float(rf_data.get('revV', 0.0)))
        self.data['t_mq'].append(float(rf_data.get('matchQ', 0.0)))
        self.data['t_fwd_watts'].append(float(rf_data.get('fwd', 0.0)))
        self.data['t_rev_watts'].append(float(rf_data.get('rev', 0.0)))
        self.data['t_swr'].append(float(rf_data.get('swr', 0.0)))
        self.data['t_freq'].append(float(rf_data.get('freq', 0.0)))

    def device_added(self, device):
        if device.profile_name == 'DTS-6':
            self.switch = device
        if device.profile_name == 'TS-480':
            self.radio = device
        if device.profile_name == 'Alpha4510A':
            self.meter = device
            self.meter.signals.update.connect(self.alpha_rf_received)
        if device.profile_name == 'CalibrationTarget':
            self.target = device
            self.target.signals.rf_received.connect(self.target_rf_received)

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

        self.started.emit(len(self.points))

        # self.target.send('version -j\n')
        # self.target.send('calibrate\n')
        self.switch.set_antenna(1)
        self.radio.set_vfoA_frequency(int(self.points[self.current_point].freq))
        self.radio.set_power_level(int(self.points[self.current_point].power))
        self.radio.key()
        self.data.clear()

    @Slot()
    def stop(self):
        self.timer.stop()

        if self.radio:
            self.radio.unkey()

        if self.target:
            self.target.send('\03')

        self.stopped.emit()

        self.final = {}
        self.final['data'] = deepcopy(self.results)
        self.final['script'] = deepcopy(self.script)
        self.final['device'] = {}
        self.target_description = {}

        with open('calibration.json', 'w') as f:
            json.dump(self.final, f)

        self.finished.emit(self.final)

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
