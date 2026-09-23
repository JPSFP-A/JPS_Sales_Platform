# -*- coding: utf-8 -*-
# Scans the raw monthly billing files for (1) GCT by title for RT40/50/60-ST/70 and
# (2) any account whose name looks like an EV operator (Evergo etc.), all months.
import csv, glob, re, json, collections
csv.field_size_limit(10**9)
norm = lambda s: str(s).strip().upper()
RMAP = {}; RCMAP = {}
for r in list(csv.reader(open(r'C:\Users\jwilson\Downloads\Rate categorry Data mapping.csv', encoding='utf-8-sig')))[1:]:
    if len(r) >= 3:
        RMAP[norm(r[2])] = r[0]; RCMAP.setdefault(norm(r[1]), r[0])
def title_of(rc, srat): return RCMAP.get(norm(rc)) or RMAP.get(norm(srat))
MON = {'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
files = sorted(f for f in glob.glob('*.csv') if re.match(r'(?i)^[a-z]{3} \d\d\.csv$', f))
out = {'gct': {}, 'ev_names': {}}
def num(x):
    try: return float(x)
    except: return 0.0
for f in files:
    m = re.match(r'(?i)^([a-z]{3}) (\d\d)\.csv$', f); mo = '20%s-%02d' % (m.group(2), MON[m.group(1).upper()])
    want_gct = mo in ('2025-01','2025-02','2025-03','2025-04','2025-05','2025-06','2025-07','2025-08',
                      '2026-01','2026-02','2026-03','2026-04','2026-05','2026-06','2026-07','2026-08')
    g = collections.defaultdict(lambda: [0, 0.0, 0.0])
    ev = collections.defaultdict(lambda: [0, 0.0, 0.0])
    with open(f, encoding='utf-8', errors='ignore', newline='') as fh:
        for r in csv.DictReader(fh):
            nm = (r.get('Name') or '')
            low = nm.lower()
            if 'evergo' in low or 'ev ergo' in low or 'ever go' in low or 'e-mobility' in low or 'emobility' in low:
                a = ev[nm.strip() + '|' + (r.get('Srat_Code') or '') + '|' + (r.get('rate_class') or '')]
                a[0] += 1; a[1] += num(r.get('net_kwh_billed_consump')); a[2] += num(r.get('net_revenue'))
            if want_gct:
                t = title_of(r.get('rate_class') or '', r.get('Srat_Code') or '')
                if t in ('RT40', 'RT50', 'RT60-ST', 'RT60', 'RT70'):
                    a = g[t]; a[0] += 1; a[1] += num(r.get('GCT')); a[2] += num(r.get('net_revenue'))
    out['gct'][mo] = {k: v for k, v in g.items()}
    out['ev_names'][mo] = {k: v for k, v in ev.items()}
    json.dump(out, open('_gct_ev_scan.json', 'w'))
    print(mo, 'done', flush=True)
print('ALL DONE', flush=True)
