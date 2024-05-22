from qtstrap import *
from codex import DeviceManager
from collections import deque
from dataclasses import dataclass
from itertools import product
import numpy as np
import json
import logging


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

    # def is_ready(self):
    #     for _, queue in self._data.items():
    #         if len(queue) != queue.maxlen:
    #             return False
    #     return True

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
            'm_fwd',
            'm_rev',
            'm_swr',
            'm_freq',
            'm_temp',
            't_v_mag',
            't_c_mag',
            't_phase',
            't_sign',
            't_freq',
            't_v_mag_volts',
            't_c_mag_volts',
            't_phase_deg',
            't_phase_rad',
            't_mod_z',
            't_power',
            't_swr',
        ]
        self.data = DataQueue(fields, stabilize={'m_fwd': 0.01}, maxlen=3)

    def rf_received(self, rf_data):
        self.data['t_freq'].append(int(rf_data.get('freq', 0)))

        self.data['t_v_mag'].append(float(rf_data.get('vMag', 0.0)))
        self.data['t_c_mag'].append(float(rf_data.get('cMag', 0.0)))
        self.data['t_phase'].append(float(rf_data.get('phase', 0.0)))
        self.data['t_sign'].append(int(rf_data.get('sign', 0)))

        self.data['t_v_mag_volts'].append(float(rf_data.get('vMagVolts', 0.0)))
        self.data['t_c_mag_volts'].append(float(rf_data.get('cMagVolts', 0.0)))

        self.data['t_phase_deg'].append(float(rf_data.get('pDeg', 0.0)))
        self.data['t_phase_rad'].append(float(rf_data.get('pRad', 0.0)))
        self.data['t_mod_z'].append(float(rf_data.get('modZ', 0.0)))
        self.data['t_power'].append(float(rf_data.get('pow', 0.0)))
        self.data['t_swr'].append(int(rf_data.get('swr', 0)))

    def device_added(self, device):
        if device.profile_name == 'DTS-6':
            self.switch = device
        if device.profile_name == 'TS-480':
            self.radio = device
        if device.profile_name == 'Alpha4510A':
            self.meter = device
            signals = device.signals
            signals.forward.connect(lambda x: self.data['m_fwd'].append(float(x)))
            signals.reverse.connect(lambda x: self.data['m_rev'].append(float(x)))
            signals.swr.connect(lambda x: self.data['m_swr'].append(float(x)))
            signals.frequency.connect(lambda x: self.data['m_freq'].append(float(x)))
            signals.temperature.connect(lambda x: self.data['m_temp'].append(float(x)))
        if device.profile_name == 'PhaseTuner':
            self.target = device
            signals = device.signals
            signals.rf_received.connect(self.rf_received)
            signals.frequency.connect(lambda x: self.data['t_freq'].append(float(x)))
            signals.handshake_received.connect(lambda s: self.target_description_ready())

    @Slot()
    def start(self):
        if self.switch is None or self.meter is None or self.radio is None or self.target is None:
            self.log.info("can't start test, device missing")
            return

        self.points = list(product([0, 1], range(1 << 5), range(1 << 5)))
        # self.points = list(product([0], range(1 << 4), range(1 << 4)))
        self.results = []
        self.data.clear()
        self.log.info(f'starting test, collecting {len(self.points)} samples')

        # clear output file
        with open('data.jsonl', 'w') as f:
            f.write('')

        self.current_point = 0

        self.started.emit(len(self.points))

        self.target.handshake()
        # self.switch.set_antenna(2)
        self.target.set_relays(*self.points[self.current_point])
        # self.radio.set_vfoA_frequency(int(self.points[self.current_point].freq))
        # self.radio.set_power_level(50)
        self.radio.key()

        self.timer.start(50)

    def target_description_ready(self):
        self.target_description = self.target.description

    @Slot()
    def stop(self):
        self.log.info('stop')
        self.timer.stop()

        if self.radio:
            self.radio.unkey()

        self.stopped.emit()

        results = {
            'device': self.target_description,
            'data': self.results,
        }

        with open('data.json', 'w') as f:
            json.dump(results, f)

        self.finished.emit(results)

    def update(self):
        self.updated.emit(self.current_point)

        if self.data.is_ready():
            p = self.points[self.current_point]
            result = {
                'relays': {
                    'caps': p[1],
                    'inds': p[2],
                    'z': p[0],
                },
                **self.data.get_data(),
            }

            self.log.info(f'data ready: {result}')
            with open('data.jsonl', 'a') as f:
                f.write(json.dumps(result) + '\n')

            self.results.append(result)
            self.current_point += 1

            if self.current_point == len(self.points):
                self.stop()
                return

            p = self.points[self.current_point]
            self.target.set_relays(
                p[1],
                p[2],
                p[0],
            )

            self.data.clear()
