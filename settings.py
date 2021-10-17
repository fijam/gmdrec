# User settings
import yaml

try:
    with open('settings.conf') as config_file:
        settings = yaml.safe_load(config_file)
except (FileNotFoundError, IOError):
    print('settings.conf file not found')

PRESS = settings['PRESS']
HOLD = settings['HOLD']
OFFSET = settings['OFFSET']

recorder = ''
server_url = settings['server_url']
wipers = settings['calibration']
