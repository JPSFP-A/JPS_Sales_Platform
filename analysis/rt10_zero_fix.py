# -*- coding: utf-8 -*-
# Re-scans the raw monthly Billing Details Report files for RT10 rows only, with a
# finer bin scheme that isolates TRUE zero-kWh consumption (kwh==0 exactly) from the
# [1,50) range -- corrected.json's existing 50kWh-wide "0" bin conflates the two,
# which caused the Zero-tier bug (2.1M+ kWh of real consumption mislabeled as "Zero").
# Country-wide aggregate only (parish='ALL'), matching RT10's existing jps_actuals grain.
import csv, glob, json, os, re, sys

DL = r'C:\Users\jwilson\Downloads'
HERE = os.path.dirname(os.path.abspath(__file__))

MONNUM = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6, 'JUL': 7, 'AUG': 8,
          'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}


def discover_billing_files():
    files = {}
    # Raw CIS exports are named "<Mon> <YY>.<ext>" (e.g. "Jul 26.csv", "Aug 26.xls");
    # only the "Billing Details Report ..." form was matched here, so a month that
    # arrived under the short name was silently absent. Mirrors corrected_scan.py.
    for pat in ('*.csv', '*.xls', '*.xlsx'):
        for fp in sorted(set(glob.glob(os.path.join(DL, pat)) + glob.glob(os.path.join(HERE, pat)))):
            base = os.path.basename(fp)
            m = re.match(r'(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+(\d{2})\.(CSV|XLS|XLSX)$', base.upper())
            if not m:
                continue
            key = '20%s-%02d' % (m.group(2), MONNUM[m.group(1)])
            files.setdefault(key, fp)
    cands = sorted(set(glob.glob(os.path.join(DL, 'Billing Details Report*.xls*')) + glob.glob(os.path.join(HERE, 'Billing Details Report*.xls*'))))
    for fp in cands:
        base = os.path.basename(fp)
        m = re.search(r'(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*[ _-]*(\d{4})', base.upper())
        if not m:
            continue
        key = '%s-%02d' % (m.group(2), MONNUM[m.group(1)])
        if key not in files:
            files[key] = fp
    csv_cands = sorted(set(glob.glob(os.path.join(DL, '*.csv')) + glob.glob(os.path.join(HERE, '*.csv'))))
    for fp in csv_cands:
        base = os.path.basename(fp)
        m = re.match(r'(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+(\d{2})\.CSV$', base.upper())
        if not m:
            continue
        key = '20%s-%02d' % (m.group(2), MONNUM[m.group(1)])
        if key not in files:
            files[key] = fp
    return dict(sorted(files.items()))


def NUM(v):
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        v = v.strip()
        if v == '':
            return 0.0
        try:
            return float(v)
        except ValueError:
            return 0.0
    return 0.0


def norm(s):
    return str(s).strip().upper()


RMAP = {}
RCMAP = {}
for r in list(csv.reader(open(DL + r'\Rate categorry Data mapping.csv')))[1:]:
    if len(r) >= 3:
        RMAP[norm(r[2])] = r[0]
        if norm(r[1]) not in RCMAP:
            RCMAP[norm(r[1])] = r[0]


def title_of(rc, srat):
    return RCMAP.get(norm(rc)) or RMAP.get(norm(srat))


def _is_zip_xlsx(path):
    with open(path, 'rb') as f:
        return f.read(2) == b'PK'


def _rows_xlsx(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True)
    detail = None
    for sn in wb.sheetnames:
        ws = wb[sn]
        for i, r in enumerate(ws.iter_rows(values_only=True)):
            if r and r[0] == 'Cust_Code':
                detail = sn
                break
            if i > 8:
                break
        if detail:
            break
    ws = wb[detail]
    for r in ws.iter_rows(values_only=True):
        yield r
    wb.close()


def _rows_tsv(path):
    with open(path, encoding='latin-1', errors='replace') as f:
        for line in f:
            yield tuple(line.rstrip('\r\n').split('\t'))


def _rows_csv(path):
    with open(path, encoding='utf-8', errors='replace', newline='') as f:
        for r in csv.reader(f):
            yield tuple(r)


def proc_rt10(path):
    if path.lower().endswith('.csv'):
        rows = _rows_csv(path)
    else:
        rows = _rows_xlsx(path) if _is_zip_xlsx(path) else _rows_tsv(path)
    hdr = None
    for r in rows:
        if r and r[0] == 'Cust_Code':
            hdr = list(r)
            break
    I = {n: k for k, n in enumerate(hdr) if n}
    g = lambda r, n: NUM(r[I[n]]) if n in I and I[n] < len(r) else 0.0
    gv = lambda r, n: (r[I[n]] if n in I and I[n] < len(r) else None)

    # [count, kwh, rev, energy, fuel, ipp, cust_charge] per tier
    tiers = {'TrueZero': [0.0] * 7, '<150': [0.0] * 7}
    n = 0
    for r in rows:
        code = r[I['Cust_Code']] if I.get('Cust_Code', -1) < len(r) else None
        if code in (None, '', 'Cust_Code'):
            continue
        # Whitelist, not blacklist -- matches corrected_scan.py's fix (2026-09-08):
        # cust_billed's only confirmed "really billed" value is '1'. Everything else
        # ('0', blank, or an unexpected flag like 'Y' -- seen tagging rows with
        # net_revenue=net_kwh=0, a zero-billed row tagged differently, not a second
        # billed state) defaults to excluded so a future flag value can't silently
        # slip through as billed.
        cb = str(gv(r, 'cust_billed') or '').strip()
        if cb != '1':
            continue
        rc = str(gv(r, 'rate_class'))
        if rc.strip() in ('PR', 'PC'):
            # PR/PC = prepaid/PAYG meter (CIS's own tag), distinct from the RT10-PAYG
            # srat codes. Missing this exclusion let 88 prepaid-tagged rows (2,437.66
            # kWh, all correctly cust_billed=1 and in [0,150)) get classified as RT10
            # via title_of() below and counted here, on top of what the separate
            # prepaid pipeline (_push_prepaid_v3.py) already counts for the same
            # premises -- caught 2026-09-08 by _push_rt10_buckets.py's reconciliation
            # gate refusing to push because this script's total no longer matched
            # corrected_scan.py's (which has excluded PR/PC all along).
            continue
        srat = str(gv(r, 'Srat_Code'))
        title = title_of(rc, srat)
        if title != 'RT10':
            continue
        kwh = g(r, 'net_kwh_billed_consump')
        if not (0 <= kwh < 150):
            continue  # only re-deriving the Zero/<150 split; other tiers unaffected
        n += 1
        rev = g(r, 'net_revenue')
        en = g(r, 'KWHP_KWH_Energy') + g(r, 'KWHL_Energy') + g(r, 'KWHO_Energy')
        fu = g(r, 'fuel') + g(r, 'FuelOffPeak') + g(r, 'FuelPartialPeak') + g(r, 'FuelOnPeak')
        ip = g(r, 'IPP_Charge')
        cc = g(r, 'Cust_Charge')
        tier = tiers['TrueZero'] if kwh == 0 else tiers['<150']
        tier[0] += 1; tier[1] += kwh; tier[2] += rev; tier[3] += en; tier[4] += fu; tier[5] += ip; tier[6] += cc
    return tiers, n


if __name__ == '__main__':
    files = discover_billing_files()
    # Was a hardcoded range ending at 2026-07, so every new month had to be typed in
    # or it silently never processed. Take whatever the discovery found from 2025 on.
    need = sorted(mo for mo in files if mo >= '2025-01')
    # Optional month filter: `python rt10_zero_fix.py 2026-08` reprocesses that month
    # only. Each pass is a full scan of a ~300MB export, so redoing twenty closed
    # months to pick up one new one costs the better part of an hour for no change.
    want = [a for a in sys.argv[1:] if not a.startswith('-')]
    if want:
        need = [mo for mo in need if mo in want]
        if not need:
            print('no discovered billing file for', want)
            raise SystemExit(1)
    # Merge into the existing result rather than starting empty -- a filtered run that
    # dumped only what it processed would silently drop every other month from the file.
    out = json.load(open('rt10_zero_fix_result.json')) if os.path.exists('rt10_zero_fix_result.json') else {}
    for mo in need:
        if mo not in files:
            continue
        print('processing', mo, files[mo], flush=True)
        tiers, n = proc_rt10(files[mo])
        out[mo] = tiers
        print('  ', mo, 'TrueZero: count=%d kwh=%.2f rev=%.2f | <150: count=%d kwh=%.2f rev=%.2f | rows in [0,150)=%d' % (
            tiers['TrueZero'][0], tiers['TrueZero'][1], tiers['TrueZero'][2],
            tiers['<150'][0], tiers['<150'][1], tiers['<150'][2], n), flush=True)
    json.dump(out, open('rt10_zero_fix_result.json', 'w'))
    print('WROTE rt10_zero_fix_result.json')
