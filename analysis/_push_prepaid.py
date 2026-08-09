# -*- coding: utf-8 -*-
# Loads the Customer-Monthly-Transaction-Report (PAYG/prepaid) file into jps_actuals,
# matching the existing prepaid aggregation scheme: parish-aggregated (not per-account),
# using the 15-admin-parish + KSAN/KSAS/Portmore split + UNMAPPED fallback already in the DB.
# 'unassigned'-tariff rows (no rate class in the CIS extract) are loaded SEPARATELY under
# rate_class='UNASSIGNED-PAYG' rather than silently dropped or guessed into RT10/RT20.
import json, sys, requests, time
import openpyxl

SRC = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\jwilson\AppData\Local\Temp\Customer-Monthly-Transaction-Report-7-26 (1).xlsx"

SECRET = open(r'D:\Projects\DataManager\.env').read().split('=', 1)[1].strip()
URL = 'https://bhrswnbenkvflpdjhfpa.supabase.co/rest/v1/jps_actuals'
HDRS = {'apikey': SECRET, 'Authorization': 'Bearer ' + SECRET, 'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates,return=minimal'}

CITY_MAP = json.load(open('city_parish_map.json'))
ADMIN_PARISHES = {
    'Clarendon', 'Hanover', 'Manchester', 'Portland', 'St. Ann', 'St. Catherine',
    'St. Elizabeth', 'St. James', 'St. Mary', 'St. Thomas', 'Trelawny', 'Westmoreland',
}
SAINT_NORM = {
    'Saint Ann': 'St. Ann', 'Saint Catherine': 'St. Catherine', 'Saint Elizabeth': 'St. Elizabeth',
    'Saint James': 'St. James', 'Saint Mary': 'St. Mary', 'Saint Thomas': 'St. Thomas',
    'Clarendon': 'Clarendon', 'Hanover': 'Hanover', 'Manchester': 'Manchester',
    'Portland': 'Portland', 'Trelawny': 'Trelawny', 'Westmoreland': 'Westmoreland',
}


def norm_parish(raw):
    if not raw or ',' not in str(raw):
        return 'UNMAPPED'
    city, admin = [p.strip() for p in str(raw).split(',', 1)]
    district = CITY_MAP.get(city)
    if district == 'KSA North':
        return 'KSAN'
    if district == 'KSA South':
        return 'KSAS'
    if district == 'Portmore':
        return 'Portmore'
    return SAINT_NORM.get(admin, 'UNMAPPED')


def load_rows():
    wb = openpyxl.load_workbook(SRC, read_only=True)
    ws = wb['Sheet-0']
    rows = []
    for i, r in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue
        rows.append(r)
    wb.close()
    return rows


rows = load_rows()
print('raw rows:', len(rows))

# columns: Account, JPSaccount, Premise_Number, Name, Address, Parish, Tariff, Arrears, KWh, Pre_GCT_Amt, GCT, Total_Amount, Month
buckets = {}  # (rate_class, parish) -> [kwh, rev_pre_gct, gct, cust_count]
months_seen = set()
for r in rows:
    tariff = str(r[6] or '').strip()
    if tariff == 'RT10-PAYG':
        rc = 'RT10'
    elif tariff == 'RT20-PAYG':
        rc = 'RT20'
    elif tariff == 'unassigned':
        rc = 'UNASSIGNED-PAYG'
    else:
        rc = 'UNASSIGNED-PAYG'
    parish = norm_parish(r[5])
    kwh = float(r[8] or 0)
    pre_gct = float(r[9] or 0)
    gct = float(r[10] or 0)
    ym = str(r[12])
    months_seen.add(ym)
    key = (rc, parish)
    b = buckets.setdefault(key, [0.0, 0.0, 0.0, 0])
    b[0] += kwh; b[1] += pre_gct; b[2] += gct; b[3] += 1

assert len(months_seen) == 1, f'multiple months in file: {months_seen}'
ym = months_seen.pop()
Y, M = int(ym[:4]), int(ym[5:7])
print('period:', Y, M)

KEYS = ['jps_ac', 'year', 'month', 'rate_class', 'name', 'consumption_bucket', 'parish', 'kwh', 'revenue_jmd',
        'demand_jmd', 'fuel_jmd', 'energy_jmd', 'ipp_jmd', 'customer_charge_jmd', 'gct_jmd', 'customer_count', 'segment']
push_rows = []
for (rc, parish), (kwh, rev, gct, cnt) in buckets.items():
    push_rows.append({
        'jps_ac': '', 'year': Y, 'month': M, 'rate_class': rc, 'name': None,
        'consumption_bucket': 'Prepaid', 'parish': parish, 'kwh': kwh, 'revenue_jmd': rev,
        'demand_jmd': 0.0, 'fuel_jmd': 0.0, 'energy_jmd': 0.0, 'ipp_jmd': 0.0,
        'customer_charge_jmd': 0.0, 'gct_jmd': gct, 'customer_count': cnt, 'segment': 'Residential',
    })
for r in push_rows:
    assert set(r.keys()) == set(KEYS)

print('push rows:', len(push_rows))
for (rc, parish), v in sorted(buckets.items()):
    print(f'  {rc:18s} {parish:14s} kwh={v[0]:14,.2f} rev={v[1]:14,.2f} cust={v[3]}')

BATCH = 200
pushed = 0
for i in range(0, len(push_rows), BATCH):
    chunk = push_rows[i:i + BATCH]
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
print('PREPAID PUSH DONE')
