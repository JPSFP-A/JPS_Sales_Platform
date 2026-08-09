# -*- coding: utf-8 -*-
# Cross-rate-class zero-consumption anomaly analysis.
#
# Two different populations, two different levels of precision:
#  1. Premise-level classes (RT20-Commercial, RT40, RT50, RT60-ST, RT70) have real
#     per-account (jps_ac) identity across months in jps_actuals, so a TRUE consecutive-
#     months-at-zero-kWh streak can be computed per account.
#  2. RT10 and RT20's residential-style (no-NAICS) population are bucket-aggregates with
#     NO per-customer identity -- only a monthly zero-consumption CUSTOMER COUNT is
#     possible there, not a per-customer streak.
#
# IMPORTANT (found by tracing a sample of long-streak accounts back to the raw CIS
# billing file): zero-kWh accounts are NOT $0-revenue accounts. Large commercial/
# industrial rate classes (RT40 etc.) bill a minimum/standby demand charge when
# metered consumption is 0 -- confirmed present in JPS's own raw extract, not a
# pipeline artifact. Many unrelated customers (from JPS itself to individual people)
# share bit-identical demand_jmd/ipp_jmd/customer_charge_jmd figures every month,
# which is the signature of a standardized minimum-bill tariff tier, not duplicate
# records. Each streak is tagged is_minbill_cluster=True when its most recent period's
# (demand,ipp,customer_charge) combo is shared with >=1 other account that period --
# those are almost certainly minimum-bill tariff accounts, not billing anomalies. The
# real open question for THOSE is operational (is the meter being read at all for 19
# straight months?), not a revenue/data-integrity one.
import json, requests

SECRET = open(r'D:\Projects\DataManager\.env').read().split('=', 1)[1].strip()
REST_HDRS = {'apikey': SECRET, 'Authorization': 'Bearer ' + SECRET}
REST_URL = 'https://bhrswnbenkvflpdjhfpa.supabase.co/rest/v1'


def get_all(table, params, select='*'):
    out = []
    page = 0
    while True:
        p = dict(params)
        p['select'] = select
        p['limit'] = 1000
        p['offset'] = page * 1000
        p['order'] = 'id.asc'
        r = requests.get(f'{REST_URL}/{table}', headers=REST_HDRS, params=p, timeout=60)
        rows = r.json()
        out.extend(rows)
        if len(rows) < 1000:
            break
        page += 1
    return out


PREMISE_CLASSES = ['RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']

print('fetching premise-level rows...', flush=True)
rows = get_all('jps_actuals',
                {'rate_class': f'in.({",".join(PREMISE_CLASSES)})', 'consumption_bucket': 'eq.Commercial'},
                select='jps_ac,rate_class,year,month,kwh,name,revenue_jmd,demand_jmd,ipp_jmd,customer_charge_jmd')
print('rows:', len(rows), flush=True)

# jps_ac -> rate_class -> list of records
by_acct = {}
for r in rows:
    if not r['jps_ac']:
        continue
    key = (r['jps_ac'], r['rate_class'])
    period = r['year'] * 12 + r['month']
    by_acct.setdefault(key, []).append({
        'period': period, 'year': r['year'], 'month': r['month'], 'kwh': r['kwh'] or 0.0,
        'name': r['name'], 'rev': r['revenue_jmd'] or 0.0,
        'demand': r['demand_jmd'], 'ipp': r['ipp_jmd'], 'cc': r['customer_charge_jmd'],
    })

# For minimum-bill-cluster detection: per (year,month), which (demand,ipp,cc) combos
# among zero-kWh rows are shared by more than one account.
by_period_combo = {}
for r in rows:
    if (r['kwh'] or 0.0) != 0:
        continue
    period = r['year'] * 12 + r['month']
    combo = (r['demand_jmd'], r['ipp_jmd'], r['customer_charge_jmd'])
    by_period_combo.setdefault(period, {}).setdefault(combo, set()).add(r['jps_ac'])

streaks = []
for (jps_ac, rc), recs in by_acct.items():
    recs.sort(key=lambda x: x['period'])
    latest = recs[-1]
    if latest['kwh'] != 0:
        continue  # most recent month isn't zero -> no ongoing streak
    streak_recs = []
    prev_period = None
    for rec in reversed(recs):
        if prev_period is not None and prev_period - rec['period'] != 1:
            break
        if rec['kwh'] != 0:
            break
        streak_recs.append(rec)
        prev_period = rec['period']
    combo = (latest['demand'], latest['ipp'], latest['cc'])
    shared_accts = by_period_combo.get(latest['period'], {}).get(combo, set())
    streaks.append({
        'jps_ac': jps_ac, 'rate_class': rc, 'name': latest['name'],
        'streak_len': len(streak_recs),
        'streak_start': f"{streak_recs[-1]['year']}-{streak_recs[-1]['month']:02d}",
        'streak_end': f"{streak_recs[0]['year']}-{streak_recs[0]['month']:02d}",
        'current_monthly_revenue': latest['rev'],
        'streak_total_revenue': sum(x['rev'] for x in streak_recs),
        'is_minbill_cluster': len(shared_accts) > 1,
    })

streaks.sort(key=lambda s: -s['streak_len'])
print('accounts with ongoing zero streak:', len(streaks))
for thresh in (2, 3, 6, 12):
    print(f'  streak >= {thresh} months:', sum(1 for s in streaks if s['streak_len'] >= thresh))
n_minbill = sum(1 for s in streaks if s['is_minbill_cluster'])
print(f'  is_minbill_cluster: {n_minbill} / {len(streaks)}')
n_zero_rev = sum(1 for s in streaks if s['current_monthly_revenue'] == 0)
print(f'  genuinely $0 current-month revenue: {n_zero_rev} / {len(streaks)}')

# Monthly zero-consumption customer counts for RT10 / RT20-residential (no per-customer streak possible)
print('fetching RT10/RT20-residential monthly zero counts...', flush=True)
rt10_zero = get_all('jps_actuals', {'rate_class': 'eq.RT10', 'consumption_bucket': 'eq.Zero', 'parish': 'eq.ALL'},
                     select='year,month,customer_count,kwh')
rt20_res_zero = get_all('jps_actuals',
                         {'rate_class': 'eq.RT20', 'consumption_bucket': 'eq.Zero', 'segment': 'eq.Residential'},
                         select='year,month,customer_count,kwh,parish')

rt10_monthly = {f"{r['year']}-{r['month']:02d}": r['customer_count'] for r in rt10_zero}
rt20_res_monthly = {}
for r in rt20_res_zero:
    key = f"{r['year']}-{r['month']:02d}"
    rt20_res_monthly[key] = rt20_res_monthly.get(key, 0) + (r['customer_count'] or 0)

json.dump({
    'streaks': streaks,
    'rt10_monthly_zero_count': rt10_monthly,
    'rt20_residential_monthly_zero_count': rt20_res_monthly,
}, open('_zero_streak_result.json', 'w'))
print('WROTE _zero_streak_result.json')
