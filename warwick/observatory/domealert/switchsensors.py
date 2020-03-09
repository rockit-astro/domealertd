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
import sys
import threading
import time
import traceback
import RPi.GPIO as GPIO

# Pin assigment for channels 0-7
# TODO Change to .BOARD
CHANNEL_PIN_TYPE = GPIO.BCM
CHANNEL_PINS = [0, 5, 6, 13, 19, 2, 21, 26]
RELAY_PIN = 23


class SwitchSensorsWatcher:
    def __init__(self, config, poll_rate=1, age_timeout=2.5):
        self._config = config
        self._updated = datetime.datetime.min
        self._channels = [False for _ in CHANNEL_PINS]
        self._lock = threading.Lock()
        self._poll_rate = poll_rate
        self._age_timeout = age_timeout
        self._available = False

        GPIO.setwarnings(False)
        GPIO.setmode(CHANNEL_PIN_TYPE)
        GPIO.setup(CHANNEL_PINS, GPIO.IN)
        GPIO.setup(RELAY_PIN, GPIO.OUT)

        loop = threading.Thread(target=self.__poll_inputs)
        loop.daemon = True
        loop.start()

    def set_relay(self, enabled):
        GPIO.output(RELAY_PIN, enabled)

    def __poll_inputs(self):
        while True:
            updated = False
            try:
                with self._lock:
                    for i, pin in enumerate(CHANNEL_PINS):
                        self._channels[i] = GPIO.input(pin) == GPIO.LOW

                    self._updated = datetime.datetime.utcnow()
                    updated = True
            except Exception:
                if self._available:
                    print('Exception while polling switches')
                    traceback.print_exc(file=sys.stdout)
            finally:
                if updated != self._available:
                    if updated:
                        print('Switches connected')
                    else:
                        print('Switches disconnected')

                self._available = updated
                time.sleep(self._poll_rate)

    def export_measurements(self, data):
        with self._lock:
            switch_valid = (datetime.datetime.utcnow() - self._updated).total_seconds() < self._age_timeout
            for s in self._config:
                data[s['id']] = self._channels[s['channel']]
                data[s['id'] + '_valid'] = switch_valid
