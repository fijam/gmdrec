import string
from itertools import chain

# MZ-R70/R90/R91 export firmware:
HOLD: 2.1
PRESS: 0.03
labelling_entry_stop = 2
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
set_katakana = []

complete_recipe = [set_common, set_uppercase, set_common, set_lowercase, set_common, set_numbers]
set_complete = list(chain.from_iterable(complete_recipe))

entrypoints = {'uppercase': set_complete.index('A'),
               'lowercase': set_complete.index('a'),
               'numbers': set_complete.index('0')}
