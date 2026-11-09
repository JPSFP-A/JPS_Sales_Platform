# -*- coding: utf-8 -*-
# Weather and EV chargers are in the base: bridge lines, section 6, section 7.2 and the market table.
p = '_build_driver_report_nov2.py'; s = open(p, encoding='utf-8').read()
def rep(old, new):
    global s
    if s.count(old) != 1: raise SystemExit('match count %d: %s' % (s.count(old), old[:100]))
    s = s.replace(old, new)

# ---------- bridge: carve the overlays out of RT10 and RT20, add Weather and EV chargers ----------
a = s.index("RESK = ['Customer acquisition'"); b = s.index("movement(27, BC27, C27")
NEW = r'''RESK = ['Customer acquisition', 'Prepaid', 'Bucket migration', 'Load decline', 'Solar and net billing']
OV = CLSJ['overlay']; evm = {(r[0], r[1]): r[4] for r in RD['ev']}
W10_27, W20_27, W10_28, W20_28 = OV['wx10_27'], OV['wx20_27'], OV['wx10_28'], OV['wx20_28']
E26 = (sum(evm[(2026, m)] for m in range(1, 11)) + 2 * evm[(2026, 10)]) / 1e6                                 # FY2026 outlook: reloaded actuals plus November and December at the October level
EB27 = ((evm[(2026, 8)] + evm[(2026, 9)]) / 2 * 9 + evm[(2026, 10)] * 3) * 1.008 / 1e6; EB28 = EB27 * 1.008      # in the August to October base
EO27, EO28 = OV['ev_ov_27'], OV['ev_ov_28']                                                                    # the monthly trend on top
EVL27 = (EB27 - E26) + EO27; EVL28 = (EB28 - EB27) + (EO28 - EO27)
# FY2027: RT10 growth and run rate on the base excluding the overlays; EV in the base is carved out of the run rate
t27b = T['RT10'][27] - W10_27 - EO27; g27b = t27b * 0.008 / 1.008
BC27['RT10']['Growth'] = g27b; BC27['RT10']['Run rate against FY2026'] = t27b - g27b - T['RT10'][26] - (EB27 - E26)
BC27['RT20']['Run rate against FY2026'] -= W20_27
BC28['RT10']['Growth'] = T['RT10'][28] - T['RT10'][27] - (W10_28 - W10_27) - (EO28 - EO27) - (EB28 - EB27)
BC28['RT20']['Growth'] -= (W20_28 - W20_27)
def reslines(g, acq):
    L = {'Customer acquisition': acq, 'Prepaid': pp_run * 0.008, 'Load decline': -EV['decl_gwh'], 'Solar and net billing': sol}
    L['Bucket migration'] = g - sum(L.values()); return L
RL27 = reslines(BC27['RT10']['Growth'], EV['acq_net'])
RL28 = reslines(BC28['RT10']['Growth'], EV['add10'] * EV['kpp10'] * 12 / 1e6)
def resplit(bc, RL, wx, ev):
    b2 = {c: {**bc[c], **{k: 0.0 for k in RESK + ['Weather', 'EV chargers']}} for c in CL}
    b2['RT10']['Growth'] = 0.0
    for k in RESK: b2['RT10'][k] = RL[k]
    b2['RT10']['Weather'] = wx[0]; b2['RT20']['Weather'] = wx[1]; b2['RT10']['EV chargers'] = ev
    return b2
BC27, BC28 = resplit(BC27, RL27, (W10_27, W20_27), EVL27), resplit(BC28, RL28, (W10_28 - W10_27, W20_28 - W20_27), EVL28)
for tr, bc in ((27, BC27), (28, BC28)):
    for c in CL:
        d = T[c][tr] - T[c][tr - 1]; s_ = sum(bc[c].values()); assert abs(d - s_) < 0.05, ('residential drivers do not tie', tr, c, d, s_)
for k in RESK + ['Weather', 'EV chargers']: C27[k] = 0.0; C28[k] = 0.0
DR = ['Run rate against FY2026'] + RESK + ['Weather', 'EV chargers', 'Growth', 'Hotel recovery', 'Defections and self-generation', 'Expansions', 'Planned outages and other', 'Pipeline customers']
DRL.update({
  'Customer acquisition': ('RT10', 'Premises joining the grid at about 820 a month (+1.5% a year), each using the FY2026 average. Section 4.'),
  'Prepaid': ('RT10', 'Prepaid volume growing with RT10 at 0.8%. Observed growth is far higher but is mostly postpaid customers converting. Section 5.4.'),
  'Bucket migration': ('RT10', 'Households moving up the consumption bands. It is the balancing driver inside the 0.8% growth, so it moves when acquisition, load decline or solar are re-measured. Section 5.2.'),
  'Load decline': ('RT10', 'Conservation and tariff response at the two ends of the book: under 150 kWh and over 950 kWh. Section 5.3.'),
  'Solar and net billing': ('RT10', 'Registered net billers added over the year, at what each exports and what it self-consumes. Section 7.'),
  'Weather': ('RT10, RT20 residential', 'A temperature anomaly over the 2023-2025 mean at 1.93% of residential load per degree. A very strong El Niño is expected through February 2027. In FY2028 the anomaly falls back to a flat 0.09C. Section 6.'),
  'EV chargers': ('RT10', 'EV44 charging accounts, now counted in sales: the August to October level in the base and the 2026 monthly trend on top. Section 7.2.'),
  'Growth': ('Commercial and RT20', 'RT20 grows 0.8% a year and commercial 1% from April 2027. In FY2028 commercial grows another 1%.')})
'''
s = s[:a] + NEW + "\n" + s[b:]

# the old "held outside the base" block: keep only the net billing expansion
i = s.index("evm = {(r[0], r[1]): r[4] for r in RD['ev']}\nev_oct"); j = s.index("# ================= 4 =================")
HELD = r'''ev_oct = evm[(2026, 10)]
add('<h3>Drivers held outside the base</h3><table><colgroup><col style="width:22%"><col style="width:16%"><col></colgroup><tr><th class="l">Driver</th><th>FY2027 GWh</th><th class="l">Why it is not in the base</th></tr>')
add('<tr><td>Government net billing expansion</td><td class="neg">&minus;14 to &minus;15 per 10 MW</td><td class="l" style="font-size:11px">A further 100 MW is planned and talks with JPS on a higher threshold and storage are open, with no dates. Section 7.</td></tr>')
add(f'<tr><td>Weather: a normal year</td><td class="neg">&minus;{W10_27 + W20_27:.0f}</td><td class="l" style="font-size:11px">The base carries the anomaly in the 7 September report. If 2027 comes in at the 2023-2025 average, this comes out. Section 6.</td></tr></table>')

'''
s = s[:i] + HELD + s[j:]

# ---------- section 6 ----------
i = s.index("add(f'<div class=\"gap\">The forecast has no weather overlay."); j = s.index("# ================= 7 =================")
SEC6 = r'''add(f'<div class="key">Temperature is in the base: {W10_27 + W20_27:+.1f} GWh in FY2027 (RT10 {W10_27:+.1f}, RT20 residential {W20_27:+.1f}) and {W10_28 + W20_28:+.1f} in FY2028. It is a forecast island-wide temperature anomaly against the 2023-2025 mean, converted to load at a constant 1.93% of residential load per degree Celsius.</div>')
add('<table><tr><th class="l">FY2027</th>' + ''.join(f'<th>{m}</th>' for m in MONL) + '</tr><tr><td>Anomaly, &deg;C above 2023-2025</td>' + ''.join(f'<td>{v:.3f}</td>' for v in (0.262, 0.270, 0.367, 0.252, 0.289, 0.177, 0.153, 0.133, 0.133, 0.097, 0.112, 0.068)) + '</tr><tr><td>Applied to load, % a month</td>' + ''.join(f'<td>{v * 1.93:.3f}</td>' for v in (0.262, 0.270, 0.367, 0.252, 0.289, 0.177, 0.153, 0.133, 0.133, 0.097, 0.112, 0.068)) + '</tr></table>')
add(f'<p>The profile and the sensitivity are the ones in the 7 September report. The market view supports a warm start to 2027: the WMO said on 3 September that El Ni&ntilde;o is firmly established, will strengthen to a very strong event peaking late in 2026 and is almost certain to last through February 2027. That fits an anomaly that is largest in the first quarter and fades through the year. Each 0.1&deg;C is worth about {res_base * 0.0193 * 0.1:.1f} GWh across RT10 and RT20 residential, so if 2027 comes in at the 2023-2025 average the {W10_27 + W20_27:.0f} GWh comes out.</p>')
add(f'<div class="note">FY2028 is a flat 0.090&deg;C in every month, {W10_28 + W20_28:.1f} GWh. Twelve identical months is not what weather does. It is a placeholder in the absence of a second-year outlook and the least evidenced number in the bridge. We have no temperature outlook for Jamaica of our own and the platform holds no temperature series to test the sensitivity against.</div>')

'''
s = s[:i] + SEC6 + s[j:]

# ---------- section 7.2 ----------
i = s.index("ev_jan_sep = sum(evm"); j = s.index("# ================= 8 =================")
SEC72 = r'''ev_slope = OV['ev_slope_kwh']
add(f'<p>EV44 is the electric vehicle charging tariff. All {evr[(2026, 10)][3]} accounts are in the name of Jamaica Public Service. The billing details report flags them as not billed, which dropped them from our sales load; Finance has confirmed that is an error and they are billed. They are now in sales, reloaded back to January 2025, which is where the RT10 history starts: {ev_oct / 1e3:,.1f} MWh in October against {evm[(2025, 10)] / 1e3:,.1f} a year earlier. Use has grown about {ev_slope / 1e3:,.1f} MWh a month through 2026.</p>')
add(f'<p><b>What the forecast carries.</b> The August to October level, about {(evm[(2026, 8)] + evm[(2026, 9)] + evm[(2026, 10)]) / 3 / 1e3:,.0f} MWh a month, is in the base. On top of it the 2026 trend continues, which adds {EO27:.1f} GWh in FY2027 and {EO28:.1f} in FY2028. EV44 is {E26:.1f} GWh in the FY2026 outlook, {EB27 + EO27:.1f} in FY2027 and {EB28 + EO28:.1f} in FY2028. The trend is a straight line through ten months and is the least evidenced number in this section. It is small in a 3,400 GWh year, but it has grown five times in twelve months.</p>')

'''
s = s[:i] + SEC72 + s[j:]

# ---------- market table, open items ----------
rep("'No weather overlay. A warmer year would lift residential load; we hold it as upside (Section 6).')", "'In the base as a temperature anomaly, worth about +' + str(round(CLSJ['overlay']['wx10_27'] + CLSJ['overlay']['wx20_27'])) + ' GWh in FY2027, largest in the first quarter (Section 6).')")
rep("<p><b>Open items.</b> Reloading EV44 for the months before October. Reopening dates", "<p><b>Open items.</b> EV44 before January 2025, which is before the RT10 history starts. Reopening dates")
open(p, 'w', encoding='utf-8').write(s); print('res2 patch applied')
