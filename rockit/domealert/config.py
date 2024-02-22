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

"""Helper function to validate and parse the json config file"""

import json
import sys
import traceback
import jsonschema

CONFIG_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'required': [
        'name', 'ip', 'port',
        'sensor_poll_rate', 'sensor_timeout', 'sensor_median_samples'
    ],
    'properties': {
        'name': {
            'type': 'string'
        },
        'ip': {
            'type': 'string'
        },
        'port': {
            'type': 'integer',
            'min': 0,
            'max': 65535
        },
        'digital_serial_port': {
            'type': 'string',
        },
        'digital_serial_baud': {
            'type': 'number',
            'min': 0
        },
        'digital_serial_timeout': {
            'type': 'number',
            'min': 0
        },
        'sensor_poll_rate': {
            'type': 'number',
            'min': 1,
            'max': 120
        },
        'sensor_timeout': {
            'type': 'number',
            'min': 1,
            'max': 120
        },
        'sensor_median_samples': {
            'type': 'number',
            'min': 0,
            'max': 120
        },
        'digital': {
            'type': 'array',
            'items': {
                'type': 'object',
                'additionalProperties': False,
                'required': ['id', 'type', 'channel'],
                'properties': {
                    'id': {
                        'type': 'string',
                    },
                    'type': {
                        'type': 'string',
                        'enum': ['temperature', 'humidity']
                    },
                    'channel': {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 3
                    },
                    'label': {
                        'type': 'string',
                    },
                    'units': {
                        'type': 'string',
                    }
                }
            }
        },
        'rj11': {
            'type': 'array',
            'items': {
                'type': 'object',
                'additionalProperties': False,
                'required': ['id', 'type', 'device', 'label'],
                'properties': {
                    'id': {
                        'type': 'string',
                    },
                    'type': {
                        'type': 'string',
                        'enum': ['t', 'tht', 'thh']
                    },
                    'device': {
                        'type': 'string'
                    },
                    'label': {
                        'type': 'string',
                    },
                    'units': {
                        'type': 'string',
                    }
                }
            }
        },
        'switches': {
            'type': 'array',
            'items': {
                'type': 'object',
                'additionalProperties': False,
                'required': ['id', 'channel', 'label'],
                'properties': {
                    'id': {
                        'type': 'string',
                    },
                    'channel': {
                        'type': 'number',
                        'min': 0,
                        'max': 7
                    },
                    'label': {
                        'type': 'string',
                    },
                    'values': {
                        'type': 'array',
                        'minItems': 2,
                        'maxItems': 2,
                        'items': {
                            'type': 'string'
                        }
                    }
                }
            }
        }
    },
    'dependencies': {
        'digital': ['digital_serial_port', 'digital_serial_baud', 'digital_serial_timeout'],
        'digital_serial_port': ['digital_serial_baud', 'digital_serial_timeout'],
        'digital_serial_baud': ['digital_serial_port', 'digital_serial_timeout'],
        'digital_serial_timeout': ['digital_serial_baud', 'digital_serial_baud']
    }
}


class ConfigSchemaViolationError(Exception):
    """Exception used to report schema violations"""
    def __init__(self, errors):
        message = 'Invalid configuration:\n\t' + '\n\t'.join(errors)
        super(ConfigSchemaViolationError, self).__init__(message)


def __create_validator():
    """Returns a template validator that includes support for the
       custom schema tags used by the observation schedules:
            daemon_name: add to string properties to require they match an entry in the
                         warwick.observatory.common.daemons address book
    """
    validators = dict(jsonschema.Draft4Validator.VALIDATORS)
    return jsonschema.validators.create(meta_schema=jsonschema.Draft4Validator.META_SCHEMA,
                                        validators=validators)


def validate_config(config_json):
    """Tests whether a json object defines a valid environment config file
       Raises SchemaViolationError on error
    """
    errors = []
    try:
        validator = __create_validator()
        for error in sorted(validator(CONFIG_SCHEMA).iter_errors(config_json),
                            key=lambda e: e.path):
            if error.path:
                path = '->'.join([str(p) for p in error.path])
                message = path + ': ' + error.message
            else:
                message = error.message
            errors.append(message)
    except Exception:
        traceback.print_exc(file=sys.stdout)
        errors = ['exception while validating']

    if errors:
        raise ConfigSchemaViolationError(errors)


class Config:
    """Daemon configuration parsed from a json file"""
    def __init__(self, config_filename):
        # Will throw on file not found or invalid json
        with open(config_filename, 'r') as config_file:
            config_json = json.load(config_file)

        # Will throw on schema violations
        validate_config(config_json)

        self.name = config_json['name']
        self.ip = config_json['ip']
        self.port = config_json['port']
        self.sensor_poll_rate = config_json['sensor_poll_rate']
        self.sensor_median_samples = config_json['sensor_median_samples']
        self.sensor_timeout = config_json['sensor_timeout']
        self.digital_serial_port = config_json.get('digital_serial_port', None)
        self.digital_serial_baud = config_json.get('digital_serial_baud', 0)
        self.digital_serial_timeout = config_json.get('digital_serial_timeout', 0)
        self.digital_sensors = config_json.get('digital', [])
        self.rj11_sensors = config_json.get('rj11', [])
        self.switch_sensors = config_json.get('switches', [])
