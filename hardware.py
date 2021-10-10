# Finding out how many times to push a button and how.
import os
import sys
import time

# help Blinka find our microcontroller
os.environ["BLINKA_MCP2221"] = "1"

try:
    import board
    import busio
except RuntimeError:
    print("Titler not conneted to USB")
    sys.exit()
from settings import *


def return_current_set(letter, current_set):
    # find out where we ended up, this carries over to the next letter
    if letter in set_uppercase:
        return 'uppercase'
    if letter in set_lowercase:
        return 'lowercase'
    if letter in set_numbers:
        return 'numbers'
    return current_set


def enter_correct_set(wanted_set, current_set):
    # get from the current set to where we want to begin entry
    times = change_set_moves[current_set][wanted_set]
    push_button('Pause', PRESS, times)


def find_distance(letter):
    # find shortest distance from the first letter of every charset to our letter
    # positive value is going right, negative is going left
    dist_dict = {}
    for entry in entrypoints:
        search_right = (set_complete.index(letter) - entrypoints[entry]) % len(set_complete)
        search_left = (set_complete.index(letter) - entrypoints[entry]) % -len(set_complete)
        dist_dict[entry] = min(search_right, search_left, key=abs)  # compare absolute, return signed
    # and the winner is
    dict_key = min(dist_dict, key=lambda k: abs(dist_dict[k]))
    return dict_key, dist_dict[dict_key]


def input_string(string_ascii):
    track_letterlist = list(string_ascii)
    current_set = set_initial
    for letter in track_letterlist:
        if letter not in set_complete:
            letter = '?'
        wanted_set, times_to_press = find_distance(letter)
        enter_correct_set(wanted_set, current_set)
        # use the sign on the modulo result to see if we are going left or right
        push_button((lambda x: (x < 0 and 'Left' or 'Right'))(times_to_press), PRESS, abs(times_to_press))
        push_button('Stop', PRESS, 1)  # advance to next letter
        current_set = return_current_set(letter, current_set)
    push_button('Stop', HOLD, 1)  # finish entry


def hardware_setup():
    # from adafruit_blinka.microcontroller.mcp2221 import mcp2221
    # mcp2221.mcp2221.gp_set_mode(3, 0b001)  # turn LED_I2C on
    from adafruit_bus_device.i2c_device import I2CDevice
    i2c = busio.I2C(board.SCL, board.SDA)
    pot = I2CDevice(i2c, 0x2C)
    return pot


def write_to_pot(value, pot):
    pot.write(bytes([0x00 & 0xff, value & 0xff]))


def shutdown_pot(pot):
    pot.write(bytes([0x20 & 0xff, 0 & 0xff]))


def push_button(button, timing, times):
    for _ in range(times):
        write_to_pot(wipers[button], ad5245)
        time.sleep(timing)
        shutdown_pot(ad5245)
        time.sleep(timing)


def cleanup_exit():
    shutdown_pot(ad5245)
    print('Bye!')
    sys.exit()


def enter_labelling():
    time.sleep(0.1)
    push_button('Display', HOLD, 1)
    time.sleep(0.1)
    push_button('Stop', PRESS, 2)


# initialize hardware as soon as possible
ad5245 = hardware_setup()
shutdown_pot(ad5245)
