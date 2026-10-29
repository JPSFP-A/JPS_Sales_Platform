# -*- coding: utf-8 -*-
d = open('cr_build.py', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global d
    assert a in d, a[:80]
    d = d.replace(a, b, cnt)

rep("(Sep2026)_v3.pptx", "(Sep2026)_v4.pptx")

# ---- sales slide: drop September Acc column, trim commentary
rep("head1 = ['', 'September', '', '', '', '', 'January to September', '', '', '', '']", "head1 = ['', 'September', '', '', '', 'January to September', '', '', '', '']")
rep("head2 = ['Rate class', 'Actual', 'Budget', 'vs bud', 'vs 2025', 'Acc', 'Actual', 'Budget', 'vs bud', 'vs 2025', 'Acc']", "head2 = ['Rate class', 'Actual', 'Budget', 'vs bud', 'vs 2025', 'Actual', 'Budget', 'vs bud', 'vs 2025', 'Acc']")
rep("pct(a / p - 1), 'n/a' if ac0 is None else f'{ac0 * 100:.0f}%', f'{ya:.1f}'", "pct(a / p - 1), f'{ya:.1f}'")
rep("colors.append([None, None, None, col_(a / b - 1), col_(a / p - 1), None, None, None, col_(ya / yb - 1), col_(ya / yp - 1), None])", "colors.append([None, None, None, col_(a / b - 1), col_(a / p - 1), None, None, col_(ya / yb - 1), col_(ya / yp - 1), None])")
rep("pct(tot[0] / tot[2] - 1), f'{acc_tot[0] * 100:.0f}%*', f'{tot[3]:,.1f}'", "pct(tot[0] / tot[2] - 1), f'{tot[3]:,.1f}'")
rep("colors.append([None, None, None, col_(tot[0] / tot[1] - 1), col_(tot[0] / tot[2] - 1), None, None, None, col_(tot[3] / tot[4] - 1), col_(tot[3] / tot[5] - 1), None])", "colors.append([None, None, None, col_(tot[0] / tot[1] - 1), col_(tot[0] / tot[2] - 1), None, None, col_(tot[3] / tot[4] - 1), col_(tot[3] / tot[5] - 1), None])")
rep("[1.9, 0.62, 0.62, 0.66, 0.66, 0.5, 0.78, 0.78, 0.66, 0.66, 0.5]", "[1.9, 0.7, 0.7, 0.75, 0.75, 0.85, 0.85, 0.75, 0.75, 0.6]")
rep("t.cell(0, 1).merge(t.cell(0, 5)); t.cell(0, 6).merge(t.cell(0, 10))", "t.cell(0, 1).merge(t.cell(0, 4)); t.cell(0, 5).merge(t.cell(0, 9))")
rep("cell_set(t.cell(0, 1), 'September', 8, True, WHITE, PP_ALIGN.CENTER, NAVY); cell_set(t.cell(0, 6), 'January to September'", "cell_set(t.cell(0, 1), 'September', 8, True, WHITE, PP_ALIGN.CENTER, NAVY); cell_set(t.cell(0, 5), 'January to September'")
rep("    for j, per in ((5, 0), (10, 1)):", "    for j, per in ((9, 1),):")
rep("'Acc: account budget vs billing. *RT40-RT70. Jan-Feb budget = actuals, so YTD vs budget flatters.'", "'Acc: YTD account budget vs billing, RT40-RT70. Jan-Feb budget = actuals, so YTD vs budget flatters.'")
rep("extra = copy.deepcopy(wp[1]._p); wm.text_frame._txBody.append(extra)\nwp = wm.text_frame.paragraphs\nwp[3].runs[0].text = 'Cement is +7.3 GWh vs budget YTD, the largest gain by industry'\nfor r in wp[3].runs[1:]: r._r.getparent().remove(r._r)\n",
    "wp[1]._p.getparent().remove(wp[1]._p)\n")

# ---- dashboard: cut the Protect column to the outage figure and chart
rep("# ================= slide 5 =================", """for sid in range(12, 25): by_id(S1, sid)._element.getparent().remove(by_id(S1, sid)._element)
ch1 = by_id(S1, 11); ch1.height = Emu(1500000)
by_id(S1, 25).top = Emu(4500000)

# ================= slide 5 =================""")

# ---- growth slide: pipeline and new load only
growth = '''
# ================= growth slide: pipeline and new load only =================
S6 = prs.slides[5]
for sid in range(4, 22): by_id(S6, sid)._element.getparent().remove(by_id(S6, sid)._element)
set_text(by_id(S6, 2), 'COMMERCIAL  |  GROWTH & PIPELINE')
set_text(by_id(S6, 3), 'The 2027 pipeline is J$1.17B across 13 projects, led by NWC; 25.67 GWh of new load connects in 2026')
pn = by_id(S6, 22); pn.left = Emu(612648); pn.width = Emu(10972800); pn.height = Emu(4300000)
for sid in (23, 24, 25, 26):
    sh = by_id(S6, sid); sh.left = Emu(sh.left - 6199632)
by_id(S6, 27)._element.getparent().remove(by_id(S6, 27)._element)
for sid in (28, 29, 30, 31):
    sh = by_id(S6, sid); sh.left = Emu(sh.left - 795160); sh.top = Emu(sh.top - (1700784 if sid in (28, 29) else 1646512 if sid == 30 else 1150000))
for r in by_id(S6, 26).text_frame.paragraphs:
    for rn in r.runs: rn.font.size = Pt(13)
    r.space_after = Pt(6)
by_id(S6, 26).top = Emu(2500000)
tbl = by_id(S6, 30).table
for rw in tbl.rows:
    rw.height = Emu(400000)
    for c in rw.cells:
        for p in c.text_frame.paragraphs:
            for rn in p.runs: rn.font.size = Pt(11)
by_id(S6, 31).top = Emu(4700000)
for p in by_id(S6, 31).text_frame.paragraphs:
    for rn in p.runs: rn.font.size = Pt(11)
kg = by_id(S6, 32).text_frame.paragraphs[-1].runs
kg[0].text = 'Pipeline delivery: '
if len(kg) > 1: kg[1].text = "connect the six 2026 projects on time and secure NWC's 2027 load against its solar programme"
for r in kg[2:]: r._r.getparent().remove(r._r)
'''
rep("# ================= new slide: revenue and retention =================", growth + "\n# ================= new slide: revenue and retention =================")

# ---- revenue slide
i0 = d.index("tiles = [(f'J${nf26 / 1e9:.1f}bn'")
i1 = d.index("tb(SA, 612648, 5320000")
rev = '''def fixn(n):
    n = n.strip()
    if n.isupper(): n = n.title()
    for a, b in [('Commissio', 'Commission'), ('Jamaica Broilers Group L', 'Jamaica Broilers Group'), ('Terminal Li', 'Terminal Ltd'), ('Jamaican Reso', 'Jamaican Resorts'), ('Power Comp', 'Power Company'),
                 ('Aggregates Limi', 'Aggregates Ltd'), ('Alcoa Mins Of Ja Ltd', 'Alcoa Minerals of Jamaica'), ('Caribbean Cement Co Ltd', 'Caribbean Cement'), ('Restaurants Of Jam Ltd', 'Restaurants of Jamaica'),
                 ('Properties Limite', 'Properties Ltd'), ('Ja Ltd', 'Jamaica'), ('Co Ltd', 'Co')]:
        n = n.replace(a, b)
    return n
tiles = [(f'J${nf26 / 1e9:.1f}bn', 'non-fuel revenue, January to September', pct(nf26 / nf25 - 1)), (f'{k26 / 1e6:,.0f} GWh', 'volume, January to September', pct(k26 / k25 - 1))]
for i, (big, lab, chg) in enumerate(tiles):
    x0 = 612648 + i * 3250000
    rect(SA, x0, 1572768, 3150000, 880000, F_TILE)
    tb(SA, x0 + 120000, 1620000, 2900000, 330000, big, 20, True, NAVY)
    tb(SA, x0 + 120000, 1960000, 2900000, 250000, lab, 8.5, False, BLACK)
    tb(SA, x0 + 120000, 2200000, 2900000, 200000, chg + ' vs 2025', 9, True, col_(float(chg.replace('%', '').replace(MINUS, '-').replace('+', ''))))
tb(SA, 612648, 2560000, 6400000, 220000, 'Top key accounts by non-fuel revenue, January to September (J$M)', 10, True, NAVY)
rows_ = [['Account', '2026', '2025', 'Change', 'GWh 2026', 'GWh vs 2025']]
cols_ = []
for n, v in top8:
    a26, a25 = v[2026]['nf'] / 1e6, v[2025]['nf'] / 1e6
    rows_.append([fixn(n), f'{a26:,.0f}', f'{a25:,.0f}', pct(a26 / a25 - 1, 0) if a25 else 'new', f'{v[2026]["kwh"] / 1e6:,.1f}', sg(v[2026]['kwh'] / 1e6 - v[2025]['kwh'] / 1e6)])
    cols_.append([None, None, None, col_(a26 - a25), None, col_(v[2026]['kwh'] - v[2025]['kwh'])])
table(SA, 612648, 2800000, 6400000, [2.6, 0.8, 0.8, 0.8, 0.9, 1.0], rows_, 262000, size=8.5, left=(0,), colors=cols_)
# retention panel (top right)
rect(SA, 7315200, 1572768, 4270000, 1750000, None, LIGHT)
tb(SA, 7440000, 1632768, 4000000, 200000, 'RETENTION, JAN TO SEP 2026 VS 2025', 9, True, GREY)
ret = [('Accounts billing in both periods', f'{logo * 100:.1f}%', f'{len(act25 & act26):,} of {len(act25):,}'), ('Volume, net of growth', f'{vol_net * 100:.1f}%', f'{vol_gross * 100:.1f}% counting losses only'),
       ('Non-fuel revenue, net of growth', f'{nf_net * 100:.1f}%', f'{nf_gross * 100:.1f}% counting losses only')]
for i, (lab, big, sub) in enumerate(ret):
    yy = 1930000 + i * 450000
    tb(SA, 7440000, yy, 2300000, 400000, [[(lab, True, NAVY)], [(sub, False, GREY)]], 8.5)
    tb(SA, 9900000, yy, 1550000, 400000, big, 20, True, NAVY, PP_ALIGN.RIGHT)
tb(SA, 7315200, 3400000, 4270000, 500000, 'Counting accounts alone makes retention look strong. Volume is the better test: a single refinery moves it more than 100 small accounts.', 9, False, BLACK)
# movers: one list
tb(SA, 7315200, 4000000, 4270000, 200000, 'Largest changes in non-fuel revenue (J$M)', 9, True, NAVY)
mv = [(fixn(n), x / 1e6) for x, n in dec6] + [(fixn(n), x / 1e6) for x, n in inc5[:3]]
rows_m = [[nm_, (MINUS if v < 0 else '+') + f'{abs(v):,.0f}'] for nm_, v in mv]
table(SA, 7315200, 4220000, 4270000, [3.2, 1.0], [['Account', 'Change']] + rows_m, 172000, size=8, left=(0,), colors=[[None, col_(v)] for nm_, v in mv])
'''
d = d[:i0] + rev + d[i1:]

# ---- outlook slide: two sentences plus hotel reopening schedule
j0 = d.index("rect(SB, 612648, 3850000, 6200000, 2000000, F_TILE)")
j1 = d.index("tb(SB, 7100000, 1572768, 4500000, 220000, 'Year on year by month")
out = '''rect(SB, 612648, 3650000, 6200000, 2200000, F_TILE)
tb(SB, 760000, 3700000, 5900000, 200000, 'WHAT MOVES THE OUTLOOK', 9, True, GREY)
tb(SB, 760000, 3910000, 5900000, 700000, [
    [('Recovery adds about 140 GWh in FY2027, ', True, NAVY), ('led by hotels returning in steps and water supply, which is nearly back to last year.', False, BLACK)],
    [('Defections take about 71 GWh. ', True, NAVY), ('Alcoa, MBJ Airports and PAC Kingston Airport are decisions already taken.', False, BLACK)]], 9.5)
tb(SB, 760000, 4650000, 5900000, 200000, 'HOTEL REOPENINGS: 5,018 ROOMS, J$4.52B A YEAR, 89.8% BACK BY MID-2027', 8.5, True, GREY)
table(SB, 760000, 4870000, 5900000, [1.6, 0.9, 1.0, 1.2], [['When', 'Hotels', 'Rooms', 'J$B a year'], ['December 2026', '6', '1,982', '1.78'], ['First half of 2027', '8', '2,524', '2.27'], ['2028', '1', '512', '0.46']], 235000, size=8.5, left=(0,))
'''
d = d[:j0] + out + d[j1:]
rep("rows2, 270000, size=9, left=(0,), colors=cols2, total=True)", "rows2, 245000, size=8.5, left=(0,), colors=cols2, total=True)")
open('cr_build.py', 'w', encoding='utf-8').write(d)
print('patched')
