# -*- coding: utf-8 -*-
# Evidence for the residential, net billing and EV sections of the driver report.
# Registered net billers (NB10/NB20/NB40) and EV44 come from the monthly billing extracts; prepaid from jps_actuals.
import csv, io, glob, json, requests, truststore
truststore.inject_into_ssl(); csv.field_size_limit(10 ** 9)
HERE = r'C:\Projects\Sales_Platform\analysis'
env = {}
for l in io.open(HERE + r'\.env', encoding='utf-8'):
    if '=' in l and not l.startswith('#'): k, v = l.strip().split('=', 1); env[k] = v.strip('"')
H = {'apikey': env['SUPABASE_SERVICE_ROLE_KEY'], 'Authorization': 'Bearer ' + env['SUPABASE_SERVICE_ROLE_KEY']}
MON = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
num = lambda s: float(s) if s not in ('', None) else 0.0
nb, ev = [], []
for f in sorted(glob.glob(HERE + r'\[A-Z][a-z][a-z] [0-9][0-9].csv')):
    base = f.split('\\')[-1]; y = 2000 + int(base[4:6]); m = MON[base[:3]]
    rd = csv.reader(io.open(f, encoding='utf-8', errors='replace')); h = next(rd); ix = {n: i for i, n in enumerate(h)}
    c = {s: [0, 0.0, 0.0, 0.0] for s in ('NB10', 'NB20', 'NB40')}; e = [0, 0, 0.0]; accts = set()
    for r in rd:
        if len(r) < 40: continue
        s = r[ix['Srat_Code']]
        if s in c and r[ix['cust_billed']] == '1':
            a = c[s]; a[0] += 1; a[1] += num(r[ix['net_kwh_billed_consump']]); a[2] += num(r[ix['KWHE_Billed_consump']]); a[3] += num(r[ix['Net_Billing_Adj']])
        elif s == 'EV44':
            e[0] += 1; k = num(r[ix['net_kwh_billed_consump']]); e[2] += k
            if k != 0: accts.add(r[ix['Cust_Code']] + '-' + r[ix['Prem_Code']])
    e[1] = len(accts)
    nb.append([y, m, {s: v for s, v in c.items()}]); ev.append([y, m, e[0], e[1], e[2]])
    print(y, m, flush=True)
rows = []; off = 0
while True:
    r = requests.get(env['SUPABASE_URL'] + '/rest/v1/jps_actuals', headers={**H, 'Range-Unit': 'items', 'Range': '%d-%d' % (off, off + 999)},
                     params={'rate_class': 'eq.RT10', 'consumption_bucket': 'eq.Prepaid', 'year': 'gte.2025', 'select': 'year,month,kwh,customer_count'}, timeout=120)
    r.raise_for_status(); d = r.json(); rows += d
    if len(d) < 1000: break
    off += 1000
pp = {}
for x in rows: k = (x['year'], x['month']); a = pp.setdefault(k, [0.0, 0]); a[0] += x['kwh'] or 0; a[1] += x['customer_count'] or 0
json.dump({'nb': sorted(nb), 'ev': sorted(ev), 'pp': [[k[0], k[1], v[0], v[1]] for k, v in sorted(pp.items())]}, open(HERE + r'\_driver_res_evidence.json', 'w'))
print('saved')
