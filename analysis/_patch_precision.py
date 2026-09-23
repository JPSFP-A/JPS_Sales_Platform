# -*- coding: utf-8 -*-
import json, csv, re
exec(open(r'C:\Projects\Sales_Platform\analysis\_build_report_v2.py', encoding='utf-8').read().split('# ---------------- Attribution block')[0])
HTMLP = HTML
html = open(HTMLP, encoding='utf-8').read()

# ---- industry (exact) ----
IND = [('Water Supply and Irrigation Systems', 155.1063, 139.4060, 6884.864, 6564.542),
       ('Hotels (except Casino Hotels) and Motels', 173.3015, 128.2876, 7126.054, 5691.606),
       ('Other Metal Ore Mining', 75.4245, 77.7178, 3151.399, 3362.849),
       ('Cement Manufacturing', 60.2547, 73.3771, 1613.848, 1956.392),
       ('Wired and Wireless Telecommunications Carriers', 57.3162, 53.9939, 2797.122, 2720.144),
       ('Executive Offices', 42.6435, 41.1733, 2202.057, 2184.534),
       ('Full-Service Restaurants', 37.6651, 37.2311, 1737.360, 1782.318),
       ('Banking, Insurance and Investments', 35.1011, 33.7167, 1732.060, 1723.179),
       ('Food Manufacturing', 29.3252, 29.8744, 1294.992, 1374.049),
       ('Supermarkets and Other Grocery Retailers', 29.2241, 29.6710, 1326.109, 1407.986)]
T25, T26, TR25, TR26 = 1250.3198, 1186.9398, 56795.964, 56200.524
NT = (143.4602, 149.2013, 7864.166, 8330.173)
top = [sum(r[i] for r in IND) for i in (1, 2, 3, 4)]
OTH = (T25 - NT[0] - top[0], T26 - NT[1] - top[1], TR25 - NT[2] - top[2], TR26 - NT[3] - top[3])
rows = []
for i, (nm, a, b, ra, rb) in enumerate(IND, 1):
    rows.append(f'<tr><td class="l">{i}. {nm}</td><td>{n(a,1)}</td><td>{n(b,1)}</td>{pcell(a, b, 1)}<td>{n(b / T26 * 100, 1)}%</td>{pcell(ra, rb, 1)}</tr>')
rows.append(f'<tr><td class="l">All other tagged industries</td><td>{n(OTH[0],1)}</td><td>{n(OTH[1],1)}</td>{pcell(OTH[0], OTH[1], 1)}<td>{n(OTH[1] / T26 * 100, 1)}%</td>{pcell(OTH[2], OTH[3], 1)}</tr>')
rows.append(f'<tr><td class="l"><i>No industry tag</i></td><td>{n(NT[0],1)}</td><td>{n(NT[1],1)}</td>{pcell(NT[0], NT[1], 1, cls=False)}<td>{n(NT[1] / T26 * 100, 1)}%</td>{pcell(NT[2], NT[3], 1, cls=False)}</tr>')
rows.append(f'<tr class="tot"><td class="l">Total commercial</td><td>{n(T25,1)}</td><td>{n(T26,1)}</td>{pcell(T25, T26, 1)}<td>100.0%</td>{pcell(TR25, TR26, 1)}</tr>')
head = '<tr><th class="l">Industry</th><th>GWh 2025</th><th>GWh 2026</th><th>GWh &Delta;</th><th>Share of commercial GWh, 2026</th><th>Revenue &Delta;</th></tr>'
new_tbl = '<table>\n' + head + '\n' + '\n'.join(rows) + '\n</table>'
i = html.index('<h3>Top 10 industries by 2026 volume</h3>'); i = html.index('<table>', i); j = html.index('</table>', i) + len('</table>')
html = html[:i] + new_tbl + html[j:]

# ---- 5a shares ----
def sh(a, b): return f'{a / T25 * 100:.2f}%</td><td>{b / T26 * 100:.2f}%'
def fix_row(label, a, b):
    global html
    pat = re.compile(r'(<tr><td class="l">' + re.escape(label) + r'</td><td>)[0-9.]+%</td><td>[0-9.]+%')
    assert pat.search(html), label
    html = pat.sub(lambda m: m.group(1) + sh(a, b), html, count=1)
fix_row('Hotels', 173.3015, 128.2876); fix_row('Cement Manufacturing', 60.2547, 73.3771)
fix_row('Other Metal Ore Mining', 75.4245, 77.7178); fix_row('Water Supply and Irrigation', 155.1063, 139.4060)
fix_row('(no industry tag)', NT[0], NT[1])

# ---- parish (exact, from the raw scan cache) ----
d = json.load(open(r'C:\Projects\Sales_Platform\analysis\corrected.json', encoding='utf-8'))
DL = r'C:/Users/jwilson/Downloads/'
norm = lambda s: str(s).strip().upper()
RMAP = {}; RCMAP = {}
for r in list(csv.reader(open(DL + 'Rate categorry Data mapping.csv', encoding='utf-8-sig')))[1:]:
    if len(r) >= 3:
        RMAP[norm(r[2])] = r[0]
        RCMAP.setdefault(norm(r[1]), r[0])
def title(k):
    s, rc = k.split('||'); return RCMAP.get(norm(rc)) or RMAP.get(norm(s))
Y25 = ['2025-%02d' % i for i in range(1, 9)]; Y26 = ['2026-%02d' % i for i in range(1, 9)]
P = {}
for mo in Y25 + Y26:
    for k, par in d['srat'][mo].items():
        if title(k) != 'RT10': continue
        for p, v in par.items():
            r = P.setdefault(p, dict(c25=0, c26=0, k25=0, k26=0, r25=0, r26=0))
            if mo == '2025-08': r['c25'] += v[0]
            if mo == '2026-08': r['c26'] += v[0]
            y = '25' if mo in Y25 else '26'
            r['k' + y] += v[1]; r['r' + y] += v[2]
order = sorted(P.items(), key=lambda x: pct(x[1]['k25'], x[1]['k26']))
prow = []
for name, r in order:
    prow.append(f'<tr><td class="l">{name}</td><td>{n(r["c26"])}</td>{pcell(r["c25"], r["c26"], 1)}<td>{n(r["k26"]/1e6,1)}</td>{pcell(r["k25"], r["k26"], 1)}{pcell(r["r25"], r["r26"], 1)}</tr>')
tk = {k: sum(r[k] for r in P.values()) for k in ('c25', 'c26', 'k25', 'k26', 'r25', 'r26')}
prow.append(f'<tr class="tot"><td class="l">Total</td><td>{n(tk["c26"])}</td>{pcell(tk["c25"], tk["c26"], 1)}<td>{n(tk["k26"]/1e6,1)}</td>{pcell(tk["k25"], tk["k26"], 1)}{pcell(tk["r25"], tk["r26"], 1)}</tr>')
head = '<tr><th class="l">Parish</th><th>Customers, Aug-26</th><th>Customers &Delta;</th><th>GWh, Jan&ndash;Aug 26</th><th>GWh &Delta;</th><th>Revenue &Delta;</th></tr>'
i = html.index('<h3>Residential (billed monthly), by parish'); i = html.index('<table>', i); j = html.index('</table>', i) + len('</table>')
html = html[:i] + '<table>\n' + head + '\n' + '\n'.join(prow) + '\n</table>' + html[j:]
open(HTMLP, 'w', encoding='utf-8').write(html)
print('patched; order:', [(nme, round(pct(r['k25'], r['k26']), 1)) for nme, r in order[:6]])
