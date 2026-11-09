# -*- coding: utf-8 -*-
# Page 7 of the October analysis: carry the refreshed FY2027 forecast in the landing table and the view on 2027.
p = '_build_deep_oct.py'; s = open(p, encoding='utf-8').read()

# 1. table: replace "vs LE / vs outlook" with "FY27 forecast / vs plan"
s = s.replace("<th>FY27 plan</th><th>vs LE</th><th>vs outlook</th></tr>", "<th>FY27 plan</th><th>FY27 forecast</th><th>vs plan</th></tr>")
old = """<td>{f27:,.1f}</td><td>{chgp(g1)}</td><td style="font-weight:bold">{chgp(g2)}</td></tr>' for i, (c, le, pj, d_, f27, g1, g2, q) in enumerate(rows_o))"""
new = """<td>{f27:,.1f}</td><td style="font-weight:bold">{NF[c]["fy27"]:,.1f}</td><td style="color:{col(NF[c]["fy27"] - f27)};font-weight:bold">{chg(NF[c]["fy27"] - f27, 1)}</td></tr>' for i, (c, le, pj, d_, f27, g1, g2, q) in enumerate(rows_o))"""
assert old in s; s = s.replace(old, new)
old = """<td>{sums["27"]:,.1f}</td><td>{chgp(pc(sums["27"], sums["le"]))}</td><td>{chgp(pc(sums["27"], sums["proj"]))}</td></tr>'"""
new = """<td>{sums["27"]:,.1f}</td><td>{TF27:,.1f}</td><td>{chg(TF27 - sums["27"], 1)}</td></tr>'"""
assert old in s; s = s.replace(old, new)
s = s.replace("orow = ''.join(", "NF = json.load(open('_fy27_byclass.json')); TF27 = sum(NF[c]['fy27'] for c in ORD)\norow = ''.join(", 1)
s = s.replace("The outlook is January to October actual, with November and December run from October's level and 2024's October to December pattern for each class (RT70 held flat). It rests on one year's pattern, so treat it as an indication, not a forecast.",
              "The outlook is January to October actual, with November and December run from October's level and 2024's October to December pattern for each class. FY27 forecast is our refreshed account-level view, which the KAMs are reviewing. The plan is the approved FY2027 budget.")

# 2. verdict
i = s.index('<div class="verdict" style="margin-top:3mm"><b>Is it sustainable through 2027?</b>')
j = s.index('GWh in 2027.</div>', i) + len('GWh in 2027.</div>')
new_v = '''<div class="verdict" style="margin-top:3mm"><b>Is it sustainable through 2027?</b> On our refreshed account-level forecast, yes in total: FY2027 lands at {TF27:,.0f} GWh against the plan's {sums["27"]:,.1f}, with a different mix. <b>Residential:</b> {NF["RT10"]["fy27"]:,.0f} GWh against {r10[4]:,.0f} planned. The {chgp(r10[6])} needed on where we expect FY2026 to finish is mostly the first half of 2026 returning to normal. From the August to October run rate with 0.8% growth we reach the plan, so it does not depend on new growth. The risk is that the second-half 2026 level does not hold, and the {z["2026-10"] - z["2025-10"]:,} zero-consumption premises coming back would add about {zret * 100:.1f}% of RT10. <b>Commercial:</b> the four classes together are {abs(com_d):.0f} GWh {"below" if com_d < 0 else "above"} plan. RT50 is {abs(d50):.0f} GWh below because we recover hotels property by property, RT70 is {abs(d70):.0f} GWh above (about 5 GWh of it from taking MBJ at 47% off rather than the KAM's 77%) and RT40 is {d40:.0f} GWh above. That depends on the hotels reopening on schedule (1,982 rooms in December and 2,524 in the first half of 2027) and no further customers moving to self-generation. Each 1% on residential is {r10[4] / 100:.1f} GWh in 2027.</div>'''
s = s[:i] + new_v + s[j:]
# 3. variables used by the verdict
s = s.replace("res_gap = sum(r[3] for r in rows_o", "com_d = sum(NF[c]['fy27'] - [r for r in rows_o if r[0] == c][0][4] for c in ('RT40', 'RT50', 'RT60-ST', 'RT70')); d50 = NF['RT50']['fy27'] - [r for r in rows_o if r[0] == 'RT50'][0][4]; d70 = NF['RT70']['fy27'] - [r for r in rows_o if r[0] == 'RT70'][0][4]; d40 = NF['RT40']['fy27'] - [r for r in rows_o if r[0] == 'RT40'][0][4]\nres_gap = sum(r[3] for r in rows_o", 1)
open(p, 'w', encoding='utf-8').write(s); print('patched')
