# -*- coding: utf-8 -*-
# Python port of the Sales Platform Driver Forecast chain (JPS_Sales_Platform_v1.html: _dfcComputeChain etc.)
# for FY2026 commercial classes (RT20, RT40, RT50, RT60-ST, RT70). asof = 9 (Jan-Sep actual), Oct-Dec forecast.
import json, collections
D = json.load(open('pull.json'))
Y, ASOF = 2026, 9
PLACE = {'Postpaid', 'Zero-Postpaid'}
KAMUSER = 'Jordache Wilson'

def kl(m, ac):
    return m.get(ac) or m.get(str(ac or '').split('-')[0]) or ''
kamMap = {str(k['jps_ac']).strip(): k['kam'] or '' for k in D['kam']}
indMap = {str(k['jps_ac']).strip(): k['industry'] or '' for k in D['ind']}

MAC = {}
for r in D['macro']:
    MAC.setdefault((r['driver_type'], r['segment'] or None, int(r['year']), int(r['month'])), float(r['value_pct'] or 0))
def macro(t, seg, y, m): return MAC.get((t, seg or None, y, m), 0.0)
def segment(rc): return 'residential' if rc in ('RT10', 'RT20') else 'commercial'

OPA = collections.defaultdict(list)
for r in D['opadj']:
    OPA[(int(r['year']), int(r['month']))].append(r)
def opadj(ac, y, m):
    for r in OPA.get((y, m), []):
        rac = str(r['jps_ac'] or '')
        if rac == ac or rac == str(ac).split('-')[0] or str(ac) == rac.split('-')[0]:
            return float(r['operational_pct'] or 0), float(r['manual_kwh'] or 0)   # first match wins, as .find()
    return 0.0, 0.0

NORM_EXCLUDE = {'302571-686496'}
def drivers(rc, industry, y, m, opac):
    seg = segment(rc)
    mac = macro('macro', rc, y, m) or macro('macro', seg, y, m)
    wea = macro('weather', None, y, m)
    sea = 0.0 if seg == 'residential' else (macro('industry', industry, y, m) if industry else 0.0)   # residential seasonality gated to y>FC_BUD_YEAR
    return mac, wea, sea     # norm / migration / solar are 0 for y == FC_BUD_YEAR
def chain(act, rc, industry, opac, newc=None):
    """act: {(y,m):kwh}. returns {m: dict(total, base, drivers...)}"""
    tot = {m: {'total': act.get((Y, m), 0.0), 'actual': True} for m in range(1, ASOF + 1)}
    for m in range(ASOF + 1, 13):
        if newc:
            base = 0.0 if (Y, m) < (newc['sy'], newc['sm']) else newc['kwh']
        else:
            terms = [tot[m - k]['total'] for k in (1, 2, 3) if m - k >= 1]
            base = sum(terms) / len(terms) if terms else 0.0
        mac, wea, sea = drivers(rc, industry, Y, m, opac)
        op_pct, op_kwh = opadj(opac, Y, m) if opac else (0.0, 0.0)
        s = max(-100, mac + wea + sea + op_pct)
        tot[m] = {'total': base * (1 + s / 100) + op_kwh, 'actual': False, 'base': base, 'macro': mac, 'weather': wea, 'industry': sea, 'oper': op_pct, 'manual': op_kwh, 'drv': s}
    return tot
