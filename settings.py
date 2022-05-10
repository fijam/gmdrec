""" Loading user settings."""
import yaml
import logging

try:
    with open('settings.conf') as config_file:
        settings = yaml.safe_load(config_file)
except (FileNotFoundError, IOError):
    logging.warning('settings.conf file not found')

recorder = ''

wipers = settings['calibration']
