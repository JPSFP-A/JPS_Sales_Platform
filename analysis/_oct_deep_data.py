# -*- coding: utf-8 -*-
# Data for the October 2026 extended analysis: recovery check, parish, industry, KAM, residential bands, 2027 outlook.
# Everything is computed from the loaded database, corrected.json (parish grain) and the held LE workbook. Output: _oct_deep.json
import csv, json, os, sys, collections, requests, openpyxl
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '_cust'))
from db import BASE, H, fetch
f = lambda v: float(v or 0)
def rpc(fn, body):
    r = requests.post(f'{BASE}/rest/v1/rpc/{fn}', headers={**H, 'Content-Type': 'application/json'}, data=json.dumps(body), timeout=300)
    r.raise_for_status(); return r.json()
rows = rpc('get_comm_actuals', {'year_cutoff': 2025}) + rpc('get_res_actuals', {'year_cutoff': 2025})
bag = rpc('get_budget_agg', {'year_cutoff': 2026})
ind = {r['jps_ac']: r['industry'] for r in fetch('jps_industries', 'select=jps_ac,industry', page=1000)}
kamrows = fetch('jps_kam', 'select=jps_ac,kam', page=1000)
kam = {str(k['jps_ac']).strip(): k['kam'] for k in kamrows}
ind_of = lambda ac: ind.get((ac or '').split('-')[0]) or ''
kam_of = lambda ac: kam.get(ac) or kam.get((ac or '').split('-')[0]) or ''
BIG = ('RT40', 'RT50', 'RT60-ST', 'RT70'); COMM = ('RT20',) + BIG
out = {}

# ---- A. monthly series 2025 and 2026
ser = collections.defaultdict(lambda: collections.defaultdict(float))
for x in rows:
    ym = (x['year'], x['month']); k = f(x['kwh']) / 1e6
    ser['total'][ym] += k
    ser['RT10'][ym] += k if x['rate_class'] == 'RT10' else 0
    ser['RT20'][ym] += k if x['rate_class'] == 'RT20' else 0
    if x['rate_class'] in BIG: ser['RT40-70'][ym] += k
    if x['jps_ac']:
        i = ind_of(x['jps_ac'])
        if 'Hotels' in i: ser['hotels'][ym] += k
        if 'Water Supply' in i: ser['water'][ym] += k
        if 'Mining' in i or 'Metal Ore' in i: ser['mining'][ym] += k
out['series'] = {g: {'%d-%02d' % ym: v for ym, v in s.items()} for g, s in ser.items()}

# ---- two-year view from corrected.json (postpaid, pre-storm baseline Oct 2024)
cj = json.load(open('corrected.json')); L = cj['srat_legend']; ix = {n: i for i, n in enumerate(L)}; SEP = cj.get('sep', '||')
norm = lambda s: str(s).strip().upper(); RMAP = {}; RCMAP = {}
for r in list(csv.reader(open(r'C:\Users\jwilson\Downloads\Rate categorry Data mapping.csv', encoding='utf-8-sig')))[1:]:
    if len(r) >= 3: RMAP[norm(r[2])] = r[0]; RCMAP.setdefault(norm(r[1]), r[0])
def title(key):
    s, rc = key.split(SEP, 1); return RCMAP.get(norm(rc)) or RMAP.get(norm(s)) or 'Other'
cls = collections.defaultdict(lambda: collections.defaultdict(float)); par = collections.defaultdict(lambda: collections.defaultdict(float))
for mo, keys in cj['srat'].items():
    for key, pp in keys.items():
        t = 'RT10' if title(key) == 'RT10' else ('COMM' if title(key) in ('RT20', 'RT40', 'RT50', 'RT60', 'RT60-ST', 'RT70') else 'OTHER')
        for pg, v in pp.items():
            cls[mo][title(key)] += v[ix['kwh']] / 1e6
            par[(mo, pg)][t] += v[ix['kwh']] / 1e6
out['postpaid_class'] = {mo: dict(v) for mo, v in cls.items() if mo in ('2024-10', '2025-10', '2026-09', '2026-10', '2024-09', '2025-09')}

# ---- B. parish: postpaid (corrected.json) plus prepaid by parish (database); budget by parish
pre = collections.defaultdict(lambda: collections.defaultdict(float))
for x in rows:
    if x['consumption_bucket'] == 'Prepaid':
        pre[(x['year'], x['month'], x['parish'])]['RT10' if x['rate_class'] == 'RT10' else 'COMM'] += f(x['kwh']) / 1e6
bud = collections.defaultdict(lambda: collections.defaultdict(float))
for x in bag:
    if x['year'] == 2026 and x['month'] == 10: bud[x['parish']]['RT10' if x['rate_class'] == 'RT10' else 'COMM'] += f(x['kwh_budget']) / 1e6
PARISH = {}
names = sorted({pg for (mo, pg) in par if mo == '2026-10'})
for pg in names:
    rec = {}
    for lab, mo, y, m in (('o26', '2026-10', 2026, 10), ('o25', '2025-10', 2025, 10), ('s26', '2026-09', 2026, 9), ('o24', '2024-10', 2024, 10)):
        for g in ('RT10', 'COMM'):
            rec[f'{lab}_{g}'] = par[(mo, pg)][g] + (pre[(y, m, pg)][g] if y >= 2025 else 0.0)
    for g in ('RT10', 'COMM'): rec[f'bud_{g}'] = bud[pg][g]
    PARISH[pg] = rec
out['parish'] = PARISH
tot = {k: sum(r[k] for r in PARISH.values()) for k in next(iter(PARISH.values()))}
out['parish_check'] = tot

# ---- C. industry (account-level rows)
IND = collections.defaultdict(lambda: collections.defaultdict(float))
for x in rows:
    if x['jps_ac'] and x['rate_class'] in COMM:
        i = ind_of(x['jps_ac']) or '(no industry)'; ym = (x['year'], x['month'])
        if ym == (2026, 10): IND[i]['o26'] += f(x['kwh']) / 1e6; IND[i]['n'] += 1
        if ym == (2025, 10): IND[i]['o25'] += f(x['kwh']) / 1e6
        if ym == (2026, 9): IND[i]['s26'] += f(x['kwh']) / 1e6
for x in bag:
    if x['year'] == 2026 and x['month'] == 10 and x['jps_ac'] and x['rate_class'] in COMM:
        IND[ind_of(x['jps_ac']) or '(no industry)']['bud'] += f(x['kwh_budget']) / 1e6
# like-for-like budget: actual kWh from accounts that have no budget line at all is shown separately
budacs = {x['jps_ac'] for x in bag if x['year'] == 2026 and x['month'] == 10 and x['jps_ac'] and f(x['kwh_budget']) > 0}
for x in rows:
    if x['jps_ac'] and x['rate_class'] in COMM and (x['year'], x['month']) == (2026, 10) and x['jps_ac'] not in budacs:
        IND[ind_of(x['jps_ac']) or '(no industry)']['unbud'] += f(x['kwh']) / 1e6
# account movers September to October (commercial accounts) with the Jul-Oct history
hist = collections.defaultdict(lambda: collections.defaultdict(float)); meta = {}
for x in rows:
    if x['jps_ac'] and x['rate_class'] in COMM and x['year'] == 2026 and x['month'] in (7, 8, 9, 10):
        hist[x['jps_ac']][x['month']] += f(x['kwh']) / 1e6; meta[x['jps_ac']] = (x['name'], x['rate_class'])
cust = collections.defaultdict(lambda: collections.defaultdict(float)); cmeta = {}
for ac, h in hist.items():
    key = ac.split('-')[0]
    for m, v in h.items(): cust[key][m] += v
    cmeta.setdefault(key, meta[ac])
out['movers'] = {k: {'name': cmeta[k][0], 'rc': cmeta[k][1], 'ind': ind_of(k + '-0'), **{str(m): v for m, v in h.items()}} for k, h in cust.items()}
# ex-Alcoa series for RT40-RT70
for x in rows:
    if x['jps_ac'] and x['jps_ac'].startswith('100185-') and x['rate_class'] in BIG:
        ser['alcoa'][(x['year'], x['month'])] += f(x['kwh']) / 1e6
out['series'] = {g: {'%d-%02d' % ym: v for ym, v in s_.items()} for g, s_ in ser.items()}
out['industry'] = {k: dict(v) for k, v in IND.items()}

# ---- D. KAM (RT20 to RT70 accounts with a named KAM)
KAMT = collections.defaultdict(lambda: collections.defaultdict(float))
for x in rows:
    if x['jps_ac'] and x['rate_class'] in COMM and kam_of(x['jps_ac']):
        ym = (x['year'], x['month']); k = kam_of(x['jps_ac'])
        if ym == (2026, 10): KAMT[k]['o26'] += f(x['kwh']) / 1e6
        if ym == (2025, 10): KAMT[k]['o25'] += f(x['kwh']) / 1e6
        if ym == (2026, 9): KAMT[k]['s26'] += f(x['kwh']) / 1e6
for x in bag:
    if x['year'] == 2026 and x['month'] == 10 and x['jps_ac'] and x['rate_class'] in COMM and kam_of(x['jps_ac']): KAMT[kam_of(x['jps_ac'])]['bud'] += f(x['kwh_budget']) / 1e6
out['kam'] = {k: dict(v) for k, v in KAMT.items()}

# ---- E. residential bands (RT10, with customers)
BAND = collections.defaultdict(lambda: collections.defaultdict(float))
for x in rows:
    if x['rate_class'] == 'RT10' and not x['jps_ac']:
        ym = '%d-%02d' % (x['year'], x['month'])
        if ym in ('2026-10', '2026-09', '2025-10'):
            BAND[x['consumption_bucket']][ym + '_kwh'] += f(x['kwh']) / 1e6; BAND[x['consumption_bucket']][ym + '_cust'] += f(x['customer_count'])
out['bands'] = {k: dict(v) for k, v in BAND.items()}

# ---- G. LE FY2026 and FY2027 by class
ws = openpyxl.load_workbook(r'C:\Projects\Sales_Platform\JPS_Billed_Sales_and_Net_Gen_FY2026-28_v5.xlsx', data_only=True)['Billed by rate class']
hdr = [c.value for c in ws[4]]; LE = {}
for r in ws.iter_rows(min_row=5, values_only=True):
    k = str(r[0] or '').split(' ')[0].replace('RT60', 'RT60-ST')
    if k in ('RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70'):
        LE[k] = {h: float(v) for h, v in zip(hdr, r) if h and isinstance(v, (int, float))}
out['le'] = LE
out['zero'] = json.load(open('_zero_streak_result_2026-10.json'))['rt10_monthly_zero_count']
json.dump(out, open('_oct_deep.json', 'w'))
print('parish check totals', {k: round(v, 3) for k, v in tot.items()})
print('industries', len(IND), '| KAMs', len(KAMT), '| bands', list(BAND))
print('LE keys sample', list(LE['RT10'])[:40])
