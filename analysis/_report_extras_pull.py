# -*- coding: utf-8 -*-
# Pulls the supporting numbers for the Attribution Check breakdown, revenue composition,
# net-biller (NB tariff) series, kVA-vs-kWh and consumption-band appendix from the cached
# raw scan (corrected.json + rt20_split_*.json). Writes _report_extras.json.
import json, os

d = json.load(open('corrected.json', encoding='utf-8'))
MONTHS = [m for m in d['months'] if m >= '2025-01']
YTD25 = [f'2025-{m:02d}' for m in range(1, 9)]
YTD26 = [f'2026-{m:02d}' for m in range(1, 9)]
out = {}

# ---- A. Registered net billers (NB10 / NB20 / NB40 srat codes) -------------------
LEG = d['srat_legend']  # count,kwh,rev,kvap,kval,kvao,kva,energy,fuel,ipp,cust,rev_adj,net_bill_adj
nb = {}
for mo in d['months']:
    row = {}
    for key, parishes in d['srat'].get(mo, {}).items():
        code = key.split('||')[0]
        if code in ('NB10', 'NB20', 'NB40'):
            r = row.setdefault(code, {'count': 0, 'kwh': 0.0, 'rev': 0.0, 'credit': 0.0})
            for v in parishes.values():
                r['count'] += v[0]; r['kwh'] += v[1]; r['rev'] += v[2]; r['credit'] += v[12]
    nb[mo] = row
out['nb'] = nb

# ---- B. kVA vs kWh for demand-billed classes -------------------------------------
kva = {}
for key, a in d['acct'].items():
    t = a['title']
    if t not in ('RT40', 'RT50', 'RT70'):
        continue
    for mo, v in a['m'].items():
        if mo < '2025-01':
            continue
        r = kva.setdefault(mo, {}).setdefault(t, {'kwh': 0.0, 'kva': 0.0, 'rev': 0.0, 'accts': 0})
        r['kwh'] += v[0]; r['rev'] += v[1]; r['kva'] += v[5]; r['accts'] += 1
out['kva'] = kva

# ---- C. Consumption bands, individually metered classes --------------------------
BANDS = [('Net export (<0)', None, 0), ('Zero', 0, 0.0000001), ('1-1,000', 0.0000001, 1000),
         ('1,001-5,000', 1000, 5000), ('5,001-20,000', 5000, 20000), ('20,001-100,000', 20000, 100000),
         ('100,001-500,000', 100000, 500000), ('Over 500,000', 500000, None)]
def band_of(k):
    if k < 0: return 0
    if k == 0: return 1
    if k <= 1000: return 2
    if k <= 5000: return 3
    if k <= 20000: return 4
    if k <= 100000: return 5
    if k <= 500000: return 6
    return 7
bands = {}
for mo in ('2025-08', '2026-08'):
    for key, a in d['acct'].items():
        v = a['m'].get(mo)
        if not v: continue
        t = a['title']
        b = band_of(v[0])
        r = bands.setdefault(mo, {}).setdefault(t, [[0, 0.0, 0.0] for _ in BANDS])
        r[b][0] += 1; r[b][1] += v[0]; r[b][2] += v[1]
    fn = 'rt20_split_%s.json' % mo.replace('-', '_')
    s = json.load(open(fn, encoding='utf-8'))
    r = bands[mo].setdefault('RT20-commercial', [[0, 0.0, 0.0] for _ in BANDS])
    for ac, b in s['comm'].items():
        k = b['v'][0]; bi = band_of(k)
        r[bi][0] += 1; r[bi][1] += k; r[bi][2] += b['v'][1]
out['bands'] = bands
out['band_labels'] = [b[0] for b in BANDS]

# ---- E. Residential postpaid revenue components (RT10 + RT20 residential) --------
def tot(mo, cls):
    t = [0.0] * 7
    for v in d['bucket'][mo][cls].values():
        for i in range(7): t[i] += v[i]
    return t  # count,kwh,rev,energy,fuel,ipp,cust
res = {}
for mo in MONTHS:
    r10 = tot(mo, 'RT10'); r20 = tot(mo, 'RT20')
    s = json.load(open('rt20_split_%s.json' % mo.replace('-', '_'), encoding='utf-8'))
    c = [sum(b['v'][i] for b in s['comm'].values()) for i in range(8)]  # kwh,rev,dem,fu,en,ipp,cust,gct
    res[mo] = {
        'kwh': r10[1] + r20[1] - c[0],
        'rev': r10[2] + r20[2] - c[1],
        'energy': r10[3] + r20[3] - c[4],
        'fuel': r10[4] + r20[4] - c[3],
        'ipp': r10[5] + r20[5] - c[5],
        'cust': r10[6] + r20[6] - c[6],
    }
out['res_components'] = res

json.dump(out, open('_report_extras.json', 'w'))
print('ok')
