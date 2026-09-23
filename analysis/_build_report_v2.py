# -*- coding: utf-8 -*-
# Rebuilds the affected blocks of JPS_Sales_Analysis_Requirements_Sep2026.html:
# segment breakdown (postpaid / prepaid / commercial / combined), revenue composition,
# parish, industry top-10, data gaps and appendix. Inputs are the query results captured
# during the analysis pass; nothing is re-derived by hand.
import re, json, sys

HTML = r'C:\Projects\Sales_Platform\JPS_Sales_Analysis_Requirements_Sep2026.html'
EX = json.load(open(r'C:\Projects\Sales_Platform\analysis\_report_extras.json'))

MINUS = '&minus;'
def n(x, dec=0):
    x = round(x, dec) + 0.0
    s = f'{abs(x):,.{dec}f}'
    return (MINUS + s) if x < 0 else s
def pct(a, b, dec=2):
    return (b / a - 1) * 100 if a else 0.0
def signed(x, dec=0):
    return ('+' if x > 0 else '') + n(x, dec) if x >= 0 else n(x, dec)
def chg(a, b, dec=0, pdec=2, cls=True):
    d = b - a; p = pct(a, b)
    c = ('pos' if d > 0 else 'neg' if d < 0 else '') if cls else ''
    ps = ('+' if p > 0 else '') + n(p, pdec) + '%'
    return f'<td class="{c}">{signed(d, dec)} ({ps})</td>'
def pcell(a, b, pdec=1, cls=True):
    p = pct(a, b)
    c = ('pos' if p > 0 else 'neg' if p < 0 else '') if cls else ''
    return f'<td class="{c}">{("+" if p > 0 else "")}{n(p, pdec)}%</td>'

# ---------------- monthly inputs (Jan..Aug) ----------------
RES_MWH = {25: [120033.44367,114173.50811,119075.24039,111905.22096,117052.9028,124675.67701,129112.37449,134921.23945],
           26: [100985.97078,91753.42062,106170.16024,104319.61843,119683.33754,121921.34197,136903.46407,141478.92331]}
RES_REV = {25: [6956.99152,6538.64679,7043.52715,6312.73405,6960.35998,7395.17762,7350.57572,7500.12767],
           26: [6211.16586,5750.19199,7112.11717,5700.73024,6806.22762,6972.3465,8099.61249,8052.44423]}
COM_MWH = {25: [150760.73318,149163.46518,153360.11275,153936.06128,157016.40663,165248.97886,175723.6575,172083.63843],
           26: [133163.63827,129543.7152,152548.28544,146318.93111,161450.83565,157364.54186,168143.92417,162483.20695]}
COM_REV = {25: [6775.94161,6869.26133,7150.65822,7044.34076,7564.19557,7797.40003,7776.75208,7508.45533],
           26: [6405.84341,6625.77175,8095.44647,6498.95889,7286.16637,7344.95759,7887.84618,7580.83277]}
PP_MWH = {25: [2001.38757+90.02066, 1844.05535+82.95703, 2093.39037+93.86622, 2118.9118+103.23379,
               2253.72746+100.50761, 2317.4096+106.71024, 2577.7494+111.92319, 2570.80604+107.49895],
          26: [2029.64137+86.65674, 1811.42563+75.81462, 2077.56489+84.75542, 2313.39146+95.63142,
               2492.12553+102.0124, 2625.14019+106.66819, 2856.0113+114.36059, 3103.78131+119.52393]}
PP_REV = {25: [108.60548+4.90083, 97.70156+4.52369, 113.48981+5.13168, 111.7032+5.39509,
               130.77634+6.24664, 135.79264+6.62513, 147.08178+6.72423, 142.6148+6.25915],
          26: [122.82835+5.59547, 110.22425+5.05985, 134.60228+6.01944, 133.78983+5.77236,
               139.51749+5.88802, 159.65564+7.13166, 166.5205+6.91065, 177.37335+6.76789]}
def ytd(d, y): return sum(d[y])
def gwh(x): return x / 1000.0

SEG = {}
for y in (25, 26):
    SEG[y] = {
        'post_gwh_aug': gwh(RES_MWH[y][7] - PP_MWH[y][7]), 'pp_gwh_aug': gwh(PP_MWH[y][7]), 'com_gwh_aug': gwh(COM_MWH[y][7]),
        'post_gwh': gwh(ytd(RES_MWH, y) - ytd(PP_MWH, y)), 'pp_gwh': gwh(ytd(PP_MWH, y)), 'com_gwh': gwh(ytd(COM_MWH, y)),
        'post_rev': ytd(RES_REV, y) - ytd(PP_REV, y), 'pp_rev': ytd(PP_REV, y), 'com_rev': ytd(COM_REV, y),
    }
CUST = {25: {'post': 684552, 'pp': 16574, 'com': 26134}, 26: {'post': 694028, 'pp': 18488, 'com': 26066}}
for y in (25, 26):
    CUST[y]['all'] = sum(CUST[y].values())
    s = SEG[y]
    s['all_gwh_aug'] = s['post_gwh_aug'] + s['pp_gwh_aug'] + s['com_gwh_aug']
    s['all_gwh'] = s['post_gwh'] + s['pp_gwh'] + s['com_gwh']
    s['all_rev'] = s['post_rev'] + s['pp_rev'] + s['com_rev']

def seg_table(key, ckey):
    a, b = SEG[25], SEG[26]
    return ('<table>\n<tr><th class="l">Metric</th><th>Aug 2025</th><th>Aug 2026</th><th>Change</th></tr>\n'
            f'<tr><td class="l">Customers</td><td>{n(CUST[25][ckey])}</td><td>{n(CUST[26][ckey])}</td>{chg(CUST[25][ckey], CUST[26][ckey])}</tr>\n'
            f'<tr><td class="l">Sales (GWh, month)</td><td>{n(a[key+"_gwh_aug"],2)}</td><td>{n(b[key+"_gwh_aug"],2)}</td>{chg(a[key+"_gwh_aug"], b[key+"_gwh_aug"], 2)}</tr>\n'
            f'<tr><td class="l">Sales YTD (GWh, Jan&ndash;Aug)</td><td>{n(a[key+"_gwh"],1)}</td><td>{n(b[key+"_gwh"],1)}</td>{chg(a[key+"_gwh"], b[key+"_gwh"], 1)}</tr>\n'
            f'<tr><td class="l">Revenue YTD (J$M)</td><td>{n(a[key+"_rev"])}</td><td>{n(b[key+"_rev"])}</td>{chg(a[key+"_rev"], b[key+"_rev"])}</tr>\n</table>')

# ---------------- Attribution block ----------------
attr = f'''<h2>Attribution Check</h2>
<p>The brief poses a specific claim: customer connections are increasing while electricity sales are declining, which it reads as a decoupling of customer growth from revenue growth and a structural shift in demand. That's a testable statement, so it's worth starting there before touching anything else. Because "customers" and "sales" mean very different things across the customer base, the check below is split four ways &mdash; residential customers billed monthly, prepaid customers, commercial customers, and then the combined system view the brief's claim was actually made about.</p>

<h3>Residential &mdash; billed monthly (homes and small residential-type accounts)</h3>
{seg_table('post', 'post')}
<p>This is where nearly all the customer growth in the system-wide numbers actually comes from, and it's also where the "growth" is least real. Of the 10,308 net new homeowner-tariff accounts this year, 7,399 &mdash; seventy-two cents of every new dollar of "growth" &mdash; are premises that are connected and billing exactly zero. The small-business tariff shows the same thing at a smaller scale, 58% of its growth. The most plausible read, given the timing, is Hurricane Melissa: homes and small businesses that were damaged or vacated in November 2025 and are still on the books but haven't been reactivated. That's an inference from the timing, not something confirmed directly in the billing data, but it's the only explanation that's consistent with everything else this analysis turned up. Volume tells a more encouraging in-month story than the year-to-date figure suggests &mdash; August itself is up about 4.5% year over year, and customers are migrating into <i>higher</i> consumption bands over this period, not lower. The year-to-date shortfall is concentrated in the western parishes that took the storm &mdash; Westmoreland down 30.5% in volume, St. Elizabeth 21.7%, Hanover 13.4%, Trelawny 12.0%, St. James 10.9% &mdash; while the east and centre of the island are flat to slightly up (Section 4). That is a recovery-lag pattern, not a fading trend.</p>

<h3>Prepaid (pay-as-you-go)</h3>
{seg_table('pp', 'pp')}
<p>Prepaid is the only residential segment growing on every measure, and it's growing much faster than the rest of the residential base: customers up 11.5% against 1.4% for monthly-billed residential, volume up 8.2% year to date and 20.3% in August alone, revenue up 15.5%. It is still small &mdash; about 2.5% of customers, 1% of volume and 1% of revenue &mdash; and prepaid customers use somewhat less per head (about 174 kWh in August against roughly 199 for monthly-billed). The pattern is consistent with households moving to prepaid for budget control, though the billing data can't confirm the reason for the switch. Worth tracking, since it is also the segment with the least visibility into what a customer is paying for (see Data Gaps).</p>

<h3>Commercial (registered businesses, individually metered)</h3>
{seg_table('com', 'com')}
<p>The opposite pattern from residential: the connection count is essentially flat (down slightly), and the volume decline is real, not a labeling artifact &mdash; but it traces to two specific, nameable events, not a diffuse trend. Alcoa Minerals' self-generation came fully online in August, and that grid draw isn't coming back. Separately, the hotel sector still hasn't finished recovering from Melissa &mdash; it's improving month over month, just not there yet. Between those two, most of the commercial decline has an address. Outside of them, this segment isn't shrinking on either count or usage. Commercial revenue also held up far better than commercial volume (down 1.3% against 5.2%) because demand charges are billed on peak kVA rather than kWh &mdash; see Section 1b.</p>

<h3>Combined (system-wide, matching the brief's framing)</h3>
<table>
<tr><th class="l">Metric</th><th>Aug 2025</th><th>Aug 2026</th><th>Change</th></tr>
<tr><td class="l">Customers</td><td>{n(CUST[25]['all'])}</td><td>{n(CUST[26]['all'])}</td>{chg(CUST[25]['all'], CUST[26]['all'])}</tr>
<tr><td class="l">Sales (GWh, month)</td><td>{n(SEG[25]['all_gwh_aug'],2)}</td><td>{n(SEG[26]['all_gwh_aug'],2)}</td>{chg(SEG[25]['all_gwh_aug'], SEG[26]['all_gwh_aug'], 2, 1)}</tr>
<tr><td class="l">Sales YTD (GWh, Jan&ndash;Aug)</td><td>{n(SEG[25]['all_gwh'],1)}</td><td>{n(SEG[26]['all_gwh'],1)}</td>{chg(SEG[25]['all_gwh'], SEG[26]['all_gwh'], 1, 1)}</tr>
<tr><td class="l">Revenue YTD (J$M)</td><td>{n(SEG[25]['all_rev'])}</td><td>{n(SEG[26]['all_rev'])}</td>{chg(SEG[25]['all_rev'], SEG[26]['all_rev'])}</tr>
</table>
<p class="note">The three segments above add exactly to these combined figures (Appendix, Table A1). Customer counts run about 23,500 higher in both years than earlier cuts of this same total &mdash; that's the small-business accounts that are individually metered, which weren't being added into the system-wide headcount before. Including them doesn't change the growth rate (still about +1.6%), since that population is close to flat year over year; it just corrects the base.</p>

<div class="key">
<b>Both halves of the brief's claim are literally true &mdash; customers are up, sales are down, every month this year bar two. But "structural shift" is doing more work in that sentence than the data supports, and splitting the segments apart shows why.</b>
<br><br>
Nearly all the customer growth is residential, and most of it isn't really customers &mdash; it's inactive connections still on the books after Melissa. Nearly all the volume decline is commercial, and it isn't diffuse &mdash; it's two accounts &mdash; plus a residential shortfall that sits in the storm-hit western parishes. Prepaid, the one segment growing on every measure, is too small yet to move the total. And the one thing that would actually indicate a structural shift &mdash; existing customers using less &mdash; doesn't show up anywhere: residential volume is up in-month and migrating into higher consumption bands, and commercial volume outside of Alcoa and the hotel sector is holding steady. That's the opposite of what conservation, efficiency gains, or broad self-generation would look like if it were driving this.
</div>

<p><b>Bottom line for how this gets written up:</b> don't frame it as customer growth decoupling from revenue growth. Frame it as sales growth lagging customer growth because of two identifiable, largely temporary or single-account events on the commercial side, sitting on top of a residential customer count that's partly inflated by inactive connections. That's a very different message to leadership than "something structural is happening to demand."</p>

'''

# ---------------- Section 1 + 1b ----------------
RC = {  # J$M, Jan-Aug, net of GCT
    'res': {25: dict(cust=3583.9, energy=14462.0, dem=0.0, fuel=23918.5, ipp=12702.0, rev=55024.6),
            26: dict(cust=3611.8, energy=13774.7, dem=0.0, fuel=25193.1, ipp=10733.4, rev=53511.2)},
    'com': {25: dict(cust=390.3, energy=8876.1, dem=8775.8, fuel=29305.4, ipp=9702.2, rev=58487.0),
            26: dict(cust=411.1, energy=8463.3, dem=8343.3, fuel=31584.6, ipp=8480.5, rev=57725.8)},
}
for k in RC:
    for y in RC[k]:
        r = RC[k][y]
        r['nonfuel'] = r['cust'] + r['energy'] + r['dem']
        r['other'] = r['rev'] - r['nonfuel'] - r['fuel'] - r['ipp']
PPREV = {25: 1033.6, 26: 1193.7}
CB = {y: {k: RC['res'][y][k] + RC['com'][y][k] for k in ('cust', 'energy', 'dem', 'nonfuel', 'fuel', 'ipp', 'other')} for y in (25, 26)}
for y in (25, 26):
    CB[y]['pp'] = PPREV[y]
    CB[y]['rev'] = RC['res'][y]['rev'] + RC['com'][y]['rev'] + PPREV[y]

def comp_rows(get, total_key, with_sub, prepaid=None):
    rows = []
    def row(label, k, sub=False, bold=False):
        a, b = get(25)[k], get(26)[k]
        cls = ' class="sub"' if sub else (' class="tot"' if bold else '')
        rows.append(f'<tr{cls}><td class="l">{label}</td><td>{n(a)}</td><td>{n(b)}</td>{chg(a, b, 0, 1, cls=False)}<td>{n(b / get(26)[total_key] * 100, 1)}%</td></tr>')
    row('Non-fuel charges (customer + energy + demand)', 'nonfuel')
    if with_sub:
        row('Customer charge', 'cust', True)
        row('Energy charge', 'energy', True)
        if get(26)['dem']:
            row('Demand (kVA) charge', 'dem', True)
    row('Fuel', 'fuel')
    row('IPP (purchased power)', 'ipp')
    row('Other (billing adjustments, credits)', 'other')
    if prepaid:
        a, b = prepaid[25], prepaid[26]
        rows.append(f'<tr><td class="l">Prepaid (not split by component in the source)</td><td>{n(a)}</td><td>{n(b)}</td>{chg(a, b, 0, 1, cls=False)}<td>{n(b / get(26)[total_key] * 100, 1)}%</td></tr>')
    a, b = get(25)[total_key], get(26)[total_key]
    rows.append(f'<tr class="tot"><td class="l">Net revenue (before GCT)</td><td>{n(a)}</td><td>{n(b)}</td>{chg(a, b, 0, 2)}<td>100.0%</td></tr>')
    return ('<table>\n<tr><th class="l">J$M, Jan&ndash;Aug</th><th>2025</th><th>2026</th><th>Change</th><th>Share, 2026</th></tr>\n'
            + '\n'.join(rows) + '\n</table>')

sec1 = f'''<h2>1. Top Level</h2>
<p>Overall, sales are down 5.1% year to date and customers are up 1.6%. Revenue held up much better than volume &mdash; down only 1.85% &mdash; because the average rate paid per kWh rose 3.4% across the period and absorbed most of the volume shortfall. It's worth remembering that the 2025 base itself isn't a clean baseline: it was already running below normal from November onward because of the storm, so part of this year's "decline" is really "hasn't caught back up yet" rather than fresh deterioration on top of a healthy prior year.</p>

<h3>1b. Revenue composition &mdash; what is actually moving</h3>
<p>Revenue is billed in layers that behave very differently: the non-fuel charges (customer charge, energy charge and, for commercial customers, the demand charge on peak kVA) are the part JPS keeps to run the network; fuel and IPP purchased power are largely passed through; taxes (GCT) sit on top. Separating them shows that the headline revenue decline is not one thing.</p>
<h3>Combined</h3>
{comp_rows(lambda y: CB[y], 'rev', False, PPREV)}
<p>Three movements explain the net J$2.1 billion decline. IPP is down J$3.2 billion (&minus;14.2%) and non-fuel charges are down J$1.5 billion (&minus;4.1%), against a J$3.6 billion increase in fuel (+6.7%) that cushions them. Fuel and IPP move in opposite directions but together they are up just 0.5% on 5% less volume, so read the pair as one pass-through block; the individual lines swing from month to month. The line to watch is "Other", which fell from J$1.8 billion to J$0.6 billion and on its own accounts for more than half of the net decline &mdash; it is a residual of billing adjustments and credits rather than a charge, and a drop of that size in a single year is worth confirming with Billing before it's treated as either real or permanent.</p>
<h3>Residential &mdash; billed monthly</h3>
{comp_rows(lambda y: RC['res'][y], 'rev', True)}
<h3>Commercial</h3>
{comp_rows(lambda y: RC['com'][y], 'rev', True)}
<p>Commercial non-fuel charges fell 4.6% against a 5.2% fall in volume, and the reason is in the demand line. Demand charges are billed on peak kVA, not on kWh, and a customer's peak doesn't fall in proportion to its total consumption: a plant that runs less often still hits the same peak when it does run. Across the three demand-billed classes (RT40, RT50, RT70) volume is down 6.3% year to date and the energy charge is down 6.3% right alongside it, but the demand charge is down only 4.9% and billed kVA only 5.9%. That gap is why commercial revenue (&minus;1.3%) is so much more resilient than commercial volume (&minus;5.2%).</p>
<table>
<tr><th class="l">Demand-billed classes, Jan&ndash;Aug</th><th>kWh</th><th>Billed kVA</th><th>Energy charge</th><th>Demand charge</th></tr>
<tr><td class="l">RT40 Commercial</td><td class="neg">&minus;6.3%</td><td class="neg">&minus;4.2%</td><td class="neg">&minus;6.3%</td><td class="neg">&minus;3.8%</td></tr>
<tr><td class="l">RT50 Large Commercial</td><td class="neg">&minus;9.6%</td><td class="neg">&minus;6.2%</td><td class="neg">&minus;9.4%</td><td class="neg">&minus;7.5%</td></tr>
<tr><td class="l">RT70 Industrial</td><td class="neg">&minus;2.2%</td><td class="neg">&minus;9.1%</td><td class="neg">&minus;2.2%</td><td class="neg">&minus;5.6%</td></tr>
<tr class="tot"><td class="l">All three</td><td class="neg">&minus;6.3%</td><td class="neg">&minus;5.9%</td><td class="neg">&minus;6.3%</td><td class="neg">&minus;4.9%</td></tr>
</table>
<p>The clearest single example is RT70 in August, where volume fell 28.4% (Alcoa's exit) yet billed kVA rose 61% and the demand charge rose 11.7%. That is what you would expect from a customer that now generates most of its own power but still holds grid capacity for backup, though the billing data alone can't confirm that is what is happening.</p>
<h3>Taxes (GCT)</h3>
<table>
<tr><th class="l">GCT billed, Jan&ndash;Apr (J$M)</th><th>2025</th><th>2026</th><th>Change</th><th>Effective rate 2026</th></tr>
<tr><td class="l">Residential &mdash; billed monthly</td><td>770</td><td>611</td>{chg(770.4, 611.2, 0, 1)}<td>2.5%</td></tr>
<tr><td class="l">Prepaid</td><td>33</td><td>39</td>{chg(33.2, 38.5, 0, 1)}<td>7.3%</td></tr>
<tr><td class="l">Commercial</td><td>3,683</td><td>3,681</td>{chg(3682.7, 3680.8, 0, 1)}<td>13.3%</td></tr>
<tr class="tot"><td class="l">Total</td><td>4,486</td><td>4,331</td>{chg(4486.3, 4330.5, 0, 1)}<td>8.3%</td></tr>
</table>
<p class="note">Tax is shown for January to April only. The tax amounts for the larger commercial classes (RT40, RT50, RT60-ST, RT70) have not been loaded for May, July and August 2026, so a full year-to-date tax comparison isn't possible yet (Data Gaps). Residential tax is falling faster than residential revenue (&minus;20.7% against &minus;8.1% over the same four months); that fits tax applying mostly to higher-consumption bills, but it hasn't been checked against the tariff schedule.</p>

'''

# ---------------- Section 3 ----------------
NB = EX['nb']
def nbc(mo, code): return round(NB[mo][code]['count'])
sec3 = f'''<h2>3. Within Rate Class &mdash; Consumption Blocks</h2>
<p>This is where the attribution check's real answer lives, so it's worth walking through carefully. RT10 and RT20 are the only two classes with banded consumption data, and both tell the same story: the Under-150 and 150&ndash;350 kWh bands are shrinking while every band above 350 kWh is growing. Concretely, for RT10 the two lowest bands lost 6,762 customers combined while the four bands from 350 kWh up gained 7,570 &mdash; more customers moved up than moved out of the low end, which means the migration is being topped up by some new connections landing directly in the middle bands too, not just by existing low-usage customers climbing. Either way, the direction is up, not down. The full band tables for every rate class are in the Appendix (Tables A2&ndash;A4).</p>

<table>
<tr><th class="l">&nbsp;</th><th>RT10</th><th>RT20 (residential)</th></tr>
<tr><td class="l">Zero-consumption customers, Aug-25 &rarr; Aug-26</td><td>50,569 &rarr; 57,968 (+7,399, +14.6%)</td><td>5,712 &rarr; 6,340 (+628, +11.0%)</td></tr>
<tr><td class="l">Share of that class's total customer growth</td><td class="neg">72%</td><td class="neg">58%</td></tr>
<tr><td class="l">Registered net-billing customers, Aug-25 &rarr; Aug-26</td><td>{nbc('2025-08','NB10')} &rarr; {nbc('2026-08','NB10')} (+{nbc('2026-08','NB10')-nbc('2025-08','NB10')}, +{pct(nbc('2025-08','NB10'), nbc('2026-08','NB10'), 1):.1f}%)</td><td>{nbc('2025-08','NB20')} &rarr; {nbc('2026-08','NB20')} (+{nbc('2026-08','NB20')-nbc('2025-08','NB20')}, +{pct(nbc('2025-08','NB20'), nbc('2026-08','NB20'), 1):.1f}%)</td></tr>
<tr><td class="l">Customers exporting more than they draw in the month, Aug-25 &rarr; Aug-26</td><td>768 &rarr; 966 (+198, +25.8%)</td><td>67 &rarr; 106 (+39, +58.2%)</td></tr>
</table>
<p>So the falling per-customer average isn't existing customers pulling back &mdash; it's the blended average getting diluted by a large number of connections that aren't consuming anything at all. That's a meaningfully different problem to solve than "customers are conserving," and it points toward a data-cleanup and reconnection question (are these premises actually vacant, or just stuck in a billing/meter-read backlog?) rather than a demand-forecasting one.</p>
<p>Solar shows up in two different ways in the data, and they tell different stories. Customers registered on the net-billing tariff are few and barely growing &mdash; about 510 on the residential tariff and 313 on the small-business tariff, up roughly 4&ndash;5% in a year, with another 65 large commercial accounts that haven't moved. But the number of customers who actually exported more than they drew in August is close to double the registered residential count (966 against 511) and grew five times as fast (+26%). At least 450 residential exporters are therefore not on the registered scheme, or not yet; that's the activity the brief asks about that sits outside registered net billing. Either way it's still small in absolute terms &mdash; about 1,100 customers &mdash; but the direction is clear and the registered count understates it. One caution: a single month of net export can also come from a meter correction or a billing estimate reversal, so the export count is an upper bound on solar, not a precise measure.</p>

'''

# ---------------- Section 4 (parish) ----------------
PAR = [  # parish, cust25, cust26, gwh25, gwh26, rev%
    ('Westmoreland', 32705, 33153, 35.9, 25.0, -28.8), ('St. Elizabeth', 43117, 43806, 41.1, 32.2, -19.9),
    ('Hanover', 15777, 15927, 18.7, 16.2, -10.8), ('Trelawny', 19500, 19873, 21.5, 18.9, -9.2),
    ('St. James', 57954, 58520, 76.4, 68.0, -8.6), ('St. Ann', 46840, 47810, 53.2, 50.6, -2.1),
    ('Manchester', 44798, 45428, 42.9, 42.0, 0.8), ('St. Mary', 31143, 31532, 32.8, 32.7, 2.7),
    ('Portmore', 50761, 51595, 70.7, 70.5, 2.6), ('Clarendon', 47512, 48218, 45.7, 45.7, 3.0),
    ('St. Catherine', 78955, 80215, 91.2, 91.9, 3.6), ('KSAN', 79216, 80016, 149.2, 150.9, 3.8),
    ('KSAS', 44413, 44649, 61.6, 62.5, 4.5), ('Portland', 22545, 22843, 22.1, 22.4, 4.6),
    ('St. Thomas', 20086, 20142, 18.6, 19.1, 6.0),
]
prow = []
for name, c25, c26, g25, g26, rv in PAR:
    prow.append(f'<tr><td class="l">{name}</td><td>{n(c26)}</td>{pcell(c25, c26, 1)}<td>{n(g26,1)}</td>{pcell(g25, g26, 1)}<td class="{"pos" if rv > 0 else "neg"}">{("+" if rv > 0 else "")}{n(rv,1)}%</td></tr>')
sec4 = f'''<h2>4. By Parish</h2>
<p>Earlier drafts flagged that only about one in ten customers carried a parish, and that the residential base had none. That turned out to be a limitation of how the residential data is stored, not of the billing itself: every residential account carries a parish in the source billing records, and it was being combined into a single island-wide total on the way into the sales platform. This section now uses the source records directly, so residential is included. What is still not available is the consumption-band view by parish (Section 3 and Appendix A2 are island-wide), which needs the band feed rebuilt at parish level.</p>
<h3>Residential (billed monthly), by parish &mdash; sorted from steepest volume decline</h3>
<table>
<tr><th class="l">Parish</th><th>Customers, Aug-26</th><th>Customers &Delta;</th><th>GWh, Jan&ndash;Aug 26</th><th>GWh &Delta;</th><th>Revenue &Delta;</th></tr>
{chr(10).join(prow)}
<tr class="tot"><td class="l">Total</td><td>643,727</td>{pcell(635322, 643727, 1)}<td>748.7</td>{pcell(781.641, 748.726, 1)}<td class="neg">&minus;1.5%</td></tr>
</table>
<p>Customer growth is even across the island, between 0.3% and 2.1% everywhere, but volume is not. The five steepest declines &mdash; Westmoreland, St. Elizabeth, Hanover, Trelawny and St. James &mdash; are the western parishes hit hardest by Hurricane Melissa, and they account for the whole of the residential volume shortfall; the east and centre are flat to slightly up. It's the same geography as the hotel story in Section 5, showing up on the residential side: connections are back or holding, consumption in the storm-hit areas isn't yet.</p>
<p>Commercial accounts (RT20 commercial, RT40, RT50, RT60-ST, RT70) carry a parish on essentially every record and show the same western pattern &mdash; St. James down 23.6% in GWh, St. Elizabeth down 20.5%, Westmoreland down 17.3%.</p>

'''

# ---------------- Section 5 (industry) ----------------
IND = [  # name, gwh25, gwh26, rev25, rev26
    ('Water Supply and Irrigation Systems', 155.1, 139.4, 6885, 6565),
    ('Hotels (except Casino Hotels) and Motels', 173.3, 128.3, 7126, 5692),
    ('Other Metal Ore Mining', 75.4, 77.7, 3151, 3363),
    ('Cement Manufacturing', 60.3, 73.4, 1614, 1956),
    ('Wired and Wireless Telecommunications Carriers', 57.3, 54.0, 2797, 2720),
    ('Executive Offices', 42.6, 41.2, 2202, 2185),
    ('Full-Service Restaurants', 37.7, 37.2, 1737, 1782),
    ('Banking, Insurance and Investments', 35.1, 33.7, 1732, 1723),
    ('Food Manufacturing', 29.3, 29.9, 1295, 1374),
    ('Supermarkets and Other Grocery Retailers', 29.2, 29.7, 1326, 1408),
]
T25, T26, TR25, TR26 = 1250.3, 1186.9, 56796, 56201
NT = (143.5, 149.2, 7864, 8330)
top = [sum(r[i] for r in IND) for i in (1, 2, 3, 4)]
OTH = (T25 - NT[0] - top[0], T26 - NT[1] - top[1], TR25 - NT[2] - top[2], TR26 - NT[3] - top[3])
irows = []
for i, (nm, a, b, ra, rb) in enumerate(IND, 1):
    irows.append(f'<tr><td class="l">{i}. {nm}</td><td>{n(a,1)}</td><td>{n(b,1)}</td>{pcell(a, b, 1)}<td>{n(b / T26 * 100, 1)}%</td>{pcell(ra, rb, 1)}</tr>')
irows.append(f'<tr><td class="l">All other tagged industries</td><td>{n(OTH[0],1)}</td><td>{n(OTH[1],1)}</td>{pcell(OTH[0], OTH[1], 1)}<td>{n(OTH[1] / T26 * 100, 1)}%</td>{pcell(OTH[2], OTH[3], 1)}</tr>')
irows.append(f'<tr><td class="l"><i>No industry tag</i></td><td>{n(NT[0],1)}</td><td>{n(NT[1],1)}</td>{pcell(NT[0], NT[1], 1, cls=False)}<td>{n(NT[1] / T26 * 100, 1)}%</td>{pcell(NT[2], NT[3], 1, cls=False)}</tr>')
irows.append(f'<tr class="tot"><td class="l">Total commercial</td><td>{n(T25,1)}</td><td>{n(T26,1)}</td>{pcell(T25, T26, 1)}<td>100.0%</td>{pcell(TR25, TR26, 1)}</tr>')

def share(a, b): return (a / T25 * 100, b / T26 * 100)
h = share(173.3, 128.3); c = share(60.3, 73.4); m = share(75.4, 77.7); w = share(155.1, 139.4); nt = share(NT[0], NT[1])
sec5 = f'''<h2>5. By Sector / Industry</h2>
<p>This covers the commercial classes (small-business commercial RT20, RT40, RT50 and RT70). RT10 residential and RT60-ST street lighting carry no industry tags, so they are excluded here by definition, not by choice. Figures are January to August.</p>
<h3>Top 10 industries by 2026 volume</h3>
<table>
<tr><th class="l">Industry</th><th>GWh 2025</th><th>GWh 2026</th><th>GWh &Delta;</th><th>Share of commercial GWh, 2026</th><th>Revenue &Delta;</th></tr>
{chr(10).join(irows)}
</table>
<p>The top ten tagged industries make up 54% of commercial volume, another 33% is spread across the remaining tagged industries, and about 13% has no industry tag at all. An earlier version of this section put the untagged share at 22%; that figure was too high because it counted residential small-business accounts, which can't carry an industry tag, in the "no tag" bucket. On the commercial accounts that should carry one, the gap is 12.6% of volume in 2026 (11.5% in 2025). It is also not evenly spread: it sits almost entirely in small-business commercial accounts, where 56% of volume (145 of 260 GWh) is untagged, against under 1% for RT40, RT50 and RT70. By premise count that is roughly 17,900 accounts. A targeted tagging cleanup on the small-business file would close nearly all of it.</p>
<h3>Biggest movers</h3>
<table>
<tr><th class="l">Industry</th><th>GWh &Delta;</th><th>Revenue &Delta;</th></tr>
<tr><td class="l">Hotels (except Casino Hotels) and Motels</td><td class="neg">&minus;26.0% (173.3&rarr;128.3)</td><td class="neg">&minus;20.1%</td></tr>
<tr><td class="l">Water Supply and Irrigation Systems</td><td class="neg">&minus;10.1%</td><td class="neg">&minus;4.6%</td></tr>
<tr><td class="l">Poultry Hatcheries</td><td class="neg">&minus;23.3%</td><td class="neg">&minus;19.8%</td></tr>
<tr><td class="l">Telemarketing / Contact Centers</td><td class="neg">&minus;22.7%</td><td class="neg">&minus;18.5%</td></tr>
<tr><td class="l">Cement Manufacturing</td><td class="pos">+21.8%</td><td class="pos">+21.2%</td></tr>
<tr><td class="l">Distilleries</td><td class="pos">+17.5%</td><td class="pos">+18.2%</td></tr>
<tr><td class="l">Other Metal Ore Mining</td><td class="pos">+3.0%</td><td class="pos">+6.7%</td></tr>
</table>
<p>Hotels is, by a wide margin, the single largest identifiable industry drag on the system &mdash; more GWh lost than the next three declining industries combined. Everything else tagged in the crosswalk mostly moves within a few percent either direction, so this reads as concentrated in one sector rather than a broad commercial slowdown.</p>

<h3>5a. Composition &mdash; is a rising share growth, or everyone else declining?</h3>
<p>The brief specifically asks whether a higher revenue or volume share for an industry reflects real growth or just other industries falling faster around it. Worth separating those two cases, because they read very differently to a board.</p>
<table>
<tr><th class="l">Industry</th><th>Share of commercial GWh, 2025</th><th>Share, 2026</th><th class="l">Read</th></tr>
<tr><td class="l">Hotels</td><td>{h[0]:.2f}%</td><td>{h[1]:.2f}%</td><td class="l">Share <span class="neg">falling</span> &mdash; genuine decline, not dilution</td></tr>
<tr><td class="l">Cement Manufacturing</td><td>{c[0]:.2f}%</td><td>{c[1]:.2f}%</td><td class="l">Share <span class="pos">rising</span>, volume also up 21.8% &mdash; real growth</td></tr>
<tr><td class="l">Other Metal Ore Mining</td><td>{m[0]:.2f}%</td><td>{m[1]:.2f}%</td><td class="l">Share <span class="pos">rising</span> despite Alcoa's August exit &mdash; other accounts in the group (Windalco, Jamalco, Alpart) are carrying it, and Alcoa's drop has only been in the data one month so far</td></tr>
<tr><td class="l">Water Supply and Irrigation</td><td>{w[0]:.2f}%</td><td>{w[1]:.2f}%</td><td class="l">Share and volume both down modestly &mdash; broad, not company-specific</td></tr>
<tr><td class="l">(no industry tag)</td><td>{nt[0]:.2f}%</td><td>{nt[1]:.2f}%</td><td class="l">Share rising slightly, because the untagged small-business accounts fell less than the tagged ones &mdash; a tagging gap more than a finding</td></tr>
</table>
<p>Cement Manufacturing is the one genuinely clean growth story here: both the dollars and the share are moving up together, which is what real growth looks like rather than growth-by-comparison. Hotels is the mirror image &mdash; an outright decline, not just a shrinking share because other things grew around it. And about one kWh in eight still has no industry attached, concentrated in small-business accounts, which caps how far the sector cut can be trusted until that is cleaned up.</p>

'''
json.dump({'attr': attr, 'sec1': sec1, 'sec3': sec3, 'sec4': sec4, 'sec5': sec5}, open(r'C:\Projects\Sales_Platform\analysis\_report_blocks_a.json', 'w'))
print('blocks A ok')
