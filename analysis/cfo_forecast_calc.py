# -*- coding: utf-8 -*-
import json, sys, io
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

YEAR = 2026
CUR_MONTH = 7  # last closed actual month
PRIOR_YEAR = 2025

acts = json.load(open('_cfo_actuals.json'))          # commercial, per-account, 2025-2026
kam_rows = json.load(open('_cfo_kam.json'))
ind_rows = json.load(open('_cfo_ind.json'))
macro_rows = json.load(open('_cfo_macro.json'))
opadj_rows = json.load(open('_cfo_opadj.json'))
bud_rows = json.load(open('_cfo_budget.json'))        # commercial, per-account, 2026
rc_acts = json.load(open('_cfo_rc_actuals.json'))     # all rate classes, aggregate
rc_bud = json.load(open('_cfo_rc_budget.json'))       # all rate classes, aggregate, 2026

kam_map = {}
for r in kam_rows:
    ac = str(r.get('jps_ac') or '').strip()
    k = (r.get('kam') or '').strip()
    if ac and k:
        kam_map[ac] = k

ind_map = {}
for r in ind_rows:
    ac = str(r.get('jps_ac') or '').strip()
    v = (r.get('industry') or '').strip()
    if ac and v:
        ind_map[ac] = v

# jps_kam/jps_industries key by customer number only (e.g. '100993'), while
# jps_actuals keys by full account (e.g. '100993-731209') -- same split-off-the-premise
# pattern the customer-summary RPC bug had. The live app's own _dfcBuildIndices()
# handles this with a customer-number fallback; replicate it here so KAM/industry
# assignment isn't silently empty for every account.
def lookup(m, full_ac):
    if full_ac in m:
        return m[full_ac]
    return m.get(full_ac.split('-')[0])

# macro assumptions: (driver_type, segment_or_None) -> {month: pct}
macro = defaultdict(dict)
for r in macro_rows:
    dt = r['driver_type']; seg = r.get('segment'); m = int(r['month'])
    macro[(dt, seg)][m] = float(r.get('value_pct') or 0)

def macro_pct(driver_type, seg, month):
    return macro.get((driver_type, seg), {}).get(month, 0.0)

# operational adjustments: (jps_ac, month) -> (pct, manual_kwh)
opadj = {}
for r in opadj_rows:
    ac = str(r.get('jps_ac') or '').strip()
    m = int(r['month'])
    opadj[(ac, m)] = (float(r.get('operational_pct') or 0), float(r.get('manual_kwh') or 0))

# account meta + monthly actuals: jps_ac -> {'rc':..,'parish':..,'bucket':..,'name':..,'m25':{1..12},'m26':{1..12}}
accts = defaultdict(lambda: {'rc': None, 'parish': None, 'bucket': None, 'name': None, 'm25': {}, 'm26': {}})
rc_recency = {}  # jps_ac -> latest (year,month) seen, so rate_class reflects CURRENT classification
for r in acts:
    ac = str(r.get('jps_ac') or '').strip()
    if not ac:
        continue
    a = accts[ac]
    y = int(r['year']); m = int(r['month']); kwh = float(r.get('kwh') or 0)
    ym = y * 100 + m
    # rate_class: same bug class as get_customers_summary's old MAX() pick -- take the
    # value from the most recent billed month, not whichever row happened to iterate last.
    if r.get('rate_class') and ym >= rc_recency.get(ac, -1):
        a['rc'] = r['rate_class']
        rc_recency[ac] = ym
    if r.get('parish'): a['parish'] = r['parish']
    if r.get('consumption_bucket') is not None: a['bucket'] = r.get('consumption_bucket') or ''
    if r.get('name'): a['name'] = r['name']
    if y == PRIOR_YEAR: a['m25'][m] = a['m25'].get(m, 0) + kwh
    elif y == YEAR: a['m26'][m] = a['m26'].get(m, 0) + kwh

print(f'Total commercial accounts discovered: {len(accts)}', file=sys.stderr)

kam_accts = {ac: a for ac, a in accts.items() if lookup(kam_map, ac)}
nonkam_accts = {ac: a for ac, a in accts.items() if not lookup(kam_map, ac)}
print(f'KAM-owned: {len(kam_accts)}  Non-KAM: {len(nonkam_accts)}', file=sys.stderr)

SEG_OF_RC = {'RT10': 'residential', 'RT20': 'residential',
             'RT40': 'commercial', 'RT50': 'commercial', 'RT60-ST': 'commercial', 'RT70': 'commercial', 'BU': 'commercial'}

def build_chain(rc, industry, ac_for_opadj, m26):
    """Returns dict month(1..12) -> total kwh for YEAR, given known actuals m26[1..cur_month]."""
    chain = {}
    for m in range(1, CUR_MONTH + 1):
        chain[m] = m26.get(m, 0.0)
    seg = SEG_OF_RC.get(rc, 'commercial')
    for m in range(CUR_MONTH + 1, 13):
        terms = [chain[mm] for mm in (m - 1, m - 2, m - 3) if mm in chain]
        base = sum(terms) / len(terms) if terms else 0.0
        macro_p = macro_pct('macro', seg, m)
        weather_p = macro_pct('weather', None, m)
        if industry:
            ind_p = macro_pct('industry', industry, m)
        elif seg == 'residential':
            ind_p = macro_pct('seasonality_residential', None, m)
        else:
            ind_p = 0.0
        oper_p, manual_kwh = (0.0, 0.0)
        if ac_for_opadj:
            oper_p, manual_kwh = opadj.get((ac_for_opadj, m), (0.0, 0.0))
        total = base * (1 + (macro_p + weather_p + ind_p + oper_p) / 100.0) + manual_kwh
        chain[m] = total
    return chain

# ---- Cohort pooling for non-KAM commercial accounts: (rc, parish, bucket) ----
cohort_m26 = defaultdict(lambda: defaultdict(float))
cohort_meta = {}
for ac, a in nonkam_accts.items():
    if not a['rc'] or a['rc'] == 'EV':
        continue
    key = (a['rc'], a['parish'] or '', a['bucket'] or '')
    cohort_meta[key] = a['rc']
    for m, v in a['m26'].items():
        cohort_m26[key][m] += v

# ---- Results accumulators ----
rc_month = defaultdict(lambda: defaultdict(float))          # rate_class -> month -> kwh (FY2026, KAM+cohort combined)
kam_month = defaultdict(lambda: defaultdict(float))         # kam -> month -> kwh
kam_ind_fy = defaultdict(lambda: defaultdict(float))        # kam -> industry -> FY kwh
kam_rc_fy = defaultdict(lambda: defaultdict(float))         # kam -> rc -> FY kwh
ind_month = defaultdict(lambda: defaultdict(float))         # industry -> month -> kwh (FY2026)
kam_py_fy = defaultdict(float)                              # kam -> FY2025 actual kwh (for YoY)
kam_accounts_count = defaultdict(int)
# kam -> custno -> {'name':.., 'fy':.., 'py':.., 'n_accounts':..} -- rolled up to
# CUSTOMER (not premise/account) since one customer can hold several accounts under
# the same KAM (same custno-vs-full-jps_ac split as jps_kam itself uses).
kam_customers = defaultdict(lambda: defaultdict(lambda: {'name': None, 'fy': 0.0, 'py': 0.0, 'n_accounts': 0}))

def bump_all(rc, industry, kam, chain, py_total, ac=None, name=None):
    for m in range(1, 13):
        v = chain.get(m, 0.0)
        rc_month[rc][m] += v
        if kam:
            kam_month[kam][m] += v
    fy = sum(chain.values())
    ind_key = industry or 'No KAM / Cohort'
    if kam:
        kam_ind_fy[kam][ind_key] += fy
        kam_rc_fy[kam][rc] += fy
        kam_py_fy[kam] += py_total
        if ac:
            custno = ac.split('-')[0]
            c = kam_customers[kam][custno]
            if name and not c['name']:
                c['name'] = name
            c['fy'] += fy
            c['py'] += py_total
            c['n_accounts'] += 1
    for m in range(1, 13):
        ind_month[ind_key][m] += chain.get(m, 0.0)

# KAM-owned accounts: individual chains
for ac, a in kam_accts.items():
    if not a['rc'] or a['rc'] == 'EV':
        continue
    industry = lookup(ind_map, ac)
    kam_name = lookup(kam_map, ac)
    chain = build_chain(a['rc'], industry, ac, a['m26'])
    py_total = sum(a['m25'].values())
    bump_all(a['rc'], industry, kam_name, chain, py_total, ac=ac, name=a['name'])
    kam_accounts_count[kam_name] += 1

# Non-KAM cohorts: pooled chains, industry=None, no op-adjustments
for key, m26 in cohort_m26.items():
    rc = cohort_meta[key]
    chain = build_chain(rc, None, None, m26)
    bump_all(rc, None, None, chain, 0)

print('\n=== Commercial FY2026 forecast by rate class (validate vs live app) ===', file=sys.stderr)
for rc in sorted(rc_month.keys()):
    fy = sum(rc_month[rc].values())
    print(f'  {rc:10s} {fy/1e6:8.2f} GWh', file=sys.stderr)

# ---- Residential pooled forecast (RT10, RT20) from RC-level aggregate actuals ----
rc_all_m = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))  # rc -> year -> month -> kwh
for r in rc_acts:
    rc_all_m[r['rate_class']][int(r['year'])][int(r['month'])] = float(r['kwh'])

for rc in ('RT10', 'RT20'):
    m26 = rc_all_m[rc].get(YEAR, {})
    chain = build_chain(rc, None, None, m26)
    for m in range(1, 13):
        rc_month[rc][m] += chain.get(m, 0.0)

# ---- Budget by rate class (all classes, full FY2026) ----
rc_budget_fy = defaultdict(float)
for r in rc_bud:
    rc_budget_fy[r['rate_class']] += float(r['kwh_budget'])

# ---- Prior year (2025) actuals by rate class (all classes, full FY) ----
rc_py_fy = defaultdict(float)
for r in rc_acts:
    if int(r['year']) == PRIOR_YEAR:
        rc_py_fy[r['rate_class']] += float(r['kwh'])

print('\n=== FULL company FY2026 forecast vs budget vs PY, by rate class ===', file=sys.stderr)
tot_fc = tot_bud = tot_py = 0
for rc in sorted(rc_month.keys()):
    fy = sum(rc_month[rc].values())
    bud = rc_budget_fy.get(rc, 0)
    py = rc_py_fy.get(rc, 0)
    tot_fc += fy; tot_bud += bud; tot_py += py
    vb = f'{(fy/bud-1)*100:.1f}%' if bud else 'n/a'
    vy = f'{(fy/py-1)*100:.1f}%' if py else 'n/a'
    print(f'  {rc:10s} FC={fy/1e6:8.2f}  Bud={bud/1e6:8.2f}  PY={py/1e6:8.2f}  vsBud={vb}  vsPY={vy}', file=sys.stderr)
print(f'  TOTAL      FC={tot_fc/1e6:8.2f}  Bud={tot_bud/1e6:8.2f}  PY={tot_py/1e6:8.2f}  vsBud={(tot_fc/tot_bud-1)*100:.1f}%  vsPY={(tot_fc/tot_py-1)*100:.1f}%', file=sys.stderr)

# ---- Budget by KAM (map commercial per-account budget rows to KAM) ----
kam_budget_fy = defaultdict(float)
for r in bud_rows:
    ac = str(r.get('jps_ac') or '').strip()
    kam = lookup(kam_map, ac)
    if kam:
        kam_budget_fy[kam] += float(r.get('kwh_budget') or 0)

print('\n=== KAM summary: FY2026 forecast vs budget vs PY2025 ===', file=sys.stderr)
for kam in sorted(kam_month.keys(), key=lambda k: -sum(kam_month[k].values())):
    fy = sum(kam_month[kam].values())
    bud = kam_budget_fy.get(kam, 0)
    py = kam_py_fy.get(kam, 0)
    n = kam_accounts_count.get(kam, 0)
    vb = f'{(fy/bud-1)*100:.1f}%' if bud else 'n/a'
    vy = f'{(fy/py-1)*100:.1f}%' if py else 'n/a'
    print(f'  {kam:20s} n={n:3d}  FC={fy/1e6:7.2f}  Bud={bud/1e6:7.2f}  PY={py/1e6:7.2f}  vsBud={vb}  vsPY={vy}', file=sys.stderr)

# ---- Assumptions actually applied to the forecast months (CUR_MONTH+1..12) ----
fc_months = list(range(CUR_MONTH + 1, 13))
assumptions = {
    'forecast_months': fc_months,
    'macro_commercial': {m: macro_pct('macro', 'commercial', m) for m in fc_months},
    'macro_residential': {m: macro_pct('macro', 'residential', m) for m in fc_months},
    'weather': {m: macro_pct('weather', None, m) for m in fc_months},
    'seasonality_residential': {m: macro_pct('seasonality_residential', None, m) for m in fc_months},
    # industry -> {month: pct} for every industry with a non-empty assumption row
    'industry': {ind: {m: pct for m, pct in months.items()} for (dt, ind), months in macro.items() if dt == 'industry'},
    'operational_adjustments': [
        {'jps_ac': r.get('jps_ac'), 'month': int(r['month']), 'operational_pct': float(r.get('operational_pct') or 0),
         'manual_kwh': float(r.get('manual_kwh') or 0), 'reason_code': r.get('reason_code'), 'justification': r.get('justification'),
         'name': accts.get(str(r.get('jps_ac') or '').strip(), {}).get('name'),
         'kam': lookup(kam_map, str(r.get('jps_ac') or '').strip())}
        for r in opadj_rows
    ],
}

print('\n=== Customer counts by KAM ===', file=sys.stderr)
for kam in sorted(kam_customers.keys(), key=lambda k: -sum(kam_month[k].values())):
    print(f'  {kam:20s} {len(kam_customers[kam])} customers', file=sys.stderr)

# ---- Save everything needed for the deck ----
out = {
    'year': YEAR, 'cur_month': CUR_MONTH, 'prior_year': PRIOR_YEAR,
    'rc_month': {rc: dict(v) for rc, v in rc_month.items()},
    'rc_budget_fy': dict(rc_budget_fy),
    'rc_py_fy': dict(rc_py_fy),
    'kam_month': {k: dict(v) for k, v in kam_month.items()},
    'kam_budget_fy': dict(kam_budget_fy),
    'kam_py_fy': dict(kam_py_fy),
    'kam_ind_fy': {k: dict(v) for k, v in kam_ind_fy.items()},
    'kam_rc_fy': {k: dict(v) for k, v in kam_rc_fy.items()},
    'kam_accounts_count': dict(kam_accounts_count),
    'kam_customers': {k: {c: v for c, v in custs.items()} for k, custs in kam_customers.items()},
    'ind_month': {k: dict(v) for k, v in ind_month.items()},
    'assumptions': assumptions,
}
json.dump(out, open('_cfo_deck_data.json', 'w'))
print('\nSaved _cfo_deck_data.json', file=sys.stderr)
