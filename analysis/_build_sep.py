# -*- coding: utf-8 -*-
# Regenerates JPS_Sales_Analysis_Requirements_Sep2026.html for January-September 2026.
import json, re, collections
import _sep_data as D

HTML = r'C:\Projects\Sales_Platform\JPS_Sales_Analysis_Requirements_Sep2026.html'
EX = json.load(open('_report_extras.json'))
M = '&minus;'

def n(x, dec=0):
    x = round(x, dec) + 0.0
    s = f'{abs(x):,.{dec}f}'
    return (M + s) if x < 0 else s
def pct(a, b): return (b / a - 1) * 100 if a else 0.0
def sg(x, dec=0): return ('+' if x > 0 else '') + n(x, dec)
def chg(a, b, dec=0, pdec=2, cls=True):
    d = b - a; p = pct(a, b); c = ('pos' if d > 0 else 'neg' if d < 0 else '') if cls else ''
    return f'<td class="{c}">{sg(d, dec)} ({("+" if p > 0 else "")}{n(p, pdec)}%)</td>'
def pc(a, b, pdec=1, cls=True):
    p = pct(a, b); c = ('pos' if p > 0 else 'neg' if p < 0 else '') if cls else ''
    return f'<td class="{c}">{("+" if p > 0 else "")}{n(p, pdec)}%</td>'
def PU(a, b, pdec=1): return f'{abs(pct(a, b)):.{pdec}f}%'
def P(a, b, pdec=1): return f'{("+" if pct(a, b) > 0 else "")}{n(pct(a, b), pdec)}%'
def tbl(head, rows, total=None):
    LC = ' class="l"'
    out = '<table>\n<tr>' + ''.join('<th%s>%s</th>' % (LC if i == 0 else '', h) for i, h in enumerate(head)) + '</tr>\n' + '\n'.join(rows)
    if total: out += '\n' + total
    return out + '\n</table>'

# =============== core series ===============
G = ('post', 'pp', 'com')
def S(g, y, i, m): return D.series(g, y, i)[m - 1]
YT = lambda g, y, i: D.ytd(g, y, i)
ALLK = {y: sum(YT(g, y, 1) for g in G) / 1e6 for y in (2025, 2026)}
ALLR = {y: sum(YT(g, y, 2) for g in G) / 1e6 for y in (2025, 2026)}
SEPK = {y: sum(S(g, y, 1, 9) for g in G) / 1e6 for y in (2025, 2026)}
CUSTS = {y: sum(D.cust(g, y, 9) for g in G) for y in (2025, 2026)}
months_down = sum(1 for m in range(1, 10) if sum(S(g, 2026, 1, m) for g in G) < sum(S(g, 2025, 1, m) for g in G))
rate = {y: ALLR[y] / ALLK[y] * 1000 for y in (2025, 2026)}   # J$ per kWh (rev J$M / kWh GWh -> *1000)

def seg_table(g):
    a25, a26 = D.cust(g, 2025, 9), D.cust(g, 2026, 9)
    return ('<table>\n<tr><th class="l">Metric</th><th>Sep 2025</th><th>Sep 2026</th><th>Change</th></tr>\n'
            f'<tr><td class="l">Customers</td><td>{n(a25)}</td><td>{n(a26)}</td>{chg(a25, a26)}</tr>\n'
            f'<tr><td class="l">Sales (GWh, month)</td><td>{n(S(g,2025,1,9)/1e6,2)}</td><td>{n(S(g,2026,1,9)/1e6,2)}</td>{chg(S(g,2025,1,9)/1e6, S(g,2026,1,9)/1e6, 2)}</tr>\n'
            f'<tr><td class="l">Sales YTD (GWh, Jan&ndash;Sep)</td><td>{n(YT(g,2025,1)/1e6,1)}</td><td>{n(YT(g,2026,1)/1e6,1)}</td>{chg(YT(g,2025,1)/1e6, YT(g,2026,1)/1e6, 1)}</tr>\n'
            f'<tr><td class="l">Revenue YTD (J$M)</td><td>{n(YT(g,2025,2)/1e6)}</td><td>{n(YT(g,2026,2)/1e6)}</td>{chg(YT(g,2025,2)/1e6, YT(g,2026,2)/1e6)}</tr>\n</table>')

# Alcoa facts from the raw cache
_d = json.load(open('corrected.json', encoding='utf-8')); _AL = _d['acct_legend']; _ix = {k: i for i, k in enumerate(_AL)}
alc = {'25': [0.0, 0.0], '26': [0.0, 0.0]}   # [all classes, RT70 only]
for _c, _a in _d['acct'].items():
    if _a['name'].upper().startswith('ALCOA'):
        for mo, v in _a['m'].items():
            if '2025-01' <= mo <= '2025-09': alc['25'][0] += v[_ix['kwh']]; alc['25'][1] += v[_ix['kwh']] if _a['title'] == 'RT70' else 0
            if '2026-01' <= mo <= '2026-09': alc['26'][0] += v[_ix['kwh']]; alc['26'][1] += v[_ix['kwh']] if _a['title'] == 'RT70' else 0
alc_ytd_chg = pct(alc['25'][0], alc['26'][0])
alc_sep = {y: sum(v[_ix['kwh']] for a in _d['acct'].values() if a['name'].upper().startswith('ALCOA') for mo, v in a['m'].items() if mo == f'{y}-09') / 1e6 for y in (2025, 2026)}
alc_sep_loss = alc_sep[2025] - alc_sep[2026]
com_sep_dec = S('com', 2025, 1, 9) / 1e6 - S('com', 2026, 1, 9) / 1e6

# =============== 1b composition ===============
RES = D.res_components()
def comp_dict():
    out = {}
    for y in (2025, 2026):
        c = dict(cust=0, energy=0, dem=0, fuel=0, ipp=0, rev=0)
        for k in D._K:
            v = D._K[k][y]; va = D._KA[k][y] if k in D._KA else (0,) * 7
            c['cust'] += (v[0] + va[0]) / 1e6; c['energy'] += (v[1] + va[1]) / 1e6; c['dem'] += (v[2] + va[2]) / 1e6
            c['fuel'] += (v[3] + va[3]) / 1e6; c['ipp'] += (v[4] + va[4]) / 1e6; c['rev'] += (v[5] + va[5]) / 1e6
        out[y] = c
    return out
COM = comp_dict()
RC = {'res': {y: dict(cust=RES[y]['cust'], energy=RES[y]['energy'], dem=0.0, fuel=RES[y]['fuel'], ipp=RES[y]['ipp'], rev=RES[y]['rev']) for y in (2025, 2026)}, 'com': COM}
for k in RC:
    for y in RC[k]:
        r = RC[k][y]; r['nonfuel'] = r['cust'] + r['energy'] + r['dem']; r['other'] = r['rev'] - r['nonfuel'] - r['fuel'] - r['ipp']
PPREV = {y: YT('pp', y, 2) / 1e6 for y in (2025, 2026)}
GRAW = D.gct_raw()
RT20C_GCT = {y: (D._K['RT20c'][y][6] + D._KA['RT20c'][y][6]) / 1e6 for y in (2025, 2026)}
GCT = {'res': {y: YT('post', y, 3) / 1e6 for y in (2025, 2026)},
       'pp': {y: YT('pp', y, 3) / 1e6 for y in (2025, 2026)},
       'com': {y: RT20C_GCT[y] + GRAW[y] for y in (2025, 2026)}}
# prepaid tax was not loaded for June 2026 -> estimate at the neighbouring-month effective rate
_pp = D.series('pp', 2026, 2); _pg = D.series('pp', 2026, 3)
_jun_rate = ((_pg[4] / _pp[4]) + (_pg[6] / _pp[6])) / 2
GCT['pp'][2026] += _pp[5] * _jun_rate / 1e6
CB = {y: {k: RC['res'][y][k] + RC['com'][y][k] for k in ('cust', 'energy', 'dem', 'nonfuel', 'fuel', 'ipp', 'other')} for y in (2025, 2026)}
for y in (2025, 2026):
    CB[y]['rev'] = RC['res'][y]['rev'] + RC['com'][y]['rev'] + PPREV[y]
    CB[y]['gct'] = GCT['res'][y] + GCT['pp'][y] + GCT['com'][y]
    RC['res'][y]['gct'] = GCT['res'][y]; RC['com'][y]['gct'] = GCT['com'][y]
# reconcile composition to the segment view
for y in (2025, 2026):
    assert abs(CB[y]['rev'] - ALLR[y]) < 5, (y, CB[y]['rev'], ALLR[y])

def comp_table(get, sub, prepaid=None):
    rows = []
    def row(label, k, s=False):
        a, b = get(2025)[k], get(2026)[k]
        rows.append(f'<tr{" class=\"sub\"" if s else ""}><td class="l">{label}</td><td>{n(a)}</td><td>{n(b)}</td>{chg(a,b,0,1,cls=False)}<td>{n(b/get(2026)["rev"]*100,1)}%</td></tr>')
    row('Non-fuel charges (customer + energy + demand)', 'nonfuel')
    if sub:
        row('Customer charge', 'cust', True); row('Energy charge', 'energy', True)
        if get(2026)['dem']: row('Demand (kVA) charge', 'dem', True)
    row('Fuel', 'fuel'); row('IPP (purchased power)', 'ipp'); row('Other (billing adjustments, credits)', 'other')
    if prepaid:
        rows.append(f'<tr><td class="l">Prepaid (single line)</td><td>{n(prepaid[2025])}</td><td>{n(prepaid[2026])}</td>{chg(prepaid[2025],prepaid[2026],0,1,cls=False)}<td>{n(prepaid[2026]/get(2026)["rev"]*100,1)}%</td></tr>')
    a, b = get(2025)['rev'], get(2026)['rev']
    rows.append(f'<tr class="tot"><td class="l">Net revenue (before GCT)</td><td>{n(a)}</td><td>{n(b)}</td>{chg(a,b,0,2)}<td>100.0%</td></tr>')
    ga, gb = get(2025)['gct'], get(2026)['gct']
    rows.append(f'<tr><td class="l">Taxes (GCT)</td><td>{n(ga)}</td><td>{n(gb)}</td>{chg(ga,gb,0,1,cls=False)}<td>&nbsp;</td></tr>')
    rows.append(f'<tr class="tot"><td class="l">Total billed, including GCT</td><td>{n(a+ga)}</td><td>{n(b+gb)}</td>{chg(a+ga,b+gb,0,2)}<td>&nbsp;</td></tr>')
    return '<table>\n<tr><th class="l">J$M, Jan&ndash;Sep</th><th>2025</th><th>2026</th><th>Change</th><th>Share of net revenue, 2026</th></tr>\n' + '\n'.join(rows) + '\n</table>'

KG = {'res': (YT('post', 2025, 1) / 1e6, YT('post', 2026, 1) / 1e6), 'com': (YT('com', 2025, 1) / 1e6, YT('com', 2026, 1) / 1e6), 'all': (ALLK[2025], ALLK[2026])}
def perk(seg, key):
    if seg == 'all': return [CB[y][key] / KG['all'][i] for i, y in enumerate((2025, 2026))]
    return [RC[seg][y][key] / KG[seg][i] for i, y in enumerate((2025, 2026))]
def perk_row(label, key, bold=False, prepaid=False):
    vals = []
    for seg in ('res', 'com', 'all'):
        if prepaid: v = [None, None] if seg != 'all' else [PPREV[y] / KG['all'][i] for i, y in enumerate((2025, 2026))]
        elif key == 'net': v = perk(seg, 'rev') if seg == 'all' else [RC[seg][y]['rev'] / KG[seg][i] for i, y in enumerate((2025, 2026))]
        elif key == 'gct': v = perk(seg, 'gct')
        elif key == 'bill':
            src = CB if seg == 'all' else RC[seg] if False else None
            if seg == 'all': v = [(CB[y]['rev'] + CB[y]['gct']) / KG['all'][i] for i, y in enumerate((2025, 2026))]
            else: v = [(RC[seg][y]['rev'] + RC[seg][y]['gct']) / KG[seg][i] for i, y in enumerate((2025, 2026))]
        else: v = perk(seg, key)
        vals.append(v)
    cells = ''.join('<td>&ndash;</td><td>&ndash;</td>' if v[0] is None else f'<td>{v[0]:.2f}</td><td>{v[1]:.2f}</td>' for v in vals)
    a, b = vals[2]
    return ('<tr class="tot">' if bold else '<tr>') + f'<td class="l">{label}</td>{cells}{pc(a,b,1,cls=False)}</tr>'
perk_html = ('<h3>Average revenue per kWh</h3>\n<p>The same layers expressed per kWh sold, which strips out the volume decline and shows what each unit of sales is actually earning. Residential and commercial use their own volumes; the combined column spreads everything, including prepaid revenue, over total system volume.</p>\n'
    '<table>\n<tr><th class="l">J$ per kWh, Jan&ndash;Sep</th><th>Resid. 2025</th><th>Resid. 2026</th><th>Comm. 2025</th><th>Comm. 2026</th><th>Comb. 2025</th><th>Comb. 2026</th><th>Comb. &Delta;</th></tr>\n'
    + '\n'.join([perk_row('Non-fuel charges', 'nonfuel'), perk_row('Fuel', 'fuel'), perk_row('IPP (purchased power)', 'ipp'), perk_row('Other', 'other'),
                 perk_row('Prepaid (single line)', None, prepaid=True), perk_row('Net revenue per kWh', 'net', True), perk_row('Taxes (GCT)', 'gct'), perk_row('Billed per kWh, including GCT', 'bill', True)]) + '\n</table>')
pk_all = {k: perk('all', k) for k in ('nonfuel', 'fuel', 'ipp', 'other', 'rev')}
d_fuel = pk_all['fuel'][1] - pk_all['fuel'][0]; d_ipp = pk_all['ipp'][1] - pk_all['ipp'][0]; d_oth = pk_all['other'][1] - pk_all['other'][0]
res_rate26 = RC['res'][2026]['rev'] / KG['res'][1]; com_rate26 = RC['com'][2026]['rev'] / KG['com'][1]
res_gk26 = RC['res'][2026]['gct'] / KG['res'][1]; com_gk26 = RC['com'][2026]['gct'] / KG['com'][1]
perk_text = (f'<p>The average net rate rose from J${pk_all["rev"][0]:.2f} to J${pk_all["rev"][1]:.2f} per kWh ({P(pk_all["rev"][0], pk_all["rev"][1])}). Fuel more than explains the increase ({"+" if d_fuel > 0 else M}J${abs(d_fuel):.2f} per kWh), offset by lower IPP ({"+" if d_ipp > 0 else M}J${abs(d_ipp):.2f}) and smaller billing adjustments ({"+" if d_oth > 0 else M}J${abs(d_oth):.2f}). '
    f'The non-fuel layer, the part that pays for the network, is roughly flat at about J${pk_all["nonfuel"][1]:.1f} per kWh ({P(pk_all["nonfuel"][0], pk_all["nonfuel"][1])}), so the network-charge yield per unit sold has held up even as volume fell. '
    f'Residential customers pay more per kWh than commercial in every layer of net revenue (J${res_rate26:.2f} against J${com_rate26:.2f} in 2026); commercial tax per kWh is far higher (J${com_gk26:.2f} against J${res_gk26:.2f}) because GCT is billed on almost all commercial consumption and on only part of residential.</p>')

tax_rows = []
for lab, key, base in (('Residential &mdash; billed monthly', 'res', RC['res']), ('Prepaid', 'pp', None), ('Commercial', 'com', RC['com'])):
    a, b = GCT[key][2025], GCT[key][2026]
    basis = base[2026]['rev'] if base else PPREV[2026]
    tax_rows.append(f'<tr><td class="l">{lab}</td><td>{n(a)}</td><td>{n(b)}</td>{chg(a,b,0,1,cls=False)}<td>{b/basis*100:.1f}%</td></tr>')
tax_tbl = ('<h3>Taxes (GCT)</h3>\n' + tbl(['GCT billed, Jan&ndash;Sep (J$M)', '2025', '2026', 'Change', 'Effective rate 2026'], tax_rows,
           f'<tr class="tot"><td class="l">Total</td><td>{n(CB[2025]["gct"])}</td><td>{n(CB[2026]["gct"])}</td>{chg(CB[2025]["gct"],CB[2026]["gct"],0,1,cls=False)}<td>{CB[2026]["gct"]/CB[2026]["rev"]*100:.1f}%</td></tr>')
           + f'\n<p class="note">Total tax billed fell {abs(pct(CB[2025]["gct"],CB[2026]["gct"])):.1f}% against a {abs(pct(CB[2025]["rev"],CB[2026]["rev"])):.1f}% fall in net revenue. Commercial tax tracks commercial revenue almost one for one at about {GCT["com"][2026]/RC["com"][2026]["rev"]*100:.1f}%; the difference comes from residential, where tax fell {abs(pct(GCT["res"][2025],GCT["res"][2026])):.1f}% against a {abs(pct(RC["res"][2025]["rev"],RC["res"][2026]["rev"])):.1f}% fall in revenue. That fits residential tax applying mostly to higher-consumption bills, which have fallen furthest in the storm-hit parishes. Prepaid tax for June is estimated at the neighbouring months\' effective rate.</p>')

# demand analysis, excluding Alcoa
DE = D.demand_ex_alcoa()
def dsum(cls, y):
    k = v = 0.0
    for (t, m), x in DE.items():
        if (cls == 'ALL' or t == cls) and f'{y}-01' <= m <= f'{y}-09': k += x[0]; v += x[1]
    return k, v
CH = {'RT40': ('RT40 Commercial', 'RT40'), 'RT50': ('RT50 Large Commercial', 'RT50'), 'RT70': ('RT70 Industrial (excluding Alcoa)', 'RT70')}
EN = {c: [D._K[c][y][1] / 1e6 for y in (2025, 2026)] for c in ('RT40', 'RT50', 'RT70')}
DM = {c: [D._K[c][y][2] / 1e6 for y in (2025, 2026)] for c in ('RT40', 'RT50', 'RT70')}
dem_rows = []
for c in ('RT40', 'RT50', 'RT70'):
    k25, v25 = dsum(c, 2025); k26, v26 = dsum(c, 2026)
    dem_rows.append(f'<tr><td class="l">{CH[c][0]}</td>{pc(k25,k26,1)}{pc(v25,v26,1)}{pc(EN[c][0],EN[c][1],1)}{pc(DM[c][0],DM[c][1],1)}</tr>')
k25, v25 = dsum('ALL', 2025); k26, v26 = dsum('ALL', 2026)
en25, en26 = sum(EN[c][0] for c in EN), sum(EN[c][1] for c in EN); dm25, dm26 = sum(DM[c][0] for c in DM), sum(DM[c][1] for c in DM)
dem_rows.append(f'<tr class="tot"><td class="l">All three</td>{pc(k25,k26,1)}{pc(v25,v26,1)}{pc(en25,en26,1)}{pc(dm25,dm26,1)}</tr>')
dem_all = dict(kwh=pct(k25, k26), kva=pct(v25, v26), en=pct(en25, en26), dm=pct(dm25, dm26))
r70s = (DE[('RT70', '2025-09')], DE[('RT70', '2026-09')])
rt70_sep = dict(kwh=pct(r70s[0][0], r70s[1][0]), kva=pct(r70s[0][1], r70s[1][1]), kva26=r70s[1][1])

# =============== assemble body ===============
out = []
A = out.append
A('<h1>Sales Analysis &mdash; September 2026</h1>')
A('<div class="meta">Sales Forecasting &amp; Analysis &middot; YTD January&ndash;September 2026 vs 2025 &middot; October 2026</div>')

# ---- September at a glance ----
_adj = SEPK[2026] + 1.58
_srev = {y: sum(S(g, y, 2, 9) for g in G) / 1e6 for y in (2025, 2026)}
_srate = (_srev[2026] / SEPK[2026]) / (_srev[2025] / SEPK[2025]) * 100 - 100
_glance = [
  f'<li><b>Sales {n(SEPK[2026],1)} GWh, down {abs(pct(SEPK[2025],SEPK[2026])):.1f}% on last year ({abs(pct(SEPK[2025],_adj)):.1f}% after correcting a billing-timing distortion); revenue up {pct(_srev[2025],_srev[2026]):.1f}%</b> because the average rate rose {_srate:.1f}%. Year to date, sales are down {abs(pct(ALLK[2025],ALLK[2026])):.1f}% and revenue down {abs(pct(ALLR[2025],ALLR[2026])):.1f}%.</li>',
  f'<li><b>The split widened.</b> Residential volume grew {pct(S("post",2025,1,9),S("post",2026,1,9)):.1f}% and prepaid {pct(S("pp",2025,1,9),S("pp",2026,1,9)):.0f}%, while commercial fell {abs(pct(S("com",2025,1,9),S("com",2026,1,9))):.1f}%.</li>',
  f'<li><b>Alcoa is the single biggest swing:</b> {alc_sep[2026]:.1f} GWh against {alc_sep[2025]:.1f} a year ago, {alc_sep_loss/com_sep_dec*100:.0f}% of the commercial decline. Its August and September demand charges are provisional and will be adjusted down, so commercial revenue for those months is overstated by up to about J$175 million.</li>',
  '<li><b>Billing timing at Caribbean Broilers</b> distorts the month: a double bill in August and only a stub in September move about 1.6 GWh between the two.</li>',
  '<li><b>Caribbean Cement dipped</b> (9.1 GWh against 10.8 a year ago) after a strong year, while <b>hotels are recovering</b>, down 19% in September against 25% year to date.</li>',
  '<li><b>Inactive connections keep growing:</b> RT10 added 1,071 zero-consumption accounts in September, more than its net growth of 802, so active residential customers fell slightly.</li>',
  '<li><b>Solar is accelerating outside the registered scheme:</b> 1,026 RT10 customers exported more than they drew (up 124% year over year) against 518 registered net billers.</li>',
  '<li><b>Demand holds up better than energy:</b> excluding Alcoa, year-to-date billed kVA is down 4.3% against kWh down 6.4%.</li>']
A('<div class="key"><b>September at a glance</b><ul>' + ''.join(_glance) + '</ul></div>')

# ---- Attribution ----
A('<h2>Sales by Segment</h2>')
A('<p>Sales are shown for four groups, because customers and sales behave very differently across the base: residential customers billed monthly, prepaid customers, commercial customers, and the combined system view.</p>')
B10 = D._B['RT10']; B20 = D._B['RT20res']
def totc(b, y): return sum(v[0] for v in b[y].values())
rt10_net = totc(B10, 2026) - totc(B10, 2025); rt10_zero = B10[2026]['Zero'][0] - B10[2025]['Zero'][0]
rt20_net = totc(B20, 2026) - totc(B20, 2025); rt20_zero = B20[2026]['Zero'][0] - B20[2025]['Zero'][0]
P_ = D.parish_res()
def pg(p): return pct(P_[p]['k25'], P_[p]['k26'])
A('<h3>Residential &mdash; billed monthly (homes and small residential-type accounts)</h3>')
A(seg_table('post'))
A(f'<p>This is where nearly all the customer growth in the system-wide numbers actually comes from, and it\'s also where the "growth" is least real. Of the {n(rt10_net)} net new homeowner-tariff accounts over the year, {n(rt10_zero)} &mdash; {rt10_zero/rt10_net*100:.0f} cents of every new dollar of "growth" &mdash; are premises that are connected and billing exactly zero. The small-business tariff shows the same thing at a smaller scale, {rt20_zero/rt20_net*100:.0f}% of its growth. The most plausible read, given the timing, is Hurricane Melissa: homes and small businesses that were damaged or vacated in November 2025 and are still on the books but haven\'t been reactivated. That\'s an inference from the timing, not something confirmed directly in the billing data, but it\'s the only explanation that\'s consistent with everything else this analysis turned up. Volume tells a more encouraging in-month story than the year-to-date figure suggests &mdash; September itself is up {pct(S("post",2025,1,9),S("post",2026,1,9)):.1f}% year over year, and customers are migrating into <i>higher</i> consumption bands over this period, not lower. The year-to-date shortfall is concentrated in the western parishes that took the storm &mdash; Westmoreland down {abs(pg("Westmoreland")):.1f}% in volume, St. Elizabeth {abs(pg("St. Elizabeth")):.1f}%, Hanover {abs(pg("Hanover")):.1f}%, Trelawny {abs(pg("Trelawny")):.1f}%, St. James {abs(pg("St. James")):.1f}% &mdash; while the rest of the island is flat to slightly up (Section 4). That is a recovery-lag pattern, not a fading trend.</p>')
A('<h3>Prepaid (pay-as-you-go)</h3>')
A(seg_table('pp'))
pp_c = (D.cust('pp', 2025, 9), D.cust('pp', 2026, 9)); post_c = (D.cust('post', 2025, 9), D.cust('post', 2026, 9))
A(f'<p>Prepaid is the only residential segment growing on every measure, and it\'s growing much faster than the rest of the residential base: customers up {pct(*pp_c):.1f}% against {pct(*post_c):.1f}% for monthly-billed residential, volume up {pct(YT("pp",2025,1),YT("pp",2026,1)):.1f}% year to date and {pct(S("pp",2025,1,9),S("pp",2026,1,9)):.1f}% in September alone, revenue up {pct(YT("pp",2025,2),YT("pp",2026,2)):.1f}%. It is still small &mdash; about {pp_c[1]/CUSTS[2026]*100:.1f}% of customers, {YT("pp",2026,1)/1e6/ALLK[2026]*100:.0f}% of volume and {YT("pp",2026,2)/1e6/ALLR[2026]*100:.0f}% of revenue. Looking account by account, growth is slowing (active accounts were up 18.5% in the year to September 2025 and are up 8.8% now), but the customers who stay are using more: the same 13,870 accounts used 7.0% more than a year ago, and average monthly spend per account is J$10,092, up 8.8%, with the share spending J$20,000 or more rising from 9% to 11%. The price paid, including tax, is J$61.8 per kWh, up 2.7%. Turnover is high: about 12% of accounts drop out and about 11% join each month, and new accounts use far less (about 93 kWh a month against 172 for retained ones). About one in five prepaid accounts (4,086) has no tariff assigned, up from 912 two years ago. Average use per account eased in September (174 to 163 kWh), more than the shorter month explains. The pattern is consistent with households moving to prepaid for budget control, though the billing data can\'t confirm the reason for the switch.</p>')
A('<h3>Commercial (registered businesses, individually metered)</h3>')
A(seg_table('com'))
A(f'<p>The opposite pattern from residential: the connection count is down {abs(pct(D.cust("com",2025,9),D.cust("com",2026,9))):.1f}%, almost all of it small-business accounts, and the volume decline is real, not a labeling artifact &mdash; but it traces to a few specific, nameable events, not a diffuse trend. Alcoa Minerals\' self-generation came fully online in August: it billed {alc_sep[2026]:.1f} GWh in September against {alc_sep[2025]:.1f} a year ago, which alone is {alc_sep_loss:.1f} GWh of the month\'s {com_sep_dec:.1f} GWh commercial decline, and that grid draw isn\'t coming back. Separately, the hotel sector still hasn\'t finished recovering from Melissa &mdash; it is improving, just not there yet. Caribbean Cement was a notable reversal in September: {9.13:.1f} GWh against 10.8 a year ago, even though it remains well ahead year to date. Month-on-month figures are also distorted by billing timing at Caribbean Broilers: its main plant was billed for two periods in August (3.4 GWh against a normal 1.7) and only a stub in September (0.08 GWh), so August is overstated and September understated by roughly 1.6 GWh each; normalised, September commercial sales are about 7% below last year, or about 4% below excluding Alcoa. Commercial revenue held up far better than commercial volume (down {abs(pct(YT("com",2025,2),YT("com",2026,2))):.1f}% against {abs(pct(YT("com",2025,1),YT("com",2026,1))):.1f}%) because demand charges are billed on peak kVA rather than kWh &mdash; see Section 1b. One caution on the revenue side: Alcoa\'s August and September demand charges (J$88 million and J$86 million, against about J$60 million a month earlier in the year) are provisional and due to be adjusted down, so commercial revenue for those two months is likely overstated by up to about J$175 million, or 0.3% of year-to-date commercial revenue.</p>')
A('<h3>Combined (system-wide)</h3>')
A(tbl(['Metric', 'Sep 2025', 'Sep 2026', 'Change'], [
    f'<tr><td class="l">Customers</td><td>{n(CUSTS[2025])}</td><td>{n(CUSTS[2026])}</td>{chg(CUSTS[2025],CUSTS[2026])}</tr>',
    f'<tr><td class="l">Sales (GWh, month)</td><td>{n(SEPK[2025],2)}</td><td>{n(SEPK[2026],2)}</td>{chg(SEPK[2025],SEPK[2026],2,1)}</tr>',
    f'<tr><td class="l">Sales YTD (GWh, Jan&ndash;Sep)</td><td>{n(ALLK[2025],1)}</td><td>{n(ALLK[2026],1)}</td>{chg(ALLK[2025],ALLK[2026],1,1)}</tr>',
    f'<tr><td class="l">Revenue YTD (J$M)</td><td>{n(ALLR[2025])}</td><td>{n(ALLR[2026])}</td>{chg(ALLR[2025],ALLR[2026])}</tr>']))
A('<p class="note">The three segments above add exactly to these combined figures (Appendix, Table A1). Customer counts include the individually metered small-business accounts, which are close to flat year over year. September 2026 commercial and combined sales are understated by about 1.6 GWh of billing timing at Caribbean Broilers; adjusted, September combined sales are about 296.3 GWh, down 1.8% on last year.</p>')
A('<div class="key"><b>Reading across the segments</b><br><br>Nearly all of the customer growth is residential, and most of it is inactive connections still on the books after Melissa rather than new load. Nearly all of the volume decline is commercial &mdash; a few large accounts and the hotel sector &mdash; plus a residential shortfall that sits in the storm-hit western parishes. Prepaid is the one segment growing on every measure but is still too small to move the total. There is no sign of broad conservation or self-generation: residential volume is up in the month and migrating into higher consumption bands, and commercial volume outside Alcoa and the hotel sector is close to flat.</div>')

# ---- 1 Top level ----
A('<h2>1. Top Level</h2>')
A(f'<p>Overall, sales are down {abs(pct(ALLK[2025],ALLK[2026])):.1f}% year to date and customers are up {pct(CUSTS[2025],CUSTS[2026]):.1f}%. Revenue held up much better than volume &mdash; down only {abs(pct(ALLR[2025],ALLR[2026])):.2f}% &mdash; because the average rate paid per kWh rose {pct(rate[2025],rate[2026]):.1f}% across the period and absorbed most of the volume shortfall. September itself was close to the year\'s best against the prior year: sales were down {abs(pct(SEPK[2025],SEPK[2026])):.1f}% ({abs(pct(SEPK[2025],SEPK[2026]+1.58)):.1f}% after adjusting for billing timing at Caribbean Broilers) and revenue up {pct(S("post",2025,2,9)+S("pp",2025,2,9)+S("com",2025,2,9), S("post",2026,2,9)+S("pp",2026,2,9)+S("com",2026,2,9)):.1f}%. It\'s worth remembering that the 2025 base itself isn\'t a clean baseline: it was already running below normal from November onward because of the storm, so part of this year\'s "decline" is really "hasn\'t caught back up yet" rather than fresh deterioration on top of a healthy prior year.</p>')
A('<h3>1b. Revenue composition &mdash; what is actually moving</h3>')
A('<p>Revenue is billed in layers that behave very differently: the non-fuel charges (customer charge, energy charge and, for commercial customers, the demand charge on peak kVA) are the part JPS keeps to run the network; fuel and IPP purchased power are largely passed through; taxes (GCT) are billed on top and shown below net revenue.</p>')
A('<h3>Combined</h3>'); A(comp_table(lambda y: CB[y], False, PPREV))
dn = CB[2026]['rev'] - CB[2025]['rev']
def dd(k): return CB[2026][k] - CB[2025][k]
A(f'<p>Three movements explain the net J${abs(dn)/1000:.1f} billion decline in net revenue. IPP is down J${abs(dd("ipp"))/1000:.1f} billion ({P(CB[2025]["ipp"],CB[2026]["ipp"])}) and non-fuel charges are down J${abs(dd("nonfuel"))/1000:.1f} billion ({P(CB[2025]["nonfuel"],CB[2026]["nonfuel"])}), against a J${dd("fuel")/1000:.1f} billion increase in fuel ({P(CB[2025]["fuel"],CB[2026]["fuel"])}) that cushions them. Fuel and IPP move in opposite directions but together they are up just {pct(CB[2025]["fuel"]+CB[2025]["ipp"],CB[2026]["fuel"]+CB[2026]["ipp"]):.1f}% on {abs(pct(ALLK[2025],ALLK[2026])):.0f}% less volume, so read the pair as one pass-through block; the individual lines swing from month to month. The line to watch is "Other", which fell from J${CB[2025]["other"]/1000:.1f} billion to J${CB[2026]["other"]/1000:.1f} billion and on its own accounts for about {abs(dd("other"))/abs(dn)*100:.0f}% of the net decline &mdash; it is a residual of billing adjustments and credits rather than a charge, and a drop of that size in a single year is worth confirming with Billing before it\'s treated as either real or permanent.</p>')
A('<h3>Residential &mdash; billed monthly</h3>'); A(comp_table(lambda y: RC['res'][y], True))
A('<h3>Commercial</h3>'); A(comp_table(lambda y: RC['com'][y], True))
cn = lambda k: RC['com'][2026][k] - RC['com'][2025][k]
A(f'<p>Commercial non-fuel charges fell {abs(pct(RC["com"][2025]["nonfuel"],RC["com"][2026]["nonfuel"])):.1f}% against a {abs(pct(YT("com",2025,1),YT("com",2026,1))):.1f}% fall in volume, and the reason is in the demand line. Demand charges are billed on peak kVA, not on kWh, and a customer\'s peak doesn\'t fall in proportion to its total consumption: a plant that runs less often still hits the same peak when it does run. The demand analysis below excludes Alcoa: its self-generation exit dominates RT70, and its billed demand for August and September is provisional and will be adjusted down, so it would otherwise distort the picture. Across the three demand-billed classes without Alcoa, volume is down {abs(dem_all["kwh"]):.1f}% year to date and the energy charge is down {abs(dem_all["en"]):.1f}% right alongside it, but the demand charge is down only {abs(dem_all["dm"]):.1f}% and billed kVA only {abs(dem_all["kva"]):.1f}%. That gap is why commercial revenue ({M}{abs(pct(YT("com",2025,2),YT("com",2026,2))):.1f}%) is so much more resilient than commercial volume ({M}{abs(pct(YT("com",2025,1),YT("com",2026,1))):.1f}%).</p>')
A(tbl(['Demand-billed classes excluding Alcoa, Jan&ndash;Sep', 'kWh', 'Billed kVA', 'Energy charge', 'Demand charge'], dem_rows))
A(f'<p>The clearest example is RT70 without Alcoa in September, where volume fell {abs(rt70_sep["kwh"]):.1f}% yet billed kVA was unchanged at {rt70_sep["kva26"]/1000:.1f}k. Fifteen large accounts cut their kWh by 25% or more year over year in September while keeping billed demand within 10% &mdash; among them Playa Hall (kWh down 65%, demand unchanged), Petrojam (down 47% against demand down 8%) and Windalco &mdash; so customers are holding capacity while they use less energy. The data alone can\'t say whether that is contract minimums or a deliberate hold on capacity for the recovery.</p>')
A(perk_html); A(perk_text); A(tax_tbl)

# ---- 2 rate class ----
def cls_row(label, keys, note=''):
    k25 = sum(D._C[k][2025][0] for k in keys); k26 = sum(D._C[k][2026][0] for k in keys)
    r25 = sum(D._C[k][2025][1] for k in keys); r26 = sum(D._C[k][2026][1] for k in keys)
    c25 = sum(D._C[k][2025][5] for k in keys); c26 = sum(D._C[k][2026][5] for k in keys)
    cs = ('' if c25 == c26 else '') ; cpc = pct(c25, c26)
    ccell = f'<td class="{"pos" if cpc > 0 else "neg" if cpc < 0 else ""}">{("+" if cpc > 0 else "")}{n(cpc,1)}%{note}</td>'
    return f'<tr><td class="l">{label}</td>{pc(k25,k26,1)}{ccell}{pc(k25/c25,k26/c26,1)}{pc(r25,r26,1)}{pc(r25/k25,r26/k26,1)}</tr>', (pct(k25, k26), pct(r25 / k25, r26 / k26))
rows2 = []; CLS = {}
for lab, keys, note in (('RT10 Residential', ['RT10', 'RT10_pp'], ''), ('RT20 Small Commercial', ['RT20_com', 'RT20_res', 'RT20_pp'], ''), ('RT40 Commercial', ['RT40'], ''), ('RT50 Large Commercial', ['RT50'], ''), ('RT60-ST Street Lighting', ['RT60-ST'], ''), ('RT70 Industrial', ['RT70'], ' (2 accts)')):
    r, v = cls_row(lab, keys, note); rows2.append(r); CLS[lab.split()[0]] = v
FAL25_50, FAL26_70 = 6.15, 7.91
rt50k = (D._C['RT50'][2025][0] / 1e6 - FAL25_50, D._C['RT50'][2026][0] / 1e6)
rt70k = (D._C['RT70'][2025][0] / 1e6 - 1.93, D._C['RT70'][2026][0] / 1e6 - FAL26_70)
A('<h2>2. Across Rate Class</h2>')
A(tbl(['Class', 'GWh &Delta;', 'Customers &Delta;', 'kWh/cust &Delta;', 'Revenue &Delta;', 'J$/kWh &Delta;'], rows2))
A(f'<p>Every class lost volume and every class gained rate &mdash; that part is uniform. RT70 is the one that looks odd at first glance, revenue actually up despite less electricity sold, but it\'s mechanical rather than encouraging: Alcoa\'s volume, one of the largest and presumably one of the cheaper-rate loads on the system, has fallen away and the class has lost two accounts, which pulls the average rate of everyone who\'s left upward. Alcoa\'s provisional demand charges also flatter RT70 revenue until they are adjusted down. It\'s a mix effect, not industrial customers suddenly paying more for the same power. One reclassification also flatters RT70 and penalises RT50: a hotel (Falmouth PHR) moved from RT50 to RT70 in August 2025, so about 6 GWh of RT50\'s decline is a change of class, not lost load. Treating that hotel consistently in both years, RT50 is down {abs(pct(*rt50k)):.1f}% and RT70 is down {abs(pct(*rt70k)):.1f}%.</p>')

# ---- 3 consumption blocks ----
NB = D.nb_series()
def nbc(mo, code): return int(round(NB[mo][code][0]))
b10l = B10[2026]['<150'][0] + B10[2026]['150>350'][0] - B10[2025]['<150'][0] - B10[2025]['150>350'][0]
b10h = sum(B10[2026][k][0] - B10[2025][k][0] for k in ('350>550', '550>750', '750>950', 'over 950'))
nb_tot = {m: sum(nbc(m, c) for c in ('NB10', 'NB20', 'NB40')) for m in ('2025-09', '2026-09')}
ex25, ex26 = D.EXPORTERS['2025-09'], D.EXPORTERS['2026-09']
summer25 = sum(D.EXPORTERS[m][0] for m in ('2025-06', '2025-07', '2025-08', '2025-09')) / 4; summer26 = sum(D.EXPORTERS[m][0] for m in ('2026-06', '2026-07', '2026-08', '2026-09')) / 4
win25 = (D.EXPORTERS['2025-01'][0] + D.EXPORTERS['2025-02'][0]) / 2; win26 = (D.EXPORTERS['2026-01'][0] + D.EXPORTERS['2026-02'][0]) / 2
A('<h2>3. Within Rate Class &mdash; Consumption Blocks</h2>')
A(f'<p>RT10 and RT20 are the only two classes with banded consumption data, and both tell the same story: the Under-150 and 150&ndash;350 kWh bands are shrinking while the bands above 350 kWh are growing. Concretely, for RT10 the two lowest bands lost {n(abs(b10l))} customers combined while the four bands from 350 kWh up gained {n(b10h)} &mdash; more customers moved up than moved out of the low end, which means the migration is being topped up by some new connections landing directly in the middle bands too, not just by existing low-usage customers climbing. Either way, the direction is up, not down. The band tables for every rate class are in the Appendix (Tables A2&ndash;A8).</p>')
A(tbl(['&nbsp;', 'RT10', 'RT20 (residential)'], [
    f'<tr><td class="l">Zero-consumption customers, Sep-25 &rarr; Sep-26</td><td>{n(B10[2025]["Zero"][0])} &rarr; {n(B10[2026]["Zero"][0])} ({sg(rt10_zero)}, {P(B10[2025]["Zero"][0],B10[2026]["Zero"][0])})</td><td>{n(B20[2025]["Zero"][0])} &rarr; {n(B20[2026]["Zero"][0])} ({sg(rt20_zero)}, {P(B20[2025]["Zero"][0],B20[2026]["Zero"][0])})</td></tr>',
    f'<tr><td class="l">Share of that class\'s total customer growth</td><td class="neg">{rt10_zero/rt10_net*100:.0f}%</td><td class="neg">{rt20_zero/rt20_net*100:.0f}%</td></tr>',
    f'<tr><td class="l">Registered net-billing customers, Sep-25 &rarr; Sep-26</td><td>{nbc("2025-09","NB10")} &rarr; {nbc("2026-09","NB10")} ({sg(nbc("2026-09","NB10")-nbc("2025-09","NB10"))}, {P(nbc("2025-09","NB10"),nbc("2026-09","NB10"))})</td><td>{nbc("2025-09","NB20")} &rarr; {nbc("2026-09","NB20")} ({sg(nbc("2026-09","NB20")-nbc("2025-09","NB20"))}, {P(nbc("2025-09","NB20"),nbc("2026-09","NB20"))})</td></tr>',
    f'<tr><td class="l">Customers exporting more than they draw in the month, Sep-25 &rarr; Sep-26</td><td>{ex25[0]} &rarr; {ex26[0]} ({sg(ex26[0]-ex25[0])}, {P(ex25[0],ex26[0])})</td><td>{ex25[1]} &rarr; {ex26[1]} ({sg(ex26[1]-ex25[1])}, {P(ex25[1],ex26[1])})</td></tr>']))
A('<p>So the falling per-customer average isn\'t existing customers pulling back &mdash; it\'s the blended average getting diluted by a large number of connections that aren\'t consuming anything at all. That\'s a meaningfully different problem to solve than "customers are conserving," and it points toward a data-cleanup and reconnection question (are these premises actually vacant, or just stuck in a billing/meter-read backlog?) rather than a demand-forecasting one. Zero-consumption connections are still rising ten months after the storm: RT10 added 1,071 in September alone, more than its entire net customer growth for the month, so active residential customers actually fell slightly.</p>')
A(f'<p>Solar shows up in two different ways in the data, and they tell different stories. Customers registered on the net-billing tariff are few and growing slowly &mdash; {nbc("2026-09","NB10")} on the residential tariff ({P(nbc("2025-09","NB10"),nbc("2026-09","NB10"))}) and {nbc("2026-09","NB20")} on the small-business tariff ({P(nbc("2025-09","NB20"),nbc("2026-09","NB20"))}), with another {nbc("2026-09","NB40")} large commercial accounts that haven\'t moved &mdash; {n(nb_tot["2026-09"])} in all, up {PU(nb_tot["2025-09"],nb_tot["2026-09"])}. They are not small users: registered residential net billers still draw about 710 kWh a month on average, four times the residential average, and the export credits they earn have been steady at about J$10 million a month across all three tariffs. But the number of customers who actually exported more than they drew in September is close to double the registered residential count ({ex26[0]:,} against {nbc("2026-09","NB10")}) and more than doubled year over year ({P(ex25[0],ex26[0],0)}); the volume they exported rose even faster, from 103 MWh to 259 MWh. At least {ex26[0]-nbc("2026-09","NB10")} residential exporters are therefore not on the registered scheme, or not yet &mdash; activity that sits outside registered net billing. The pattern is also seasonal: exporters peak in the low-consumption winter months and trough in summer. Like for like, the summer months of 2026 (June to September, about {summer26:,.0f} a month) are {PU(summer25,summer26,0)} above summer 2025, but the winter peak was lower, with {win26:,.0f} exporters in January and February 2026 against {win25:,.0f} a year earlier. A drop in the peak while the base rises is consistent with some rooftop systems having been damaged in the storm, though the billing data can\'t confirm that. It is still small in absolute terms &mdash; about {ex26[0]+ex26[1]:,} customers across the two residential tariffs &mdash; but the direction is clear and the registered count understates it. One caution: a single month of net export can also come from a meter correction or a billing estimate reversal, so the export count is an upper bound on solar, not a precise measure.</p>')

# ---- 4 parish ----
A('<h2>4. By Parish</h2>')
A('<p>Every residential account carries a parish, so the residential base is shown here alongside commercial. Consumption bands (Section 3 and Appendix A2) are island-wide.</p>')
A('<h3>Residential (billed monthly), by parish &mdash; sorted from steepest volume decline</h3>')
prow = []
for name, r in sorted(P_.items(), key=lambda x: pct(x[1]['k25'], x[1]['k26'])):
    prow.append(f'<tr><td class="l">{name}</td><td>{n(r["c26"])}</td>{pc(r["c25"],r["c26"],1)}<td>{n(r["k26"]/1e6,1)}</td>{pc(r["k25"],r["k26"],1)}{pc(r["r25"],r["r26"],1)}</tr>')
tk = {k: sum(r[k] for r in P_.values()) for k in ('c25', 'c26', 'k25', 'k26', 'r25', 'r26')}
A(tbl(['Parish', 'Customers, Sep-26', 'Customers &Delta;', 'GWh, Jan&ndash;Sep 26', 'GWh &Delta;', 'Revenue &Delta;'], prow,
      f'<tr class="tot"><td class="l">Total</td><td>{n(tk["c26"])}</td>{pc(tk["c25"],tk["c26"],1)}<td>{n(tk["k26"]/1e6,1)}</td>{pc(tk["k25"],tk["k26"],1)}{pc(tk["r25"],tk["r26"],1)}</tr>'))
cp = lambda p: pct(*D.PAR_COM[p])
A(f'<p>Customer growth is even across the island, between {min(pct(r["c25"],r["c26"]) for r in P_.values()):.1f}% and {max(pct(r["c25"],r["c26"]) for r in P_.values()):.1f}% everywhere, but volume is not. The five steepest declines &mdash; Westmoreland, St. Elizabeth, Hanover, Trelawny and St. James &mdash; are the western parishes hit hardest by Hurricane Melissa, and together they account for more than the whole of the residential volume shortfall; the rest of the island runs from {pg("St. Ann"):.1f}% (St. Ann) to +{pg("St. Thomas"):.1f}% (St. Thomas), mostly within &plusmn;2%. It\'s the same geography as the hotel story in Section 5, showing up on the residential side: connections are back or holding, consumption in the storm-hit areas isn\'t yet.</p>')
A(f'<p>Commercial accounts (RT20 commercial, RT40, RT50, RT60-ST, RT70) show the same western pattern &mdash; St. James down {abs(cp("St. James")):.1f}% in GWh, St. Elizabeth down {abs(cp("St. Elizabeth")):.1f}%, Westmoreland down {abs(cp("Westmoreland")):.1f}%.</p>')

# ---- 5 industry ----
top = sorted(D.IND.items(), key=lambda kv: -kv[1][1])[:10]
T25, T26, TR25, TR26 = D.IND_TOTAL
NA = D.IND_NA
t10 = [sum(v[i] for _, v in top) for i in range(4)]
oth = (T25 - NA[0] - t10[0], T26 - NA[1] - t10[1], TR25 - NA[2] - t10[2], TR26 - NA[3] - t10[3])
SHORT = {'Wired and Wireless Telecommunications Carriers (except Satellite)': 'Wired and Wireless Telecommunications Carriers', 'Supermarkets and Other Grocery Retailers (except Convenience Retailers)': 'Supermarkets and Other Grocery Retailers'}
irows = []
for i, (nm, (a, b, ra, rb)) in enumerate(top, 1):
    irows.append(f'<tr><td class="l">{i}. {SHORT.get(nm, nm)}</td><td>{n(a,1)}</td><td>{n(b,1)}</td>{pc(a,b,1)}<td>{n(b/T26*100,1)}%</td>{pc(ra,rb,1)}</tr>')
irows.append(f'<tr><td class="l">All other industries with an industry assigned</td><td>{n(oth[0],1)}</td><td>{n(oth[1],1)}</td>{pc(oth[0],oth[1],1)}<td>{n(oth[1]/T26*100,1)}%</td>{pc(oth[2],oth[3],1)}</tr>')
irows.append(f'<tr><td class="l"><i>Industry not yet assigned</i></td><td>{n(NA[0],1)}</td><td>{n(NA[1],1)}</td>{pc(NA[0],NA[1],1,cls=False)}<td>{n(NA[1]/T26*100,1)}%</td>{pc(NA[2],NA[3],1,cls=False)}</tr>')
irows.append(f'<tr class="tot"><td class="l">Total commercial</td><td>{n(T25,1)}</td><td>{n(T26,1)}</td>{pc(T25,T26,1)}<td>100.0%</td>{pc(TR25,TR26,1)}</tr>')
A('<h2>5. By Sector / Industry</h2>')
A('<p>This covers the commercial classes (small-business commercial RT20, RT40, RT50 and RT70). RT10 residential and RT60-ST street lighting carry no industry classification, so they are excluded here by definition, not by choice. Figures are January to September.</p>')
A('<h3>Top 10 industries by 2026 volume</h3>')
A(tbl(['Industry', 'GWh 2025', 'GWh 2026', 'GWh &Delta;', 'Share of commercial GWh, 2026', 'Revenue &Delta;'], irows[:-1], irows[-1]))
A(f'<p>The top ten industries make up {t10[1]/T26*100:.0f}% of commercial volume, another {oth[1]/T26*100:.0f}% is spread across the remaining industries with an industry assigned, and about {NA[1]/T26*100:.0f}% belongs to real businesses whose industry hasn\'t been assigned yet. Residential accounts are excluded because they can\'t carry an industry; on the commercial accounts that should, the gap is {NA[1]/T26*100:.1f}% of volume in 2026 ({NA[0]/T25*100:.1f}% in 2025). It is also not evenly spread: it sits almost entirely in small-business commercial accounts, where 56% of volume (166 of 297 GWh) has no industry assigned, against about 1% for RT40, RT50 and RT70. These are identifiable businesses (a coffee chain, printers, an auto dealer, quarries, government departments), so the gap is a classification backlog, not missing customers. By premise count that is roughly 17,900 accounts. Assigning industries to the small-business accounts would close nearly all of it.</p>')
mv = lambda nm: D.IND[nm]
mov = [('Hotels (except Casino Hotels) and Motels', 'Hotels (except Casino Hotels) and Motels'), ('Poultry Hatcheries', 'Poultry Hatcheries'), ('Telemarketing Bureaus and Other Contact Centers', 'Telemarketing / Contact Centers'), ('Water Supply and Irrigation Systems', 'Water Supply and Irrigation Systems'), ('Cement Manufacturing', 'Cement Manufacturing'), ('Distilleries', 'Distilleries'), ('Other Metal Ore Mining', 'Other Metal Ore Mining')]
mrows = []
for key, lab in mov:
    a, b, ra, rb = mv(key)
    mrows.append(f'<tr><td class="l">{lab}</td>{pc(a,b,1)}{pc(ra,rb,1)}</tr>')
A('<h3>Biggest movers</h3>'); A(tbl(['Industry', 'GWh &Delta;', 'Revenue &Delta;'], mrows))
hot = mv('Hotels (except Casino Hotels) and Motels'); nxt3 = sorted([(v[1] - v[0]) for k, v in D.IND.items() if k != 'Hotels (except Casino Hotels) and Motels' and (v[1] - v[0]) < 0])[:3]
A(f'<p>Hotels is, by a wide margin, the single largest identifiable industry drag on the system &mdash; {abs(hot[1]-hot[0]):.1f} GWh lost, more than the next three declining industries combined ({abs(sum(nxt3)):.1f} GWh). Other Metal Ore Mining has turned negative as Alcoa\'s exit works through the year-to-date total, and Cement Manufacturing\'s growth has slowed from its earlier pace but is still the largest gain. Everything else with an industry assigned mostly moves within about &plusmn;5%, so this reads as concentrated in a few sectors rather than a broad commercial slowdown.</p>')
sh = lambda nm: (mv(nm)[0] / T25 * 100, mv(nm)[1] / T26 * 100)
A('<h3>5a. Composition &mdash; is a rising share growth, or everyone else declining?</h3>')
A('<p>A rising share can mean real growth, or simply other industries falling faster around it. The table separates the two.</p>')
hs, cs_, ms, ws = sh('Hotels (except Casino Hotels) and Motels'), sh('Cement Manufacturing'), sh('Other Metal Ore Mining'), sh('Water Supply and Irrigation Systems')
ca, cb, _, _ = mv('Cement Manufacturing'); ma, mb, _, _ = mv('Other Metal Ore Mining'); wa, wb, _, _ = mv('Water Supply and Irrigation Systems')
A(tbl(['Industry', 'Share of commercial GWh, 2025', 'Share, 2026', 'Read'], [
    f'<tr><td class="l">Hotels</td><td>{hs[0]:.2f}%</td><td>{hs[1]:.2f}%</td><td class="l">Share <span class="neg">falling</span> &mdash; genuine decline, not dilution</td></tr>',
    f'<tr><td class="l">Cement Manufacturing</td><td>{cs_[0]:.2f}%</td><td>{cs_[1]:.2f}%</td><td class="l">Share <span class="pos">rising</span>, volume also up {pct(ca,cb):.1f}% &mdash; real growth</td></tr>',
    f'<tr><td class="l">Other Metal Ore Mining</td><td>{ms[0]:.2f}%</td><td>{ms[1]:.2f}%</td><td class="l">Share holding, but volume is down {abs(pct(ma,mb)):.1f}% &mdash; Alcoa\'s exit offset by gains at Windalco and others, and the rest of the commercial base shrinking at a similar pace</td></tr>',
    f'<tr><td class="l">Water Supply and Irrigation</td><td>{ws[0]:.2f}%</td><td>{ws[1]:.2f}%</td><td class="l">Share and volume both down ({pct(wa,wb):.1f}%) &mdash; broad, not company-specific</td></tr>',
    f'<tr><td class="l">(industry not yet assigned)</td><td>{NA[0]/T25*100:.2f}%</td><td>{NA[1]/T26*100:.2f}%</td><td class="l">Share rising slightly, because the small-business accounts with no industry assigned fell less than the others &mdash; an assignment gap more than a finding</td></tr>']))
A('<p>Cement Manufacturing is the one genuinely clean growth story here: both the dollars and the share are moving up together, which is what real growth looks like rather than growth-by-comparison. Hotels is the mirror image &mdash; an outright decline, not just a shrinking share because other things grew around it. And about one kWh in eight still has no industry assigned, concentrated in small-business accounts, which caps how far the sector cut can be trusted until that is cleaned up.</p>')
A('<h3>5b. Concentration &mdash; how much of this sits with a handful of accounts?</h3>')
A('<p>Taking RT50 as the sharpest example, since it has the steepest volume decline of any class: year to date, the largest declines are Jamaica Broilers Group (&minus;10.6 GWh) and four hotel and resort properties &mdash; X Fund Properties (&minus;5.5), Sandals Whitehouse (&minus;5.0), HOCATSA (&minus;3.2) and Royal Caribbean Sea Club (&minus;2.3). The largest gain is Caribbean Cement at +11.5 GWh, well ahead of the next biggest, West Meat Packers and Windalco (+1.7 and +1.5). Two items need care: Jamaica Broilers Group stepped down in mid-2025, so most of its year-to-date gap is a base effect and September itself is only about 13% below last year; and Falmouth PHR (a further &minus;6.2 GWh in RT50) did not decline at all but moved to RT70. That\'s the pattern across every class this analysis touched: the movement is a small number of large accounts, not a broad shift across the customer base.</p>')

# ---- 6 defection ----
DEF = [('Storm window, not recovered', 475, 4.23, 0.09), ('Storm window, recovering', 54, 4.97, 0.97), ('Account closed', 78, 1.82, 0.05),
       ('Contracted capacity released (outside the storm window)', 4, 1.64, 0.19), ('Small business, no clear signal', 236, 1.08, 0.09), ('Self-generation indicated', 2, 0.18, 0.01)]
DEF.sort(key=lambda r: -(r[2] - r[3]))
tot25 = sum(r[2] for r in DEF); tot26 = sum(r[3] for r in DEF); totn = sum(r[1] for r in DEF); loss = tot25 - tot26
com_decl = YT('com', 2025, 1) / 1e6 - YT('com', 2026, 1) / 1e6
oper = sum(r[2] - r[3] for r in DEF if r[0] not in ('Small business, no clear signal', 'Self-generation indicated'))
drow = ''.join(f'<tr><td class="l">{a}</td><td>{b}</td><td>{c:.2f}</td><td>{d:.2f}</td><td class="neg">{M}{c-d:.2f}</td><td>{(c-d)/loss*100:.0f}%</td></tr>\n' for a, b, c, d in DEF)
NAMED = [('HOCATSA Jamaica Limited', 'Hotels', 3.98, 0.79, -80, 'Storm damage; hotel now recovering month by month'),
 ('Carib Products Co Ltd', 'Fats and oils refining', 1.00, 0.13, -87, 'Volume and contracted demand both cut from February 2026; operational'),
 ('United Call Solutions (Jamaica)', 'Contact centers', 0.90, 0.00, -100, 'Storm window; demand cut to the minimum, site closed'),
 ('Coyaba Beach Resort & Club', 'Hotels', 0.69, 0.13, -81, 'Storm damage; recovering'),
 ('Contax360 BPO Solutions', 'Contact centers', 0.52, 0.00, -100, 'Storm window; demand cut to the minimum, site closed'),
 ('BBNH Resorts Limited', 'Hotels', 0.51, 0.00, -100, 'Storm window; no longer billing'),
 ('M & W Investments Ltd', 'Banking, insurance and investments', 0.38, 0.03, -91, 'Account closed; no billing since February 2026'),
 ('Shoppers Fair', 'Supermarkets and grocery', 0.34, 0.00, -99, 'Storm window; demand cut to the minimum'),
 ('Unique Vacations Ltd', 'Contact centers', 0.31, 0.03, -90, 'Storm window; no billing since April 2026'),
 ('24-7 Intouch JAM2 Inc', 'Industry not yet assigned', 0.27, 0.02, -92, 'Storm window; account closed'),
 ('Strobe Communications Ltd', 'Contact centers', 0.27, 0.01, -96, 'Storm window; demand cut to the minimum'),
 ('Eight Rivers Energy Company', 'Hydroelectric power generation', 0.27, 0.00, -99, 'Storm window; a generator, so confirm whether it now supplies itself'),
 ('Dougall Flooring Ltd.', 'Flooring contractors', 0.23, 0.02, -91, 'Volume and contracted demand run down gradually; operational'),
 ('White Diamond Hotels & Resorts', 'Hotels', 0.20, 0.00, -100, 'Storm window; no longer billing'),
 ('St James Parish Council', 'Industry not yet assigned', 0.12, 0.00, -98, 'Storm window; consumption near zero'),
 ('AMGL Account Outsourcing Group', 'Industry not yet assigned', 0.12, 0.01, -94, 'Storm window; account closed'),
 ('Jamaica Public Service Co. Ltd', 'Hydroelectric power generation', 0.10, 0.00, -101, 'JPS\'s own generating-station account, not a customer defection')]
nrow = ''.join(f'<tr><td class="l">{a}</td><td class="l">{b}</td><td>{c:.2f}</td><td>{d:.2f}</td><td class="neg">{M}{abs(e)}%</td><td class="l">{f}</td></tr>\n' for a, b, c, d, e, f in NAMED)
A('<h2>6. Customer Defection</h2>')
A(f'<p>A commercial customer is treated as defecting when its consumption for January to September 2026 is more than 80% below the same period of 2025. On that definition {totn} customers qualify, with a combined 2025 volume of {tot25:.1f} GWh that has fallen to {tot26:.1f} GWh &mdash; a loss of {loss:.1f} GWh, or about {loss/(YT("com",2025,1)/1e6)*100:.1f}% of commercial volume and roughly {loss/com_decl*100:.0f}% of the {com_decl:.0f} GWh decline in commercial sales. Defection is real but small; most of the decline in the commercial base comes from customers that reduced volume without leaving.</p>')
A('<p>Each defection is classified as operational (a business that closed, was damaged or released capacity) or self-generation (a customer that now supplies itself but stays connected), based on when the drop occurred and whether the customer kept its contracted demand.</p>')
A(tbl(['Likely cause', 'Customers', 'GWh Jan&ndash;Sep 2025', 'GWh Jan&ndash;Sep 2026', 'GWh lost', 'Share of loss'], drow.rstrip('\n').split('\n'),
      f'<tr class="tot"><td class="l">Total</td><td>{totn}</td><td>{tot25:.2f}</td><td>{tot26:.2f}</td><td class="neg">{M}{loss:.2f}</td><td>100%</td></tr>'))
A(f'<p>About {oper/loss*100:.0f}% of the volume lost to defection is operational, and most of it is storm-related: customers whose consumption fell away in the two months after the hurricane and have not come back, plus 54 that are recovering. Only two customers carry the self-generation signature of near-zero kWh with grid capacity held, and together they account for under 2% of the loss; one of them is JPS\'s own generating-station account rather than a customer. The four customers that released contracted capacity outside the storm window (Carib Products, Dougall Flooring and two others) are the ones to confirm directly, since a capacity cut can also follow a move to on-site generation. Alcoa does not appear here because it ran at normal volume for the first seven months of 2026, so its year-to-date total is down only {abs(alc_ytd_chg):.0f}%; on its current run rate (about 0.8 GWh a month against 7 to 9 before) it is down about 91%, and it is the one large, confirmed self-generation case in the base.</p>')
A('<h3>Largest defecting customers (2025 volume of 0.1 GWh or more)</h3>')
A(tbl(['Customer', 'Industry', 'GWh 2025', 'GWh 2026', 'Change', 'Likely cause'], nrow.rstrip('\n').split('\n')).replace('<th>Industry</th>', '<th class="l">Industry</th>').replace('<th>Likely cause</th>', '<th class="l">Likely cause</th>'))
A('<p class="note">Cause is an indicator, not a confirmation. The 236 small-business customers in "no clear signal" carry no demand charge, so the demand test cannot be applied to them.</p>')

json.dump({'body': '\n'.join(out)}, open('_sep_body_a.json', 'w'))
print('part A ok; months_down', months_down, 'rate', rate, 'dem_all', dem_all, 'rt70_sep', rt70_sep, 'alcoa ytd chg %.1f' % alc_ytd_chg, 'alc sep', alc_sep, 'rt50 ex falmouth %.1f rt70 ex %.1f' % (pct(*rt50k), pct(*rt70k)))
print('CB rev', CB[2025]['rev'], CB[2026]['rev'], 'ALLR', ALLR, 'gct', CB[2025]['gct'], CB[2026]['gct'], 'jun pp gct est rate %.4f' % _jun_rate)
