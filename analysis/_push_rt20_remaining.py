# -*- coding: utf-8 -*-
import json, requests, glob, time

SECRET = open(r'D:\Projects\DataManager\.env').read().split('=', 1)[1].strip()
URL = 'https://bhrswnbenkvflpdjhfpa.supabase.co/rest/v1/jps_actuals'
HDRS = {'apikey': SECRET, 'Authorization': 'Bearer ' + SECRET, 'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates,return=minimal'}
KEYS = ['jps_ac', 'year', 'month', 'rate_class', 'name', 'consumption_bucket', 'parish', 'kwh', 'revenue_jmd',
        'demand_jmd', 'fuel_jmd', 'energy_jmd', 'ipp_jmd', 'customer_charge_jmd', 'gct_jmd', 'customer_count', 'segment']

DONE = {'rt20_split_2025_01.json', 'rt20_split_2025_02.json', 'rt20_split_2025_03.json',
        'rt20_split_2025_04.json', 'rt20_split_2025_05.json', 'rt20_split_2025_06.json',
        'rt20_split_2025_07.json', 'rt20_split_2025_08.json', 'rt20_split_2025_09.json'}
files = sorted(f for f in glob.glob('rt20_split_20??_??.json') if f not in DONE)
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
        ok = False
        last_err = None
        for attempt in range(5):
            try:
                resp = requests.post(URL + '?on_conflict=year,month,jps_ac,rate_class,parish,consumption_bucket',
                                      headers=HDRS, data=json.dumps(chunk), timeout=60)
                if resp.status_code < 300:
                    ok = True
                    break
                last_err = f'{resp.status_code} {resp.text[:300]}'
            except Exception as e:
                last_err = repr(e)
            time.sleep(3)
        if not ok:
            print(f'{fp} batch {i} FAILED: {last_err}', flush=True)
            continue
        pushed += len(chunk)
    grand_total += pushed
    print(f'{fp} ({Y}-{M:02d}): pushed {pushed}/{len(rows)}', flush=True)
print('GRAND TOTAL PUSHED:', grand_total, flush=True)
print('PUSH DONE', flush=True)
