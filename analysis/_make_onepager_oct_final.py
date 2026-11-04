# -*- coding: utf-8 -*-
# Derives _build_onepager_oct_final.py (October one-pager with prepaid loaded) from the pre-prepaid builder, which is left untouched.
s = open('_build_onepager_oct.py', encoding='utf-8').read()
def rep(a, b):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, 1)

rep("BEFORE prepaid.", "with prepaid loaded.")
rep("def agg(y, m, rc=None, bucket_ne_prepaid=True, acct=None):", "def agg(y, m, rc=None, bucket_ne_prepaid=False, acct=None):")
rep("assert not any(x['year'] == 2026 and x['month'] == 10 and x['consumption_bucket'] == 'Prepaid' for x in rows), 'October prepaid is loaded: this page is the pre-prepaid view'",
    "pp_oct = {c: sum(f(x['kwh']) for x in rows if x['year'] == 2026 and x['month'] == 10 and x['rate_class'] == c and x['consumption_bucket'] == 'Prepaid') / 1e6 for c in ORDER}\nassert pp_oct['RT10'] > 0, 'October prepaid is not loaded'")
rep("bud_pre = {c: sum(f(x['kwh_budget']) for x in bag if x['month'] == 10 and x['year'] == 2026 and x['rate_class'] == c and x['consumption_bucket'] != 'Prepaid') / 1e6 for c in ORDER}\nfor c in ORDER: assert abs(bud_pre[c] + sum(f(x['kwh_budget']) for x in bag if x['month'] == 10 and x['year'] == 2026 and x['rate_class'] == c and x['consumption_bucket'] == 'Prepaid') / 1e6 - f(bc[c]['kwh_budget']) / 1e6) < 0.01, c",
    "bud_pre = {c: f(bc[c]['kwh_budget']) / 1e6 for c in ORDER}      # full budget, prepaid included")
rep("assert abs(o26 - 291.462) < 0.01, o26", "assert abs(o26 - 294.296) < 0.02, o26")
rep("<div class=\"sub\">Jamaica Public Service | before prepaid<br>", "<div class=\"sub\">Jamaica Public Service<br>")
dirw = "dirw = lambda v: 'above' if v >= 0 else 'below'\ns25_rt10 = agg(2025, 9, 'RT10')[0]\nrt10_mom, rt10_mom_ly = A['RT10']['o26'][0] / A['RT10']['s26'][0] - 1, A['RT10']['o25'][0] / s25_rt10 - 1\npp_sep_tot = prepaid_sep; pp_oct_tot = sum(pp_oct.values())\nalc_share = "
rep("alc_share = ", dirw)
rep("<div class=\"head\">Sales before prepaid were {o26:,.1f} GWh, {abs(o26 / o25 - 1) * 100:.1f}% above October last year and {abs(o26 / bud - 1) * 100:.1f}% above budget. The mass market carried the month while RT40 to RT70 ran {abs(com_var):.1f} GWh below budget, {alc_share * 100:.0f}% of it Alcoa.</div>",
    "<div class=\"head\">Sales were {o26:,.1f} GWh, {abs(o26 / o25 - 1) * 100:.1f}% {dirw(o26 - o25)} October last year, {abs(o26 / bud - 1) * 100:.1f}% {dirw(o26 - bud)} budget and {abs(o26 / le_tot - 1) * 100:.1f}% {dirw(o26 - le_tot)} the forecast. The mass market carried the month while RT40 to RT70 ran {abs(com_var):.1f} GWh below budget, {alc_share * 100:.0f}% of it Alcoa.</div>")
rep("October sales, before prepaid", "October sales")
rep("{chg((o26 / bud - 1) * 100)}% vs budget; {chg((o26 / le_tot - 1) * 100)}% vs LE ({chg((sum(est(c) for c in ORDER) / le_tot - 1) * 100)}% with prepaid)", "{chg((o26 / bud - 1) * 100)}% vs budget; {chg((o26 / le_tot - 1) * 100)}% vs LE; {chg(o26 - s26)} GWh on September")
rep("By rate class (GWh, before prepaid)", "By rate class (GWh)")
a = s.index('<div style="font-size:7.3pt;color:{GREY};margin-top:1.4mm">Budget and 2025')
b = s.index('</div></div>', a)
s = s[:a] + '<div style="font-size:7.3pt;color:{GREY};margin-top:1.4mm">Prepaid is included in every column: {pp_oct_tot:.1f} GWh in October against {pp_sep_tot:.1f} in September. The LE is the financials forecast held at 3,299.7 GWh for the year. The October 2025 base includes the late-October storm.' + s[b:]
rep("Variance vs forecast, before prepaid (GWh)", "Variance vs forecast (GWh)")
rep("Without prepaid, RT10 is also {abs(A[\"RT10\"][\"o26\"][0] / A[\"RT10\"][\"s26\"][0] - 1) * 100:.1f}% down on September, as it was last year.", "RT10 is {abs(rt10_mom) * 100:.1f}% {'down' if rt10_mom < 0 else 'up'} on September; last year it moved {chg(rt10_mom_ly * 100)}%.")
rep("The LE has RT10 at {LE[\"RT10\"]:.1f} GWh, {chgp(LE[\"RT10\"] / (A[\"RT10\"][\"s26\"][0] + pp[\"RT10\"]) - 1)} on September. It fell {abs(A[\"RT10\"][\"o26\"][0] / A[\"RT10\"][\"s26\"][0] - 1) * 100:.1f}% before prepaid, and last year it fell 4.0%. RT40 to RT70 beat the LE by {sum(A[c][\"o26\"][0] - LE[c] for c in big):.1f} GWh.",
    "RT10 came in at {A[\"RT10\"][\"o26\"][0]:.1f} GWh against an LE of {LE[\"RT10\"]:.1f} ({chgp(A[\"RT10\"][\"o26\"][0] / LE[\"RT10\"] - 1)}). The LE had RT10 {chgp(LE[\"RT10\"] / A[\"RT10\"][\"s26\"][0] - 1)} on September; it moved {chg(rt10_mom * 100)}%. RT40 to RT70 beat the LE by {sum(A[c][\"o26\"][0] - LE[c] for c in big):.1f} GWh.")
rep("   <li>RT10 net-export accounts", "   <li>Prepaid fell {abs(pp_oct_tot / pp_sep_tot - 1) * 100:.0f}% on September ({pp_oct_tot:.2f} vs {pp_sep_tot:.2f} GWh) with RT10 customers flat at about 18,000.</li>\n   <li>RT10 net-export accounts")
a = s.index('<div class="watch"><b>Not yet in these figures.</b>')
b = s.index('</div>', a) + len('</div>')
s = s[:a] + '<div class="watch"><b>Prepaid is in.</b> October prepaid is {pp_oct_tot:.2f} GWh ({pp_oct["RT10"]:.2f} RT10, {pp_oct["RT20"]:.2f} RT20), {abs(pp_oct_tot / pp_sep_tot - 1) * 100:.0f}% below September. The earlier estimate that assumed September\'s level was {pp_sep_tot - pp_oct_tot:.2f} GWh too high.</div>' + s[b:]
rep("October 2026, before prepaid</span>", "October 2026</span>")
rep("_onepager_JPS_OnePager_Sales_Analysis_Oct2026.html", "_onepager_JPS_OnePager_Sales_Analysis_Oct2026_Final.html")
open('_build_onepager_oct_final.py', 'w', encoding='utf-8').write(s)
print('wrote _build_onepager_oct_final.py')
