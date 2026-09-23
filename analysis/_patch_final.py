# -*- coding: utf-8 -*-
# Final-report pass: remove Data Gaps, complete GCT, per-kWh composition, EV answer,
# defection section, and strip every reference to earlier versions / data plumbing.
import re, json
exec(open(r'C:\Projects\Sales_Platform\analysis\_build_report_v2.py', encoding='utf-8').read().split('# ---------------- Attribution block')[0])
html = open(HTML, encoding='utf-8').read()

def cut(start, end, new):
    global html
    i = html.index(start); j = html.index(end, i)
    html = html[:i] + new + html[j:]
def rep(a, b, count=1):
    global html
    assert a in html, a[:70]
    html = html.replace(a, b) if count == 0 else html.replace(a, b, count)

# ---------------- 1b: composition incl. taxes, per-kWh ----------------
RC = {'res': {25: dict(cust=3583.9, energy=14462.0, dem=0.0, fuel=23918.5, ipp=12702.0, rev=55024.6),
              26: dict(cust=3611.8, energy=13774.7, dem=0.0, fuel=25193.1, ipp=10733.4, rev=53511.2)},
      'com': {25: dict(cust=390.3, energy=8876.1, dem=8775.8, fuel=29305.4, ipp=9702.2, rev=58487.0),
              26: dict(cust=411.1, energy=8463.3, dem=8343.3, fuel=31584.6, ipp=8480.5, rev=57725.8)}}
GCT = {'res': {25: 1461.3, 26: 1345.5}, 'pp': {25: 76.0, 26: 75.4}, 'com': {25: 6113.8 + 1933.4, 26: 5980.2 + 1966.0}}
PPREV = {25: 1033.6, 26: 1193.7}
for k in RC:
    for y in RC[k]:
        r = RC[k][y]; r['nonfuel'] = r['cust'] + r['energy'] + r['dem']; r['other'] = r['rev'] - r['nonfuel'] - r['fuel'] - r['ipp']
CB = {y: {k: RC['res'][y][k] + RC['com'][y][k] for k in ('cust', 'energy', 'dem', 'nonfuel', 'fuel', 'ipp', 'other')} for y in (25, 26)}
for y in (25, 26):
    CB[y]['rev'] = RC['res'][y]['rev'] + RC['com'][y]['rev'] + PPREV[y]
    CB[y]['gct'] = GCT['res'][y] + GCT['pp'][y] + GCT['com'][y]
    RC['res'][y]['gct'] = GCT['res'][y]; RC['com'][y]['gct'] = GCT['com'][y]

def comp_rows(get, with_sub, prepaid=None):
    rows = []
    def row(label, k, sub=False):
        a, b = get(25)[k], get(26)[k]
        cls = ' class="sub"' if sub else ''
        rows.append(f'<tr{cls}><td class="l">{label}</td><td>{n(a)}</td><td>{n(b)}</td>{chg(a, b, 0, 1, cls=False)}<td>{n(b / get(26)["rev"] * 100, 1)}%</td></tr>')
    row('Non-fuel charges (customer + energy + demand)', 'nonfuel')
    if with_sub:
        row('Customer charge', 'cust', True); row('Energy charge', 'energy', True)
        if get(26)['dem']: row('Demand (kVA) charge', 'dem', True)
    row('Fuel', 'fuel'); row('IPP (purchased power)', 'ipp'); row('Other (billing adjustments, credits)', 'other')
    if prepaid:
        a, b = prepaid[25], prepaid[26]
        rows.append(f'<tr><td class="l">Prepaid (single line)</td><td>{n(a)}</td><td>{n(b)}</td>{chg(a, b, 0, 1, cls=False)}<td>{n(b / get(26)["rev"] * 100, 1)}%</td></tr>')
    a, b = get(25)['rev'], get(26)['rev']
    rows.append(f'<tr class="tot"><td class="l">Net revenue (before GCT)</td><td>{n(a)}</td><td>{n(b)}</td>{chg(a, b, 0, 2)}<td>100.0%</td></tr>')
    ga, gb = get(25)['gct'], get(26)['gct']
    rows.append(f'<tr><td class="l">Taxes (GCT)</td><td>{n(ga)}</td><td>{n(gb)}</td>{chg(ga, gb, 0, 1, cls=False)}<td>&nbsp;</td></tr>')
    rows.append(f'<tr class="tot"><td class="l">Total billed, including GCT</td><td>{n(a + ga)}</td><td>{n(b + gb)}</td>{chg(a + ga, b + gb, 0, 2)}<td>&nbsp;</td></tr>')
    return ('<table>\n<tr><th class="l">J$M, Jan&ndash;Aug</th><th>2025</th><th>2026</th><th>Change</th><th>Share of net revenue, 2026</th></tr>\n' + '\n'.join(rows) + '\n</table>')

# per-kWh
G = {'res': (SEG[25]['post_gwh'], SEG[26]['post_gwh']), 'com': (SEG[25]['com_gwh'], SEG[26]['com_gwh']), 'all': (SEG[25]['all_gwh'], SEG[26]['all_gwh'])}
def pk(seg, key):
    src = {'res': RC['res'], 'com': RC['com']}
    if seg in src: return [src[seg][y][key] / G[seg][i] for i, y in enumerate((25, 26))]
    return [CB[y][key] / G['all'][i] for i, y in enumerate((25, 26))]
def pkrow(label, key, bold=False, prepaid=False):
    vals = []
    for seg in ('res', 'com', 'all'):
        if prepaid:
            v = [None, None] if seg != 'all' else [PPREV[y] / G['all'][i] for i, y in enumerate((25, 26))]
        elif key == 'net':
            v = [RC[seg][y]['rev'] / G[seg][i] for i, y in enumerate((25, 26))] if seg != 'all' else [CB[y]['rev'] / G['all'][i] for i, y in enumerate((25, 26))]
        elif key == 'gct':
            v = ([GCT['res'][y] / G['res'][i] for i, y in enumerate((25, 26))] if seg == 'res' else [GCT['com'][y] / G['com'][i] for i, y in enumerate((25, 26))] if seg == 'com' else [CB[y]['gct'] / G['all'][i] for i, y in enumerate((25, 26))])
        elif key == 'bill':
            v = ([(RC['res'][y]['rev'] + GCT['res'][y]) / G['res'][i] for i, y in enumerate((25, 26))] if seg == 'res' else [(RC['com'][y]['rev'] + GCT['com'][y]) / G['com'][i] for i, y in enumerate((25, 26))] if seg == 'com' else [(CB[y]['rev'] + CB[y]['gct']) / G['all'][i] for i, y in enumerate((25, 26))])
        else:
            v = pk(seg, key)
        vals.append(v)
    cells = ''.join(('<td>&ndash;</td><td>&ndash;</td>' if v[0] is None else f'<td>{v[0]:.2f}</td><td>{v[1]:.2f}</td>') for v in vals)
    a, b = vals[2]
    d = pcell(a, b, 1, cls=False)
    tr = '<tr class="tot">' if bold else '<tr>'
    return tr + f'<td class="l">{label}</td>{cells}{d}</tr>'
prows = [pkrow('Non-fuel charges', 'nonfuel'), pkrow('Fuel', 'fuel'), pkrow('IPP (purchased power)', 'ipp'), pkrow('Other', 'other'),
         pkrow('Prepaid (single line)', None, prepaid=True), pkrow('Net revenue per kWh', 'net', True), pkrow('Taxes (GCT)', 'gct'), pkrow('Billed per kWh, including GCT', 'bill', True)]
perkwh = ('<h3>Average revenue per kWh</h3>\n<p>The same layers expressed per kWh sold, which strips out the volume decline and shows what each unit of sales is actually earning. Residential and commercial use their own volumes; the combined column spreads everything, including prepaid revenue, over total system volume.</p>\n'
          '<table>\n<tr><th class="l">J$ per kWh, Jan&ndash;Aug</th><th>Resid. 2025</th><th>Resid. 2026</th><th>Comm. 2025</th><th>Comm. 2026</th><th>Comb. 2025</th><th>Comb. 2026</th><th>Comb. &Delta;</th></tr>\n'
          + '\n'.join(prows) + '\n</table>')
nk = {s: (pk(s, 'nonfuel'), pk(s, 'fuel'), pk(s, 'ipp')) for s in ('res', 'com', 'all')}
comb_net = [CB[y]['rev'] / G['all'][i] for i, y in enumerate((25, 26))]
perkwh_text = (f'<p>The average net rate rose from J${comb_net[0]:.2f} to J${comb_net[1]:.2f} per kWh (+{pct(comb_net[0], comb_net[1], 1):.1f}%), and almost all of that is fuel: '
               f'the fuel layer went from J${nk["all"][1][0]:.2f} to J${nk["all"][1][1]:.2f} per kWh while IPP fell from J${nk["all"][2][0]:.2f} to J${nk["all"][2][1]:.2f}. '
               f'The non-fuel layer, the part that pays for the network, rose from J${nk["all"][0][0]:.2f} to J${nk["all"][0][1]:.2f} per kWh &mdash; fixed charges spread over fewer units of sales. Commercial customers pay far more per kWh than residential in every layer, mostly because demand charges sit on top.</p>')

tax_tbl = ('<h3>Taxes (GCT)</h3>\n<table>\n<tr><th class="l">GCT billed, Jan&ndash;Aug (J$M)</th><th>2025</th><th>2026</th><th>Change</th><th>Effective rate 2026</th></tr>\n'
           + '\n'.join(
               f'<tr><td class="l">{lab}</td><td>{n(a)}</td><td>{n(b)}</td>{chg(a, b, 0, 1, cls=False)}<td>{rate:.1f}%</td></tr>'
               for lab, a, b, rate in (('Residential &mdash; billed monthly', GCT['res'][25], GCT['res'][26], GCT['res'][26] / RC['res'][26]['rev'] * 100),
                                       ('Prepaid', GCT['pp'][25], GCT['pp'][26], GCT['pp'][26] / PPREV[26] * 100),
                                       ('Commercial', GCT['com'][25], GCT['com'][26], GCT['com'][26] / RC['com'][26]['rev'] * 100)))
           + f'\n<tr class="tot"><td class="l">Total</td><td>{n(CB[25]["gct"])}</td><td>{n(CB[26]["gct"])}</td>{chg(CB[25]["gct"], CB[26]["gct"], 0, 1, cls=False)}<td>{CB[26]["gct"] / CB[26]["rev"] * 100:.1f}%</td></tr>\n</table>\n'
           f'<p class="note">Total tax billed fell {abs(pct(CB[25]["gct"], CB[26]["gct"], 1)):.1f}%, a little more than net revenue ({abs(pct(CB[25]["rev"], CB[26]["rev"], 1)):.1f}%). Commercial tax tracks commercial revenue almost one for one at about 13.8%; the difference comes from residential, where tax fell {abs(pct(GCT["res"][25], GCT["res"][26], 1)):.1f}% against a {abs(pct(RC["res"][25]["rev"], RC["res"][26]["rev"], 1)):.1f}% fall in revenue. That fits residential tax applying mostly to higher-consumption bills, which have fallen furthest in the storm-hit parishes.</p>\n')

old_1b = html[html.index('<h3>1b. Revenue composition'):html.index('<h2>2. Across Rate Class</h2>')]
i_kva = old_1b.index('<p>Commercial non-fuel charges fell 4.6%'); i_kva_end = old_1b.index('<h3>Taxes (GCT)</h3>')
kva_block = old_1b[i_kva:i_kva_end]
new_1b = ('<h3>1b. Revenue composition &mdash; what is actually moving</h3>\n'
          '<p>Revenue is billed in layers that behave very differently: the non-fuel charges (customer charge, energy charge and, for commercial customers, the demand charge on peak kVA) are the part JPS keeps to run the network; fuel and IPP purchased power are largely passed through; taxes (GCT) are billed on top and shown below net revenue.</p>\n'
          '<h3>Combined</h3>\n' + comp_rows(lambda y: CB[y], False, PPREV) + '\n'
          '<p>Three movements explain the net J$2.1 billion decline in net revenue. IPP is down J$3.2 billion (&minus;14.2%) and non-fuel charges are down J$1.5 billion (&minus;4.1%), against a J$3.6 billion increase in fuel (+6.7%) that cushions them. Fuel and IPP move in opposite directions but together they are up just 0.5% on 5% less volume, so read the pair as one pass-through block; the individual lines swing from month to month. The line to watch is "Other", which fell from J$1.8 billion to J$0.6 billion and on its own accounts for more than half of the net decline &mdash; it is a residual of billing adjustments and credits rather than a charge, and a drop of that size in a single year is worth confirming with Billing before it\'s treated as either real or permanent.</p>\n'
          '<h3>Residential &mdash; billed monthly</h3>\n' + comp_rows(lambda y: RC['res'][y], True) + '\n'
          '<h3>Commercial</h3>\n' + comp_rows(lambda y: RC['com'][y], True) + '\n'
          + kva_block + perkwh + '\n' + perkwh_text + '\n' + tax_tbl + '\n')
html = html.replace(old_1b, new_1b)

# ---------------- final-report wording: no history, no plumbing ----------------
rep('Everything below comes from live billing data and the account&ndash;industry mapping, and every number that could be cross-checked against a second, independent cut was.',
    'Everything below is drawn from billed sales and revenue, and every number that could be cross-checked against a second, independent cut was.')
rep(' Worth tracking, since it is also the segment with the least visibility into what a customer is paying for (see Data Gaps).', ' Worth tracking as it scales.')
cut('<p class="note">The three segments above add exactly', '<div class="key">',
    '<p class="note">The three segments above add exactly to these combined figures (Appendix, Table A1). Customer counts include the individually metered small-business accounts, which are close to flat year over year.</p>\n\n')
cut('<h2>4. By Parish</h2>', '<h3>Residential (billed monthly), by parish',
    '<h2>4. By Parish</h2>\n<p>Every residential account carries a parish, so the residential base is shown here alongside commercial. Consumption bands (Section 3 and Appendix A2) are island-wide.</p>\n')
rep('Commercial accounts (RT20 commercial, RT40, RT50, RT60-ST, RT70) carry a parish on essentially every record and show the same western pattern', 'Commercial accounts (RT20 commercial, RT40, RT50, RT60-ST, RT70) show the same western pattern')
rep('Everything else tagged in the crosswalk mostly moves', 'Everything else with an industry assigned mostly moves')
rep('A targeted classification cleanup on the small-business file would close nearly all of it.', 'Assigning industries to the small-business accounts would close nearly all of it.')
rep('a tagging gap more than a finding', 'an assignment gap more than a finding')
rep('Source: billing actuals and account&ndash;industry mapping, Sales Analytics Platform.', 'Source: JPS billed sales and revenue records.')
rep('The full band tables for every rate class are in the Appendix (Tables A2&ndash;A4).', 'The band tables for every rate class are in the Appendix (Tables A2&ndash;A8).')
rep(' Registered figures come from the billing extract; the sales platform does not currently flag the net-billing tariff.', '')
rep(' Thirteen zero-consumption accounts (eleven a year ago) are not mapped to any rate class and are left out of the class tables; the volume involved is nil.', '')
rep('Customers</b> are billed accounts in the month: residential counts come as totals by band, commercial counts are one per metered account.', 'Customers</b> are billed accounts in the month, one per metered account for commercial.')

# A1 simplified
cut('<h3>A1. Reconciliation', '<h3>A2.', '<h3>A1. Segment build-up of the combined figures</h3>\n' + tbl_a1 if False else '<h3>A1. Segment build-up of the combined figures</h3>\n')
a1 = ('<table>\n<tr><th class="l">Customers</th><th>Aug 2025</th><th>Aug 2026</th></tr>\n'
      f'<tr><td class="l">Residential &mdash; billed monthly</td><td>{n(CUST[25]["post"])}</td><td>{n(CUST[26]["post"])}</td></tr>\n'
      f'<tr><td class="l">Prepaid</td><td>{n(CUST[25]["pp"])}</td><td>{n(CUST[26]["pp"])}</td></tr>\n'
      f'<tr><td class="l">Commercial</td><td>{n(CUST[25]["com"])}</td><td>{n(CUST[26]["com"])}</td></tr>\n'
      f'<tr class="tot"><td class="l">Combined</td><td>{n(CUST[25]["all"])}</td><td>{n(CUST[26]["all"])}</td></tr>\n</table>\n'
      '<table>\n<tr><th class="l">Sales and revenue, Jan&ndash;Aug</th><th>Residential</th><th>Prepaid</th><th>Commercial</th><th>Combined</th></tr>\n'
      f'<tr><td class="l">Sales 2025 (GWh)</td><td>{n(SEG[25]["post_gwh"],1)}</td><td>{n(SEG[25]["pp_gwh"],1)}</td><td>{n(SEG[25]["com_gwh"],1)}</td><td>{n(SEG[25]["all_gwh"],1)}</td></tr>\n'
      f'<tr><td class="l">Sales 2026 (GWh)</td><td>{n(SEG[26]["post_gwh"],1)}</td><td>{n(SEG[26]["pp_gwh"],1)}</td><td>{n(SEG[26]["com_gwh"],1)}</td><td>{n(SEG[26]["all_gwh"],1)}</td></tr>\n'
      f'<tr><td class="l">Net revenue 2025 (J$M)</td><td>{n(SEG[25]["post_rev"])}</td><td>{n(SEG[25]["pp_rev"])}</td><td>{n(SEG[25]["com_rev"])}</td><td>{n(SEG[25]["all_rev"])}</td></tr>\n'
      f'<tr><td class="l">Net revenue 2026 (J$M)</td><td>{n(SEG[26]["post_rev"])}</td><td>{n(SEG[26]["pp_rev"])}</td><td>{n(SEG[26]["com_rev"])}</td><td>{n(SEG[26]["all_rev"])}</td></tr>\n</table>\n\n')
i = html.index('<h3>A1. Segment build-up of the combined figures</h3>\n') + len('<h3>A1. Segment build-up of the combined figures</h3>\n')
html = html[:i] + a1 + html[i:]

# ---------------- Section 6: defection ----------------
NAMED = [('HOCATSA Jamaica Limited', 'Hotels', 3.54, 0.65, -82, 'Storm damage; hotel now recovering month by month'),
         ('Carib Products Co Ltd', 'Fats and oils refining', 0.89, 0.13, -86, 'Volume and contracted demand both cut from February 2026; operational'),
         ('United Call Solutions (Jamaica)', 'Contact centers', 0.80, 0.00, -100, 'Storm window; demand cut to the minimum, site closed'),
         ('Coyaba Beach Resort & Club', 'Hotels', 0.61, 0.09, -86, 'Storm damage; not yet recovered'),
         ('BBNH Resorts Limited', 'Hotels', 0.51, 0.00, -100, 'Storm window; no longer billing'),
         ('Contax360 BPO Solutions', 'Contact centers', 0.46, 0.00, -100, 'Storm window; demand cut to the minimum, site closed'),
         ('M & W Investments Ltd', 'Banking, insurance and investments', 0.36, 0.03, -91, 'Account closed; no billing since February 2026'),
         ('Shoppers Fair', 'Supermarkets and grocery', 0.30, 0.00, -98, 'Storm window; demand cut to the minimum'),
         ('Unique Vacations Ltd', 'Contact centers', 0.28, 0.03, -88, 'Storm window; no billing since April 2026'),
         ('Strobe Communications Ltd', 'Contact centers', 0.24, 0.01, -95, 'Storm window; demand cut to the minimum'),
         ('Eight Rivers Energy Company', 'Hydroelectric power generation', 0.23, 0.00, -99, 'Storm window; a generator, so confirm whether it now supplies itself'),
         ('24-7 Intouch JAM2 Inc', 'Industry not yet assigned', 0.23, 0.02, -90, 'Storm window; account closed'),
         ('Dougall Flooring Ltd.', 'Flooring contractors', 0.20, 0.02, -92, 'Volume and contracted demand run down gradually; operational'),
         ('White Diamond Hotels & Resorts', 'Hotels', 0.20, 0.00, -100, 'Storm window; no longer billing'),
         ('AMGL Account Outsourcing Group', 'Industry not yet assigned', 0.11, 0.01, -93, 'Storm window; account closed'),
         ('St James Parish Council', 'Industry not yet assigned', 0.11, 0.00, -98, 'Storm window; consumption near zero')]
nrows = ''.join(f'<tr><td class="l">{a}</td><td class="l">{b}</td><td>{c:.2f}</td><td>{d:.2f}</td><td class="neg">{"&minus;" if e < 0 else ""}{abs(e)}%</td><td class="l">{f}</td></tr>\n' for a, b, c, d, e, f in NAMED)
CLS = [('Storm window, not recovered', 490, 4.41, 0.16), ('Storm window, recovering', 77, 4.02, 0.72), ('Account closed', 67, 1.60, 0.05),
       ('Contracted capacity released (outside the storm window)', 4, 1.49, 0.18), ('Small business, no clear signal', 227, 0.99, 0.08),
       ('Self-generation indicated', 2, 0.17, 0.00)]
crow = ''.join(f'<tr><td class="l">{a}</td><td>{b}</td><td>{c:.2f}</td><td>{d:.2f}</td><td class="neg">&minus;{c - d:.2f}</td><td>{(c - d) / 11.49 * 100:.0f}%</td></tr>\n' for a, b, c, d in CLS)
sec6 = f'''<h2>6. Customer Defection</h2>
<p>A commercial customer is treated as defecting when its consumption for January to August 2026 is more than 80% below the same period of 2025. On that definition 867 customers qualify, with a combined 2025 volume of 12.7 GWh that has fallen to 1.2 GWh &mdash; a loss of 11.5 GWh, or about 1% of commercial volume and roughly 18% of the 63 GWh decline in commercial sales. Defection is real but small; most of the decline in the commercial base comes from customers that reduced volume without leaving.</p>
<p>The next question is whether each defection is operational (a business that closed, was damaged or released capacity) or self-generation (a customer that now supplies itself but stays connected). Two signals separate them. The first is timing: a drop that lands in November and December 2025 coincides with Hurricane Melissa and points to storm damage or closure. The second is what the customer keeps paying for. A self-generating customer normally holds its grid connection and contracted demand as backup, so its demand charge stays in place while kWh disappears; an operational exit releases the capacity and the demand charge falls to the minimum or to nothing.</p>
<table>
<tr><th class="l">Likely cause</th><th>Customers</th><th>GWh Jan&ndash;Aug 2025</th><th>GWh Jan&ndash;Aug 2026</th><th>GWh lost</th><th>Share of loss</th></tr>
{crow}<tr class="tot"><td class="l">Total</td><td>867</td><td>12.68</td><td>1.19</td><td class="neg">&minus;11.49</td><td>100%</td></tr>
</table>
<p>About 91% of the volume lost to defection is operational, and most of it is storm-related: customers whose consumption fell away in the two months after the hurricane and have not come back, plus 77 that are recovering. Only two customers show the self-generation signature of near-zero kWh with grid capacity held, and together they account for under 2% of the loss. The four customers that released contracted capacity outside the storm window (Carib Products, Dougall Flooring and two others) are the ones to confirm directly, since a capacity cut can also follow a move to on-site generation. Alcoa does not appear here because its August exit is too recent to move a January-to-August total by 80%; it is the one large, confirmed self-generation case in the base and will enter this definition as 2026 progresses.</p>
<h3>Largest defecting customers (2025 volume of 0.1 GWh or more)</h3>
<table>
<tr><th class="l">Customer</th><th class="l">Industry</th><th>GWh 2025</th><th>GWh 2026</th><th>Change</th><th class="l">Likely cause</th></tr>
{nrows}</table>
<p class="note">Cause is inferred from timing and from whether the customer kept its contracted demand; it is an indicator, not a confirmation. The 227 small-business customers in "no clear signal" carry no demand charge, so the second test cannot be applied to them.</p>

'''
i = html.index('<h2>Questions to Consider</h2>')
html = html[:i] + sec6 + html[i:]

# ---------------- Q&A: EV, self-generation, lost sales ----------------
def sub(start, end, new):
    global html
    i = html.index(start); j = html.index(end, i) + len(end)
    html = html[:i] + new + html[j:]
sub('<dd>There is an EV rate class in use', '</dd>',
    '<dd>Growing quickly, and mostly through greater usage per site rather than more sites. Billing under the EV tariff rose from 12.6 MWh in August 2025 to 66.2 MWh in August 2026 (5.2 times), and revenue from J$0.5 million to J$2.4 million. Sites went from 20 to 25, but average use per site rose from about 630 kWh to about 2,650 kWh a month. January&ndash;August volume is 375 MWh against 65 MWh a year earlier. The step-up came in January 2026 (12.8 MWh in December to 36.6 MWh in January on just two more sites), which suggests higher-capacity chargers coming into service, and it has climbed every month since March. Every EV-tariff site is billed to JPS itself, across the parishes, so today the growth is JPS\'s own charging network; no third-party operator has a site on the EV tariff. Chargers run by other operators, such as Evergo, that are metered on ordinary commercial tariffs cannot be separated from other commercial load. The volume is still tiny &mdash; 0.02% of monthly system sales &mdash; and earns about J$36.5 per kWh against a system average near J$53.</dd>')
sub('<dd>Solar shows up in two ways in the data.', '</dd>',
    '<dd>Solar shows up in two ways. Customers registered on the net-billing tariff number about 890 (roughly 510 residential, 313 small business, 65 large commercial) and are barely growing, up 4&ndash;5% in a year. But customers who actually exported more than they drew in August number about 1,070 across the two residential tariffs, close to double the registered residential count, and grew 26% (RT10) and 58% (RT20) year over year &mdash; so at least 450 residential exporters sit outside registered net billing, and that group is where the growth is. The forecast expected 1,632 RT10 net-export customers in August against the 966 realized, so residential self-generation is running behind plan rather than ahead of it. Among commercial customers, the 867 that cut consumption by more than 80% are overwhelmingly operational (storm closures, releases of contracted capacity); only two carry the self-generation signature (Section 6). Alcoa\'s exit is the one large, clear self-generation case: a full one-month departure from grid draw (9 GWh to 1.2), not a gradual export pattern. Commercial exporters are rare (about 50 small-business accounts and none on RT40/RT50 in August) and commercial net-billing accounts are flat. See Sections 3 and 6 and Appendix A9.</dd>')
sub('<dd>Two causes cover nearly all of it:', '</dd>',
    '<dd>Two causes cover nearly all of it: Alcoa\'s self-generation (RT70, permanent, not returning) and the hotel sector\'s still-incomplete Hurricane Melissa recovery (temporary, closing gradually month over month). Outright defection, meaning customers down more than 80%, accounts for only about 18% of the commercial decline and is overwhelmingly storm-related (Section 6).</dd>')

# ---------------- remove Data Gaps ----------------
cut('<h2>Data Gaps Identified This Pass</h2>', '<div style="page-break-before:always"></div>', '')
open(HTML, 'w', encoding='utf-8').write(html)
print('final patch applied', len(html))
