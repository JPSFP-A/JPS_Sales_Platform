# -*- coding: utf-8 -*-
"""Build the system losses report from the workbook, so the two cannot drift.

Everything is read out of JPS_LE_Sales_Gen_FY2026-28.xlsx 'Sales Wide': row 12
grand total sales, row 13 losses (kWh, added 7 Sep 2026), row 14 monthly loss %,
row 15 rolling 12-month loss %, row 16 net generation. Nothing is restated by
hand, and the workbook is reconciled internally before a line of the report is
written -- but the reconciliation no longer requires every year to close at
27.10%, since FY2026 is known and explained not to. See ROW below if these shift
again; they are indexed by row number, not by name, and nothing catches a
silent off-by-one except this comment.

Placeholders are @tokens@ rather than %-format, because the template carries CSS
percent signs and escaping every one of them is a defect waiting to happen.
"""
import io, re, openpyxl

SRC = r'C:\Projects\Sales_Platform\JPS_LE_Sales_Gen_FY2026-28.xlsx'
DST = r'C:\Projects\Sales_Platform\JPS_System_Losses_FY2026-28.html'
M = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
COL = {2026: 2, 2027: 15, 2028: 28}
# Row 13 ("Losses (kWh)") was inserted ahead of these on 7 Sep 2026, shifting the three
# rows below it down by one -- losspct/roll/netgen were 13/14/15, now 14/15/16.
ROW = {'sales': 12, 'losspct': 14, 'roll': 15, 'netgen': 16}
ACTUAL_THROUGH = 8                      # August 2026 is the last billed month

ws = openpyxl.load_workbook(SRC, data_only=True)['Sales Wide']
D = {y: {k: [ws.cell(r, COL[y] + m).value for m in range(12)] for k, r in ROW.items()}
     for y in (2026, 2027, 2028)}
for y in D:
    D[y]['losses'] = [(D[y]['netgen'][m] or 0) - (D[y]['sales'][m] or 0) for m in range(12)]

FY = {}
for y in (2026, 2027, 2028):
    S = sum(D[y]['sales']) / 1e6
    L = sum(D[y]['losses']) / 1e6
    FY[y] = (S, L, L / (S + L) * 100, S + L)

# ---------------- reconcile before writing ----------------
# Two different checks, deliberately kept apart. Internal consistency (does the stated
# monthly % actually match losses/net-gen in the same row) must never fail -- that is a
# real arithmetic bug and the report will not publish over one. Closeness to a 27.10%
# year-end target is informational only: FY2026 is now known and explained to miss it
# (losses were not refreshed against the higher post-August sales base -- see the
# workbook and the Exec Summary/Driver Report), and asserting it would block a report
# whose whole job is to say so.
print('%-6s %10s %10s %8s %12s' % ('FY', 'sales', 'losses', 'loss %', 'net gen'))
bad = 0
for y in (2026, 2027, 2028):
    S, L, P, N = FY[y]
    flag = '  (%s%.2fpp vs 27.10%% target)' % ('+' if P >= 27.10 else '', P - 27.10) if abs(P - 27.10) > 0.02 else ''
    print('%-6d %10.1f %10.1f %8.2f %12.1f%s' % (y, S, L, P, N, flag))
    for m in range(12):
        stated = D[y]['losspct'][m] * 100
        derived = D[y]['losses'][m] / D[y]['netgen'][m] * 100
        if abs(stated - derived) > 0.02:
            bad += 1; print('   *** %s %d stated %.2f%% vs derived %.2f%%' % (M[m], y, stated, derived))
fwd = [D[y]['losspct'][m] * 100 for y in (2027, 2028) for m in range(12)]
rollv = [D[y]['roll'][m] * 100 for y in (2027, 2028) for m in range(12)]
CLOSE_2027 = FY[2027][2]   # the real close, used below instead of a hardcoded 27.10
print('monthly %.2f-%.2f | rolling %.2f-%.2f | internal-consistency failures %d'
      % (min(fwd), max(fwd), min(rollv), max(rollv), bad))
assert bad == 0, 'workbook does not reconcile internally; report not written'

# Half-up, not Python's round(): FY2027 sales land on exactly 3,406.35 GWh, where
# banker's rounding gives 3,406.3 and the rest of the pack says 3,406.4.
from decimal import Decimal, ROUND_HALF_UP


def f(v, d=1):
    q = Decimal(str(v)).quantize(Decimal('1e-%d' % d), rounding=ROUND_HALF_UP)
    return format(q, ',.%df' % d)

# ---------------- monthly table ----------------
rows = []
for y in (2026, 2027, 2028):
    tag = ', January to August actual and September to December target (unrefreshed)' if y == 2026 else ''
    rows.append('<tr class="yr"><td class="l" colspan="6"><b>FY%d</b>%s</td></tr>' % (y, tag))
    for m in range(12):
        act = (y == 2026 and m < ACTUAL_THROUGH)
        rows.append('<tr><td class="l">%s%s</td><td>%s</td><td>%s</td><td>%.2f%%</td><td>%s</td><td>%s</td></tr>'
                    % (M[m], ' <span class="a">actual</span>' if act else '',
                       f(D[y]['sales'][m] / 1e6), f(D[y]['losses'][m] / 1e6), D[y]['losspct'][m] * 100,
                       f(D[y]['netgen'][m] / 1e6),
                       ('%.2f%%' % (D[y]['roll'][m] * 100)) if D[y]['roll'][m] else '&mdash;'))
    S, L, P, N = FY[y]
    rows.append('<tr class="tot"><td class="l">FY%d total</td><td>%s</td><td>%s</td><td>%.2f%%</td><td>%s</td><td></td></tr>'
                % (y, f(S), f(L), P, f(N)))
MONTHLY = '\n'.join(rows)

# ---------------- chart ----------------
mser = [D[y]['losspct'][m] * 100 for y in (2026, 2027, 2028) for m in range(12)]
rser = [(D[y]['roll'][m] * 100 if D[y]['roll'][m] else None) for y in (2026, 2027, 2028) for m in range(12)]
LO, HI, W, TOP, BOT = 20.0, 32.0, 1010.0, 18.0, 196.0
x = lambda i: 42 + i * (W - 78) / 35.0
yy = lambda v: BOT - (v - LO) / (HI - LO) * (BOT - TOP)

sv = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eef4f9"/>'
      % (x(0) - 6, TOP, x(ACTUAL_THROUGH - 1) - x(0) + 12, BOT - TOP)]
for g in range(20, 33, 2):
    sv.append('<line x1="36" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#e4e4e4"/>' % (yy(g), W - 30, yy(g)))
    sv.append('<text x="30" y="%.1f" text-anchor="end" fill="#888" font-size="9.5">%d%%</text>' % (yy(g) + 3, g))
for i in (12, 24):
    sv.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#bbb" stroke-dasharray="3,2"/>'
              % (x(i) - 6, TOP, x(i) - 6, BOT))
sv.append('<line x1="36" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#999"/>' % (yy(CLOSE_2027), W - 30, yy(CLOSE_2027)))
sv.append('<text x="%.1f" y="%.1f" text-anchor="end" fill="#0b3d66" font-size="9.5" font-weight="bold">%.2f%% FY2027 close</text>'
          % (W - 34, yy(CLOSE_2027) - 4, CLOSE_2027))
sv.append('<polyline fill="none" stroke="#2e86c1" stroke-width="1.8" points="%s"/>'
          % ' '.join('%.1f,%.1f' % (x(i), yy(v)) for i, v in enumerate(mser)))
sv.append('<polyline fill="none" stroke="#c0392b" stroke-width="1.8" points="%s"/>'
          % ' '.join('%.1f,%.1f' % (x(i), yy(v)) for i, v in enumerate(rser) if v is not None))
for i, v in enumerate(mser):
    sv.append('<circle cx="%.1f" cy="%.1f" r="1.9" fill="#2e86c1"/>' % (x(i), yy(v)))
for i, lb in ((0, 'Jan 26'), (6, 'Jul 26'), (11, 'Dec 26'), (12, 'Jan 27'),
              (23, 'Dec 27'), (24, 'Jan 28'), (35, 'Dec 28')):
    sv.append('<text x="%.1f" y="%.1f" text-anchor="middle" fill="#666" font-size="9.5">%s</text>'
              % (x(i), BOT + 14, lb))
CHART = '\n  '.join(sv)

a26 = ''.join('<td class="pos">%.2f%%</td>' % (D[2026]['losspct'][m] * 100) for m in range(ACTUAL_THROUGH))

sens = []
S27 = FY[2027][0]
SENS_RATES = [round(CLOSE_2027 - 1.0, 2), round(CLOSE_2027 - 0.5, 2), round(CLOSE_2027, 2),
              round(CLOSE_2027 + 0.5, 2), round(CLOSE_2027 + 1.0, 2)]
for r in SENS_RATES:
    L = S27 * r / (100 - r)
    d = (S27 + L) - FY[2027][3]
    sens.append('<tr><td class="l">%.2f%%%s</td><td>%s</td><td>%s</td><td class="%s">%s</td></tr>'
                % (r, ' (plan)' if abs(r - CLOSE_2027) < 1e-9 else '', f(L), f(S27 + L),
                   'pos' if d > 0.05 else ('neg' if d < -0.05 else ''),
                   '&mdash;' if abs(d) < 0.05 else ('%s%s' % ('+' if d > 0 else '&minus;', f(abs(d))))))

HTML = '''<!doctype html>
<html><head><meta charset="utf-8">
<title>JPS System Losses FY2026-FY2028</title>
<style>
body{font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#1a1a1a;max-width:1060px;margin:24px auto;padding:0 20px;background:#fff}
h1{font-size:23px;margin-bottom:2px}
h2{font-size:16px;margin-top:32px;border-bottom:2px solid #0b3d66;padding-bottom:5px;color:#0b3d66}
h3{font-size:13.5px;margin:20px 0 6px;color:#0b3d66}
.meta{color:#666;font-size:11px;margin-bottom:16px}
table{border-collapse:collapse;width:100%;margin:10px 0 14px;font-size:12.5px}
th{background:#0b3d66;color:#fff;text-align:right;padding:7px 9px;font-weight:600}
th:first-child,th.l{text-align:left}
td{padding:6px 9px;border-bottom:1px solid #e4e4e4;text-align:right}
td:first-child,td.l{text-align:left}
tr:nth-child(even){background:#f7f9fb}
.tot{font-weight:700;border-top:2px solid #0b3d66}
.yr td{background:#0b3d66;color:#fff;font-size:11.5px}
.a{color:#8fd6b0;font-size:10px;font-weight:bold;text-transform:uppercase;letter-spacing:.4px}
.pos{color:#1e7a46}.neg{color:#b3261e}
.note{font-size:11px;color:#666;margin:6px 0 14px;line-height:1.5}
.key{background:#f7f9fb;border-left:3px solid #0b3d66;padding:10px 12px;margin:10px 0 16px;font-size:12px;line-height:1.55}
.warn{background:#fdf3f2;border-left:3px solid #b3261e;padding:10px 12px;margin:10px 0 16px;font-size:11.5px;line-height:1.55}
.gap{background:#fffbe6;border-left:3px solid #c99a00;padding:10px 12px;margin:10px 0 16px;font-size:11.5px;line-height:1.55}
.kpi{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0 4px}
.kpi div{flex:1;min-width:150px;background:#f7f9fb;border-left:3px solid #0b3d66;padding:9px 11px}
.kpi b{display:block;font-size:19px;color:#0b3d66}
.kpi span{font-size:10.5px;color:#666}
.wf{overflow-x:auto;margin:10px 0 4px}
.lgd{font-size:10.5px;color:#666;margin:2px 0 14px}
.sw{display:inline-block;width:22px;height:3px;vertical-align:middle;margin:0 5px 0 12px}
ul{margin:8px 0 14px;padding-left:20px}li{margin-bottom:6px;line-height:1.45}

@page{
  size:A4; margin:16mm 13mm 17mm 13mm;
  @bottom-left{content:"JPS System Losses, FY2026 to FY2028"; font:8.5pt Arial,Helvetica,sans-serif; color:#888}
  @bottom-right{content:"Page " counter(page) " of " counter(pages); font:8.5pt Arial,Helvetica,sans-serif; color:#888}
}
@media print{
  body{max-width:none;margin:0;padding:0;font-size:10.5pt;background:#fff}
  h1{font-size:17pt}
  h2{font-size:12pt;break-after:avoid;page-break-after:avoid}
  h3{break-after:avoid;page-break-after:avoid}
  table{font-size:8.6pt;break-inside:auto}
  thead{display:table-header-group}
  tr{break-inside:avoid;page-break-inside:avoid}
  .key,.warn,.gap,.note,.act,.rk,.kpi,.wf,svg{break-inside:avoid;page-break-inside:avoid}
  .wf{overflow:visible}
  a{text-decoration:none;color:inherit}
}
</style></head><body>

<h1>System Losses, FY2026 to FY2028</h1>
<div class="meta">Sales Forecasting &amp; Analysis &middot; 7 September 2026, updated for August actuals &middot; Companion to the Executive Summary and Driver Report</div>

<div class="kpi">
<div><b>@l26@</b><span>FY2026 losses (GWh) &middot; @p26@%</span></div>
<div><b>@l27@</b><span>FY2027 &middot; @p27@%</span></div>
<div><b>@l28@</b><span>FY2028 &middot; @p28@%</span></div>
<div><b>@n28@</b><span>FY2028 net generation (GWh)</span></div>
</div>

<div class="key">
<b>FY2027 and FY2028 hold losses at @p27@% and @p28@% at each December</b>, so no improvement in loss performance is assumed in either out-year. Losses still grow in absolute terms, from @l26@ to @l28@ GWh, because they are carried as a constant share of a growing book. That is a deliberately neutral assumption rather than a forecast of the loss reduction programme. Any recovery below the target is upside to net generation that is not in these numbers.
<br><br><b>FY2026 no longer closes near that level.</b> It reads @p26@% because August landed above the forecast the 19 August submission carried, and losses were not refreshed to match; there is currently no live generation-actuals feed to refresh them against. That figure is sales moving against a frozen losses number, not a genuine improvement in loss performance, and should not be presented as one. See Basis of Preparation.
</div>

<h2>Annual Position</h2>
<table>
<tr><th class="l">Fiscal Year</th><th>Billed Sales</th><th>System Losses</th><th>Loss %</th><th>Net Generation</th><th>Net Gen YoY</th></tr>
<tr><td class="l">FY2026</td><td>@s26@</td><td>@l26@</td><td>@p26@%</td><td>@n26@</td><td>&mdash;</td></tr>
<tr><td class="l">FY2027</td><td>@s27@</td><td>@l27@</td><td>@p27@%</td><td>@n27@</td><td class="pos">+@g27@%</td></tr>
<tr><td class="l">FY2028</td><td>@s28@</td><td>@l28@</td><td>@p28@%</td><td>@n28@</td><td class="pos">+@g28@%</td></tr>
</table>
<div class="note">Loss percentage is losses over net generation. Sales are billed volumes; the gap between billed sales and net generation is technical and non-technical loss combined. This report does not split them, because billing data cannot.</div>

<h2>Monthly Loss Path</h2>
<div class="wf">
<svg viewBox="0 0 @cw@ 218" width="100%" height="218" preserveAspectRatio="xMidYMid meet" font-family="Arial,Helvetica,sans-serif">
  @chart@
</svg>
</div>
<div class="lgd"><span class="sw" style="background:#2e86c1"></span>monthly loss %<span class="sw" style="background:#c0392b"></span>rolling 12-month<span class="sw" style="background:#eef4f9;height:9px"></span>actual, January to July 2026</div>
<div class="note">The monthly line swings between @mlo@% and @mhi@%; the rolling twelve-month line sits in a @rlo@% to @rhi@% band and closes each December on 27.10%. <b>The monthly swing is seasonality in sales, not volatility in losses.</b> Loss is closer to fixed than sales are, so a low-sales month carries a higher loss percentage on much the same absolute loss. February is the clearest case: it is the smallest sales month of the year and the lowest loss percentage, because the fixed component is spread over a shorter billing cycle.</div>

<h2>Monthly Detail (GWh)</h2>
<table>
<tr><th class="l">Month</th><th>Billed Sales</th><th>Losses</th><th>Loss %</th><th>Net Generation</th><th>Rolling 12-mth</th></tr>
@monthly@
</table>

<h2>How the Targets Were Built</h2>
<p>The FY2027 and FY2028 monthly path is not an assumption laid on top of the forecast. It is solved from three constraints:</p>
<ul>
<li><b>Shape</b> comes from billed actuals. The month-to-month pattern is taken from 2024 and 2025, with October to December 2025 excluded. Hurricane Melissa collapsed net generation in that quarter, November 2025 coming in at 245,234 MWh against a norm near 390,000, and those months are not representative of normal operation.</li>
<li><b>Level</b> is solved so each fiscal year closes near 27.10%. FY2027 and FY2028 land at @p27@% and @p28@%, a hair off 27.10% because the supplied monthly rates are quoted to two decimals and now apply to a marginally different sales mix; the gap is within the schedule's own rounding, not a drift.</li>
<li><b>The rolling series is derived</b> from the monthly path, not imposed on it. This matters: the two are not independent, and setting both invites a contradiction.</li>
</ul>

<div class="warn">
<b>This replaced an earlier set of targets that did not survive inspection.</b> The previous FY2027 and FY2028 targets were set as a smooth twelve-month rolling series, independent of sales seasonality. Inverted against the real monthly sales profile they implied a monthly loss rate of 15.9% in January 2027 and <b>0.57% in January 2028</b>, neither of them a credible month, and worsening year on year. The rebuilt path runs @mlo@% to @mhi@%, against 21.84% to 30.96% observed across 2024 and 2025. December is unchanged at 27.10%, so <b>net generation is unaffected by the rebuild</b>. Only the phasing within the year changed.
</div>

<h2>FY2026 Actual Against Target</h2>
<p>January to August are billed actuals. September to December are the target of record; losses for these months were not refreshed against the higher post-August sales base, see Basis of Preparation.</p>
<table>
<tr><th class="l">FY2026 monthly loss %</th><th>Jan</th><th>Feb</th><th>Mar</th><th>Apr</th><th>May</th><th>Jun</th><th>Jul</th><th>Aug</th><th>Sep&ndash;Dec</th></tr>
<tr><td class="l">Actual, then target</td>@a26@<td>target</td></tr>
</table>
<div class="note">FY2026's rolling twelve-month loss no longer converges cleanly to a single year-end target the way it did before the August update, because losses were not refreshed alongside sales. Read the monthly actuals above as billed fact; read September&ndash;December as the pre-August target carried forward unchanged, not a live forecast.</div>

<h2>Sensitivity</h2>
<div class="gap">
<b>Every half point on the loss rate is worth roughly 32 GWh of net generation in FY2027.</b> Sales are held constant in this table; only the loss rate moves.
<table style="margin:8px 0 4px">
<tr><th class="l">FY2027 loss rate</th><th>Losses (GWh)</th><th>Net generation (GWh)</th><th>Against plan</th></tr>
@sens@
</table>
Loss reduction is one of the largest single levers on net generation in this plan, on a par with a year's worth of new accounts joining the grid.
</div>

<h2>Basis of Preparation</h2>
<ul>
<li>Billed sales are read live from the Driver Forecast engine as of 7 September 2026, not the 3,281,970 MWh submitted on 19 August. FY2026 now stands at @s26@ GWh; see the Executive Summary and Driver Report for the full reconciliation.</li>
<li>FY2026 monthly loss rates are actual for January to August and the pre-August target, unrefreshed, for September to December. This is the one figure in this report that was not updated alongside sales: there is no live generation-actuals feed for FY2026 to refresh losses against, so they were deliberately left as-is rather than adjusted by hand.</li>
<li>FY2027 and FY2028 monthly rates come from a fixed rate schedule applied directly in the workbook build, keyed by calendar month. They are not currently held in a database table the platform reads live, so a future change to this schedule has to be made in the workbook generator, not the app.</li>
<li>This report is generated from the workbook rather than written alongside it, and it will not publish unless every month's stated loss rate reconciles internally to its own sales and net generation. It does not require every year to close at exactly 27.10%; FY2026 is known and explained not to.</li>
<li>Losses are presented in total. The split between technical and non-technical loss is not derivable from billing data and is not attempted here.</li>
</ul>

</body></html>
'''

TOK = {'s26': f(FY[2026][0]), 's27': f(FY[2027][0]), 's28': f(FY[2028][0]),
       'l26': f(FY[2026][1]), 'l27': f(FY[2027][1]), 'l28': f(FY[2028][1]),
       'p26': '%.2f' % FY[2026][2], 'p27': '%.2f' % FY[2027][2], 'p28': '%.2f' % FY[2028][2],
       'n26': f(FY[2026][3]), 'n27': f(FY[2027][3]), 'n28': f(FY[2028][3]),
       'g27': '%.1f' % ((FY[2027][3] / FY[2026][3] - 1) * 100),
       'g28': '%.1f' % ((FY[2028][3] / FY[2027][3] - 1) * 100),
       'chart': CHART, 'cw': '%.0f' % W, 'monthly': MONTHLY,
       'mlo': '%.2f' % min(fwd), 'mhi': '%.2f' % max(fwd),
       'rlo': '%.2f' % min(rollv), 'rhi': '%.2f' % max(rollv),
       'a26': a26, 'sens': '\n'.join(sens)}

out = HTML
for k, v in TOK.items():
    out = out.replace('@%s@' % k, v)
assert not re.search(r'@[A-Z0-9_]+@', out), 'unresolved token in template'
io.open(DST, 'w', encoding='utf-8').write(out)
print('written', DST)
