import string
from itertools import chain

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
set_katakana = ['ア', 'イ', 'ウ', 'エ', 'オ', 'カ', 'キ', 'ク', 'ケ', 'コ', 'サ', 'シ', 'ス', 'セ', 'ソ', 'タ', 'チ', 'ツ', 'テ', 'ト', 'ナ', 'ニ',
                'ヌ', 'ネ', 'ノ', 'ハ', 'ヒ', 'フ', 'ヘ', 'ホ', 'マ', 'ミ', 'ム', 'メ', 'モ', 'ヤ', 'ユ', 'ヨ', 'ラ', 'リ', 'ル', 'レ', 'ロ', 'ワ',
                'ヲ', 'ン', 'ァ', 'ィ', 'ゥ', 'ェ', 'ォ', 'ャ', 'ュ', 'ョ', 'ッ', 'ガ', 'ギ', 'グ', 'ゲ', 'ゴ', 'ザ', 'ジ', 'ズ', 'ゼ', 'ゾ', 'ダ',
                'ヂ', 'ヅ', 'デ', 'ド', 'バ', 'ビ', 'ブ', 'ベ', 'ボ', 'パ', 'ピ', 'プ', 'ペ', 'ポ', 'ヴ']

complete_recipe = [set_common, set_katakana, set_common, set_uppercase, set_common, set_lowercase, set_common, set_numbers]
set_complete = list(chain.from_iterable(complete_recipe))

entrypoints = {'katakana': set_complete.index('ア'),
               'uppercase': set_complete.index('A'),
               'lowercase': set_complete.index('a'),
               'numbers': set_complete.index('0')}
