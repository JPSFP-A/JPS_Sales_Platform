# -*- coding: utf-8 -*-
# Backfills Prepaid (PAYG) data for all months that were sitting in local
# Customer-Monthly-Transaction-Report files but never loaded (Jan 2025-May 2026;
# Jun/Jul 2026 already loaded via _push_prepaid_v3.py). Uses the same canonical
# Parish Grouping.csv resolution as v3.
#
# These historical files have inconsistent formats vs the July 2026 reference:
#  - Some have a plain "Amount" column (GCT-inclusive, no Pre_GCT/GCT breakout) --
#    Jan 2025 xlsx/csv also had a Total already, no separate GCT ever available
#    in ANY of these files except the one July 2026 upload.
#  - Column header whitespace varies (" Total_Amount " etc).
#  - Amount values are comma-formatted strings, sometimes with surrounding spaces.
#  - Parish field format varies: most are "City, Admin Parish" (same as July),
#    but some (e.g. Jan 2025) are just the admin parish name alone, no city.
#
# Since none of these files carry a separate GCT column, pre-GCT revenue is
# backed out using the GCT rate empirically verified against the one file that
# DID have both (July 2026 xlsx): GCT / Pre_GCT = 7.00% exactly, consistently,
# across multiple sampled rows. revenue_jmd (this pipeline's pre-GCT convention,
# matching every other jps_actuals load) = total_amount / 1.07.
import csv, json, glob, os, re, sys, requests, time

SECRET = open(r'D:\Projects\DataManager\.env').read().split('=', 1)[1].strip()
URL = 'https://bhrswnbenkvflpdjhfpa.supabase.co/rest/v1/jps_actuals'
HDRS = {'apikey': SECRET, 'Authorization': 'Bearer ' + SECRET, 'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates,return=minimal'}
GCT_RATE = 0.07
DRY_RUN = '--dry-run' in sys.argv

PMAP = {}
def norm(s):
    return str(s).strip().upper()
with open(r'C:\Users\jwilson\Downloads\Parish Grouping.csv', encoding='utf-8-sig') as f:
    for r in list(csv.reader(f))[1:]:
        if len(r) >= 2:
            PMAP[norm(r[0])] = r[1]

CITY_ALIAS = {'ST ANNS BAY': "ST. ANN'S BAY"}
SAINT_NORM = {
    'SAINT ANN': 'St. Ann', 'SAINT CATHERINE': 'St. Catherine', 'SAINT ELIZABETH': 'St. Elizabeth',
    'SAINT JAMES': 'St. James', 'SAINT MARY': 'St. Mary', 'SAINT THOMAS': 'St. Thomas',
    'CLARENDON': 'Clarendon', 'HANOVER': 'Hanover', 'MANCHESTER': 'Manchester',
    'PORTLAND': 'Portland', 'TRELAWNY': 'Trelawny', 'WESTMORELAND': 'Westmoreland',
    'PORTMORE': 'Portmore', 'KSAN': 'KSAN', 'KSAS': 'KSAS',
}
# Some historical files put a bare CITY name (not the admin parish, and no comma
# to disambiguate) directly in the Parish field -- e.g. Jan 2025's "Spanish Town",
# "Mandeville", "KSA North". Same town->parish resolution as the July load.
TOWN_TO_PARISH = {
    'SPANISH TOWN': 'St. Catherine', 'OLD HARBOUR': 'St. Catherine',
    'ST ANNS BAY': 'St. Ann', "ST. ANN'S BAY": 'St. Ann',
    'MANDEVILLE': 'Manchester', 'MONTEGO BAY': 'St. James', 'MAY PEN': 'Clarendon',
    'BLACK RIVER': 'St. Elizabeth', 'SAVANNA-LA-MAR': 'Westmoreland', 'SAV-LA-MAR': 'Westmoreland',
    'PORT ANTONIO': 'Portland', 'PORT MARIA': 'St. Mary', 'ST MARY': 'St. Mary',
    'FALMOUTH': 'Trelawny', 'MORANT BAY': 'St. Thomas', 'LUCEA': 'Hanover',
    'KSA NORTH': 'KSAN', 'KSA SOUTH': 'KSAS',
}
AMBIGUOUS_BARE = {'KINGSTON', 'SAINT ANDREW', 'KINGSTON & ST ANDREW'}


def resolve_parish(raw):
    """Handles both 'City, Admin Parish' (most files) and bare (some older files,
    e.g. Jan 2025) formats -- and bare can itself be either a city/town name or
    an admin parish name, unpredictably, in the same file."""
    if not raw:
        return 'UNMAPPED'
    raw = str(raw)
    if ',' in raw:
        pg = PMAP.get(norm(raw))
        if pg:
            return pg
        city = raw.split(',', 1)[0].strip()
        pg = PMAP.get(norm(city))
        if pg:
            return pg
        alias = CITY_ALIAS.get(norm(city))
        if alias:
            pg = PMAP.get(norm(alias))
            if pg:
                return pg
        admin = raw.split(',', 1)[1].strip()
        return SAINT_NORM.get(norm(admin), 'UNMAPPED')
    n = norm(raw)
    if n in AMBIGUOUS_BARE:
        return 'UNMAPPED'  # can't split KSAN/KSAS without a city or explicit tag
    if n in TOWN_TO_PARISH:
        return TOWN_TO_PARISH[n]
    return SAINT_NORM.get(n, 'UNMAPPED')


def find_col(hdr_map, *candidates):
    for c in candidates:
        if c in hdr_map:
            return hdr_map[c]
    # fuzzy: normalize whitespace/case
    norm_map = {k.strip().lower(): v for k, v in hdr_map.items()}
    for c in candidates:
        if c.strip().lower() in norm_map:
            return norm_map[c.strip().lower()]
    return None


def parse_amount(v):
    if v is None:
        return 0.0
    v = str(v).strip().replace(',', '')
    if v == '':
        return 0.0
    try:
        return float(v)
    except ValueError:
        return 0.0


FILES = {
    '2025-01': 'Customer-Monthly-Transaction-Report-1_25.csv',
    '2025-02': 'Customer-Monthly-Transaction-Report-2_25.csv',
    '2025-03': 'Customer-Monthly-Transaction-Report-3_25.csv',
    '2025-04': 'Customer-Monthly-Transaction-Report-4_25.csv',
    '2025-05': 'Customer-Monthly-Transaction-Report-5_25.csv',
    '2025-06': 'Customer-Monthly-Transaction-Report-6-25.csv',
    '2025-07': 'Customer-Monthly-Transaction-Report-7-25.csv',
    '2025-08': 'Customer-Monthly-Transaction-Report-8-25.csv',
    '2025-09': 'Customer-Monthly-Transaction-Report-9-25.csv',
    '2025-10': 'Customer-Monthly-Transaction-Report-10-25.csv',
    '2025-11': 'Customer-Monthly-Transaction-Report-11-25.csv',
    '2025-12': 'Customer-Monthly-Transaction-Report-12-25.csv',
    '2026-01': 'Customer-Monthly-Transaction-Report-1-26.csv',
    '2026-02': 'Customer-Monthly-Transaction-Report-2-26.csv',
    '2026-03': 'Customer-Monthly-Transaction-Report-3-26.csv',
    '2026-04': 'Customer-Monthly-Transaction-Report-4-26.csv',
    '2026-05': 'Customer-Monthly-Transaction-Report-5-26.csv',
}

KEYS = ['jps_ac', 'year', 'month', 'rate_class', 'name', 'consumption_bucket', 'parish', 'kwh', 'revenue_jmd',
        'demand_jmd', 'fuel_jmd', 'energy_jmd', 'ipp_jmd', 'customer_charge_jmd', 'gct_jmd', 'customer_count', 'segment']


def push(rows_out):
    if DRY_RUN:
        return len(rows_out)
    BATCH = 200
    pushed = 0
    for i in range(0, len(rows_out), BATCH):
        chunk = rows_out[i:i + BATCH]
        ok = False
        last = None
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
            print('BATCH FAILED', last, flush=True)
            continue
        pushed += len(chunk)
    return pushed


grand_total = 0
for mo, fn in sorted(FILES.items()):
    if not os.path.exists(fn):
        print(mo, 'FILE MISSING:', fn, flush=True)
        continue
    Y, M = int(mo[:4]), int(mo[5:7])
    with open(fn, encoding='utf-8', errors='replace', newline='') as f:
        rows = list(csv.reader(f))
    hdr = rows[0]
    hdr_map = {h: i for i, h in enumerate(hdr)}
    c_tariff = find_col(hdr_map, 'Tariff')
    c_parish = find_col(hdr_map, 'Parish')
    c_kwh = find_col(hdr_map, 'Kwh', 'KWh', 'kwh')
    c_amt = find_col(hdr_map, 'Total_Amount', 'Amount', ' Total_Amount ')
    c_month = find_col(hdr_map, 'Month')

    buckets = {}  # (rate_class, parish) -> [kwh, rev, gct, cust_count]
    unmapped_n = 0
    for r in rows[1:]:
        if not r or len(r) <= max(c_tariff, c_parish, c_kwh, c_amt):
            continue
        tariff = str(r[c_tariff] or '').strip()
        if tariff == 'RT10-PAYG':
            rc = 'RT10'
        elif tariff == 'RT20-PAYG':
            rc = 'RT20'
        else:
            rc = 'UNASSIGNED-PAYG'
        parish = resolve_parish(r[c_parish])
        if parish == 'UNMAPPED':
            unmapped_n += 1
        kwh = parse_amount(r[c_kwh])
        total_amt = parse_amount(r[c_amt])
        pre_gct = total_amt / (1 + GCT_RATE)
        gct = total_amt - pre_gct
        key = (rc, parish)
        b = buckets.setdefault(key, [0.0, 0.0, 0.0, 0])
        b[0] += kwh; b[1] += pre_gct; b[2] += gct; b[3] += 1

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

    n = push(push_rows)
    grand_total += n
    tot_kwh = sum(v[0] for v in buckets.values())
    tot_rev = sum(v[1] for v in buckets.values())
    print(f'{mo}: rows_in_file={len(rows)-1} unmapped_parish={unmapped_n} buckets_pushed={n} '
          f'total_kwh={tot_kwh:,.2f} total_rev={tot_rev:,.2f}', flush=True)

print('GRAND TOTAL PUSHED:', grand_total, flush=True)
print('PREPAID BACKFILL DONE', flush=True)
