# -*- coding: utf-8 -*-
# Zero-consumption streaks for the latest loaded month (default 2026-10), built from the account-level
# aggregate the platform itself uses (get_comm_actuals / get_res_actuals), so it sees every class and bucket tag.
# Replaces _zero_streak_analysis.py for current data: that script filtered consumption_bucket='Commercial', and
# since zero-kWh commercial accounts are now tagged 'Zero' it would silently drop exactly the accounts it exists to find.
# Output: _zero_streak_result_<YYYY-MM>.json (same shape the workbook builder reads, plus a monthly zero-account trend).
# Usage: python _zero_streak_2026_10.py [YYYY-MM]
import csv, json, os, sys, requests
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '_cust'))
from db import BASE, H, fetch
csv.field_size_limit(10 ** 9)

MO = sys.argv[1] if len(sys.argv) > 1 else '2026-10'
Y, M = int(MO[:4]), int(MO[5:7])
LATEST = Y * 12 + M
MON3 = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][M - 1]
RAW = '%s %02d.csv' % (MON3, Y % 100)
STATUS_LABEL = {'A': 'Active', 'I': 'Inactive', 'N': 'New', 'F': 'Final/Closed', '': 'Unknown'}


def rpc(fn, body):
    r = requests.post(f'{BASE}/rest/v1/rpc/{fn}', headers={**H, 'Content-Type': 'application/json'}, data=json.dumps(body), timeout=300)
    r.raise_for_status()
    return r.json()


print('account rows ...', flush=True)
rows = rpc('get_comm_actuals', {'year_cutoff': 2025})
res = rpc('get_res_actuals', {'year_cutoff': 2025})
print('  account rows', len(rows), '| residential aggregate rows', len(res), flush=True)
assert any(r['year'] == Y and r['month'] == M for r in rows), 'latest month not loaded'

by_acct = {}
for r in rows:
    if not r['jps_ac']:
        continue
    by_acct.setdefault(r['jps_ac'], []).append({'period': r['year'] * 12 + r['month'], 'year': r['year'], 'month': r['month'],
        'kwh': float(r['kwh'] or 0), 'rev': float(r['revenue_jmd'] or 0), 'name': r['name'], 'rc': r['rate_class']})

# monthly count of account rows billed at exactly zero kWh, by class group
trend = {}
for r in rows:
    if not r['jps_ac']:
        continue
    k = '%d-%02d' % (r['year'], r['month'])
    t = trend.setdefault(k, {'accounts': 0, 'zero': 0, 'RT20': 0, 'RT40-RT70': 0})
    t['accounts'] += 1
    if float(r['kwh'] or 0) == 0:
        t['zero'] += 1
        t['RT20' if r['rate_class'] == 'RT20' else 'RT40-RT70'] += 1

flagged = {}
for ac, recs in by_acct.items():
    recs.sort(key=lambda x: x['period'])
    latest = recs[-1]
    if latest['period'] != LATEST or latest['kwh'] != 0:
        continue
    streak = []; prev = None
    for rec in reversed(recs):
        if prev is not None and prev - rec['period'] != 1:
            break
        if rec['kwh'] != 0:
            break
        streak.append(rec); prev = rec['period']
    flagged[ac] = {'jps_ac': ac, 'rate_class': latest['rc'], 'name': latest['name'], 'streak_len': len(streak),
        'streak_start': '%d-%02d' % (streak[-1]['year'], streak[-1]['month']), 'streak_end': '%d-%02d' % (streak[0]['year'], streak[0]['month']),
        'current_monthly_revenue': latest['rev'], 'streak_total_revenue': sum(x['rev'] for x in streak), 'is_minbill_cluster': False}
print('accounts at zero in', MO, ':', len(flagged), flush=True)

# minimum-bill cluster: unrelated accounts sharing identical demand / ipp / customer-charge at zero kWh in the latest month
print('billing components for zero rows ...', flush=True)
comp = fetch('jps_actuals', 'select=jps_ac,demand_jmd,ipp_jmd,customer_charge_jmd&year=eq.%d&month=eq.%d&kwh=eq.0&jps_ac=neq.' % (Y, M), page=1000)
combo = {}
for r in comp:
    combo.setdefault((r['demand_jmd'], r['ipp_jmd'], r['customer_charge_jmd']), set()).add(r['jps_ac'])
acct_combo = {r['jps_ac']: (r['demand_jmd'], r['ipp_jmd'], r['customer_charge_jmd']) for r in comp}
for ac, s in flagged.items():
    s['is_minbill_cluster'] = len(combo.get(acct_combo.get(ac), ())) > 1

# account status and suspension from the raw billing extract for the same month
print('account status from', RAW, flush=True)
want = {tuple(ac.split('-', 1)): ac for ac in flagged if '-' in ac}
found = {}
with open(RAW, encoding='utf-8', errors='replace', newline='') as fh:
    for r in csv.DictReader(fh):
        key = ((r.get('Cust_Code') or '').strip().replace(',', ''), (r.get('Prem_Code') or '').strip())
        if key in want:
            billed = (r.get('cust_billed') or '').strip() == '1'
            if key not in found or billed:
                found[key] = ((r.get('Account_Status') or '').strip(), (r.get('is_suspended') or '').strip())
for key, ac in want.items():
    s = flagged[ac]
    v = found.get(key)
    if v:
        s['account_status'], s['is_suspended'] = v[0], v[1]; s['account_status_label'] = STATUS_LABEL.get(v[0], v[0])
    else:
        s['account_status'], s['is_suspended'] = None, None; s['account_status_label'] = 'Not found in raw file'

streaks = sorted(flagged.values(), key=lambda s: -s['streak_len'])
rt10 = {}; rt20r = {}
for r in res:
    k = '%d-%02d' % (r['year'], r['month'])
    if r['rate_class'] == 'RT10' and r['consumption_bucket'] == 'Zero':
        rt10[k] = rt10.get(k, 0) + (r['customer_count'] or 0)
    if r['rate_class'] == 'RT20' and r['consumption_bucket'] == 'Zero':
        rt20r[k] = rt20r.get(k, 0) + (r['customer_count'] or 0)
out = {'month': MO, 'streaks': streaks, 'rt10_monthly_zero_count': rt10, 'rt20_residential_monthly_zero_count': rt20r, 'monthly_zero_accounts': trend}
json.dump(out, open('_zero_streak_result_%s.json' % MO, 'w'))
from collections import Counter
print('streak >= 2/3/6/12:', [sum(1 for s in streaks if s['streak_len'] >= n) for n in (2, 3, 6, 12)])
print('by class:', Counter(s['rate_class'] for s in streaks).most_common())
print('status:', Counter(s['account_status_label'] for s in streaks).most_common())
print('minbill cluster:', sum(s['is_minbill_cluster'] for s in streaks), '| $0 current revenue:', sum(1 for s in streaks if s['current_monthly_revenue'] == 0))
print('WROTE _zero_streak_result_%s.json' % MO)
