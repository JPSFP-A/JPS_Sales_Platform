# -*- coding: utf-8 -*-
# KAM round data: rebuilt 7 Sep forecast (as of August close) vs September actual, live forecast, adjustment register and effects.
import json, re, collections
d = json.load(open('pull.json'))
A8 = json.load(open('kam_run_asof8.json'))      # rebuilt forecast as at 7 Sep (Aug close), adjustments on file then
LIVE = json.load(open('kam_run_live2.json'))      # live forecast, September actual loaded, all adjustments
NOOP = json.load(open('kam_run_noop_new.json'))      # live, no adjustments
kamMap = {str(k['jps_ac']).strip(): k['kam'] for k in d['kam']}
def kam_of(ac):
    return kamMap.get(ac) or kamMap.get(str(ac).split('-')[0]) or ''
def norm(n):
    return re.sub(r'[^a-z0-9 ]', '', (n or '').lower()).strip()
KAMS = ['Simone Chisholm', 'Nicole Watson', 'Tanya Williams', 'Anna-Kay Toyloy', 'Sheryl Davis', 'Ewan Pitter', 'Sharmica Holness', 'Ruel Barnett', 'Kenroy Williams', 'Jean Waugh-Evans']
def idx(run): return {a['ac']: a for a in run['accts']}
I8, IL, IN = idx(A8), idx(LIVE), idx(NOOP)
G = 1e6
accts = {}
for ac, a in IL.items():
    k = kam_of(ac)
    if not k and not ac.startswith('NEW'): continue
    f8 = I8.get(ac); nop = IN.get(ac)
    accts[ac] = dict(ac=ac, name=a['name'], rc=a['rc'], ind=a.get('ind') or '', kam=k,
        sep_act=a['k']['2026'][8] / G, sep_fc=(f8['k']['2026'][8] / G) if f8 else 0.0,
        live={y: [v / G for v in a['k'][y]] for y in ('2026', '2027', '2028')},
        prev={y: ([v / G for v in f8['k'][y]] if f8 else [0.0] * 12) for y in ('2026', '2027', '2028')},
        noop={y: ([v / G for v in nop['k'][y]] if nop else [0.0] * 12) for y in ('2026', '2027', '2028')})
# adjustments
USERKAM = {'srholness': 'Sharmica Holness', 'nwatson': 'Nicole Watson', 'jwaugh': 'Jean Waugh-Evans', 'shdavis': 'Sheryl Davis', 'kenwilliams': 'Kenroy Williams',
           'atoyloy': 'Anna-Kay Toyloy', 'tawilliams': 'Tanya Williams', 'Simone Chisholm': 'Simone Chisholm'}
CACHE_NAMES = json.load(open('../_kam_register_cache.json', encoding='utf-8')).get('names', {})
adj = []
for o in d['opadj']:
    ac = o['jps_ac']; k = kam_of(ac)
    by = USERKAM.get(o['created_by'])
    nm = ''
    if ac in accts: nm = accts[ac]['name']
    elif ac in CACHE_NAMES: nm = CACHE_NAMES[ac]
    adj.append(dict(ac=ac, name=nm, kam=k, year=int(o['year']), month=int(o['month']), pct=float(o['operational_pct'] or 0), kwh=float(o['manual_kwh'] or 0),
                    reason=o.get('reason_code') or '', just=o.get('justification') or '', by=('KAM' if by else 'Sales Forecasting'), by_name=by or '', created=str(o['created_at'])[:10]))
if __name__ == '__main__':
    print('accounts', len(accts), 'adjustments', len(adj))
    print('no-kam adjustments (no effect):', sum(1 for a in adj if not a['kam']))
    print('by source', collections.Counter(a['by'] for a in adj))
    up = [a for a in adj if (a['year'], a['month']) >= (2026, 10)]
    print('upcoming (Oct 2026 onward)', len(up), 'accounts', len({a['ac'] for a in up}), collections.Counter(a['kam'] for a in up))
    print('past (before Oct 2026)', len(adj) - len(up))
    tot = collections.defaultdict(lambda: dict(f=0, a=0, abs=0, n=0))
    for a in accts.values():
        t = tot[a['kam']]; t['f'] += a['sep_fc']; t['a'] += a['sep_act']; t['abs'] += abs(a['sep_act'] - a['sep_fc']); t['n'] += 1
    for k in KAMS:
        t = tot[k]; print(k, 'fc', round(t['f'], 2), 'act', round(t['a'], 2), 'net acc', round(1 - abs(t['a'] - t['f']) / t['a'], 3), 'acct acc', round(1 - t['abs'] / t['a'], 3), t['n'])
    T = lambda key: sum(t[key] for k, t in tot.items() if k in KAMS)
    print('TOTAL fc', round(T('f'), 1), 'act', round(T('a'), 1), 'acct acc', round(1 - T('abs') / T('a'), 3))
