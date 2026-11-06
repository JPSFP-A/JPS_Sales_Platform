# -*- coding: utf-8 -*-
# Parish recovery tracker: year-on-year by month for every parish, residential (RT10) and commercial (RT20 to RT70), Jan to Oct 2026.
# Parish volumes come from the billing-file scan (corrected.json, parish grain, every month back to 2024) plus prepaid by parish from the database
# (2025 onward). Residential here is RT10; commercial is RT20 to RT70. Output: _parish_tracker.json and _parish_tracker.html (one A4 page).
import csv, json, os, sys, collections, requests
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '_cust'))
from db import BASE, H
f = lambda v: float(v or 0)
src = open('_build_onepagers.py', encoding='utf-8').read()
exec(src.split('# =====================================================================  SALES ONE-PAGER')[0])
def chg(x, d=1):
    s_ = f'{abs(x):.{d}f}'
    return s_ if round(x, d) == 0 else (('+' if x > 0 else MINUS) + s_)
def rpc(fn, body):
    r = requests.post(f'{BASE}/rest/v1/rpc/{fn}', headers={**H, 'Content-Type': 'application/json'}, data=json.dumps(body), timeout=300); r.raise_for_status(); return r.json()

cj = json.load(open('corrected.json')); L = cj['srat_legend']; ix = {n: i for i, n in enumerate(L)}; SEP = cj.get('sep', '||')
norm = lambda s: str(s).strip().upper(); RMAP = {}; RCMAP = {}
for r in list(csv.reader(open(r'C:\Users\jwilson\Downloads\Rate categorry Data mapping.csv', encoding='utf-8-sig')))[1:]:
    if len(r) >= 3: RMAP[norm(r[2])] = r[0]; RCMAP.setdefault(norm(r[1]), r[0])
title = lambda key: (lambda s, rc: RCMAP.get(norm(rc)) or RMAP.get(norm(s)) or 'Other')(*key.split(SEP, 1))
V = collections.defaultdict(float)          # (month, parish, seg) -> GWh
for mo, keys in cj['srat'].items():
    for key, pp in keys.items():
        t = title(key); seg = 'RES' if t == 'RT10' else ('COM' if t in ('RT20', 'RT40', 'RT50', 'RT60', 'RT60-ST', 'RT70') else None)
        if not seg: continue
        for pg, v in pp.items():
            pg2 = pg if pg not in ('UNMAPPED', 'Unknown County', '') else 'Other'
            V[(mo, pg2, seg)] += v[ix['kwh']] / 1e6
for x in rpc('get_res_actuals', {'year_cutoff': 2025}):
    if x['consumption_bucket'] == 'Prepaid':
        V[('%d-%02d' % (x['year'], x['month']), x['parish'], 'RES' if x['rate_class'] == 'RT10' else 'COM')] += f(x['kwh']) / 1e6
parishes = sorted({pg for (mo, pg, seg) in V if mo == '2026-10' and pg != 'Other'}, key=lambda p: -(V[('2026-10', p, 'RES')] + V[('2026-10', p, 'COM')]))
mos = ['2026-%02d' % m for m in range(1, 11)]
def yoy(pg, seg, m): a, b = V[(m, pg, seg)], V[(m.replace('2026', '2025'), pg, seg)]; return (a / b - 1) if b else None
def ytd(pg, seg, y): return sum(V[('%d-%02d' % (y, m), pg, seg)] for m in range(1, 11))
West = ['St. James', 'Westmoreland', 'Hanover', 'Trelawny', 'St. Elizabeth']
def row(pg, seg):
    series = [yoy(pg, seg, m) for m in mos]
    o24 = V[('2024-10', pg, seg)]; o26 = V[('2026-10', pg, seg)] - (V[('2026-10', pg, seg)] and 0)
    return dict(series=series, ytd=ytd(pg, seg, 2026) / ytd(pg, seg, 2025) - 1, gap_closed=(series[8] - series[0]) * 100 if series[0] is not None and series[8] is not None else None, oct26=V[('2026-10', pg, seg)])
T = {}
for seg in ('RES', 'COM'):
    T[seg] = {pg: row(pg, seg) for pg in parishes}
    T[seg]['__total'] = dict(series=[(sum(V[(m, p, seg)] for p in parishes) / sum(V[(m.replace('2026', '2025'), p, seg)] for p in parishes) - 1) for m in mos],
                              ytd=sum(ytd(p, seg, 2026) for p in parishes) / sum(ytd(p, seg, 2025) for p in parishes) - 1, oct26=sum(V[('2026-10', p, seg)] for p in parishes))
    T[seg]['__total']['gap_closed'] = (T[seg]['__total']['series'][8] - T[seg]['__total']['series'][0]) * 100
# October against October 2024 (postpaid only; no prepaid before 2025)
for seg in ('RES', 'COM'):
    for pg in parishes + ['__total']:
        ps = parishes if pg == '__total' else [pg]
        pre26 = sum(V[('2026-10', p, seg)] for p in ps); pre24 = sum(V[('2024-10', p, seg)] for p in ps)
        T[seg][pg]['vs24'] = None  # filled below from postpaid only
json.dump({'parishes': parishes, 'months': mos, 'T': T}, open('_parish_tracker.json', 'w'))

# postpaid-only October 2026 vs 2024 (same basis)
PP = collections.defaultdict(float)
for mo in ('2024-10', '2026-10'):
    for key, pp in cj['srat'][mo].items():
        t = title(key); seg = 'RES' if t == 'RT10' else ('COM' if t in ('RT20', 'RT40', 'RT50', 'RT60', 'RT60-ST', 'RT70') else None)
        if not seg: continue
        for pg, v in pp.items(): PP[(mo, pg if pg not in ('UNMAPPED', 'Unknown County', '') else 'Other', seg)] += v[ix['kwh']] / 1e6
vs24 = lambda pg, seg: (PP[('2026-10', pg, seg)] / PP[('2024-10', pg, seg)] - 1) if PP[('2024-10', pg, seg)] else None

def cell(v, tot=False):
    if v is None: return '<td>n/a</td>'
    if tot: return f'<td>{chg(v * 100, 0)}</td>'
    pct = v * 100; bg = '#DDEFDF' if pct >= 0 else ('#FFF0C8' if pct >= -10 else ('#F6D3D6' if pct >= -20 else '#EDB3B8'))
    return f'<td style="background:{bg}">{chg(pct, 0)}</td>'
def block(seg, name):
    hdr = ''.join(f'<th>{m[5:]}</th>' for m in mos)
    hdr = ''.join(f'<th>{n}</th>' for n in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct*'])
    rows = []
    for i, pg in enumerate(parishes + ['__total']):
        r = T[seg][pg]; lab = 'Total' if pg == '__total' else pg
        ps = parishes if pg == '__total' else [pg]
        v24 = (sum(PP[('2026-10', p, seg)] for p in ps) / sum(PP[('2024-10', p, seg)] for p in ps) - 1) if pg == '__total' else vs24(pg, seg)
        cls = 'tot' if pg == '__total' else ('alt' if i % 2 else '')
        west = ' style="color:#C00000"' if pg in West else ''
        rows.append(f'<tr class="{cls}"><td class="l"{west if cls != "tot" else ""}>{lab}{" (W)" if pg in West else ""}</td>' + ''.join(cell(v, pg == '__total') for v in r['series']) + f'<td>{r["oct26"]:.1f}</td><td>{chg(r["ytd"] * 100, 1)}%</td><td>{chg(r["gap_closed"], 0)}</td><td>{chg(v24 * 100, 1) + "%" if v24 is not None else "n/a"}</td></tr>')
    return f'<div class="sec">{name}: year on year by month, 2026 vs 2025</div><table class="t7"><tr><th class="l">Parish</th>{hdr}<th>Oct GWh</th><th>YTD</th><th>Gap closed<br>Jan to Sep (pts)</th><th>Oct vs<br>Oct 2024</th></tr>{"".join(rows)}</table>'

res_t, com_t = T['RES']['__total'], T['COM']['__total']
west_res = sum(V[('2026-10', p, 'RES')] for p in West) / sum(V[('2025-10', p, 'RES')] for p in West) - 1
east_res = sum(V[('2026-10', p, 'RES')] for p in parishes if p not in West) / sum(V[('2025-10', p, 'RES')] for p in parishes if p not in West) - 1
html = f'''<!doctype html><html><head><meta charset="utf-8"><title>JPS Parish Recovery Tracker October 2026</title><style>{CSS}
.top h1 {{ font-size: 18pt; }} .t7 td {{ padding: 0.6mm 0.6mm; font-size: 7.2pt; }} .t7 th {{ font-size: 6.6pt; padding: 0.8mm 0.4mm; }} .small {{ font-size: 7.2pt; color: {GREY}; margin-top: 1.2mm; }} .head {{ font-size: 11.5pt; margin: 2.4mm 0 2mm; }}
</style></head><body><div class="page">
<div class="top"><div><h1>Parish recovery tracker: October 2026</h1></div><div class="sub">Jamaica Public Service | page 2 of 7<br>Billed volume including prepaid, year on year</div></div>
<div class="head">Residential volumes are above last year in the east and centre and still below it in the west. The commercial gap sits in St James (hotels) and Clarendon (Alcoa).</div>
{block('RES', 'Residential (RT10)')}
<div style="height:3.2mm"></div>
{block('COM', 'Commercial (RT20 to RT70)')}
<div class="small">(W) marks the five hurricane-hit western parishes. *October 2025 includes the storm of 28 October, so October is flattered; the last column compares postpaid volume with October 2024, a clean year. Gap closed is September's year-on-year less January's, in percentage points. Colours: green at or above last year, amber to 10% below, light red 10 to 20% below, red over 20% below.</div>
<div class="box" style="margin-top:3mm"><div class="sec">What it shows</div><ul style="margin:0;padding-left:4mm;font-size:8.2pt">
<li><b>Residential, west:</b> {chg(west_res * 100, 1)}% on October 2025, against {chg(east_res * 100, 1)}% in the east and centre. Last October's base was already depressed in the west, so the gap is real.</li>
<li><b>Residential, all parishes:</b> January {chg(res_t["series"][0] * 100, 0)}%, September {chg(res_t["series"][8] * 100, 0)}%, October {chg(res_t["series"][9] * 100, 0)}% (flattered). Year to date {chg(res_t["ytd"] * 100, 1)}%.</li>
<li><b>The west has plateaued, not finished:</b> Westmoreland reached {chg(T['RES']['Westmoreland']['series'][6] * 100, 0)}% in July and has slipped to {chg(T['RES']['Westmoreland']['series'][9] * 100, 0)}%; Hanover is {chg(T['RES']['Hanover']['series'][9] * 100, 0)}% and St Elizabeth {chg(T['RES']['St. Elizabeth']['series'][9] * 100, 0)}%. St James commercial has sat between {chg(min(T['COM']['St. James']['series'][4:10]) * 100, 0)}% and {chg(max(T['COM']['St. James']['series'][4:10]) * 100, 0)}% since May, so hotels are not closing the gap on their own.</li>
<li><b>Commercial:</b> January {chg(com_t["series"][0] * 100, 0)}%, September {chg(com_t["series"][8] * 100, 0)}%, October {chg(com_t["series"][9] * 100, 0)}%. Year to date {chg(com_t["ytd"] * 100, 1)}%. Portmore's swings (−24, +22, −26, +5) are Caribbean Broilers' billing timing, not demand.</li></ul></div>
<div class="foot"><span><b>Jamaica Public Service</b> | Parish Recovery Tracker | October 2026</span><span>Prepaid is included in its parish from 2025.</span></div>
</div></body></html>'''
open('_parish_tracker.html', 'w', encoding='utf-8').write(html); print('wrote _parish_tracker.html')
for pg in parishes: print('%-14s RES Oct %+.1f%% Sep %+.1f%% Jan %+.1f%% ytd %+.1f%% | COM Oct %+.1f%% Sep %+.1f%% Jan %+.1f%% ytd %+.1f%%' % (pg, T['RES'][pg]['series'][9] * 100, T['RES'][pg]['series'][8] * 100, T['RES'][pg]['series'][0] * 100, T['RES'][pg]['ytd'] * 100, T['COM'][pg]['series'][9] * 100, T['COM'][pg]['series'][8] * 100, T['COM'][pg]['series'][0] * 100, T['COM'][pg]['ytd'] * 100))
