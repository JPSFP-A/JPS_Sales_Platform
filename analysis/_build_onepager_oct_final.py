# -*- coding: utf-8 -*-
# One-page October 2026 sales analysis, BEFORE prepaid. Everything is computed from the loaded data (platform RPCs and the
# zero-streak result), not typed in. Reuses the September one-pager's styling. Rendered by render_onepager.js.
import csv, json, os, sys, requests
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '_cust'))
from db import BASE, H, fetch
csv.field_size_limit(10 ** 9)

src = open('_build_onepagers.py', encoding='utf-8').read()
exec(src.split('# =====================================================================  SALES ONE-PAGER')[0])   # CSS, bars(), helpers, colours

def chg(x, d=1):      # no sign on a value that rounds to zero
    s_ = f'{abs(x):.{d}f}'
    return '' + (s_ if round(x, d) == 0 else (('+' if x > 0 else MINUS) + s_))
def chgp(x, d=1): return chg(x * 100, d) + '%'

def rpc(fn, body):
    r = requests.post(f'{BASE}/rest/v1/rpc/{fn}', headers={**H, 'Content-Type': 'application/json'}, data=json.dumps(body), timeout=300)
    r.raise_for_status(); return r.json()

rows = rpc('get_comm_actuals', {'year_cutoff': 2025}) + rpc('get_res_actuals', {'year_cutoff': 2025})
f = lambda v: float(v or 0)
def agg(y, m, rc=None, bucket_ne_prepaid=True, acct=None):
    k = r = 0.0
    for x in rows:
        if x['year'] != y or x['month'] != m: continue
        if rc and x['rate_class'] != rc: continue
        if bucket_ne_prepaid and x['consumption_bucket'] == 'Prepaid': continue
        if acct and x['jps_ac'] != acct: continue
        k += f(x['kwh']); r += f(x['revenue_jmd'])
    return k / 1e6, r / 1e6          # GWh, J$M
A = {c: {'o26': agg(2026, 10, c, False), 'o25': agg(2025, 10, c, False), 's26': agg(2026, 9, c, False), 's25': agg(2025, 9, c, False)} for c in ORDER}
prepaid_sep = sum(f(x['kwh']) for x in rows if x['year'] == 2026 and x['month'] == 9 and x['consumption_bucket'] == 'Prepaid') / 1e6
pp_oct = sum(f(x['kwh']) for x in rows if x['year'] == 2026 and x['month'] == 10 and x['consumption_bucket'] == 'Prepaid') / 1e6
assert pp_oct > 2.0, 'October prepaid is not loaded'
pp_oct25 = sum(f(x['kwh']) for x in rows if x['year'] == 2025 and x['month'] == 10 and x['consumption_bucket'] == 'Prepaid') / 1e6

bc = {r['rate_class']: r for r in fetch('jps_budget_class_month', 'select=*&year=eq.2026&month=eq.10', page=1000)}
bag = rpc('get_budget_agg', {'year_cutoff': 2026})
bud_pre = {c: sum(f(x['kwh_budget']) for x in bag if x['month'] == 10 and x['year'] == 2026 and x['rate_class'] == c and x['consumption_bucket'] != 'Prepaid') / 1e6 for c in ORDER}
for c in ORDER: assert abs(bud_pre[c] + sum(f(x['kwh_budget']) for x in bag if x['month'] == 10 and x['year'] == 2026 and x['rate_class'] == c and x['consumption_bucket'] == 'Prepaid') / 1e6 - f(bc[c]['kwh_budget']) / 1e6) < 0.01, c
bud_pre = {c: f(bc[c]['kwh_budget']) / 1e6 for c in ORDER}   # full-class budget, prepaid included
T = lambda key, i: sum(A[c][key][i] for c in ORDER)
o26, o25, s26 = T('o26', 0), T('o25', 0), T('s26', 0)
r26, r25 = T('o26', 1), T('o25', 1)
bud = sum(bud_pre.values())
assert abs(o26 - 294.30) < 0.02, o26
rate26, rate25 = r26 / o26, r25 / o25            # J$M per GWh is J$ per kWh
big = ['RT40', 'RT50', 'RT60-ST', 'RT70']
c26 = sum(A[c]['o26'][0] for c in big); c25 = sum(A[c]['o25'][0] for c in big); cb = sum(bud_pre[c] for c in big)
res_var = sum(A[c]['o26'][0] - bud_pre[c] for c in ('RT10', 'RT20'))
com_var = c26 - cb

# accounts
def acct(ac, y, m): return agg(y, m, None, True, ac)[0]
alcoa = '100185-607213'; cem = '302571-686496'; bro = '100058-1154117'; petro = '101188-101755'
alc26 = acct(alcoa, 2026, 10); alc_bud = sum(f(x['kwh_budget']) for x in bag if x['jps_ac'] == alcoa and x['year'] == 2026 and x['month'] == 10) / 1e6
alc_rate26 = agg(2026, 10, None, True, alcoa)[1] / alc26 if alc26 else 0
alc_rev3 = sum(agg(2026, m, None, True, alcoa)[1] for m in (7, 8, 9)); alc_k3 = sum(acct(alcoa, 2026, m) for m in (7, 8, 9))   # J$M and GWh
cem26, cem25 = acct(cem, 2026, 10), acct(cem, 2025, 10)
pet26, pet_s = acct(petro, 2026, 10), acct(petro, 2026, 9)
ind = {r['jps_ac']: r['industry'] for r in fetch('jps_industries', 'select=jps_ac,industry', page=1000)}
hot = lambda a: 'Hotels' in (ind.get(a.split('-')[0]) or '')
hot26 = sum(f(x['kwh']) for x in rows if x['year'] == 2026 and x['month'] == 10 and x['jps_ac'] and hot(x['jps_ac']) and x['rate_class'] in big) / 1e6
hot_b = sum(f(x['kwh_budget']) for x in bag if x['year'] == 2026 and x['month'] == 10 and x['jps_ac'] and hot(x['jps_ac']) and x['rate_class'] in big) / 1e6
by = {}
for x in rows:
    if x['jps_ac'] and x['year'] == 2026 and x['month'] in (8, 9, 10) or (x['jps_ac'] and x['year'] == 2025 and x['month'] == 10):
        by.setdefault(x['jps_ac'], {})[(x['year'], x['month'])] = f(x['kwh'])
stopped = [a for a, d in by.items() if d.get((2026, 10), 0) == 0 and d.get((2026, 9), 0) > 0]
restarted = [a for a, d in by.items() if d.get((2026, 10), 0) > 0 and d.get((2026, 9), 0) == 0]
newac = [a for a in restarted if by[a].get((2026, 8), 0) == 0 and by[a].get((2025, 10), 0) == 0]
st_k = sum(by[a].get((2026, 9), 0) for a in stopped) / 1e3; re_k = sum(by[a].get((2026, 10), 0) for a in restarted) / 1e3
z = json.load(open('_zero_streak_result_2026-10.json')); zs = z['streaks']; zt = z['monthly_zero_accounts']
zn = lambda lo: sum(1 for s in zs if s['streak_len'] >= lo)
rt10z = z['rt10_monthly_zero_count']
netb = lambda y, m: (sum(f(x['customer_count']) for x in rows if x['year'] == y and x['month'] == m and x['rate_class'] == 'RT10' and x['consumption_bucket'] == '<Zero'), sum(f(x['kwh']) for x in rows if x['year'] == y and x['month'] == m and x['rate_class'] == 'RT10' and x['consumption_bucket'] == '<Zero') / 1e3)
nb26, nb_s = netb(2026, 10), netb(2026, 9)

# raw-file flags: credits on rows the load excludes as not billed
nb = []; nb_k = 0.0
with open('Oct 26.csv', encoding='utf-8', errors='replace', newline='') as fh:
    for r in csv.DictReader(fh):
        if (r.get('cust_billed') or '').strip() == '1' or not ((r.get('Srat_Code') or '').strip() or (r.get('rate_class') or '').strip()): continue
        try: k = float(str(r.get('net_kwh_billed_consump') or 0).replace(',', ''))
        except ValueError: k = 0.0
        nb_k += k
        if k < -50000: nb.append(((r.get('Name') or '').strip(), k))
nb.sort(key=lambda x: x[1])
nb = [((n if ',' not in n else 'a residential account'), k) for n, k in nb]

import openpyxl
_ws = openpyxl.load_workbook(r'C:\Projects\Sales_Platform\JPS_Billed_Sales_and_Net_Gen_FY2026-28_v5.xlsx', data_only=True)['Billed by rate class']
_hdr = [c.value for c in _ws[4]]; _oc = _hdr.index('Oct 26')
LE = {}
for r in _ws.iter_rows(min_row=5, values_only=True):
    k = str(r[0] or '').split(' ')[0].replace('RT60', 'RT60-ST')
    if k in ORDER: LE[k] = float(r[_oc])
assert set(LE) == set(ORDER), LE
le_tot = sum(LE.values())
pp = {c: 0.0 for c in ORDER}
est = lambda c: A[c]['o26'][0] + pp[c]
rows_html = []
for i, c in enumerate(ORDER):
    a26, ra26 = A[c]['o26']; a25, ra25 = A[c]['o25']; as_, _ = A[c]['s26']; b = bud_pre[c]
    pcell = lambda v: f'<td style="color:{col(v)};font-weight:bold">{chgp(v)}</td>'
    rows_html.append(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap">{NAMES[c]}</td><td>{a26:,.1f}</td><td>{a25:,.1f}</td>{pcell(a26 / a25 - 1)}<td>{b:,.1f}</td>{pcell(a26 / b - 1)}<td>{LE[c]:,.1f}</td>{pcell(a26 / LE[c] - 1)}{pcell(ra26 / ra25 - 1)}</tr>')
rows_html.append(f'<tr class="tot"><td class="l">Total system</td><td>{o26:,.1f}</td><td>{o25:,.1f}</td><td>{chgp(o26 / o25 - 1)}</td><td>{bud:,.1f}</td><td>{chgp(o26 / bud - 1)}</td><td>{le_tot:,.1f}</td><td>{chgp(o26 / le_tot - 1)}</td><td>{chgp(r26 / r25 - 1)}</td></tr>')

zero_rows = f'''<table class="t7"><tr><th class="l">Billed at zero kWh</th><th>Oct 2026</th><th>Sep 2026</th><th>Oct 2025</th></tr>
<tr><td class="l">Accounts (RT20 and above)</td><td>{zt["2026-10"]["zero"]}</td><td>{zt["2026-09"]["zero"]}</td><td>{zt["2025-10"]["zero"]}</td></tr>
<tr class="alt"><td class="l">  of which RT20 / RT40 to RT70</td><td>{zt["2026-10"]["RT20"]} / {zt["2026-10"]["RT40-RT70"]}</td><td>{zt["2026-09"]["RT20"]} / {zt["2026-09"]["RT40-RT70"]}</td><td>{zt["2025-10"]["RT20"]} / {zt["2025-10"]["RT40-RT70"]}</td></tr>
<tr><td class="l">RT10 customers at zero</td><td>{rt10z["2026-10"]:,}</td><td>{rt10z["2026-09"]:,}</td><td>{rt10z["2025-10"]:,}</td></tr></table>'''

alc_share = (alc26 - alc_bud) / com_var
html = f'''<!doctype html><html><head><meta charset="utf-8"><title>JPS Sales Analysis October 2026</title><style>{CSS}
.kpi .v {{ font-size: 17pt; }} .head {{ font-size: 12pt; margin: 3mm 0 2.6mm; }} .kpis {{ margin-bottom: 3mm; }} .watch {{ margin-top: 2.6mm; font-size: 8.2pt; padding: 1.8mm 3mm; }} .page {{ padding-top: 9mm; }} .items .it {{ margin-bottom: 1.6mm; }} .items .it b {{ font-size: 8.6pt; }} .items {{ font-size: 8.3pt; }} .box ul {{ margin: 0; padding-left: 4mm; font-size: 8.1pt; }} .box li {{ margin-bottom: 1.2mm; }}
</style></head><body><div class="page">
<div class="top"><div><h1>Sales Analysis: October 2026</h1></div><div class="sub">Jamaica Public Service<br>Customer-billed volume and net revenue before GCT</div></div>
<div class="head">Sales were {o26:,.1f} GWh, {abs(o26 / o25 - 1) * 100:.1f}% {"above" if o26 >= o25 else "below"} October last year and {abs(o26 / bud - 1) * 100:.1f}% {"above" if o26 >= bud else "below"} budget. The mass market carried the month while RT40 to RT70 ran {abs(com_var):.1f} GWh {"below" if com_var < 0 else "above"} budget{f", {alc_share * 100:.0f}% of it Alcoa" if com_var < 0 else ""}.</div>
<div class="kpis">
 <div class="kpi"><div class="l">October sales</div><div class="v">{o26:,.1f} <small>GWh</small></div><div class="d" style="color:{BLUE}">{chgp(o26 / o25 - 1)} vs 2025</div><div class="n">{chg((o26 / bud - 1) * 100)}% vs budget; {chg((o26 / le_tot - 1) * 100)}% vs LE</div></div>
 <div class="kpi"><div class="l">October revenue</div><div class="v">J${r26 / 1000:,.1f} <small>bn</small></div><div class="d" style="color:{BLUE}">{chgp(r26 / r25 - 1)} vs 2025</div><div class="n">Average rate J${rate26:,.1f} per kWh, {chgp(rate26 / rate25 - 1)} on 2025</div></div>
 <div class="kpi c"><div class="l">RT40 to RT70</div><div class="v">{c26:,.1f} <small>GWh</small></div><div class="d" style="color:{RED}">{chg((c26 / cb - 1) * 100)}% vs budget</div><div class="n">{chg((c26 / c25 - 1) * 100)}% vs 2025; Alcoa alone {chg(alc26 - alc_bud)} GWh vs budget</div></div>
 <div class="kpi c"><div class="l">Accounts billed at zero</div><div class="v">{zt["2026-10"]["zero"]} <small>of {zt["2026-10"]["accounts"]:,}</small></div><div class="d" style="color:{GREY}">{zt["2026-09"]["zero"]} in September</div><div class="n">{zn(12)} at zero for 12+ months; none at $0 revenue</div></div>
</div>
<div class="row">
 <div style="flex:2.05"><div class="sec">By rate class (GWh)</div>
 <table class="t7"><tr><th class="l" rowspan="2">Rate class</th><th colspan="5">October</th><th colspan="2">Forecast (LE)</th><th rowspan="2">Revenue<br>vs 2025</th></tr>
 <tr><th class="sub">Actual</th><th class="sub">2025</th><th class="sub">vs 2025</th><th class="sub">Budget</th><th class="sub">vs budget</th><th class="sub">LE</th><th class="sub">vs LE</th></tr>
 {''.join(rows_html)}</table>
 <div style="font-size:7.3pt;color:{GREY};margin-top:1.4mm">Budget, LE and 2025 include prepaid. October prepaid was {pp_oct:.1f} GWh ({(pp_oct / pp_oct25 - 1) * 100:+.0f}% on October 2025). The October 2025 base includes the late-October storm.</div></div>
 <div style="flex:1"><div class="sec">Variance vs budget (GWh)</div>
 {bars([(NAMES[c].split(' ')[0], A[c]['o26'][0] - bud_pre[c]) for c in ORDER], w=250, label_w=40, row_h=15)}
 <div class="sec" style="margin-top:2mm">Variance vs forecast (GWh)</div>
 {bars([(NAMES[c].split(' ')[0], A[c]['o26'][0] - LE[c]) for c in ORDER], w=250, label_w=40, row_h=15)}</div>
</div>
<div class="row" style="margin-top:3.6mm">
 <div class="box items" style="flex:1.2"><div class="sec">What moved October</div>
  <div class="it"><div class="num">1</div><div><b>The mix, not the total, missed budget</b>RT10 and RT20 ran {res_var:.1f} GWh above budget and RT40 to RT70 {abs(com_var):.1f} GWh below. RT10 is {abs(A["RT10"]["o26"][0] / A["RT10"]["s26"][0] - 1) * 100:.1f}% {"below" if A["RT10"]["o26"][0] < A["RT10"]["s26"][0] else "above"} September; last year it moved {chg((A["RT10"]["o25"][0] / A["RT10"]["s25"][0] - 1) * 100)}%.</div></div>
  <div class="it"><div class="num">2</div><div><b>Alcoa billed {alc26 * 1000:,.0f} MWh against a budget of {alc_bud * 1000:,.0f}</b>Down from 9.0 GWh in July to {acct(alcoa, 2026, 8) * 1000:,.0f}, {acct(alcoa, 2026, 9) * 1000:,.0f} and {alc26 * 1000:,.0f} MWh as its own generation took over; not expected back.</div></div>
  <div class="it"><div class="num">3</div><div><b>Hotels {hot26:.1f} GWh against {hot_b:.1f} budget</b>{chg(hot26 - hot_b)} GWh. Half Moon Bay, Playa Hall and Seawind Key are still a fraction of last October.</div></div>
  <div class="it"><div class="num">4</div><div><b>Against the forecast, RT10 is the miss</b>The LE has RT10 at {LE["RT10"]:.1f} GWh, {chgp(LE["RT10"] / (A["RT10"]["s26"][0] + pp["RT10"]) - 1)} on September. It moved {chg((A["RT10"]["o26"][0] / A["RT10"]["s26"][0] - 1) * 100)}% on September; last year it moved {chg((A["RT10"]["o25"][0] / A["RT10"]["s25"][0] - 1) * 100)}%. RT40 to RT70 beat the LE by {sum(A[c]["o26"][0] - LE[c] for c in big):.1f} GWh.</div></div>
  <div class="it"><div class="num">5</div><div><b>Accounts churned</b>Caribbean Cement and Petrojam offset ({cem26:.1f} and {pet26:.1f} GWh). {len(stopped)} accounts above RT10 stopped billing ({st_k:,.0f} MWh in September), {len(restarted)} restarted ({re_k:,.0f} MWh) and {len(newac)} are new, including PriceSmart.</div></div>
 </div>
 <div style="flex:1">
  <div class="box" style="margin-bottom:3mm"><div class="sec">Billed at zero</div>{zero_rows}
   <div style="font-size:7.6pt;margin-top:1.6mm">{zn(2)} of the {len(zs)} have been at zero for 2+ months, {zn(6)} for 6+ and {zn(12)} for 12+. {sum(1 for s in zs if s["account_status"] == "A")} are Active and {sum(1 for s in zs if s["is_minbill_cluster"])} are on a shared minimum-bill tariff, so none bills $0; the question is whether the meter is being read. RT10 zero customers are {rt10z["2026-10"] / rt10z["2025-10"] * 100 - 100:.0f}% above October 2025, down from {rt10z["2025-12"]:,} in December.</div></div>
  <div class="box"><div class="sec">Data flags</div><ul>
   <li>Alcoa's rate fell to J${alc_rate26:,.1f}/kWh from J${alc_rev3 / alc_k3:,.1f} over July to September. Its demand charges are provisional.</li>
   <li>Credits on rows the load excludes as not billed total {nb_k / 1e3:,.0f} MWh, led by {nb[0][0][:30]} ({nb[0][1] / 1e3:,.0f} MWh) and {nb[1][0][:30]} ({nb[1][1] / 1e3:,.0f} MWh). Confirm with billing whether they are reversals.</li>
   <li>RT10 net-export accounts fell to {nb26[0]:,.0f} from {nb_s[0]:,.0f} but their export rose to {abs(nb26[1]):,.0f} MWh from {abs(nb_s[1]):,.0f}.</li>
   </ul></div>
 </div>
</div>
<div class="watch"><b>Prepaid.</b> October prepaid is loaded at {pp_oct:.1f} GWh ({(pp_oct / pp_oct25 - 1) * 100:+.0f}% on October 2025), against {prepaid_sep:.1f} GWh in September. It is included in every figure on this page.</div>
<div class="foot"><span><b>Jamaica Public Service</b> | Sales Analysis | October 2026</span><span>Customer-billed basis. Variances are against October 2025 and the approved budget.</span></div>
</div></body></html>'''
p = os.path.join(r'C:\Projects\Sales_Platform\analysis', '_onepager_JPS_OnePager_Sales_Analysis_Oct2026_Final.html')
open(p, 'w', encoding='utf-8').write(html)
print('wrote', p)
print('total %.3f LY %.3f bud %.3f | RT40-70 %.3f bud %.3f | alcoa %.3f/%.3f | hotels %.2f/%.2f | stopped %d restarted %d new %d | zero %d' % (o26, o25, bud, c26, cb, alc26, alc_bud, hot26, hot_b, len(stopped), len(restarted), len(newac), zt['2026-10']['zero']))
