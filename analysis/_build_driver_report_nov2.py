# -*- coding: utf-8 -*-
# Sales Forecast Driver Report, FY2026-FY2028: the 7 September report updated for the October close and the refreshed forecast.
# Same eleven sections, whole book (every rate class and every customer, managed or not).
import json, os, html, re, collections
import numpy as np, pandas as pd
os.chdir(r'C:\Projects\Sales_Platform\analysis')
exec(open('_build_driver_report_nov.py', encoding='utf-8').read().split('pages = []')[0])    # data, components, helpers (T, TT, C27, C28, BC27, BC28, DR, ALL ...)
EV = json.load(open('_driver_nov_evidence.json'))
old = open(os.path.join(os.path.dirname(os.getcwd()), 'JPS_Sales_Forecast_Driver_Report.html'), encoding='utf-8').read()
STYLE = re.search(r'<style>.*?</style>', old, flags=re.S).group(0)
M = '&minus;'
def f1(x): return f'{x:,.1f}'
def sgn(x, d=1):
    return f'{abs(x):,.{d}f}' if round(x, d) == 0 else (('+' if x > 0 else M) + f'{abs(x):,.{d}f}')
def cls(x): return 'pos' if x > 0.0499 else ('neg' if x < -0.0499 else '')
def yoy(a, b): return pc(a, b) * 100
def ycell(a, b):
    v = yoy(a, b); return f'<td class="{cls(v)}">{sgn(v)}%</td>'
def gcell(v, d=1): return f'<td class="{cls(v)}">{sgn(v, d)}</td>'
CNH = {'RT10': 'RT10 Residential', 'RT20': 'RT20 Small Commercial', 'RT40': 'RT40 Commercial', 'RT50': 'RT50 Large Commercial', 'RT60-ST': 'RT60-ST Street Lighting', 'RT70': 'RT70 Industrial'}
fam27 = family(BC27); fam28 = family(BC28)
le26 = sum(sum(LE[c]['%s 26' % m] for m in MONL) for c in CL)
S = []
def add(x): S.append(x)

# ---------- svg waterfall in the report's style ----------
def wf_svg(items, w=1120, h=290):
    vals = [v for _, v in items]; run = vals[0]; levels = [run]
    for v in vals[1:-1]: run += v; levels.append(run)
    allv = [vals[0]] + levels + [vals[-1]]; lo, hi = min(allv), max(allv); pad = (hi - lo) * 0.18 or 1; lo -= pad; hi += pad * 0.5
    x0, x1, y0, y1 = 12, w - 12, 22, h - 74; n = len(items); bw = (x1 - x0) / n * 0.6
    Y = lambda v: y0 + (y1 - y0) * (hi - v) / (hi - lo)
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg" style="font-family:Arial,Helvetica,sans-serif">']
    run = vals[0]
    for i, (lab, v) in enumerate(items):
        cx = x0 + (x1 - x0) / n * (i + 0.5); bx = cx - bw / 2
        if i in (0, n - 1):
            top = Y(v); o.append(f'<rect x="{bx:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{Y(lo) - top:.1f}" fill="#0b3d66"/><text x="{cx:.1f}" y="{top - 5:.1f}" font-size="12" font-weight="bold" text-anchor="middle">{v:,.1f}</text>')
        else:
            a, b = run, run + v; top, bot = Y(max(a, b)), Y(min(a, b)); colr = '#1e7a46' if v >= 0 else '#b3261e'
            o.append(f'<rect x="{bx:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{max(bot - top, 1.5):.1f}" fill="{colr}"/><text x="{cx:.1f}" y="{top - 5:.1f}" font-size="12" font-weight="bold" text-anchor="middle">{sgn(v)}</text>'); run = b
        words = lab.split(' '); lines = []; cur = ''
        for wd in words:
            if len(cur) + len(wd) + 1 > 17 and cur: lines.append(cur); cur = wd
            else: cur = (cur + ' ' + wd).strip()
        lines.append(cur)
        for k, ln in enumerate(lines[:4]): o.append(f'<text x="{cx:.1f}" y="{y1 + 16 + k * 13:.1f}" font-size="11" text-anchor="middle" fill="#333">{html.escape(ln)}</text>')
    o.append('</svg>'); return ''.join(o)

# ---------- managed and unmanaged ----------
ALLm = ALL.copy(); ALLm['managed'] = ALLm.kam.astype(str) != ''
def split(c, col):
    s = ALLm[ALLm.rc == c]; return s[s.managed][col].sum() / G, s[~s.managed][col].sum() / G
rem = {26: out['RT20']['rem26'], 27: out['RT20']['rem27'], 28: out['RT20']['rem28']}
dk = {26: 'fy26_out', 27: 'fy27', 28: 'fy28'}

# ================= header =================
add('<!doctype html><html><head><meta charset="utf-8"><title>JPS Sales Forecast Driver Report, FY2026-FY2028</title>' + STYLE + '</head><body>')
add('<h1>Sales Forecast Driver Report</h1><div class="meta">Sales Forecasting &amp; Analysis &middot; FY2026&ndash;FY2028 &middot; 8 November 2026 &middot; Supporting detail to the Executive Summary &middot; updated for the October close</div>')
add(f'<div class="key">This report explains how the forecast moves and why. It covers total sales: every rate class and every customer, whether or not a key account manager handles it. FY2027 comes to {TT[27]:,.1f} GWh and FY2028 to {TT[28]:,.1f}, against the plan\'s {TH27:,.1f} and {TH28:,.1f}. FY2026 is our outlook: billed sales to October plus our forecast for November and December, {TT[26]:,.1f} GWh, {abs(TT[26] - le26):,.1f} GWh below the financials\' {le26:,.1f} (Section 11).</div>')

# ================= 1 =================
add('<h2>1. Three-Year Outlook by Rate Class (GWh)</h2><table><tr><th class="l">Rate Class</th><th>FY2025</th><th>FY2026</th><th>YoY</th><th>FY2027</th><th>YoY</th><th>FY2028</th><th>YoY</th></tr>')
for c in CL:
    t = T[c]; add(f'<tr><td>{CNH[c]}</td><td>{f1(t[25])}</td><td>{f1(t[26])}</td>{ycell(t[26], t[25])}<td>{f1(t[27])}</td>{ycell(t[27], t[26])}<td>{f1(t[28])}</td>{ycell(t[28], t[27])}</tr>')
add(f'<tr class="tot"><td>Total</td><td>{f1(TT[25])}</td><td>{f1(TT[26])}</td>{ycell(TT[26], TT[25])}<td>{f1(TT[27])}</td>{ycell(TT[27], TT[26])}<td>{f1(TT[28])}</td>{ycell(TT[28], TT[27])}</tr></table>')
add('<div class="note">FY2025 includes the storm months of November and December. FY2027 growth reads high because the first half of 2026 was storm-depressed; Section 2 separates that out.</div>')
add('<h3>Against the plan</h3><table><tr><th class="l">Rate Class</th><th>FY2027 forecast</th><th>FY2027 plan</th><th>Difference</th><th>FY2028 forecast</th><th>FY2028 plan</th><th>Difference</th></tr>')
for c in CL: add(f'<tr><td>{CNH[c]}</td><td>{f1(T[c][27])}</td><td>{f1(H27[c])}</td>{gcell(T[c][27] - H27[c])}<td>{f1(T[c][28])}</td><td>{f1(H28[c])}</td>{gcell(T[c][28] - H28[c])}</tr>')
add(f'<tr class="tot"><td>Total</td><td>{f1(TT[27])}</td><td>{f1(TH27)}</td>{gcell(TT[27] - TH27)}<td>{f1(TT[28])}</td><td>{f1(TH28)}</td>{gcell(TT[28] - TH28)}</tr></table>')
add(f'<div class="note">The plan is the approved budget held in the financials. RT50 is the biggest gap ({sgn(T["RT50"][27] - H27["RT50"], 0)} GWh in FY2027, {sgn(T["RT50"][28] - H28["RT50"], 0)} in FY2028). The plan lifts the whole class for storm recovery; we recover hotels property by property. RT70 is {sgn(T["RT70"][27] - H27["RT70"], 0)} GWh in FY2027, about 5 GWh of it because we take MBJ at 47% off and the KAM has 77%.</div>')
add('<h3>Managed and unmanaged customers</h3><table><tr><th class="l">Rate Class</th><th>Basis</th><th>FY2026</th><th>FY2027</th><th>FY2028</th></tr>')
tm = {26: 0, 27: 0, 28: 0}; tu = {26: 0, 27: 0, 28: 0}; tc = {26: 0, 27: 0, 28: 0}
for c in ('RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70'):
    m_ = {y: split(c, dk[y])[0] for y in (26, 27, 28)}; u_ = {y: split(c, dk[y])[1] for y in (26, 27, 28)}
    add(f'<tr><td>{CNH[c]}</td><td class="l">Managed by a KAM</td>' + ''.join(f'<td>{f1(m_[y])}</td>' for y in (26, 27, 28)) + '</tr>')
    add(f'<tr><td></td><td class="l">Not managed, billed individually</td>' + ''.join(f'<td>{f1(u_[y])}</td>' for y in (26, 27, 28)) + '</tr>')
    for y in (26, 27, 28): tm[y] += m_[y]; tu[y] += u_[y]
    if c == 'RT20':
        add('<tr><td></td><td class="l">Not billed individually (parish and bucket)</td>' + ''.join(f'<td>{f1(rem[y])}</td>' for y in (26, 27, 28)) + '</tr>')
        for y in (26, 27, 28): tc[y] += rem[y]
add('<tr><td>RT10 Residential</td><td class="l">Billed in aggregate</td>' + ''.join(f'<td>{f1(T["RT10"][y])}</td>' for y in (26, 27, 28)) + '</tr>')
for y in (26, 27, 28): tc[y] += T['RT10'][y]
add(f'<tr class="sub"><td>Managed by a KAM</td><td></td>' + ''.join(f'<td>{f1(tm[y])}</td>' for y in (26, 27, 28)) + '</tr>')
add(f'<tr class="sub"><td>Not managed, billed individually</td><td></td>' + ''.join(f'<td>{f1(tu[y])}</td>' for y in (26, 27, 28)) + '</tr>')
add(f'<tr class="sub"><td>Billed in aggregate</td><td></td>' + ''.join(f'<td>{f1(tc[y])}</td>' for y in (26, 27, 28)) + '</tr>')
add(f'<tr class="tot"><td>Total sales</td><td></td>' + ''.join(f'<td>{f1(tm[y] + tu[y] + tc[y])}</td>' for y in (26, 27, 28)) + '</tr></table>')
add(f'<div class="note">KAM-managed accounts are {tm[27] / TT[27] * 100:.0f}% of FY2027 sales. The rest is billed individually but not managed ({tu[27] / TT[27] * 100:.0f}%, mostly small RT20 premises and RT40) or billed in aggregate (residential and small commercial, {tc[27] / TT[27] * 100:.0f}%). Every figure in this report is total sales.</div>')
cem = ALL.loc['302571-686496']; ce = {26: cem.fy26_out / G, 27: cem.fy27 / G, 28: cem.fy28 / G}
add('<h3>RT50 excluding Caribbean Cement</h3><table><tr><th class="l">RT50</th><th>FY2026</th><th>FY2027</th><th>YoY</th><th>FY2028</th><th>YoY</th></tr>')
add(f'<tr><td>Caribbean Cement</td><td>{f1(ce[26])}</td><td>{f1(ce[27])}</td>{ycell(ce[27], ce[26])}<td>{f1(ce[28])}</td>{ycell(ce[28], ce[27])}</tr>')
add(f'<tr><td>All other RT50</td><td>{f1(T["RT50"][26] - ce[26])}</td><td>{f1(T["RT50"][27] - ce[27])}</td>{ycell(T["RT50"][27] - ce[27], T["RT50"][26] - ce[26])}<td>{f1(T["RT50"][28] - ce[28])}</td>{ycell(T["RT50"][28] - ce[28], T["RT50"][27] - ce[27])}</tr>')
add(f'<tr class="tot"><td>RT50 total</td><td>{f1(T["RT50"][26])}</td><td>{f1(T["RT50"][27])}</td>{ycell(T["RT50"][27], T["RT50"][26])}<td>{f1(T["RT50"][28])}</td>{ycell(T["RT50"][28], T["RT50"][27])}</tr></table>')
add(f'<div class="note">Caribbean Cement is {ce[26] / T["RT50"][26] * 100:.0f}% of RT50 in FY2026. It was not hit by the storm and its volume rose through 2026, so it gets no storm recovery, only commercial growth. October kWh were flat on September. The J$174M revenue credit on its bill is a monthly revenue item and does not change the kWh.</div>')

HOTg = HOT[HOT.hotel_up27 > 0]; gap_all_m = float((HOTg.ps - HOTg.level).sum()) / 1e6
add('<h3>What the market is telling us</h3><table><colgroup><col style="width:13%"><col style="width:50%"><col style="width:37%"></colgroup><tr><th class="l">Item</th><th class="l">What we have read</th><th class="l">In the forecast</th></tr>')
MK = [('Hotel rooms', 'About 70% of the storm-hit room stock was back by 14 September. More than 11,000 rooms return through 2027: just over 1,900 in December (Sandals Montego Bay, Sandals Royal Caribbean, Iberostar Rose Hall, Bahia Principe) and just under 3,500 in the first quarter of 2027 (Hyatt Ziva and Zilara Rose Hall, Secrets, Breathless, Jewel Grande, Catalonia). Tortuga Resorts said on 8 November it is spending over US$400m, with reopenings from the first quarter of 2027.', 'Recovery follows that schedule: 19% of each hotel\'s gap to pre-storm in January 2027, 75% by December, 80% by the end of 2028. Hotels below 30% of pre-storm get nothing until a date is confirmed (Section 10).'),
      ('Reopening dates', 'They have slipped. Sandals Montego Bay, Royal Caribbean and South Coast were due on 30 May 2026, and the Hyatt Inclusive group on 1 November 2026 (TravelPulse, February).', 'Ten points less recovery all year takes ' + f'{gap_all_m * 0.1 * 12:.1f}' + ' GWh off. The KAMs are giving us dates by property.'),
      ('Economy', 'The PIOJ said on 19 August that output could be back at its pre-Melissa level as early as April to June 2027, sooner than it expected.', 'No commercial growth until April 2027, then 1% a year.'),
      ('Alumina', 'Century Aluminum brought a new turbine (TG4) online at Jamalco in early August. The refinery now runs entirely on its own power and reached full capacity by the end of July (Gleaner, 9 August).', 'Alcoa (Jamalco) goes to zero from November. A standby load of 0.26 GWh a month would add about 3 GWh a year.'),
      ('New load', 'PriceSmart opened its Montego Bay club on 1 October and will open South Camp Road in Kingston in December (Observer, 4 November).', 'Montego Bay is in from November and Kingston from January 2027, at the 258 and 268 MWh a month the KAM entered.'),
      ('Solar policy', 'Government plans a further 100 MW of distributed solar through a strengthened net billing programme, and has opened talks with JPS on a higher net billing threshold and battery storage.', 'Not in the base. Every 10 MW would take about 14 to 15 GWh a year off (Section 7).'),
      ('Weather', 'The WMO said on 3 September that El Ni\u00f1o is firmly established, will strengthen to a very strong event peaking late in 2026 and is almost certain to last through February 2027.', 'In the base as a temperature anomaly, worth about +' + str(round(CLSJ['overlay']['wx10_27'] + CLSJ['overlay']['wx20_27'])) + ' GWh in FY2027, largest in the first quarter (Section 6).')]
for a_, b_, c_ in MK: add(f'<tr><td class="l"><b>{a_}</b></td><td class="l" style="font-size:11px">{b_}</td><td class="l" style="font-size:11px">{c_}</td></tr>')
add('</table><div class="note">Sources and how far we checked them are listed in Section 11.</div>')

# ================= 2 and 3 =================
DRL = {'Run rate against FY2026': ('Residential and commercial', 'The August to October 2026 run rate set against FY2026, which carries the storm-depressed first half. Positive where that half was depressed, negative where a customer has already stepped down, as Alcoa has.'),
       'Growth': ('All classes', 'Residential and RT20 grow 0.8% a year and commercial 1% from April 2027. In FY2028 commercial grows another 1%.'),
       'Hotel recovery': ('RT20 to RT70', 'Each hotel recovers part of its own gap to pre-storm, following the reopening schedule: 19% of the gap in January 2027, 75% by December and 80% by December 2028. Section 10.'),
       'Defections and self-generation': ('RT70, RT50, RT40', 'KAM entries for customers moving to their own generation, with our changes to Alcoa, PAC, MBJ, West Meat Packers, Sutherland and Clarendon Distillers. Section 9.'),
       'Expansions': ('RT40, RT50', 'KAM expansion entries, mostly the National Water Commission booster and relift facilities and hospitals.'),
       'Planned outages and other': ('RT70', 'The Petrojam planned shutdown (50% of trend in January and February, 10% above trend April to June) and other month-only entries.'),
       'Pipeline customers': ('RT40, RT50', 'New customers on file: PriceSmart, National Water Commission, CB Egg Farm, Restaurants of Jamaica, Continental Baking, Progressive Grocers.')}
def acct_rows(cdf, key, n=4, cols_tr=None):
    # top accounts by customer for a driver
    g = cdf.groupby(['base_ac']).agg(v=(key, 'sum'), name=('name', 'first')).reset_index()
    g = g[g.v.abs() >= 0.05]; g['a'] = g.v.abs(); return g.sort_values('a', ascending=False).head(n)
def movement(tr, bc, cdf, y0, y1, hd):
    fam = family(bc); sm = sum(fam.values())
    items = [(f'FY{y0}' + (' outlook' if y0 == 26 else ''), TT[y0])] + [(k, fam[k]) for k in DR if abs(fam[k]) >= 0.05] + [(f'FY{y1}', TT[y1])]
    add(f'<h2>{hd[0]} ({sgn(sm)} GWh)</h2><div class="wf">{wf_svg(items)}</div>')
    add(f'<div class="note">Each bar is one driver and starts where the last one finished. Together they make up the whole movement of {sgn(sm)}. The commercial drivers are measured account by account. In residential, bucket migration is the balancing driver inside the RT10 growth. The axis does not start at zero.</div>')
    add('<table><colgroup><col style="width:27%"><col style="width:14%"><col style="width:8%"><col></colgroup><tr><th class="l">Driver</th><th class="l">Rate class</th><th>GWh</th><th class="l">What drives it</th></tr>')
    for k in DR:
        if abs(fam[k]) < 0.05: continue
        add(f'<tr><td>{k}</td><td class="l">{DRL[k][0]}</td><td class="{cls(fam[k])}">{sgn(fam[k])}</td><td class="l" style="font-size:11px">{DRL[k][1]}</td></tr>')
        if k in ('Defections and self-generation', 'Expansions', 'Pipeline customers', 'Planned outages and other', 'Hotel recovery'):
            for _, r in acct_rows(cdf, k, 4).iterrows():
                nm = str(r['name']).strip(); nm = nm.title() if nm.isupper() else nm
                add(f'<tr class="sub"><td>{html.escape(nm[:40])}</td><td class="l"></td><td class="{cls(r.v)}">{sgn(r.v)}</td><td class="l"></td></tr>')
        if k == 'Run rate against FY2026':
            for c in CL:
                if abs(bc[c][k]) >= 0.5: add(f'<tr class="sub"><td>{CNH[c]}</td><td class="l"></td><td class="{cls(bc[c][k])}">{sgn(bc[c][k])}</td><td class="l"></td></tr>')
    add(f'<tr class="tot"><td>Total movement</td><td></td><td>{sgn(sm)}</td><td class="l">{f1(TT[y0])} to {f1(TT[y1])}</td></tr></table>')
    add('<div class="note">Indented rows are the largest components of the line above and are already included in it.</div>')
    heads = ['Rate Class'] + DR + ['Total']
    add('<h3>By rate class</h3><table><tr>' + ''.join(f'<th class="{"l" if i == 0 else ""}">{h}</th>' for i, h in enumerate(heads)) + '</tr>')
    for c in CL: add(f'<tr><td>{CNH[c]}</td>' + ''.join(f'<td>{sgn(bc[c][k]) if abs(bc[c][k]) >= 0.005 else chr(8212)}</td>' for k in DR) + f'<td><b>{sgn(sum(bc[c].values()))}</b></td></tr>')
    add('<tr class="tot"><td>Total</td>' + ''.join(f'<td>{sgn(fam[k])}</td>' for k in DR) + f'<td>{sgn(sm)}</td></tr></table>')
    # by industry
    ind = cdf.copy(); g = ind.groupby('ind')[DR].sum(); g['tot'] = g.sum(axis=1)
    res_row = {k: bc['RT10'][k] for k in DR}; rem_row = {k: 0.0 for k in DR}
    if tr == 27:
        gr = rem[27] * 0.008 / 1.008; rem_row['Growth'] = gr; rem_row['Run rate against FY2026'] = rem[27] - gr - rem[26]
    else: rem_row['Growth'] = rem[28] - rem[27]
    ex = pd.DataFrame([res_row, rem_row], index=['Residential (RT10)', 'Small commercial not billed individually']); ex['tot'] = ex.sum(axis=1)
    g = pd.concat([g, ex]); g = g.reindex(g.tot.abs().sort_values(ascending=False).index); top = g.head(14); rest = g.iloc[14:].sum()
    add(f'<h3>FY{y0} to FY{y1}, by industry</h3><table><tr><th class="l">Industry</th>' + ''.join(f'<th>{h}</th>' for h in DR) + '<th>Total</th></tr>')
    for nm, r in top.iterrows(): add(f'<tr><td>{html.escape(nm)}</td>' + ''.join(f'<td>{sgn(r[k]) if abs(r[k]) >= 0.005 else chr(8212)}</td>' for k in DR) + f'<td><b>{sgn(r.tot)}</b></td></tr>')
    add('<tr class="tot"><td>All other industries</td>' + ''.join(f'<td>{sgn(rest[k])}</td>' for k in DR) + f'<td>{sgn(rest.tot)}</td></tr></table>')
    # class commentary
    add(f'<div class="key"><b>What is driving each class.</b> The customers and industries behind each class movement:</div><ul>')
    for c in CL:
        d = T[c][y1] - T[c][y0]
        s = cdf[cdf.rc == c]
        txt = f'<b>{CNH[c]}, {"up" if d >= 0 else "down"} {abs(d):,.1f} GWh.</b> '
        if c in ('RT10',):
            bcc = bc[c]; txt += f'Run rate against FY2026 {sgn(bcc["Run rate against FY2026"])}, customer acquisition {sgn(bcc["Customer acquisition"])}, prepaid {sgn(bcc["Prepaid"])}, bucket migration {sgn(bcc["Bucket migration"])}, load decline {sgn(bcc["Load decline"])}, solar and net billing {sgn(bcc["Solar and net billing"])}. Residential is modelled at class level, so there is no customer split. The evidence is in Sections 4, 5 and 7.'
        else:
            g2 = s.groupby('base_ac').agg(v=('tot' if False else DR[0], 'sum'), name=('name', 'first'))
            s2 = s.copy(); s2['tot'] = s2[DR].sum(axis=1); g2 = s2.groupby('base_ac').agg(v=('tot', 'sum'), name=('name', 'first')).reset_index()
            up = g2.sort_values('v', ascending=False).head(3); dn = g2.sort_values('v').head(3)
            nm = lambda r: (str(r['name']).strip().title() if str(r['name']).strip().isupper() else str(r['name']).strip())
            if c == 'RT20': txt += f'Includes the accounts not billed individually ({sgn(bc[c]["Run rate against FY2026"] + bc[c]["Growth"] if tr == 27 else bc[c]["Growth"])} on run rate and growth). '
            txt += 'Largest increases: ' + ', '.join(f'{html.escape(nm(r)[:40])} {sgn(r.v)}' for _, r in up.iterrows() if r.v > 0.05) + '. '
            dns = ', '.join(f'{html.escape(nm(r)[:40])} {sgn(r.v)}' for _, r in dn.iterrows() if r.v < -0.05)
            txt += ('Largest decreases: ' + dns + '.') if dns else 'No customer falls by 0.05 GWh or more.'
        add(f'<li>{txt}</li>')
    add('</ul>')

# ================= residential drivers (as in the 7 September report) =================
RD = json.load(open('_driver_res_evidence.json'))
ppm = {(r[0], r[1]): r[2] for r in RD['pp']}
pp_run = sum(ppm[(2026, m)] for m in (8, 9, 10)) / 3 * 12 / 1e6            # GWh a year at the August to October rate
nbm = {(r[0], r[1]): r[2] for r in RD['nb']}
nb10_adds = nbm[(2026, 10)]['NB10'][0] - nbm[(2025, 10)]['NB10'][0]
win = [k for k in nbm if (2025, 11) <= k <= (2026, 10)]
exp_acct = sum(nbm[k]['NB10'][2] for k in win) / (sum(nbm[k]['NB10'][0] for k in win) / 12)   # kWh exported a year per registered NB10 account
SOLAR_X = 3.0                                                                     # self-consumption per kWh exported, the ratio the 7 September report carried (4.3 erosion on 1.4 observed)
sol = -nb10_adds * exp_acct * SOLAR_X / 1e6
RESK = ['Customer acquisition', 'Prepaid', 'Bucket migration', 'Load decline', 'Solar and net billing']
OV = CLSJ['overlay']; evm = {(r[0], r[1]): r[4] for r in RD['ev']}
W10_27, W20_27, W10_28, W20_28 = OV['wx10_27'], OV['wx20_27'], OV['wx10_28'], OV['wx20_28']
E26 = (sum(evm[(2026, m)] for m in range(1, 11)) + 2 * evm[(2026, 10)]) / 1e6                                 # FY2026 outlook: reloaded actuals plus November and December at the October level
EB27 = ((evm[(2026, 8)] + evm[(2026, 9)]) / 2 * 9 + evm[(2026, 10)] * 3) * 1.008 / 1e6; EB28 = EB27 * 1.008      # in the August to October base
EO27, EO28 = OV['ev_ov_27'], OV['ev_ov_28']                                                                    # the monthly trend on top
EVL27 = (EB27 - E26) + EO27; EVL28 = (EB28 - EB27) + (EO28 - EO27)
# FY2027: RT10 growth and run rate on the base excluding the overlays; EV in the base is carved out of the run rate
t27b = T['RT10'][27] - W10_27 - EO27; g27b = t27b * 0.008 / 1.008
BC27['RT10']['Growth'] = g27b; BC27['RT10']['Run rate against FY2026'] = t27b - g27b - T['RT10'][26] - (EB27 - E26)
BC27['RT20']['Run rate against FY2026'] -= W20_27
BC28['RT10']['Growth'] = T['RT10'][28] - T['RT10'][27] - (W10_28 - W10_27) - (EO28 - EO27) - (EB28 - EB27)
BC28['RT20']['Growth'] -= (W20_28 - W20_27)
def reslines(g, acq):
    L = {'Customer acquisition': acq, 'Prepaid': pp_run * 0.008, 'Load decline': -EV['decl_gwh'], 'Solar and net billing': sol}
    L['Bucket migration'] = g - sum(L.values()); return L
RL27 = reslines(BC27['RT10']['Growth'], EV['acq_net'])
RL28 = reslines(BC28['RT10']['Growth'], EV['add10'] * EV['kpp10'] * 12 / 1e6)
def resplit(bc, RL, wx, ev):
    b2 = {c: {**bc[c], **{k: 0.0 for k in RESK + ['Weather', 'EV chargers']}} for c in CL}
    b2['RT10']['Growth'] = 0.0
    for k in RESK: b2['RT10'][k] = RL[k]
    b2['RT10']['Weather'] = wx[0]; b2['RT20']['Weather'] = wx[1]; b2['RT10']['EV chargers'] = ev
    return b2
BC27, BC28 = resplit(BC27, RL27, (W10_27, W20_27), EVL27), resplit(BC28, RL28, (W10_28 - W10_27, W20_28 - W20_27), EVL28)
for tr, bc in ((27, BC27), (28, BC28)):
    for c in CL:
        d = T[c][tr] - T[c][tr - 1]; s_ = sum(bc[c].values()); assert abs(d - s_) < 0.05, ('residential drivers do not tie', tr, c, d, s_)
for k in RESK + ['Weather', 'EV chargers']: C27[k] = 0.0; C28[k] = 0.0
DR = ['Run rate against FY2026'] + RESK + ['Weather', 'EV chargers', 'Growth', 'Hotel recovery', 'Defections and self-generation', 'Expansions', 'Planned outages and other', 'Pipeline customers']
DRL.update({
  'Customer acquisition': ('RT10', 'Premises joining the grid at about 820 a month (+1.5% a year), each using the FY2026 average. Section 4.'),
  'Prepaid': ('RT10', 'Prepaid volume growing with RT10 at 0.8%. Observed growth is far higher but is mostly postpaid customers converting. Section 5.4.'),
  'Bucket migration': ('RT10', 'Households moving up the consumption bands. It is the balancing driver inside the 0.8% growth, so it moves when acquisition, load decline or solar are re-measured. Section 5.2.'),
  'Load decline': ('RT10', 'Conservation and tariff response at the two ends of the book: under 150 kWh and over 950 kWh. Section 5.3.'),
  'Solar and net billing': ('RT10', 'Registered net billers added over the year, at what each exports and what it self-consumes. Section 7.'),
  'Weather': ('RT10, RT20 residential', 'A temperature anomaly over the 2023-2025 mean at 1.93% of residential load per degree. A very strong El Niño is expected through February 2027. In FY2028 the anomaly falls back to a flat 0.09C. Section 6.'),
  'EV chargers': ('RT10', 'EV44 charging accounts, now counted in sales: the August to October level in the base and the 2026 monthly trend on top. Section 7.2.'),
  'Growth': ('Commercial and RT20', 'RT20 grows 0.8% a year and commercial 1% from April 2027. In FY2028 commercial grows another 1%.')})

movement(27, BC27, C27, 26, 27, ('2. FY2026 to FY2027 Movement by Driver', ''))
movement(28, BC28, C28, 27, 28, ('3. FY2027 to FY2028 Movement by Driver', ''))
res_base = T['RT10'][27] + EV['rt20r_27']
import numpy as np

ev_oct = evm[(2026, 10)]
add('<h3>Drivers held outside the base</h3><table><colgroup><col style="width:22%"><col style="width:16%"><col></colgroup><tr><th class="l">Driver</th><th>FY2027 GWh</th><th class="l">Why it is not in the base</th></tr>')
add('<tr><td>Government net billing expansion</td><td class="neg">&minus;14 to &minus;15 per 10 MW</td><td class="l" style="font-size:11px">A further 100 MW is planned and talks with JPS on a higher threshold and storage are open, with no dates. Section 7.</td></tr>')
add(f'<tr><td>Weather: a normal year</td><td class="neg">&minus;{W10_27 + W20_27:.0f}</td><td class="l" style="font-size:11px">The base carries the anomaly in the 7 September report. If 2027 comes in at the 2023-2025 average, this comes out. Section 6.</td></tr></table>')

# ================= 4 =================
r10 = EV['rt10']; r20 = EV['rt20r']
def mval(rows, y, m): return next(r for r in rows if r[0] == y and r[1] == m)
def comp_g(a, b, n): return ((b / a) ** (1 / n) - 1) * 100
w1 = (mval(r10, 2025, 1)[2], mval(r10, 2025, 10)[2], 9); w2 = (mval(r10, 2025, 1)[2], mval(r10, 2026, 10)[2], 21); w3 = (mval(r10, 2025, 12)[2], mval(r10, 2026, 10)[2], 10)
def wrow(lbl, w):
    a, b, n = w; mo = comp_g(a, b, n); return f'<tr><td>{lbl}</td><td>{a:,}</td><td>{b:,}</td><td>{b - a:+,}</td><td>{(b - a) / n:,.0f}</td><td>{((1 + mo / 100) ** 12 - 1) * 100:+.2f}%</td></tr>'
add('<h2>4. New Load and Customer Acquisition: The Evidence</h2>')
add(f'<div class="key">Residential growth comes from two places. New premises join the grid, and households already on it move into higher consumption bands. Premises added in FY2027 are worth about {EV["acq27"]:.1f} GWh. The rest of the rise is the current run rate, which already includes every premise connected to October (Section 5). We show them separately because they are easy to mix up.</div>')
add('<h3>4.1 The rate at which customers join</h3><p>The measure is premises connected, taken from the billed customer count for the class. RT10, compound monthly growth:</p>')
add('<table><tr><th class="l">Window</th><th>From</th><th>To</th><th>Movement</th><th>Per month</th><th>Per year</th></tr>' + wrow('Jan-Oct 2025', w1) + wrow('Jan 2025 - Oct 2026', w2) + wrow('Dec 2025 - Oct 2026', w3) + '</table>')
a, b = mval(r20, 2025, 4)[2], mval(r20, 2026, 10)[2]; mo20 = comp_g(a, b, 18)
add(f'<p>The full twenty-one-month span is adopted: {comp_g(w2[0], w2[1], w2[2]):.4f}% a month, {(w2[1] - w2[0]) / w2[2]:,.0f} premises, {((1 + comp_g(w2[0], w2[1], w2[2]) / 100) ** 12 - 1) * 100:+.2f}% a year. RT20 residential is measured from April 2025 at {mo20:.4f}% a month, {(b - a) / 18:,.0f} premises, {((1 + mo20 / 100) ** 12 - 1) * 100:+.2f}% a year. The March-to-April 2025 boundary carries a reclassification that moves roughly 5,565 premises out of RT20 residential, so any window crossing it reads as a collapse in the customer base that did not happen. The RT20 count covers the residential segment only.</p>')
add('<p>We use premises connected because it reads through the storm: it fell by 3,325 in November 2025 and was back above its October level by December.</p>')
add('<h3>4.2 What a new premise consumes</h3><p>Each premise added is assumed to consume the FY2026 average for its class, struck across the full year so that no seasonality is carried into an annual figure:</p>')
add(f'<table><tr><th class="l">Class</th><th>FY2026 sales</th><th>Average premises</th><th>kWh per premise per month</th></tr><tr><td>RT10</td><td>{T["RT10"][26]:,.1f} GWh</td><td>{EV["avg_p10"]:,.0f}</td><td>{EV["kpp10"]:,.1f}</td></tr><tr><td>RT20 residential</td><td>{EV["rt20r_26"]:,.1f} GWh</td><td>{EV["avg_p20"]:,.0f}</td><td>{EV["kpp20"]:,.1f}</td></tr></table>')
add('<h3>4.3 What the line is worth</h3><p>A premise connected in March bills for ten months of the year, not twelve, so the year carries the running total of additions rather than the year-end count:</p>')
add(f'<table><tr><th class="l">Class</th><th>Opening premises</th><th>Added in the year</th><th>FY2027 GWh</th><th>FY2028 GWh</th></tr><tr><td>RT10</td><td>{EV["open10"]:,.0f}</td><td>+{EV["add10"]:,.0f}</td><td>{EV["w10_27"]:.1f}</td><td>{EV["w10_28"]:.1f}</td></tr><tr><td>RT20 residential</td><td>{EV["open20"]:,.0f}</td><td>+{EV["add20"]:,.0f}</td><td>{EV["w20_27"]:.1f}</td><td>{EV["w20_28"]:.1f}</td></tr><tr class="tot"><td>Total</td><td></td><td>+{EV["add10"] + EV["add20"]:,.0f}</td><td>{EV["w10_27"] + EV["w20_27"]:.1f}</td><td>{EV["w10_28"] + EV["w20_28"]:.1f}</td></tr></table>')
add(f'<div class="note"><b>Sensitivity.</b> On the January-October 2025 rate the line is worth {EV["acq27_a"]:.1f} GWh; on the December 2025 to October 2026 run-rate it is {EV["acq27_b"]:.1f}. We use the longer window. A short one can pick up deferred connections catching up and read as a faster rate than the base supports.</div>')
# 4.4 bands
BNAME = {'<150': 'Under 150 kWh', '150>350': '150-350', '350>550': '350-550', '550>750': '550-750', '750>950': '750-950', 'over 950': 'Over 950', 'Prepaid': 'Prepaid'}
def band_table(label, rows_oct, rows_avg):
    od = {(r[0], r[1]): (r[2], r[3]) for r in rows_oct}; av = {(r[0], r[1]): (r[2], r[3]) for r in rows_avg}
    o = f'<table><tr><th class="l">Consumption band</th><th>Customers Oct-25</th><th>Oct-26</th><th>Change</th><th>kWh per customer per month</th><th>Change in kWh per customer (Jul-Oct)</th></tr>'
    cons = [0, 0, 0, 0]
    for b in BNAME:
        c25, k25 = od[(2025, b)]; c26, k26 = od[(2026, b)]; a25, ak25 = av[(2025, b)]; a26, ak26 = av[(2026, b)]
        kp = k26 / c26 if c26 else 0; ch = ((ak26 / a26) / (ak25 / a25) - 1) * 100 if a25 and a26 else 0
        o += f'<tr><td>{BNAME[b]}</td><td>{c25:,}</td><td>{c26:,}</td><td class="{cls(c26 - c25)}">{c26 - c25:+,}</td><td>{kp:,.1f}</td><td class="{cls(ch)}">{ch:+.1f}%</td></tr>'
        if b != 'Prepaid': cons[0] += c25; cons[1] += c26
    zc25, zc26 = od[(2025, 'Zero')][0], od[(2026, 'Zero')][0]; nc25, nc26 = od[(2025, '<Zero')][0], od[(2026, '<Zero')][0]
    tot25 = sum(v[0] for (y, b), v in od.items() if y == 2025); tot26 = sum(v[0] for (y, b), v in od.items() if y == 2026)
    o += f'<tr class="sub"><td>Consuming customers (positive kWh)</td><td>{tot25 - zc25 - nc25:,}</td><td>{tot26 - zc26 - nc26:,}</td><td></td><td></td><td></td></tr><tr class="sub"><td>Zero consumption</td><td>{zc25:,}</td><td>{zc26:,}</td><td>{zc26 - zc25:+,}</td><td></td><td></td></tr><tr class="sub"><td>Negative kWh (credit)</td><td>{nc25:,}</td><td>{nc26:,}</td><td>{nc26 - nc25:+,}</td><td></td><td></td></tr><tr class="tot"><td>Total connected premises</td><td>{tot25:,}</td><td>{tot26:,}</td><td>{tot26 - tot25:+,}</td><td></td><td></td></tr></table>'
    return o, (tot25, tot26, zc25, zc26)
add('<h3>4.4 Consumption by band</h3><p>RT10:</p>')
t10, z10 = band_table('RT10', EV['rt10oct'], EV['rt10b']); add(t10)
add(f'<p>Growth comes from the movement between bands, not from usage inside them. The two lowest bands lost customers while the bands above gained: over 350 kWh a month the customer count is {EV["heavy26"]:,} against {EV["heavy25"]:,} a year ago ({(EV["heavy26"] / EV["heavy25"] - 1) * 100:+.1f}%). Consumption per customer is close to flat in the middle bands and falls at both ends.</p>')
add(f'<p>"Consuming customers" is not the same base as total connections. Zero-consumption premises are up {z10[3] - z10[2]:,} year on year to {z10[3]:,}, likely vacant properties or accounts disconnected but not yet removed. The negative bucket holds bills that net to a credit: customers exporting more than they import and reversed or cancelled bills.</p>')
add('<p>RT20 residential (excludes RT20 commercial accounts, which carry no per-customer band data):</p>')
t20, z20 = band_table('RT20', EV['rt20oct'], EV['rt20b']); add(t20)
add(f'<p>RT20 residential is a small book relative to RT10, so a handful of accounts move its percentages. Over 950 is the exception to the flat-middle pattern: its per-customer average ({EV["o950_20"]:,.0f} kWh a month) runs well above RT10\'s equivalent band and has grown. Both are tagged segment Residential in the source data; the cause of the gap has not been investigated further.</p>')

# ================= 5 =================
add('<h2>5. Residential Demand: Macro, Migration and Load Decline</h2>')
g27 = T['RT10'][27] * 0.008 / 1.008; rb = BC27['RT10']
add(f'<div class="key">Underlying residential demand is the largest single line in the FY2027 bridge: {sgn(rb["Run rate against FY2026"] + rb["Growth"])} GWh on RT10, of which {sgn(rb["Growth"])} is growth and {sgn(rb["Run rate against FY2026"])} is the run rate set against a first half of 2026 that the storm depressed. In FY2028 it is growth only, {sgn(BC28["RT10"]["Growth"])} GWh.</div>')
add('<h3>5.1 The growth rate</h3><table><tr><th class="l">Class</th><th>FY2027</th><th>FY2028</th><th class="l">Applies to</th></tr><tr><td>RT10 residential</td><td>0.8% a year</td><td>0.8% a year</td><td class="l">August to October 2026 run rate, with prepaid</td></tr><tr><td>RT20 residential and small commercial</td><td>0.8% a year</td><td>0.8% a year</td><td class="l">Accounts and the aggregate</td></tr><tr><td>Commercial</td><td>0% to March, 1% from April</td><td>1% a year</td><td class="l">RT40, RT50, account by account</td></tr></table>')
add(f'<p>These are annual rates applied to the August to October run rate, so the rate shown is the growth the forecast carries. The 0.8% reconciles to the evidence in Section 4 like this: premises added over the period from the base months to each month of 2027 are worth about {EV["acq_net"]:.0f} GWh on RT10 at the FY2026 consumption per premise; the net growth carried is {g27:.0f} GWh. In the bridge that growth is split into customer acquisition ({RL27["Customer acquisition"]:+.1f}), prepaid ({RL27["Prepaid"]:+.1f}), load decline ({RL27["Load decline"]:+.1f}), solar and net billing ({RL27["Solar and net billing"]:+.1f}) and bucket migration ({RL27["Bucket migration"]:+.1f}). Migration is the balancing line, as it was in the 7 September report: it takes whatever the other four leave, so it moves when any of them is re-measured. Each 1% on RT10 is {T["RT10"][27] / 100:.1f} GWh.</p>')
add('<h3>5.2 Bucket migration</h3>')
add(f'<p>Bands are reassigned every month on that month\'s consumption, so a household moving from 140 to 400 kWh leaves the under-150 band and joins 350-550. October against September shows it in both directions: {EV["mig_heavy_dn_pct"]:.0f}% of the {EV["mig_heavy_s"]:,} customers using over 350 kWh in September fell to a lower band ({EV["mig_heavy_dn"]:,} customers), {EV["mig_heavy_stay"]:,} stayed and {EV["mig_heavy_up"]:,} moved up. Across all bands {EV["mig_up"]:,} customers moved up, {EV["mig_dn"]:,} moved down and {EV["mig_stay"]:,} stayed put, so the October step down is broad and seasonal and not down to a few customers.</p>')
add(f'<p>Zero-consumption customers barely moved: of {EV["z_tot"]:,} at zero in September, {EV["z_stay"]:,} are still at zero and {EV["z_back"]:,} returned to usage, while {EV["z_new"]:,} fell to zero from usage. The negative bucket is mostly one-month credits: of {EV["neg_sep"]:,} in September, only {EV["neg_stay"]} are negative again in October.</p>')
add('<h3>5.3 Load decline</h3>')
add(f'<p>Set out in section 4.4. Over July to October, consumption per customer falls at the two ends of the book: under-150 by {abs(EV["chg_u150"]):.1f}% and over-950 by {abs(EV["chg_o950"]):.1f}%, with the middle bands within {EV["mid_max"]:.1f}% either way. The two ends carry {EV["ends_share"]:.0f}% of RT10 volume, so falls of that size imply about {EV["decl_pct"]:.2f}% a year on the book, {EV["decl_gwh"]:.1f} GWh in FY2027. It is its own line in the bridge, carved out of the 0.8% net growth.</p>')
add('<h3>5.4 Prepaid</h3>')
add(f'<p>Prepaid is inside RT10 and grows with it at 0.8%. Observed over July to October 2026 against 2025, prepaid volume is {EV["pp_vol"]:+.1f}% and the customer count {EV["pp_cust"]:+.1f}% ({EV["pp_c25"]:,} to {EV["pp_c26"]:,}). That growth is substantially conversion of existing postpaid customers rather than new load, so booking the observed rate on top of the residential growth would double-count. Prepaid is worth {RL27["Prepaid"]:+.1f} GWh in FY2027 at 0.8% on about {pp_run:.0f} GWh a year. If the conversion programme accelerates, prepaid is the line to revisit.</p>')


add('<h3>5.5 The storm gap in RT10</h3>')
add('<p>The run-rate line is the largest in the bridge, so the evidence for it matters. RT10 ran well below the same month of 2025 through the storm and has been above it since mid-year:</p>')
r10m = {(r[0], r[1]): (r[2], r[3]) for r in EV['rt10']}
add('<table><tr><th class="l">RT10</th>' + ''.join(f'<th>{MONL[m - 1]}</th>' for m in range(1, 11)) + '</tr>')
add('<tr><td>2025 GWh</td>' + ''.join(f'<td>{r10m[(2025, m)][1]:,.1f}</td>' for m in range(1, 11)) + '</tr><tr><td>2026 GWh</td>' + ''.join(f'<td>{r10m[(2026, m)][1]:,.1f}</td>' for m in range(1, 11)) + '</tr>')
add('<tr><td>Change</td>' + ''.join(f'<td class="{cls(r10m[(2026, m)][1] / r10m[(2025, m)][1] * 100 - 100)}">{r10m[(2026, m)][1] / r10m[(2025, m)][1] * 100 - 100:+.1f}%</td>' for m in range(1, 11)) + '</tr>')
add('<tr><td>Premises 2026</td>' + ''.join(f'<td>{r10m[(2026, m)][0]:,}</td>' for m in range(1, 11)) + '</tr></table>')
h1 = sum(r10m[(2025, m)][1] for m in range(1, 7)) - sum(r10m[(2026, m)][1] for m in range(1, 7))
add(f'<p>January to June 2026 is {h1:,.0f} GWh below January to June 2025 with {r10m[(2026, 6)][0] - r10m[(2025, 6)][0]:,} more premises on the system. That shortfall is what the FY2027 run rate recovers.</p>')

# ================= 6 =================
add('<h2>6. Temperature</h2>')
res_base = T['RT10'][27] + EV['rt20r_27']
add(f'<div class="key">Temperature is in the base: {W10_27 + W20_27:+.1f} GWh in FY2027 (RT10 {W10_27:+.1f}, RT20 residential {W20_27:+.1f}) and {W10_28 + W20_28:+.1f} in FY2028. It is a forecast island-wide temperature anomaly against the 2023-2025 mean, converted to load at a constant 1.93% of residential load per degree Celsius.</div>')
add('<table><tr><th class="l">FY2027</th>' + ''.join(f'<th>{m}</th>' for m in MONL) + '</tr><tr><td>Anomaly, &deg;C above 2023-2025</td>' + ''.join(f'<td>{v:.3f}</td>' for v in (0.262, 0.270, 0.367, 0.252, 0.289, 0.177, 0.153, 0.133, 0.133, 0.097, 0.112, 0.068)) + '</tr><tr><td>Applied to load, % a month</td>' + ''.join(f'<td>{v * 1.93:.3f}</td>' for v in (0.262, 0.270, 0.367, 0.252, 0.289, 0.177, 0.153, 0.133, 0.133, 0.097, 0.112, 0.068)) + '</tr></table>')
add(f'<p>The profile and the sensitivity are the ones in the 7 September report. The market view supports a warm start to 2027: the WMO said on 3 September that El Ni&ntilde;o is firmly established, will strengthen to a very strong event peaking late in 2026 and is almost certain to last through February 2027. That fits an anomaly that is largest in the first quarter and fades through the year. Each 0.1&deg;C is worth about {res_base * 0.0193 * 0.1:.1f} GWh across RT10 and RT20 residential, so if 2027 comes in at the 2023-2025 average the {W10_27 + W20_27:.0f} GWh comes out.</p>')
add(f'<div class="note">FY2028 is a flat 0.090&deg;C in every month, {W10_28 + W20_28:.1f} GWh. Twelve identical months is not what weather does. It is a placeholder in the absence of a second-year outlook and the least evidenced number in the bridge. We have no temperature outlook for Jamaica of our own and the platform holds no temperature series to test the sensitivity against.</div>')

# ================= 7 =================
nb = EV['nb']
add('<h2>7. Solar, Net Billing and EV Chargers</h2>')
add('<table><tr><th class="l">RT10 bills netting to a credit</th>' + ''.join(f'<th>{MONL[r[1] - 1]}-{str(r[0])[2:]}</th>' for r in nb if r[0] == 2026) + '</tr>')
add('<tr><td>Customers</td>' + ''.join(f'<td>{r[2]:,}</td>' for r in nb if r[0] == 2026) + '</tr>')
add('<tr><td>Net export (MWh)</td>' + ''.join(f'<td>{r[3]:,.1f}</td>' for r in nb if r[0] == 2026) + '</tr>')
add('<tr><td>Credits (J$m)</td>' + ''.join(f'<td>{r[4]:,.2f}</td>' for r in nb if r[0] == 2026) + '</tr></table>')
n26 = [r for r in nb if r[0] == 2026]; sm_ = -sum(r[3] for r in n26); sj = -sum(r[4] for r in n26)
o25 = next(r for r in nb if r[0] == 2025 and r[1] == 10); o26 = next(r for r in nb if r[0] == 2026 and r[1] == 10)
add(f'<p>Ten months to October 2026: {sm_:,.0f} MWh exported and J${sj:,.2f}m in credits. October is the largest export month of 2026 at {abs(o26[3]):,.0f} MWh against {abs(o25[3]):,.0f} a year earlier ({(o26[3] / o25[3] - 1) * 100:+.0f}%), while the customer count is {o26[2]:,} against {o25[2]:,} ({(o26[2] / o25[2] - 1) * 100:+.0f}%): each net biller exports more. The bucket is also fed by reversed or cancelled bills, so the count is not a measure of solar customers.</p>')

add('<h3>7.1 Registered net billers and what they take off</h3>')
add('<p>The table above counts bills that net to a credit in the month. It also catches reversed and cancelled bills, so it is not a count of solar customers. The registered net billers, the accounts on the net billing tariffs (NB10, NB20 and NB40), are a steadier measure:</p>')
mm = [m for m in range(1, 11)]
add('<table><tr><th class="l">Registered net billers</th>' + ''.join(f'<th>{MONL[m - 1]}-26</th>' for m in mm) + '</tr>')
for t_ in ('NB10', 'NB20', 'NB40'): add(f'<tr><td>{t_} accounts</td>' + ''.join(f'<td>{nbm[(2026, m)][t_][0]:,}</td>' for m in mm) + '</tr>')
add('<tr><td>Billed net kWh (MWh)</td>' + ''.join(f'<td>{sum(nbm[(2026, m)][t_][1] for t_ in ("NB10", "NB20", "NB40")) / 1e3:,.0f}</td>' for m in mm) + '</tr>')
add('<tr><td>Exported kWh (MWh)</td>' + ''.join(f'<td>{sum(nbm[(2026, m)][t_][2] for t_ in ("NB10", "NB20", "NB40")) / 1e3:,.0f}</td>' for m in mm) + '</tr></table>')
ex26 = sum(sum(nbm[(2026, m)][t_][2] for t_ in ('NB10', 'NB20', 'NB40')) for m in mm); ex25 = sum(sum(nbm[(2025, m)][t_][2] for t_ in ('NB10', 'NB20', 'NB40')) for m in mm)
n26 = sum(nbm[(2026, 10)][t_][0] for t_ in ('NB10', 'NB20', 'NB40')); n25 = sum(nbm[(2025, 10)][t_][0] for t_ in ('NB10', 'NB20', 'NB40')); n24 = sum(nbm[(2024, 10)][t_][0] for t_ in ('NB10', 'NB20', 'NB40'))
add(f'<p>Registered net billers are {n26:,} against {n25:,} a year ago ({(n26 / n25 - 1) * 100:+.1f}%) and {n24:,} two years ago, of which NB10 residential is {nbm[(2026, 10)]["NB10"][0]:,} ({nb10_adds:+,} in the year). Exports from January to October are {ex26 / 1e6:,.2f} GWh against {ex25 / 1e6:,.2f} in 2025 ({(ex26 / ex25 - 1) * 100:+.0f}%). The registered book is growing slowly and exporting no more, so the visible solar effect is small. The risk is self-consumption, which never shows as export.</p>')
add(f'<p><b>What the bridge carries.</b> {nb10_adds} new NB10 accounts at {exp_acct:,.0f} kWh exported a year each, with self-consumption at {SOLAR_X:.0f} times the export (the ratio the 7 September report used), takes {abs(sol):.1f} GWh off RT10 in each year. This is the most judgemental number in the residential bridge. Every additional 500 net billers at the {EV["kwh_per_nb"]:,.0f} kWh a month seen in the credit bucket is about {500 * EV["kwh_per_nb"] * 12 / 1e6:.1f} GWh a year.</p>')
add('<p>Commercial solar is handled account by account: PAC (4 MW), MBJ (6 MW), Sutherland (100 kW) and the other KAM entries in Section 9. The Government plans a further 100 MW through a strengthened net billing programme, which would take roughly 14 to 15 GWh a year off for every 10 MW, and has opened talks with JPS on a higher net billing threshold and battery storage. None of that is in the base.</p>')
add('<h3>7.2 EV chargers (EV44)</h3>')
evr = {(r[0], r[1]): r for r in RD['ev']}
add('<table><tr><th class="l">EV44</th><th>Oct-24</th><th>Oct-25</th>' + ''.join(f'<th>{MONL[m - 1]}-26</th>' for m in range(1, 11)) + '</tr>')
add('<tr><td>Accounts with usage</td><td>' + f'{evr[(2024, 10)][3]}</td><td>{evr[(2025, 10)][3]}</td>' + ''.join(f'<td>{evr[(2026, m)][3]}</td>' for m in range(1, 11)) + '</tr>')
add('<tr><td>kWh (MWh)</td><td>' + f'{evr[(2024, 10)][4] / 1e3:,.1f}</td><td>{evr[(2025, 10)][4] / 1e3:,.1f}</td>' + ''.join(f'<td>{evr[(2026, m)][4] / 1e3:,.1f}</td>' for m in range(1, 11)) + '</tr></table>')
ev_slope = OV['ev_slope_kwh']
add(f'<p>EV44 is the electric vehicle charging tariff. All {evr[(2026, 10)][3]} accounts are in the name of Jamaica Public Service. The billing details report flags them as not billed, which dropped them from our sales load; Finance has confirmed that is an error and they are billed. They are now in sales, reloaded back to January 2025, which is where the RT10 history starts: {ev_oct / 1e3:,.1f} MWh in October against {evm[(2025, 10)] / 1e3:,.1f} a year earlier. Use has grown about {ev_slope / 1e3:,.1f} MWh a month through 2026.</p>')
add(f'<p><b>What the forecast carries.</b> The August to October level, about {(evm[(2026, 8)] + evm[(2026, 9)] + evm[(2026, 10)]) / 3 / 1e3:,.0f} MWh a month, is in the base. On top of it the 2026 trend continues, which adds {EO27:.1f} GWh in FY2027 and {EO28:.1f} in FY2028. EV44 is {E26:.1f} GWh in the FY2026 outlook, {EB27 + EO27:.1f} in FY2027 and {EB28 + EO28:.1f} in FY2028. The trend is a straight line through ten months and is the least evidenced number in this section. It is small in a 3,400 GWh year, but it has grown five times in twelve months.</p>')

# ================= 8 =================
add('<h2>8. Commercial Movement by Industry</h2>')
com = pd.concat([C27[C27.rc != 'RT10']]); cm = ALL[ALL.rc != 'RT10'].copy(); cm['ind'] = [ind_name(r) for _, r in cm.assign(industry=cm.industry.fillna('')).iterrows()]
cm['acc'] = 1
g = cm.groupby('ind').agg(acc=('acc', 'sum'), a26=('fy26_out', 'sum'), a27=('fy27', 'sum'), a28=('fy28', 'sum')); g[['a26', 'a27', 'a28']] /= G
g.loc['Small commercial not billed individually'] = [0, rem[26], rem[27], rem[28]]
g['d27'] = g.a27 - g.a26; g['d28'] = g.a28 - g.a27; g = g.reindex(g.d27.abs().sort_values(ascending=False).index)
add(f'<p>The commercial movement is measured account by account and aggregated to industry. This is total commercial: the account book, managed or not, plus the small commercial accounts that are not billed individually. It ties to the commercial rate classes in Section 1 ({sum(T[c][26] for c in CL if c != "RT10"):,.1f} to {sum(T[c][27] for c in CL if c != "RT10"):,.1f} to {sum(T[c][28] for c in CL if c != "RT10"):,.1f} GWh).</p>')
add('<table><tr><th class="l">Industry</th><th>Accounts</th><th>FY2026</th><th>FY2027</th><th>Change</th><th>FY2028</th><th>Change</th></tr>')
for nm, r in g.head(16).iterrows(): add(f'<tr><td>{html.escape(nm)}</td><td>{int(r.acc):,}</td><td>{f1(r.a26)}</td><td>{f1(r.a27)}</td>{gcell(r.d27)}<td>{f1(r.a28)}</td>{gcell(r.d28)}</tr>')
rest = g.iloc[16:]
add(f'<tr><td>All other industries and unclassified</td><td>{int(rest.acc.sum()):,}</td><td>{f1(rest.a26.sum())}</td><td>{f1(rest.a27.sum())}</td>{gcell(rest.d27.sum())}<td>{f1(rest.a28.sum())}</td>{gcell(rest.d28.sum())}</tr>')
add(f'<tr class="tot"><td>Total commercial</td><td>{int(g.acc.sum()):,}</td><td>{f1(g.a26.sum())}</td><td>{f1(g.a27.sum())}</td>{gcell(g.d27.sum())}<td>{f1(g.a28.sum())}</td>{gcell(g.d28.sum())}</tr></table>')
add(f'<div class="note">{int((g.d27.abs() >= 0.05).sum())} industries carry a movement of 0.05 GWh or more in FY2027. Metal ore mining and airport operations are the defections in Section 9 seen from the industry side, and hotels is the storm recovery in Section 10.</div>')

# ================= 9 =================
add('<h2>9. Commercial Defection and Self-Generation</h2>')
dfx = A_[A_.adjr == 'Defection or self-generation'].copy(); dfx['d27'] = (dfx.fy27 - dfx.fy26_out) / G; dfx['d28'] = (dfx.fy28 - dfx.fy27) / G
dfx['g'] = dfx.base_ac if 'base_ac' in dfx else [str(a).split('-')[0] for a in dfx.index]
dd = dfx.groupby('g').agg(name=('name', lambda s: s.iloc[0]), rc=('rc', lambda s: ', '.join(sorted(set(s)))), f26=('fy26_out', 'sum'), f27=('fy27', 'sum'), f28=('fy28', 'sum'), ac=('name', lambda s: s.index[0] if False else 0)).reset_index()
dd[['f26', 'f27', 'f28']] /= G; dd['d'] = dd.f27 - dd.f26; dd = dd.reindex(dd.d.sort_values().index).head(10)
basis = {'100185': 'Self-generation completed August 2026. Zero from November; October billed 0.26 GWh after a 2.0 GWh billing credit.', '804282': '6 MW PV. KAM entry is 77% off from January; we use 47% (public record supports about 60% solar).', '1411748': '4 MW PV, staged load sharing. KAM entry 80% off from October; October bills are still full, so applied from November.',
         '100312': 'Solar farm and two LNG units. 70% of load leaves by Q1 2027; applied from March.', '1164542': '100 kW PV at three sites. KAM entry 80% off; billing shows no drop, so we use 15%.', '100187': 'Two CHP units installed but idle. Held at 25% off until they run.', '288617': 'University of Technology moving to self-generation: 95% off from January 2028.'}
add(f'<p>Defection here means a customer moving to its own generation. The entries are the KAMs\', and where we changed one the reason is shown. Alcoa in our data is Jamalco, where Century Aluminum brought a new turbine online in early August and the refinery now runs on its own power. The customers below fall {abs(dd.d.sum()):,.1f} GWh in FY2027 in total. Of that, {abs(fam27["Defections and self-generation"]):,.1f} GWh is the entry applied from here; the rest is run rate, because part of FY2026 was billed before the customer stepped down (Alcoa, PAC and MBJ most of all). FY2028 carries a further {sgn(fam28["Defections and self-generation"])} GWh, mostly University of Technology.</p>')
add('<table><tr><th class="l">Customer</th><th>Class</th><th>FY2026</th><th>FY2027</th><th>Change</th><th>FY2028</th><th class="l">Basis</th></tr>')
for _, r in dd.iterrows():
    nm = str(r['name']).strip(); nm = nm.title() if nm.isupper() else nm
    add(f'<tr><td>{html.escape(nm[:34])}</td><td>{r.rc}</td><td>{f1(r.f26)}</td><td>{f1(r.f27)}</td>{gcell(r.d)}<td>{f1(r.f28)}</td><td class="l" style="font-size:11px">{html.escape(basis.get(r["g"], "KAM entry on file."))}</td></tr>')
add(f'<tr class="tot"><td>Total</td><td></td><td>{f1(dd.f26.sum())}</td><td>{f1(dd.f27.sum())}</td>{gcell(dd.d.sum())}<td>{f1(dd.f28.sum())}</td><td></td></tr></table>')
add('<div class="note">Windalco is not a defection. Its reduction in 2026 was an outage, and it is held at its run rate. Petrojam\'s September fire and planned 2027 shutdown are operational events and sit in Planned outages and other. University of Technology is the largest FY2028 mover.</div>')

# ================= 10 =================
add('<h2>10. Storm Recovery in the Commercial Book</h2>')
hot = cm[cm.hotel]; hg = hot.groupby('rc').agg(n=('hotel', 'sum'), f26=('fy26_out', 'sum'), f27=('fy27', 'sum'), f28=('fy28', 'sum')); hg[['f26', 'f27', 'f28']] /= G
HT = HOT[HOT.ps > 0]; n_rec = int((HT.hotel_up27 > 0).sum()); n_closed = int((HT.level < 0.3 * HT.ps).sum()); gap_m = float((HT[HT.hotel_up27 > 0].ps - HT[HT.hotel_up27 > 0].level).sum()) / 1e6
add(f'<p>Hotels across all rate classes, {int(hot.shape[0])} accounts, move from {hot.fy26_out.sum() / G:,.1f} GWh in FY2026 to {hot.fy27.sum() / G:,.1f} in FY2027 and {hot.fy28.sum() / G:,.1f} in FY2028. Of the FY2027 step, {HOT.hotel_up27.sum() / G:,.1f} GWh is recovery we model explicitly and the rest is the run rate against a storm-depressed first half of 2026.</p>')
add('<table><tr><th class="l">Rate class</th><th>Hotel accounts</th><th>FY2026</th><th>FY2027</th><th>Change</th><th>FY2028</th><th>Change</th></tr>')
for c, r in hg.iterrows(): add(f'<tr><td>{CNH[c]}</td><td>{int(r.n):,}</td><td>{f1(r.f26)}</td><td>{f1(r.f27)}</td>{gcell(r.f27 - r.f26)}<td>{f1(r.f28)}</td>{gcell(r.f28 - r.f27)}</tr>')
add(f'<tr class="tot"><td>Total</td><td>{int(hg.n.sum()):,}</td><td>{f1(hg.f26.sum())}</td><td>{f1(hg.f27.sum())}</td>{gcell(hg.f27.sum() - hg.f26.sum())}<td>{f1(hg.f28.sum())}</td>{gcell(hg.f28.sum() - hg.f27.sum())}</tr></table>')
add(f'<p>The market gives us a schedule. About 70% of the affected rooms were back by mid-September, just over 1,900 more return in December and just under 3,500 in the first quarter of 2027, with the rest through 2027. We apply that to each property\'s own gap to its pre-storm level, the average month of January to September 2025: 19% of the gap in January 2027, 40% by May, 75% by December and 80% by the end of 2028. Not all of a reopened room\'s load comes back. Arrivals are still well down and a hotel that is not full still carries its fixed load, so we stop at 80%.</p>')
add(f'<p>{n_rec} properties recover. {n_closed} are below 30% of their pre-storm level and get nothing until a KAM gives us a reopening date; the Tortuga rebuild from the first quarter of 2027 is the kind of date we are asking for. The gap across the properties that recover is {gap_m:.1f} GWh a month. Reopening dates have slipped before, so ten points less recovery all year would take {gap_m * 0.1 * 12:.1f} GWh off.</p>')
add('<p>Before, we applied storm normalisation by rate class (RT50 at 4.66% a month, RT40 and RT20 smaller). It reached accounts the storm never touched and lifted RT50 by 24% in FY2027, which is why RT50 sits below the plan now. The property-by-property recovery above replaces it. RT10 needs none because its storm gap closed inside FY2026: it ran 12.5% and 15.4% below prior year in January and February, went above prior year in May and has been 3% to 5% above since July. Industrial carries none beyond hotels, after the class-wide adjustment was withdrawn on 29 August.</p>')

# ================= 11 =================
add('<h2>11. Basis of Preparation</h2>')
add(f'<p><b>FY2025</b> is billed actual. <b>FY2026</b> is January to October billed actual plus our forecast for November and December, {TT[26]:,.1f} GWh. It is {abs(TT[26] - le26):,.1f} GWh below the financials\' latest estimate of {le26:,.1f}: residential and RT20 are about {abs(sum(T[c][26] - sum(LE[c]["%s 26" % m] for m in MONL) for c in ("RT10", "RT20"))):,.0f} GWh short because the LE holds October to December flat on September while usage normally falls, and the commercial classes are ahead of it. The 19 August submission (3,282.0 GWh) stays frozen as the number of record.</p>')
add(f'<p><b>FY2027 and FY2028</b> are projected account by account. Each account starts from the median of its August, September and October 2026 kWh, so one odd month does not drive it, and is shaped by the average pattern of 2024 and 2025 (75% weight on 2025), both before the storm; October to December follow the October level and the 2024 pattern. Commercial accounts grow 1% a year from April 2027 and again in 2028, residential and small commercial 0.8%. Hotels recover on the reopening schedule in Section 10. The KAM adjustments on file are applied as the platform does (a percentage on the trend forecast, manual kWh added) through 2028, and the pipeline customers enter from their start month. Residential and the RT20 accounts that are not billed individually are projected at class level with the same method.</p>')
add(f'<p><b>What changed from the 7 September report.</b> The engine\'s macro, weather, solar and storm-normalisation drivers are replaced by the drivers in Sections 2 and 3, each measured account by account. FY2027 moves from 3,439.6 to {TT[27]:,.1f} GWh and FY2028 from 3,514.8 to {TT[28]:,.1f}. In FY2027 RT50 and RT70 move the most. In FY2028 residential is {abs(T["RT10"][28] - H28["RT10"]):,.0f} GWh and RT50 {abs(T["RT50"][28] - H28["RT50"]):,.0f} GWh below the plan, and RT40 {abs(T["RT40"][28] - H28["RT40"]):,.0f} GWh above it, because the earlier RT40 forecast was flat and this one grows 1%.</p>')
add(f'<p><b>Adjustments.</b> {len(ENT)} entries are on file; {int((ENT.treat == "Applied").sum())} are applied as entered, {int((ENT.treat == "Replaced by analyst override").sum())} replaced by our changes (Section 9 and the Petrojam shutdown), {int((ENT.treat == "Replaced by account-level hotel recovery").sum())} class-wide storm recovery entries replaced by hotel recovery by property, and {int((ENT.treat.isin(["Past month, in actuals", "Beyond 2028"])).sum())} fall outside the horizon or are already in actuals. The KAMs are reviewing the forecast now and their changes will move this report.</p>')
add('<p><b>Open items.</b> EV44 before January 2025, which is before the RT10 history starts. Reopening dates for the properties below 30% of pre-storm. MBJ commissioning date and storage. Whether Alcoa keeps a standby load (about 3 GWh a year). When the PAC reduction shows in the bills. Whether the 7,742 zero-kWh premises return (about 8 GWh). The seasonal pattern weighting moves the total by about 22 GWh either way.</p>')
add('<p><b>System losses</b> and the Sales &amp; Generation workbook are unchanged by this update. The workbook will carry these class totals once the KAM review closes.</p>')
add('<h3>Sources</h3><p style="font-size:11px">Read in full: Jamaica Gleaner, 14 September 2026 (room stock and reopening schedule, Ministry of Tourism, JAPEX); TravelPulse, 15 February 2026 (original reopening dates); Jamaica Gleaner, 9 August 2026 (Jamalco TG4); WMO press release, 3 September 2026 (El Ni&ntilde;o). Headline and opening paragraph read: Jamaica Gleaner, 8 November 2026 (Tortuga Resorts); Jamaica Observer, 19 August 2026 (PIOJ) and 4 November 2026 (PriceSmart South Camp Road); PriceSmart Jamaica site (Montego Bay opening); Government of Jamaica renewable energy tender notice (net billing). Search summary only, to be opened before quoting outside the company: Caribbean Journal, 13 July 2026 (stayover arrivals); Rio Times (Sangster arrivals, August); Jamaica Observer, 25 September 2026 (Rusal and Windalco); JIS (MBJ solar); Jamaica Gleaner, 30 July 2026 (cement volumes).</p>')
add('<p style="margin-top:18px;color:#666;font-size:11px">Prepared by Sales Forecasting &amp; Analysis. Figures in GWh unless stated.</p></body></html>')
open('JPS_Sales_Forecast_Driver_Report_Nov2026.html', 'w', encoding='utf-8').write('\n'.join(S)); print('written', len(''.join(S)))
