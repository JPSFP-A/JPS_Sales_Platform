# -*- coding: utf-8 -*-
# Sales Forecast Driver Report, September 2026 close: FY2026 to FY2028 with the market, weather and commercial explanation for each year.
# FY2026, FY2027 and FY2028 totals are held at the financials (3,299.7 / 3,439.5 / 3,514.7 GWh).
import json, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
CLS = ['RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']
NAMES = {'RT10': 'RT10 Residential', 'RT20': 'RT20 Small commercial', 'RT40': 'RT40 Commercial', 'RT50': 'RT50 Large commercial',
         'RT60-ST': 'RT60 Street lighting', 'RT70': 'RT70 Industrial'}
G = 1e6
MINUS = '−'
NAVY, BLUE, CYAN, GREY, LIGHT = '#062552', '#0E4E95', '#009FDA', '#66788A', '#D9E1F2'
RED, GREEN, F_ALT = '#C00000', '#2E7D52', '#F3F6FB'

# ---------------- data ----------------
E = json.load(open(os.path.join(HERE, '_cust', 'engine_out.json')))
live26 = {rc: [v / G for v in E['2026'][rc]] for rc in CLS}
src = open(os.path.join(HERE, '_build_wb_v2.py'), encoding='utf-8').read()
ns = {}
for name in ('m26', 'm27', 'm28'):
    i = src.index(name + ' = {'); j = src.index(chr(10) + '}' + chr(10), i) + 3
    exec(src[i:j], ns)
reg = {y: {rc: [v / G for v in ns['m%d' % (y - 2000)][rc]] for rc in CLS} for y in (2026, 2027, 2028)}
FY25 = {'RT10': 1157.319, 'RT20': 627.296, 'RT40': 776.738, 'RT50': 362.830, 'RT60-ST': 38.647, 'RT70': 288.124}
FY_HELD = {2026: 3299.661, 2027: 3439.5, 2028: 3514.7}
SUBMISSION = 3281.97
fy = {y: {rc: sum(reg[y][rc]) for rc in CLS} for y in (2026, 2027, 2028)}
scale = FY_HELD[2026] / sum(fy[2026].values()); fy[2026] = {rc: v * scale for rc, v in fy[2026].items()}
tot = {2025: sum(FY25.values()), 2026: sum(fy[2026].values()), 2027: sum(fy[2027].values()), 2028: sum(fy[2028].values())}
assert abs(tot[2026] - 3299.661) < 1e-6 and abs(tot[2027] - 3439.5) < 0.01 and abs(tot[2028] - 3514.7) < 0.01
ytd = {rc: sum(live26[rc][:9]) for rc in CLS}
sep_act = {rc: live26[rc][8] for rc in CLS}
sep_reg = {rc: reg[2026][rc][8] for rc in CLS}
q4_new = {rc: fy[2026][rc] - ytd[rc] for rc in CLS}
T = lambda d: sum(d.values())
assert abs(T(sep_act) - 294.805) < 0.01 and abs(T(ytd) - 2429.037) < 0.01

# monthly year-on-year patterns from billed actuals
d = json.load(open(os.path.join(HERE, '_cust', 'pull.json'))); nn = json.load(open(os.path.join(HERE, '_cust', 'pull_nc.json')))
ind = {str(k['jps_ac']).strip(): k['industry'] or '' for k in d['ind']}
def kl(ac): return ind.get(ac) or ind.get(str(ac or '').split('-')[0]) or ''
cm = collections.defaultdict(float); tm = collections.defaultdict(float); hot = collections.defaultdict(float); wat = collections.defaultdict(float)
for r in d['act'] + nn['act_nc']:
    k = float(r['kwh'] or 0); y, m = r['year'], r['month']
    cm[(r['rate_class'], y, m)] += k; tm[(y, m)] += k
    i = kl(r['jps_ac']) if r['jps_ac'] else ''
    if 'Hotel' in i or 'Motel' in i: hot[(y, m)] += k
    if 'Water Supply' in i: wat[(y, m)] += k
yoy = lambda dd, m: (dd[(2026, m)] / dd[(2025, m)] - 1) * 100
S_TOT = [yoy(tm, m) for m in range(1, 10)]
S_RT10 = [(cm[('RT10', 2026, m)] / cm[('RT10', 2025, m)] - 1) * 100 for m in range(1, 10)]
S_HOT = [yoy(hot, m) for m in range(1, 10)]
S_WAT = [yoy(wat, m) for m in range(1, 10)]
RT20_Y = [(cm[('RT20', 2026, m)] / cm[('RT20', 2025, m)] - 1) * 100 for m in range(1, 10)]
RT70_Y = [(cm[('RT70', 2026, m)] / cm[('RT70', 2025, m)] - 1) * 100 for m in range(1, 10)]
oct25, nov25, dec25 = tm[(2025, 10)] / G, tm[(2025, 11)] / G, tm[(2025, 12)] / G
q4_25 = oct25 + nov25 + dec25
hot_ytd = (sum(hot[(2026, m)] for m in range(1, 10)) / sum(hot[(2025, m)] for m in range(1, 10)) - 1) * 100
assert abs(S_TOT[8] - (-2.29)) < 0.05 and abs(q4_25 - 701.0) < 0.2, (S_TOT[8], q4_25)

def f1(x): return f'{x:,.1f}'
def sg(x, d=1):
    s = f'{abs(x):,.{d}f}'
    return ('+' if x > 1e-7 else (MINUS if x < -1e-7 else '')) + s
def pc(x, d=1): return sg(x * 100, d) + '%'
def pp(x, d=1): return sg(x, d) + '%'
def col(x): return RED if x < 0 else BLUE
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']

# ---------------- bridges ----------------
B27 = [('Residential', 83.6), ('Temp.', 7.1), ('Solar', -5.1), ('Defections', -71.4), ('Comm. adj.', -14.7), ('Storm recovery', 140.3)]
B28 = [('Residential', 68.8), ('Temp.', 3.5), ('Solar', -10.3), ('Defections', -3.0), ('Comm. adj.', 16.2)]
assert abs(3299.7 + sum(v for _, v in B27) - 3439.5) < 0.051 and abs(3439.5 + sum(v for _, v in B28) - 3514.7) < 0.051

def waterfall(start, steps, end, lo, hi, w=330, h=215):
    n = len(steps) + 2
    left, right, top, bot = 6, w - 6, 24, h - 62
    slot = (right - left) / n; bw = slot * 0.62
    yv = lambda v: bot - (v - lo) / (hi - lo) * (bot - top)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" style="display:block;font-family:Arial">']
    s.append(f'<line x1="{left}" y1="{bot}" x2="{right}" y2="{bot}" stroke="{LIGHT}" stroke-width="1"/>')
    def lab(i, text, y, color):
        s.append(f'<text x="{left + slot * i + slot / 2:.1f}" y="{y:.1f}" font-size="8.5" font-weight="bold" fill="{color}" text-anchor="middle">{text}</text>')
    def cat(i, text):
        words = text.split(' '); lines = [words[0]] + ([' '.join(words[1:])] if len(words) > 1 else [])
        for k, ln in enumerate(lines):
            s.append(f'<text x="{left + slot * i + slot / 2:.1f}" y="{bot + 13 + k * 10}" font-size="7.4" fill="{GREY}" text-anchor="middle" font-weight="bold">{ln}</text>')
    x = lambda i: left + slot * i + (slot - bw) / 2
    s.append(f'<rect x="{x(0):.1f}" y="{yv(start):.1f}" width="{bw:.1f}" height="{bot - yv(start):.1f}" fill="{NAVY}"/>'); lab(0, f1(start), yv(start) - 4, NAVY); cat(0, 'Opening')
    run = start
    for k, (nm, dd) in enumerate(steps, 1):
        new = run + dd; ty, by = yv(max(run, new)), yv(min(run, new)); c = BLUE if dd >= 0 else RED
        s.append(f'<rect x="{x(k):.1f}" y="{ty:.1f}" width="{bw:.1f}" height="{max(by - ty, 1.2):.1f}" fill="{c}"/>')
        lab(k, sg(dd), ty - 4 if dd >= 0 else by + 10, c)
        s.append(f'<line x1="{x(k - 1) + bw:.1f}" y1="{yv(run):.1f}" x2="{x(k):.1f}" y2="{yv(run):.1f}" stroke="{GREY}" stroke-width="0.6"/>')
        cat(k, nm); run = new
    k = len(steps) + 1
    s.append(f'<line x1="{x(k - 1) + bw:.1f}" y1="{yv(run):.1f}" x2="{x(k):.1f}" y2="{yv(run):.1f}" stroke="{GREY}" stroke-width="0.6"/>')
    s.append(f'<rect x="{x(k):.1f}" y="{yv(end):.1f}" width="{bw:.1f}" height="{bot - yv(end):.1f}" fill="{NAVY}"/>'); lab(k, f1(end), yv(end) - 4, NAVY); cat(k, 'Closing')
    s.append('</svg>')
    return ''.join(s)

def linechart(series, lo=-40, hi=10, w=420, h=210):
    left, right, top, bot = 34, w - 62, 14, h - 34
    xs = lambda i: left + (right - left) * i / 8
    yv = lambda v: bot - (v - lo) / (hi - lo) * (bot - top)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" style="display:block;font-family:Arial">']
    for g in range(lo, hi + 1, 10):
        s.append(f'<line x1="{left}" y1="{yv(g):.1f}" x2="{right}" y2="{yv(g):.1f}" stroke="{NAVY if g == 0 else LIGHT}" stroke-width="{1 if g == 0 else 0.6}"/>')
        s.append(f'<text x="{left - 4}" y="{yv(g) + 3:.1f}" font-size="7.5" fill="{GREY}" text-anchor="end">{g}%</text>')
    for i, m in enumerate(MON):
        s.append(f'<text x="{xs(i):.1f}" y="{bot + 12}" font-size="7.8" fill="{GREY}" text-anchor="middle" font-weight="bold">{m}</text>')
    ly = {}
    order = sorted(range(len(series)), key=lambda k: yv(series[k][1][-1]))
    last = -99
    for k in order:
        y = max(yv(series[k][1][-1]), last + 10); ly[k] = y; last = y
    for k, (name, vals, c) in enumerate(series):
        pts = ' '.join(f'{xs(i):.1f},{yv(v):.1f}' for i, v in enumerate(vals))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="2"/>')
        for i, v in enumerate(vals): s.append(f'<circle cx="{xs(i):.1f}" cy="{yv(v):.1f}" r="2" fill="{c}"/>')
        s.append(f'<text x="{xs(8) + 6:.1f}" y="{ly[k] + 3:.1f}" font-size="7.8" font-weight="bold" fill="{c}">{name} {sg(vals[-1], 1)}%</text>')
    s.append('</svg>')
    return ''.join(s)

CSS = f'''
@page {{ size: A4; margin: 0 }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; color: #1F1F1F; font-size: 9.1pt; line-height: 1.38; }}
.page {{ width: 210mm; height: 297mm; padding: 12mm 13mm 14mm; page-break-after: always; position: relative; overflow: hidden; }}
.page:last-child {{ page-break-after: auto; }}
.top {{ display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2.2pt solid {NAVY}; padding-bottom: 2.5mm; margin-bottom: 4mm; }}
.top h1 {{ margin: 0; font-size: 20pt; color: {NAVY}; }}
.top .sub {{ color: {GREY}; font-size: 8.4pt; text-align: right; }}
h2 {{ font-size: 12.5pt; color: {NAVY}; margin: 4mm 0 2mm; }}
.head {{ color: {BLUE}; font-weight: bold; font-size: 12.2pt; line-height: 1.28; margin: 1mm 0 3.5mm; }}
.kpis {{ display: flex; gap: 3mm; margin-bottom: 4mm; }}
.kpi {{ flex: 1; border: 0.75pt solid {LIGHT}; border-top: 2.2pt solid {BLUE}; padding: 2.2mm 2.6mm 2mm; }}
.kpi.c {{ border-top-color: {CYAN}; }}
.kpi .l {{ font-size: 7pt; color: {GREY}; font-weight: bold; letter-spacing: .3pt; text-transform: uppercase; }}
.kpi .v {{ font-size: 19pt; font-weight: bold; color: {NAVY}; line-height: 1.15; }}
.kpi .v small {{ font-size: 9pt; color: {GREY}; font-weight: normal; }}
.kpi .d {{ font-size: 8.4pt; font-weight: bold; }}
.kpi .n {{ font-size: 7.6pt; color: {GREY}; }}
.sec {{ font-size: 8pt; font-weight: bold; color: {GREY}; letter-spacing: .4pt; text-transform: uppercase; margin: 0 0 1.6mm; }}
table {{ border-collapse: collapse; width: 100%; }}
th {{ background: {NAVY}; color: #fff; font-size: 7.8pt; padding: 1.4mm 1.4mm; text-align: center; font-weight: bold; }}
th.sub {{ background: {BLUE}; }}
th.l, td.l {{ text-align: left; }}
td {{ padding: 1.3mm 1.5mm; text-align: center; font-size: 8.5pt; border-bottom: 0.5pt solid {LIGHT}; vertical-align: top; }}
td.l {{ font-weight: bold; color: {NAVY}; }}
td.t {{ text-align: left; font-size: 8.3pt; }}
tr.alt td {{ background: {F_ALT}; }}
tr.tot td {{ background: {NAVY}; color: #fff; font-weight: bold; border: none; }}
.box {{ border: 0.75pt solid {LIGHT}; border-top: 2.2pt solid {BLUE}; padding: 2.6mm 3mm; }}
.box p {{ margin: 0 0 1.8mm; }}
.box p:last-child {{ margin: 0; }}
.row {{ display: flex; gap: 4mm; align-items: flex-start; }}
.note {{ font-size: 7.5pt; color: {GREY}; margin-top: 1.4mm; }}
.watch {{ background: {LIGHT}; border-left: 2.2pt solid {BLUE}; padding: 2.4mm 3.2mm; font-size: 8.9pt; }}
.watch b, .box b {{ color: {NAVY}; }}
.ins p {{ margin: 0 0 2.2mm; }}
.ins b {{ color: {NAVY}; }}
'''

# ================= page 1 =================
rows = []
for i, rc in enumerate(CLS):
    cells = [f'<td>{f1(FY25[rc])}</td>']; prev = FY25[rc]
    for y in (2026, 2027, 2028):
        v = fy[y][rc]; cells.append(f'<td>{f1(v)}</td><td style="color:{col(v - prev)};font-weight:bold">{pc(v / prev - 1)}</td>'); prev = v
    rows.append(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap">{NAMES[rc]}</td>{"".join(cells)}</tr>')
cells = [f'<td>{f1(tot[2025])}</td>']; prev = tot[2025]
for y in (2026, 2027, 2028):
    cells.append(f'<td>{f1(tot[y])}</td><td>{pc(tot[y] / prev - 1)}</td>'); prev = tot[y]
rows.append(f'<tr class="tot"><td class="l">Total billed sales</td>{"".join(cells)}</tr>')
p1 = f'''<div class="page">
<div class="top"><div><h1>Sales Forecast Driver Report</h1></div><div class="sub">Jamaica Public Service<br>FY2026 to FY2028 | Updated for the September 2026 close</div></div>
<div class="head">Billed sales recover from a storm-hit FY2026 to {f1(tot[2028])} GWh by FY2028. Recovery drives FY2027; rooftop solar and customers generating their own power slow growth after that.</div>
<div class="kpis">
 <div class="kpi"><div class="l">FY2026</div><div class="v">{f1(tot[2026])} <small>GWh</small></div><div class="d" style="color:{BLUE}">{pc(tot[2026] / tot[2025] - 1)} vs FY2025</div><div class="n">{sg(tot[2026] - SUBMISSION)} GWh vs the 19 August submission</div></div>
 <div class="kpi"><div class="l">FY2027</div><div class="v">{f1(tot[2027])} <small>GWh</small></div><div class="d" style="color:{BLUE}">{pc(tot[2027] / tot[2026] - 1)} vs FY2026</div><div class="n">{sg(tot[2027] - tot[2026])} GWh</div></div>
 <div class="kpi c"><div class="l">FY2028</div><div class="v">{f1(tot[2028])} <small>GWh</small></div><div class="d" style="color:{BLUE}">{pc(tot[2028] / tot[2027] - 1)} vs FY2027</div><div class="n">{sg(tot[2028] - tot[2027])} GWh</div></div>
 <div class="kpi c"><div class="l">January to September 2026</div><div class="v">{f1(T(ytd))} <small>GWh</small></div><div class="d" style="color:{RED}">{pc(T(ytd) / 2549.958 - 1)} vs 2025</div><div class="n">Actual billed sales</div></div>
</div>
<div class="sec">Three-year outlook by rate class (GWh)</div>
<table><tr><th class="l" rowspan="2">Rate class</th><th rowspan="2">FY2025<br>actual</th><th colspan="2">FY2026</th><th colspan="2">FY2027</th><th colspan="2">FY2028</th></tr>
<tr><th class="sub">GWh</th><th class="sub">YoY</th><th class="sub">GWh</th><th class="sub">YoY</th><th class="sub">GWh</th><th class="sub">YoY</th></tr>
{''.join(rows)}</table>
<div class="note">FY2026 is January to September actual plus forecast. Class figures may not add to the total because of rounding.</div>
<h2>The three-year story</h2>
<div class="box ins">
<p><b>FY2026, {f1(tot[2026])} GWh ({pc(tot[2026] / tot[2025] - 1)}): a storm year with a recovery inside it.</b> Hurricane Melissa struck on 28 October 2025 and billed sales fell from {oct25:.0f} GWh that month to {nov25:.0f} GWh in November. January and February 2026 were still {abs(S_TOT[0]):.0f} to {abs(S_TOT[1]):.0f}% below the year before. By May the system had returned to prior-year levels and homes and small businesses have run {RT20_Y[6]:.0f} to {S_RT10[6]:.0f}% above them since July as El Niño heat lifted cooling load. Hotels, still short of rooms, were {abs(S_HOT[8]):.0f}% below in September. The year finishes above FY2025 because the fourth quarter of 2025 was itself storm-depressed.</p>
<p><b>FY2027, {f1(tot[2027])} GWh ({pc(tot[2027] / tot[2026] - 1)}): the recovery year.</b> About 3,500 hotel rooms are due back in the first quarter, reconstruction is being organised through the new National Reconstruction and Resilience Authority, and the IMF has the economy growing again after a flat 2026. With a hotter, drier winter forecast, recovery and residential demand add {B27[5][1] + B27[0][1] + B27[1][1]:.0f} GWh. Alcoa's Jamalco refinery now generates its own power and two airports are commissioning on-site solar, which removes 71 GWh.</p>
<p><b>FY2028, {f1(tot[2028])} GWh ({pc(tot[2028] / tot[2027] - 1)}): back to underlying growth.</b> Storm recovery is complete and the weather returns toward normal. Growth comes from new connections and customers using more as incomes recover. Rooftop solar takes {abs(B28[2][1]):.0f} GWh and the licence renewal in July 2027 is the main regulatory unknown.</p>
</div>
</div>'''

# ================= page 2: FY2026 =================
yoytab = ''.join(
    f'<tr class="{"alt" if i % 2 else ""}"><td class="l">{nm}</td>' + ''.join(f'<td style="color:{col(v)};font-weight:bold">{sg(v, 1)}</td>' for v in vals) + '</tr>'
    for i, (nm, vals) in enumerate([('Total system', S_TOT), ('RT10 Residential', S_RT10), ('RT20 Small commercial', RT20_Y), ('Hotels', S_HOT), ('Water supply', S_WAT), ('RT70 Industrial', RT70_Y)]))
p2 = f'''<div class="page">
<div class="top"><div><h1>FY2026: A Storm Year</h1></div><div class="sub">Jamaica Public Service<br>Billed sales, year on year, GWh</div></div>
<div class="head">FY2026 holds at {f1(tot[2026])} GWh, {pc(tot[2026] / tot[2025] - 1)} on FY2025. The first nine months show a storm shock that has largely healed in homes and water, is healing slowly in hotels, and has been replaced by a permanent loss in industry.</div>
<div class="sec">Monthly change on the same month of 2025 (%)</div>
{linechart([('Total', S_TOT, NAVY), ('RT10', S_RT10, BLUE), ('Hotels', S_HOT, RED), ('Water', S_WAT, CYAN)], w=700, h=135)}
<table style="margin-top:1.5mm"><tr><th class="l">Segment</th>{''.join(f'<th>{m}</th>' for m in MON)}</tr>{yoytab}</table>
<div class="note">Hotels and water supply are customers coded to those industries across all rate classes.</div>
<h2>What the numbers say, and why</h2>
<div class="box ins">
<p><b>The storm cut November sales by more than a third, and the recovery took until May.</b> October 2025 billed {oct25:.0f} GWh and November {nov25:.0f} GWh, down {abs(nov25 / oct25 - 1) * 100:.0f}%. January and February 2026 were still {abs(S_TOT[0]):.1f}% and {abs(S_TOT[1]):.1f}% below prior year as the west of the island waited for restoration. From May the total has sat within about 4% of prior year, and in July it was level.</p>
<p><b>Homes are now above last year, and the weather is the reason.</b> RT10 ran {sg(S_RT10[6])}%, {sg(S_RT10[7])}% and {sg(S_RT10[8])}% against 2025 in July, August and September, and RT20 {sg(RT20_Y[6])}%, {sg(RT20_Y[7])}% and {sg(RT20_Y[8])}%. The Met Service warned in May of a hotter, drier summer as El Niño developed and JPS reported a 2026 peak of 676.9 MW on 1 July, confirming a link to temperature. The fuel charge also helped: it peaked at J$33.0 per kWh in March, when the Middle East conflict closed the Strait of Hormuz and Brent reached US$113, and had eased to J$26.8 by July. Prepaid volume grew 19.5% in September, consistent with households moving to pay as you go to control spending.</p>
<p><b>Hotels are the largest piece still missing.</b> Hotel customers were {abs(S_HOT[0]):.0f}% below prior year in January and {abs(S_HOT[8]):.0f}% below in September, {abs(hot_ytd):.0f}% down for the year to date. Stopover arrivals fell 27.5% in the first quarter, the biggest drop in the Caribbean, and although most hotels have reopened, several large resorts, including the Sandals properties in Montego Bay, do not return until December. Hotel volumes follow reopened rooms, so this line improves in steps. Water supply customers, by contrast, have recovered, from {abs(S_WAT[0]):.0f}% below prior year in January to level in September, which is consistent with pumping stations and the network being restored.</p>

<p><b>Industry has been lost for good.</b> RT70 was {abs(RT70_Y[7]):.0f}% and {abs(RT70_Y[8]):.0f}% below prior year in August and September. Jamalco, the Alcoa Minerals refinery in Clarendon, commissioned a new turbine in August that lets it generate all its own electricity, and its draw from the grid fell from 9.0 GWh in July to 0.6 GWh in September. Century Aluminum, its majority owner, expects savings of about US$28 million a year, which makes a return to the grid unlikely.</p>
</div>
<div class="watch" style="margin-top:3mm"><b>Reading FY2026.</b> The year is held at {f1(tot[2026])} GWh, {sg(tot[2026] - SUBMISSION)} GWh above the 19 August submission. September closed at {f1(T(sep_act))} GWh, {f1(T(sep_act) - T(sep_reg))} GWh above forecast with every class ahead. FY2026 finishes above FY2025 because the last quarter of 2025 was a storm-depressed base of {q4_25:.0f} GWh; the remaining months are forecast at {f1(T(q4_new))} GWh, {pc(T(q4_new) / q4_25 - 1, 0)} on that base, which is the recovery assumption in one number. Fuel was dearer too: in September heavy fuel oil was 16.6% and diesel 49.6% above a year earlier (System Operations), customers paid 3.3% more per kWh and bought 2.3% less.</div>
</div>'''

# ================= page 3: FY2027 =================
d27 = [
 ('Storm recovery', '+140.3', 'Hotels return in steps: Sandals resorts in December 2026, then about 3,500 more rooms in the first quarter of 2027 (Dreams, Secrets, Hyatt Ziva and Zilara among them). Reconstruction is being organised: the National Reconstruction and Resilience Authority became operational in June 2026, and the state housing programme plans more than 20,000 homes. The IMF has growth at zero in 2026 and 2.4% in 2027, and the PIOJ expects growth to resume by mid-2027. The forecast assumes about 53% of the 265.7 GWh of commercial load lost between November 2025 and May 2026 returns.'),
 ('Residential demand (RT10, RT20)', '+83.6', 'Customers are still moving into higher consumption bands (+81.7) because the recovery growth already visible in 2026 carries into the new year. New connections add +13.8 (about 820 premises a month) and prepaid +0.9. Conservation and the tariff response take back 12.8 as higher bills push the lightest and heaviest users to cut back.'),
 ('Temperature', '+7.1', 'NOAA puts the chance of a very strong El Niño in October to December at 81% and of El Niño lasting to early spring 2027 at 97%. The Met Service has warned the December to March dry season could be drier than normal and compared the drought risk with the one four years ago. A hotter, drier winter lifts cooling load.'),
 ('Solar', MINUS + '5.1', 'Self-generators have grown 73.7% since March 2024, and unlicensed systems 82.2%. Government plans a further 100 MW of distributed renewable energy through net billing, with online applications from December 2026. Each addition takes daytime load off the grid.'),
 ('Commercial defections', MINUS + '71.4', 'Jamalco (Alcoa Minerals) now generates all its own power, and MBJ Airports and PAC Kingston Airport are commissioning on-site solar. These are decisions already taken, not forecasts of behaviour. Windalco\'s owner, Rusal, is reported to be looking for a buyer, which is a further industrial risk not in the forecast.'),
 ('Commercial adjustment', MINUS + '14.7', 'Balancing line to the held totals. It includes the Windalco turbine outage and the continued shrinking of contact centres, where industry commentary reports the workforce falling from about 62,000 to under 50,000 as automation spreads.'),
]
dh27 = ''.join(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap;width:24%">{a}</td><td style="color:{RED if b.startswith(MINUS) else BLUE};font-weight:bold;white-space:nowrap">{b}</td><td class="t">{c}</td></tr>' for i, (a, b, c) in enumerate(d27))
p3 = f'''<div class="page">
<div class="top"><div><h1>FY2027: The Recovery Year</h1></div><div class="sub">Jamaica Public Service<br>FY2026 to FY2027, GWh</div></div>
<div class="head">Billed sales rise {f1(tot[2027] - tot[2026])} GWh ({pc(tot[2027] / tot[2026] - 1)}) to {f1(tot[2027])} GWh. Storm recovery and a hot winter more than cover the loss of Jamalco and two airport accounts to self-generation.</div>
<div class="row">
 <div style="flex:1"><div class="sec">Movement by driver ({sg(tot[2027] - tot[2026])} GWh)</div>{waterfall(3299.7, B27, 3439.5, 3260, 3470)}<div class="note">Axis does not start at zero.</div></div>
 <div style="flex:1"><div class="box ins" style="margin-top:5mm"><div class="sec">How to read it</div>
  <p>Underlying commercial volumes fall {f1(abs(B27[3][1] + B27[4][1]))} GWh before recovery, so recovery is what turns the commercial book to growth.</p>
  <p>RT50 rises {sg(fy[2027]['RT50'] - fy[2026]['RT50'])} GWh ({pc(fy[2027]['RT50'] / fy[2026]['RT50'] - 1)}) as hotels and food producers return. RT70 falls {f1(abs(fy[2027]['RT70'] - fy[2026]['RT70']))} GWh ({pc(abs(fy[2027]['RT70'] / fy[2026]['RT70'] - 1))}), almost all from the three defections.</p>
  <p>Residential is the steadiest piece: it is already growing in 2026 and the weather outlook supports it.</p></div></div>
</div>
<table style="margin-top:3mm"><tr><th class="l">Driver</th><th>GWh</th><th class="l" style="text-align:left">Why it moves, and what is behind it</th></tr>{dh27}</table>
</div>'''

# ================= page 4: FY2028 =================
d28 = [
 ('Residential demand (RT10, RT20)', '+68.8', 'Growth slows because the recovery already sits in the FY2027 base. New connections add +14.1 and migration to higher bands +65.7, against a conservation response of ' + MINUS + '11.7. The BOJ expects growth to strengthen through 2027/28 as reconstruction gathers pace, which supports household incomes, but inflation is forecast to stay elevated until mid-2027 and the policy rate rose to 6% in September.'),
 ('Commercial adjustment', '+16.2', 'Balancing line. Large commercial customers hold their post-storm volumes and RT50 grows {rt50:.1f} GWh with every industry up. New hotel supply adds to this: Marriott\'s 522-room Montego Bay resort is due in 2028, and the JAMPRO pipeline is US$4.2 billion across 13 projects and 8,943 rooms, with about 10% of it already delayed.'.format(rt50=fy[2028]['RT50'] - fy[2027]['RT50'])),
 ('Temperature', '+3.5', 'The weather effect halves. NOAA expects El Niño to fade by spring 2027, so winter and summer cooling load move back toward normal. El Niño years also tend to be quiet for Atlantic hurricanes, which lowers the chance of a second storm shock, though no outlook for the 2027 season has been issued.'),
 ('Solar', MINUS + '10.3', 'The loss doubles as adoption compounds. The net billing expansion adds up to 100 MW of distributed renewables, talks are under way to add battery storage, and the government has said it will not renew the JPS licence on existing terms. The licence expires on 8 July 2027, so the rules for exporting, storage and tariffs could change inside the forecast period.'),
 ('Commercial defections', MINUS + '3.0', 'The University of Technology moves load off the grid. No other defection is assumed.'),
 ('Storm recovery', 'nil', 'Recovery is complete by the end of FY2027, which is why the largest FY2027 driver disappears.'),
]
dh28 = ''.join(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap;width:24%">{a}</td><td style="color:{RED if b.startswith(MINUS) else BLUE};font-weight:bold;white-space:nowrap">{b}</td><td class="t">{c}</td></tr>' for i, (a, b, c) in enumerate(d28))
p4 = f'''<div class="page">
<div class="top"><div><h1>FY2028: Underlying Growth</h1></div><div class="sub">Jamaica Public Service<br>FY2027 to FY2028, GWh</div></div>
<div class="head">Billed sales rise {f1(tot[2028] - tot[2027])} GWh ({pc(tot[2028] / tot[2027] - 1)}) to {f1(tot[2028])} GWh. With storm recovery complete, growth is residential and is held back by rooftop solar.</div>
<div class="row">
 <div style="flex:1"><div class="sec">Movement by driver ({sg(tot[2028] - tot[2027])} GWh)</div>{waterfall(3439.5, B28, 3514.7, 3400, 3530)}<div class="note">Axis does not start at zero.</div></div>
 <div style="flex:1"><div class="box ins" style="margin-top:5mm"><div class="sec">How to read it</div>
  <p>Residential adds {f1(B28[0][1])} GWh, about {B28[0][1] / (tot[2028] - tot[2027]) * 100:.0f}% of the movement, so the outlook now rests on households and not on recovery.</p>
  <p>Solar is the only driver that gets larger: {f1(abs(B28[2][1]))} GWh against {f1(abs(B27[2][1]))} GWh a year earlier.</p>
  <p>RT50 still grows {pc(fy[2028]['RT50'] / fy[2027]['RT50'] - 1)}, the fastest class, because the volumes recovered in FY2027 become the base.</p></div></div>
</div>
<table style="margin-top:3mm"><tr><th class="l">Driver</th><th>GWh</th><th class="l" style="text-align:left">Why it moves, and what is behind it</th></tr>{dh28}</table>
</div>'''

# ================= page 5: risks, basis, sources =================
risks = [
 ('Hotel recovery pace', 'Up to 140.3 GWh of FY2027 recovery', 'Rooms reopened against plan (December 2026, first quarter 2027); monthly stopover arrivals; hotel customer volumes, now ' + f'{abs(S_HOT[8]):.0f}% below prior year', 'Downside if reopenings slip. About 10% of the new hotel pipeline is already delayed.'),
 ('Weather', 'Temperature +7.1 GWh in FY2027', 'NOAA monthly ENSO update; Met Service drought watches; JPS peak demand', 'Upside to cooling load in a strong El Niño, with drought risk to water and agriculture. 2027 hurricane outlook not yet issued.'),
 ('Self-generation and industry', MINUS + '71.4 GWh in FY2027, solar ' + MINUS + '10.3 GWh in FY2028', 'Net billing approvals; Windalco sale process; Alpart reopening decision; new customer solar applications', 'Downside. Further industrial exits are not in the forecast.'),
 ('Prices and the economy', 'Residential conservation ' + MINUS + '12.8 GWh in FY2027', 'JPS monthly fuel charge; inflation toward mid-2027; BOJ policy rate; IMF and PIOJ growth updates', 'Downside if fuel stays high or growth slips. The IMF cut its 2027 growth forecast to 2.4% from 3.1% in October.'),
 ('Licence and regulation', 'Outside the forecast', 'Outcome of the licence negotiation before 8 July 2027; net billing rule changes', 'Timing and tariff structure could change export, storage and solar economics from FY2028.'),
]
rr = ''.join(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap">{a}</td><td style="font-weight:bold;color:{NAVY};text-align:left">{b}</td><td class="t">{c}</td><td class="t">{e}</td></tr>' for i, (a, b, c, e) in enumerate(risks))
p5 = f'''<div class="page">
<div class="top"><div><h1>Risks and Basis</h1></div><div class="sub">Jamaica Public Service<br>Sales forecast, FY2026 to FY2028</div></div>
<div class="head">Five things would move the outlook. Hotel recovery is the largest and the first to show in the data.</div>
<table><tr><th class="l">Risk</th><th class="l" style="text-align:left">Size in the forecast</th><th class="l" style="text-align:left">What to watch</th><th class="l" style="text-align:left">Direction</th></tr>{rr}</table>
<h2>Sources for the market, weather and commercial context</h2>
<div class="note" style="font-size:7.8pt;line-height:1.5">NOAA Climate Prediction Center, ENSO diagnostic discussion, 9 July 2026. Jamaica Meteorological Service via the Gleaner, 20 May and 14 July 2026. Jamaica Observer, 8 July 2026 (JPS peak demand). JPS fuel rate schedule, February to July 2026. System Operations Grid Performance Review, September 2026. Caribbean Journal, 13 July 2026 (Caribbean Tourism Organization arrivals). JAPEX 2026 tourism ministry briefing as reported by Travel Market Report and TravelPulse. Jamaica Gleaner, 26 July 2026 (JAMPRO hotel pipeline). alCircle, 11 August 2026 (Jamalco turbine). Jamaica Gleaner, 25 September 2026 (Rusal and Windalco). Jamaica Observer, 26 July 2026 (Alpart). JPS statement on the fuel charge and the Middle East conflict, March 2026, as reported by Irie FM. IMF World Economic Outlook, October 2026, as reported by the Gleaner on 16 October. PIOJ, August 2026, and Bank of Jamaica, September 2026, as reported by the Observer and JIS. Jamaica Information Service (National Reconstruction and Resilience Authority; housing programme; net billing; licensing negotiation). Industry commentary on contact centre employment as republished by Outsource Accelerator.</div>
<div class="note" style="margin-top:3mm">Prepared by Sales Forecasting and Analysis. Figures in GWh unless stated.</div>
</div>'''

html = f'<!doctype html><html><head><meta charset="utf-8"><title>JPS Sales Forecast Driver Report September 2026</title><style>{CSS}</style></head><body>{p1}{p2}{p3}{p4}{p5}</body></html>'
out = os.path.join(HERE, '_driver_report_sep2026.html')
open(out, 'w', encoding='utf-8').write(html)
print('wrote', out)
print('YoY total', [round(v, 1) for v in S_TOT]); print('RT10', [round(v, 1) for v in S_RT10]); print('hot', [round(v, 1) for v in S_HOT], round(hot_ytd, 1)); print('wat', [round(v, 1) for v in S_WAT])
print('Q4 25', round(q4_25, 1), 'Q4 26', round(T(q4_new), 1), 'oct/nov25', round(oct25, 1), round(nov25, 1), 'RT20', [round(v, 1) for v in RT20_Y[6:]], 'RT70', [round(v, 1) for v in RT70_Y[7:]])
