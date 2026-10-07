# -*- coding: utf-8 -*-
# Raw-file figures for September (GCT by title for RT40/50/60-ST/70, and EV-tariff rows).
import csv, json, collections
csv.field_size_limit(10**9)
norm = lambda s: str(s).strip().upper()
RMAP = {}; RCMAP = {}
for r in list(csv.reader(open(r'C:\Users\jwilson\Downloads\Rate categorry Data mapping.csv', encoding='utf-8-sig')))[1:]:
    if len(r) >= 3:
        RMAP[norm(r[2])] = r[0]; RCMAP.setdefault(norm(r[1]), r[0])
title_of = lambda rc, s: RCMAP.get(norm(rc)) or RMAP.get(norm(s))
def num(x):
    try: return float(x)
    except: return 0.0
out = {}
for f in ('Sep 25.csv', 'Sep 26.csv'):
    g = collections.defaultdict(lambda: [0, 0.0, 0.0]); ev = collections.defaultdict(lambda: [0, 0.0, 0.0])
    with open(f, encoding='utf-8', errors='ignore', newline='') as fh:
        for r in csv.DictReader(fh):
            t = title_of(r.get('rate_class') or '', r.get('Srat_Code') or '')
            if t in ('RT40', 'RT50', 'RT60-ST', 'RT60', 'RT70'):
                a = g[t]; a[0] += 1; a[1] += num(r.get('GCT')); a[2] += num(r.get('net_revenue'))
            if (r.get('rate_class') or '').strip().upper() == 'EV':
                a = ev[(r.get('Name') or '').strip()]; a[0] += 1; a[1] += num(r.get('net_kwh_billed_consump')); a[2] += num(r.get('net_revenue'))
    out[f] = {'gct': dict(g), 'ev': dict(ev)}
    print(f, {k: (v[0], round(v[1] / 1e6, 1), round(v[2] / 1e6, 1)) for k, v in g.items()}, 'EV rows', sum(v[0] for v in ev.values()), 'kWh', round(sum(v[1] for v in ev.values())), 'rev', round(sum(v[2] for v in ev.values())), flush=True)
json.dump(out, open('_sep_scan2.json', 'w'))
