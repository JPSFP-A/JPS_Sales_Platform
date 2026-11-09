# -*- coding: utf-8 -*-
# Class-level FY2027 numbers from the account-level forecast (kam_fy27_model), written where the workbook and deck builders read them.
import json, os
import numpy as np, pandas as pd
HERE = r'C:\Projects\Sales_Platform\analysis'; os.chdir(HERE)
ALL = pd.read_pickle(r'_cust\kam_fy27_accounts.pkl'); CLSJ = json.load(open(r'_cust\kam_fy27_class.json'))
A = json.load(open('_fy27_actuals.json')); LEY = json.load(open('_oct_deep.json'))['le']
CL = ['RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']; MONL = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
M27 = ['m2027%02d' % m for m in range(1, 13)]
f27 = {}
for c in CL:
    if c == 'RT10': f27[c] = list(CLSJ['rt10'])
    else:
        s = ALL[ALL.rc == c]; v = [s[m].sum() / 1e6 for m in M27]
        if c == 'RT20': v = [a + b / 1e6 for a, b in zip(v, CLSJ['rem27'])]
        f27[c] = v
fy26 = {}
for c in CL:
    o = CLSJ['out'][c]; fy26[c] = o.get('total26', o.get('acct26', 0) + o.get('rem26', 0))
byc = {}
for c in CL:
    a26 = [A['2026-%02d' % m][c] for m in range(1, 11)]
    h1_26 = sum(a26[:6]); h1_27 = sum(f27[c][:6]); fy27 = sum(f27[c])
    byc[c] = dict(fy25=sum(A['2025-%02d' % m][c] for m in range(1, 13)), fy26=fy26[c], fy27=fy27, h1=h1_27 - h1_26, h2=(fy27 - h1_27) - (fy26[c] - h1_26))
held = {c: sum(LEY[c]['%s 27' % m] for m in MONL) for c in CL}; le26 = {c: sum(LEY[c]['%s 26' % m] for m in MONL) for c in CL}
hot = ALL.hotel_up27.sum() / 1e6
new_ = ALL.index.astype(str).str.startswith('NEW'); pipe = ALL[new_].fy27.sum() / 1e6; adj = (ALL[~new_].fy27 - ALL[~new_].base27 - ALL[~new_].hotel_up27).sum() / 1e6; base = ALL[~new_].base27.sum() / 1e6
json.dump(byc, open('_fy27_byclass.json', 'w'))
json.dump({'f27': f27, 'fy26': fy26, 'held': held, 'le': le26, 'hotel': hot, 'pipe': pipe, 'adj': adj, 'base': base}, open('_fy27_result.json', 'w'))
tot = sum(byc[c]['fy27'] for c in CL); print('FY27 total %.1f | FY26 outlook %.1f | held %.1f' % (tot, sum(fy26.values()), sum(held.values())))
for c in CL: print('%-8s FY25 %7.1f FY26 %7.1f FY27 %7.1f  H1 %+6.1f H2 %+6.1f' % (c, byc[c]['fy25'], byc[c]['fy26'], byc[c]['fy27'], byc[c]['h1'], byc[c]['h2']))
print('H1 total %+.1f H2 total %+.1f hotel %.1f' % (sum(byc[c]['h1'] for c in CL), sum(byc[c]['h2'] for c in CL), hot))
print('monthly', [round(sum(f27[c][m] for c in CL), 1) for m in range(12)])
