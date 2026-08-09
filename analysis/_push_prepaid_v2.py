# -*- coding: utf-8 -*-
# v2: fixes the Kingston-metro / Portmore mapping bug in _push_prepaid.py.
# Any row whose CITY indicates Kingston-metro (Kingston, Kingston & St Andrew, KSA North,
# KSA South) or Portmore is EXCLUDED from this push entirely -- those populations are
# already correctly loaded in jps_actuals (KSAN/KSAS/Portmore rows, untouched by the v1
# push) and must not be re-derived or duplicated. Only the remaining ~12 parishes are
# recomputed and pushed, replacing v1's corrupted values for those parishes.
import json, sys, requests, time
import openpyxl

SRC = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\jwilson\AppData\Local\Temp\Customer-Monthly-Transaction-Report-7-26 (1).xlsx"
DRY_RUN = '--dry-run' in sys.argv

SECRET = open(r'D:\Projects\DataManager\.env').read().split('=', 1)[1].strip()
URL = 'https://bhrswnbenkvflpdjhfpa.supabase.co/rest/v1/jps_actuals'
HDRS = {'apikey': SECRET, 'Authorization': 'Bearer ' + SECRET, 'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates,return=minimal'}

KSA_METRO_CITIES = {'Kingston', 'Kingston & St Andrew', 'KSA North', 'KSA South'}
PORTMORE_CITY = 'Portmore'

TOWN_TO_PARISH = {
    'Spanish Town': 'St. Catherine', 'Old Harbour': 'St. Catherine',
    'St Anns Bay': 'St. Ann', "St. Ann's Bay": 'St. Ann',
    'Mandeville': 'Manchester',
    'Montego Bay': 'St. James',
    'May Pen': 'Clarendon',
    'Black River': 'St. Elizabeth',
    'Savanna-la-Mar': 'Westmoreland', 'Sav-la-Mar': 'Westmoreland',
    'Port Antonio': 'Portland',
    'Port Maria': 'St. Mary', 'St Mary': 'St. Mary',
    'Falmouth': 'Trelawny',
    'Morant Bay': 'St. Thomas',
    'Lucea': 'Hanover',
}
SAINT_NORM = {
    'Saint Ann': 'St. Ann', 'Saint Catherine': 'St. Catherine', 'Saint Elizabeth': 'St. Elizabeth',
    'Saint James': 'St. James', 'Saint Mary': 'St. Mary', 'Saint Thomas': 'St. Thomas',
    'Clarendon': 'Clarendon', 'Hanover': 'Hanover', 'Manchester': 'Manchester',
    'Portland': 'Portland', 'Trelawny': 'Trelawny', 'Westmoreland': 'Westmoreland',
}
AMBIGUOUS_ADMIN = {'Kingston', 'Saint Andrew', 'KSAN', 'KSAS', 'KSA North', 'KSA South', 'Kingston & St Andrew'}


EXPLICIT_KSA = {'KSAN': 'KSAN', 'KSAS': 'KSAS', 'KSA North': 'KSAN', 'KSA South': 'KSAS'}


def resolve_parish(raw, protect_existing_ksa_portmore):
    """Returns a parish label to push, or None if this row must be skipped because it
    duplicates the already-correct existing KSAN/KSAS/Portmore RT10/RT20 population.
    protect_existing_ksa_portmore is False for 'unassigned' rows, which have no existing
    Kingston-metro representation to protect against duplicating."""
    if not raw or ',' not in str(raw):
        return 'SKIP_UNPARSEABLE'
    city, admin = [p.strip() for p in str(raw).split(',', 1)]
    if protect_existing_ksa_portmore and (city in KSA_METRO_CITIES or city == PORTMORE_CITY):
        return None
    if city == PORTMORE_CITY:
        return 'Portmore'
    if city in EXPLICIT_KSA:
        return EXPLICIT_KSA[city]
    if admin in EXPLICIT_KSA:
        return EXPLICIT_KSA[admin]
    if city in TOWN_TO_PARISH:
        return TOWN_TO_PARISH[city]
    if admin in AMBIGUOUS_ADMIN:
        return 'UNMAPPED' if not protect_existing_ksa_portmore else None
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

buckets = {}  # (rate_class, parish) -> [kwh, rev_pre_gct, gct, cust_count]
skipped = 0
skip_unparseable = 0
months_seen = set()
for r in rows:
    tariff = str(r[6] or '').strip()
    if tariff == 'RT10-PAYG':
        rc = 'RT10'
    elif tariff == 'RT20-PAYG':
        rc = 'RT20'
    else:
        rc = 'UNASSIGNED-PAYG'
    parish = resolve_parish(r[5], protect_existing_ksa_portmore=(rc != 'UNASSIGNED-PAYG'))
    if parish is None:
        skipped += 1
        continue
    if parish == 'SKIP_UNPARSEABLE':
        skip_unparseable += 1
        parish = 'UNMAPPED'
    kwh = float(r[8] or 0)
    pre_gct = float(r[9] or 0)
    gct = float(r[10] or 0)
    ym = str(r[12])
    months_seen.add(ym)
    key = (rc, parish)
    b = buckets.setdefault(key, [0.0, 0.0, 0.0, 0])
    b[0] += kwh; b[1] += pre_gct; b[2] += gct; b[3] += 1

print('rows skipped (already-correct KSAN/KSAS/Portmore population):', skipped)
print('rows unparseable parish field:', skip_unparseable)
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
print('PREPAID PUSH V2 DONE')
