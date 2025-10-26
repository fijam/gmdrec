""" Loading user settings."""
import yaml
import logging
from os import path

settings_path = path.abspath(path.join(path.dirname(__file__), 'settings.conf'))

try:
    with open(settings_path) as config_file:
        settings = yaml.safe_load(config_file)
except (FileNotFoundError, IOError):
    logging.warning('settings.conf file not found')

recorder = ''

wipers = settings['calibration']
