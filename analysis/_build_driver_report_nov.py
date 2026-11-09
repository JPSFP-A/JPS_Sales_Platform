# -*- coding: utf-8 -*-
# Sales Forecast Driver Report FY2027-FY2028, refreshed for the October 2026 close and the account-level forecast.
import json, os, re, html, collections
import numpy as np, pandas as pd
os.chdir(r'C:\Projects\Sales_Platform\analysis')
src = open('_build_onepagers.py', encoding='utf-8').read()
exec(src.split('# =====================================================================  SALES ONE-PAGER')[0])   # CSS, colours, helpers
def chg(x, d=1):
    s_ = f'{abs(x):,.{d}f}'
    return s_ if round(x, d) == 0 else (('+' if x > 0 else MINUS) + s_)
def chgp(x, d=1): return chg(x * 100, d) + '%'
pc = lambda a, b: (a / b - 1) if b else 0.0
ALL = pd.read_pickle(r'_cust\kam_fy27_accounts.pkl'); ENT = pd.read_pickle(r'_cust\kam_fy27_entries.pkl'); HOT = pd.read_pickle(r'_cust\kam_fy27_hotels.pkl')
CLSJ = json.load(open(r'_cust\kam_fy27_class.json')); META = json.load(open(r'_cust\kam_fy27_meta.json'))
BYC = json.load(open('_fy27_byclass.json')); LE = json.load(open('_oct_deep.json'))['le']; RES = json.load(open('_fy27_result.json'))
MONL = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
G = 1e6
CL = ['RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']
CN = {'RT10': 'RT10 Residential', 'RT20': 'RT20 Small commercial', 'RT40': 'RT40 Commercial', 'RT50': 'RT50 Large commercial', 'RT60-ST': 'RT60 Street lighting', 'RT70': 'RT70 Industrial'}
# ---------------- class totals ----------------
out = CLSJ['out']
def tot(c, y):
    o = out[c]; k = {26: ('total26', 'acct26', 'rem26'), 27: ('total27', 'acct27', 'rem27'), 28: ('total28', 'acct28', 'rem28')}[y]
    return o.get(k[0], o.get(k[1], 0) + o.get(k[2], 0))
T = {c: {25: BYC[c]['fy25'], 26: tot(c, 26), 27: tot(c, 27), 28: tot(c, 28)} for c in CL}
H27 = {c: sum(LE[c]['%s 27' % m] for m in MONL) for c in CL}; H28 = {c: sum(LE[c]['%s 28' % m] for m in MONL) for c in CL}
TT = {y: sum(T[c][y] for c in CL) for y in (25, 26, 27, 28)}; TH27, TH28 = sum(H27.values()), sum(H28.values())
# ---------------- driver components ----------------
pipe_mask = ALL.index.astype(str).str.startswith('NEW')
A_ = ALL[~pipe_mask].copy(); P_ = ALL[pipe_mask].copy()
DR = ['Run rate against FY2026', 'Growth', 'Hotel recovery', 'Defections and self-generation', 'Expansions', 'Planned outages and other', 'Pipeline customers']
def comps27(df, pipe=False):
    d = pd.DataFrame(index=df.index)
    for k in DR: d[k] = 0.0
    if pipe:
        d['Pipeline customers'] = (df.fy27 - df.fy26_out) / G; return d
    d['Run rate against FY2026'] = (df.base27_ng - df.fy26_out) / G; d['Growth'] = (df.base27 - df.base27_ng) / G; d['Hotel recovery'] = df.hotel_up27 / G
    adj = (df.fy27 - df.base27 - df.hotel_up27) / G
    for k, name in (('Defection or self-generation', 'Defections and self-generation'), ('Expansion', 'Expansions')):
        d[name] = np.where(df.adjr == k, adj, 0.0)
    d['Planned outages and other'] = np.where(df.adjr.isin(['Planned outage', 'Other', '']) | df.adjr.isna(), adj, 0.0)
    return d
def comps28(df, pipe=False):
    d = pd.DataFrame(index=df.index)
    for k in DR: d[k] = 0.0
    if pipe:
        d['Pipeline customers'] = (df.fy28 - df.fy27) / G; return d
    d['Growth'] = (df.base28 - df.base27) / G; d['Hotel recovery'] = (df.hotel_up28 - df.hotel_up27) / G
    adj = ((df.fy28 - df.base28 - df.hotel_up28) - (df.fy27 - df.base27 - df.hotel_up27)) / G
    for k, name in (('Defection or self-generation', 'Defections and self-generation'), ('Expansion', 'Expansions')):
        d[name] = np.where(df.adjr == k, adj, 0.0)
    d['Planned outages and other'] = np.where(df.adjr.isin(['Planned outage', 'Other', '']) | df.adjr.isna(), adj, 0.0)
    return d
C27 = pd.concat([comps27(A_), comps27(P_, True)]); C28 = pd.concat([comps28(A_), comps28(P_, True)])
for d_ in (C27, C28): d_['rc'] = ALL.rc; d_['industry'] = ALL.industry.fillna(''); d_['hotel'] = ALL.hotel; d_['name'] = ALL.name; d_['kam'] = ALL.kam; d_['base_ac'] = [str(a) if str(a).startswith('NEW') else str(a).split('-')[0] for a in d_.index]
def by_class(cdf, tr):
    rows = {}
    for c in CL:
        if c in ('RT10',) or c == 'RT20':
            pass
        s = cdf[cdf.rc == c]
        r = {k: s[k].sum() for k in DR}
        rows[c] = r
    # class-level pieces: RT10 and the RT20 accounts not billed individually
    for c, (f0, f1, g0) in (('RT10', (T['RT10'][26], T['RT10'][27], 0.008)),):
        if tr == 27: gr = f1 * g0 / (1 + g0); rows[c]['Growth'] = gr; rows[c]['Run rate against FY2026'] = f1 - gr - f0
        else: rows[c]['Growth'] = T['RT10'][28] - T['RT10'][27]
    rem26, rem27, rem28 = out['RT20']['rem26'], out['RT20']['rem27'], out['RT20']['rem28']
    if tr == 27: gr = rem27 * 0.008 / 1.008; rows['RT20']['Growth'] += gr; rows['RT20']['Run rate against FY2026'] += rem27 - gr - rem26
    else: rows['RT20']['Growth'] += rem28 - rem27
    return rows
BC27, BC28 = by_class(C27, 27), by_class(C28, 28)
for tr, bc in ((27, BC27), (28, BC28)):
    for c in CL:
        d = T[c][tr] - T[c][tr - 1]; s_ = sum(bc[c].values())
        assert abs(d - s_) < 0.05, (tr, c, d, s_)
print('components tie to class movements')
# ---------------- helpers: table, waterfall ----------------
def waterfall(items, w=560, h=250, unit='GWh', start_lbl='', end_lbl=''):
    vals = [v for _, v in items]
    cum = [0.0]
    for v in vals[1:-1]: cum.append(cum[-1] + v)
    run = vals[0]; levels = [run]
    for v in vals[1:-1]: run += v; levels.append(run)
    allv = [vals[0]] + levels + [vals[-1]]; lo = min(allv); hi = max(allv); pad = (hi - lo) * 0.15 or 1; lo -= pad; hi += pad * 0.6
    x0, x1, y0, y1 = 10, w - 10, 14, h - 62; n = len(items); bw = (x1 - x0) / n * 0.62
    Y = lambda v: y0 + (y1 - y0) * (hi - v) / (hi - lo)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" style="display:block">']
    run = vals[0]; prev = vals[0]
    for i, (lab, v) in enumerate(items):
        cx = x0 + (x1 - x0) / n * (i + 0.5); bx = cx - bw / 2
        if i == 0 or i == n - 1:
            top, bot, colr = Y(v), Y(lo), NAVY; txt = f'{v:,.0f}'
            o.append(f'<rect x="{bx:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{bot - top:.1f}" fill="{colr}"/>')
            o.append(f'<text x="{cx:.1f}" y="{top - 4:.1f}" font-size="8.5" font-weight="bold" font-family="Arial" text-anchor="middle" fill="#1F1F1F">{txt}</text>')
        else:
            a, b = run, run + v; top, bot = Y(max(a, b)), Y(min(a, b)); colr = GREEN if v >= 0 else RED
            o.append(f'<rect x="{bx:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{max(bot - top, 1):.1f}" fill="{colr}"/>')
            o.append(f'<text x="{cx:.1f}" y="{top - 4:.1f}" font-size="8.5" font-weight="bold" font-family="Arial" text-anchor="middle" fill="#1F1F1F">{chg(v, 1)}</text>')
            run = b
        words = lab.split(' '); lines = []; cur = ''
        for wd in words:
            if len(cur) + len(wd) + 1 > 15 and cur: lines.append(cur); cur = wd
            else: cur = (cur + ' ' + wd).strip()
        lines.append(cur)
        for k, ln in enumerate(lines[:4]): o.append(f'<text x="{cx:.1f}" y="{y1 + 11 + k * 9:.1f}" font-size="7.4" font-family="Arial" text-anchor="middle" fill="#3C4A5A">{html.escape(ln)}</text>')
    o.append('</svg>'); return ''.join(o)
def family(bc):
    tot_ = {k: sum(bc[c][k] for c in CL) for k in DR}; return tot_
def sent(t, n=170):
    t = str(t or '').strip()
    if len(t) <= n: return t
    cut = t[:n]; k = max(cut.rfind('. '), cut.rfind('; '))
    return (cut[:k + 1] if k > 40 else cut.rsplit(' ', 1)[0] + '...')
def tbl(heads, rows, cls='t7', first_left=True, widths=None):
    h = ''.join(f'<th class="{"l" if (i == 0 and first_left) else ""}">{x}</th>' for i, x in enumerate(heads))
    return f'<table class="{cls}"><tr>{h}</tr>{"".join(rows)}</table>'
def cell(v, d=1, bold=False, color=True):
    if v is None: return '<td>\u2014</td>'
    st = f'color:{col(v)};' if color else ''
    return f'<td style="{st}{"font-weight:bold;" if bold else ""}">{chg(v, d)}</td>'
IND_SHORT = {'Wired and Wireless Telecommunications Carriers (except Satellite)': 'Telecommunications', 'Water Supply and Irrigation Systems': 'Water supply and irrigation', 'Other Metal Ore Mining': 'Mining (Alcoa)',
             'General Medical and Surgical Hospitals': 'Hospitals', 'Colleges, Universities, and Professional Schools': 'Colleges and universities', 'Telemarketing Bureaus and Other Contact Centers': 'Contact centres',
             'Hotels (except Casino Hotels) and Motels': 'Hotels and motels'}
def ind_name(r):
    if r['hotel']: return 'Hotels and resorts'
    i = (r['industry'] or '').strip()
    if not i: return 'Not classified'
    return IND_SHORT.get(i, i)[:40]
for d_ in (C27, C28): d_['ind'] = d_.apply(ind_name, axis=1)

pages = []
FOOT = '<div class="foot"><span><b>Jamaica Public Service</b> | Sales Forecast Driver Report | November 2026</span><span>GWh billed including prepaid. FY2026 is the outlook: January to October actual plus our forecast for November and December.</span></div>'
def page(n, ttl, sub, head, body):
    pages.append(f'<div class="page"><div class="top"><div><h1>{ttl}</h1></div><div class="sub">Jamaica Public Service | page {n} of NP<br>{sub}</div></div><div class="head">{head}</div>{body}{FOOT}</div>')

# ================= page 1: outlook =================
rows = []
for i, c in enumerate(CL):
    t = T[c]
    rows.append(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="font-weight:bold">{CN[c]}</td><td>{t[25]:,.1f}</td><td>{t[26]:,.1f}</td>{cell(pc(t[26], t[25]) * 100, 1)[:-5]}%</td><td style="font-weight:bold">{t[27]:,.1f}</td>{cell(pc(t[27], t[26]) * 100, 1)[:-5]}%</td><td style="font-weight:bold">{t[28]:,.1f}</td>{cell(pc(t[28], t[27]) * 100, 1)[:-5]}%</td><td>{H27[c]:,.1f}</td>{cell(t[27] - H27[c])}<td>{H28[c]:,.1f}</td>{cell(t[28] - H28[c])}</tr>')
rows.append(f'<tr class="tot"><td class="l">Total</td><td>{TT[25]:,.1f}</td><td>{TT[26]:,.1f}</td><td>{chgp(pc(TT[26], TT[25]))}</td><td>{TT[27]:,.1f}</td><td>{chgp(pc(TT[27], TT[26]))}</td><td>{TT[28]:,.1f}</td><td>{chgp(pc(TT[28], TT[27]))}</td><td>{TH27:,.1f}</td><td>{chg(TT[27] - TH27)}</td><td>{TH28:,.1f}</td><td>{chg(TT[28] - TH28)}</td></tr>')
# bars: class totals by year
def outlook_chart(w=560, h=200):
    mx = max(T[c][y] for c in ('RT10', 'RT20', 'RT40', 'RT50', 'RT70') for y in (25, 26, 27, 28)) * 1.08
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" style="display:block">']
    cs = ['RT10', 'RT20', 'RT40', 'RT50', 'RT70']; gw = (w - 40) / len(cs); bw = gw / 5.4; cols_ = ['#B8C4D2', '#7F95AE', BLUE, NAVY]
    for i, c in enumerate(cs):
        for k, y in enumerate((25, 26, 27, 28)):
            v = T[c][y]; bh = (h - 44) * v / mx; x = 30 + i * gw + k * (bw + 2) + gw * 0.1
            o.append(f'<rect x="{x:.1f}" y="{h - 26 - bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{cols_[k]}"/><text x="{x + bw / 2:.1f}" y="{h - 29 - bh:.1f}" font-size="6.6" font-family="Arial" text-anchor="middle" fill="#1F1F1F">{v:,.0f}</text>')
        o.append(f'<text x="{30 + i * gw + gw * 0.5:.1f}" y="{h - 12}" font-size="8" font-family="Arial" text-anchor="middle" fill="#3C4A5A">{CN[c]}</text>')
    for k, (y, lab) in enumerate(zip(cols_, ('FY2025', 'FY2026 outlook', 'FY2027', 'FY2028'))):
        o.append(f'<rect x="{30 + k * 100}" y="2" width="8" height="8" fill="{y}"/><text x="{42 + k * 100}" y="9.5" font-size="8" font-family="Arial" fill="#3C4A5A">{lab}</text>')
    o.append('</svg>'); return ''.join(o)
cc_ = T['RT50']
fy27_vs = TT[27] - TH27; fy28_vs = TT[28] - TH28
page(1, 'Three-year outlook by rate class', 'FY2025 to FY2028, GWh',
     f'We forecast {TT[27]:,.0f} GWh in FY2027, level with the plan, and {TT[28]:,.0f} GWh in FY2028, {abs(fy28_vs):,.0f} GWh ({abs(pc(TT[28], TH28)) * 100:.1f}%) {"below" if fy28_vs < 0 else "above"} it. Residential and commercial growth is mostly 2026 returning to normal; the mix against the plan is different.',
     f'<div class="sec">Outlook by rate class</div>' + tbl(['Rate class', 'FY2025 actual', 'FY2026 outlook', 'YoY', 'FY2027', 'YoY', 'FY2028', 'YoY', 'FY2027 plan', 'vs plan', 'FY2028 plan', 'vs plan'], rows) +
     f'<div class="small">The plan is the approved budget held in the financials. FY2025 includes the storm months of November and December. YoY on FY2026 is flattered by the storm-depressed first half of 2026.</div>' +
     f'<div class="row" style="margin-top:3.4mm"><div style="flex:1.4"><div class="sec">By rate class, GWh</div>{outlook_chart()}</div>'
     f'<div style="flex:1"><div class="sec">What to take from it</div><div class="box items"><ul>'
     f'<li><b>FY2027 is {chg(TT[27] - TT[26], 0)} GWh on FY2026</b>, of which {chg(sum(BYC[c]["h1"] for c in CL), 0)} GWh falls in January to June. That half was depressed by the storm in 2026; July to December is {chg(sum(BYC[c]["h2"] for c in CL), 0)} GWh.</li>'
     f'<li><b>FY2028 adds {chg(TT[28] - TT[27], 0)} GWh</b>: growth, the slower tail of hotel recovery, and the full-year effect of 2027 customers. It is {abs(TT[28] - TH28):,.0f} GWh below the plan because the plan carries faster RT50 and residential growth.</li>'
     f'<li><b>RT70 falls {abs(T["RT70"][27] - T["RT70"][26]):,.0f} GWh in FY2027</b> as Alcoa, PAC and MBJ move to their own generation. It is the only class that shrinks.</li>'
     f'<li><b>Against the plan</b> RT50 is {abs(T["RT50"][27] - H27["RT50"]):,.0f} GWh lower in FY2027 and RT70 {abs(T["RT70"][27] - H27["RT70"]):,.0f} GWh higher; the rest is within 5 GWh a class.</li></ul></div></div></div>')

# ================= pages 2 and 3: movement FY26->27 and FY27->28 =================
def move_page(n, tr, bc, cdf, y0, y1, ttl, head):
    fam = family(bc); items = [(f'FY{y0} outlook' if y0 == 26 else f'FY{y0}', TT[y0])] + [(k, fam[k]) for k in DR if abs(fam[k]) >= 0.05] + [(f'FY{y1}', TT[y1])]
    sm = sum(fam.values()); assert abs(sm - (TT[y1] - TT[y0])) < 0.1, (sm, TT[y1] - TT[y0])
    heads = ['Rate class'] + ['Run rate against FY2026', 'Growth', 'Hotel recovery', 'Defections and self-generation', 'Expansions', 'Planned outages and other', 'Pipeline customers'] + ['Total']
    rows = []
    for i, c in enumerate(CL):
        r = bc[c]; rows.append(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="font-weight:bold">{CN[c]}</td>' + ''.join(cell(r[k]) if abs(r[k]) >= 0.005 else '<td style="color:#999">\u2014</td>' for k in DR) + cell(sum(r.values()), bold=True) + '</tr>')
    rows.append('<tr class="tot"><td class="l">Total</td>' + ''.join(f'<td>{chg(fam[k])}</td>' for k in DR) + f'<td>{chg(sm)}</td></tr>')
    # industry table
    ind = cdf.copy(); ind['tot'] = ind[DR].sum(axis=1)
    # class-level pieces as their own lines
    g = ind.groupby('ind')[DR].sum(); g['tot'] = g.sum(axis=1)
    res_row = {k: bc['RT10'][k] for k in DR}
    rem_row = {k: 0.0 for k in DR}
    if tr == 27:
        gr = out['RT20']['rem27'] * 0.008 / 1.008; rem_row['Growth'] = gr; rem_row['Run rate against FY2026'] = out['RT20']['rem27'] - gr - out['RT20']['rem26']
    else: rem_row['Growth'] = out['RT20']['rem28'] - out['RT20']['rem27']
    extra = pd.DataFrame([res_row, rem_row], index=['Residential (RT10)', 'Small commercial not billed individually']); extra['tot'] = extra.sum(axis=1)
    g = pd.concat([g, extra]); g = g.reindex(g.tot.abs().sort_values(ascending=False).index)
    top = g.head(12); rest = g.iloc[12:].sum()
    irows = []
    for i, (nm, r) in enumerate(top.iterrows()):
        irows.append(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap">{html.escape(nm)}</td>' + ''.join(cell(r[k]) if abs(r[k]) >= 0.005 else '<td style="color:#999">\u2014</td>' for k in DR) + cell(r['tot'], bold=True) + '</tr>')
    irows.append('<tr class="tot"><td class="l">All other industries</td>' + ''.join(f'<td>{chg(rest[k])}</td>' for k in DR) + f'<td>{chg(rest["tot"])}</td></tr>')
    expl = {27: ('Run rate against FY2026 is the August to October run rate set against FY2026, which carries the storm-depressed first half. It is positive where that half was depressed and negative where a customer has already stepped down, as Alcoa has. Growth is 1% on commercial from April and 0.8% on residential and small commercial. Hotel recovery closes 30% of each property\'s gap to pre-storm in January, rising to 62%. Defections are the KAM entries and our changes (Alcoa, PAC, MBJ, West Meat Packers, Sutherland, Clarendon Distillers). Expansions are the KAM entries, mostly National Water Commission.',),
            28: ('FY2028 has no base effect: every month is the same month of 2027 grown by the annual rate. Hotel recovery moves from 62% to 70% of the gap. Adjustments move because entries made for 2027 apply for a full year (the pipeline customers and National Water Commission expansions) or start in 2028 (University of Technology, Spanish Town Hospital).',)}[tr]
    body = (f'<div class="sec">Movement by driver, GWh</div>{waterfall(items, w=720, h=215)}'
            f'<div class="small" style="margin-bottom:2mm">{expl[0]}</div>'
            f'<div class="sec" style="margin-top:2mm">By rate class</div>' + tbl(heads, rows) +
            f'<div class="sec" style="margin-top:3mm">By industry, largest movements</div>' + tbl(['Industry'] + heads[1:], irows) +
            f'<div class="small">Account-level drivers are computed account by account and add to the class movement exactly. Residential and the small commercial accounts that are not billed individually are modelled at class level: growth and run rate only.</div>')
    page(n, ttl, f'FY{y0} to FY{y1}, GWh', head, body)
fam27 = family(BC27); fam28 = family(BC28)
move_page(2, 27, BC27, C27, 26, 27, f'FY2026 to FY2027: movement by driver', f'FY2027 is {chg(TT[27] - TT[26], 1)} GWh on FY2026. Most of it is base returning to normal ({chg(fam27["Run rate against FY2026"], 0)} GWh): the first half of 2026 was depressed by the storm. Growth adds {chg(fam27["Growth"], 0)}, hotels {chg(fam27["Hotel recovery"], 0)} and the pipeline {chg(fam27["Pipeline customers"], 0)}, while customers leaving the grid take {abs(fam27["Defections and self-generation"]):,.0f} GWh off.')
move_page(3, 28, BC28, C28, 27, 28, f'FY2027 to FY2028: movement by driver', f'FY2028 is {chg(TT[28] - TT[27], 1)} GWh on FY2027, and it is growth ({chg(fam28["Growth"], 0)} GWh) and the tail of hotel recovery ({chg(fam28["Hotel recovery"], 0)}). Expansions that start or run a full year add {chg(fam28["Expansions"], 0)}; defections and planned outages net to {chg(fam28["Defections and self-generation"] + fam28["Planned outages and other"], 0)} GWh.')

# ================= page 4: customer movements =================
def cust_table(cdf, tr):
    d = cdf.copy(); d['tot'] = d[DR].sum(axis=1)
    g = d.groupby(['kam', 'base_ac']).agg(**{k: (k, 'sum') for k in DR}, tot=('tot', 'sum'), name=('name', lambda s: s.iloc[np.argmax([abs(x) for x in d.loc[s.index, 'tot']])]), cls=('rc', lambda s: ', '.join(sorted(set(s))))).reset_index()
    g = g[g.kam.astype(str) != ''] if False else g
    return g
def driver_txt(r):
    parts = []
    for k in DR:
        if abs(r[k]) >= 0.05: parts.append(f'{k.lower().replace("fy2026", "FY2026")} {chg(r[k])}')
    return ', '.join(parts)
def mover_rows(cdf, tr, n=12):
    g = cust_table(cdf, tr); up = g.sort_values('tot', ascending=False).head(n); dn = g.sort_values('tot').head(n)
    def rows(df):
        o = []
        for i, (_, r) in enumerate(df.iterrows()):
            nm = str(r['name']).strip(); nm = nm.title() if nm.isupper() else nm
            o.append(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap">{html.escape(nm[:32])}</td><td class="l">{r["kam"] or "\u2014"}</td>{cell(r["tot"], 2, True)}<td class="l" style="font-size:6.8pt">{html.escape(driver_txt(r))}</td></tr>')
        return ''.join(o)
    return rows(up), rows(dn)
u27, d27 = mover_rows(C27, 27); u28, d28 = mover_rows(C28, 28)
hdr = '<tr><th class="l">Customer</th><th class="l">KAM</th><th>GWh</th><th class="l">Drivers, GWh</th></tr>'
cs = lambda t: t.replace('<td class="l" style="font-size:6.8pt">', '<td class="l" style="font-size:6.8pt;font-weight:normal">')
page(4, 'Customers behind the movement, FY2027', 'FY2026 to FY2027, GWh',
     'A short list of customers carries the year. Alcoa, MBJ and PAC explain the fall in RT70; hotels, National Water Commission and the pipeline explain most of the rise.',
     f'<div class="sec">Largest increases</div><table class="t7">{hdr}{cs(u27)}</table><div class="sec" style="margin-top:3.2mm">Largest decreases</div><table class="t7">{hdr}{cs(d27)}</table>'
     f'<div class="small">Customers are grouped across all their accounts. Drivers add to the customer total.</div>')
page(5, 'Customers behind the movement, FY2028', 'FY2027 to FY2028, GWh',
     'FY2028 is a smaller movement, led by the National Water Commission expansions running a full year, hotels and pipeline customers. University of Technology is the one large decrease.',
     f'<div class="sec">Largest increases</div><table class="t7">{hdr}{cs(u28)}</table><div class="sec" style="margin-top:3.2mm">Largest decreases</div><table class="t7">{hdr}{cs(d28)}</table>'
     f'<div class="small">Customers are grouped across all their accounts. Drivers add to the customer total.</div>')

# ================= page 5: hotels =================
hh = HOT[HOT.ps > 0].copy(); hh['pct'] = hh.level / hh.ps
rec = hh[hh.hotel_up27 > 0].sort_values('hotel_up27', ascending=False); closed = hh[hh.level < 0.3 * hh.ps].sort_values('ps', ascending=False)
hr = ''
for i, (ac, h) in enumerate(rec.head(14).iterrows()):
    nm = str(h['name']).strip(); nm = nm.title() if nm.isupper() else nm
    hr += f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap">{html.escape(nm[:34])}</td><td class="l">{h.kam or ""}</td><td>{h.rc}</td><td>{h.ps / 1e3:,.0f}</td><td>{h.level / 1e3:,.0f}</td><td>{h.pct * 100:.0f}%</td>{cell(h.hotel_up27 / G, 2)}{cell(h.hotel_up28 / G, 2)}</tr>'
cr = ''
for i, (ac, h) in enumerate(closed.head(8).iterrows()):
    nm = str(h['name']).strip(); nm = nm.title() if nm.isupper() else nm
    cr += f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap">{html.escape(nm[:34])}</td><td class="l">{h.kam or ""}</td><td>{h.rc}</td><td>{h.ps / 1e3:,.0f}</td><td>{h.level / 1e3:,.0f}</td><td>{h.pct * 100:.0f}%</td></tr>'
gap_all = float((hh.ps - hh.level).clip(lower=0).sum()) / 1e3
page(6, 'Hotel recovery', 'By property, MWh a month unless stated',
     f'Hotels add {HOT.hotel_up27.sum() / G:,.0f} GWh in FY2027 and a further {(HOT.hotel_up28.sum() - HOT.hotel_up27.sum()) / G:,.0f} GWh in FY2028. We recover part of each property\'s own gap to pre-storm, not a class-wide rate, and give nothing to the {len(closed)} properties still below 30% of their pre-storm level until a reopening date is confirmed.',
     f'<div class="row"><div style="flex:1.4"><div class="sec">Largest recoveries in the forecast</div><table class="t7"><tr><th class="l">Property</th><th class="l">KAM</th><th>Class</th><th>Pre-storm</th><th>Now</th><th>Now %</th><th>FY27 GWh</th><th>FY28 GWh</th></tr>{hr}</table></div></div>'
     f'<div class="row" style="margin-top:3mm"><div style="flex:1.2"><div class="sec">Below 30% of pre-storm: no recovery assumed</div><table class="t7"><tr><th class="l">Property</th><th class="l">KAM</th><th>Class</th><th>Pre-storm</th><th>Now</th><th>Now %</th></tr>{cr}</table></div>'
     f'<div style="flex:1"><div class="sec">The assumption</div><div class="box items"><ul><li>Pre-storm is the average month of January to September 2025. Now is the middle month of August to October 2026.</li><li>We close 30% of the gap in January 2027, rising to 62% in December and 70% by December 2028. The remainder reflects arrivals still about 20% down and the fixed load of a hotel that is not full.</li><li>The gap across properties that recover is {sum((HOT[HOT.hotel_up27 > 0].ps - HOT[HOT.hotel_up27 > 0].level)) / 1e3:,.0f} MWh a month. Ten points more or less recovered all year is {abs(float((HOT[HOT.hotel_up27 > 0].ps - HOT[HOT.hotel_up27 > 0].level).sum()) * 0.10 * 12) / G:,.1f} GWh.</li><li>The KAMs are asked to give reopening dates by property.</li></ul></div></div></div>')

# ================= page 6: adjustments and pipeline =================
adj_rows = []
reason = {'Defection or self-generation': 'Defections and self-generation', 'Expansion': 'Expansions', 'Planned outage': 'Planned outages and other', 'Other': 'Planned outages and other'}
A2 = A_.copy(); A2['adj27'] = (A2.fy27 - A2.base27 - A2.hotel_up27) / G; A2['adj28'] = (A2.fy28 - A2.base28 - A2.hotel_up28) / G
A2 = A2[A2.adjr.astype(str) != '']
top_adj = A2.reindex(A2.adj27.abs().sort_values(ascending=False).index).head(10)
ar = ''
for i, (ac, a) in enumerate(top_adj.iterrows()):
    nm = str(a['name']).strip(); nm = nm.title() if nm.isupper() else nm
    why = META['OVERRIDE'].get(ac, '')
    ar += f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap">{html.escape(nm[:30])}</td><td class="l">{a.kam or ""}</td><td class="l">{a.adjr}</td>{cell(a.adj27, 2, True)}{cell(a.adj28, 2)}<td class="l" style="font-size:6.6pt">{html.escape(sent(why, 190))}</td></tr>'
byr = A2.groupby('adjr').agg(n=('fy27', 'count'), a27=('adj27', 'sum'), a28=('adj28', 'sum'))
br_ = ''.join(f'<tr class="{"alt" if i % 2 else ""}"><td class="l">{k}</td><td>{int(v.n):,}</td>{cell(v.a27)}{cell(v.a28)}</tr>' for i, (k, v) in enumerate(byr.iterrows()))
def pipe_note(ac, p):
    cols = ['m2026%02d' % m for m in (11, 12)] + ['m2027%02d' % m for m in range(1, 13)] + ['m2028%02d' % m for m in range(1, 13)]
    lab = ['Nov 2026', 'Dec 2026'] + [f'{MONL[m - 1]} 2027' for m in range(1, 13)] + [f'{MONL[m - 1]} 2028' for m in range(1, 13)]
    first = next((i for i, c in enumerate(cols) if p[c] > 0), None)
    base = f'Starts {lab[first]} at {p[cols[first]] / 1e3:,.0f} MWh a month.' if first is not None else 'No volume yet.'
    return base + (' ' + sent(p.note, 90) if 'On file' not in str(p.note) and str(p.note) != 'New customer on file.' else '')
P2 = P_.copy(); pr = ''
for i, (ac, p) in enumerate(P2.sort_values('fy27', ascending=False).iterrows()):
    nm = str(p['name']).strip()
    pr += f'<tr class="{"alt" if i % 2 else ""}"><td class="l">{html.escape(nm[:34])}</td><td class="l">{p.kam or ""}</td><td>{p.rc}</td>{cell(p.fy27 / G, 2)}{cell(p.fy28 / G, 2)}<td class="l" style="font-size:6.6pt">{html.escape(pipe_note(ac, p))}</td></tr>'
page(7, 'KAM adjustments and pipeline customers', 'Entries on file and customers expected, GWh',
     f'The adjustments on file take {abs(sum(r.a27 for _, r in byr.iterrows())):,.0f} GWh off FY2027 net, almost all of it customers moving to their own generation, and the pipeline customers add {P2.fy27.sum() / G:,.0f} GWh. Several entries were changed or replaced; the reason is shown.',
     f'<div class="row"><div style="flex:1"><div class="sec">Adjustments by type</div><table class="t7"><tr><th class="l">Type</th><th>Accounts</th><th>FY2027 GWh</th><th>FY2028 GWh</th></tr>{br_}</table></div>'
     f'<div style="flex:1"><div class="sec">How they are applied</div><div class="box"><div style="font-size:8.2pt">A percentage entry is applied to the trend forecast for the account and manual kWh are added. Defection, expansion and renewal entries stay in force until the next entry for the account. Operational disruption entries apply to the months entered. We replaced entries that were solved against the platform engine rather than entered at face value (the Petrojam shutdown) and the class-wide storm recovery entries, which are now hotel recovery by property.</div></div></div></div>'
     f'<div class="sec" style="margin-top:3mm">Largest account effects</div><table class="t7"><tr><th class="l">Account</th><th class="l">KAM</th><th class="l">Type</th><th>FY27 GWh</th><th>FY28 GWh</th><th class="l">What we did</th></tr>{ar}</table>'
     f'<div class="sec" style="margin-top:3mm">Pipeline customers in the forecast</div><table class="t7"><tr><th class="l">Customer</th><th class="l">KAM</th><th>Class</th><th>FY27 GWh</th><th>FY28 GWh</th><th class="l">Note</th></tr>{pr}</table>')

# ================= page 7: residential =================
WM = json.load(open('_oct_who_moved.json')); WB = WM['bands']; MG = WM['mig']
BO = ['<Zero', 'Zero', '<150', '150>350', '350>550', '550>750', '750>950', 'over 950']
BL = {'<Zero': 'Negative kWh (credit)', 'Zero': 'Zero kWh', '<150': 'Under 150', '150>350': '150 to 350', '350>550': '350 to 550', '550>750': '550 to 750', '750>950': '750 to 950', 'over 950': 'Over 950'}
bro = ''
for i, b in enumerate(BO):
    c26, c25, c24 = WB['o26'][b][0], WB['s26'][b][0], WB['o25'][b][0]
    bro += f'<tr class="{"alt" if i % 2 else ""}"><td class="l">{BL[b]}</td><td>{c26:,}</td>{cell(c26 - c25, 0)}{cell(c26 - c24, 0)}<td>{WB["o26"][b][1] / 1e6:.2f}</td></tr>'
r10 = T['RT10']; gr27 = r10[27] * 0.008 / 1.008
zr = z['2026-10'] - z['2025-10'] if 'z' in globals() else 7742
page(8, 'Residential demand', 'RT10 and the residential share of RT20',
     f'Residential grows {chgp(pc(r10[27], r10[26]))} in FY2027 and {chgp(pc(r10[28], r10[27]))} in FY2028. Only {gr27:,.0f} GWh of the FY2027 rise is growth; {r10[27] - r10[26] - gr27:,.0f} GWh is the first half of 2026 returning to normal.',
     f'<div class="row"><div style="flex:1"><div class="sec">RT10 customers by bucket, October 2026</div><table class="t7"><tr><th class="l">Bucket (kWh a month)</th><th>Customers</th><th>vs Sep</th><th>vs Oct 25</th><th>GWh</th></tr>{bro}</table><div class="small">Postpaid customers billed in the month. Prepaid is not in the buckets.</div></div>'
     f'<div style="flex:1"><div class="sec">What we assume</div><div class="box items"><ul>'
     f'<li><b>Level.</b> The August and September 2026 mean, with prepaid, shaped by the 2024 and 2025 seasonal pattern. October to December follow the October level and the 2024 pattern, so the usual fall in November and December is in.</li>'
     f'<li><b>Growth.</b> 0.8% a year: customers about +1.5% less solar and efficiency drag. FY2028 repeats it. Each 1% is {r10[27] / 100:.1f} GWh.</li>'
     f'<li><b>Zero kWh.</b> {zr:,} more premises are at zero consumption than before the storm and are not assumed to return. If they all do by mid-2027 residential rises about {r10[27] * 0.013 / 2:.0f} GWh.</li>'
     f'<li><b>Weather.</b> No weather overlay. A warmer year is upside; the platform holds no temperature series to size it.</li>'
     f'<li><b>Net billing.</b> No expansion beyond today\'s base. The government target of 100 MW distributed would be a downside of roughly 14 to 15 GWh for every 10 MW.</li>'
     f'</ul></div></div></div>'
     f'<div class="sec" style="margin-top:3mm">What the October movement tells us</div><div class="box items"><ul>'
     f'<li>38% of customers using over 350 kWh in September fell to a lower bucket in October, so the step down is broad and seasonal, not a few customers.</li>'
     f'<li>Zero-kWh customers barely moved: of 59,059 at zero in September, 51,120 are still at zero.</li>'
     f'<li>The negative bucket is mostly one-month credits: of 1,027 in September, only 8 are negative again in October.</li></ul></div>')

# ================= page 8: against the plan and risks =================
prow = ''
for i, c in enumerate(CL):
    prow += f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="font-weight:bold">{CN[c]}</td><td>{T[c][27]:,.1f}</td><td>{H27[c]:,.1f}</td>{cell(T[c][27] - H27[c], 1, True)}<td>{T[c][28]:,.1f}</td><td>{H28[c]:,.1f}</td>{cell(T[c][28] - H28[c], 1, True)}</tr>'
prow += f'<tr class="tot"><td class="l">Total</td><td>{TT[27]:,.1f}</td><td>{TH27:,.1f}</td><td>{chg(TT[27] - TH27)}</td><td>{TT[28]:,.1f}</td><td>{TH28:,.1f}</td><td>{chg(TT[28] - TH28)}</td></tr>'
hg = float((HOT[HOT.hotel_up27 > 0].ps - HOT[HOT.hotel_up27 > 0].level).sum())
sens = [('Each 1% on residential (RT10)', r10[27] / 100), ('Each 1% on RT20', T['RT20'][27] / 100), ('Each 1% on RT40', T['RT40'][27] / 100),
        ('Hotel gap closed 10 points higher all year', hg * 0.10 * 12 / G), ('MBJ at 77% off instead of 47%', -0.30 * ALL.at['804282-768320', 'level'] * 12 / G),
        ('PAC reduction slips to July 2027', 0.8 * ALL.at['1411748-834411', 'level'] * 6 / G), ('Alcoa keeps its October standby load', 259407 * 12 / G),
        ('Zero-kWh premises back by mid-2027', r10[27] * 0.013 / 2), ('Seasonal pattern: 2025 only, or equal weight on 2024 and 2025', 22.0)]
srow = ''.join(f'<tr class="{"alt" if i % 2 else ""}"><td class="l">{a}</td>{cell(v, 1)}</tr>' for i, (a, v) in enumerate(sens))
page(9, 'Against the plan, and what could move it', 'FY2027 and FY2028, GWh',
     f'We are {abs(TT[27] - TH27):,.1f} GWh from the plan in FY2027 and {abs(TT[28] - TH28):,.0f} GWh below it in FY2028. The totals hide a different mix: RT50 and RT70 are the two classes where we disagree with the plan.',
     f'<div class="sec">Forecast against the plan by class</div><table class="t7"><tr><th class="l">Rate class</th><th>FY27 forecast</th><th>FY27 plan</th><th>vs plan</th><th>FY28 forecast</th><th>FY28 plan</th><th>vs plan</th></tr>{prow}</table>'
     f'<div class="row" style="margin-top:3.4mm"><div style="flex:1"><div class="sec">Sensitivities, FY2027 GWh</div><table class="t7"><tr><th class="l">Lever</th><th>GWh</th></tr>{srow}</table></div>'
     f'<div style="flex:1"><div class="sec">Why we differ from the plan</div><div class="box items"><ul>'
     f'<li><b>RT50, {chg(T["RT50"][27] - H27["RT50"], 0)} GWh in FY2027.</b> The plan lifts the whole class for storm recovery. We recover hotels property by property and hold the rest of the class at its run rate.</li>'
     f'<li><b>RT70, {chg(T["RT70"][27] - H27["RT70"], 0)} GWh.</b> About 5 GWh is MBJ at 47% off, not the KAM\'s 77%; the rest is run-rate treatment of Petrojam and Windalco and a smaller assumed loss at PAC.</li>'
     f'<li><b>FY2028, {chg(T["RT10"][28] - H28["RT10"], 0)} GWh on residential and {chg(T["RT50"][28] - H28["RT50"], 0)} on RT50.</b> The plan carries faster growth in both than the trend supports.</li>'
     f'<li><b>Not in the base.</b> The Windalco pilot (about 12 GWh), FLOW cell sites, NWC solar, net billing expansion. All are probability-weighted in the revenue-at-risk register, not here.</li></ul></div></div></div>')

NP = len(pages)
doc = f'''<!doctype html><html><head><meta charset="utf-8"><title>JPS Sales Forecast Driver Report FY2027 to FY2028</title><style>{CSS}
.page {{ page-break-after: always; }} .page:last-child {{ page-break-after: auto; }} .top h1 {{ font-size: 18pt; white-space: nowrap; }} .head {{ font-size: 11pt; margin: 3mm 0 2.6mm; }}
.t7 td {{ padding: 0.7mm 0.9mm; font-size: 7.4pt; }} .t7 th {{ font-size: 6.7pt; padding: 0.8mm 0.7mm; }} .box ul {{ margin: 0; padding-left: 4mm; font-size: 8pt; }} .box li {{ margin-bottom: 1.1mm; }} .small {{ font-size: 7.2pt; color: {GREY}; margin-top: 1.2mm; }}
</style></head><body>{"".join(pages).replace("NP", str(NP))}</body></html>'''
open('_driver_report_nov.html', 'w', encoding='utf-8').write(doc); print('pages', NP)
print('family27', {k: round(v, 1) for k, v in fam27.items()}); print('family28', {k: round(v, 1) for k, v in fam28.items()})
