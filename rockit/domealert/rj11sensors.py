#
# This file is part of the Robotic Observatory Control Kit (rockit)
#
# rockit is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rockit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rockit.  If not, see <http://www.gnu.org/licenses/>.

from collections import deque
from datetime import datetime
from glob import glob
import os.path
from statistics import median
import sys
import threading
import time
import traceback


def read_value(f_file, retries=5):
    attempt = 0
    while True:
        try:
            return f_file.read()
        except OSError:
            if attempt == retries:
                raise
            time.sleep(0.1)


class SensorWatcher:
    def __init__(self, config, poll_rate, median_samples, age_timeout):
        self._id = config['id']
        self._age_timeout = age_timeout
        self._updated = datetime.min
        self._poll_rate = poll_rate
        self._lock = threading.Lock()
        self._type = config['type']
        self._device_path = os.path.join('/sys/bus/w1/devices', config['device'])
        self._available = False

        # Reject outliers by taking a median filter over buffer_size samples
        self._buffer = deque(maxlen=median_samples)
        self._value = 0

        loop = threading.Thread(target=self.__poll_sensor)
        loop.daemon = True
        loop.start()

    def __poll_sensor(self):
        while True:
            available = False
            updated = False
            try:
                if not os.path.exists(self._device_path):
                    continue

                if self._type == 't':
                    # hwmon index is not fixed
                    paths = glob(os.path.join(self._device_path, 'hwmon/hwmon*/temp*_input'))
                    if not paths:
                        continue

                    with open(paths[0], 'r') as f_file:
                        value = int(read_value(f_file)) / 1000.
                        available = updated = True

                else:
                    temperature_path = os.path.join(self._device_path, 'temperature')

                    with open(temperature_path, 'r') as f_file:
                        temperature_raw = int(read_value(f_file))
                        temperature = (temperature_raw >> 3) * 0.03125

                    if self._type == 'thh':
                        vad_path = os.path.join(self._device_path, 'vad')
                        vdd_path = os.path.join(self._device_path, 'vdd')
                        if not os.path.exists(vad_path) or not os.path.exists(vdd_path):
                            continue

                        with open(vad_path, 'r') as f_file:
                            vad = float(read_value(f_file))

                        with open(vdd_path, 'r') as f_file:
                            vdd = float(read_value(f_file))

                        sensor_rh = (vad / vdd - 0.16) / 0.0062
                        value = sensor_rh / (1.0546 - 0.00216 * temperature)

                        # A race condition between temperature, vad, vdd can produce a calculated humidity > 100%
                        # Skip these bad readings
                        available = True
                        updated = value <= 100
                    else:
                        value = temperature
                        available = updated = True

                if updated:
                    with self._lock:
                        self._buffer.append(value)
                        self._value = median(self._buffer)
                        self._updated = datetime.utcnow()

            except Exception:
                if self._available:
                    print('Exception while polling {}'.format(self._id))
                    traceback.print_exc(file=sys.stdout)

            finally:
                if available != self._available:
                    if available:
                        print('Sensor ' + self._id + ' connected')
                    else:
                        print('Sensor ' + self._id + ' disconnected')

                self._available = available
                time.sleep(self._poll_rate)

    def export_measurement(self, data):
        with self._lock:
            data[self._id] = round(self._value, 2)
            data[self._id + '_valid'] = (datetime.utcnow() - self._updated).total_seconds() < self._age_timeout


class RJ11SensorsWatcher:
    def __init__(self, sensor_config, poll_rate, median_samples, age_timeout):
        self._sensors = [SensorWatcher(s, poll_rate, median_samples, age_timeout) for s in sensor_config]

    def export_measurements(self, data):
        for s in self._sensors:
            s.export_measurement(data)
