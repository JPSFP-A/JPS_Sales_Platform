# -*- coding: utf-8 -*-
# Pushes the corrected RT10 Zero/<150 split (from rt10_zero_fix.py's exact-zero-aware
# reprocessing of the raw billing files) to jps_actuals, replacing the mislabeled rows
# that came from corrected.json's 50kWh-wide histogram bins.
import json, requests, time

SECRET = open(r'D:\Projects\DataManager\.env').read().split('=', 1)[1].strip()
URL = 'https://bhrswnbenkvflpdjhfpa.supabase.co/rest/v1/jps_actuals'
HDRS = {'apikey': SECRET, 'Authorization': 'Bearer ' + SECRET, 'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates,return=minimal'}

d = json.load(open('rt10_zero_fix_result.json'))

KEYS = ['jps_ac', 'year', 'month', 'rate_class', 'name', 'consumption_bucket', 'parish', 'kwh', 'revenue_jmd',
        'demand_jmd', 'fuel_jmd', 'energy_jmd', 'ipp_jmd', 'customer_charge_jmd', 'gct_jmd', 'customer_count', 'segment']

rows = []
for mo, tiers in d.items():
    Y, M = int(mo[:4]), int(mo[5:7])
    for bucket_label, key in [('Zero', 'TrueZero'), ('<150', '<150')]:
        cnt, kwh, rev, en, fu, ip, cc = tiers[key]
        rows.append({
            'jps_ac': '', 'year': Y, 'month': M, 'rate_class': 'RT10', 'name': None,
            'consumption_bucket': bucket_label, 'parish': 'ALL', 'kwh': kwh, 'revenue_jmd': rev,
            'demand_jmd': 0.0, 'fuel_jmd': 0.0, 'energy_jmd': 0.0, 'ipp_jmd': 0.0,
            'customer_charge_jmd': 0.0, 'gct_jmd': 0.0, 'customer_count': int(cnt), 'segment': 'Residential',
        })
for r in rows:
    assert set(r.keys()) == set(KEYS)

print('pushing', len(rows), 'rows')
BATCH = 100
pushed = 0
for i in range(0, len(rows), BATCH):
    chunk = rows[i:i + BATCH]
    ok = False
    for attempt in range(5):
        try:
            resp = requests.post(URL + '?on_conflict=year,month,jps_ac,rate_class,parish,consumption_bucket',
                                  headers=HDRS, data=json.dumps(chunk), timeout=60)
            if resp.status_code < 300:
                ok = True
                break
            last = f'{resp.status_code} {resp.text[:300]}'
        except Exception as e:
            last = repr(e)
        time.sleep(2)
    if not ok:
        print('BATCH FAILED', last)
        continue
    pushed += len(chunk)
print('pushed:', pushed)
print('RT10 ZERO FIX PUSH DONE')
