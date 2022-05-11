"""Finding out which button to push and how many times. Sanitizing input.

Recorder-specific settings are loaded from the corresponding definition file.
"""
import time

from unihandecode import Unihandecoder
from hardware import push_button
from settings import recorder

if recorder == 'R55/R37':
    from definitions.r55 import *
if recorder == 'R55/R37 JPN':
    from definitions.r55_jpn import *
if recorder == 'R70 through N707':
    from definitions.r90 import *
if recorder == 'R70 through N707 JPN':
    from definitions.r90_jpn import *
if recorder == 'R909/R910/N1':
    from definitions.r909 import *
if recorder == 'R909/R910/N1 JPN':
    from definitions.r909_jpn import *


def return_current_set(letter, current_set):
    # find out where we ended up, this carries over to the next letter
    return 'katakana' if letter in set_katakana else \
           'uppercase' if letter in set_uppercase else \
           'lowercase' if letter in set_lowercase else \
           'numbers' if letter in set_numbers else \
           set_initial if recorder in ['R55/R37', 'R55/R37 JPN'] else \
           current_set


def enter_correct_set(wanted_set, current_set):
    # get from the current set to where we want to begin entry
    d = charset_list.index(wanted_set) - charset_list.index(current_set)
    times = d if d >= 0 else d + len(charset_list)
    push_button('Pause', PRESS, times + 1)


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


def letter_replace(trackname):
    change_from = "[{「『]}」』|。・、"
    change_to = "(((())))I.-,"
    return trackname.translate(trackname.maketrans(change_from, change_to))


def sanitize_track(trackname, lang_code=None):
    trackname = letter_replace(trackname)
    if set(trackname) <= set(set_complete):
        return trackname
    if lang_code:
        return Unihandecoder(lang=lang_code.casefold()).decode(trackname)
    else:
        return Unihandecoder().decode(trackname)


def sanitize_tracklist(tracklist, lang_code=None):
    sanitized_tracklist = [sanitize_track(track, lang_code) for track in tracklist]
    return sanitized_tracklist


def input_string(trackname):
    # string should be already sanitized!
    track_letterlist = list(trackname)
    current_set = set_initial
    for letter in track_letterlist:
        wanted_set, times_to_press = find_distance(letter)
        enter_correct_set(wanted_set, current_set)
        # use the sign on the modulo result to see if we are going left or right
        push_button((lambda x: (x < 0 and 'Left' or 'Right'))(times_to_press), PRESS, abs(times_to_press))
        push_button('Stop', PRESS, 1)  # advance to next letter
        current_set = return_current_set(letter, current_set)
    push_button('Stop', HOLD, 1)  # finish entry


def enter_rec_stby():  # don't shut down pot to simulate 'hold and press'
    push_button('Pause', HOLD, 1, False)
    push_button('Record', PRESS, 1)
    time.sleep(6)


def next_track():
    push_button('Right', PRESS, 1)


def pause_unpause():
    push_button('Pause', PRESS, 1)


def write_toc():
    print('Writing TOC...')
    push_button('Stop', PRESS, 1)
    time.sleep(12)


def tmark_it():
    push_button('TMark', PRESS, 1)


def erase():
    push_button('Playmode', PRESS, 128)


def enter_labelling():
    # 100 ms delays here are *required*
    time.sleep(0.1)
    push_button('Display', HOLD, 1)
    time.sleep(0.1)
    push_button('Stop', PRESS, labelling_entry_stop)
    time.sleep(0.1)
