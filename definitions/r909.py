import string
from itertools import chain

# MZ-R909/R910/N1 export firmware:
HOLD = 2.1
PRESS = 0.03
labelling_entry_stop = 2
charset_list = ['uppercase', 'lowercase', 'numbers']
set_initial = charset_list[0]
set_common = ["'", ',', '/', ':', ' ']
set_uppercase = list(string.ascii_uppercase)
set_lowercase = list(string.ascii_lowercase)
set_numbers = (list(string.digits)
               + ['!', '~', '#', '$', '%', '&', '(', ')', '*', '.', ';',
                  '<', '=', '>', '?', '@', '_', '`', '+', '-'])
set_katakana = []

complete_recipe = [set_common, set_uppercase, set_common, set_lowercase, set_common, set_numbers]
set_complete = list(chain.from_iterable(complete_recipe))

entrypoints = {'uppercase': set_complete.index('A'),
               'lowercase': set_complete.index('a'),
               'numbers': set_complete.index('0')}
