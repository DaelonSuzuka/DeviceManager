import json
import logging
from collections import deque
from dataclasses import dataclass
from itertools import product

import numpy as np
from codex import DeviceManager
from qtstrap import *

from plugins.devices.alpha4510A import Alpha4510A
from plugins.devices.dts6 import DTS6
from plugins.devices.mc200 import MC200
from plugins.kenwood_ts480.kenwoodTS480 import TS480


@dataclass
class Point:
    freq: str
    power: str


class DataQueue:
    def __init__(self, keys, stabilize={}, maxlen=10):
        self._data = {}
        self.stabilize = stabilize
        self.reject_count = 0
        self.time = TimeStamp()

        for key in keys:
            self._data[key] = deque(maxlen=maxlen)

    def __getitem__(self, key):
        return self._data[key]

    def clear(self):
        for _, queue in self._data.items():
            queue.clear()
        self.reject_count = 0
        self.time.update()

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
        result = {
            '_reject_count': self.reject_count,
            'time': self.time.time_since(),
            'data': {},
            'raw': {},
        }
        self.time.update()
        for name, queue in self._data.items():
            result['data'][name] = np.mean(queue)
            result['raw'][f'{name}_raw'] = list(queue)

        return result


@DeviceManager.subscribe
class RelayWorker(QObject):
    started = Signal(int)
    stopped = Signal()
    updated = Signal(int)
    finished = Signal(list)

    def __init__(self):
        super().__init__()

        self.log = logging.getLogger(__name__)

        self.switch: DTS6
        self.meter: Alpha4510A
        self.radio: TS480
        self.target: MC200

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.update())

        self.points = []
        self.current_point = 0
        self.previous_point = 0
        self.results = []
        self.script = []
        self.redo_count = 0

        fields = [
            'm_fwd',
            'm_rev',
            'm_swr',
            'm_freq',
            'm_temp',
            't_fwd_volts',
            't_rev_volts',
            't_fwd',
            't_rev',
            't_swr',
        ]
        self.data = DataQueue(fields, stabilize={'m_fwd': 0.1, 't_fwd': 0.1}, maxlen=5)

    def alpha_rf_received(self, rf_data):
        self.data['m_fwd'].append(float(rf_data.get('forward', 0.0)))
        self.data['m_rev'].append(float(rf_data.get('reverse', 0.0)))
        self.data['m_swr'].append(float(rf_data.get('swr', 0.0)))
        self.data['m_freq'].append(float(rf_data.get('temperature', 0.0)))
        self.data['m_temp'].append(int(rf_data.get('frequency', 0)))

    def target_rf_received(self, rf_data):
        self.data['t_fwd_volts'].append(float(rf_data.get('fwdV', 0.0)))
        self.data['t_rev_volts'].append(float(rf_data.get('revV', 0.0)))
        self.data['t_fwd'].append(float(rf_data.get('fwd', 0.0)))
        self.data['t_rev'].append(float(rf_data.get('rev', 0.0)))
        self.data['t_swr'].append(float(rf_data.get('swr', 0.0)))

    def device_added(self, device):
        if device.profile_name == 'DTS-6':
            self.switch = device
        if device.profile_name == 'TS-480':
            self.radio = device
        if device.profile_name == 'Alpha4510A':
            self.meter = device
            self.meter.signals.update.connect(self.alpha_rf_received)
        if device.profile_name == 'MC-200':
            self.target = device
            self.target.signals.rf_received.connect(self.target_rf_received)

    @Slot()
    def start(self, points):
        if self.switch is None or self.meter is None or self.radio is None or self.target is None:
            self.log.info("can't start test, device missing")
            return

        self.points = points

        self.results = []
        self.data.clear()
        self.log.info(f'starting test, collecting {len(self.points)} samples')

        # clear output file
        with open('data.jsonl', 'w') as f:
            f.write('')

        self.current_point = 0
        self.previous_point = 0

        self.started.emit(len(self.points))

        first_point = self.points[0]
        self.switch.set_antenna(first_point[0])
        self.radio.set_vfoA_frequency(first_point[1])
        self.radio.set_power_level(first_point[2])
        self.radio.key()

        self.timer.start(50)

    @Slot()
    def stop(self):
        self.log.info('stop')
        self.timer.stop()

        if self.radio:
            self.radio.unkey()

        self.stopped.emit()

        results = {
            'data': self.results,
        }

        with open('data.json', 'w') as f:
            json.dump(results, f)

        self.finished.emit(results)

    def update(self):
        self.log.info('update')
        self.updated.emit(self.current_point)

        if self.data.is_ready():
            p = self.points[self.current_point]
            prev = self.points[self.previous_point]

            # if (prev[2] != p[2] and p[2] == '005') or self.current_point == 0:
            # if (p[2] == '005') or self.current_point == 0:
            #     if self.redo_count < 1:
            #         self.log.info('redo')
            #         self.redo_count += 1
            #         self.data.clear()
            #         return

            #     self.redo_count = 0

            result = {
                'location': {
                    'ant': p[0],
                    'freq': p[1],
                    'power': p[2],
                },
                **self.data.get_data(),
            }

            with open('data.jsonl', 'a') as f:
                f.write(json.dumps(result) + '\n')

            self.results.append(result)
            self.previous_point = self.current_point
            self.current_point += 1

            if self.current_point == len(self.points):
                self.stop()
                return

            point = self.points[self.current_point]
            prev = self.points[self.previous_point]

            self.data.clear()

            if point[0] != prev[0] or point[1] != prev[1]:
                self.radio.unkey()

            self.switch.set_antenna(point[0])
            self.radio.set_vfoA_frequency(point[1])
            self.radio.set_power_level(point[2])

            if point[0] != prev[0] or point[1] != prev[1]:
                self.radio.key()
