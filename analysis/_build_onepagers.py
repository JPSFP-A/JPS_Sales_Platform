# -*- coding: utf-8 -*-
# One-page September 2026 sales analysis and one-page forecast accuracy (HTML, rendered to PDF by render_onepager.js).
# Inputs are the verified class/account figures already used in the full September report and the accuracy deck.
import os

OUT = r'C:\Projects\Sales_Platform'
NAVY, BLUE, CYAN, GREY, LIGHT = '#062552', '#0E4E95', '#009FDA', '#66788A', '#D9E1F2'
RED, GREEN = '#C00000', '#2E7D52'
F_GOOD, F_MID, F_BAD, F_ALT = '#DDEFDF', '#FFF0C8', '#F6D3D6', '#F3F6FB'
MINUS = '\u2212'

ORDER = ['RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']
NAMES = {'RT10': 'RT10 Residential', 'RT20': 'RT20 Small commercial', 'RT40': 'RT40 Commercial', 'RT50': 'RT50 Large commercial',
         'RT60-ST': 'RT60 Street lighting', 'RT70': 'RT70 Industrial'}

# ---- actuals (GWh and J$M, customer-billed basis, September restated) ----
ACT = {  # class: (sep26, sep25, ytd26, ytd25, rev_sep26, rev_sep25, rev_ytd26, rev_ytd25)
 'RT10': (114.566, 110.279, 882.601, 909.698, 6625.0, 6320.1, 52330.8, 52556.9),
 'RT20': (60.618, 58.278, 475.762, 490.521, 3299.5, 3185.3, 26748.3, 27282.5),
 'RT40': (67.313, 68.941, 569.767, 605.324, 3199.8, 3204.7, 27336.0, 27688.0),
 'RT50': (30.253, 33.527, 259.549, 287.170, 1203.1, 1281.3, 10564.4, 11407.4),
 'RT60-ST': (3.413, 3.409, 27.490, 30.382, 213.7, 215.3, 1739.0, 1906.3),
 'RT70': (18.643, 27.281, 213.868, 226.863, 874.1, 1072.8, 9127.3, 8983.4),
}
BUD = {  # class: aug, sep, ytd budget GWh
 'RT10': (114.154, 104.830, 853.626), 'RT20': (58.922, 57.649, 461.306), 'RT40': (72.325, 73.334, 584.913),
 'RT50': (35.090, 35.268, 274.111), 'RT60-ST': (3.375, 3.312, 27.057), 'RT70': (23.364, 22.866, 192.712)}
AUG_ACT = {'RT10': 117.671, 'RT20': 60.610, 'RT40': 71.883, 'RT50': 30.677, 'RT60-ST': 3.413, 'RT70': 19.708}
ACCT_ABS = {'RT40': (21.609, 22.938, 106.260), 'RT50': (11.021, 10.841, 60.604), 'RT60-ST': (0.083, 0.138, 0.726), 'RT70': (13.486, 13.490, 45.296)}
IND = {  # industry: (sep actual, sep budget, sep abs err, ytd actual, ytd budget, ytd abs err)
 'Water supply and irrigation': (18.623, 21.042, 8.774, 158.029, 166.537, 41.227),
 'Hotels and motels': (17.231, 20.944, 8.686, 145.540, 156.689, 42.421),
 'Cement manufacturing': (9.150, 8.728, 0.444, 82.527, 75.219, 7.373),
 'Telecommunications': (6.972, 8.189, 2.203, 60.966, 65.744, 10.902),
 'Executive offices': (5.931, 5.832, 1.397, 47.379, 46.608, 7.068),
 'Full-service restaurants': (5.138, 5.295, 0.952, 42.369, 42.372, 4.471),
 'Banking, insurance and investments': (4.801, 4.750, 0.744, 38.518, 38.031, 3.496),
 'Supermarkets and grocery': (3.994, 4.050, 0.661, 33.665, 32.315, 4.152),
}

def acc(a, f): return max(0.0, 1 - abs(a - f) / a) if a else 0.0
def pct(x, d=0): return f'{x * 100:.{d}f}%'
def chg(x, d=1):
    s = f'{abs(x):.{d}f}'
    return ('+' if x > 0 else (MINUS if x < 0 else '')) + s
def chgp(x, d=1): return chg(x * 100, d) + '%'
def col(x): return RED if x < 0 else BLUE
def fill(v): return F_GOOD if v >= 0.95 else (F_MID if v >= 0.85 else F_BAD)

CSS = f'''
@page {{ size: A4; margin: 0 }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; color: #1F1F1F; font-size: 9.2pt; line-height: 1.32; }}
.page {{ width: 210mm; height: 297mm; padding: 11mm 12mm 9mm; position: relative; overflow: hidden; }}
.top {{ display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2.2pt solid {NAVY}; padding-bottom: 2.5mm; }}
.top h1 {{ margin: 0; font-size: 21pt; color: {NAVY}; letter-spacing: -0.2pt; }}
.top .sub {{ color: {GREY}; font-size: 8.5pt; text-align: right; }}
.head {{ color: {BLUE}; font-weight: bold; font-size: 13pt; line-height: 1.25; margin: 4mm 0 3.5mm; }}
.kpis {{ display: flex; gap: 3mm; margin-bottom: 4mm; }}
.kpi {{ flex: 1; border: 0.75pt solid {LIGHT}; border-top: 2.2pt solid {BLUE}; padding: 2.2mm 2.6mm 2mm; }}
.kpi.c {{ border-top-color: {CYAN}; }}
.kpi .l {{ font-size: 7pt; color: {GREY}; font-weight: bold; letter-spacing: 0.3pt; text-transform: uppercase; }}
.kpi .v {{ font-size: 19pt; font-weight: bold; color: {NAVY}; line-height: 1.15; }}
.kpi .v small {{ font-size: 9pt; color: {GREY}; font-weight: normal; }}
.kpi .d {{ font-size: 8.3pt; font-weight: bold; }}
.kpi .n {{ font-size: 7.4pt; color: {GREY}; }}
.row {{ display: flex; gap: 4mm; align-items: flex-start; }}
.sec {{ font-size: 8pt; font-weight: bold; color: {GREY}; letter-spacing: 0.4pt; text-transform: uppercase; margin: 0 0 1.6mm; }}
table {{ border-collapse: collapse; width: 100%; }}
th {{ background: {NAVY}; color: #fff; font-size: 7.6pt; padding: 1.4mm 1.2mm; text-align: center; font-weight: bold; }}
th.sub {{ background: {BLUE}; }}
th.l, td.l {{ text-align: left; }}
td {{ padding: 1.15mm 1.4mm; text-align: center; font-size: 8.4pt; border-bottom: 0.5pt solid {LIGHT}; }}
td.l {{ font-weight: bold; color: {NAVY}; }}
.t7 th {{ font-size: 7pt; padding: 1mm 0.8mm; }}
.t7 td {{ font-size: 7.9pt; padding: 1.05mm 0.9mm; }}
tr.alt td {{ background: {F_ALT}; }}
tr.tot td {{ background: {NAVY}; color: #fff; font-weight: bold; border: none; }}
tr.tot td.l {{ color: #fff; }}
.box {{ border: 0.75pt solid {LIGHT}; border-top: 2.2pt solid {BLUE}; padding: 2.6mm 3mm; }}
.items .it {{ display: flex; gap: 2.6mm; margin-bottom: 2.6mm; }}
.items .it:last-child {{ margin-bottom: 0; }}
.num {{ flex: 0 0 5.6mm; height: 5.6mm; border-radius: 50%; background: {BLUE}; color: #fff; font-weight: bold; font-size: 8.5pt; text-align: center; line-height: 5.6mm; margin-top: 0.4mm; }}
.it b {{ color: {NAVY}; display: block; font-size: 9pt; }}
.watch {{ background: {LIGHT}; border-left: 2.2pt solid {BLUE}; padding: 2.4mm 3.2mm; margin-top: 4mm; font-size: 8.8pt; }}
.watch b {{ color: {NAVY}; }}
.foot {{ position: absolute; left: 12mm; right: 12mm; bottom: 7mm; display: flex; justify-content: space-between; font-size: 7.2pt; color: {GREY}; border-top: 0.5pt solid {LIGHT}; padding-top: 1.6mm; }}
.foot b {{ color: {NAVY}; }}
.legend {{ display: flex; gap: 3mm; font-size: 7.2pt; color: {GREY}; margin-top: 1.4mm; align-items: center; }}
.legend i {{ display: inline-block; width: 3mm; height: 3mm; margin-right: 1mm; vertical-align: middle; border: 0.4pt solid {LIGHT}; }}
'''

def bars(items, w=300, label_w=88, row_h=21, title_note=''):
    """Diverging horizontal bars. items = [(label, value)] in GWh."""
    vmax = max(abs(v) for _, v in items) * 1.25
    plot = w - label_w - 36
    zero = label_w + plot / 2
    h = row_h * len(items) + 8
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" style="display:block">']
    s.append(f'<line x1="{zero}" y1="2" x2="{zero}" y2="{h - 2}" stroke="{GREY}" stroke-width="0.8"/>')
    for i, (lab, v) in enumerate(items):
        y = 4 + i * row_h
        bw = abs(v) / vmax * (plot / 2)
        x = zero if v >= 0 else zero - bw
        c = BLUE if v >= 0 else RED
        s.append(f'<text x="{label_w - 6}" y="{y + row_h / 2 + 3}" font-size="9" font-family="Arial" fill="{NAVY}" font-weight="bold" text-anchor="end">{lab}</text>')
        s.append(f'<rect x="{x:.1f}" y="{y + 3}" width="{max(bw, 0.8):.1f}" height="{row_h - 8}" fill="{c}"/>')
        if v < 0 and bw > 30:
            s.append(f'<text x="{x + 4:.1f}" y="{y + row_h / 2 + 3}" font-size="9" font-family="Arial" font-weight="bold" fill="#fff" text-anchor="start">{chg(v)}</text>')
        else:
            tx = x + bw + 4 if v >= 0 else x - 4
            s.append(f'<text x="{tx:.1f}" y="{y + row_h / 2 + 3}" font-size="9" font-family="Arial" font-weight="bold" fill="{c}" text-anchor="{"start" if v >= 0 else "end"}">{chg(v)}</text>')
    s.append('</svg>')
    return ''.join(s)

# =====================================================================  SALES ONE-PAGER
tot = [sum(ACT[c][i] for c in ORDER) for i in range(8)]
s26, s25, y26, y25, r26, r25, ry26, ry25 = tot
rate26, rate25 = r26 / s26, r25 / s25
rate_y26, rate_y25 = ry26 / y26, ry25 / y25
bud_sep = sum(BUD[c][1] for c in ORDER)
assert abs(s26 - 294.806) < 0.01 and abs(y26 - 2429.037) < 0.01, (s26, y26)

alcoa26, alcoa25 = 0.616, 6.922      # main Alcoa supply account (RT70)
cem26, cem25 = 9.128, 10.829         # Caribbean Cement (RT50)
rt70_dec = ACT['RT70'][0] - ACT['RT70'][1]
rt50_dec = ACT['RT50'][0] - ACT['RT50'][1]
timing = 1.6
adj_s26 = s26 + timing

bud_ytd = sum(BUD[c][2] for c in ORDER)
rows = []
def pc(v, bold=True):
    return f'<td style="color:{col(v)};font-weight:bold">{chgp(v)}</td>'
for i, c in enumerate(ORDER):
    a26, a25, ya26, ya25, ra26, ra25, rya26, rya25 = ACT[c]
    bs, by = BUD[c][1], BUD[c][2]
    rows.append(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap">{NAMES[c]}</td><td>{a26:,.1f}</td><td>{a25:,.1f}</td>{pc(a26 / a25 - 1)}'
                f'<td>{bs:,.1f}</td>{pc(a26 / bs - 1)}'
                f'<td>{ya26:,.1f}</td>{pc(ya26 / ya25 - 1)}{pc(ya26 / by - 1)}{pc(ra26 / ra25 - 1)}</tr>')
rows.append(f'<tr class="tot"><td class="l">Total system</td><td>{s26:,.1f}</td><td>{s25:,.1f}</td><td>{chgp(s26 / s25 - 1)}</td><td>{bud_sep:,.1f}</td><td>{chgp(s26 / bud_sep - 1)}</td>'
            f'<td>{y26:,.1f}</td><td>{chgp(y26 / y25 - 1)}</td><td>{chgp(y26 / bud_ytd - 1)}</td><td>{chgp(r26 / r25 - 1)}</td></tr>')
res_bud = sum(ACT[c][0] - BUD[c][1] for c in ('RT10', 'RT20'))
com_bud = sum(ACT[c][0] - BUD[c][1] for c in ('RT40', 'RT50', 'RT60-ST', 'RT70'))
two_bud = (7.130 - 0.616) + (1.903 - 0.081)

sales_html = f'''<!doctype html><html><head><meta charset="utf-8"><title>JPS Sales Analysis September 2026</title><style>{CSS}</style></head><body><div class="page">
<div class="top"><div><h1>Sales Analysis: September 2026</h1></div><div class="sub">Jamaica Public Service<br>Customer-billed volume and net revenue before GCT</div></div>
<div class="head">Sales of {s26:,.1f} GWh were {abs(s26 / s25 - 1) * 100:.1f}% below September last year and {abs(s26 / bud_sep - 1) * 100:.1f}% below budget, but revenue rose {(r26 / r25 - 1) * 100:.1f}% on a {(rate26 / rate25 - 1) * 100:.1f}% higher average rate.</div>
<div class="kpis">
 <div class="kpi"><div class="l">September sales</div><div class="v">{s26:,.1f} <small>GWh</small></div><div class="d" style="color:{RED}">{chgp(s26 / s25 - 1)} vs 2025</div><div class="n">{chg((s26 / bud_sep - 1) * 100)}% vs budget; {adj_s26:,.1f} GWh ({chgp(adj_s26 / s25 - 1)}) after billing timing</div></div>
 <div class="kpi"><div class="l">September revenue</div><div class="v">J${r26 / 1000:,.1f} <small>bn</small></div><div class="d" style="color:{BLUE}">{chgp(r26 / r25 - 1)} vs 2025</div><div class="n">Average rate J${rate26:,.1f} per kWh, {chgp(rate26 / rate25 - 1)}</div></div>
 <div class="kpi c"><div class="l">Year to date sales</div><div class="v">{y26:,.0f} <small>GWh</small></div><div class="d" style="color:{RED}">{chgp(y26 / y25 - 1)} vs 2025</div><div class="n">{chgp(y26 / bud_ytd - 1)} vs budget; {chg(y26 - y25, 0)} GWh on January to September 2025</div></div>
 <div class="kpi c"><div class="l">Year to date revenue</div><div class="v">J${ry26 / 1000:,.1f} <small>bn</small></div><div class="d" style="color:{RED}">{chgp(ry26 / ry25 - 1)} vs 2025</div><div class="n">Average rate J${rate_y26:,.1f} per kWh, {chgp(rate_y26 / rate_y25 - 1)}</div></div>
</div>
<div class="row">
 <div style="flex:2.05"><div class="sec">By rate class</div>
 <table class="t7"><tr><th class="l" rowspan="2">Rate class</th><th colspan="5">September (GWh)</th><th colspan="3">January to September</th><th rowspan="2">Sept<br>revenue<br>vs 2025</th></tr>
 <tr><th class="sub">Actual</th><th class="sub">2025</th><th class="sub">vs 2025</th><th class="sub">Budget</th><th class="sub">vs budget</th><th class="sub">GWh</th><th class="sub">vs 2025</th><th class="sub">vs budget</th></tr>
 {''.join(rows)}</table>
 <div style="font-size:7.4pt;color:{GREY};margin-top:1.4mm">RT10 includes prepaid customers. Revenue is net of GCT. January and February budgets were set equal to actuals.</div></div>
 <div style="flex:1"><div class="sec">September change vs 2025 (GWh)</div>
 {bars([(NAMES[c].split(' ')[0], ACT[c][0] - ACT[c][1]) for c in ORDER], w=250, label_w=40, row_h=15)}
 <div class="sec" style="margin-top:2mm">September variance vs budget (GWh)</div>
 {bars([(NAMES[c].split(' ')[0], ACT[c][0] - BUD[c][1]) for c in ORDER], w=250, label_w=40, row_h=15)}</div>
</div>
<div class="row" style="margin-top:4.2mm">
 <div class="box items" style="flex:1.62"><div class="sec">What moved September</div>
  <div class="it"><div class="num">1</div><div><b>Against budget, September was {abs(s26 - bud_sep):.1f} GWh short</b>RT10 and RT20 ran {res_bud:.1f} GWh above budget while RT40 to RT70 ran {abs(com_bud):.1f} GWh below. Alcoa and Caribbean Broilers account for {two_bud:.1f} GWh of that commercial gap. Year to date, sales are {y26 - bud_ytd:.1f} GWh ({(y26 / bud_ytd - 1) * 100:.1f}%) above budget.</div></div>
  <div class="it"><div class="num">2</div><div><b>Residential grew in the month</b>RT10 rose {chgp(ACT['RT10'][0] / ACT['RT10'][1] - 1)} to {ACT['RT10'][0]:.1f} GWh and RT20 {chgp(ACT['RT20'][0] / ACT['RT20'][1] - 1)}. Prepaid grew 19.5% to 3.1 GWh on 18,541 customers. Year to date RT10 is still {abs(ACT['RT10'][2] / ACT['RT10'][3] - 1) * 100:.1f}% below 2025 as the parishes hit by Hurricane Melissa recover.</div></div>
  <div class="it"><div class="num">3</div><div><b>Alcoa is the largest single swing</b>Its main supply account billed {alcoa26:.1f} GWh against {alcoa25:.1f} a year ago, {abs(alcoa26 - alcoa25):.1f} GWh or {abs((alcoa26 - alcoa25) / rt70_dec) * 100:.0f}% of the RT70 decline of {abs(rt70_dec):.1f} GWh, as it moves to self-generation. Its August and September demand charges are provisional and could come down by up to J$175 million.</div></div>
  <div class="it"><div class="num">4</div><div><b>Caribbean Cement dipped</b>{cem26:.1f} GWh against {cem25:.1f} a year ago. The {abs(cem26 - cem25):.1f} GWh fall is {abs((cem26 - cem25) / rt50_dec) * 100:.0f}% of the RT50 decline of {abs(rt50_dec):.1f} GWh, although it remains ahead of budget year to date.</div></div>
  <div class="it"><div class="num">5</div><div><b>Billing timing moved about {timing} GWh</b>Caribbean Broilers was billed for two periods in August (3.4 GWh against a normal 1.7) and only a stub in September (0.08 GWh). Adjusted, September sales are {adj_s26:,.1f} GWh, {abs(adj_s26 / s25 - 1) * 100:.1f}% below last year.</div></div>
  <div class="it"><div class="num">6</div><div><b>Rate carried revenue</b>The average rate rose {(rate26 / rate25 - 1) * 100:.1f}% in the month and {(rate_y26 / rate_y25 - 1) * 100:.1f}% year to date, so revenue is down {abs(ry26 / ry25 - 1) * 100:.1f}% year to date on volume down {abs(y26 / y25 - 1) * 100:.1f}%.</div></div>
 </div>
</div>
<div class="watch"><b>Outlook.</b> Alcoa's lost grid load is not expected to return and should be carried through year end in the fourth quarter forecast. Recovery in the parishes hit by Hurricane Melissa and in hotels is the main upside to year-end volume.</div>
<div class="foot"><span><b>Jamaica Public Service</b> | Sales Analysis | September 2026</span><span>Customer-billed basis. Variances are against the same period of 2025 and the approved budget.</span></div>
</div></body></html>'''

# =====================================================================  FORECAST ACCURACY ONE-PAGER
per = {'AUG': 0, 'SEP': 1, 'YTD': 2}
act_p = {c: {'AUG': AUG_ACT[c], 'SEP': ACT[c][0], 'YTD': ACT[c][2]} for c in ORDER}
tot_a = {p: sum(act_p[c][p] for c in ORDER) for p in per}
tot_f = {p: sum(BUD[c][per[p]] for c in ORDER) for p in per}
large = ['RT40', 'RT50', 'RT60-ST', 'RT70']
la = {p: sum(act_p[c][p] for c in large) for p in per}
le = {p: sum(ACCT_ABS[c][per[p]] for c in large) for p in per}
acct_acc = {p: 1 - le[p] / la[p] for p in per}
net = {p: acc(tot_a[p], tot_f[p]) for p in per}
com_var = sum(act_p[c]['SEP'] - BUD[c][1] for c in large)
two = (7.130 - 0.616) + (1.903 - 0.081)         # Alcoa main account and Caribbean Broilers main plant vs budget
two_share = two / abs(com_var)
assert abs(tot_a['SEP'] - s26) < 0.01

crow = []
for i, c in enumerate(ORDER):
    a, f = act_p[c]['SEP'], BUD[c][1]
    ncell = ''.join(f'<td style="background:{fill(acc(act_p[c][p], BUD[c][per[p]]))};font-weight:bold">{pct(acc(act_p[c][p], BUD[c][per[p]]))}</td>' for p in ('AUG', 'SEP', 'YTD'))
    if c in ACCT_ABS:
        acell = ''.join(f'<td style="background:{fill(1 - ACCT_ABS[c][per[p]] / act_p[c][p])};font-weight:bold">{pct(1 - ACCT_ABS[c][per[p]] / act_p[c][p])}</td>' for p in ('SEP', 'YTD'))
    else:
        acell = f'<td style="color:{GREY}">n/a</td><td style="color:{GREY}">n/a</td>'
    crow.append(f'<tr><td class="l" style="white-space:nowrap">{NAMES[c]}</td><td>{a:,.1f}</td><td>{f:,.1f}</td><td style="color:{col(a - f)};font-weight:bold">{chg(a - f)}</td>{ncell}{acell}</tr>')
crow.append(f'<tr class="tot"><td class="l">Total system</td><td>{tot_a["SEP"]:,.1f}</td><td>{tot_f["SEP"]:,.1f}</td><td>{chg(tot_a["SEP"] - tot_f["SEP"])}</td>'
            + ''.join(f'<td>{pct(net[p], 1)}</td>' for p in ('AUG', 'SEP', 'YTD')) + ''.join(f'<td>{pct(acct_acc[p], 1)}</td>' for p in ('SEP', 'YTD')) + '</tr>')

irow = []
for i, (nm, (a, f, ab, ya, yf, yab)) in enumerate(IND.items()):
    irow.append(f'<tr><td class="l" style="white-space:nowrap;font-size:8pt">{nm}</td><td>{a:,.1f}</td><td style="color:{col(a - f)};font-weight:bold">{chg(a - f)}</td>'
                f'<td style="background:{fill(acc(a, f))};font-weight:bold">{pct(acc(a, f))}</td><td style="background:{fill(1 - ab / a)};font-weight:bold">{pct(1 - ab / a)}</td>'
                f'<td style="background:{fill(acc(ya, yf))};font-weight:bold">{pct(acc(ya, yf))}</td><td style="background:{fill(1 - yab / ya)};font-weight:bold">{pct(1 - yab / ya)}</td></tr>')
hot = IND['Hotels and motels']; wat = IND['Water supply and irrigation']
legend = ''.join(f'<span><i style="background:{c}"></i>{t}</span>' for c, t in ((F_GOOD, '95% or better'), (F_MID, '85 to 95%'), (F_BAD, 'below 85%')))

acc_html = f'''<!doctype html><html><head><meta charset="utf-8"><title>JPS Forecast Accuracy September 2026</title><style>{CSS}</style></head><body><div class="page">
<div class="top"><div><h1>Forecast Accuracy: September 2026</h1></div><div class="sub">Jamaica Public Service<br>Forecast is the approved budget</div></div>
<div class="head">System sales were forecast to {pct(net['SEP'], 0)} in September, but large commercial accounts were forecast to only {pct(acct_acc['SEP'], 0)} account by account.</div>
<div class="kpis">
 <div class="kpi"><div class="l">System accuracy, September</div><div class="v">{pct(net['SEP'], 1)}</div><div class="d" style="color:{RED}">{chg(tot_a['SEP'] - tot_f['SEP'])} GWh vs forecast</div><div class="n">August {pct(net['AUG'], 1)}; January to September {pct(net['YTD'], 1)}</div></div>
 <div class="kpi"><div class="l">Large accounts, September</div><div class="v">{pct(acct_acc['SEP'], 0)}</div><div class="d" style="color:{RED}">RT40 to RT70, by account</div><div class="n">August {pct(acct_acc['AUG'], 0)}; January to September {pct(acct_acc['YTD'], 0)}</div></div>
 <div class="kpi c"><div class="l">Commercial shortfall</div><div class="v">{chg(com_var)} <small>GWh</small></div><div class="d" style="color:{RED}">RT40 to RT70 vs forecast</div><div class="n">Two accounts explain {two_share * 100:.0f}% of it</div></div>
 <div class="kpi c"><div class="l">Residential above plan</div><div class="v">{chg(act_p['RT10']['SEP'] - BUD['RT10'][1])} <small>GWh</small></div><div class="d" style="color:{BLUE}">RT10, {chgp(act_p['RT10']['SEP'] / BUD['RT10'][1] - 1, 0)} vs forecast</div><div class="n">RT20 {chg(act_p['RT20']['SEP'] - BUD['RT20'][1])} GWh</div></div>
</div>
<div class="row">
 <div style="flex:1.75"><div class="sec">By rate class</div>
 <table><tr><th class="l" rowspan="2">Rate class</th><th colspan="3">September (GWh)</th><th colspan="3">Net accuracy</th><th colspan="2">Account level</th></tr>
 <tr><th class="sub">Actual</th><th class="sub">Forecast</th><th class="sub">Variance</th><th class="sub">Aug</th><th class="sub">Sept</th><th class="sub">YTD</th><th class="sub">Sept</th><th class="sub">YTD</th></tr>
 {''.join(crow)}</table>
 <div style="font-size:7.4pt;color:{GREY};margin-top:1.4mm">Accuracy = 1 {MINUS} |actual {MINUS} forecast| ÷ actual. Account level adds up the miss on every account (RT40 to RT70 have account budgets; RT10 and RT20 are budgeted in consumption bands). January and February budgets were set equal to actuals, which lifts the year to date figures.</div></div>
 <div style="flex:1"><div class="sec">September variance vs forecast (GWh)</div>
 {bars([(NAMES[c].split(' ')[0], act_p[c]['SEP'] - BUD[c][1]) for c in ORDER], w=250, label_w=40, row_h=22)}
 <div style="font-size:7.6pt;color:{GREY};margin-top:1mm">Residential ran above forecast while RT40, RT50 and RT70 ran below, so the system total looks closer than the classes are.</div></div>
</div>
<div class="row" style="margin-top:4.2mm">
 <div style="flex:1.75"><div class="sec">Largest commercial industries</div>
 <table><tr><th class="l" rowspan="2">Industry</th><th colspan="2">September (GWh)</th><th colspan="2">September accuracy</th><th colspan="2">Jan to Sep accuracy</th></tr>
 <tr><th class="sub">Actual</th><th class="sub">Variance</th><th class="sub">Net</th><th class="sub">Account</th><th class="sub">Net</th><th class="sub">Account</th></tr>
 {''.join(irow)}</table><div class="legend">{legend}</div></div>
 <div class="box items" style="flex:1"><div class="sec">What it means</div>
  <div class="it"><div class="num">1</div><div><b>Two accounts drive the miss</b>Alcoa's move to self-generation ({chg(0.616 - 7.130)} GWh) and the Caribbean Broilers billing timing ({chg(0.081 - 1.903)} GWh) are {two_share * 100:.0f}% of the commercial shortfall.</div></div>
  <div class="it"><div class="num">2</div><div><b>Hotels are below plan</b>{chg(hot[0] - hot[1])} GWh in September, still recovering from Hurricane Melissa.</div></div>
  <div class="it"><div class="num">3</div><div><b>Totals hide account misses</b>Water supply is {pct(acc(wat[3], wat[4]))} accurate year to date in total but {pct(1 - wat[5] / wat[3])} account by account.</div></div>
  <div class="it"><div class="num">4</div><div><b>Action</b>Key account managers to refresh the outlook for the largest accounts as soon as a change is known: self-generation, outage, expansion or billing correction.</div></div>
 </div>
</div>
<div class="foot"><span><b>Jamaica Public Service</b> | Forecast Accuracy | September 2026</span><span>Customer-billed basis, September restated. Forecast is the approved budget.</span></div>
</div></body></html>'''

for name, html in (('JPS_OnePager_Sales_Analysis_Sep2026', sales_html), ('JPS_OnePager_Forecast_Accuracy_Sep2026', acc_html)):
    p = os.path.join(r'C:\Projects\Sales_Platform\analysis', '_onepager_' + name + '.html')
    open(p, 'w', encoding='utf-8').write(html)
    print('wrote', p)
print('sales', round(s26, 3), round(s25, 3), f'{(s26/s25-1)*100:.2f}%', 'rev', f'{(r26/r25-1)*100:.2f}%', 'rate', f'{(rate26/rate25-1)*100:.2f}%', 'ytd', f'{(y26/y25-1)*100:.2f}%', f'{(ry26/ry25-1)*100:.2f}%')
print('acc net', {k: round(v, 4) for k, v in net.items()}, 'acct', {k: round(v, 4) for k, v in acct_acc.items()}, 'com_var', round(com_var, 3), 'two', round(two, 3), round(two_share, 3))
