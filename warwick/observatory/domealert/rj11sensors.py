#
# This file is part of domealertd
#
# domealertd is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# domealertd is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with domealertd.  If not, see <http://www.gnu.org/licenses/>.

import datetime
from glob import glob
import os.path
import sys
import threading
import time
import traceback


class SensorWatcher:
    def __init__(self, config, poll_rate, age_timeout):
        self._id = config['id']
        self._value = 0
        self._age_timeout = age_timeout
        self._updated = datetime.datetime.min
        self._poll_rate = poll_rate
        self._lock = threading.Lock()
        self._type = config['type']
        self._device_path = os.path.join('/sys/bus/w1/devices', config['device'])
        self._available = False

        loop = threading.Thread(target=self.__poll_sensor)
        loop.daemon = True
        loop.start()

    def __poll_sensor(self):
        while True:
            updated = False
            value = 0
            try:
                if not os.path.exists(self._device_path):
                    continue

                if self._type == 't':
                    # hwmon index is not fixed
                    paths = glob(os.path.join(self._device_path, 'hwmon/hwmon*/temp*_input'))
                    if not paths:
                        continue

                    with open(paths[0], 'r') as f_file:
                        value = int(f_file.read()) / 1000.
                        updated = True

                else:
                    temperature_path = os.path.join(self._device_path, 'temperature')

                    with open(temperature_path, 'r') as f_file:
                        temperature_raw = int(f_file.read())
                        temperature = (temperature_raw >> 3) * 0.03125

                    if self._type == 'thh':
                        vad_path = os.path.join(self._device_path, 'vad')
                        vdd_path = os.path.join(self._device_path, 'vdd')
                        if not os.path.exists(vad_path) or not os.path.exists(vdd_path):
                            continue

                        with open(vad_path, 'r') as f_file:
                            vad = float(f_file.read())

                        with open(vdd_path, 'r') as f_file:
                            vdd = float(f_file.read())

                        sensor_rh = (vad / vdd - 0.16) / 0.0062
                        value = sensor_rh / (1.0546 - 0.00216 * temperature)
                        updated = True
                    else:
                        value = temperature
                        updated = True

                if updated:
                    with self._lock:
                        self._value = value
                        self._updated = datetime.datetime.utcnow()

            except Exception:
                if self._available:
                    print('Exception while polling {}'.format(self._id))
                    traceback.print_exc(file=sys.stdout)

            finally:
                if updated != self._available:
                    if updated:
                        print('Sensor ' + self._id + ' connected')
                    else:
                        print('Sensor ' + self._id + ' disconnected')

                self._available = updated
                time.sleep(self._poll_rate)

    def export_measurement(self, data):
        with self._lock:
            data[self._id] = round(self._value, 2)
            data[self._id + '_valid'] = (datetime.datetime.utcnow() - self._updated).total_seconds() < 2.5


class RJ11SensorsWatcher:
    def __init__(self, sensor_config, poll_rate=1, age_timeout=2.5):
        self._sensors = [SensorWatcher(s, poll_rate, age_timeout) for s in sensor_config]

    def export_measurements(self, data):
        for s in self._sensors:
            s.export_measurement(data)
