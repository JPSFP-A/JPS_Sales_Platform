# -*- coding: utf-8 -*-
# One-page KAM forecast accuracy for October 2026 (HTML; rendered to PDF by ../render_onepager.js).
import collections, json, os
from kam_acc_oct import *
src = open('../_build_onepagers.py', encoding='utf-8').read()
exec(src.split('# =====================================================================  SALES ONE-PAGER')[0])   # CSS, bars(), helpers
def chg(x, d=1):      # no sign on a value that rounds to zero
    t_ = f'{abs(x):.{d}f}'
    return t_ if round(x, d) == 0 else (('+' if x > 0 else MINUS) + t_)
S = json.load(open('_kam_acc_oct_summary.json')); SEP, SEPT = S['sep'], S['sep_tot']
ctx = collections.defaultdict(dict)
for r in d['act']:
    if r['jps_ac'] and r['year'] == 2026 and r['month'] in (7, 8, 9): ctx[r['jps_ac']][r['month']] = ctx[r['jps_ac']].get(r['month'], 0.0) + float(r['kwh'] or 0) / 1e6

T = TOTAL
order = sorted(KAMS, key=lambda k: -BYK[k]['act'])
rows = []
for i, k in enumerate(order):
    s = BYK[k]; sa = SEP[k][1]
    rows.append(f'<tr class="{"alt" if i % 2 else ""}"><td class="l">{k}</td><td>{s["n"]:,}</td><td>{s["fc"]:.1f}</td><td>{s["act"]:.1f}</td><td style="color:{col(s["var"])};font-weight:bold">{chg(s["var"], 2)}</td>'
                f'<td style="background:{fill(s["net"])};font-weight:bold">{pct(s["net"])}</td><td style="background:{fill(s["acct"])};font-weight:bold">{pct(s["acct"])}</td><td>{pct(sa)}</td><td style="color:{col(s["acct"] - sa)}">{chg((s["acct"] - sa) * 100, 1)}</td></tr>')
rows.append(f'<tr class="tot"><td class="l">Total</td><td>{T["n"]:,}</td><td>{T["fc"]:.1f}</td><td>{T["act"]:.1f}</td><td>{chg(T["var"], 2)}</td><td>{pct(T["net"], 1)}</td><td>{pct(T["acct"], 1)}</td><td>{pct(SEPT[1], 1)}</td><td>{chg((T["acct"] - SEPT[1]) * 100, 1)}</td></tr>')

NOTE = {
 'PAC Kingston Airport Ltd.': 'Billing 0.8 to 0.9 GWh a month; forecast carries an 80% defection.',
 'Caribbean Cement Co Ltd': 'Above its 8.5 GWh base; no adjustment on file.',
 'Windalco': 'Base followed a low August (1.18); load recovered.',
 'Petrojam Ltd': 'Base carried a low September (0.85); October normal.',
 'Alcoa Mins Of Ja Ltd': 'Forecast assumed zero; a small load still bills.',
 'Riu Jamaicotel Limited': 'Falling since July; forecast stayed at the base.',
 'PriceSmart (Jamaica) Ltd': 'New load ramping (0.10 in September); not forecast.',
 'Wisynco Group Limited': 'Rebounded from a soft August.',
 'NFE NORTH HOLDINGS LIMITED': 'August spike (0.82) inflated the base.',
 'Sandals Whitehouse Management Limited': 'Building as the hotel reopens.',
}
mrows = []
for i, a in enumerate(MISSES[:8]):
    mrows.append(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap">{a["name"].strip()[:30]}</td><td class="k">{a["kam"].split(" ")[0]}</td><td>{a["fc"]:.2f}</td><td>{a["act"]:.2f}</td><td style="color:{col(a["miss"])};font-weight:bold">{chg(a["miss"], 2)}</td><td style="text-align:left;font-size:7pt">{NOTE.get(a["name"].strip(), "")}</td></tr>')

big5 = sum(abs(a['miss']) for a in MISSES[:5]) / T['abs']
n05 = sum(1 for a in MISSES if abs(a['miss']) > 0.05)
html = f'''<!doctype html><html><head><meta charset="utf-8"><title>KAM Forecast Accuracy October 2026</title><style>{CSS}
.top h1 {{ font-size: 18pt; white-space: nowrap; }} .t7 td {{ padding: 0.8mm 0.9mm; }} td.k {{ white-space: nowrap; }} .items .it {{ margin-bottom: 1.4mm; }} .items {{ font-size: 8.3pt; }} .kpi .v {{ font-size: 18pt; }} .head {{ font-size: 12pt; margin: 3mm 0 2.6mm; }} .kpis {{ margin-bottom: 3mm; }}
</style></head><body><div class="page">
<div class="top"><div><h1>KAM Forecast Accuracy: October 2026</h1></div><div class="sub">Jamaica Public Service<br>Forecast after the September close vs October billing</div></div>
<div class="head">The KAM forecast was {pct(T["net"], 1)} accurate in total but {pct(T["acct"], 1)} account by account. It was {T["var"]:.1f} GWh low, and the miss is spread across many accounts rather than a few.</div>
<div class="kpis">
 <div class="kpi"><div class="l">Net accuracy</div><div class="v">{pct(T["net"], 1)}</div><div class="d" style="color:{RED}">{chg((T["net"] - SEPT[0]) * 100, 1)} pts on September</div><div class="n">September {pct(SEPT[0], 1)}</div></div>
 <div class="kpi"><div class="l">Account-level accuracy</div><div class="v">{pct(T["acct"], 1)}</div><div class="d" style="color:{BLUE}">{chg((T["acct"] - SEPT[1]) * 100, 1)} pts on September</div><div class="n">September {pct(SEPT[1], 1)}</div></div>
 <div class="kpi c"><div class="l">Forecast vs actual</div><div class="v">{T["fc"]:.1f} <small>GWh</small></div><div class="d" style="color:{GREY}">actual {T["act"]:.1f} GWh</div><div class="n">{chg(T["var"], 2)} GWh, {chg(T["var"] / T["act"] * 100, 1)}% of actual</div></div>
 <div class="kpi c"><div class="l">Accounts missed by over 0.05 GWh</div><div class="v">{n05} <small>of {T["n"]:,}</small></div><div class="d" style="color:{GREY}">top 5 = {big5 * 100:.0f}% of the miss</div><div class="n">September: 29%</div></div>
</div>
<div class="row">
 <div style="flex:2.2"><div class="sec">Accuracy by KAM (GWh)</div>
 <table class="t7"><tr><th class="l">KAM</th><th>Accounts</th><th>Forecast</th><th>Actual</th><th>Variance</th><th>Net</th><th>Account<br>level</th><th>Sep acct<br>level</th><th>Change<br>(pts)</th></tr>{''.join(rows)}</table>
 <div style="font-size:7.3pt;color:{GREY};margin-top:1.4mm">Net = 1 - |actual - forecast| / actual on the KAM total. Account level = 1 - the sum of each account's miss / actual. Green 95%+, amber 85 to 95%.</div></div>
 <div style="flex:1"><div class="sec">Variance by KAM (GWh)</div>{bars([(k.split(' ')[0], BYK[k]['var']) for k in order], w=250, label_w=58, row_h=15)}</div>
</div>
<div class="row" style="margin-top:3.4mm">
 <div style="flex:1.75"><div class="sec">Eight largest account misses (GWh)</div>
 <table class="t7"><tr><th class="l">Customer</th><th>KAM</th><th>Forecast</th><th>Actual</th><th>Miss</th><th class="l" style="text-align:left">What the history shows</th></tr>{''.join(mrows)}</table></div>
</div>
<div class="row" style="margin-top:3.4mm">
 <div class="box items" style="flex:1"><div class="sec">What drove October</div>
  <div class="it"><div class="num">1</div><div><b>Too low by {S["pos"] - 0:.1f} GWh, too high by {abs(S["neg"]):.1f}</b>Accounts above forecast added {S["pos"]:.1f} GWh and accounts below it took {abs(S["neg"]):.1f}, a net {T["var"]:.1f} GWh under.</div></div>
  <div class="it"><div class="num">2</div><div><b>The base misled three large accounts</b>Petrojam (low September), NFE North (high August) and Windalco (low August) follow the three-month base, so a one-off month carried into October.</div></div>
  <div class="it"><div class="num">3</div><div><b>Two defections have not shown up in the bill yet</b>PAC Kingston bills near 0.8 GWh against a forecast of 0.16, and Alcoa still draws 0.26 GWh against zero. New load (PriceSmart) is also late to the forecast.</div></div>
 </div>
 <div class="box" style="flex:0.9"><div class="sec">Ask of the KAMs</div><div style="font-size:8.3pt">For every account that missed by more than 0.1 GWh, add the reason in the workbook (<b>Largest misses</b>, last column). Confirm whether PAC Kingston and Alcoa should stay at their adjusted levels, and whether PriceSmart's ramp should be entered as new load.</div>
  <div style="font-size:7.4pt;color:{GREY};margin-top:2mm">The forecast is the Driver Forecast as it stood after the September close, rebuilt from the data and adjustments on file. It is not a stored snapshot.</div></div>
</div>
<div class="foot"><span><b>Jamaica Public Service</b> | KAM Forecast Accuracy | October 2026</span><span>Account level for KAM-assigned accounts. Account detail is in the accompanying workbook.</span></div>
</div></body></html>'''
p = os.path.join(r'C:\Projects\Sales_Platform\analysis', '_onepager_JPS_OnePager_KAM_Forecast_Accuracy_Oct2026.html')
open(p, 'w', encoding='utf-8').write(html); print('wrote', p)
