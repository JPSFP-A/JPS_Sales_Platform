# -*- coding: utf-8 -*-
# October 2026 KAM forecast accuracy. Forecast = the Driver Forecast as it stood after the September close (the platform engine before the
# roll-forward change, actuals through September, every adjustment on file), account level for KAM-assigned accounts. Actual = October billing per account.
# Net accuracy = 1 - |actual - forecast| / actual on the KAM total. Account-level accuracy = 1 - sum of account misses / actual.
import json, re, collections
G = 1e6
d = json.load(open('pull_oct.json'))
R9 = json.load(open('kam_run_asof9.json'))
kamMap = {str(k['jps_ac']).strip(): k['kam'] for k in d['kam']}
def kam_of(ac): return kamMap.get(ac) or kamMap.get(str(ac).split('-')[0]) or ''
def norm(n): return re.sub(r'[^a-z0-9 ]', '', (n or '').lower()).strip()
KAMS = ['Simone Chisholm', 'Nicole Watson', 'Tanya Williams', 'Anna-Kay Toyloy', 'Sheryl Davis', 'Ewan Pitter', 'Sharmica Holness', 'Ruel Barnett', 'Kenroy Williams', 'Jean Waugh-Evans']
act = collections.defaultdict(float); nm = {}; rcs = {}
for r in d['act']:
    if r['jps_ac'] and r['year'] == 2026 and r['month'] == 10:
        act[r['jps_ac']] += float(r['kwh'] or 0); nm[r['jps_ac']] = r['name']; rcs[r['jps_ac']] = r['rate_class']
fc = {a['ac']: a for a in R9['accts']}
sep_act = collections.defaultdict(float)
for r in d['act']:
    if r['jps_ac'] and r['year'] == 2026 and r['month'] == 9: sep_act[r['jps_ac']] += float(r['kwh'] or 0)

adj_oct = collections.defaultdict(list)
for o in d['opadj']:
    if int(o['year']) == 2026 and int(o['month']) == 10:
        adj_oct[o['jps_ac']].append((float(o['operational_pct'] or 0), float(o['manual_kwh'] or 0), o.get('reason_code') or '', (o.get('justification') or '').strip()))

A = {}
for ac in set(fc) | set(act):
    if '|' in str(ac): continue
    k = kam_of(ac)
    if not k and not str(ac).startswith('NEW'): continue
    f = fc.get(ac)
    A[ac] = dict(ac=ac, kam=k, name=(f['name'] if f else nm.get(ac, '')), rc=(f['rc'] if f else rcs.get(ac, '')), fc=(f['k']['2026'][9] / G if f else 0.0), act=act.get(ac, 0.0) / G,
                 sep_act=sep_act.get(ac, 0.0) / G, adj=adj_oct.get(ac, []))
for a in A.values(): a['miss'] = a['act'] - a['fc']

def summarise(L):
    f = sum(a['fc'] for a in L); x = sum(a['act'] for a in L); ab = sum(abs(a['miss']) for a in L)
    return dict(n=len(L), fc=f, act=x, net=(1 - abs(x - f) / x) if x else 0, acct=(1 - ab / x) if x else 0, abs=ab, var=x - f)
BYK = {k: summarise([a for a in A.values() if a['kam'] == k]) for k in KAMS}
TOTAL = summarise([a for a in A.values() if a['kam'] in KAMS])
MISSES = sorted([a for a in A.values() if a['kam'] in KAMS], key=lambda a: -abs(a['miss']))
if __name__ == '__main__':
    print('accounts', len(A), '| KAM accounts', sum(1 for a in A.values() if a['kam'] in KAMS), '| not in a named KAM', sum(1 for a in A.values() if a['kam'] and a['kam'] not in KAMS))
    for k in KAMS:
        s = BYK[k]; print('%-18s n=%4d fc %7.2f act %7.2f var %+6.2f net %.3f acct %.3f' % (k, s['n'], s['fc'], s['act'], s['var'], s['net'], s['acct']))
    s = TOTAL; print('TOTAL n=%d fc %.2f act %.2f var %+.2f net %.3f acct %.3f abs %.2f' % (s['n'], s['fc'], s['act'], s['var'], s['net'], s['acct'], s['abs']))
    print('top 5 share of abs miss: %.3f' % (sum(abs(a['miss']) for a in MISSES[:5]) / s['abs']))
    for a in MISSES[:12]: print('%-10s %-34s %-7s fc %6.3f act %6.3f miss %+6.3f adj %s' % (a['kam'][:10], (a['name'] or '')[:34], a['rc'], a['fc'], a['act'], a['miss'], a['adj'][:1]))
