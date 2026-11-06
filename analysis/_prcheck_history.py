# -*- coding: utf-8 -*-
# For every month: PR/PC-tagged rows in the postpaid file, and how many of those premises
# also appear in that month's prepaid (PAYG) transaction report, with kWh covered vs not.
import csv, glob, re, json, os, openpyxl
csv.field_size_limit(10**9)
MON = {'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
def num(x):
    try: return float(str(x).replace(',', '') or 0)
    except: return 0.0
def prepaid_premises(y, m):
    cands = glob.glob('Customer-Monthly-Transaction-Report-%d-%02d.*' % (m, y % 100)) + glob.glob('Customer-Monthly-Transaction-Report-%d_%02d.*' % (m, y % 100))
    cands = [c for c in cands if 'unass' not in c.lower()]
    if not cands: return None
    f = cands[0]; prem = set()
    if f.lower().endswith('.csv'):
        with open(f, encoding='cp1252', errors='replace', newline='') as fh:
            rd = csv.reader(fh); h = [c.strip().lower() for c in next(rd)]
            ja, pn = h.index('jpsaccount'), h.index('premise_number')
            for r in rd:
                if len(r) > max(ja, pn): prem.add((r[ja].strip(), r[pn].strip()))
    else:
        wb = openpyxl.load_workbook(f, read_only=True); ws = wb['Sheet-0']
        for i, r in enumerate(ws.iter_rows(values_only=True)):
            if i == 0 or not r[0]: continue
            prem.add((str(r[1]).strip(), str(r[2]).strip()))
    return prem
out = {}
for f in sorted(glob.glob('??? ??.csv')):
    m = re.match(r'(?i)^([a-z]{3}) (\d\d)\.csv$', f)
    if not m: continue
    y = 2000 + int(m.group(2)); mo = MON[m.group(1).upper()]
    if y < 2025: continue
    prem = prepaid_premises(y, mo)
    rows = cov = 0; k = kc = ku = rev = 0.0; unb = ev = 0
    with open(f, encoding='utf-8', errors='ignore', newline='') as fh:
        for r in csv.DictReader(fh):
            rc = (r.get('rate_class') or '').strip()
            if rc in ('PR', 'PC') and (r.get('cust_billed') or '').strip() == '1':
                rows += 1; kw = num(r.get('net_kwh_billed_consump')); k += kw; rev += num(r.get('net_revenue'))
                key = ((r.get('Cust_Code') or '').strip().replace(',', ''), (r.get('Prem_Code') or '').strip())
                if prem is not None and key in prem: cov += 1; kc += kw
                else: ku += kw
    out['%d-%02d' % (y, mo)] = dict(rows=rows, covered=cov, kwh=k, kwh_covered=kc, kwh_uncovered=ku, rev=rev, report=prem is not None)
    print('%d-%02d rows %4d covered %4d kWh %9.0f (covered %8.0f, uncovered %9.0f) rev %.0f report=%s' % (y, mo, rows, cov, k, kc, ku, rev, prem is not None), flush=True)
    json.dump(out, open('_prcheck_history.json', 'w'))
print('DONE', flush=True)
