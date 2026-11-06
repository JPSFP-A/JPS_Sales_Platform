# -*- coding: utf-8 -*-
# October one-pager v3: year-to-date table and variance, National Water Commission by parish, Petrojam fire shutdown, billing-days note, plainer wording.
d = open('_build_onepager_oct_final.py', encoding='utf-8').read()
def rep(a, b):
    global d
    assert a in d, a[:100]
    d = d.replace(a, b, 1)

rep("rows_html = []\n", '''import collections as _c
_S = _c.defaultdict(float); _R = _c.defaultdict(float)
for x in rows:
    if x['year'] in (2025, 2026) and 1 <= int(x['month']) <= 10:
        _S[(x['year'], x['rate_class'])] += f(x['kwh']) / 1e6; _R[(x['year'], x['rate_class'])] += f(x['revenue_jmd']) / 1e6
Y26 = {c: _S[(2026, c)] for c in ORDER}; Y25 = {c: _S[(2025, c)] for c in ORDER}
assert abs(sum(Y26.values()) - 2723.33) < 0.1 and abs(sum(Y25.values()) - 2839.09) < 0.1, (sum(Y26.values()), sum(Y25.values()))
_bm = fetch('jps_budget_class_month', 'select=*&year=eq.2026', page=1000)
YB = {c: sum(f(r['kwh_budget']) for r in _bm if r['rate_class'] == c and int(r['month']) <= 10) / 1e6 for c in ORDER}
y26, y25, ybud = sum(Y26.values()), sum(Y25.values()), sum(YB.values())
yr26, yr25 = sum(_R[(2026, c)] for c in ORDER), sum(_R[(2025, c)] for c in ORDER)
_pc = lambda v: f'<td style="color:{col(v)};font-weight:bold">{chgp(v)}</td>'
ytd_rows = []
for i, c in enumerate(ORDER):
    a, p, b = Y26[c], Y25[c], YB[c]
    ytd_rows.append(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap">{NAMES[c]}</td><td>{a:,.1f}</td><td>{p:,.1f}</td>{_pc(a / p - 1)}<td>{b:,.1f}</td>{_pc(a / b - 1)}{_pc(_R[(2026, c)] / _R[(2025, c)] - 1)}</tr>')
ytd_rows.append(f'<tr class="tot"><td class="l">Total system</td><td>{y26:,.1f}</td><td>{y25:,.1f}</td><td>{chgp(y26 / y25 - 1)}</td><td>{ybud:,.1f}</td><td>{chgp(y26 / ybud - 1)}</td><td>{chgp(yr26 / yr25 - 1)}</td></tr>')
ytd_html = ('<div class="sec" style="margin-top:3mm">Year to date, January to October (GWh)</div><table class="t7"><tr><th class="l">Rate class</th><th>2026</th><th>2025</th><th>vs 2025</th><th>Budget</th><th>vs budget</th><th>Revenue<br>vs 2025</th></tr>'
            + ''.join(ytd_rows) + f'</table><div style="font-size:7.3pt;color:{GREY};margin-top:1.2mm">January and February budget equals actuals, so the budget comparison is flattered. 2025 is the cleaner base.</div>')
_nw = _c.defaultdict(lambda: _c.defaultdict(float))
for x in rows:
    if x['jps_ac'] and x['jps_ac'].startswith('100012-') and (x['year'], x['month']) in ((2026, 9), (2026, 10), (2025, 10)):
        _nw[x['parish']][(x['year'], x['month'])] += f(x['kwh']) / 1e6
nw_o26 = sum(v[(2026, 10)] for v in _nw.values()); nw_s26 = sum(v[(2026, 9)] for v in _nw.values()); nw_o25 = sum(v[(2025, 10)] for v in _nw.values())
assert abs(nw_o26 - 18.41) < 0.1, nw_o26
nw_top = sorted(((v[(2026, 10)] - v[(2026, 9)], p) for p, v in _nw.items()), reverse=True)[:2]
nw_share = sum(t[0] for t in nw_top) / (nw_o26 - nw_s26)
rows_html = []
''')
rep('<div class="head">Sales were {o26:,.1f} GWh, {abs(o26 / o25 - 1) * 100:.1f}% {"above" if o26 >= o25 else "below"} October last year and {abs(o26 / bud - 1) * 100:.1f}% {"above" if o26 >= bud else "below"} budget. The mass market carried the month while RT40 to RT70 ran {abs(com_var):.1f} GWh {"below" if com_var < 0 else "above"} budget{f", {alc_share * 100:.0f}% of it Alcoa" if com_var < 0 else ""}.</div>',
    '<div class="head">Sales were {o26:,.1f} GWh, {abs(o26 / o25 - 1) * 100:.1f}% {"above" if o26 >= o25 else "below"} October last year and {abs(o26 / bud - 1) * 100:.1f}% {"above" if o26 >= bud else "below"} budget. Year to date sales are {y26:,.1f} GWh, {abs(y26 / y25 - 1) * 100:.1f}% below 2025. RT40 to RT70 ran {abs(com_var):.1f} GWh below budget in October, {alc_share * 100:.0f}% of it Alcoa.</div>')
rep("The October 2025 base includes the late-October storm.</div></div>", "October 2025 had fewer billing days because billing ran a few days early after the hurricane.</div>{ytd_html}</div>")
rep('<div class="sec" style="margin-top:2mm">Variance vs forecast (GWh)</div>\n {bars([(NAMES[c].split(\' \')[0], A[c][\'o26\'][0] - LE[c]) for c in ORDER], w=250, label_w=40, row_h=15)}</div>',
    '<div class="sec" style="margin-top:2mm">Year to date vs 2025 (GWh)</div>\n {bars([(NAMES[c].split(\' \')[0], Y26[c] - Y25[c]) for c in ORDER], w=250, label_w=40, row_h=15)}</div>')
rep('<b>The mix, not the total, missed budget</b>', '<b>Mix against budget</b>')
rep('<b>Against the forecast, RT10 is the miss</b>', '<b>RT10 against the forecast</b>')
rep('<b>Accounts churned</b>Caribbean Cement and Petrojam offset ({cem26:.1f} and {pet26:.1f} GWh). {len(stopped)} accounts above RT10 stopped billing ({st_k:,.0f} MWh in September), {len(restarted)} restarted ({re_k:,.0f} MWh) and {len(newac)} are new, including PriceSmart.</div></div>',
    '<b>National Water Commission</b>{nw_o26:.1f} GWh, {chg(nw_o26 - nw_s26)} GWh on September and {chg(nw_o26 - nw_o25)} GWh on last October. {nw_top[0][1]} and {nw_top[1][1]} are {nw_share * 100:.0f}% of the monthly rise.</div></div>\n  <div class="it"><div class="num">6</div><div><b>Account changes</b>Petrojam billed {pet26:.1f} GWh after a two-week fire shutdown in September ({pet_s:.1f} GWh). Caribbean Cement billed {cem26:.1f} GWh. {len(stopped)} accounts above RT10 stopped billing ({st_k:,.0f} MWh in September), {len(restarted)} restarted ({re_k:,.0f} MWh) and {len(newac)} are new, including PriceSmart.</div></div>')
rep("'_onepager_JPS_OnePager_Sales_Analysis_Oct2026_Final.html'", "'_onepager_JPS_OnePager_Sales_Analysis_Oct2026_v3.html'")
open('_build_onepager_oct_v3.py', 'w', encoding='utf-8').write(d)
print('ok')
