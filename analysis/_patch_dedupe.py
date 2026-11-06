# -*- coding: utf-8 -*-
import re
p = '_build_deep_oct.py'; s = open(p, encoding='utf-8').read()

# ---- page 7: drop the residential band table and the commercial movers table (now pages 5 and 4); shorter drivers ----
i = s.index('<div class="head">Residential fell {abs(res_oct / res_sep - 1)')
j = s.index('<div class="box" style="flex:1.1"><div class="sec">FY2026 landing')
new7 = '''<div class="head">Residential fell {abs(res_oct / res_sep - 1) * 100:.1f}% on September and commercial rose {abs(T["o26_COMM"] / T["s26_COMM"] - 1) * 100:.1f}%, about half of it Caribbean Broilers and Petrojam recovering from a low September. Neither is a trend, and the 2027 plan leans on both.</div>
<div class="row" style="margin-top:3mm"><div class="box items" style="flex:1"><div class="sec">What is driving the swing</div><ul>
<li><b>Residential vs September ({chg(res_oct - res_sep, 1)} GWh).</b> Seasonal and spread across the heavy-use buckets (page 5). It is deeper than the {chg((c24["2024-10"]["RT10"] / c24["2024-09"]["RT10"] - 1) * 100, 1)}% October move in 2024. The structural drag is small but real: {nb26:,.0f} net-export accounts against {nb25:,.0f} last October, exporting {abs(nbk26) * 1000:,.0f} MWh against {abs(nbk25) * 1000:,.0f}.</li>
<li><b>Residential vs the LE.</b> The LE has RT10 flat on September, while 2024 and 2025 both fall. That is phasing, not weakness, but it carries into November and December.</li>
<li><b>Commercial vs September ({chg(T["o26_COMM"] - T["s26_COMM"], 1)} GWh).</b> Caribbean Broilers (billing timing) and Petrojam (back after its September fire) are {chg(timing_g, 1)} GWh of it, {abs(timing_g / (tot_up + tot_dn)) * 100:.0f}%, so October is a normal month and not a step up (page 4). National Water Commission's {chg(mv["100012"]["10"] - mv["100012"]["9"], 1)} GWh is the one real rise: {mv["100012"]["10"]:.1f} GWh against {mv["100012"]["7"]:.1f} and {mv["100012"]["8"]:.1f} in July and August, with water supply {chgp(yoy("water", 10))} on last year. Whether it holds depends on pumping demand.</li></ul></div>
'''
s = s[:i] + new7 + s[j:]

# ---- Petrojam: September fire outage, not billing timing ----
s = s.replace("NOTE = {'RT40|100058': 'Billing timing', 'RT70|101188': 'Billing timing'", "NOTE = {'RT40|100058': 'Billing timing', 'RT70|101188': 'Back after September fire outage'")
s = s.replace("Petrojam ({smw((pet[\"o26\"] - pet[\"s26\"]) / 1000)} MWh) are billing timing, and Alcoa", "Petrojam ({smw((pet[\"o26\"] - pet[\"s26\"]) / 1000)} MWh) are not growth: Broilers is billing timing and Petrojam is back after its September fire. Alcoa")
s = s.replace("A handful of accounts explain the commercial movement. Caribbean Broilers", "A handful of accounts explain the commercial movement. Caribbean Broilers")
s = s.replace("{smw((alc[\"o26\"] - alc[\"s26\"]) / 1000)} MWh) has left the grid.", "{smw((alc[\"o26\"] - alc[\"s26\"]) / 1000)} MWh) has left the grid.")
s = s.replace("Petrojam's +0.9 GWh on September is timing. PAC's solar", "Petrojam is back after its September fire. PAC's solar")
s = s.replace(" That is billing timing, not growth. Petrojam does the same for Kingston South ({chg(mv[\"101188\"][\"10\"] - mv[\"101188\"][\"9\"], 1)} GWh).", " That is billing timing, not growth. Kingston South also gains from Petrojam returning after its September fire ({chg(mv[\"101188\"][\"10\"] - mv[\"101188\"][\"9\"], 1)} GWh).")
s = s.replace("TIMING = ('Caribbean Broilers', 'Petrojam')", "TIMING = ('Caribbean Broilers', 'Petrojam')   # September lows that reverse in October: Broilers billing timing, Petrojam fire outage")
s = s.replace("tag = 'billing timing' if any(t in nm for t in TIMING)", "tag = ('fire outage in Sep' if 'Petrojam' in nm else 'billing timing') if any(t in nm for t in TIMING)")

# ---- page 3: class bullets point to page 4 for names instead of repeating them ----
a = s.index('<li><b>Residential.</b> Down {abs(pc(cv["RT10"]["o26"]')
b = s.index('</ul></div></div></div>', a)
newb = '''<li><b>Residential.</b> Down {abs(pc(cv["RT10"]["o26"], cv["RT10"]["s26"])) * 100:.1f}% on September in the heavy-use buckets (page 5). The LE holds October flat on September, so the {abs(pc(cv["RT10"]["o26"], cv["RT10"]["le"])) * 100:.1f}% gap to the LE is phasing.</li>
<li><b>RT20.</b> Back above its pre-storm level. About {catch20:.1f} GWh of October is catch-up billing that will not repeat. Without it the month is {chgp(rt20_underlying)} on last year.</li>
<li><b>RT40.</b> Two accounts, Caribbean Broilers and National Water Commission, are the whole movement on September (page 4). Catch-up bills add about {catch40:.2f} GWh.</li>
<li><b>RT50.</b> {chgp(pc(cv["RT50"]["o26"], cv["RT50"]["o25"]))} on last October is the storm base. Hotels are still {abs(yoy("hotels", 10)) * 100:.0f}% down, and West Meat Packers is falling ({wmp:.0f} MWh on September).</li>
<li><b>RT60.</b> Street lighting, steady at {cv["RT60-ST"]["o26"]:.1f} GWh a month.</li>
<li><b>RT70.</b> {abs(pc(cv["RT70"]["o26"], cv["RT70"]["o25"])) * 100:.0f}% below last October, which is Alcoa ({al26:.2f} GWh against {al25:.1f} a year ago, after a {al_cr:.1f} GWh billing credit). Petrojam is back after its September fire. PAC's solar is not yet in the bills ({pac:.2f} GWh).</li>'''
s = s[:a] + newb + s[b:]
# the same bullets sit in the class block definition; keep the builder and the block file in step
s = s.replace('mrow = []\nfor i, a in enumerate(AX):', 'mig_rows = []\nfor i, a in enumerate(AX):').replace("    mrow.append(f'<tr class=\"{\"alt\" if i % 2 else \"\"}\"><td class=\"l\">{BL.get(a, a)}</td>{\"\".join(cells)}", "    mig_rows.append(f'<tr class=\"{\"alt\" if i % 2 else \"\"}\"><td class=\"l\">{BL.get(a, a)}</td>{\"\".join(cells)}").replace("{''.join(mrow)}</table>\n<div class=\"small\">Shaded diagonal", "{''.join(mig_rows)}</table>\n<div class=\"small\">Shaded diagonal")
open(p, 'w', encoding='utf-8').write(s)
print('mrow refs:', len(re.findall(r'\bmrow\b', s)), 'mig_rows refs:', s.count('mig_rows'))
