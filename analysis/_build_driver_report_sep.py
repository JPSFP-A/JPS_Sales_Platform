# -*- coding: utf-8 -*-
# Concise CFO version of the Sales Forecast Driver Report, updated for the September 2026 close.
# FY2026, FY2027 and FY2028 totals are held at the financials (3,299.7 / 3,439.5 / 3,514.7 GWh).
import json, os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '_cust'))

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CLS = ['RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']
NAMES = {'RT10': 'RT10 Residential', 'RT20': 'RT20 Small commercial', 'RT40': 'RT40 Commercial', 'RT50': 'RT50 Large commercial',
         'RT60-ST': 'RT60 Street lighting', 'RT70': 'RT70 Industrial'}
G = 1e6
MINUS = '−'
NAVY, BLUE, CYAN, GREY, LIGHT = '#062552', '#0E4E95', '#009FDA', '#66788A', '#D9E1F2'
RED, GREEN, F_ALT = '#C00000', '#2E7D52', '#F3F6FB'

# ---------------- data ----------------
E = json.load(open(os.path.join(HERE, '_cust', 'engine_out.json')))
live26 = {rc: [v / G for v in E['2026'][rc]] for rc in CLS}                   # January to September are actual billed sales
src = open(os.path.join(HERE, '_build_wb_v2.py'), encoding='utf-8').read()
ns = {}
for name in ('m26', 'm27', 'm28'):
    i = src.index(name + ' = {'); j = src.index(chr(10) + '}' + chr(10), i) + 3
    exec(src[i:j], ns)
reg = {y: {rc: [v / G for v in ns['m%d' % (y - 2000)][rc]] for rc in CLS} for y in (2026, 2027, 2028)}
FY25 = {'RT10': 1157.319, 'RT20': 627.296, 'RT40': 776.738, 'RT50': 362.830, 'RT60-ST': 38.647, 'RT70': 288.124}   # billed actual, verified
FY_HELD = {2026: 3299.661, 2027: 3439.5, 2028: 3514.7}
SUBMISSION = 3281.97

fy = {y: {rc: sum(reg[y][rc]) for rc in CLS} for y in (2026, 2027, 2028)}
scale = FY_HELD[2026] / sum(fy[2026].values())
fy[2026] = {rc: v * scale for rc, v in fy[2026].items()}
tot = {2025: sum(FY25.values()), 2026: sum(fy[2026].values()), 2027: sum(fy[2027].values()), 2028: sum(fy[2028].values())}
assert abs(tot[2026] - 3299.661) < 1e-6 and abs(tot[2027] - 3439.5) < 0.01 and abs(tot[2028] - 3514.7) < 0.01, tot

ytd = {rc: sum(live26[rc][:9]) for rc in CLS}
sep_act = {rc: live26[rc][8] for rc in CLS}
sep_reg = {rc: reg[2026][rc][8] for rc in CLS}
q4_prior = {rc: sum(reg[2026][rc][9:]) * scale for rc in CLS}
q4_new = {rc: fy[2026][rc] - ytd[rc] for rc in CLS}
T = lambda d: sum(d.values())
assert abs(T(sep_act) - 294.805) < 0.01 and abs(T(ytd) - 2429.037) < 0.01

def f1(x): return f'{x:,.1f}'
def sg(x, d=1):
    s = f'{abs(x):,.{d}f}'
    return ('+' if x > 0.0000001 else (MINUS if x < -0.0000001 else '')) + s
def pc(x, d=1): return sg(x * 100, d) + '%'
def col(x): return RED if x < 0 else BLUE

# ---------------- bridges (driver lines held; commercial load adjustment is the balancing line) ----------------
B27 = [('Residential', 83.6), ('Temp.', 7.1), ('Solar', -5.1), ('Defections', -71.4), ('Comm. adj.', -14.7), ('Storm recovery', 140.3)]
B28 = [('Residential', 68.8), ('Temp.', 3.5), ('Solar', -10.3), ('Defections', -3.0), ('Comm. adj.', 16.2)]
assert abs(3299.7 + sum(v for _, v in B27) - 3439.5) < 0.051, sum(v for _, v in B27)
assert abs(3439.5 + sum(v for _, v in B28) - 3514.7) < 0.051, sum(v for _, v in B28)

def waterfall(start, steps, end, lo, hi, w=330, h=215):
    n = len(steps) + 2
    left, right, top, bot = 6, w - 6, 24, h - 62
    slot = (right - left) / n; bw = slot * 0.62
    yv = lambda v: bot - (v - lo) / (hi - lo) * (bot - top)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" style="display:block;font-family:Arial">']
    s.append(f'<line x1="{left}" y1="{bot}" x2="{right}" y2="{bot}" stroke="{LIGHT}" stroke-width="1"/>')
    def lab(i, text, y, color, anchor='middle'):
        s.append(f'<text x="{left + slot * i + slot / 2:.1f}" y="{y:.1f}" font-size="8.5" font-weight="bold" fill="{color}" text-anchor="middle">{text}</text>')
    def cat(i, text):
        words = text.split(' '); lines = [' '.join(words[:1])] + ([' '.join(words[1:])] if len(words) > 1 else [])
        for k, ln in enumerate(lines):
            s.append(f'<text x="{left + slot * i + slot / 2:.1f}" y="{bot + 13 + k * 10}" font-size="7" fill="{GREY}" text-anchor="middle" font-weight="bold">{ln}</text>')
    x = lambda i: left + slot * i + (slot - bw) / 2
    s.append(f'<rect x="{x(0):.1f}" y="{yv(start):.1f}" width="{bw:.1f}" height="{bot - yv(start):.1f}" fill="{NAVY}"/>'); lab(0, f1(start), yv(start) - 4, NAVY); cat(0, 'Opening')
    run = start
    for k, (nm, d) in enumerate(steps, 1):
        new = run + d; top_y, bot_y = yv(max(run, new)), yv(min(run, new))
        c = BLUE if d >= 0 else RED
        s.append(f'<rect x="{x(k):.1f}" y="{top_y:.1f}" width="{bw:.1f}" height="{max(bot_y - top_y, 1.2):.1f}" fill="{c}"/>')
        if d >= 0: lab(k, sg(d), top_y - 4, c)
        else: lab(k, sg(d), bot_y + 10, c)
        s.append(f'<line x1="{x(k - 1) + bw:.1f}" y1="{yv(run):.1f}" x2="{x(k):.1f}" y2="{yv(run):.1f}" stroke="{GREY}" stroke-width="0.6"/>')
        cat(k, nm); run = new
    k = len(steps) + 1
    s.append(f'<line x1="{x(k - 1) + bw:.1f}" y1="{yv(run):.1f}" x2="{x(k):.1f}" y2="{yv(run):.1f}" stroke="{GREY}" stroke-width="0.6"/>')
    s.append(f'<rect x="{x(k):.1f}" y="{yv(end):.1f}" width="{bw:.1f}" height="{bot - yv(end):.1f}" fill="{NAVY}"/>'); lab(k, f1(end), yv(end) - 4, NAVY); cat(k, 'Closing')
    s.append('</svg>')
    return ''.join(s)

CSS = f'''
@page {{ size: A4; margin: 0 }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; color: #1F1F1F; font-size: 9.4pt; line-height: 1.38; }}
.page {{ width: 210mm; height: 297mm; padding: 12mm 13mm 14mm; page-break-after: always; position: relative; overflow: hidden; }}
.page:last-child {{ page-break-after: auto; }}
.top {{ display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2.2pt solid {NAVY}; padding-bottom: 2.5mm; margin-bottom: 4mm; }}
.top h1 {{ margin: 0; font-size: 20pt; color: {NAVY}; }}
.top .sub {{ color: {GREY}; font-size: 8.4pt; text-align: right; }}
h2 {{ font-size: 13pt; color: {NAVY}; margin: 5mm 0 2mm; }}
.head {{ color: {BLUE}; font-weight: bold; font-size: 12.5pt; line-height: 1.28; margin: 1mm 0 3.5mm; }}
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
td {{ padding: 1.3mm 1.5mm; text-align: center; font-size: 8.6pt; border-bottom: 0.5pt solid {LIGHT}; vertical-align: top; }}
td.l {{ font-weight: bold; color: {NAVY}; }}
td.t {{ text-align: left; font-size: 8.4pt; }}
tr.alt td {{ background: {F_ALT}; }}
tr.tot td {{ background: {NAVY}; color: #fff; font-weight: bold; border: none; }}
.box {{ border: 0.75pt solid {LIGHT}; border-top: 2.2pt solid {BLUE}; padding: 2.6mm 3mm; }}
.box p {{ margin: 0 0 1.8mm; }}
.box p:last-child {{ margin: 0; }}
.row {{ display: flex; gap: 4mm; align-items: flex-start; }}
.note {{ font-size: 7.6pt; color: {GREY}; margin-top: 1.6mm; }}
.watch {{ background: {LIGHT}; border-left: 2.2pt solid {BLUE}; padding: 2.4mm 3.2mm; font-size: 9pt; }}
.watch b, .box b {{ color: {NAVY}; }}
'''

# ---------------- page 1: outlook ----------------
rows = []
for i, rc in enumerate(CLS):
    cells = [f'<td>{f1(FY25[rc])}</td>']
    prev = FY25[rc]
    for y in (2026, 2027, 2028):
        v = fy[y][rc]; cells.append(f'<td>{f1(v)}</td><td style="color:{col(v - prev)};font-weight:bold">{pc(v / prev - 1)}</td>'); prev = v
    rows.append(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap">{NAMES[rc]}</td>{"".join(cells)}</tr>')
cells = [f'<td>{f1(tot[2025])}</td>']; prev = tot[2025]
for y in (2026, 2027, 2028):
    cells.append(f'<td>{f1(tot[y])}</td><td>{pc(tot[y] / prev - 1)}</td>'); prev = tot[y]
rows.append(f'<tr class="tot"><td class="l">Total billed sales</td>{"".join(cells)}</tr>')

p1 = f'''<div class="page">
<div class="top"><div><h1>Sales Forecast Driver Report</h1></div><div class="sub">Jamaica Public Service<br>FY2026 to FY2028 | Updated for the September 2026 close</div></div>
<div class="head">Billed sales grow from {f1(tot[2026])} GWh in FY2026 to {f1(tot[2028])} GWh in FY2028, led by storm recovery and residential growth, with the loss of three large industrial customers as the main offset.</div>
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
<h2>Summary</h2>
<div class="box">
<p><b>FY2026 is held at {f1(tot[2026])} GWh.</b> September closed at {f1(T(sep_act))} GWh, {f1(T(sep_act) - T(sep_reg))} GWh above forecast. With the full year held, the fourth quarter is now {f1(T(q4_new))} GWh against {f1(T(q4_prior))} GWh previously.</p>
<p><b>FY2027 grows {f1(tot[2027] - tot[2026])} GWh ({pc(tot[2027] / tot[2026] - 1)}).</b> Storm recovery in the commercial book adds 140.3 GWh and residential demand adds 83.6 GWh. The loss of Alcoa, MBJ Airports and PAC Kingston Airport to self-generation takes 71.4 GWh away. RT50 grows {pc(fy[2027]['RT50'] / fy[2026]['RT50'] - 1)} as hotels and food producers recover; RT70 falls {pc(abs(fy[2027]['RT70'] / fy[2026]['RT70'] - 1))}.</p>
<p><b>FY2028 grows {f1(tot[2028] - tot[2027])} GWh ({pc(tot[2028] / tot[2027] - 1)}).</b> Storm recovery is complete, so growth is residential (68.8 GWh), partly offset by rooftop solar (10.3 GWh).</p>
</div>
</div>'''

# ---------------- page 2: September close ----------------
srows = []
for i, rc in enumerate(CLS):
    a, f = sep_act[rc], sep_reg[rc]
    srows.append(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap">{NAMES[rc]}</td><td>{f1(a)}</td><td>{f1(f)}</td><td style="color:{col(a - f)};font-weight:bold">{sg(a - f)}</td>'
                 f'<td>{f1(ytd[rc])}</td><td>{f1(q4_prior[rc])}</td><td>{f1(q4_new[rc])}</td><td style="color:{col(q4_new[rc] - q4_prior[rc])};font-weight:bold">{sg(q4_new[rc] - q4_prior[rc])}</td><td>{f1(fy[2026][rc])}</td></tr>')
srows.append(f'<tr class="tot"><td class="l">Total</td><td>{f1(T(sep_act))}</td><td>{f1(T(sep_reg))}</td><td>{sg(T(sep_act) - T(sep_reg))}</td><td>{f1(T(ytd))}</td><td>{f1(T(q4_prior))}</td><td>{f1(T(q4_new))}</td><td>{sg(T(q4_new) - T(q4_prior))}</td><td>{f1(T(fy[2026]))}</td></tr>')
p2 = f'''<div class="page">
<div class="top"><div><h1>September Close and FY2026</h1></div><div class="sub">Jamaica Public Service<br>Billed sales, GWh</div></div>
<div class="head">September billed sales of {f1(T(sep_act))} GWh beat the forecast by {f1(T(sep_act) - T(sep_reg))} GWh across every rate class. The full year stays at {f1(tot[2026])} GWh, so the fourth quarter absorbs the difference.</div>
<div class="sec">September actual, year to date and fourth quarter by rate class</div>
<table><tr><th class="l" rowspan="2">Rate class</th><th colspan="3">September</th><th>Jan to Sep</th><th colspan="3">October to December</th><th>FY2026</th></tr>
<tr><th class="sub">Actual</th><th class="sub">Forecast</th><th class="sub">Variance</th><th class="sub">Actual</th><th class="sub">Previous</th><th class="sub">Now</th><th class="sub">Change</th><th class="sub">Held</th></tr>
{''.join(srows)}</table>
<div class="row" style="margin-top:5mm">
 <div class="box" style="flex:1.25"><div class="sec">Reading the close</div>
  <p>September came in {abs(T(sep_act) / 301.715 - 1) * 100:.1f}% below September 2025. Year to date, billed sales are {f1(T(ytd))} GWh, {abs(T(ytd) / 2549.958 - 1) * 100:.1f}% below the same period of 2025.</p>
  <p>The upside was broad: RT10 and RT20 added {f1(sep_act['RT10'] + sep_act['RT20'] - sep_reg['RT10'] - sep_reg['RT20'])} GWh and RT40 to RT70 {f1(sep_act['RT40'] + sep_act['RT50'] + sep_act['RT60-ST'] + sep_act['RT70'] - sep_reg['RT40'] - sep_reg['RT50'] - sep_reg['RT60-ST'] - sep_reg['RT70'])} GWh against forecast.</p>
  <p>Because FY2026 is held at {f1(tot[2026])} GWh, the fourth quarter falls {f1(abs(T(q4_new) - T(q4_prior)))} GWh to {f1(T(q4_new))} GWh. That is a monthly average of {f1(T(q4_new) / 3)} GWh, against {f1(sum(T({rc: live26[rc][m] for rc in CLS}) for m in (6, 7, 8)) / 3)} GWh for July to September.</p>
 </div>
 <div class="box" style="flex:1"><div class="sec">FY2026 against the submission</div>
  <p>The 19 August submission was {f1(SUBMISSION)} GWh. FY2026 now stands at {f1(tot[2026])} GWh, {sg(tot[2026] - SUBMISSION)} GWh higher ({pc(tot[2026] / SUBMISSION - 1)}).</p>
  <p>The submission stays the figure of record. This report states the current number and the gap.</p>
 </div>
</div>
<div class="watch" style="margin-top:5mm"><b>Watch.</b> A fourth quarter of {f1(T(q4_new) / 3)} GWh a month is {f1(sum(T({rc: live26[rc][m] for rc in CLS}) for m in (6, 7, 8)) / 3 - T(q4_new) / 3)} GWh a month below the July to September average. Alcoa's grid draw fell from 9.0 GWh in July to 0.6 GWh in September, and the rest is seasonal. Any shortfall in hotel and commercial recovery would show in this quarter first.</div>
</div>'''

# ---------------- page 3: drivers ----------------
drows = [
 ('Residential demand (RT10, RT20)', '+83.6', '+68.8', 'New connections (+13.8 and +14.1), customers moving into higher consumption bands (+81.7 and +65.7) and prepaid growth (+0.9 and +0.7), less conservation and tariff response (' + MINUS + '12.8 and ' + MINUS + '11.7).'),
 ('Temperature', '+7.1', '+3.5', 'Weather assumptions for the residential book.'),
 ('Solar', MINUS + '5.1', MINUS + '10.3', 'Residential customers generating their own power. The effect doubles in FY2028 as adoption continues.'),
 ('Commercial defections', MINUS + '71.4', MINUS + '3.0', 'FY2027: Alcoa (self-generation completed in August 2026), MBJ Airports and PAC Kingston Airport (on-site solar). FY2028: University of Technology.'),
 ('Commercial adjustment', MINUS + '14.7', '+16.2', 'Balancing line to the held totals. FY2027 includes Windalco turbine maintenance. FY2028 reflects large commercial accounts holding their higher post-storm volumes.'),
 ('Storm recovery', '+140.3', 'nil', 'Recovery of part of the 265.7 GWh of commercial load that Hurricane Melissa suppressed between November 2025 and May 2026. Complete by the end of FY2027.'),
]
dh = ''.join(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap">{a}</td><td style="color:{RED if b.startswith(MINUS) else BLUE};font-weight:bold">{b}</td><td style="color:{RED if c.startswith(MINUS) else BLUE};font-weight:bold">{c}</td><td class="t">{d}</td></tr>' for i, (a, b, c, d) in enumerate(drows))
dh += f'<tr class="tot"><td class="l">Total movement</td><td>{sg(tot[2027] - tot[2026])}</td><td>{sg(tot[2028] - tot[2027])}</td><td class="t" style="color:#fff">{f1(tot[2026])} to {f1(tot[2027])} GWh, then to {f1(tot[2028])} GWh</td></tr>'
p3 = f'''<div class="page">
<div class="top"><div><h1>What Drives the Outlook</h1></div><div class="sub">Jamaica Public Service<br>Movement in billed sales, GWh</div></div>
<div class="head">Two drivers decide FY2027: storm recovery adds {B27[5][1]:.1f} GWh and defections remove {abs(B27[3][1]):.1f} GWh. In FY2028 the outlook rests on residential growth.</div>
<div class="row">
 <div style="flex:1"><div class="sec">FY2026 to FY2027 ({sg(tot[2027] - tot[2026])} GWh)</div>{waterfall(3299.7, B27, 3439.5, 3260, 3470)}</div>
 <div style="flex:1"><div class="sec">FY2027 to FY2028 ({sg(tot[2028] - tot[2027])} GWh)</div>{waterfall(3439.5, B28, 3514.7, 3400, 3530)}</div>
</div>
<div class="note" style="margin-bottom:4mm">Axes do not start at zero.</div>
<table><tr><th class="l">Driver</th><th>FY2027</th><th>FY2028</th><th class="l" style="text-align:left">What is behind it</th></tr>{dh}</table>
<div class="row" style="margin-top:5mm">
 <div class="box" style="flex:1"><div class="sec">Commercial and residential</div>
  <p>Underlying commercial volumes fall {f1(abs(B27[3][1] + B27[4][1]))} GWh in FY2027 before storm recovery, so recovery is what turns the commercial book to growth.</p>
  <p>Residential demand adds {f1(B27[0][1])} GWh in FY2027 and {f1(B28[0][1])} GWh in FY2028, and is the steadiest part of the outlook.</p>
 </div>
 <div class="box" style="flex:1"><div class="sec">By rate class</div>
  <p>RT50 rises {sg(fy[2027]['RT50'] - fy[2026]['RT50'])} GWh in FY2027 and {sg(fy[2028]['RT50'] - fy[2027]['RT50'])} GWh in FY2028 as hotels and food producers recover.</p>
  <p>RT70 falls {f1(abs(fy[2027]['RT70'] - fy[2026]['RT70']))} GWh in FY2027, almost all from the three defections.</p>
 </div>
</div>
</div>'''

# ---------------- page 4: risks and basis ----------------
risks = [
 ('Storm recovery', '+140.3 GWh in FY2027', 'About 53% of the 265.7 GWh Hurricane Melissa took out of commercial load is assumed to return by the end of FY2027. It is the largest single driver and the least certain. Hotels and water supply are the largest recovering industries.'),
 ('Residential growth', '+83.6 GWh in FY2027, +68.8 GWh in FY2028', 'Mainly customers moving into higher consumption bands. An independent check of the migration effect gives +78.0 GWh against +81.7 GWh in the forecast.'),
 ('Large customer defections', MINUS + '71.4 GWh in FY2027', 'Alcoa has completed its move to self-generation. MBJ Airports and PAC Kingston Airport are commissioning on-site solar. Further defections would add to the loss, and none is assumed beyond University of Technology in FY2028.'),
 ('Rooftop solar', MINUS + '5.1 GWh in FY2027, ' + MINUS + '10.3 GWh in FY2028', 'Self-generators grew 73.7% between March 2024 and September 2026. The forecast assumes continued adoption at the current pace.'),
]
rr = ''.join(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap">{a}</td><td style="font-weight:bold;color:{NAVY};text-align:left">{b}</td><td class="t">{c}</td></tr>' for i, (a, b, c) in enumerate(risks))
p4 = f'''<div class="page">
<div class="top"><div><h1>Risks and Basis</h1></div><div class="sub">Jamaica Public Service<br>Sales forecast, FY2026 to FY2028</div></div>
<div class="head">The outlook depends on four judgements. Storm recovery is the largest and the one to watch first.</div>
<table><tr><th class="l">Judgement</th><th class="l" style="text-align:left">Size in the forecast</th><th class="l" style="text-align:left">View</th></tr>{rr}</table>
<h2>Basis of preparation</h2>
<div class="box">
<p><b>Actuals and forecast.</b> FY2025 is billed actual. FY2026 is January to September actual plus forecast, held at {f1(tot[2026])} GWh. FY2027 and FY2028 are full driver projections, held at {f1(tot[2027])} and {f1(tot[2028])} GWh.</p>
<p><b>Method.</b> Each customer or customer group is projected from its recent three-month average, adjusted for the macro outlook, weather, industry seasonality, solar, storm recovery and confirmed customer events.</p>
<p><b>Balancing line.</b> Commercial adjustment is the balancing line between the named drivers and the held totals.</p>
<p><b>Sales basis.</b> Figures are customer-billed sales. Normalised sales, which adjust for billing timing, are higher: 300.2 GWh in September against 294.8 GWh billed.</p>
</div>
<div class="note" style="margin-top:4mm">Prepared by Sales Forecasting and Analysis. Figures in GWh unless stated.</div>
</div>'''

html = f'<!doctype html><html><head><meta charset="utf-8"><title>JPS Sales Forecast Driver Report September 2026</title><style>{CSS}</style></head><body>{p1}{p2}{p3}{p4}</body></html>'
out = os.path.join(HERE, '_driver_report_sep2026.html')
open(out, 'w', encoding='utf-8').write(html)
print('wrote', out)
print('FY', {y: round(v, 3) for y, v in tot.items()})
print('Sep act', round(T(sep_act), 3), 'reg', round(T(sep_reg), 3), 'Q4 prior', round(T(q4_prior), 3), 'Q4 new', round(T(q4_new), 3), 'YTD', round(T(ytd), 3))
print('class FY26/27/28', {rc: (round(fy[2026][rc], 1), round(fy[2027][rc], 1), round(fy[2028][rc], 1)) for rc in CLS})
