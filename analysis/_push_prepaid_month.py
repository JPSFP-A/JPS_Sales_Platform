# -*- coding: utf-8 -*-
# Loads ONE month of prepaid (PAYG) from a Customer-Monthly-Transaction-Report CSV into
# jps_actuals, using the same parish resolution and tariff-based GCT back-out as
# _push_prepaid_backfill.py (CSV reports carry only the GST-inclusive total).
# Usage: python _push_prepaid_month.py <file.csv> <YYYY-MM> [--dry-run]
import csv, json, sys, time, requests

src = open(r'C:\Projects\Sales_Platform\analysis\_push_prepaid_backfill.py', encoding='utf-8').read()
head = src.split('FILES = {')[0].replace('D:\\Projects\\DataManager', 'C:\\Projects\\DataManager')
exec(head)

fn = [a for a in sys.argv[1:] if not a.startswith('--')][0]
mo = [a for a in sys.argv[1:] if not a.startswith('--')][1]
Y, M = int(mo[:4]), int(mo[5:7])

with open(fn, encoding='utf-8', errors='replace', newline='') as f:
    rows = list(csv.reader(f))
hdr_map = {h: i for i, h in enumerate(rows[0])}
c_tariff = find_col(hdr_map, 'Tariff'); c_parish = find_col(hdr_map, 'Parish')
c_kwh = find_col(hdr_map, 'Kwh', 'KWh', 'kwh'); c_amt = find_col(hdr_map, 'Total_Amount', 'Amount', ' Total_Amount ')
c_month = find_col(hdr_map, 'Month')

buckets = {}; months_seen = set(); unmapped = 0
for r in rows[1:]:
    if not r or len(r) <= max(c_tariff, c_parish, c_kwh, c_amt, c_month):
        continue
    months_seen.add(r[c_month].strip())
    tariff = str(r[c_tariff] or '').strip()
    rc = 'RT20' if tariff == 'RT20-PAYG' else 'RT10'
    parish = resolve_parish(r[c_parish])
    unmapped += parish == 'UNMAPPED'
    kwh = parse_amount(r[c_kwh]); total = parse_amount(r[c_amt])
    rate = GCT_RATE_BY_TARIFF.get(tariff, GCT_RATE_BY_TARIFF['unassigned'])
    pre = total / (1 + rate)
    b = buckets.setdefault((rc, parish), [0.0, 0.0, 0.0, 0])
    b[0] += kwh; b[1] += pre; b[2] += total - pre; b[3] += 1

assert months_seen == {mo}, f'file months {months_seen} != {mo}'
print('unmapped parish rows:', unmapped)
for rc in ('RT10', 'RT20'):
    k = sum(v[0] for (c, p), v in buckets.items() if c == rc); rv = sum(v[1] for (c, p), v in buckets.items() if c == rc)
    n = sum(v[3] for (c, p), v in buckets.items() if c == rc)
    print(f'{rc}: customers {n:,}  {k/1e3:,.1f} MWh  pre-GCT J${rv/1e6:,.2f}M')

push_rows = [{'jps_ac': '', 'year': Y, 'month': M, 'rate_class': rc, 'name': None, 'consumption_bucket': 'Prepaid',
              'parish': parish, 'kwh': kwh, 'revenue_jmd': rev, 'demand_jmd': 0.0, 'fuel_jmd': 0.0, 'energy_jmd': 0.0,
              'ipp_jmd': 0.0, 'customer_charge_jmd': 0.0, 'gct_jmd': gct, 'customer_count': cnt,
              'segment': 'Residential'}
             for (rc, parish), (kwh, rev, gct, cnt) in buckets.items()]
if '--dry-run' in sys.argv:
    print('DRY RUN,', len(push_rows), 'rows, not pushing'); sys.exit(0)
pushed = 0
for i in range(0, len(push_rows), 200):
    chunk = push_rows[i:i + 200]
    for attempt in range(5):
        resp = requests.post(URL + '?on_conflict=year,month,jps_ac,rate_class,parish,consumption_bucket',
                             headers=HDRS, data=json.dumps(chunk), timeout=60)
        if resp.status_code < 300:
            pushed += len(chunk); break
        time.sleep(2)
    else:
        raise SystemExit('batch failed: %s %s' % (resp.status_code, resp.text[:300]))
print('pushed', pushed, 'rows')
