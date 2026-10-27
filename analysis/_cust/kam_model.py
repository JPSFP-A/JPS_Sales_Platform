# -*- coding: utf-8 -*-
# Shared numbers for the KAM round deck and workbook.
import json, re, collections
from kam_data import *

MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
MINUS = '−'
def t_label(t):
    return '%s %s' % (MON[(t - 1) % 12], str(2026 + (t - 1) // 12)[2:])
def rng(ms):
    ms = sorted(set(ms)); out = []; s = p = ms[0]
    for x in ms[1:]:
        if x == p + 1: p = x; continue
        out.append((s, p)); s = p = x
    out.append((s, p))
    return ', '.join(t_label(a) if a == b else '%s to %s' % (t_label(a), t_label(b)) for a, b in out)

# FY2025 actual by KAM and customer
FY25 = collections.defaultdict(float)
for r in d['act']:
    if r['year'] == 2025 and r['jps_ac']:
        FY25[r['jps_ac']] += float(r['kwh'] or 0) / G
for r in json.load(open('pull_nc.json'))['act_nc']:
    pass
for ac, a in accts.items():
    a['fy25'] = FY25.get(ac, 0.0)

def fy(a, y, key='live'): return sum(a[key][y])
effect = {ac: [fy(a, y, 'live') - fy(a, y, 'noop') for y in ('2026', '2027', '2028')] for ac, a in accts.items()}

# KAM portfolio
PORT = {}
for k in KAMS:
    L = [a for a in accts.values() if a['kam'] == k]
    P = dict(accounts=len(L), customers=len({norm(a['name']) for a in L if not a['ac'].startswith('NEW')}),
             fy25=sum(a['fy25'] for a in L),
             live=[sum(fy(a, y) for a in L) for y in ('2026', '2027', '2028')],
             prev=[sum(fy(a, y, 'prev') for a in L) for y in ('2026', '2027', '2028')],
             sep_fc=sum(a['sep_fc'] for a in L), sep_act=sum(a['sep_act'] for a in L),
             sep_abs=sum(abs(a['sep_act'] - a['sep_fc']) for a in L))
    PORT[k] = P
KAMS_SORTED = sorted(KAMS, key=lambda k: -PORT[k]['live'][1])
TOT = dict(accounts=sum(p['accounts'] for p in PORT.values()), fy25=sum(p['fy25'] for p in PORT.values()),
           live=[sum(p['live'][i] for p in PORT.values()) for i in range(3)], prev=[sum(p['prev'][i] for p in PORT.values()) for i in range(3)],
           sep_fc=sum(p['sep_fc'] for p in PORT.values()), sep_act=sum(p['sep_act'] for p in PORT.values()), sep_abs=sum(p['sep_abs'] for p in PORT.values()))
def net_acc(f, a): return 1 - abs(a - f) / a if a else 0.0
def acct_acc(ab, a): return 1 - ab / a if a else 0.0

# account misses
MISSES = sorted(accts.values(), key=lambda a: -abs(a['sep_act'] - a['sep_fc']))

# customers (KAM + normalised name)
CUST = {}
for a in accts.values():
    if not a['kam']: continue
    key = (a['kam'], norm(a['name']) or a['ac'])
    c = CUST.setdefault(key, dict(kam=a['kam'], name=a['name'], accounts=[], rcs=set(), ind=a['ind']))
    c['accounts'].append(a['ac']); c['rcs'].add(a['rc'])
for key, c in CUST.items():
    A = [accts[ac] for ac in c['accounts']]
    c['fy25'] = sum(a['fy25'] for a in A)
    c['live'] = [sum(fy(a, y) for a in A) for y in ('2026', '2027', '2028')]
    c['prev'] = [sum(fy(a, y, 'prev') for a in A) for y in ('2026', '2027', '2028')]
    c['eff'] = [sum(effect[ac][i] for ac in c['accounts']) for i in range(3)]

# adjustments grouped by account / pattern
grp = collections.OrderedDict()
for a in adj:
    key = (a['ac'], a['pct'], a['kwh'], a['reason'], a['just'], a['by'])
    t = (a['year'] - 2026) * 12 + a['month']
    grp.setdefault(key, dict(a=a, ms=[]))['ms'].append(t)
GADJ = []
for key, g in grp.items():
    a = g['a']; ms = g['ms']
    GADJ.append(dict(a, months=rng(ms), first=min(ms), last=max(ms), n=len(ms)))
UPCOMING = [g for g in GADJ if g['last'] >= 10]
def fmt_pct(p):
    q = ('%.0f' if abs(p) >= 10 else '%.1f') % abs(p)
    return ('+' if p > 0 else MINUS) + q + '%'
def adj_text(g):
    v = fmt_pct(g['pct']) if g['pct'] else ''
    if g['kwh']: v = (v + ', ' if v else '') + (format(g['kwh'], '+,.0f') + ' kWh').replace('-', MINUS)
    return '%s, %s' % (v, g['months'])

def cust_adjustments(kam):
    out = collections.OrderedDict()
    for g in UPCOMING:
        if g['kam'] != kam: continue
        nm = g['name'] or g['ac']
        k = norm(nm) or g['ac']
        c = out.setdefault(k, dict(name=nm, accounts=set(), items=[], reasons=set(), by=set()))
        c['accounts'].add(g['ac']); c['reasons'].add(g['reason'] or 'Not stated'); c['by'].add(g['by'])
        txt = adj_text(g)
        if txt not in c['items']: c['items'].append(txt)
    for k, c in out.items():
        c['eff27'] = sum(effect[ac][1] for ac in c['accounts'] if ac in effect)
        c['eff28'] = sum(effect[ac][2] for ac in c['accounts'] if ac in effect)
    return sorted(out.values(), key=lambda c: -abs(c['eff27']))

# how each adjustment applies on the roll-forward engine
ROLLS = {'Confirmed defection', 'Possible defection', 'Expansion', 'Renewal', 'Win-back'}
for g in GADJ:
    g['kind'] = 'No value' if not (g['pct'] or g['kwh']) else ('Rolls forward' if g['reason'] in ROLLS else 'Month only')
    if g['kind'] == 'Rolls forward': g['months'] = 'from ' + t_label(g['first'])
def kind_customers(kind):
    out = collections.OrderedDict()
    for g in GADJ:
        if g['kind'] != kind or not g['kam']: continue
        k = (g['kam'], norm(g['name']) or g['ac'])
        c = out.setdefault(k, dict(kam=g['kam'], name=g['name'] or g['ac'], accounts=set(), items=[], reasons=set(), first=g['first'], last=g['last'], by=set()))
        c['accounts'].add(g['ac']); c['reasons'].add(g['reason'] or 'Not stated'); c['by'].add(g['by'])
        c['first'] = min(c['first'], g['first']); c['last'] = max(c['last'], g['last'])
        tx = adj_text(g)
        if tx not in c['items']: c['items'].append(tx)
    for c in out.values():
        c['eff'] = [sum(effect[ac][i] for ac in c['accounts'] if ac in effect) for i in range(3)]
    return list(out.values())
ROLL_CUST = sorted(kind_customers('Rolls forward'), key=lambda c: -abs(c['eff'][2]))
OP_CUST = sorted(kind_customers('Month only'), key=lambda c: -abs(c['eff'][0]))

PIPE = [dict(name=n['name'], kam=n.get('kam') or '', rc=n['rate_class'], parish=n.get('parish') or '', ind=n.get('industry') or '',
             start='%s %d' % (MON[int(n['start_month']) - 1], int(n['start_year'])), kwh=float(n['expected_kwh'] or 0), by=n.get('created_by') or '')
        for n in d['newc']]

if __name__ == '__main__':
    print('customers', len(CUST), 'upcoming groups', len(UPCOMING))
    print('TOT live', [round(v, 1) for v in TOT['live']], 'prev', [round(v, 1) for v in TOT['prev']], 'fy25', round(TOT['fy25'], 1))
    print('net acc', round(net_acc(TOT['sep_fc'], TOT['sep_act']), 3), 'acct', round(acct_acc(TOT['sep_abs'], TOT['sep_act']), 3))
    print('top 5 misses share of abs', round(sum(abs(a['sep_act'] - a['sep_fc']) for a in MISSES[:5]) / TOT['sep_abs'], 3), 'accounts with miss>0.05', sum(1 for a in MISSES if abs(a['sep_act'] - a['sep_fc']) > 0.05))
    for k in KAMS_SORTED: print(k, PORT[k]['customers'], PORT[k]['accounts'], [round(v, 1) for v in PORT[k]['live']], round(PORT[k]['fy25'], 1))
    for k in KAMS_SORTED[:3]:
        for c in cust_adjustments(k)[:3]: print(k, '|', c['name'], c['items'][:2], round(c['eff27'], 2))
    print('rolling customers', len(ROLL_CUST), 'month-only customers', len(OP_CUST))
