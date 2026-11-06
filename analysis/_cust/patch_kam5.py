# -*- coding: utf-8 -*-
d = open('kam_deck.py', encoding='utf-8').read()
a = "Last round is the forecast after the August close. Sharmica Holness falls because of Alcoa, MBJ Airports and Windalco."
assert a in d
d = d.replace(a, "Last round is the forecast after the August close, before adjustments rolled forward, so the change includes that. Sharmica Holness falls because of Alcoa and MBJ Airports.")
open('kam_deck.py', 'w', encoding='utf-8').write(d)
print('ok')
