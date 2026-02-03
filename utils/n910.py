#!/usr/bin/python3
import sys
import time
import string
from itertools import chain
from pprint import pp
import os
os.environ["BLINKA_MCP2221"] = "1"

import logging
logging.basicConfig(level=logging.WARN)

#n910 definitions
HOLD = 2.1
PRESS = 0.050

charset_list = ['uppercase', 'lowercase', 'numbers']
set_initial = charset_list[0]
set_common = ["'", ',', '/', ':', ' ']
set_uppercase = list(string.ascii_uppercase)
set_lowercase = list(string.ascii_lowercase)
set_numbers = (list(string.digits)
               + ['!', '~', '#', '$', '%', '&', '(', ')', '*', '.', ';',
                  '<', '=', '>', '?', '@', '_', '`', '+', '-'])

complete_recipe = [set_common, set_uppercase, set_common, set_lowercase, set_common, set_numbers]
set_complete = list(chain.from_iterable(complete_recipe))

entrypoints = {'uppercase': set_complete.index('A'),
               'lowercase': set_complete.index('a'),
               'numbers': set_complete.index('0')}

def return_current_set(letter, current_set):
    # find out where we ended up, this carries over to the next letter
    return 'uppercase' if letter in set_uppercase else \
           'lowercase' if letter in set_lowercase else \
           'numbers' if letter in set_numbers else \
           current_set

def enter_correct_set(wanted_set, current_set):
    # get from the current set to where we want to begin entry
    d = charset_list.index(wanted_set) - charset_list.index(current_set)
    times = d if d >= 0 else d + len(charset_list)
    push_button('Playmode', PRESS, times + 1) # is it?


def input_string(trackname):
    # string should be already sanitized!
    current_set = set_initial
    for letter in list(trackname):
        if letter not in set_complete:
            letter = '?'
        wanted_set, times_to_press = find_distance(letter)
        enter_correct_set(wanted_set, current_set)
        # use the sign on the modulo result to see if we are going left or right
        push_button((lambda x: (x < 0 and 'VolDown' or 'VolUp'))(times_to_press), PRESS, abs(times_to_press))
        push_button('Ent', PRESS, 1)  # advance to next letter
        current_set = return_current_set(letter, current_set)


def find_distance(letter):
    # find the shortest distance from the first letter of every charset to our letter
    # positive value is going right, negative is going left
    dist_dict = {}
    for entry in entrypoints:
        search_right = (set_complete.index(letter) - entrypoints[entry]) % len(set_complete)
        search_left = (set_complete.index(letter) - entrypoints[entry]) % -len(set_complete)
        dist_dict[entry] = min(search_right, search_left, key=abs)  # compare absolute, return signed
    # and the winner is
    dict_key = min(dist_dict, key=lambda k: abs(dist_dict[k]))
    return dict_key, dist_dict[dict_key]


def read_mcp_eeprom(address):
    result = bytearray(2)
    pot.write_then_readinto(bytes([(address & 15) << 4 | 12]), result)
    return int.from_bytes(result, 'big')


def read_status():
    # 0b111110000 = dec 496 = hex 0x01, 0xf0
    result = bytearray(2)
    pot.write_then_readinto(bytes([(5 & 15) << 4 | 12]), result)
    return True if result == bytearray([0x01, 0xf0]) else False


def shutdown_pot():
    pot.write(bytes([0x40 & 0xff, 0xf9 & 0xff]))


def write_pot(value):
    pot.write(bytes([0x00 & 0xff, value & 0xff]))
    pot.write(bytes([0x40 & 0xff, 0xff]))  # resume from shutdown


def push_button(button, timing, times, shutdown=True):
    for _ in range(times):
        write_pot(wipers[button])
        time.sleep(timing)
        if shutdown:
            shutdown_pot()
            time.sleep(timing)


def cleanup_exit():
    shutdown_pot()
    digitalio.DigitalInOut(board.G2).direction = digitalio.Direction.INPUT
    sys.exit(0)

try:
    import board
    import busio
    import digitalio
    from adafruit_blinka.microcontroller.mcp2221 import mcp2221
    from adafruit_bus_device.i2c_device import I2CDevice
    i2c = busio.I2C(board.SCL, board.SDA)
    pot = I2CDevice(i2c, 0x2C)
    mcp2221.mcp2221.gp_set_mode(3, 0b001)  # GP3 LED_I2C
    # assume that we need to apply pull-down on data line
    datapin = digitalio.DigitalInOut(board.G2)
    datapin.direction = digitalio.Direction.OUTPUT
    datapin.value = False
    logging.info('Hardware init done')
except RuntimeError:
    logging.warning('Hardware init failed')
    sys.exit(1)

logging.info(f'Digital pot detected: {read_status()}')

values = [read_mcp_eeprom(address) for address in range(6, 16)]
logging.info(f'Digital pot EEPROM contents: {values}')

wiper_list = ['Play', 'Left', 'Right', 'Pause', 'Stop', 'VolUp', 'TMark', 'Playmode', 'Display', 'Record']
wipers = dict(zip(wiper_list, values))

# value of 1 should give us approx 330 Ohm for the Ent button
wipers['Ent'] = 1
# value of 44 should give us approx 8400 Ohm for VolDown
wipers['VolDown'] = 44

try:
    string = input('Type input string and press Return key \n')
    assert set(string) <= set(set_complete)

    # enter labeling
    push_button('Display', HOLD, 1)
    time.sleep(0.1)
    push_button('Ent', PRESS, 3)

    # input string
    input_string(string)

    # exit labeling
    push_button('Ent', HOLD, 1)

    input(f'Track name should now read: {string}. Press Return key to exit.')
except AssertionError:
    print('String contains characters not present in the supported set:')
    pp(set_complete, width=80, compact=True)
    input('Press Return to exit.')
finally:
    cleanup_exit()
