# -*- coding: utf-8 -*-
import json, requests, glob, os, re, time

SECRET = open(r'D:\Projects\DataManager\.env').read().split('=', 1)[1].strip()
URL = 'https://bhrswnbenkvflpdjhfpa.supabase.co/rest/v1/jps_actuals'
HDRS = {'apikey': SECRET, 'Authorization': 'Bearer ' + SECRET, 'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates,return=minimal'}
KEYS = ['jps_ac', 'year', 'month', 'rate_class', 'name', 'consumption_bucket', 'parish', 'kwh', 'revenue_jmd',
        'demand_jmd', 'fuel_jmd', 'energy_jmd', 'ipp_jmd', 'customer_charge_jmd', 'gct_jmd', 'customer_count', 'segment']

files = sorted(glob.glob('rt20_split_20??_??.json'))
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
