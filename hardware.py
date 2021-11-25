# Finding out how many times to push a button and how.
import sys
import time

from digipot import *
from settings import PRESS, HOLD, wipers, recorder

if recorder == 'R55 through R900':
    from definitions.r90 import change_set_moves, set_initial, set_uppercase, \
        set_lowercase, set_numbers, set_complete, entrypoints
if recorder in ['R55 through R900 JPN', 'R55 through R900 JPN early FW']:
    from definitions.r90_jpn import change_set_moves, set_initial, set_uppercase, \
        set_lowercase, set_numbers, set_complete, entrypoints
if recorder == 'R909/R910/N1':
    from definitions.r909 import change_set_moves, set_initial, set_uppercase, \
        set_lowercase, set_numbers, set_complete, entrypoints
if recorder == 'R909/R910/N1 JPN':
    from definitions.r909_jpn import change_set_moves, set_initial, set_uppercase, \
        set_lowercase, set_numbers, set_complete, entrypoints


def return_current_set(letter, current_set):
    # find out where we ended up, this carries over to the next letter
    if letter in set_uppercase:
        return 'uppercase'
    if letter in set_lowercase:
        return 'lowercase'
    if letter in set_numbers:
        return 'numbers'
    if recorder == 'R55 through R900 JPN early FW' and letter != ' ':
        return 'katakana'
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


def letter_replace(letter):
    if letter in ['[', '{']:
        replacement = '('
    elif letter in [']', '}']:
        replacement = ')'
    elif letter == '|':
        replacement = 'I'
    elif letter == '\\':
        replacement = '/'
    elif letter not in set_complete:
        replacement = '?'
    else:
        replacement = letter
    return replacement


def input_string(string_ascii):
    track_letterlist = list(string_ascii)
    current_set = set_initial
    for letter in track_letterlist:
        letter = letter_replace(letter)
        wanted_set, times_to_press = find_distance(letter)
        enter_correct_set(wanted_set, current_set)
        # use the sign on the modulo result to see if we are going left or right
        push_button((lambda x: (x < 0 and 'Left' or 'Right'))(times_to_press), PRESS, abs(times_to_press))
        push_button('Stop', PRESS, 1)  # advance to next letter
        current_set = return_current_set(letter, current_set)
    push_button('Stop', HOLD, 1)  # finish entry


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


def enter_rec_stby():  # don't shut down pot to simulate 'hold and press'
    write_to_pot(wipers['Pause'], ad5245)
    time.sleep(HOLD)
    write_to_pot(wipers['Record'], ad5245)
    time.sleep(PRESS)
    shutdown_pot(ad5245)


def enter_labelling():
    time.sleep(0.1)
    push_button('Display', HOLD, 1)
    time.sleep(0.1)
    push_button('Stop', PRESS, 2)


ad5245 = hardware_setup()
shutdown_pot(ad5245)
