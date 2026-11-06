# -*- coding: utf-8 -*-
# Who moved in October 2026: customers by platform rate class (Oct 26, Sep 26, Oct 25) and the RT10 consumption-band migration Sep -> Oct.
import csv, io, json, collections, os
HERE = r'C:\Projects\Sales_Platform\analysis'; os.chdir(HERE)
norm = lambda s: str(s).strip().upper(); RMAP = {}; RCMAP = {}
for r in list(csv.reader(open(r'C:\Users\jwilson\Downloads\Rate categorry Data mapping.csv', encoding='utf-8-sig')))[1:]:
    if len(r) >= 3: RMAP[norm(r[2])] = r[0]; RCMAP.setdefault(norm(r[1]), r[0])
cls_of = lambda s, rc: RCMAP.get(norm(rc)) or RMAP.get(norm(s)) or 'Other'
def band(k):
    if k < 0: return '<Zero'
    if k == 0: return 'Zero'
    if k < 150: return '<150'
    if k < 350: return '150>350'
    if k < 550: return '350>550'
    if k < 750: return '550>750'
    if k < 950: return '750>950'
    return 'over 950'
FILES = {'o26': 'Oct 26.csv', 's26': 'Sep 26.csv', 'o25': 'Oct 25.csv'}
cust = collections.defaultdict(lambda: {'name': '', 'o26': 0.0, 's26': 0.0, 'o25': 0.0})   # key class|cust
res = {k: {} for k in FILES}                                                              # RT10 premise-service -> net kWh
for tag, fn in FILES.items():
    rd = csv.reader(io.open(fn, encoding='utf-8', errors='replace')); h = next(rd); ix = {n: i for i, n in enumerate(h)}
    ci, pi, si, ni, sr, rc, kw = ix['Cust_Code'], ix['Prem_Code'], ix['Ucrserv_Num'], ix['Name'], ix['Srat_Code'], ix['rate_class'], ix['net_kwh_billed_consump']
    cb = ix['cust_billed']
    for row in rd:
        if len(row) <= kw: continue
        c = cls_of(row[sr], row[rc])
        try: k = float(row[kw] or 0)
        except ValueError: continue
        if c in ('RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70'):
            e = cust[c + '|' + row[ci]]; e[tag] += k
            if not e['name'] or tag == 'o26': e['name'] = row[ni].strip()
        elif c == 'RT10':
            if row[cb] == '0': continue          # not billed this month: the platform's band counts exclude these rows
            res[tag][row[ci] + '|' + row[pi] + '|' + row[si]] = res[tag].get(row[ci] + '|' + row[pi] + '|' + row[si], 0.0) + k
    print(tag, 'done', len(res[tag]), flush=True)
# residential bands and migration
BANDS = ['<Zero', 'Zero', '<150', '150>350', '350>550', '550>750', '750>950', 'over 950']
summ = {tag: {b: [0, 0.0] for b in BANDS} for tag in FILES}
for tag in FILES:
    for k, v in res[tag].items(): s = summ[tag][band(v)]; s[0] += 1; s[1] += v
mig = collections.defaultdict(int); NB = 'Not billed'
for k in set(res['o26']) | set(res['s26']):
    a = band(res['s26'][k]) if k in res['s26'] else NB; b = band(res['o26'][k]) if k in res['o26'] else NB
    mig[a + '>' + b] += 1
json.dump({'cust': cust, 'bands': summ, 'mig': mig}, open('_oct_who_moved.json', 'w'))
print('saved', len(cust))
