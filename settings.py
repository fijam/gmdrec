# Settings. Tread lightly.
import string
from itertools import chain

OFFSET = 0.01  # in seconds
PRESS = 0.03
HOLD = 2.1

server_url = 'http://127.0.0.1:8880'

wipers = {
    'Play': 254,  # 200
    'Left': 250,  # 1000
    'Right': 237,  # 3650
    'Pause': 229,  # 5160
    'Stop': 218,  # 7100
    'TMark': 193,  # 11900
    'Display': 166,  # 16700
    'Record': 152  # 19500
}

# Recorder-specific definitions.

# MZ-R90/R91:
change_set_moves = {'uppercase': {'uppercase': 1, 'lowercase': 2, 'numbers': 3},
                    'lowercase': {'uppercase': 3, 'lowercase': 1, 'numbers': 2},
                    'numbers':   {'uppercase': 2, 'lowercase': 3, 'numbers': 1}}
set_initial = 'uppercase' 
set_common = ["'", ',', '/', ':', ' ']
set_uppercase = list(string.ascii_uppercase)
set_lowercase = list(string.ascii_lowercase)
set_numbers = (list(string.digits)
               + ['!', '"', '#', '$', '%', '&', '(', ')', '*', '.', ';',
                  '<', '=', '>', '?', '@', '_', '`', '+', '-'])

complete_recipe = [set_common, set_uppercase, set_common, set_lowercase, set_common, set_numbers]
set_complete = list(chain.from_iterable(complete_recipe))

entrypoints = {'uppercase': set_complete.index('A'),
               'lowercase': set_complete.index('a'),
               'numbers': set_complete.index('0')}


'''
# MZ-R90/R91 Japanese firmware:
change_set_moves = {'katakana':  {'katakana': 1, 'uppercase': 2, 'lowercase': 3, 'numbers': 4},
                    'uppercase': {'katakana': 4, 'uppercase': 1, 'lowercase': 2, 'numbers': 3},
                    'lowercase': {'katakana': 3, 'uppercase': 4, 'lowercase': 1, 'numbers': 2},
                    'numbers':   {'katakana': 2, 'uppercase': 3, 'lowercase': 4, 'numbers': 1}
                    }
set_initial = 'katakana'
set_common = ["'", ',', '/', ':', ' ']
set_uppercase = list(string.ascii_uppercase)
set_lowercase = list(string.ascii_lowercase)
set_numbers = (list(string.digits)
               + ['!', '"', '#', '$', '%', '&', '(', ')', '*', '.', ';',
                  '<', '=', '>', '?', '@', '_', '`', '+', '-'])
set_katakana = ['ア'] * 81  # todo, 81 characters

complete_recipe = [set_common, set_katakana, set_common, set_uppercase, set_common, set_lowercase, set_common, set_numbers]
set_complete = list(chain.from_iterable(complete_recipe))

entrypoints = {'katakana': set_complete.index('ア'),
               'uppercase': set_complete.index('A'),
               'lowercase': set_complete.index('a'),
               'numbers': set_complete.index('0')}
'''