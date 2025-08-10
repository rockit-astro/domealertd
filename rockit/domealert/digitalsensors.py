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

import datetime
from collections import deque
import re
from statistics import median
import sys
import threading
import time
import traceback
import serial

SENSOR_REGEX = [
    r'(?P<channel>[0123]):TH;(?P<temperature>\d+\.\d+);(?P<humidity>\d+\.\d+)\r\n',
    r'(?P<channel>[0123]):T;(?P<temperature>\d+\.\d+)\r\n',
]


class DigitalSensorsWatcher:
    def __init__(self, config):
        self._config = config
        self._sensor_regex = [re.compile(r) for r in SENSOR_REGEX]
        self._data = [{} for _ in range(4)]
        self._updated = [{} for _ in range(4)]
        for sensor in config.digital_sensors:
            queue = deque(maxlen=config.sensor_median_samples)
            self._data[sensor['channel']][sensor['type']] = queue
            self._updated[sensor['channel']][sensor['type']] = datetime.datetime.min

        if self._config.digital_serial_port:
            threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        """Main run loop"""
        port_error = False
        while True:
            # Initial setup
            try:
                port = serial.Serial(self._config.digital_serial_port, self._config.digital_serial_baud,
                                     timeout=self._config.digital_serial_timeout)
                print('Connected to', self._config.digital_serial_port)

                port_error = False
            except Exception as exception:
                if not port_error:
                    print(exception)
                    print('Will retry in 10 seconds...')

                port_error = True
                time.sleep(10.)
                continue

            try:
                # First line may have been only partially received
                port.readline()

                # Main run loop
                while True:
                    data = port.readline().decode('ascii')
                    for r in self._sensor_regex:
                        match = r.match(data)
                        if match:
                            fields = match.groupdict()
                            channel = int(fields['channel'])
                            for f in fields:
                                if f == 'channel' or f not in self._data[channel]:
                                    continue

                                self._data[channel][f].append(float(fields[f]))
                                self._updated[channel][f] = datetime.datetime.now(datetime.timezone.utc)

            except Exception:
                port.close()
                if not port_error:
                    traceback.print_exc(file=sys.stdout)

                    print('Will retry in 10 seconds...')
                port_error = True
                time.sleep(10.)

    def export_measurements(self, data):
        for sensor in self._config.digital_sensors:
            try:
                value = median(self._data[sensor['channel']][sensor['type']])
                updated = self._updated[sensor['channel']][sensor['type']]
                valid = (datetime.datetime.now(datetime.timezone.utc) - updated).total_seconds() < self._config.sensor_timeout
            except:
                value = 0
                valid = False

            data[sensor['id']] = round(value, 2)
            data[sensor['id'] + '_valid'] = valid
