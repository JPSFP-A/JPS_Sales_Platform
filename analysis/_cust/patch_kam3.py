# -*- coding: utf-8 -*-
d = open('kam_deck.py', encoding='utf-8').read()
i = d.index('# ================= 1 cover =================')
j = d.index('# ================= 2 asks =================')
d = d[:i] + d[j:]
a = "tb(s, 186473, 6413496, 287140, 265842, str(page[0] + 1), 9, True, NAVY)"
assert a in d
d = d.replace(a, "tb(s, 186473, 6413496, 287140, 265842, str(page[0]), 9, True, NAVY)")
d = d.replace("OUT = r'C:\\Projects\\Sales_Platform\\JPS_KAM_Forecast_Round_Oct2026.pptx'", "OUT = r'C:\\Projects\\Sales_Platform\\JPS_KAM_Forecast_Round_Oct2026_v2.pptx'")
open('kam_deck.py', 'w', encoding='utf-8').write(d)
print('patched', 'v2.pptx' in d)
