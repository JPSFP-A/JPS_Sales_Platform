# -*- coding: utf-8 -*-
# Part B: questions, appendix and final assembly of the September report.
from _build_sep import *
import _build_sep as _X
import json, collections
_d = _X._d; _ix = _X._ix

# ----- extra facts -----
SEPR = {y: sum(S(g, y, 2, 9) for g in G) / 1e6 for y in (2025, 2026)}
ev = D.ev_series()
evm = lambda y, m: ev['%d-%02d' % (y, m)]
ev_ytd = {y: sum(evm(y, m)[1] for m in range(1, 10)) for y in (2025, 2026)}
ev_mono = all(evm(2026, m)[1] < evm(2026, m + 1)[1] for m in range(3, 9))
s2 = json.load(open('_sep_scan2.json'))
for f in s2:
    assert all('JAMAICA PUBLIC SERVICE' in nm.upper() for nm in s2[f]['ev']), s2[f]['ev'].keys()
rt70d = D._C['RT70'][2026][0] / 1e6 - D._C['RT70'][2025][0] / 1e6
alc70 = (alc['26'][1] - alc['25'][1]) / 1e6
ind_rev = lambda nm: pct(D.IND[nm][2], D.IND[nm][3])
ind_vol = lambda nm: pct(D.IND[nm][0], D.IND[nm][1])
HN, WN = 'Hotels (except Casino Hotels) and Motels', 'Water Supply and Irrigation Systems'
exp_n = D.EXPORTERS['2026-09']; exp_o = D.EXPORTERS['2025-09']
sepsys_adj = SEPK[2026] + 1.58
QA = []
def q(question, answer): QA.append(f'<dt>{question}</dt>\n<dd>{answer}</dd>')
q('How are we performing from a sales perspective? Growing, declining, or flat?',
  f'Declining in volume ({M}{abs(pct(ALLK[2025],ALLK[2026])):.1f}% YTD), growing in customer count (+{pct(CUSTS[2025],CUSTS[2026]):.1f}%), close to flat in revenue ({M}{abs(pct(ALLR[2025],ALLR[2026])):.1f}%, cushioned by the rate increase). September sales were down {abs(pct(SEPK[2025],SEPK[2026])):.1f}% ({abs(pct(SEPK[2025],sepsys_adj)):.1f}% after adjusting for billing timing at Caribbean Broilers) and revenue was up {pct(SEPR[2025],SEPR[2026]):.1f}%. See Section 1.')
q('What customer class is driving sales and peak-demand changes? What are the drivers? Where are the shortfalls?',
  f'RT50 and RT60-ST have the steepest percentage volume declines ({M}9.6% and {M}9.5%); RT70 has the steepest customer-count decline ({M}8.7%, two accounts), though one hotel moving from RT50 to RT70 in 2025 flatters RT70 and penalises RT50. Excluding Alcoa, billed demand across RT40, RT50 and RT70 is down {abs(dem_all["kva"]):.1f}% against kWh down {abs(dem_all["kwh"]):.1f}%. See Sections 1b and 2.')
q('Which customers explain the gains? Do these reflect business growth, new accounts, return to the grid, or billing adjustments?',
  f'Mostly new connections in count terms, but a large share of those are zero-consumption (Section 3), so they\'re not really adding load. The gains that do reflect real business growth are concentrated in a handful of named accounts &mdash; Caribbean Cement (+11.5 GWh year to date in RT50), the distilleries ({P(*D.IND["Distilleries"][:2],0)}) &mdash; and in the upward migration of existing residential customers into higher bands, not broad-based growth across the customer file. Prepaid is the other clear gain, up {pct(YT("pp",2025,1),YT("pp",2026,1)):.0f}% in volume.')
q('Which customers explain lost sales? What is the cause, and when is demand expected to return, if so?',
  f'Three causes cover most of it: Alcoa\'s self-generation (RT70, permanent, not returning), the hotel sector\'s still-incomplete Hurricane Melissa recovery (temporary, closing gradually), and a handful of other large accounts such as Jamaica Broilers Group, whose volume stepped down in mid-2025. Outright defection, meaning customers down more than 80%, accounts for only about {loss/com_decl*100:.0f}% of the commercial decline and is overwhelmingly storm-related (Section 6).')
q('Where a rate class shows net growth or net decline overall, is that outcome driven mainly by new connections and closures rather than by existing customers, and could that be masking an underlying decline (or growth) among the existing customer base?',
  'Yes, and this is the central finding of the whole exercise. Existing RT10 and RT20 customers are genuinely using more, moving into higher consumption bands, but that real growth is invisible in the blended per-customer average because it\'s being swamped by a wave of connections that use nothing at all. See Section 3.')
q('Within each rate class, does the number of customers gaining vs. losing consumption align with the direction of net load change, or is the result being driven by a small number of accounts with disproportionately large swings?',
  f'A small number of accounts. See Section 5b &mdash; RT50\'s losses trace to a poultry group and four hotel properties (and one reclassified hotel), and its largest gain is a single cement account; Alcoa accounts for {abs(alc70):.1f} GWh of RT70\'s {abs(rt70d):.1f} GWh year-to-date decline.')
q('Which industries are growing or declining, and why? Are changes widespread or concentrated in a few customers/classes?',
  f'Concentrated. Hotels alone outweighs the next three declining industries combined. See Section 5.')
q('Within industries, how is the composition of demand changing? Does a higher share reflect growth or declines elsewhere?',
  'Mixed, and worth distinguishing case by case: Cement Manufacturing\'s rising share is real growth (volume and share both up together); Hotels\' falling share is a genuine decline, not dilution by faster-growing peers. See Section 5a.')
q('Where is demand loss concentrated? Which Rate Class? Which consumption bucket?',
  'By class, RT50 and RT60-ST. By consumption bucket, RT10\'s two lowest bands are losing customers even as everyone who remains in the higher bands uses more. By geography, the western parishes &mdash; Westmoreland, St. Elizabeth, Hanover, Trelawny and St. James &mdash; carry the whole of the residential volume decline. See Sections 3 and 4.')
sites = lambda y, m: evm(y, m)[0]
q('Is charging demand growing through more accounts or greater usage? Which operators are driving the increase?',
  f'Growing quickly, and mostly through greater usage per site rather than more sites. Billing under the EV tariff rose from {evm(2025,9)[1]:.1f} MWh in September 2025 to {evm(2026,9)[1]:.1f} MWh in September 2026 ({evm(2026,9)[1]/evm(2025,9)[1]:.1f} times), and revenue from J${evm(2025,9)[2]/1e6:.2f} million to J${evm(2026,9)[2]/1e6:.2f} million. Sites went from {sites(2025,9)} to {sites(2026,9)}, but average use per site rose from about {evm(2025,9)[1]*1000/sites(2025,9):,.0f} kWh to about {evm(2026,9)[1]*1000/sites(2026,9):,.0f} kWh a month. January&ndash;September volume is {ev_ytd[2026]:.0f} MWh against {ev_ytd[2025]:.0f} MWh a year earlier. The step-up came in January 2026 ({evm(2025,12)[1]:.1f} MWh in December to {evm(2026,1)[1]:.1f} MWh in January on just two more sites), which suggests higher-capacity chargers coming into service, and it has climbed every month since March. Every EV-tariff site is billed to JPS itself, across the parishes, so today the growth is JPS\'s own charging network; no third-party operator has a site on the EV tariff. Chargers run by other operators, such as Evergo, that are metered on ordinary commercial tariffs cannot be separated from other commercial load. The volume is still tiny &mdash; {evm(2026,9)[1]/(SEPK[2026]*1000)*100:.2f}% of monthly system sales &mdash; and earns about J${evm(2026,9)[2]/(evm(2026,9)[1]*1000):.1f} per kWh against a system average near J${ALLR[2026]/ALLK[2026]:.0f}.')
assert ev_mono
q('How quickly is self-generation growing? How does it affect grid purchases, and how much activity sits outside registered net billing? For declining accounts, is the reduction due to lower usage while remaining connected versus full disconnection from the grid?',
  f'Solar shows up in two ways. Customers registered on the net-billing tariff number {n(nb_tot["2026-09"])} ({nbc("2026-09","NB10")} residential, {nbc("2026-09","NB20")} small business, {nbc("2026-09","NB40")} large commercial) and are growing slowly, up {PU(nb_tot["2025-09"],nb_tot["2026-09"])} in a year. But customers who actually exported more than they drew in September number {n(exp_n[0]+exp_n[1])} across the two residential tariffs, close to double the registered residential count, and are up {PU(exp_o[0],exp_n[0],0)} (RT10) and {PU(exp_o[1],exp_n[1],0)} (RT20) year over year &mdash; so at least {exp_n[0]-nbc("2026-09","NB10")} residential exporters sit outside registered net billing, and that group is where the growth is. The pattern is seasonal, with fewer exporters in summer, but the summer base is now about {PU(summer25,summer26,0)} higher than a year ago. Among commercial customers, the {totn} that cut consumption by more than 80% are overwhelmingly operational (storm closures, releases of contracted capacity); only two carry the self-generation signature, and one of those is JPS\'s own account (Section 6). Alcoa\'s exit is the one large, clear self-generation case: a full one-month departure from grid draw (9 GWh to 1.3), not a gradual export pattern, and it still runs about 0.8 GWh a month. Commercial exporters are rare ({D.EXPORTERS["2026-09"][2]} small-business accounts and {D.EXPORTERS["2026-09"][3]} on RT40 to RT70 in September) and commercial net-billing accounts are flat. See Sections 3 and 6 and Appendix A9.')
q('How are demand changes affecting revenue across rate classes?',
  f'Far more gently than the volume numbers suggest &mdash; system-wide, {M}{abs(pct(ALLR[2025],ALLR[2026])):.1f}% revenue against {M}{abs(pct(ALLK[2025],ALLK[2026])):.1f}% volume, because the average rate rose {pct(rate[2025],rate[2026]):.1f}% and absorbed most of the difference. For commercial customers there is a second cushion: demand charges are billed on peak kVA, which doesn\'t fall in step with kWh, so across RT40, RT50 and RT70 (excluding Alcoa) volume is down {abs(dem_all["kwh"]):.1f}% and the energy charge {abs(dem_all["en"]):.1f}% while billed kVA is down {abs(dem_all["kva"]):.1f}%. RT70 revenue is actually up despite selling less power, partly because of Alcoa\'s provisional demand charges. See Sections 1b and 2.')
q('Which industries now contribute the most revenue? How does an industry or rate-class change compare in scale to the overall system-level change &mdash; is it disproportionately responsible relative to its size?',
  f'Hotels lost {abs(ind_vol(HN)):.1f}% of its volume but only {abs(ind_rev(HN)):.1f}% of its revenue &mdash; a favorable rate or mix shift cushioned some of the blow. Water Supply shows the same pattern at a smaller scale ({abs(ind_vol(WN)):.1f}% of volume, {abs(ind_rev(WN)):.1f}% of revenue). See Section 5.')
q('What is happening within key customer businesses? Which changes are temporary disruptions versus sustained changes in grid demand?',
  'Temporary: the hotel sector\'s Melissa recovery, which is closing gradually. Sustained: Alcoa\'s self-generation, which is a permanent reduction in grid draw, not a dip that reverses. Alcoa\'s billed demand is provisional and will be adjusted down, so its remaining revenue should not be read as retained capacity.')
q('Is average revenue per kWh changing?',
  f'Yes, and it\'s the main reason revenue held up better than volume &mdash; the system-wide blended rate rose from J${rate[2025]/1000:.2f}/kWh to J${rate[2026]/1000:.2f}/kWh, {P(rate[2025],rate[2026])}. Every rate class saw its own rate rise over the period; RT70 ({CLS["RT70"][1]:+.1f}%) and RT40 ({CLS["RT40"][1]:+.1f}%) moved the most. The split by non-fuel, fuel, IPP and taxes is in Section 1b: fuel drives the increase, while the non-fuel rate is roughly flat.')
A('<h2>Key Questions</h2>'); A('<dl class="qa">\n' + '\n\n'.join(QA) + '\n</dl>')

# ================= Appendix =================
A('<h2>Appendix</h2>')
A('<p>Supporting tables for the sections above. Unless stated, figures are September 2025 against September 2026, or January to September for year-to-date measures. Sales are billed kWh; revenue is net billed revenue before GCT.</p>')
A('<h3>A1. Segment build-up of the combined figures</h3>')
A(tbl(['Customers', 'Sep 2025', 'Sep 2026'], [
    f'<tr><td class="l">Residential &mdash; billed monthly</td><td>{n(D.cust("post",2025,9))}</td><td>{n(D.cust("post",2026,9))}</td></tr>',
    f'<tr><td class="l">Prepaid</td><td>{n(D.cust("pp",2025,9))}</td><td>{n(D.cust("pp",2026,9))}</td></tr>',
    f'<tr><td class="l">Commercial</td><td>{n(D.cust("com",2025,9))}</td><td>{n(D.cust("com",2026,9))}</td></tr>'],
    f'<tr class="tot"><td class="l">Combined</td><td>{n(CUSTS[2025])}</td><td>{n(CUSTS[2026])}</td></tr>'))
A(tbl(['Sales and revenue, Jan&ndash;Sep', 'Residential', 'Prepaid', 'Commercial', 'Combined'], [
    f'<tr><td class="l">Sales 2025 (GWh)</td><td>{n(YT("post",2025,1)/1e6,1)}</td><td>{n(YT("pp",2025,1)/1e6,1)}</td><td>{n(YT("com",2025,1)/1e6,1)}</td><td>{n(ALLK[2025],1)}</td></tr>',
    f'<tr><td class="l">Sales 2026 (GWh)</td><td>{n(YT("post",2026,1)/1e6,1)}</td><td>{n(YT("pp",2026,1)/1e6,1)}</td><td>{n(YT("com",2026,1)/1e6,1)}</td><td>{n(ALLK[2026],1)}</td></tr>',
    f'<tr><td class="l">Net revenue 2025 (J$M)</td><td>{n(YT("post",2025,2)/1e6)}</td><td>{n(YT("pp",2025,2)/1e6)}</td><td>{n(YT("com",2025,2)/1e6)}</td><td>{n(ALLR[2025])}</td></tr>',
    f'<tr><td class="l">Net revenue 2026 (J$M)</td><td>{n(YT("post",2026,2)/1e6)}</td><td>{n(YT("pp",2026,2)/1e6)}</td><td>{n(YT("com",2026,2)/1e6)}</td><td>{n(ALLR[2026])}</td></tr>']))

BH = ['Band (kWh per month)', 'Customers Sep-25', 'Customers Sep-26', 'Change', 'GWh Sep-25', 'GWh Sep-26']
def band_table(rows):
    body = []; t = [0, 0, 0.0, 0.0]
    for lab, c25, c26, g25, g26 in rows:
        t[0] += c25; t[1] += c26; t[2] += g25; t[3] += g26
        body.append(f'<tr><td class="l">{lab}</td><td>{n(c25)}</td><td>{n(c26)}</td>{chg(c25,c26,0,1,cls=False) if c25 else "<td>new</td>"}<td>{n(g25,2)}</td><td>{n(g26,2)}</td></tr>')
    return tbl(BH, body, f'<tr class="tot"><td class="l">Total</td><td>{n(t[0])}</td><td>{n(t[1])}</td>{chg(t[0],t[1],0,1,cls=False)}<td>{n(t[2],2)}</td><td>{n(t[3],2)}</td></tr>')
RESB = [('Net export (below zero)', '<Zero'), ('Zero consumption', 'Zero'), ('Under 150', '<150'), ('150 to 350', '150>350'), ('350 to 550', '350>550'), ('550 to 750', '550>750'), ('750 to 950', '750>950'), ('Over 950', 'over 950'), ('Prepaid', 'Prepaid')]
def res_rows(c): return [(lab, D._B[c][2025][k][0], D._B[c][2026][k][0], D._B[c][2025][k][1] / 1e6, D._B[c][2026][k][1] / 1e6) for lab, k in RESB]
A('<h3>A2. Consumption bands &mdash; RT10 residential</h3>'); A(band_table(res_rows('RT10')))
A('<h3>A3. Consumption bands &mdash; RT20 residential (small residential-type accounts)</h3>'); A(band_table(res_rows('RT20res')))
A('<p class="note">RT10 and RT20 residential use the standard residential bands. Customers in the prepaid line are also counted in the totals but have no band; net export means the customer sent more solar to the grid than it drew that month.</p>')
BL = EX['band_labels']; LAB = {BL[0]: 'Net export (below zero)', BL[1]: 'Zero consumption'}
def comm_rows(cls):
    a, b = EX['bands']['2025-09'].get(cls), EX['bands']['2026-09'].get(cls); out_ = []
    for i, lab in enumerate(BL):
        c25, c26 = (int(a[i][0]) if a else 0), (int(b[i][0]) if b else 0)
        if not (c25 or c26): continue
        out_.append((LAB.get(lab, lab.replace('-', ' to ')), c25, c26, (a[i][1] / 1e6 if a else 0), (b[i][1] / 1e6 if b else 0)))
    return out_
for tag, cls, nm in (('A4', 'RT20-commercial', 'RT20 commercial (small business, individually metered)'), ('A5', 'RT40', 'RT40 Commercial'), ('A6', 'RT50', 'RT50 Large Commercial'), ('A7', 'RT60-ST', 'RT60-ST Street Lighting'), ('A8', 'RT70', 'RT70 Industrial')):
    A(f'<h3>{tag}. Consumption bands &mdash; {nm}</h3>'); A(band_table(comm_rows(cls)))
A('<p class="note">Commercial and industrial classes are individually metered, so the bands are set on each account\'s monthly kWh rather than the residential bands. Zero-consumption accounts that are not mapped to any rate class are left out of the class tables; the volume involved is nil.</p>')

A('<h3>A9. Net billing &mdash; registered customers against customers exporting in the month</h3>')
def nbrow(label, code):
    a, b, c = nbc('2025-09', code), nbc('2025-12', code), nbc('2026-09', code)
    return f'<tr><td class="l">{label}</td><td>{a}</td><td>{b}</td><td>{c}</td>{chg(a,c,0,1,cls=False)}</tr>'
ta, tb, tc = (sum(nbc(m, c) for c in ('NB10', 'NB20', 'NB40')) for m in ('2025-09', '2025-12', '2026-09'))
A(tbl(['Registered on the net-billing tariff', 'Sep 2025', 'Dec 2025', 'Sep 2026', 'Change'], [nbrow('Residential (NB10)', 'NB10'), nbrow('Small business (NB20)', 'NB20'), nbrow('Large commercial (NB40)', 'NB40')],
      f'<tr class="tot"><td class="l">Total registered</td><td>{ta}</td><td>{tb}</td><td>{tc}</td>{chg(ta,tc,0,1,cls=False)}</tr>'))
A(tbl(['Customers exporting more than they drew, in September', 'Sep 2025', 'Sep 2026', 'Change'], [
    f'<tr><td class="l">RT10 residential</td><td>{n(exp_o[0])}</td><td>{n(exp_n[0])}</td>{chg(exp_o[0],exp_n[0],0,1,cls=False)}</tr>',
    f'<tr><td class="l">RT20 residential</td><td>{n(exp_o[1])}</td><td>{n(exp_n[1])}</td>{chg(exp_o[1],exp_n[1],0,1,cls=False)}</tr>',
    f'<tr><td class="l">RT20 commercial</td><td>{n(exp_o[2])}</td><td>{n(exp_n[2])}</td>{chg(exp_o[2],exp_n[2],0,1,cls=False)}</tr>',
    f'<tr><td class="l">RT40 to RT70 commercial</td><td>{n(exp_o[3])}</td><td>{n(exp_n[3])}</td>{chg(exp_o[3],exp_n[3],0,1,cls=False)}</tr>']))
A('<p class="note">Registered net-billing customers, on average, still draw more from the grid than they export, so they are not the same population as customers in net export in a given month. Exporters are seasonal: they peak in the low-consumption winter months and trough in summer, so September is best compared with September.</p>')
# producers note
PROD = {'WIGTON': 'Wigton Windfarm', 'WEST KINGSTON POWER': 'West Kingston Power Partners', 'JAMAICA ENERGY PARTNERS': 'Jamaica Energy Partners', 'NFE SOUTH': 'NFE South Power Holdings', 'JAMAICA PRIVATE POWER': 'Jamaica Private Power Company', 'BMR JAMAICA WIND': 'BMR Jamaica Wind', 'EIGHT RIVERS': 'Eight Rivers Energy', 'SOUTH JAMAICA POWER': 'South Jamaica Power Company'}
neg = collections.Counter(); other_neg = collections.Counter()
for _c, _a in _d['acct'].items():
    if _a['title'] not in ('RT50', 'RT70'): continue
    for mo, v in _a['m'].items():
        if '2025-01' <= mo <= '2026-09' and v[_ix['kwh']] < 0:
            nm = ' '.join(_a['name'].split()).upper(); hit = next((lab for k, lab in PROD.items() if nm.startswith(k)), None)
            (neg if hit else other_neg)[hit or ' '.join(_a['name'].split())] += 1
tot_neg = sum(neg.values()) + sum(other_neg.values())
prod_txt = ', '.join(f'{k} ({v})' for k, v in neg.most_common())
oth_txt = ', '.join(sorted(other_neg))
A(f'<p class="note">RT50 and RT70 have no registered net-billing customers. Their negative-kWh months since January 2025 ({tot_neg} account-months) come almost entirely from power producers selling to the grid: {prod_txt}. The remaining {sum(other_neg.values())} ({oth_txt}) are reversals or station-service entries rather than exports.</p>')

A('<h3>A10. Demand-billed classes excluding Alcoa &mdash; volume, billed demand and charges, January to September</h3>')
arows = []
for c, lab in (('RT40', 'RT40 Commercial'), ('RT50', 'RT50 Large Commercial'), ('RT70', 'RT70 Industrial (excluding Alcoa)')):
    k25, v25 = dsum(c, 2025); k26, v26 = dsum(c, 2026)
    arows.append(f'<tr><td class="l">{lab}</td><td>{n(k25/1e6,1)} &rarr; {n(k26/1e6,1)}</td><td>{n(v25/1000)} &rarr; {n(v26/1000)}</td><td>{n(EN[c][0])} &rarr; {n(EN[c][1])}</td><td>{n(DM[c][0])} &rarr; {n(DM[c][1])}</td></tr>')
k25, v25 = dsum('ALL', 2025); k26, v26 = dsum('ALL', 2026)
A(tbl(['Class', 'GWh', 'Billed kVA (thousands)', 'Energy charge (J$M)', 'Demand charge (J$M)'], arows,
      f'<tr class="tot"><td class="l">All three</td><td>{n(k25/1e6,1)} &rarr; {n(k26/1e6,1)}</td><td>{n(v25/1000)} &rarr; {n(v26/1000)}</td><td>{n(en25)} &rarr; {n(en26)}</td><td>{n(dm25)} &rarr; {n(dm26)}</td></tr>'))
A('<p class="note">Alcoa is excluded because its billed demand for August and September is provisional and will be adjusted down. September figures for RT40 also carry a billing-timing distortion at one large account (Caribbean Broilers).</p>')
A('<h3>A11. Definitions</h3>')
A('<ul>\n<li><b>Residential &mdash; billed monthly</b>: RT10 homeowner accounts and the residential-type accounts on RT20, billed after use. <b>Prepaid</b>: pay-as-you-go accounts on RT10 and RT20, reported separately. <b>Commercial</b>: RT20 accounts registered as businesses, plus RT40, RT50, RT60-ST and RT70.</li>\n<li><b>Customers</b> are billed accounts in the month, one per metered account for commercial. <b>Sales</b> are billed kWh. <b>Revenue</b> is net billed revenue before GCT, which is shown separately.</li>\n<li><b>Non-fuel charges</b> are the customer charge, energy charge and (commercial only) demand charge; <b>fuel</b> and <b>IPP</b> are the pass-through charges; <b>other</b> is what remains between the sum of those charges and net revenue (billing adjustments and credits).</li>\n<li><b>Defecting customer</b>: a commercial customer whose January&ndash;September consumption is more than 80% below the same period of the prior year.</li>\n</ul>')
A('<div class="meta">Prepared by Sales Forecasting &amp; Analysis. Figures in GWh / J$ unless stated. Source: JPS billed sales and revenue records.</div>')

head = open(HTML, encoding='utf-8').read().replace('Attribution &amp; Requirements Review','September 2026').replace('Attribution & Requirements Review','September 2026')
head = head[:head.index('</style></head><body>') + len('</style></head><body>')]
open(HTML, 'w', encoding='utf-8').write(head + '\n\n' + '\n'.join(out) + '\n\n</body></html>\n')
print('written', HTML, 'producers', neg.most_common(), 'other', other_neg, 'alc70', alc70, 'rt70d', rt70d)
