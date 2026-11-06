# -*- coding: utf-8 -*-
# October 2026 extended sales analysis (3 A4 pages): recovery check, parish / industry / KAM, drivers and the 2027 outlook.
# All numbers come from _oct_deep.json (database + corrected.json + held LE workbook). Rendered by render_onepager.js.
import json, os, csv, collections
src = open('_build_onepagers.py', encoding='utf-8').read()
exec(src.split('# =====================================================================  SALES ONE-PAGER')[0])   # CSS, colours, helpers
def chg(x, d=1):
    s_ = f'{abs(x):.{d}f}'
    return s_ if round(x, d) == 0 else (('+' if x > 0 else MINUS) + s_)
def chgp(x, d=1): return chg(x * 100, d) + '%'
D = json.load(open('_oct_deep.json')); S = D['series']; P = D['parish']; I = D['industry']; K = D['kam']; LE = D['le']; B = D['bands']
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
yoy = lambda g, m: S[g]['2026-%02d' % m] / S[g]['2025-%02d' % m] - 1
ex = lambda m, y: S['RT40-70']['%d-%02d' % (y, m)] - S['alcoa']['%d-%02d' % (y, m)]
yoy_ex = lambda m: ex(m, 2026) / ex(m, 2025) - 1
pc = lambda a, b: (a / b - 1) if b else 0.0
ytd = lambda g, y: sum(S[g]['%d-%02d' % (y, m)] for m in range(1, 11))

# ---------- page 1 chart: year-on-year by month ----------
def line_chart(w=560, h=290):
    x0, x1, y0, y1 = 36, w - 135, 12, h - 24; lo, hi = -40, 10
    X = lambda i: x0 + (x1 - x0) * i / 9; Y = lambda v: y0 + (y1 - y0) * (hi - v) / (hi - lo)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" style="display:block">']
    for v in range(lo, hi + 1, 10):
        out.append(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}" stroke="{"#66788A" if v == 0 else LIGHT}" stroke-width="{0.9 if v == 0 else 0.5}"/><text x="{x0 - 4}" y="{Y(v) + 3:.1f}" font-size="7.5" font-family="Arial" fill="{GREY}" text-anchor="end">{v}%</text>')
    for i, m in enumerate(MON[:10]): out.append(f'<text x="{X(i):.1f}" y="{h - 10}" font-size="7.5" font-family="Arial" fill="{GREY}" text-anchor="middle">{m}</text>')
    out.append(f'<rect x="{X(9) - 9:.1f}" y="{y0}" width="18" height="{y1 - y0}" fill="#F6D3D6" opacity="0.45"/>')
    series = [('Residential RT10', [yoy('RT10', m) * 100 for m in range(1, 11)], BLUE, ''), ('RT20', [yoy('RT20', m) * 100 for m in range(1, 11)], CYAN, ''),
              ('RT40-RT70', [yoy('RT40-70', m) * 100 for m in range(1, 11)], NAVY, ''), ('RT40-RT70 ex Alcoa', [yoy_ex(m) * 100 for m in range(1, 11)], NAVY, '4 3'),
              ('Hotels', [yoy('hotels', m) * 100 for m in range(1, 11)], RED, ''), ('Water supply', [yoy('water', m) * 100 for m in range(1, 11)], GREEN, '')]
    ends = sorted(range(len(series)), key=lambda i: Y(max(lo, min(hi, series[i][1][-1]))))
    ly = {}; last = -99
    for i in ends:
        yv = max(Y(max(lo, min(hi, series[i][1][-1]))) + 3, last + 8.2); ly[i] = yv; last = yv
    for si, (lab, vals, c, dash) in enumerate(series):
        pts = ' '.join(f'{X(i):.1f},{Y(max(lo, min(hi, v))):.1f}' for i, v in enumerate(vals))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="1.7"{" stroke-dasharray=%s" % chr(34) + dash + chr(34) if dash else ""}/>')
        out.append(f'<text x="{X(9) + 5:.1f}" y="{ly[si]:.1f}" font-size="7.2" font-family="Arial" font-weight="bold" fill="{c}">{lab} {chg(vals[-1], 0)}%</text>')
    out.append('</svg>')
    return ''.join(out)

pp = D['postpaid_class']
def post(cl, mo): return pp[mo].get(cl, 0.0)
rt1024, rt1026 = post('RT10', '2024-10'), post('RT10', '2026-10'); rt2024, rt2026 = post('RT20', '2024-10'), post('RT20', '2026-10')
big24 = sum(post(c, '2024-10') for c in ('RT40', 'RT50', 'RT60-ST', 'RT70')); big26 = sum(post(c, '2026-10') for c in ('RT40', 'RT50', 'RT60-ST', 'RT70'))
z = D['zero']
ytd_big, ytd_big25 = ytd('RT40-70', 2026), ytd('RT40-70', 2025)
ytd_ex26 = sum(ex(m, 2026) for m in range(1, 11)); ytd_ex25 = sum(ex(m, 2025) for m in range(1, 11))
west = ['Westmoreland', 'Hanover', 'St. James', 'St. Elizabeth', 'Trelawny']
status = lambda ok: f'<td style="font-weight:bold;color:{GREEN if ok == "Recovered" else (RED if ok == "Not recovered" else "#B8860B")}">{ok}</td>'
sc = [('Residential RT10 vs Oct 2024 (pre-storm, postpaid)', f'{rt1026:,.1f} vs {rt1024:,.1f} GWh', chgp(pc(rt1026, rt1024)), 'Recovered'),
      ('RT20 vs Oct 2024 (postpaid)', f'{rt2026:,.1f} vs {rt2024:,.1f} GWh', chgp(pc(rt2026, rt2024)), 'Recovered'),
      ('RT40 to RT70 vs Oct 2024', f'{big26:,.1f} vs {big24:,.1f} GWh', chgp(pc(big26, big24)), 'Not recovered'),
      ('RT40 to RT70 ex Alcoa, Jan to Oct vs 2025', f'{ytd_ex26:,.0f} vs {ytd_ex25:,.0f} GWh', chgp(pc(ytd_ex26, ytd_ex25)), 'Not recovered'),
      ('Hotels, October vs 2025 (January was ' + chgp(yoy('hotels', 1), 0) + ')', f'{S["hotels"]["2026-10"]:,.1f} vs {S["hotels"]["2025-10"]:,.1f} GWh', chgp(yoy('hotels', 10)), 'Recovering'),
      ('Water supply, October vs 2025 (January was ' + chgp(yoy('water', 1), 0) + ')', f'{S["water"]["2026-10"]:,.1f} vs {S["water"]["2025-10"]:,.1f} GWh', chgp(yoy('water', 10)), 'Recovered'),
      ('RT10 customers at zero kWh vs pre-storm (Oct 2025)', f'{z["2026-10"]:,} vs {z["2025-10"]:,}', chgp(pc(z['2026-10'], z['2025-10'])), 'Not recovered'),
      ('Residential in the west vs 2025 (' + ', '.join(f'{w.replace("St. ", "St ")} {chgp(pc(P[w]["o26_RT10"], P[w]["o25_RT10"]), 0)}' for w in west[:4]) + ')', 'west parishes', chgp(pc(sum(P[w]['o26_RT10'] for w in west), sum(P[w]['o25_RT10'] for w in west))), 'Not recovered')]
sc_html = ''.join(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="font-weight:normal;color:#1F1F1F">{a}</td><td>{b}</td><td style="font-weight:bold;color:{col(float(c.replace(MINUS, "-").replace("+", "").replace("%", "")))}">{c}</td>{status(d)}</tr>' for i, (a, b, c, d) in enumerate(sc))

# ---------- page 2 tables ----------
prow = []
for i, (pg, r) in enumerate(sorted(P.items(), key=lambda kv: -(kv[1]['o26_RT10'] + kv[1]['o26_COMM']))):
    t26 = r['o26_RT10'] + r['o26_COMM']; t25 = r['o25_RT10'] + r['o25_COMM']
    c = lambda v: f'<td style="color:{col(v)};font-weight:bold">{chgp(v)}</td>'
    prow.append(f'<tr class="{"alt" if i % 2 else ""}"><td class="l">{pg}</td><td>{r["o26_RT10"]:.1f}</td>{c(pc(r["o26_RT10"], r["o25_RT10"]))}{c(pc(r["o26_RT10"], r["s26_RT10"]))}<td>{r["o26_COMM"]:.1f}</td>{c(pc(r["o26_COMM"], r["o25_COMM"]))}{c(pc(r["o26_COMM"], r["bud_COMM"]))}{c(pc(r["o26_COMM"], r["s26_COMM"]))}<td style="color:{col(t26 - t25)};font-weight:bold">{chg(t26 - t25, 2)}</td></tr>')
T = P and {k: sum(r[k] for r in P.values()) for k in next(iter(P.values()))}
prow.append(f'<tr class="tot"><td class="l">Total</td><td>{T["o26_RT10"]:.1f}</td><td>{chgp(pc(T["o26_RT10"], T["o25_RT10"]))}</td><td>{chgp(pc(T["o26_RT10"], T["s26_RT10"]))}</td><td>{T["o26_COMM"]:.1f}</td><td>{chgp(pc(T["o26_COMM"], T["o25_COMM"]))}</td><td>{chgp(pc(T["o26_COMM"], T["bud_COMM"]))}</td><td>{chgp(pc(T["o26_COMM"], T["s26_COMM"]))}</td><td>{chg(T["o26_RT10"] + T["o26_COMM"] - T["o25_RT10"] - T["o25_COMM"], 2)}</td></tr>')
irows = []
cand = [(k, v) for k, v in I.items() if k != '(no industry)' and max(v.get('o26', 0), v.get('o25', 0)) >= 1.0]
for i, (k, v) in enumerate(sorted(cand, key=lambda kv: -abs(kv[1].get('o26', 0) - kv[1].get('o25', 0)))[:11]):
    o26, o25, s26 = v.get('o26', 0), v.get('o25', 0), v.get('s26', 0); lfl = (o26 - v.get('unbud', 0)) - v.get('bud', 0)
    nm = (k.replace(' (except Casino Hotels)', '').replace('Wired and Wireless Telecommunications Carriers (except Satellite)', 'Telecommunications').replace('Water Supply and Irrigation Systems', 'Water supply and irrigation').replace('Other Metal Ore Mining', 'Mining (Alcoa)').replace('Telemarketing Bureaus and Other Contact Centers', 'Contact centres').replace('General Medical and Surgical Hospitals', 'Hospitals').replace('Colleges, Universities, and Professional Schools', 'Colleges and universities'))[:34]
    cc = lambda x: f'<td style="color:{col(x)};font-weight:bold">{chg(x, 2)}</td>'
    irows.append(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap">{nm}</td><td>{o26:.1f}</td>{cc(o26 - o25)}{cc(o26 - s26)}{cc(lfl)}</tr>')
korder = sorted(K.items(), key=lambda kv: -kv[1]['o26'])
krows = ''.join(f'<tr class="{"alt" if i % 2 else ""}"><td class="l">{k}</td><td>{v["o26"]:.1f}</td><td style="color:{col(v["o26"] - v["o25"])};font-weight:bold">{chg(v["o26"] - v["o25"], 2)}</td><td style="color:{col(v["o26"] - v["s26"])};font-weight:bold">{chg(v["o26"] - v["s26"], 2)}</td><td style="color:{col(v["o26"] - v["bud"])};font-weight:bold">{chg(v["o26"] - v["bud"], 2)}</td></tr>' for i, (k, v) in enumerate(korder))

# ---------- page 3 ----------
bands = [('<150', 'Under 150 kWh'), ('150>350', '150 to 350'), ('350>550', '350 to 550'), ('550>750', '550 to 750'), ('750>950', '750 to 950'), ('over 950', 'Over 950'), ('Prepaid', 'Prepaid')]
brow = []; hi_k = hi_c = lo_k = 0.0
for i, (b, lab) in enumerate(bands):
    v = B[b]; dk = v['2026-10_kwh'] - v['2026-09_kwh']; dc = v['2026-10_cust'] - v['2026-09_cust']
    if b in ('350>550', '550>750', '750>950', 'over 950'): hi_k += dk; hi_c += dc
    if b in ('<150', '150>350'): lo_k += dk
    brow.append(f'<tr class="{"alt" if i % 2 else ""}"><td class="l">{lab}</td><td>{v["2026-10_kwh"]:.1f}</td><td style="color:{col(dk)};font-weight:bold">{chg(dk, 2)}</td><td>{v["2026-10_cust"]:,.0f}</td><td style="color:{col(dc)};font-weight:bold">{f'{dc:+,.0f}'.replace('-', MINUS)}</td><td style="color:{col(pc(v["2026-10_kwh"], v["2025-10_kwh"]))}">{chgp(pc(v["2026-10_kwh"], v["2025-10_kwh"]))}</td></tr>')
res_oct, res_sep = T['o26_RT10'], T['s26_RT10']
mv = D['movers']; mv_l = sorted(mv.items(), key=lambda kv: -(kv[1].get('10', 0) - kv[1].get('9', 0)))
ups, dns = [(k, v) for k, v in mv_l if v.get('10', 0) - v.get('9', 0) > 0][:6], [(k, v) for k, v in reversed(mv_l) if v.get('10', 0) - v.get('9', 0) < 0][:4]
tot_up = sum(max(0, v.get('10', 0) - v.get('9', 0)) for v in mv.values()); tot_dn = sum(min(0, v.get('10', 0) - v.get('9', 0)) for v in mv.values())
TIMING = ('Caribbean Broilers', 'Petrojam')   # September lows that reverse in October: Broilers billing timing, Petrojam fire outage
mrow = []
for i, (k, v) in enumerate(ups + dns):
    d_ = v.get('10', 0) - v.get('9', 0); nm = v['name'].strip().title() if v['name'].isupper() else v['name'].strip()
    tag = ('fire outage in Sep' if 'Petrojam' in nm else 'billing timing') if any(t in nm for t in TIMING) else ('Alcoa exit' if 'Alcoa' in nm else ('water supply' if 'Water' in nm or 'Irrigation' in nm else '—'))
    mrow.append(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap">{nm[:30]}</td><td>{v.get("9", 0):.2f}</td><td>{v.get("10", 0):.2f}</td><td style="color:{col(d_)};font-weight:bold">{chg(d_, 2)}</td><td style="text-align:left;font-size:7pt">{tag}</td></tr>')
timing_g = sum(mv[k]['10'] - mv[k]['9'] for k in mv if any(t in mv[k]['name'] for t in TIMING))
# FY2026 landing on a 2024 seasonal replay, and what FY2027 needs
cj = json.load(open('corrected.json')); L_ = cj['srat_legend']; ix = {n: i for i, n in enumerate(L_)}; SEP = cj.get('sep', '||')
norm = lambda s: str(s).strip().upper(); RMAP = {}; RCMAP = {}
for r in list(csv.reader(open(r'C:\Users\jwilson\Downloads\Rate categorry Data mapping.csv', encoding='utf-8-sig')))[1:]:
    if len(r) >= 3: RMAP[norm(r[2])] = r[0]; RCMAP.setdefault(norm(r[1]), r[0])
tt = lambda key: (lambda s, rc: RCMAP.get(norm(rc)) or RMAP.get(norm(s)) or 'Other')(*key.split(SEP, 1))
c24 = collections.defaultdict(lambda: collections.defaultdict(float))
for mo in ('2024-09', '2024-10', '2024-11', '2024-12'):
    for key, pp_ in cj['srat'][mo].items():
        for pg, v in pp_.items(): c24[mo][tt(key)] += v[ix['kwh']] / 1e6
ORD = ['RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']
oct26 = {c: post(c, '2026-10') for c in ORD}
prepaid = {'RT10': B['Prepaid']['2026-10_kwh'], 'RT20': 0.104}
yr = lambda c, y: sum(LE[c]['%s %s' % (m, y)] for m in MON)
ytd_le_sep = {c: sum(LE[c]['%s 26' % m] for m in MON[:9]) for c in ORD}
oct_tot = {c: oct26[c] + prepaid.get(c, 0.0) for c in ORD}
rows_o = []; sums = collections.defaultdict(float)
for i, c in enumerate(ORD):
    rn = 1.0 if c == 'RT70' else c24['2024-11'][c] / c24['2024-10'][c]; rd = 1.0 if c == 'RT70' else c24['2024-12'][c] / c24['2024-10'][c]
    nov = oct26[c] * rn + prepaid.get(c, 0.0); dec = oct26[c] * rd + prepaid.get(c, 0.0)
    fy_proj = ytd_le_sep[c] + oct_tot[c] + nov + dec; fy_le = yr(c, 26); fy27 = yr(c, 27)
    sums['le'] += fy_le; sums['proj'] += fy_proj; sums['27'] += fy27
    q4le = sum(LE[c]['%s 26' % m] for m in ('Nov', 'Dec')); q4p = nov + dec
    rows_o.append((c, fy_le, fy_proj, fy_proj - fy_le, fy27, pc(fy27, fy_le), pc(fy27, fy_proj), q4p - q4le))
orow = ''.join(f'<tr class="{"alt" if i % 2 else ""}"><td class="l">{NAMES[c].split(" ")[0]}</td><td>{le:,.1f}</td><td>{pj:,.1f}</td><td style="color:{col(d_)};font-weight:bold">{chg(d_, 1)}</td><td>{f27:,.1f}</td><td>{chgp(g1)}</td><td style="font-weight:bold">{chgp(g2)}</td></tr>' for i, (c, le, pj, d_, f27, g1, g2, q) in enumerate(rows_o))
orow += f'<tr class="tot"><td class="l">System</td><td>{sums["le"]:,.1f}</td><td>{sums["proj"]:,.1f}</td><td>{chg(sums["proj"] - sums["le"], 1)}</td><td>{sums["27"]:,.1f}</td><td>{chgp(pc(sums["27"], sums["le"]))}</td><td>{chgp(pc(sums["27"], sums["proj"]))}</td></tr>'
res_gap = sum(r[3] for r in rows_o if r[0] in ('RT10', 'RT20')); com_gap = sum(r[3] for r in rows_o if r[0] not in ('RT10', 'RT20'))
r10 = [r for r in rows_o if r[0] == 'RT10'][0]; bigs = [r for r in rows_o if r[0] in ('RT40', 'RT50', 'RT60-ST', 'RT70')]
big_le = sum(r[1] for r in bigs); big_pj = sum(r[2] for r in bigs); big_27 = sum(r[4] for r in bigs)
act_cust = sum(B[b]['2026-10_cust'] for b in ('<150', '150>350', '350>550', '550>750', '750>950', 'over 950', 'Prepaid')); avg_kwh = (sum(B[b]['2026-10_kwh'] for b in ('<150', '150>350', '350>550', '550>750', '750>950', 'over 950', 'Prepaid')) * 1e6) / act_cust
zret = (z['2026-10'] - z['2025-10']) * avg_kwh * 12 / 1e6 / r10[4]
nb26, nb25 = B['<Zero']['2026-10_cust'], B['<Zero']['2025-10_cust']; nbk26, nbk25 = B['<Zero']['2026-10_kwh'], B['<Zero']['2025-10_kwh']

# ---------- by rate class page ----------
AC = json.load(open('_fy27_actuals.json')); CB = json.load(open('_oct_class_budget.json'))
CLS = ['RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']
CNAME = {'RT10': 'RT10 Residential', 'RT20': 'RT20 Small commercial', 'RT40': 'RT40 Commercial', 'RT50': 'RT50 Large commercial', 'RT60-ST': 'RT60 Street lighting', 'RT70': 'RT70 Industrial'}
ac = lambda y, m, c: AC['%d-%02d' % (y, m)][c]
cv = {}
for c in CLS:
    o26, o25, s26 = ac(2026, 10, c), ac(2025, 10, c), ac(2026, 9, c)
    y26 = sum(ac(2026, m, c) for m in range(1, 11)); y25 = sum(ac(2025, m, c) for m in range(1, 11))
    j26 = sum(ac(2026, m, c) for m in range(7, 11)); j25 = sum(ac(2025, m, c) for m in range(7, 11))
    cv[c] = dict(j26=j26, j25=j25, o26=o26, o25=o25, s26=s26, le=LE[c]['Oct 26'], bud=CB[c]['oct'], y26=y26, y25=y25, yle=sum(LE[c]['%s 26' % m] for m in MON[:10]), ybud=CB[c]['ytd'])
tot_c = {k: sum(cv[c][k] for c in CLS) for k in cv['RT10']}
crow = []
cc = lambda v, d=1: f'<td style="color:{"#66788A" if abs(v) < 0.0005 else col(v)};font-weight:bold">{chgp(v, d)}</td>'
for i, c in enumerate(CLS):
    v = cv[c]
    crow.append(f'<tr class="{"alt" if i % 2 else ""}"><td class="l" style="white-space:nowrap;font-weight:bold">{CNAME[c]}</td><td>{v["o26"]:.1f}</td>{cc(pc(v["o26"], v["o25"]))}{cc(pc(v["o26"], v["s26"]))}{cc(pc(v["o26"], v["le"]))}{cc(pc(v["o26"], v["bud"]))}{cc(pc(v["j26"], v["j25"]))}{cc(pc(v["y26"], v["y25"]))}</tr>')
t_ = tot_c
crow.append(f'<tr class="tot"><td class="l">Total</td><td>{t_["o26"]:.1f}</td><td>{chgp(pc(t_["o26"], t_["o25"]))}</td><td>{chgp(pc(t_["o26"], t_["s26"]))}</td><td>{chgp(pc(t_["o26"], t_["le"]))}</td><td>{chgp(pc(t_["o26"], t_["bud"]))}</td><td>{chgp(pc(t_["j26"], t_["j25"]))}</td><td>{chgp(pc(t_["y26"], t_["y25"]))}</td></tr>')
# bridge: October actual less the LE, by class (GWh)
def bridge_svg(w=330, h=190):
    vals = [(c, cv[c]['o26'] - cv[c]['le']) for c in CLS]; mx = max(abs(v) for _, v in vals) or 1
    x0 = 150; scale = (w - x0 - 40) / (2 * mx); zx = x0 + mx * scale
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" style="display:block">']
    for i, (c, v) in enumerate(vals):
        y = 8 + i * 28; bw = abs(v) * scale; bx = zx if v >= 0 else zx - bw
        out.append(f'<text x="0" y="{y + 12}" font-size="8" font-family="Arial" fill="#1F1F1F">{CNAME[c]}</text>')
        out.append(f'<rect x="{bx:.1f}" y="{y}" width="{max(bw, 1):.1f}" height="16" fill="{GREEN if v >= 0 else RED}"/>')
        lx = zx + bw + 4 if v >= 0 else zx - bw - 4
        out.append(f'<text x="{lx:.1f}" y="{y + 12}" font-size="8" font-family="Arial" font-weight="bold" fill="#1F1F1F" text-anchor="{"start" if v >= 0 else "end"}">{chg(v, 1)}</text>')
    out.append(f'<line x1="{zx:.1f}" y1="2" x2="{zx:.1f}" y2="{h - 8}" stroke="#66788A" stroke-width="0.8"/></svg>')
    return ''.join(out)
r10d = cv['RT10']['o26'] - cv['RT10']['le']; oth = sum(cv[c]['o26'] - cv[c]['le'] for c in CLS if c != 'RT10')
SC = json.load(open('_oct_anomaly_scan.json')); oc_, sp_ = SC['oct'], SC['sep']
al25 = CB['_alcoa_oct25']; al26 = oc_['100185-607213']['net'] / 1e6; al_cr = -oc_['100185-607213']['adj'] / 1e6
catch20 = sum(oc_[k]['adj'] for k in ('1410783-1015430', '1576881-1260246')) / 1e6
catch40 = sum(oc_[k]['adj'] for k in ('100012-172245', '1050236-1120260')) / 1e6
wmp = (sp_['100312-100512']['net'] - oc_['100312-100512']['net']) / 1e3
pac = oc_['1411748-834411']['net'] / 1e6
brk = mv['100058']['10'] - mv['100058']['9']; nwc = mv['100012']['10'] - mv['100012']['9']
rt20_underlying = pc(cv['RT20']['o26'] - catch20, cv['RT20']['o25'])
class_html = f'''<div class="page">
<div class="top"><div><h1>By rate class: what is driving each</h1></div><div class="sub">Jamaica Public Service | page 3 of 7<br>October 2026, GWh billed including prepaid</div></div>
<div class="head">October is {chgp(pc(t_["o26"], t_["o25"]))} on last year and level with the LE. Since July the system is level on last year ({chgp(pc(t_["j26"], t_["j25"]))}): residential and RT20 are up about 4%, RT50 is down {abs(pc(cv["RT50"]["j26"], cv["RT50"]["j25"])) * 100:.0f}% on hotels and RT70 is down {abs(pc(cv["RT70"]["j26"], cv["RT70"]["j25"])) * 100:.0f}% on Alcoa.</div>
<table class="t7"><tr><th class="l">Rate class</th><th>Oct 26</th><th>vs Oct 25</th><th>vs Sep</th><th>vs LE</th><th>vs budget</th><th>Jul-Oct vs 2025</th><th>YTD vs 2025</th></tr>{''.join(crow)}</table>
<div class="small">The LE is the financials forecast held. October 2025 includes the storm of 28 October, so every comparison with it is flattered. July to October is the post-recovery period. Year to date is January to October. Prepaid is included.</div>
<div class="row" style="margin-top:3.4mm"><div style="flex:1"><div class="sec">October actual less the LE, GWh</div>{bridge_svg()}</div>
<div style="flex:1.5"><div class="sec">What is driving each class</div><div class="box items"><ul>
<li><b>Residential.</b> Down {abs(pc(cv["RT10"]["o26"], cv["RT10"]["s26"])) * 100:.1f}% on September in the heavy-use buckets (page 5). The LE holds October flat on September, so the {abs(pc(cv["RT10"]["o26"], cv["RT10"]["le"])) * 100:.1f}% gap to the LE is phasing.</li>
<li><b>RT20.</b> Back above its pre-storm level. About {catch20:.1f} GWh of October is catch-up billing that will not repeat. Without it the month is {chgp(rt20_underlying)} on last year.</li>
<li><b>RT40.</b> Two accounts, Caribbean Broilers and National Water Commission, are the whole movement on September (page 4). Catch-up bills add about {catch40:.2f} GWh.</li>
<li><b>RT50.</b> {chgp(pc(cv["RT50"]["o26"], cv["RT50"]["o25"]))} on last October is the storm base. Hotels are still {abs(yoy("hotels", 10)) * 100:.0f}% down, and West Meat Packers is falling ({wmp:.0f} MWh on September).</li>
<li><b>RT60.</b> Street lighting, steady at {cv["RT60-ST"]["o26"]:.1f} GWh a month.</li>
<li><b>RT70.</b> {abs(pc(cv["RT70"]["o26"], cv["RT70"]["o25"])) * 100:.0f}% below last October, which is Alcoa ({al26:.2f} GWh against {al25:.1f} a year ago, after a {al_cr:.1f} GWh billing credit). Petrojam is back after its September fire. PAC's solar is not yet in the bills ({pac:.2f} GWh).</li></ul></div></div></div>
<div class="foot"><span><b>Jamaica Public Service</b> | Sales Analysis | October 2026</span><span>Budget is the 2026 account-level budget.</span></div>
</div>
'''


# ---------- who moved: top and bottom companies by rate class, and residential bucket movement ----------
WM = json.load(open('_oct_who_moved.json'))
WNAME = {'RT20': 'RT20 Small commercial', 'RT40': 'RT40 Commercial', 'RT50': 'RT50 Large commercial', 'RT60-ST': 'RT60 Street lighting', 'RT70': 'RT70 Industrial'}
NOTE = {'RT40|100058': 'Billing timing', 'RT70|101188': 'Back after September fire outage', 'RT70|100185': 'Left the grid; 2.0 GWh credit in October', 'RT20|1410783': 'New account; catch-up bill', 'RT20|1576881': 'Catch-up bill', 'RT40|1050236': 'Catch-up bill'}
def tname(n):
    n = (n or '').strip(); n = n.title() if n.isupper() else n
    return n[:34]
by_cls = collections.defaultdict(list)
for key, e in WM['cust'].items():
    c, cc_ = key.split('|', 1)
    if max(abs(e['o26']), abs(e['s26']), abs(e['o25'])) < 20000: continue
    by_cls[c].append((cc_, e))
wrows = []; shown = {}
mw = lambda v: f'{v / 1000:,.0f}'
def smw(x):
    return '0' if round(x) == 0 else (f'+{x:,.0f}' if x > 0 else MINUS + f'{abs(x):,.0f}')
def chg_mwh(v):
    x = v / 1000
    return f'<td style="color:{col(x)};font-weight:bold">{smw(x)}</td>'
n_row = 0
for c in ('RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70'):
    L = by_cls[c]; L.sort(key=lambda t: t[1]['o26'] - t[1]['s26'])
    down = L[:3]; up = L[::-1][:3]
    tot_o, tot_s = sum(e['o26'] for _, e in L), sum(e['s26'] for _, e in L)
    wrows.append(f'<tr class="tot"><td class="l" colspan="8">{WNAME[c]}: {len(L)} customers over 20 MWh, {mw(tot_o)} MWh in October, {smw((tot_o - tot_s) / 1000)} MWh on September</td></tr>')
    flat = all(abs(e['o26'] - e['s26']) < 1 for _, e in L)
    if flat:
        wrows.append('<tr><td class="l" colspan="8" style="font-size:7.2pt">No movement: these accounts bill the same kWh every month. The largest are ' + ' and '.join('%s (%s MWh)' % (tname(e['name']).replace('&', '&amp;'), mw(e['o26'])) for _, e in sorted(L, key=lambda t: -t[1]['o26'])[:2]) + '.</td></tr>')
    for grp, lab in (() if flat else ((up, 'Up'), (down, 'Down'))):
        for cc_, e in grp:
            n_row += 1
            d = e['o26'] - e['s26']; d25 = e['o26'] - e['o25']
            wrows.append(f'<tr class="{"alt" if n_row % 2 else ""}"><td class="l" style="color:{GREEN if lab == "Up" else RED};font-weight:bold">{lab}</td><td class="l" style="white-space:nowrap">{tname(e["name"])}</td><td>{mw(e["o26"])}</td><td>{mw(e["s26"])}</td>{chg_mwh(d)}<td>{mw(e["o25"])}</td>{chg_mwh(d25)}<td class="l" style="font-size:6.8pt">{NOTE.get(c + "|" + cc_, "")}</td></tr>')
    shown[c] = (up, down)
bro = [e for k, e in WM['cust'].items() if k == 'RT40|100058'][0]; pet = [e for k, e in WM['cust'].items() if k == 'RT70|101188'][0]; alc = [e for k, e in WM['cust'].items() if k == 'RT70|100185'][0]
who_html = f'''<div class="page">
<div class="top"><div><h1>Who moved: top and bottom companies</h1></div><div class="sub">Jamaica Public Service | page 4 of 7<br>Billed MWh by rate class, October 2026</div></div>
<div class="head">A handful of accounts explain the commercial movement. Caribbean Broilers ({smw((bro["o26"] - bro["s26"]) / 1000)} MWh) and Petrojam ({smw((pet["o26"] - pet["s26"]) / 1000)} MWh) are not growth: Broilers is billing timing and Petrojam is back after its September fire. Alcoa ({smw((alc["o26"] - alc["s26"]) / 1000)} MWh) has left the grid.</div>
<table class="t7"><tr><th class="l" style="width:6%"></th><th class="l">Company</th><th>Oct 26</th><th>Sep 26</th><th>vs Sep</th><th>Oct 25</th><th>vs Oct 25</th><th class="l">Note</th></tr>{''.join(wrows)}</table>
<div class="small">Three largest rises and falls on September in each class, among customers above 20 MWh in either month. Customers are grouped across all their premises. Alcoa is shown after a 2.0 GWh billing credit. October 2025 includes the storm of 28 October.</div>
<div class="foot"><span><b>Jamaica Public Service</b> | Sales Analysis | October 2026</span><span>Net billed kWh, shown in MWh.</span></div>
</div>
'''
# ---- residential bucket movement ----
BO = ['<Zero', 'Zero', '<150', '150>350', '350>550', '550>750', '750>950', 'over 950']
BL = {'<Zero': 'Negative kWh (credit)', 'Zero': 'Zero kWh', '<150': 'Under 150', '150>350': '150 to 350', '350>550': '350 to 550', '550>750': '550 to 750', '750>950': '750 to 950', 'over 950': 'Over 950'}
WB = WM['bands']; MG = WM['mig']
arow = []
for i, b in enumerate(BO):
    o26c, s26c, o25c = WB['o26'][b][0], WB['s26'][b][0], WB['o25'][b][0]
    o26k, s26k, o25k = WB['o26'][b][1] / 1e6, WB['s26'][b][1] / 1e6, WB['o25'][b][1] / 1e6
    avg = lambda k, c: f'{k * 1e6 / c:,.0f}' if c and b not in ('Zero',) else '—'
    arow.append(f'<tr class="{"alt" if i % 2 else ""}"><td class="l">{BL[b]}</td><td>{o26c:,.0f}</td><td style="color:{col(o26c - s26c)};font-weight:bold">{f"{o26c - s26c:+,.0f}".replace("-", MINUS)}</td><td style="color:{col(o26c - o25c)}">{f"{o26c - o25c:+,.0f}".replace("-", MINUS)}</td><td>{o26k:.2f}</td><td style="color:{col(o26k - s26k)};font-weight:bold">{chg(o26k - s26k, 2)}</td><td style="color:{col(o26k - o25k)}">{chg(o26k - o25k, 2)}</td><td>{avg(o26k, o26c)}</td><td>{avg(s26k, s26c)}</td></tr>')
ST = ['<150', '150>350', '350>550', '550>750', '750>950', 'over 950']
NB_ = 'Not billed'; AX = ['<Zero', 'Zero'] + ST + [NB_]
mig_rows = []
for i, a in enumerate(AX):
    cells = []; tot = sum(MG.get(a + '>' + b, 0) for b in AX)
    for b in AX:
        v = MG.get(a + '>' + b, 0)
        st = 'font-weight:bold;background:#DCE6F1' if a == b else ''
        cells.append(f'<td style="{st}">{v:,}</td>')
    mig_rows.append(f'<tr class="{"alt" if i % 2 else ""}"><td class="l">{BL.get(a, a)}</td>{"".join(cells)}<td style="font-weight:bold">{tot:,}</td></tr>')
def split_key(k):
    for a_ in BO + [NB_]:
        if k.startswith(a_ + '>') and k[len(a_) + 1:] in BO + [NB_]: return a_, k[len(a_) + 1:]
    raise ValueError(k)
rank = {b: k for k, b in enumerate(ST)}
stay = up_ = dn_ = 0; heavy_s = heavy_dn = heavy_up = heavy_stay = 0
for k, v in MG.items():
    a, b = split_key(k)
    if a in rank and b in rank:
        if a == b: stay += v
        elif rank[b] > rank[a]: up_ += v
        else: dn_ += v
        if rank[a] >= 2:
            heavy_s += v
            if a == b: heavy_stay += v
            elif rank[b] < rank[a]: heavy_dn += v
            else: heavy_up += v
z_stay = MG.get('Zero>Zero', 0); z_back = sum(MG.get('Zero>' + b, 0) for b in ST); z_new = sum(MG.get(a + '>Zero', 0) for a in ST)
z_tot = sum(MG.get('Zero>' + b, 0) for b in AX)
h26 = sum(WB['o26'][b][0] for b in ST[2:]); h25 = sum(WB['s26'][b][0] for b in ST[2:]); h24 = sum(WB['o25'][b][0] for b in ST[2:])
hk26 = sum(WB['o26'][b][1] for b in ST[2:]) / 1e6; hk25 = sum(WB['s26'][b][1] for b in ST[2:]) / 1e6
lowc = sum(WB['o26'][b][0] - WB['s26'][b][0] for b in ST[:2])
bucket_html = f'''<div class="page">
<div class="top"><div><h1>Residential: consumption bucket movement</h1></div><div class="sub">Jamaica Public Service | page 5 of 7<br>RT10 postpaid, Oct vs Sep 2026</div></div>
<div class="head">{heavy_dn / heavy_s * 100:.0f}% of the customers using over 350 kWh in September fell to a lower bucket in October. The heavy buckets lost {h25 - h26:,.0f} customers and {hk25 - hk26:.1f} GWh, while the two lowest buckets gained {lowc:,.0f}.</div>
<div class="sec">Customers and volume by bucket</div>
<table class="t7"><tr><th class="l">Bucket (kWh a month)</th><th>Customers</th><th>vs Sep</th><th>vs Oct 25</th><th>GWh</th><th>vs Sep</th><th>vs Oct 25</th><th>Avg kWh Oct</th><th>Avg kWh Sep</th></tr>{''.join(arow)}</table>
<div class="small">Postpaid customers billed in the month. Prepaid is not in the buckets. Oct 25 is the storm month. The negative bucket holds bills that net to a credit.</div>
<div class="sec" style="margin-top:3.4mm">Where customers moved: September bucket (rows) to October bucket (columns), number of customers</div>
<table class="t7"><tr><th class="l">Sep bucket</th>{''.join(f'<th>{BL.get(b, b)}</th>' for b in AX)}<th>Total</th></tr>{''.join(mig_rows)}</table>
<div class="small">Shaded diagonal is customers who stayed in the same bucket. Negative kWh customers are bills that net to a credit: customers exporting more than they import, and reversed or cancelled bills. Not billed means no bill in that month.</div>
<div class="box items" style="margin-top:3mm"><div class="sec">What the movement shows</div><ul>
<li><b>Heavy users stepped down.</b> Of {heavy_s:,} customers over 350 kWh in September, {heavy_stay:,} stayed, {heavy_dn:,} dropped and {heavy_up:,} moved up. Customers over 350 kWh are {h26:,.0f} now against {h25:,.0f} in September and {h24:,.0f} a year ago.</li>
<li><b>Across all buckets,</b> {up_:,} customers moved up, {dn_:,} moved down and {stay:,} stayed put, so the step down is broad, not a few customers.</li>
<li><b>Zero kWh barely moved.</b> Of {z_tot:,} customers at zero in September, {z_stay:,} are still at zero, {z_back:,} returned to usage and {MG.get("Zero>Not billed", 0):,} had no bill. {z_new:,} customers fell to zero from usage.</li></ul></div>
<div class="foot"><span><b>Jamaica Public Service</b> | Sales Analysis | October 2026</span><span>Customer here is a metered service line.</span></div>
</div>
'''

html = f'''<!doctype html><html><head><meta charset="utf-8"><title>JPS Sales Analysis October 2026: recovery, parish and industry</title><style>{CSS}
.page {{ page-break-after: always; }} .page:last-child {{ page-break-after: auto; }} .top h1 {{ font-size: 18pt; white-space: nowrap; }} .head {{ font-size: 11.5pt; margin: 3mm 0 2.6mm; }}
.t7 td {{ padding: 0.8mm 0.9mm; font-size: 7.6pt; }} .t7 th {{ font-size: 6.9pt; padding: 0.9mm 0.7mm; }} .box ul {{ margin: 0; padding-left: 4mm; font-size: 8pt; }} .box li {{ margin-bottom: 1.1mm; }}
.verdict {{ background: {LIGHT}; border-left: 2.2pt solid {BLUE}; padding: 2.2mm 3.2mm; font-size: 8.6pt; margin-bottom: 3mm; }} .verdict b {{ color: {NAVY}; }} .small {{ font-size: 7.2pt; color: {GREY}; margin-top: 1.2mm; }}
</style></head><body>

<div class="page">
<div class="top"><div><h1>October 2026: how far has the recovery got?</h1></div><div class="sub">Jamaica Public Service | page 1 of 7<br>Billed volume including prepaid</div></div>
<div class="head">Residential and small commercial are through the recovery. Large commercial is not: hotels are still {abs(yoy("hotels", 10)) * 100:.0f}% down, Alcoa has left the grid and the hurricane-hit west is still below last year.</div>
<div class="verdict">Recovery is still under way in three places. <b>Hotels</b> have narrowed the gap to last year from {abs(yoy("hotels", 1)) * 100:.0f}% in January to {abs(yoy("hotels", 10)) * 100:.0f}%. <b>The western parishes</b> are closer but not back. And <b>{z["2026-10"] - z["2025-10"]:,} more residential premises than before the storm</b> are still billing zero consumption, a number that has not moved since June. Everywhere else we are either back above where we were before the storm (residential, RT20, water supply) or lower for a structural reason (Alcoa and the industrial customers).</div>
<div class="row"><div style="flex:1.45"><div class="sec">Year on year by month, 2026 vs 2025</div>{line_chart()}
<div class="small">October looks stronger than it is because the October 2025 base includes the storm of 28 October (shaded). Prepaid is included.</div></div>
<div style="flex:1"><div class="sec">What the trend tells us</div><div class="box"><ul>
<li>Residential has run above last year since July ({chgp(yoy("RT10", 7))}, {chgp(yoy("RT10", 8))}, {chgp(yoy("RT10", 9))}, {chgp(yoy("RT10", 10))}) and is {chgp(pc(rt1026, rt1024))} on October 2024, the last clean October.</li>
<li>Large commercial (RT40 to RT70) slipped from {chgp(yoy("RT40-70", 7))} in July to {chgp(yoy("RT40-70", 9))} in September. Without Alcoa it ran {chgp(yoy_ex(7))} to {chgp(yoy_ex(9))}, so the commercial base was still short of last year before October.</li>
<li>October's {chgp(yoy_ex(10))} for large commercial excluding Alcoa reflects the weak storm base. It is not a turn. Hotels, still {abs(yoy("hotels", 10)) * 100:.1f}% down, show what that base is hiding.</li>
<li>Water supply is the one large commercial group fully back ({chgp(yoy("water", 10))}).</li></ul></div></div></div>
<div class="sec" style="margin-top:3.4mm">Recovery scorecard</div>
<table class="t7"><tr><th class="l" style="width:46%">Indicator</th><th>Now vs comparison</th><th>Change</th><th>Status</th></tr>{sc_html}</table>
<div class="row" style="margin-top:3.4mm"><div class="box" style="flex:1"><div class="sec">The west</div><div style="font-size:8.2pt">St James, Westmoreland, Hanover, Trelawny and St Elizabeth together ran {chgp(pc(sum(P[w]["o26_RT10"] + P[w]["o26_COMM"] for w in west), sum(P[w]["o25_RT10"] + P[w]["o25_COMM"] for w in west)))} on last October, against a base the storm had already depressed there, so the shortfall is real. The Montego Bay hotels are the largest piece: St James commercial is {abs(pc(P["St. James"]["o26_COMM"], P["St. James"]["o25_COMM"])) * 100:.1f}% below last year and {abs(pc(P["St. James"]["o26_COMM"], P["St. James"]["bud_COMM"])) * 100:.1f}% below budget.</div></div>
<div class="box" style="flex:1"><div class="sec">What we need to see</div><div style="font-size:8.2pt">Hotels within 10% of last year once the December reopenings (1,982 rooms) land. Residential premises at zero consumption back under 53,000. Western residential back above last year. We are not there on any of the three yet.</div></div></div>
<div class="foot"><span><b>Jamaica Public Service</b> | Sales Analysis | October 2026</span><span>Comparisons with 2024 exclude prepaid, held only from 2025.</span></div>
</div>

{class_html}{who_html}{bucket_html}
<div class="page">
<div class="top"><div><h1>Where: parish, industry and KAM</h1></div><div class="sub">Jamaica Public Service | page 6 of 7<br>October 2026, GWh</div></div>
<div class="head">Growth is concentrated in Kingston and St Catherine. St James and Clarendon pull the other way, and each has a single explanation.</div>
<div class="sec">By parish</div>
<table class="t7"><tr><th class="l" rowspan="2">Parish</th><th colspan="3">Residential (RT10)</th><th colspan="4">Commercial (RT20 to RT70)</th><th rowspan="2">Total vs<br>2025 (GWh)</th></tr>
<tr><th class="sub">Oct 26</th><th class="sub">vs 2025</th><th class="sub">vs Sep</th><th class="sub">Oct 26</th><th class="sub">vs 2025</th><th class="sub">vs budget</th><th class="sub">vs Sep</th></tr>{''.join(prow)}</table>
<div class="small">Prepaid is shown in its parish. Residential is not compared with budget by parish because the parish budgets are an allocation of the national figure. Commercial is compared with the account budgets.</div>
<div class="row" style="margin-top:3.2mm"><div style="flex:1.25"><div class="sec">By industry (accounts RT20 and above), largest changes on 2025</div>
<table class="t7"><tr><th class="l">Industry</th><th>Oct 26</th><th>vs 2025</th><th>vs Sep</th><th>vs budget*</th></tr>{''.join(irows)}</table>
<div class="small">*Budget variance covers accounts that carry a budget. Telecoms, executive offices and courts have many small accounts with no budget line.</div></div>
<div style="flex:1"><div class="sec">By KAM (accounts with a named KAM)</div>
<table class="t7"><tr><th class="l">KAM</th><th>Oct 26</th><th>vs 2025</th><th>vs Sep</th><th>vs budget</th></tr>{krows}</table>
<div class="small">Sharmica Holness's shortfall against budget is Alcoa, whose main account is {abs(7.09):.1f} GWh under.</div></div></div>
<div class="box items" style="margin-top:3mm"><div class="sec">What this tells us</div><ul>
<li><b>St James</b> commercial is {chgp(pc(P["St. James"]["o26_COMM"], P["St. James"]["o25_COMM"]))} on last year ({chg(P["St. James"]["o26_COMM"] - P["St. James"]["o25_COMM"], 1)} GWh). This is the hotel belt, and hotels are {chg(S["hotels"]["2026-10"] - S["hotels"]["2025-10"], 1)} GWh on last October.</li>
<li><b>Clarendon</b> commercial is {chgp(pc(P["Clarendon"]["o26_COMM"], P["Clarendon"]["o25_COMM"]))} ({chg(P["Clarendon"]["o26_COMM"] - P["Clarendon"]["o25_COMM"], 1)} GWh), which is Alcoa's refinery. Mining is {chg(I["Other Metal Ore Mining"]["o26"] - I["Other Metal Ore Mining"]["o25"], 1)} GWh on last year.</li>
<li><b>Kingston South</b> commercial is {chgp(pc(P["KSAS"]["o26_COMM"], P["KSAS"]["o25_COMM"]))} ({chg(P["KSAS"]["o26_COMM"] - P["KSAS"]["o25_COMM"], 1)} GWh), of which Caribbean Cement is {chg(I["Cement Manufacturing"]["o26"] - I["Cement Manufacturing"]["o25"], 1)} on a storm-hit base.</li>
<li><b>Portmore</b> commercial is {chgp(pc(P["Portmore"]["o26_COMM"], P["Portmore"]["s26_COMM"]))} on September because Caribbean Broilers' main plant is billed there ({chg(mv["100058"]["10"] - mv["100058"]["9"], 1)} GWh). That is billing timing, not growth. Kingston South also gains from Petrojam returning after its September fire ({chg(mv["101188"]["10"] - mv["101188"]["9"], 1)} GWh).</li>
<li><b>Residential</b> is up in the east and centre ({chgp(pc(sum(P[w]["o26_RT10"] for w in P if w not in west), sum(P[w]["o25_RT10"] for w in P if w not in west)))} on 2025) and down in the west ({chgp(pc(sum(P[w]["o26_RT10"] for w in west), sum(P[w]["o25_RT10"] for w in west)))}).</li></ul></div>
<div class="foot"><span><b>Jamaica Public Service</b> | Sales Analysis | October 2026</span><span>Industry and KAM views cover accounts RT20 and above.</span></div>
</div>

<div class="page">
<div class="top"><div><h1>What is driving the swing, and 2027</h1></div><div class="sub">Jamaica Public Service | page 7 of 7<br>Residential down, commercial up</div></div>
<div class="head">Residential fell {abs(res_oct / res_sep - 1) * 100:.1f}% on September and commercial rose {abs(T["o26_COMM"] / T["s26_COMM"] - 1) * 100:.1f}%, about half of it Caribbean Broilers and Petrojam recovering from a low September. Neither is a trend, and the 2027 plan leans on both.</div>
<div class="row" style="margin-top:3mm"><div class="box items" style="flex:1"><div class="sec">What is driving the swing</div><ul>
<li><b>Residential vs September ({chg(res_oct - res_sep, 1)} GWh).</b> Seasonal and spread across the heavy-use buckets (page 5). It is deeper than the {chg((c24["2024-10"]["RT10"] / c24["2024-09"]["RT10"] - 1) * 100, 1)}% October move in 2024. The structural drag is small but real: {nb26:,.0f} net-export accounts against {nb25:,.0f} last October, exporting {abs(nbk26) * 1000:,.0f} MWh against {abs(nbk25) * 1000:,.0f}.</li>
<li><b>Residential vs the LE.</b> The LE has RT10 flat on September, while 2024 and 2025 both fall. That is phasing, not weakness, but it carries into November and December.</li>
<li><b>Commercial vs September ({chg(T["o26_COMM"] - T["s26_COMM"], 1)} GWh).</b> Caribbean Broilers (billing timing) and Petrojam (back after its September fire) are {chg(timing_g, 1)} GWh of it, {abs(timing_g / (tot_up + tot_dn)) * 100:.0f}%, so October is a normal month and not a step up (page 4). National Water Commission's {chg(mv["100012"]["10"] - mv["100012"]["9"], 1)} GWh is the one real rise: {mv["100012"]["10"]:.1f} GWh against {mv["100012"]["7"]:.1f} and {mv["100012"]["8"]:.1f} in July and August, with water supply {chgp(yoy("water", 10))} on last year. Whether it holds depends on pumping demand.</li></ul></div>
<div class="box" style="flex:1.1"><div class="sec">FY2026 landing if the year ends like 2024 (GWh)</div>
<table class="t7"><tr><th class="l">Class</th><th>FY26 LE</th><th>FY26 outlook</th><th>Gap</th><th>FY27 plan</th><th>vs LE</th><th>vs outlook</th></tr>{orow}</table>
<div class="small">The outlook is January to October actual, with November and December run from October's level and 2024's October to December pattern for each class (RT70 held flat). It rests on one year's pattern, so treat it as an indication, not a forecast.</div></div></div>
<div class="verdict" style="margin-top:3mm"><b>Is it sustainable through 2027?</b> Our view is that the commercial position holds and the residential plan does not, as it stands. On this outlook FY2026 lands {abs(sums["proj"] - sums["le"]):.0f} GWh ({abs(pc(sums["proj"], sums["le"])) * 100:.1f}%) {"below" if sums["proj"] < sums["le"] else "above"} the LE in total, but with a different mix: residential and RT20 {chg(res_gap, 0)} GWh and large commercial {chg(com_gap, 0)} GWh. <b>Residential:</b> the November and December fall is seasonal and the LE does not carry it, so FY2027 needs RT10 growth of {chgp(r10[6])} on where we expect to finish, against the planned {chgp(r10[5])}. That leans on the {z["2026-10"] - z["2025-10"]:,} zero-consumption premises coming back (worth roughly {zret * 100:.1f}% of RT10 at the average {avg_kwh:.0f} kWh a month) and on normal weather. <b>Commercial:</b> October is a clean base, so large commercial needs {chgp(pc(big_27, big_pj))} against the {chgp(pc(big_27, big_le))} in the plan, provided the hotels reopen on schedule (1,982 rooms in December and 2,524 in the first half of 2027) and we lose no further customers to self-generation. Each 1% on residential is {r10[4] / 100:.1f} GWh in 2027.</div>
<div class="foot"><span><b>Jamaica Public Service</b> | Sales Analysis | October 2026</span><span>The LE is the financials forecast held at 3,299.7 GWh for FY2026. FY2027 is the approved plan.</span></div>
</div>
</body></html>'''
p = os.path.join(r'C:\Projects\Sales_Platform\analysis', '_deep_oct.html'); open(p, 'w', encoding='utf-8').write(html); print('wrote', p)
print('replay: LE %.1f proj %.1f 27 %.1f | res gap %.1f comm gap %.1f | RT10 growth plan %.3f vs replay %.3f' % (sums['le'], sums['proj'], sums['27'], res_gap, com_gap, r10[5], r10[6]))
for r in rows_o: print('  %-8s LE %.1f proj %.1f gap %+.1f | FY27 %.1f | %+.1f%% vs LE %+.1f%% vs replay | Nov-Dec gap %+.1f' % (r[0], r[1], r[2], r[3], r[4], r[5] * 100, r[6] * 100, r[7]))
