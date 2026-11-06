# -*- coding: utf-8 -*-
# October 2026 billing extract scan for large accounts: billed-consumption adjustments, repeats of September, negatives, big swings.
import csv, io, collections, sys, json, requests
import truststore; truststore.inject_into_ssl()
HERE = r'C:\Projects\Sales_Platform\analysis'
env = {}
for l in io.open(HERE + r'\.env', encoding='utf-8'):
    if '=' in l and not l.startswith('#'):
        k, v = l.strip().split('=', 1); env[k] = v.strip('"')
H = {'apikey': env['SUPABASE_SERVICE_ROLE_KEY'], 'Authorization': 'Bearer ' + env['SUPABASE_SERVICE_ROLE_KEY']}
kam = {}; off = 0
while True:
    r = requests.get(env['SUPABASE_URL'] + '/rest/v1/jps_kam', headers={**H, 'Range': '%d-%d' % (off, off + 999)}, params={'select': 'jps_ac,kam'}, timeout=60); d = r.json()
    for x in d: kam[x['jps_ac'].split('-')[0]] = x['kam']
    if len(d) < 1000: break
    off += 1000

def scan(fn):
    acc = {}
    rd = csv.reader(io.open(fn, encoding='utf-8', errors='replace')); h = next(rd); ix = {n: i for i, n in enumerate(h)}
    f = lambda row, n: row[ix[n]] if ix[n] < len(row) else ''
    num = lambda s: float(s) if s not in ('', None) else 0.0
    for row in rd:
        if len(row) < 40: continue
        k = f(row, 'Cust_Code') + '-' + f(row, 'Prem_Code')
        a = acc.setdefault(k, {'name': f(row, 'Name'), 'rc': f(row, 'Srat_Code'), 'gross': 0.0, 'adj': 0.0, 'net': 0.0, 'rev': 0.0, 'radj': 0.0, 'n': 0, 'status': f(row, 'Account_Status'), 'parish': f(row, 'Parish'), 'mult': f(row, 'multilpier')})
        a['gross'] += num(f(row, 'kwh_billed_consump')); a['adj'] += num(f(row, 'kwh_billed_consump_adj')); a['net'] += num(f(row, 'net_kwh_billed_consump'))
        a['rev'] += num(f(row, 'net_revenue')); a['radj'] += num(f(row, 'revenue_adj')); a['n'] += 1
    return acc
oc = scan(HERE + r'\Oct 26.csv'); sp = scan(HERE + r'\Sep 26.csv')
json.dump({'oct': oc, 'sep': sp}, open(HERE + r'\_oct_anomaly_scan.json', 'w'))
print('accounts oct', len(oc), 'sep', len(sp))
