# -*- coding: utf-8 -*-
# Restore the residential, net billing, weather and EV rationale in the driver report, as in the 7 September report.
p = '_build_driver_report_nov2.py'; s = open(p, encoding='utf-8').read()
def rep(old, new):
    global s
    if s.count(old) != 1: raise SystemExit('match count %d: %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)

# ---------- 1. residential drivers in the bridge ----------
BLOCK = r'''
# ================= residential drivers (as in the 7 September report) =================
RD = json.load(open('_driver_res_evidence.json'))
ppm = {(r[0], r[1]): r[2] for r in RD['pp']}
pp_run = sum(ppm[(2026, m)] for m in (8, 9, 10)) / 3 * 12 / 1e6            # GWh a year at the August to October rate
nbm = {(r[0], r[1]): r[2] for r in RD['nb']}
nb10_adds = nbm[(2026, 10)]['NB10'][0] - nbm[(2025, 10)]['NB10'][0]
win = [k for k in nbm if (2025, 11) <= k <= (2026, 10)]
exp_acct = sum(nbm[k]['NB10'][2] for k in win) / (sum(nbm[k]['NB10'][0] for k in win) / 12)   # kWh exported a year per registered NB10 account
SOLAR_X = 3.0                                                                     # self-consumption per kWh exported, the ratio the 7 September report carried (4.3 erosion on 1.4 observed)
sol = -nb10_adds * exp_acct * SOLAR_X / 1e6
RESK = ['Customer acquisition', 'Prepaid', 'Bucket migration', 'Load decline', 'Solar and net billing']
def reslines(g, acq):
    L = {'Customer acquisition': acq, 'Prepaid': pp_run * 0.008, 'Load decline': -EV['decl_gwh'], 'Solar and net billing': sol}
    L['Bucket migration'] = g - sum(L.values()); return L
RL27 = reslines(BC27['RT10']['Growth'], EV['acq_net'])
RL28 = reslines(BC28['RT10']['Growth'], EV['add10'] * EV['kpp10'] * 12 / 1e6)
def resplit(bc, RL):
    b2 = {c: {**bc[c], **{k: 0.0 for k in RESK}} for c in CL}
    b2['RT10']['Growth'] = 0.0
    for k in RESK: b2['RT10'][k] = RL[k]
    return b2
BC27, BC28 = resplit(BC27, RL27), resplit(BC28, RL28)
for k in RESK: C27[k] = 0.0; C28[k] = 0.0
DR = ['Run rate against FY2026'] + RESK + ['Growth', 'Hotel recovery', 'Defections and self-generation', 'Expansions', 'Planned outages and other', 'Pipeline customers']
DRL.update({
  'Customer acquisition': ('RT10', 'Premises joining the grid at about 820 a month (+1.5% a year), each using the FY2026 average. Section 4.'),
  'Prepaid': ('RT10', 'Prepaid volume growing with RT10 at 0.8%. Observed growth is far higher but is mostly postpaid customers converting. Section 5.4.'),
  'Bucket migration': ('RT10', 'Households moving up the consumption bands. It is the balancing driver inside the 0.8% growth, so it moves when acquisition, load decline or solar are re-measured. Section 5.2.'),
  'Load decline': ('RT10', 'Conservation and tariff response at the two ends of the book: under 150 kWh and over 950 kWh. Section 5.3.'),
  'Solar and net billing': ('RT10', 'Registered net billers added over the year, at what each exports and what it self-consumes. Section 7.'),
  'Growth': ('Commercial and RT20', 'RT20 grows 0.8% a year and commercial 1% from April 2027. In FY2028 commercial grows another 1%.')})
'''
rep("movement(27, BC27, C27, 26, 27, ('2. FY2026 to FY2027 Movement by Driver', ''))", BLOCK + "\nmovement(27, BC27, C27, 26, 27, ('2. FY2026 to FY2027 Movement by Driver', ''))")
rep("bcc = bc[c]; txt += f'Run rate against FY2026 {sgn(bcc[\"Run rate against FY2026\"])}, growth {sgn(bcc[\"Growth\"])}. ' + ('Residential is modelled at class level, so there is no customer split; the evidence is in Sections 4 and 5.' if True else '')",
    "bcc = bc[c]; txt += f'Run rate against FY2026 {sgn(bcc[\"Run rate against FY2026\"])}, customer acquisition {sgn(bcc[\"Customer acquisition\"])}, prepaid {sgn(bcc[\"Prepaid\"])}, bucket migration {sgn(bcc[\"Bucket migration\"])}, load decline {sgn(bcc[\"Load decline\"])}, solar and net billing {sgn(bcc[\"Solar and net billing\"])}. Residential is modelled at class level, so there is no customer split. The evidence is in Sections 4, 5 and 7.'")

# drivers outside the base, after the FY2028 bridge
OUT = r'''
evm = {(r[0], r[1]): r[4] for r in RD['ev']}
ev_oct = evm[(2026, 10)]; ev_slope = float(np.polyfit(range(10), [evm[(2026, m)] for m in range(1, 11)], 1)[0])
ev27_rr = ev_oct * 12 / 1e6; ev27_tr = sum(ev_oct + ev_slope * k for k in range(3, 15)) / 1e6
add('<h3>Drivers held outside the base</h3><table><colgroup><col style="width:17%"><col style="width:12%"><col></colgroup><tr><th class="l">Driver</th><th>FY2027 GWh</th><th class="l">Why it is not in the base</th></tr>')
add(f'<tr><td>Weather</td><td class="pos">+{res_base * 0.0193 * 0.2:.0f}</td><td class="l" style="font-size:11px">The 7 September report carried +7.1 from a temperature outlook we no longer have. A strong El Ni&ntilde;o through February 2027 points the same way, so we size it as upside. Section 6.</td></tr>')
add(f'<tr><td>EV chargers (EV44)</td><td class="pos">+{ev27_rr:.1f} to +{ev27_tr:.1f}</td><td class="l" style="font-size:11px">Counted in sales from the October load, after Finance confirmed the billing report flags these accounts as not billed in error. Earlier months are not reloaded yet, so the base does not carry them. Section 7.2.</td></tr>')
add('<tr><td>Government net billing expansion</td><td class="neg">&minus;14 to &minus;15 per 10 MW</td><td class="l" style="font-size:11px">A further 100 MW is planned and talks with JPS on a higher threshold and storage are open, with no dates. Section 7.</td></tr></table>')
'''
rep("movement(28, BC28, C28, 27, 28, ('3. FY2027 to FY2028 Movement by Driver', ''))", "movement(28, BC28, C28, 27, 28, ('3. FY2027 to FY2028 Movement by Driver', ''))\nres_base = T['RT10'][27] + EV['rt20r_27']\nimport numpy as np\n" + OUT)

# ---------- 2. section 5 ----------
a = "The difference, {g27 - EV[\"acq_net\"]:+.0f} GWh, is the load decline in 5.3 net of households moving into higher bands. Each 1% on RT10 is {T[\"RT10\"][27] / 100:.1f} GWh."
b = "In the bridge that growth is split into customer acquisition ({RL27[\"Customer acquisition\"]:+.1f}), prepaid ({RL27[\"Prepaid\"]:+.1f}), load decline ({RL27[\"Load decline\"]:+.1f}), solar and net billing ({RL27[\"Solar and net billing\"]:+.1f}) and bucket migration ({RL27[\"Bucket migration\"]:+.1f}). Migration is the balancing line, as it was in the 7 September report: it takes whatever the other four leave, so it moves when any of them is re-measured. Each 1% on RT10 is {T[\"RT10\"][27] / 100:.1f} GWh."
rep(a, b)
rep("We do not book it as a separate line. It sits inside the net 0.8% growth, where it offsets part of the premises growth in 4.3.", "It is its own line in the bridge, carved out of the 0.8% net growth.")
rep("If the conversion programme accelerates, prepaid is the line to revisit.</p>')", "Prepaid is worth {RL27[\"Prepaid\"]:+.1f} GWh in FY2027 at 0.8% on about {pp_run:.0f} GWh a year. If the conversion programme accelerates, prepaid is the line to revisit.</p>')")

STORM = r'''
add('<h3>5.5 The storm gap in RT10</h3>')
add('<p>The run-rate line is the largest in the bridge, so the evidence for it matters. RT10 ran well below the same month of 2025 through the storm and has been above it since mid-year:</p>')
r10m = {(r[0], r[1]): (r[2], r[3]) for r in EV['rt10']}
add('<table><tr><th class="l">RT10</th>' + ''.join(f'<th>{MONL[m - 1]}</th>' for m in range(1, 11)) + '</tr>')
add('<tr><td>2025 GWh</td>' + ''.join(f'<td>{r10m[(2025, m)][1]:,.1f}</td>' for m in range(1, 11)) + '</tr><tr><td>2026 GWh</td>' + ''.join(f'<td>{r10m[(2026, m)][1]:,.1f}</td>' for m in range(1, 11)) + '</tr>')
add('<tr><td>Change</td>' + ''.join(f'<td class="{cls(r10m[(2026, m)][1] / r10m[(2025, m)][1] * 100 - 100)}">{r10m[(2026, m)][1] / r10m[(2025, m)][1] * 100 - 100:+.1f}%</td>' for m in range(1, 11)) + '</tr>')
add('<tr><td>Premises 2026</td>' + ''.join(f'<td>{r10m[(2026, m)][0]:,}</td>' for m in range(1, 11)) + '</tr></table>')
h1 = sum(r10m[(2025, m)][1] for m in range(1, 7)) - sum(r10m[(2026, m)][1] for m in range(1, 7))
add(f'<p>January to June 2026 is {h1:,.0f} GWh below January to June 2025 with {r10m[(2026, 6)][0] - r10m[(2025, 6)][0]:,} more premises on the system. That shortfall is what the FY2027 run rate recovers.</p>')
'''
rep("add('<h3>5.4 Prepaid</h3>')", "add('<h3>5.4 Prepaid</h3>')")
rep("# ================= 6 =================", STORM + "\n# ================= 6 =================")

# ---------- 3. section 7 ----------
i = s.index("add(f'<p>The forecast has no separate solar line."); j = s.index("# ================= 8 =================")
SEC7 = r'''
add('<h3>7.1 Registered net billers and what they take off</h3>')
add('<p>The table above counts bills that net to a credit in the month. It also catches reversed and cancelled bills, so it is not a count of solar customers. The registered net billers, the accounts on the net billing tariffs (NB10, NB20 and NB40), are a steadier measure:</p>')
mm = [m for m in range(1, 11)]
add('<table><tr><th class="l">Registered net billers</th>' + ''.join(f'<th>{MONL[m - 1]}-26</th>' for m in mm) + '</tr>')
for t_ in ('NB10', 'NB20', 'NB40'): add(f'<tr><td>{t_} accounts</td>' + ''.join(f'<td>{nbm[(2026, m)][t_][0]:,}</td>' for m in mm) + '</tr>')
add('<tr><td>Billed net kWh (MWh)</td>' + ''.join(f'<td>{sum(nbm[(2026, m)][t_][1] for t_ in ("NB10", "NB20", "NB40")) / 1e3:,.0f}</td>' for m in mm) + '</tr>')
add('<tr><td>Exported kWh (MWh)</td>' + ''.join(f'<td>{sum(nbm[(2026, m)][t_][2] for t_ in ("NB10", "NB20", "NB40")) / 1e3:,.0f}</td>' for m in mm) + '</tr></table>')
ex26 = sum(sum(nbm[(2026, m)][t_][2] for t_ in ('NB10', 'NB20', 'NB40')) for m in mm); ex25 = sum(sum(nbm[(2025, m)][t_][2] for t_ in ('NB10', 'NB20', 'NB40')) for m in mm)
n26 = sum(nbm[(2026, 10)][t_][0] for t_ in ('NB10', 'NB20', 'NB40')); n25 = sum(nbm[(2025, 10)][t_][0] for t_ in ('NB10', 'NB20', 'NB40')); n24 = sum(nbm[(2024, 10)][t_][0] for t_ in ('NB10', 'NB20', 'NB40'))
add(f'<p>Registered net billers are {n26:,} against {n25:,} a year ago ({(n26 / n25 - 1) * 100:+.1f}%) and {n24:,} two years ago, of which NB10 residential is {nbm[(2026, 10)]["NB10"][0]:,} ({nb10_adds:+,} in the year). Exports from January to October are {ex26 / 1e6:,.2f} GWh against {ex25 / 1e6:,.2f} in 2025 ({(ex26 / ex25 - 1) * 100:+.0f}%). The registered book is growing slowly and exporting no more, so the visible solar effect is small. The risk is self-consumption, which never shows as export.</p>')
add(f'<p><b>What the bridge carries.</b> {nb10_adds} new NB10 accounts at {exp_acct:,.0f} kWh exported a year each, with self-consumption at {SOLAR_X:.0f} times the export (the ratio the 7 September report used), takes {abs(sol):.1f} GWh off RT10 in each year. This is the most judgemental number in the residential bridge. Every additional 500 net billers at the {EV["kwh_per_nb"]:,.0f} kWh a month seen in the credit bucket is about {500 * EV["kwh_per_nb"] * 12 / 1e6:.1f} GWh a year.</p>')
add('<p>Commercial solar is handled account by account: PAC (4 MW), MBJ (6 MW), Sutherland (100 kW) and the other KAM entries in Section 9. The Government plans a further 100 MW through a strengthened net billing programme, which would take roughly 14 to 15 GWh a year off for every 10 MW, and has opened talks with JPS on a higher net billing threshold and battery storage. None of that is in the base.</p>')
add('<h3>7.2 EV chargers (EV44)</h3>')
evr = {(r[0], r[1]): r for r in RD['ev']}
add('<table><tr><th class="l">EV44</th><th>Oct-24</th><th>Oct-25</th>' + ''.join(f'<th>{MONL[m - 1]}-26</th>' for m in range(1, 11)) + '</tr>')
add('<tr><td>Accounts with usage</td><td>' + f'{evr[(2024, 10)][3]}</td><td>{evr[(2025, 10)][3]}</td>' + ''.join(f'<td>{evr[(2026, m)][3]}</td>' for m in range(1, 11)) + '</tr>')
add('<tr><td>kWh (MWh)</td><td>' + f'{evr[(2024, 10)][4] / 1e3:,.1f}</td><td>{evr[(2025, 10)][4] / 1e3:,.1f}</td>' + ''.join(f'<td>{evr[(2026, m)][4] / 1e3:,.1f}</td>' for m in range(1, 11)) + '</tr></table>')
ev_jan_sep = sum(evm[(2026, m)] for m in range(1, 10)) / 1e6
add(f'<p>EV44 is the electric vehicle charging tariff. All {evr[(2026, 10)][3]} accounts are in the name of Jamaica Public Service. The billing details report flags them as not billed, which dropped them from our sales load; Finance has confirmed that is an error and they are billed. They are in sales from the October load: {ev_oct / 1e3:,.1f} MWh, against {evm[(2025, 10)] / 1e3:,.1f} a year earlier. Use has grown about {ev_slope / 1e3:,.1f} MWh a month through 2026.</p>')
add(f'<p><b>What the forecast carries.</b> Months before October are not reloaded yet. January to September 2026 holds {ev_jan_sep:,.2f} GWh of EV44 that is missing from the FY2026 outlook, and the August to October base counts it only through October, so we treat FY2027 and FY2028 as excluding it. At the October rate it is worth {ev27_rr:.1f} GWh a year, and {ev27_tr:.1f} GWh in FY2027 if the 2026 trend continues. The trend is a straight line through ten months and is the least evidenced number in this section. It is a small number in a 3,400 GWh year, but it has grown five times in twelve months and it will show up in the year-on-year comparison.</p>')
'''
s = s[:i] + SEC7 + "\n" + s[j:]
# moved: ev27_rr/ev27_tr/evm are defined after the FY2028 bridge, which comes before section 7, so they are available here
rep("add('<h2>7. Solar and Net Billing</h2>')", "add('<h2>7. Solar, Net Billing and EV Chargers</h2>')")

# ---------- 4. open items ----------
rep("<p><b>Open items.</b> Reopening dates", "<p><b>Open items.</b> Reloading EV44 for the months before October. Reopening dates")
open(p, 'w', encoding='utf-8').write(s); print('res patch applied')
