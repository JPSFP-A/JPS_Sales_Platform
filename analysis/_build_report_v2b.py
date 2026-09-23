# -*- coding: utf-8 -*-
# Part B: Data Gaps, Appendix, Q&A edits, then splice all blocks into the report HTML.
import json, re
exec(open(r'C:\Projects\Sales_Platform\analysis\_build_report_v2.py', encoding='utf-8').read().split('# ---------------- Attribution block')[0])
A = json.load(open(r'C:\Projects\Sales_Platform\analysis\_report_blocks_a.json', encoding='utf-8'))
NB = EX['nb']
def nbc(mo, code): return round(NB[mo][code]['count'])

def tbl(head, rows, total=None):
    LC = ' class="l"'
    out = '<table>\n<tr>' + ''.join('<th%s>%s</th>' % (LC if i == 0 else '', h) for i, h in enumerate(head)) + '</tr>\n'
    out += '\n'.join(rows)
    if total: out += '\n' + total
    return out + '\n</table>'

def band_rows(bands, dec=2):
    rows = []; t = [0, 0, 0.0, 0.0]
    for lab, c25, c26, g25, g26 in bands:
        t[0] += c25; t[1] += c26; t[2] += g25; t[3] += g26
        rows.append(f'<tr><td class="l">{lab}</td><td>{n(c25)}</td><td>{n(c26)}</td>{chg(c25, c26, 0, 1, cls=False) if c25 else "<td>new</td>"}<td>{n(g25, dec)}</td><td>{n(g26, dec)}</td></tr>')
    tot = f'<tr class="tot"><td class="l">Total</td><td>{n(t[0])}</td><td>{n(t[1])}</td>{chg(t[0], t[1], 0, 1, cls=False)}<td>{n(t[2], dec)}</td><td>{n(t[3], dec)}</td></tr>'
    return rows, tot
BH = ['Band (kWh per month)', 'Customers Aug-25', 'Customers Aug-26', 'Change', 'GWh Aug-25', 'GWh Aug-26']

RT10 = [('Net export (below zero)', 768, 966, -0.15, -0.25), ('Zero consumption', 50569, 57968, 0.0, 0.0),
        ('Under 150', 312030, 310802, 23.88, 23.22), ('150 to 350', 206685, 201151, 46.08, 45.07),
        ('350 to 550', 40652, 44120, 17.39, 18.94), ('550 to 750', 12672, 14436, 8.03, 9.15),
        ('750 to 950', 5092, 6129, 4.26, 5.13), ('Over 950', 6854, 8155, 11.40, 13.30), ('Prepaid', 16080, 17983, 2.57, 3.10)]
RT20R = [('Net export (below zero)', 67, 106, -0.09, -0.05), ('Zero consumption', 5712, 6340, 0.0, 0.0),
         ('Under 150', 18927, 18874, 1.12, 1.10), ('150 to 350', 10085, 9992, 2.37, 2.36),
         ('350 to 550', 4788, 4757, 2.10, 2.09), ('550 to 750', 2537, 2658, 1.63, 1.71),
         ('750 to 950', 1615, 1671, 1.36, 1.41), ('Over 950', 5499, 5903, 12.86, 15.07), ('Prepaid', 494, 505, 0.11, 0.12)]

L = EX['band_labels']
LAB = {L[0]: 'Net export (below zero)', L[1]: 'Zero consumption'}
def comm_bands(cls):
    a, b = EX['bands']['2025-08'].get(cls), EX['bands']['2026-08'].get(cls)
    out = []
    for i, lab in enumerate(L):
        c25, c26 = int(a[i][0]) if a else 0, int(b[i][0]) if b else 0
        if not (c25 or c26): continue
        g25, g26 = (a[i][1] / 1e6 if a else 0), (b[i][1] / 1e6 if b else 0)
        out.append((LAB.get(lab, lab.replace('-', ' to ')), c25, c26, g25, g26))
    return out

app = '<div style="page-break-before:always"></div>\n<h2>Appendix</h2>\n'
app += '<p>Supporting tables for the sections above. Unless stated, figures are August 2025 against August 2026, or January to August for year-to-date measures. Sales are billed kWh; revenue is net billed revenue before GCT.</p>\n'

app += '<h3>A1. Reconciliation of the segment view to the system totals</h3>\n'
app += tbl(['Customers', 'Aug 2025', 'Aug 2026'], [
    f'<tr><td class="l">Residential &mdash; billed monthly</td><td>{n(CUST[25]["post"])}</td><td>{n(CUST[26]["post"])}</td></tr>',
    f'<tr><td class="l">Prepaid</td><td>{n(CUST[25]["pp"])}</td><td>{n(CUST[26]["pp"])}</td></tr>',
    f'<tr><td class="l">Commercial</td><td>{n(CUST[25]["com"])}</td><td>{n(CUST[26]["com"])}</td></tr>',
    f'<tr class="tot"><td class="l">Combined</td><td>{n(CUST[25]["all"])}</td><td>{n(CUST[26]["all"])}</td></tr>',
    '<tr><td class="l">Less: individually metered small-business accounts, not in the earlier headcount</td><td>&minus;23,617</td><td>&minus;23,542</td></tr>',
    '<tr class="tot"><td class="l">Equals the previously reported system total</td><td>703,643</td><td>715,040</td></tr>']) + '\n'
app += tbl(['Sales and revenue', 'Segments added up', 'Previously reported', 'Difference'], [
    f'<tr><td class="l">Sales Aug 2025 (GWh)</td><td>{n(SEG[25]["all_gwh_aug"],2)}</td><td>307.00</td><td>{n(SEG[25]["all_gwh_aug"]-307.00,2)}</td></tr>',
    f'<tr><td class="l">Sales Aug 2026 (GWh)</td><td>{n(SEG[26]["all_gwh_aug"],2)}</td><td>303.96</td><td>{n(SEG[26]["all_gwh_aug"]-303.96,2)}</td></tr>',
    f'<tr><td class="l">Sales Jan&ndash;Aug 2025 (GWh)</td><td>{n(SEG[25]["all_gwh"],1)}</td><td>2,248.2</td><td>{n(SEG[25]["all_gwh"]-2248.2,1)}</td></tr>',
    f'<tr><td class="l">Sales Jan&ndash;Aug 2026 (GWh)</td><td>{n(SEG[26]["all_gwh"],1)}</td><td>2,134.2</td><td>{n(SEG[26]["all_gwh"]-2134.2,1)}</td></tr>',
    f'<tr><td class="l">Revenue Jan&ndash;Aug 2025 (J$M)</td><td>{n(SEG[25]["all_rev"])}</td><td>114,545</td><td>{n(SEG[25]["all_rev"]-114545)}</td></tr>',
    f'<tr><td class="l">Revenue Jan&ndash;Aug 2026 (J$M)</td><td>{n(SEG[26]["all_rev"])}</td><td>112,431</td><td>{n(SEG[26]["all_rev"]-112431)}</td></tr>']) + '\n'
app += '<p class="note">Differences are rounding only. The revenue components in Section 1b also add back to these revenue totals to within J$1M.</p>\n'

app += '<h3>A2. Consumption bands &mdash; RT10 residential</h3>\n'
r, t = band_rows(RT10); app += tbl(BH, r, t) + '\n'
app += '<h3>A3. Consumption bands &mdash; RT20 residential (small residential-type accounts)</h3>\n'
r, t = band_rows(RT20R); app += tbl(BH, r, t) + '\n'
app += '<p class="note">RT10 and RT20 residential use the standard residential bands. Customers in the prepaid line are also counted in the totals but have no band; net export means the customer sent more solar to the grid than it drew that month.</p>\n'
for tag, cls, nm in (('A4', 'RT20-commercial', 'RT20 commercial (small business, individually metered)'), ('A5', 'RT40', 'RT40 Commercial'),
                     ('A6', 'RT50', 'RT50 Large Commercial'), ('A7', 'RT60-ST', 'RT60-ST Street Lighting'), ('A8', 'RT70', 'RT70 Industrial')):
    app += f'<h3>{tag}. Consumption bands &mdash; {nm}</h3>\n'
    r, t = band_rows(comm_bands(cls)); app += tbl(BH, r, t) + '\n'
app += '<p class="note">Commercial and industrial classes are individually metered, so the bands are set on each account\'s monthly kWh rather than the residential bands. Thirteen zero-consumption accounts (eleven a year ago) are not mapped to any rate class and are left out of the class tables; the volume involved is nil.</p>\n'

app += '<h3>A9. Net billing &mdash; registered customers against customers exporting in the month</h3>\n'
app += tbl(['Registered on the net-billing tariff', 'Aug 2025', 'Dec 2025', 'Aug 2026', 'Change'], [
    f'<tr><td class="l">Residential (NB10)</td><td>{nbc("2025-08","NB10")}</td><td>{nbc("2025-12","NB10")}</td><td>{nbc("2026-08","NB10")}</td>{chg(nbc("2025-08","NB10"), nbc("2026-08","NB10"), 0, 1, cls=False)}</tr>',
    f'<tr><td class="l">Small business (NB20)</td><td>{nbc("2025-08","NB20")}</td><td>{nbc("2025-12","NB20")}</td><td>{nbc("2026-08","NB20")}</td>{chg(nbc("2025-08","NB20"), nbc("2026-08","NB20"), 0, 1, cls=False)}</tr>',
    f'<tr><td class="l">Large commercial (NB40)</td><td>{nbc("2025-08","NB40")}</td><td>{nbc("2025-12","NB40")}</td><td>{nbc("2026-08","NB40")}</td>{chg(nbc("2025-08","NB40"), nbc("2026-08","NB40"), 0, 1, cls=False)}</tr>'],
    total=(lambda a, b, c: f'<tr class="tot"><td class="l">Total registered</td><td>{a}</td><td>{b}</td><td>{c}</td>{chg(a, c, 0, 1, cls=False)}</tr>')(
        sum(nbc('2025-08', k) for k in ('NB10', 'NB20', 'NB40')), sum(nbc('2025-12', k) for k in ('NB10', 'NB20', 'NB40')), sum(nbc('2026-08', k) for k in ('NB10', 'NB20', 'NB40')))) + '\n'
app += tbl(['Customers exporting more than they drew, in August', 'Aug 2025', 'Aug 2026', 'Change'], [
    '<tr><td class="l">RT10 residential</td><td>768</td><td>966</td>' + chg(768, 966, 0, 1, cls=False) + '</tr>',
    '<tr><td class="l">RT20 residential</td><td>67</td><td>106</td>' + chg(67, 106, 0, 1, cls=False) + '</tr>',
    '<tr><td class="l">RT20 commercial</td><td>25</td><td>50</td>' + chg(25, 50, 0, 1, cls=False) + '</tr>',
    '<tr><td class="l">RT40 and RT50 commercial</td><td>1</td><td>0</td><td>&nbsp;</td></tr>']) + '\n'
app += '<p class="note">Registered net-billing customers, on average, still draw more from the grid than they export, so they are not the same population as customers in net export in a given month. Registered figures come from the billing extract; the sales platform does not currently flag the net-billing tariff.</p>\n'

app += '<h3>A10. Demand-billed classes &mdash; volume, billed demand and charges, January to August</h3>\n'
KV = [('RT40 Commercial', 536.4, 502.5, 2066, 1980, 3620.2, 3391.0, 5206.2, 5006.7),
      ('RT50 Large Commercial', 253.6, 229.3, 1369, 1284, 1228.0, 1112.8, 1760.5, 1628.0),
      ('RT70 Industrial', 199.6, 195.2, 936, 851, 993.6, 971.9, 1809.3, 1708.7)]
kr = []
for nm, g25, g26, v25, v26, e25, e26, d25, d26 in KV:
    kr.append(f'<tr><td class="l">{nm}</td><td>{n(g25,1)} &rarr; {n(g26,1)}</td><td>{n(v25)} &rarr; {n(v26)}</td><td>{n(e25)} &rarr; {n(e26)}</td><td>{n(d25)} &rarr; {n(d26)}</td></tr>')
app += tbl(['Class', 'GWh', 'Billed kVA (thousands)', 'Energy charge (J$M)', 'Demand charge (J$M)'], kr) + '\n'
app += '<p class="note">Billed kVA is the sum of the monthly billed demand across the accounts in each class.</p>\n'

app += '<h3>A11. Definitions</h3>\n<ul>\n'
app += '<li><b>Residential &mdash; billed monthly</b>: RT10 homeowner accounts and the residential-type accounts on RT20, billed after use. <b>Prepaid</b>: pay-as-you-go accounts on RT10 and RT20, reported separately. <b>Commercial</b>: RT20 accounts registered as businesses, plus RT40, RT50, RT60-ST and RT70.</li>\n'
app += '<li><b>Customers</b> are billed accounts in the month: residential counts come as totals by band, commercial counts are one per metered account. <b>Sales</b> are billed kWh. <b>Revenue</b> is net billed revenue before GCT, which is shown separately.</li>\n'
app += '<li><b>Non-fuel charges</b> are the customer charge, energy charge and (commercial only) demand charge; <b>fuel</b> and <b>IPP</b> are the pass-through charges; <b>other</b> is what remains between the sum of those charges and net revenue (billing adjustments and credits).</li>\n</ul>\n'

# ---------------- Data gaps ----------------
gaps = '''<h2>Data Gaps Identified This Pass</h2>
<p>A few things came up repeatedly enough while working through this that they're worth listing separately rather than burying in the sections above, since they'll limit how far any future version of this analysis can go until they're addressed.</p>
<ul>
<li><b>Parish by consumption band isn't available for residential.</b> Every residential account carries a parish in the source billing records, and Section 4 now uses that directly. But the residential band feed into the sales platform combines all parishes into one island-wide total, so a band-by-parish cut still needs that feed rebuilt at parish level.</li>
<li><b>Registered net billing isn't flagged in the sales platform.</b> The net-billing tariff (about 890 accounts) is folded into the ordinary residential, small-business and commercial classes on the way in, so it can only be seen by going back to the billing extract, which is where the figures in this report come from. Customers exporting in the month can be seen in the platform, but that is a different and larger group (Section 3, Appendix A9). Carrying a net-billing flag through to the platform would remove the need to reconstruct it.</li>
<li><b>Revenue components are stored only for commercial accounts.</b> Fuel, energy, IPP and customer-charge splits are held in the platform for commercial accounts only. Residential components in Section 1b come straight from the billing extract, and prepaid isn't split by component in any source, so it appears as a single revenue line.</li>
<li><b>GCT is missing for the larger commercial classes in recent months.</b> Tax on RT40, RT50, RT60-ST and RT70 hasn't been loaded for May, July or August 2026 (and RT60-ST in June looks out of line with earlier months), so tax is shown for January to April only.</li>
<li><b>"Other" revenue fell J$1.2 billion year over year.</b> Adjustments and credits dropped from about J$200 million a month on commercial accounts in early 2025 to about J$55 million in 2026. It accounts for over half of the net revenue decline and should be confirmed with Billing as either real or a change in how adjustments are recorded.</li>
<li><b>EV charging (tariff EV40) is modeled in the forecast layer ahead of the actuals cutover.</b> 26 JPS-owned sites are already classified as EV in the June-2026 Latest Estimate; 3 have real billing history, still coded under RT40/RT20. There's no way to track EV growth, public or JPS-owned, until the metering/billing side finishes reclassifying these accounts into the live feed.</li>
<li class="pos"><b>Fixed during this pass, not just flagged.</b> Every commercial account on RT20, RT40, RT50, RT60-ST and RT70 was being given the same generic "Commercial" usage tag regardless of what it actually consumed &mdash; so a business exporting power to the grid, or one billing zero for the month, looked identical in the data to one drawing normal load. That's why export and zero-consumption commercial customers were invisible to the cuts used elsewhere in this report. Corrected across the full history. Real counts, now visible: RT40 carries 71 net-exporting customer-months and 1,287 zero-consumption customer-months historically; RT50 carries 65 and 166; RT20 commercial carries 783 and 47,614 out of 461,828 records. Commercial customers exporting in the month are rare and not trending sharply (RT40 about 1 a month in 2025 to about 2.75 in 2026, RT50 flat at about 2).</li>
<li><b>Self-generation is only tracked through the net-billing tariff.</b> The planning record that looks like it should log self-generation is forward-looking assumptions for 2027 onward. Anything outside the roughly 890 registered accounts &mdash; including a large single-account change like Alcoa's &mdash; has to be reconstructed after the fact from billing going to zero or negative.</li>
<li><b>About one kWh in eight of commercial volume carries no industry classification</b> (12.6% in 2026), almost all of it small-business accounts, where 56% of volume is untagged. A tagging cleanup targeted at the small-business file would close nearly all of it (Section 5).</li>
</ul>

'''

# ---------------- splice ----------------
html = open(HTML, encoding='utf-8').read()
def cut(start, end, new):
    global html
    i = html.index(start); j = html.index(end, i)
    html = html[:i] + new + html[j:]
cut('<h2>Attribution Check</h2>', '<h2>1. Top Level</h2>', A['attr'])
cut('<h2>1. Top Level</h2>', '<h2>2. Across Rate Class</h2>', A['sec1'])
cut('<h2>3. Within Rate Class', '<h2>4. By Parish</h2>', A['sec3'])
cut('<h2>4. By Parish</h2>', '<h2>5. By Sector / Industry</h2>', A['sec4'])
cut('<h2>5. By Sector / Industry</h2>', '<h3>5b.', A['sec5'])
cut('<h2>Data Gaps Identified This Pass</h2>', '<div class="meta">', gaps + app + '\n')

def sub(old_start, old_end_marker, new):
    global html
    i = html.index(old_start); j = html.index(old_end_marker, i) + len(old_end_marker)
    html = html[:i] + new + html[j:]

# Q&A: self-generation
sub('<dd>There\'s no record that logs historical self-generation', '</dd>',
    '<dd>Solar shows up in two ways in the data. Customers registered on the net-billing tariff number about 890 (roughly 510 residential, 313 small business, 65 large commercial) and are barely growing, up 4&ndash;5% in a year. But customers who actually exported more than they drew in August number about 1,070 across the two residential tariffs, close to double the registered residential count, and grew 26% (RT10) and 58% (RT20) year over year &mdash; so at least 450 residential exporters sit outside registered net billing, and that group is where the growth is. The forecast expected 1,632 RT10 net-export customers in August against the 966 realized, so residential self-generation is running behind plan rather than ahead of it. Alcoa\'s exit was categorically different, a full one-month departure from grid draw (9 GWh to 1.2), not a gradual export pattern. Commercial exporters are rare (about 50 small-business accounts and none on RT40/RT50 in August) and commercial net-billing accounts are flat. There is no record that logs self-generation events as they happen beyond the registered tariff, so anything outside it has to be reconstructed after the fact. See Section 3 and Appendix A9.</dd>')
# Q&A: revenue effect
sub('<dd>Far more gently than the volume numbers suggest', '</dd>',
    '<dd>Far more gently than the volume numbers suggest &mdash; system-wide, &minus;1.85% revenue against &minus;5.1% volume, because the average rate rose 3.4% and absorbed most of the difference. For commercial customers there is a second cushion: demand charges are billed on peak kVA, which doesn\'t fall in step with kWh, so across RT40, RT50 and RT70 volume and the energy charge are both down 6.3% while the demand charge is down only 4.9%. RT70 revenue is actually up despite selling less power. See Sections 1b and 2.</dd>')
# Q&A: where demand loss concentrated
sub('<dd>By class, RT50 and RT60-ST.', '</dd>',
    '<dd>By class, RT50 and RT60-ST. By consumption bucket, RT10\'s two lowest bands are losing customers even as everyone who remains in the higher bands uses more. By geography, the western parishes &mdash; Westmoreland, St. Elizabeth, Hanover, Trelawny and St. James &mdash; carry the whole of the residential volume decline. See Sections 3 and 4.</dd>')

open(HTML, 'w', encoding='utf-8').write(html)
print('report rebuilt', len(html))
