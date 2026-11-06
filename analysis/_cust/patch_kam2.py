# -*- coding: utf-8 -*-
m = open('kam_model.py', encoding='utf-8').read()
a = "FLAG_LIST = sorted(FLAG_CUST.values(), key=lambda c: c['dl'][1])"
assert a in m
m = m.replace(a, "FLAG_LIST = sorted([c for c in FLAG_CUST.values() if abs(c['dl'][1]) + abs(c['dl'][2]) >= 0.05], key=lambda c: c['dl'][1])")
open('kam_model.py', 'w', encoding='utf-8').write(m)

d = open('kam_deck.py', encoding='utf-8').read()
def rep(a, b):
    global d
    assert a in d, a[:70]
    d = d.replace(a, b, 1)
rep("""         ('NO VALUE ENTERED', str(n_noeff), 'Entries with 0% and 0 kWh change nothing. 9 are marked Confirmed defection.'),
         ('NO KAM ON THE ACCOUNT', str(n_nokam), 'Adjustments on accounts with no KAM have no effect on the forecast.')]""",
    """         ('ENTRIES WITH NO VALUE', str(n_zero_entries), f'On {len(zero_accts)} accounts every entry is 0% and 0 kWh, so nothing changes. Three are possible defections on accounts with no KAM.'),
         ('EFFECT ON FY2027', sg(eff27, 0) + ' GWh', 'Across the assigned accounts, against the forecast with no adjustments.')]""")
rep("n_noeff = sum(1 for a in adj if a['pct'] == 0 and a['kwh'] == 0)",
    "_by = collections.defaultdict(list)\nfor a in adj: _by[a['ac']].append(a)\nzero_accts = [ac for ac, l in _by.items() if all(x['pct'] == 0 and x['kwh'] == 0 for x in l)]\nn_zero_entries = sum(len(_by[ac]) for ac in zero_accts)")
open('kam_deck.py', 'w', encoding='utf-8').write(d)
print('patched')
