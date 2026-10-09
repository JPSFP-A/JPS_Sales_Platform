# -*- coding: utf-8 -*-
# Adds the prepaid-tagged billed rows the standard scan leaves out of a month's jps_actuals:
#   (EV-tariff premises are flagged cust_billed=0 and stay excluded like every other not-billed row.)
#   PR (prepaid-tagged RT10) rows in the postpaid file with cust_billed=='1'. Most of these
#      premises also appear in the prepaid transaction report, but with different kWh (the
#      two are separate billing records); the Earnings Sheet counts both, so both are loaded.
#      Added into the existing RT10 (PR) / RT20 (PC) 'Prepaid' bucket rows by parish.
# All other cust_billed!=1 rows stay excluded (RT10/RT20 credits, deposits, admin charges).
#
# Idempotent: PR/PC additions are recorded in _month_adj_applied_<YYYY-MM>.json; a re-run
# backs the prior additions out of the live row before adding the new ones.
# Usage: python _push_month_adjustments.py <YYYY-MM> [--dry-run]
import csv, glob, json, os, re, sys, requests
csv.field_size_limit(10**9)

src = open(r'C:\Projects\Sales_Platform\analysis\_push_prepaid_backfill.py', encoding='utf-8').read()
head = src.split('FILES = {')[0].replace('D:\\Projects\\DataManager', 'C:\\Projects\\DataManager')
exec(head)   # URL, HDRS, PMAP, norm, resolve_parish, parse_amount, find_col

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
mo = [a for a in sys.argv[1:] if not a.startswith('--')][0]
DRY = '--dry-run' in sys.argv
Y, M = int(mo[:4]), int(mo[5:7])
MONTH3 = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'][M - 1].title()
raw_file = '%s %02d.csv' % (MONTH3, Y % 100)
prepaid_glob = glob.glob('Customer-Monthly-Transaction-Report-%d-%02d.*' % (M, Y % 100)) + \
               glob.glob('Customer-Monthly-Transaction-Report-%d_%02d.*' % (M, Y % 100))
prepaid_glob = [c for c in prepaid_glob if 'unass' not in c.lower()]
assert prepaid_glob, 'no prepaid transaction report found for ' + mo

def num(x):
    try: return float(str(x).replace(',', '') or 0)
    except Exception: return 0.0

def prepaid_premises(f):
    prem = set()
    if f.lower().endswith('.csv'):
        with open(f, encoding='cp1252', errors='replace', newline='') as fh:
            rd = csv.reader(fh); h = [c.strip().lower() for c in next(rd)]
            ja, pn = h.index('jpsaccount'), h.index('premise_number')
            for r in rd:
                if len(r) > max(ja, pn): prem.add((r[ja].strip(), r[pn].strip()))
    else:
        import openpyxl
        ws = openpyxl.load_workbook(f, read_only=True)['Sheet-0']
        for i, r in enumerate(ws.iter_rows(values_only=True)):
            if i == 0 or not r[0]: continue
            prem.add((str(r[1]).strip(), str(r[2]).strip()))
    return prem


def parish_of(raw):
    pg = PMAP.get(norm(raw))
    return pg if pg else resolve_parish(raw)

pr = {}; n_pr = 0; unmapped = 0
with open(raw_file, encoding='utf-8', errors='replace', newline='') as fh:
    for r in csv.DictReader(fh):
        rc = (r.get('rate_class') or '').strip(); cb = (r.get('cust_billed') or '').strip()
        code = (r.get('Cust_Code') or '').strip().replace(',', ''); prem = (r.get('Prem_Code') or '').strip()
        if rc == 'PR' and cb == '1':   # PC (RT20) rows are already in the standard RT20 postpaid load
            pg = parish_of(r.get('Parish')); unmapped += pg == 'UNMAPPED'
            k = ('RT20' if rc == 'PC' else 'RT10', pg)
            a = pr.setdefault(k, {'kwh': 0.0, 'rev': 0.0, 'gct': 0.0, 'cnt': 0})
            a['kwh'] += num(r.get('net_kwh_billed_consump')); a['rev'] += num(r.get('net_revenue')); a['gct'] += num(r.get('GCT')); a['cnt'] += 1
            n_pr += 1
print('PR rows added %d | unmapped parish %d' % (n_pr, unmapped))
for rc in ('RT10',):
    print('%s PR kWh %.0f  rev %.0f  premises %d' % (rc, sum(a['kwh'] for (c, p), a in pr.items() if c == rc),
          sum(a['rev'] for (c, p), a in pr.items() if c == rc), sum(a['cnt'] for (c, p), a in pr.items() if c == rc)))

def get(params):
    r = requests.get(URL + '?' + params, headers=HDRS, timeout=60); r.raise_for_status(); return r.json()

applied_f = '_month_adj_applied_%s.json' % mo
prev = json.load(open(applied_f)) if os.path.exists(applied_f) else {}
push = []
for pk in sorted(set(pr) | {tuple(k.split('|', 1)) for k in prev}):   # include keys from a prior run that no longer apply, to back them out
    rc, pg = pk; a = pr.get(pk, {'kwh': 0.0, 'rev': 0.0, 'gct': 0.0, 'cnt': 0})
    live = get('year=eq.%d&month=eq.%d&rate_class=eq.%s&parish=eq.%s&consumption_bucket=eq.Prepaid&jps_ac=eq.' % (Y, M, rc, requests.utils.quote(pg)))
    p = prev.get(rc + '|' + pg, {'kwh': 0, 'rev': 0, 'gct': 0, 'cnt': 0})
    if live:
        L = live[0]
        row = {'jps_ac': '', 'year': Y, 'month': M, 'rate_class': rc, 'name': None, 'consumption_bucket': 'Prepaid', 'parish': pg,
               'kwh': float(L['kwh']) - p['kwh'] + a['kwh'], 'revenue_jmd': float(L['revenue_jmd']) - p['rev'] + a['rev'],
               'gct_jmd': float(L['gct_jmd'] or 0) - p['gct'] + a['gct'], 'customer_count': int(L['customer_count'] or 0) - p['cnt'] + a['cnt'],
               'demand_jmd': 0.0, 'fuel_jmd': 0.0, 'energy_jmd': 0.0, 'ipp_jmd': 0.0, 'customer_charge_jmd': 0.0, 'segment': 'Residential'}
    else:
        row = {'jps_ac': '', 'year': Y, 'month': M, 'rate_class': rc, 'name': None, 'consumption_bucket': 'Prepaid', 'parish': pg,
               'kwh': a['kwh'], 'revenue_jmd': a['rev'], 'gct_jmd': a['gct'], 'customer_count': a['cnt'],
               'demand_jmd': 0.0, 'fuel_jmd': 0.0, 'energy_jmd': 0.0, 'ipp_jmd': 0.0, 'customer_charge_jmd': 0.0, 'segment': 'Residential'}
    push.append(row)
KEYS = sorted({k for r in push for k in r})
push = [{k: (r.get(k) if k != 'segment' else r.get(k, '')) for k in KEYS} for r in push]   # segment is NOT NULL, '' for account classes   # PostgREST needs identical keys per batch
print('rows to upsert:', len(push), '(prepaid-bucket merges)')
if DRY:
    print('DRY RUN, nothing pushed'); sys.exit(0)
for i in range(0, len(push), 200):
    resp = requests.post(URL + '?on_conflict=year,month,jps_ac,rate_class,parish,consumption_bucket', headers=HDRS,
                         data=json.dumps(push[i:i + 200]), timeout=60)
    if resp.status_code >= 300: raise SystemExit('batch failed: %s %s' % (resp.status_code, resp.text[:300]))
json.dump({rc + '|' + pg: a for (rc, pg), a in pr.items()}, open(applied_f, 'w'))
print('pushed', len(push), 'rows; refreshing views')
r = requests.post(URL.replace('/jps_actuals', '/rpc/refresh_sales_mvs'), headers=HDRS, data='{}', timeout=180)
print('refresh_sales_mvs', r.status_code, r.text[:200])
