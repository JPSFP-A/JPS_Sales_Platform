# -*- coding: utf-8 -*-
# Derives _build_onepager_oct_prepaid.py from the pre-prepaid October one-pager build: RT10 carries an assumed 3.0 GWh prepaid
# estimate (revenue at September's prepaid rate), and the budget / 2025 / September comparators include prepaid so every column is like for like.
d = open('_build_onepager_oct.py', encoding='utf-8').read()
def rep(a, b):
    global d
    assert a in d, a[:90]
    d = d.replace(a, b, 1)

rep("A = {c: {'o26': agg(2026, 10, c), 'o25': agg(2025, 10, c), 's26': agg(2026, 9, c)} for c in ORDER}",
    """PP_OCT = 3.0   # GWh, assumed until the October prepaid file is loaded (September carried 3.0)
pp_sep_k = sum(f(x['kwh']) for x in rows if x['year'] == 2026 and x['month'] == 9 and x['consumption_bucket'] == 'Prepaid') / 1e6
pp_sep_r = sum(f(x['revenue_jmd']) for x in rows if x['year'] == 2026 and x['month'] == 9 and x['consumption_bucket'] == 'Prepaid') / 1e6
PP_OCT_REV = pp_sep_r * PP_OCT / pp_sep_k   # J$M at September's prepaid rate per kWh
A = {c: {'o26': agg(2026, 10, c), 'o25': agg(2025, 10, c, False), 's26': agg(2026, 9, c, False), 's25': agg(2025, 9, c, False)} for c in ORDER}
A['RT10']['o26'] = (A['RT10']['o26'][0] + PP_OCT, A['RT10']['o26'][1] + PP_OCT_REV)""")
rep("T = lambda key, i: sum(A[c][key][i] for c in ORDER)", "bud_pre = {c: f(bc[c]['kwh_budget']) / 1e6 for c in ORDER}   # full-class budget, prepaid included\nT = lambda key, i: sum(A[c][key][i] for c in ORDER)")
rep("assert abs(o26 - 291.462) < 0.01, o26", "assert abs(o26 - (291.462 + PP_OCT)) < 0.01, o26")
rep("pp = {c: sum(f(x['kwh']) for x in rows if x['year'] == 2026 and x['month'] == 9 and x['rate_class'] == c and x['consumption_bucket'] == 'Prepaid') / 1e6 for c in ORDER}   # September prepaid, used only as the estimate",
    "pp = {c: 0.0 for c in ORDER}   # the prepaid estimate is already inside A['RT10']")
rep("Jamaica Public Service | before prepaid<br>", "Jamaica Public Service | prepaid estimated at {PP_OCT:.1f} GWh<br>")
rep('<div class="head">Sales before prepaid were {o26:,.1f} GWh, {abs(o26 / o25 - 1) * 100:.1f}% above October last year and {abs(o26 / bud - 1) * 100:.1f}% above budget. The mass market carried the month while RT40 to RT70 ran {abs(com_var):.1f} GWh below budget, {alc_share * 100:.0f}% of it Alcoa.</div>',
    '<div class="head">Sales were {o26:,.1f} GWh including a {PP_OCT:.1f} GWh prepaid estimate, {abs(o26 / o25 - 1) * 100:.1f}% {"above" if o26 >= o25 else "below"} October last year and {abs(o26 / bud - 1) * 100:.1f}% {"above" if o26 >= bud else "below"} budget. The mass market carried the month while RT40 to RT70 ran {abs(com_var):.1f} GWh {"below" if com_var < 0 else "above"} budget{f", {alc_share * 100:.0f}% of it Alcoa" if com_var < 0 else ""}.</div>')
rep('October sales, before prepaid', 'October sales, incl. prepaid estimate')
rep(' ({chg((sum(est(c) for c in ORDER) / le_tot - 1) * 100)}% with prepaid)', '')
rep('Average rate J${rate26:,.1f} per kWh, {chgp(rate26 / rate25 - 1)} on 2025', 'Average rate J${rate26:,.1f} per kWh, {chgp(rate26 / rate25 - 1)} on 2025; prepaid at September rate')
rep('By rate class (GWh, before prepaid)', 'By rate class (GWh, prepaid estimated in RT10)')
rep("Budget and 2025 are shown without prepaid; the LE includes it. Prepaid is not yet loaded for October (September carried {prepaid_sep:.1f} GWh). With that added, RT10 is {chg(est('RT10') - LE['RT10'])} GWh ({chgp(est('RT10') / LE['RT10'] - 1)}) against the LE and the system {chg(sum(est(c) for c in ORDER) - le_tot)} GWh ({chgp(sum(est(c) for c in ORDER) / le_tot - 1)}). The October 2025 base includes the late-October storm.",
    "Everything is billed except RT10 prepaid. The October prepaid file is not loaded, so {PP_OCT:.1f} GWh is assumed (September carried {prepaid_sep:.1f} GWh) and its revenue is estimated at September's rate. Budget, LE and 2025 all include prepaid. The October 2025 base includes the late-October storm.")
rep('Variance vs forecast, before prepaid (GWh)', 'Variance vs forecast (GWh)')
rep('Without prepaid, RT10 is also {abs(A["RT10"]["o26"][0] / A["RT10"]["s26"][0] - 1) * 100:.1f}% down on September, as it was last year.',
    'RT10 is {abs(A["RT10"]["o26"][0] / A["RT10"]["s26"][0] - 1) * 100:.1f}% {"below" if A["RT10"]["o26"][0] < A["RT10"]["s26"][0] else "above"} September with prepaid held at {PP_OCT:.1f} GWh; last year it moved {chg((A["RT10"]["o25"][0] / A["RT10"]["s25"][0] - 1) * 100)}%.')
rep('It fell {abs(A["RT10"]["o26"][0] / A["RT10"]["s26"][0] - 1) * 100:.1f}% before prepaid, and last year it fell 4.0%.',
    'It moved {chg((A["RT10"]["o26"][0] / A["RT10"]["s26"][0] - 1) * 100)}% on September (prepaid assumed at {PP_OCT:.1f} GWh); last year it moved {chg((A["RT10"]["o25"][0] / A["RT10"]["s25"][0] - 1) * 100)}%.')
rep("<b>Not yet in these figures.</b> October prepaid and the prepaid-tagged adjustments (about {prepaid_sep:.1f} GWh and J$180M a month at September's level) are not loaded, so system sales will rise when they are.",
    "<b>Estimate to replace.</b> October prepaid ({PP_OCT:.1f} GWh assumed, about J${PP_OCT_REV:,.0f}M at September's rate) is not loaded. Each 0.1 GWh moves system sales by {0.1 / o26 * 100:.2f}%; the page is rebuilt when the file arrives.")
rep('October 2026, before prepaid</span>', 'October 2026, prepaid estimated</span>')
rep("'_onepager_JPS_OnePager_Sales_Analysis_Oct2026.html'", "'_onepager_JPS_OnePager_Sales_Analysis_Oct2026_Prepaid.html'")
open('_build_onepager_oct_prepaid.py', 'w', encoding='utf-8').write(d)
print('ok')
