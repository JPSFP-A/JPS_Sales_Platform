# -*- coding: utf-8 -*-
"""Load residential (RT10) volume by parish into jps_res_parish for a month, or backfill every month on file.

jps_actuals carries RT10 at parish 'ALL' by consumption band, so it cannot show recovery by parish. This table does:
one row per month, parish and segment (Postpaid from the billing scan in corrected.json, Prepaid from the prepaid rows already in jps_actuals).
Idempotent: an upsert on (year, month, rate_class, parish, segment). Run after corrected_scan.py and the prepaid load; _push_rt10_buckets.py calls it.

    python _push_res_parish.py 2026-10        one month
    python _push_res_parish.py --all          every month in corrected.json from 2024-01 (prepaid from 2025-01)
Every month is reconciled to jps_actuals RT10 before the run finishes.
"""
import csv, json, os, sys, time, collections, requests
try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)

def load_env(path):
    e = {}
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1); e[k.strip()] = v.strip().strip('"').strip("'")
    return e
ENV = load_env(os.path.join(HERE, '.env')); BASE = ENV['SUPABASE_URL'].rstrip('/'); KEY = ENV['SUPABASE_SERVICE_ROLE_KEY']
H = {'apikey': KEY, 'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'}

M = json.load(open('corrected.json')); LEG = M['srat_legend']; IX = {n: i for i, n in enumerate(LEG)}; SEP = M.get('sep', '||')
norm = lambda s: str(s).strip().upper(); RMAP = {}; RCMAP = {}
for r in list(csv.reader(open(r'C:\Users\jwilson\Downloads\Rate categorry Data mapping.csv', encoding='utf-8-sig')))[1:]:
    if len(r) >= 3: RMAP[norm(r[2])] = r[0]; RCMAP.setdefault(norm(r[1]), r[0])
title = lambda key: (lambda s, rc: RCMAP.get(norm(rc)) or RMAP.get(norm(s)) or 'Other')(*key.split(SEP, 1))

def get(params):
    out = []; off = 0
    while True:
        r = requests.get(BASE + '/rest/v1/jps_actuals', headers={**H, 'Range-Unit': 'items', 'Range': '%d-%d' % (off, off + 999)}, params=params, timeout=120)
        r.raise_for_status(); d = r.json(); out += d
        if len(d) < 1000: return out
        off += 1000

def postpaid(mo):
    acc = collections.defaultdict(lambda: [0.0, 0.0, 0])
    for key, pp in M['srat'][mo].items():
        if title(key) != 'RT10': continue
        for pg, v in pp.items():
            a = acc[pg]; a[0] += v[IX['kwh']]; a[1] += v[IX['rev']]; a[2] += int(v[IX['count']])
    return acc

def rows_for(mo):
    y, m = int(mo[:4]), int(mo[5:7]); rows = []
    for pg, (k, r, c) in postpaid(mo).items():
        rows.append({'year': y, 'month': m, 'rate_class': 'RT10', 'parish': pg, 'segment': 'Postpaid', 'kwh': round(k, 3), 'revenue_jmd': round(r, 2), 'customer_count': c})
    if y >= 2025:
        for x in get({'year': 'eq.%d' % y, 'month': 'eq.%d' % m, 'rate_class': 'eq.RT10', 'consumption_bucket': 'eq.Prepaid', 'select': 'parish,kwh,revenue_jmd,customer_count'}):
            rows.append({'year': y, 'month': m, 'rate_class': 'RT10', 'parish': x['parish'], 'segment': 'Prepaid', 'kwh': float(x['kwh'] or 0), 'revenue_jmd': float(x['revenue_jmd'] or 0), 'customer_count': int(x['customer_count'] or 0)})
    return rows

def push(rows):
    h = {**H, 'Prefer': 'resolution=merge-duplicates,return=minimal'}
    for i in range(0, len(rows), 200):
        for attempt in range(5):
            r = requests.post(BASE + '/rest/v1/jps_res_parish?on_conflict=year,month,rate_class,parish,segment', headers=h, data=json.dumps(rows[i:i + 200]), timeout=60)
            if r.status_code < 300: break
            time.sleep(2)
        else:
            raise SystemExit('push failed: %s %s' % (r.status_code, r.text[:300]))

def reconcile(months):
    bad = []
    live = collections.defaultdict(float)
    for x in get({'rate_class': 'eq.RT10', 'parish': 'eq.ALL', 'select': 'year,month,kwh,consumption_bucket'}):
        live[(x['year'], x['month'])] += float(x['kwh'] or 0)
    tab = collections.defaultdict(float)
    r = requests.get(BASE + '/rest/v1/jps_res_parish', headers=H, params={'select': 'year,month,kwh,segment', 'segment': 'eq.Postpaid', 'limit': 5000}, timeout=120); r.raise_for_status()
    for x in r.json(): tab[(x['year'], x['month'])] += float(x['kwh'])
    for mo in months:
        k = (int(mo[:4]), int(mo[5:7]))
        if k in live and abs(live[k] - tab[k]) > 100000: bad.append((mo, tab[k] / 1e6, live[k] / 1e6))
    return bad

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    months = sorted(M['months']) if '--all' in sys.argv else args
    if not months: raise SystemExit(__doc__)
    total = 0
    for mo in months:
        rows = rows_for(mo); push(rows); total += len(rows)
        print('%s: %d rows, postpaid %.3f GWh, prepaid %.3f GWh' % (mo, len(rows), sum(r['kwh'] for r in rows if r['segment'] == 'Postpaid') / 1e6, sum(r['kwh'] for r in rows if r['segment'] == 'Prepaid') / 1e6), flush=True)
    print('pushed %d rows' % total)
    bad = reconcile(months)
    if bad:
        print('Postpaid parish totals differ from the RT10 band rows in these months (GWh parish table vs band rows; the band rows may predate a correction):')
        for mo, a, b in bad: print('  %s  %.3f vs %.3f  (%+.3f)' % (mo, a, b, a - b))
    else:
        print('All %d months reconcile to the RT10 band rows' % len(months))

if __name__ == '__main__':
    main()
