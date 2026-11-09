# -*- coding: utf-8 -*-
# Add EV44 to the months already loaded under earlier rules (2025-01 to 2026-07) without rebuilding them: a month rebuilt from the extract
# differs from what is loaded for reasons unrelated to EV44, so the EV44 accounts are added to the bucket rows as they stand.
# Each month is applied once (logged) and checked afterwards: the RT10 total must rise by exactly the EV44 kWh.
import csv, io, json, os, sys, requests, truststore
truststore.inject_into_ssl(); csv.field_size_limit(10 ** 9)
HERE = r'C:\Projects\Sales_Platform\analysis'
env = {}
for l in io.open(HERE + r'\.env', encoding='utf-8'):
    if '=' in l and not l.startswith('#'): k, v = l.strip().split('=', 1); env[k] = v.strip('"')
BASE = env['SUPABASE_URL'] + '/rest/v1/jps_actuals'
H = {'apikey': env['SUPABASE_SERVICE_ROLE_KEY'], 'Authorization': 'Bearer ' + env['SUPABASE_SERVICE_ROLE_KEY'], 'Content-Type': 'application/json'}
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
LOG = HERE + r'\_ev44_delta_log.json'; done = json.load(open(LOG)) if os.path.exists(LOG) else {}
num = lambda s: float(s) if s not in ('', None) else 0.0
def bucket(k):
    if k < 0: return '<Zero'
    if k == 0: return 'Zero'
    if k < 150: return '<150'
    if k < 350: return '150>350'
    if k < 550: return '350>550'
    if k < 750: return '550>750'
    if k <= 950: return '750>950'
    return 'over 950'
def ev_rows(y, m):
    f = HERE + r'\%s %02d.csv' % (MON[m - 1], y - 2000)
    rd = csv.reader(io.open(f, encoding='utf-8', errors='replace')); h = next(rd); ix = {n: i for i, n in enumerate(h)}; out = {}
    for r in rd:
        if len(r) < 40 or r[ix['Srat_Code']] != 'EV44': continue
        k = num(r[ix['net_kwh_billed_consump']]); b = out.setdefault(bucket(k), [0, 0.0, 0.0]); b[0] += 1; b[1] += k; b[2] += num(r[ix['net_revenue']])
    return out
def rows(y, m):
    r = requests.get(BASE, headers=H, params={'year': 'eq.%d' % y, 'month': 'eq.%d' % m, 'rate_class': 'eq.RT10', 'parish': 'eq.ALL', 'select': 'id,consumption_bucket,kwh,revenue_jmd,customer_count'}, timeout=120); r.raise_for_status(); return r.json()
def total(y, m): return sum(x['kwh'] or 0 for x in rows(y, m) if x['consumption_bucket'] != 'Prepaid')
months = [(2025, m) for m in range(1, 13)] + [(2026, m) for m in range(1, 8)]
for y, m in months:
    key = '%d-%02d' % (y, m)
    if key in done: print(key, 'already applied'); continue
    ev = ev_rows(y, m); exp = sum(v[1] for v in ev.values()); before = total(y, m); R = {x['consumption_bucket']: x for x in rows(y, m) if x['consumption_bucket'] != 'Prepaid'}
    if any(b not in R for b in ev): print(key, 'MISSING BUCKET ROW', [b for b in ev if b not in R]); continue
    for b, (n, k, rv) in ev.items():
        x = R[b]; body = {'kwh': round((x['kwh'] or 0) + k, 2), 'revenue_jmd': round((x['revenue_jmd'] or 0) + rv, 2), 'customer_count': (x['customer_count'] or 0) + n}
        p = requests.patch(BASE, headers={**H, 'Prefer': 'return=minimal'}, params={'id': 'eq.%d' % x['id']}, data=json.dumps(body), timeout=120); p.raise_for_status()
    after = total(y, m); ok = abs((after - before) - exp) < 1.0
    print(key, 'EV44 %.1f kWh in %d rows | RT10 %.4f -> %.4f GWh | %s' % (exp, sum(v[0] for v in ev.values()), before / 1e6, after / 1e6, 'OK' if ok else 'CHECK FAILED'), flush=True)
    done[key] = {'kwh': exp, 'ok': ok}; json.dump(done, open(LOG, 'w'))
