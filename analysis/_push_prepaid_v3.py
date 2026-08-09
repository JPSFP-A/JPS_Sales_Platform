# -*- coding: utf-8 -*-
# v3: uses the canonical "Parish Grouping.csv" (the same mapping corrected_scan.py uses
# for postpaid data) instead of the hand-rolled city/admin heuristics in v1/v2. This
# correctly resolves Kingston-metro rows into KSAN vs KSAS (v2 could not do this and
# defensively skipped ~5,700 rows to avoid duplicating the existing KSAN/KSAS population
# instead). Supersedes v2 entirely -- no more skip/protect logic needed.
import json, sys, csv, requests, time
import openpyxl

SRC = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\jwilson\AppData\Local\Temp\Customer-Monthly-Transaction-Report-7-26 (1).xlsx"
DRY_RUN = '--dry-run' in sys.argv

SECRET = open(r'D:\Projects\DataManager\.env').read().split('=', 1)[1].strip()
URL = 'https://bhrswnbenkvflpdjhfpa.supabase.co/rest/v1/jps_actuals'
HDRS = {'apikey': SECRET, 'Authorization': 'Bearer ' + SECRET, 'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates,return=minimal'}


def norm(s):
    return str(s).strip().upper()


PMAP = {}
with open(r'C:\Users\jwilson\Downloads\Parish Grouping.csv', encoding='utf-8-sig') as f:
    for r in list(csv.reader(f))[1:]:
        if len(r) >= 2:
            PMAP[norm(r[0])] = r[1]

# punctuation-variant aliases the canonical CSV doesn't have an exact match for
# (verified against this file's specific raw strings)
CITY_ALIAS = {'ST ANNS BAY': 'ST. ANN\'S BAY'}


def resolve_parish(raw):
    if not raw or ',' not in str(raw):
        return 'UNMAPPED'
    pg = PMAP.get(norm(raw))
    if pg:
        return pg
    city = str(raw).split(',', 1)[0].strip()
    pg = PMAP.get(norm(city))
    if pg:
        return pg
    alias = CITY_ALIAS.get(norm(city))
    if alias:
        pg = PMAP.get(norm(alias))
        if pg:
            return pg
    return 'UNMAPPED'


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

buckets = {}  # (rate_class, parish) -> [kwh, rev_pre_gct, gct, cust_count]
unmapped_samples = []
months_seen = set()
for r in rows:
    tariff = str(r[6] or '').strip()
    if tariff == 'RT10-PAYG':
        rc = 'RT10'
    elif tariff == 'RT20-PAYG':
        rc = 'RT20'
    else:
        rc = 'UNASSIGNED-PAYG'
    parish = resolve_parish(r[5])
    if parish == 'UNMAPPED' and len(unmapped_samples) < 10:
        unmapped_samples.append(r[5])
    kwh = float(r[8] or 0)
    pre_gct = float(r[9] or 0)
    gct = float(r[10] or 0)
    ym = str(r[12])
    months_seen.add(ym)
    key = (rc, parish)
    b = buckets.setdefault(key, [0.0, 0.0, 0.0, 0])
    b[0] += kwh; b[1] += pre_gct; b[2] += gct; b[3] += 1

print('unmapped samples:', unmapped_samples)
assert len(months_seen) == 1, f'multiple months in file: {months_seen}'
ym = months_seen.pop()
Y, M = int(ym[:4]), int(ym[5:7])
print('period:', Y, M)

for (rc, parish), v in sorted(buckets.items()):
    print(f'  {rc:18s} {parish:14s} kwh={v[0]:14,.2f} rev={v[1]:14,.2f} cust={v[3]}')

if DRY_RUN:
    print('DRY RUN - not pushing')
    sys.exit(0)

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
print('PREPAID PUSH V3 DONE')
