# -*- coding: utf-8 -*-
import json, io, requests
import truststore; truststore.inject_into_ssl()
HERE = r'C:\Projects\Sales_Platform\analysis'
d = json.load(open(HERE + r'\_oct_anomaly_scan.json')); oc, sp = d['oct'], d['sep']
env = {}
for l in io.open(HERE + r'\.env', encoding='utf-8'):
    if '=' in l and not l.startswith('#'):
        k, v = l.strip().split('=', 1); env[k] = v.strip('"')
H = {'apikey': env['SUPABASE_SERVICE_ROLE_KEY'], 'Authorization': 'Bearer ' + env['SUPABASE_SERVICE_ROLE_KEY']}
kam = {}; off = 0
while True:
    r = requests.get(env['SUPABASE_URL'] + '/rest/v1/jps_kam', headers={**H, 'Range': '%d-%d' % (off, off + 999)}, params={'select': 'jps_ac,kam'}, timeout=60); x = r.json()
    for y in x: kam[y['jps_ac'].split('-')[0]] = y['kam']
    if len(x) < 1000: break
    off += 1000
K = lambda ac: kam.get(ac.split('-')[0], '')
nm = lambda a: a['name'][:30]
print('=== A. consumption adjustments in October (kwh_billed_consump_adj), |adj| >= 1,000 kWh')
A = [(k, a) for k, a in oc.items() if abs(a['adj']) >= 1000]
print('accounts', len(A), 'net adj kWh', round(sum(a['adj'] for k, a in A)), ' gross total', round(sum(a['gross'] for a in oc.values())), 'net total', round(sum(a['net'] for a in oc.values())))
for k, a in sorted(A, key=lambda kv: -abs(kv[1]['adj']))[:18]:
    s = sp.get(k, {}); print('%-16s %-30s %-6s adj %12.0f gross %12.0f net %12.0f | Sep net %12.0f | %s' % (k, nm(a), a['rc'], a['adj'], a['gross'], a['net'], s.get('net', float('nan')), K(k)))
print('Sep adjustments for comparison: accounts', len([1 for a in sp.values() if abs(a['adj']) >= 1000]), 'net adj', round(sum(a['adj'] for a in sp.values() if abs(a['adj']) >= 1000)))
print('\n=== B. large accounts (>=20,000 kWh both months) billed exactly the same gross kWh as September')
B = [(k, a) for k, a in oc.items() if a['gross'] >= 20000 and k in sp and abs(a['gross'] - sp[k]['gross']) < 0.5]
print(len(B), 'accounts', round(sum(a['gross'] for k, a in B)), 'kWh')
for k, a in sorted(B, key=lambda kv: -kv[1]['gross'])[:15]: print('%-16s %-30s %-6s %12.0f %s' % (k, nm(a), a['rc'], a['gross'], K(k)))
print('\n=== C. negative net kWh, |kWh| >= 100')
C = [(k, a) for k, a in oc.items() if a['net'] <= -100]
print(len(C), 'accounts', round(sum(a['net'] for k, a in C)))
for k, a in sorted(C, key=lambda kv: kv[1]['net'])[:12]: print('%-16s %-30s %-6s net %10.0f gross %10.0f Sep %10.0f %s' % (k, nm(a), a['rc'], a['net'], a['gross'], sp.get(k, {}).get('net', float('nan')), K(k)))
print('\n=== D. biggest swings, large accounts (>=50,000 kWh either month), net kWh Oct vs Sep')
D = []
for k in set(oc) | set(sp):
    o = oc.get(k, {}).get('net', 0.0); s = sp.get(k, {}).get('net', 0.0)
    if max(abs(o), abs(s)) >= 50000: D.append((k, o, s, o - s, (oc.get(k) or sp.get(k))))
D.sort(key=lambda t: t[3])
print('count', len(D), 'net change', round(sum(t[3] for t in D)))
print('-- down'); [print('%-16s %-30s %-6s Oct %11.0f Sep %11.0f chg %11.0f %s' % (t[0], nm(t[4]), t[4]['rc'], t[1], t[2], t[3], K(t[0]))) for t in D[:14]]
print('-- up'); [print('%-16s %-30s %-6s Oct %11.0f Sep %11.0f chg %11.0f %s' % (t[0], nm(t[4]), t[4]['rc'], t[1], t[2], t[3], K(t[0]))) for t in D[::-1][:14]]
print('\n=== E. appeared / disappeared (>=20,000 kWh)')
new = [(k, a) for k, a in oc.items() if a['net'] >= 20000 and (k not in sp or sp[k]['net'] <= 100)]
gone = [(k, a) for k, a in sp.items() if a['net'] >= 20000 and (k not in oc or oc[k]['net'] <= 100)]
print('new/restarted', len(new), round(sum(a['net'] for k, a in new)), '| dropped to ~zero', len(gone), round(sum(a['net'] for k, a in gone)))
for k, a in sorted(new, key=lambda kv: -kv[1]['net'])[:8]: print('  NEW  %-16s %-30s %-6s %11.0f %s' % (k, nm(a), a['rc'], a['net'], K(k)))
for k, a in sorted(gone, key=lambda kv: -kv[1]['net'])[:10]: print('  GONE %-16s %-30s %-6s Sep %11.0f Oct %11.0f %s' % (k, nm(a), a['rc'], a['net'], oc.get(k, {}).get('net', float('nan')), K(k)))
print('\n=== F. revenue adjustments |J$| >= 10M in the billing extract')
for k, a in sorted(oc.items(), key=lambda kv: -abs(kv[1]['radj']))[:10]:
    if abs(a['radj']) >= 10e6: s = sp.get(k, {}); print('%-16s %-30s %-6s radj %14.0f net rev %14.0f kWh net %11.0f | Sep radj %14.0f %s' % (k, nm(a), a['rc'], a['radj'], a['rev'], a['net'], s.get('radj', 0), K(k)))
