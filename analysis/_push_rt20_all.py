# -*- coding: utf-8 -*-
import json, requests, glob, os, re, time

# A TLS-inspecting proxy on the corporate network re-signs HTTPS with a private
# root. requests uses certifi's bundle and does not trust it, so this failed with
# CERTIFICATE_VERIFY_FAILED while curl and the browser worked. truststore points
# Python at the Windows certificate store. Verification stays ON: this is the
# correct fix, not verify=False.
try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass


SECRET = open(r'C:\Projects\DataManager\.env').read().split('=', 1)[1].strip()
URL = 'https://bhrswnbenkvflpdjhfpa.supabase.co/rest/v1/jps_actuals'
HDRS = {'apikey': SECRET, 'Authorization': 'Bearer ' + SECRET, 'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates,return=minimal'}
KEYS = ['jps_ac', 'year', 'month', 'rate_class', 'name', 'consumption_bucket', 'parish', 'kwh', 'revenue_jmd',
        'demand_jmd', 'fuel_jmd', 'energy_jmd', 'ipp_jmd', 'customer_charge_jmd', 'gct_jmd', 'customer_count', 'segment']

files = sorted(glob.glob('rt20_split_20??_??.json'))
# Explicit month filter: `python _push_rt20_all.py 2026_08` pushes that month only.
# `--all` re-pushes every cached split file on disk.
#
# A bare run used to default to --all, on the theory that re-pushing an unchanged
# file is a harmless no-op upsert. It is only a no-op if the cached json's parish
# values still match what the on_conflict key expects in the DB. On 2026-09-02 they
# didn't -- rt20_split.py had been patched to map parish through Parish Grouping.csv,
# but rt20_split_2026_01.json..07.json on disk were never regenerated and still held
# raw town names from before the patch. Re-pushing them didn't update the existing
# grouped-parish rows (different key), it inserted a second copy under the town-name
# key instead -- doubling RT20 for seven months, all silent, until user caught it in
# their reporting. --all is now something you have to ask for, not the default.
import sys as _sys
_args = _sys.argv[1:]
_want = [a for a in _args if not a.startswith('-')]
if not _want and '--all' not in _args:
    print('Refusing to run with no target -- this pushes every cached rt20_split_*.json,', flush=True)
    print('which is only safe if every one of them was built by the CURRENT rt20_split.py.', flush=True)
    print('Pass a month (`2026_08`) or `--all` once you have verified that.', flush=True)
    raise SystemExit(1)
if _want:
    files = [f for f in files if any(w in f for w in _want)]
    if not files:
        print('no rt20_split file matches', _want, flush=True); raise SystemExit(1)
print('files to push:', len(files), flush=True)
grand_total = 0
for fp in files:
    d = json.load(open(fp))
    Y, M = d['year'], d['month']
    rows = []
    for jps_ac, b in d['comm'].items():
        kwh, rev, dem, fu, en, ipp, cust_chg, gct = b['v']
        rows.append({'jps_ac': jps_ac, 'year': Y, 'month': M, 'rate_class': 'RT20', 'name': b['name'],
                     'consumption_bucket': 'Commercial', 'parish': b['parish'], 'kwh': kwh, 'revenue_jmd': rev,
                     'demand_jmd': dem, 'fuel_jmd': fu, 'energy_jmd': en, 'ipp_jmd': ipp,
                     'customer_charge_jmd': cust_chg, 'gct_jmd': gct, 'customer_count': None, 'segment': 'Commercial'})
    for key, v in d['res'].items():
        parish, bucket = key.split('||', 1)
        kwh, rev, gct, cnt = v
        rows.append({'jps_ac': '', 'year': Y, 'month': M, 'rate_class': 'RT20', 'name': None,
                     'consumption_bucket': bucket, 'parish': parish, 'kwh': kwh, 'revenue_jmd': rev,
                     'demand_jmd': 0.0, 'fuel_jmd': 0.0, 'energy_jmd': 0.0, 'ipp_jmd': 0.0,
                     'customer_charge_jmd': 0.0, 'gct_jmd': gct, 'customer_count': int(cnt), 'segment': 'Residential'})
    for r in rows:
        assert set(r.keys()) == set(KEYS)
    BATCH = 500
    pushed = 0
    for i in range(0, len(rows), BATCH):
        chunk = rows[i:i + BATCH]
        for attempt in range(3):
            resp = requests.post(URL + '?on_conflict=year,month,jps_ac,rate_class,parish,consumption_bucket',
                                  headers=HDRS, data=json.dumps(chunk), timeout=60)
            if resp.status_code < 300:
                break
            time.sleep(2)
        else:
            print(f'{fp} batch {i} FAILED: {resp.status_code} {resp.text[:300]}', flush=True)
            continue
        pushed += len(chunk)
    grand_total += pushed
    print(f'{fp} ({Y}-{M:02d}): pushed {pushed}/{len(rows)}', flush=True)
print('GRAND TOTAL PUSHED:', grand_total, flush=True)
print('PUSH DONE', flush=True)
