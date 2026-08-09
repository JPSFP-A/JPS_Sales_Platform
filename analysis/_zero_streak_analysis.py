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
import json, requests

SECRET = open(r'D:\Projects\DataManager\.env').read().split('=', 1)[1].strip()
URL = 'https://bhrswnbenkvflpdjhfpa.supabase.co/rest/v1/rpc/exec_sql_placeholder'  # unused, direct REST below

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
                select='jps_ac,rate_class,year,month,kwh,name,revenue_jmd')
print('rows:', len(rows), flush=True)

# jps_ac -> rate_class -> list of (period_idx, year, month, kwh, name, rev)
by_acct = {}
for r in rows:
    if not r['jps_ac']:
        continue
    key = (r['jps_ac'], r['rate_class'])
    period = r['year'] * 12 + r['month']
    by_acct.setdefault(key, []).append((period, r['year'], r['month'], r['kwh'] or 0.0, r['name'], r['revenue_jmd'] or 0.0))

streaks = []
for (jps_ac, rc), recs in by_acct.items():
    recs.sort()
    latest = recs[-1]
    if latest[3] != 0:
        continue  # most recent month isn't zero -> no ongoing streak
    # walk backward from the latest record while consecutive present months are all zero
    streak_months = []
    prev_period = None
    for rec in reversed(recs):
        period, y, m, kwh, name, rev = rec
        if prev_period is not None and prev_period - period != 1:
            break  # gap in presence -> streak ends
        if kwh != 0:
            break
        streak_months.append(rec)
        prev_period = period
    streaks.append({
        'jps_ac': jps_ac, 'rate_class': rc, 'name': latest[4],
        'streak_len': len(streak_months),
        'streak_start': f'{streak_months[-1][1]}-{streak_months[-1][2]:02d}',
        'streak_end': f'{streak_months[0][1]}-{streak_months[0][2]:02d}',
        'last_nonzero_rev': next((rec[5] for rec in reversed(recs) if rec[3] != 0), None),
    })

streaks.sort(key=lambda s: -s['streak_len'])
print('accounts with ongoing zero streak:', len(streaks))
for thresh in (2, 3, 6, 12):
    print(f'  streak >= {thresh} months:', sum(1 for s in streaks if s['streak_len'] >= thresh))

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
