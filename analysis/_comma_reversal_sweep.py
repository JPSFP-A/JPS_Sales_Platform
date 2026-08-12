# -*- coding: utf-8 -*-
# Sweep every locally available raw Billing Details Report for rows whose Cust_Code
# still carries the stray thousands-comma (e.g. "100,185") -- these are exactly the
# rows the OLD (pre-fix) NUM()/code-parsing in corrected_scan.py would have silently
# mis-parsed or key-mismatched, the same bug found for Alcoa's Jul/Aug-2025 RT70
# reversal. Report every match (account, month, sign, magnitude) so each can be
# checked against jps_actuals individually before any correction is applied.
#
# Two-pass per xlsx file: pass 1 reads ONLY the Cust_Code column (fast — skips
# parsing the other 68 columns' XML in read_only mode) to find hit row numbers;
# pass 2 re-walks the sheet and only fully-parses rows at those positions. For
# the (expected) common case of zero hits, this is much faster than one full
# 69-column pass over a 300MB+ file.
import csv, glob, openpyxl, re, sys, time

FILES = sorted(set(
    glob.glob('Billing Details Report*.xls*') +
    glob.glob('Billing Details Report*.xls') +
    ['Jul 25.csv', 'Aug 25.csv']
))
MONNUM = {'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}


def parse_month(fn):
    m = re.search(r'(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*[ _-]*(\d{4}|\d{2})\b', fn.upper())
    if not m:
        return None
    y = m.group(2)
    y = '20' + y if len(y) == 2 else y
    return f'{y}-{MONNUM[m.group(1)]:02d}'


def is_zip(path):
    with open(path, 'rb') as f:
        return f.read(2) == b'PK'


def find_detail_sheet(wb):
    for sn in wb.sheetnames:
        ws = wb[sn]
        for i, r in enumerate(ws.iter_rows(max_col=1, values_only=True)):
            if r and r[0] == 'Cust_Code':
                return sn
            if i > 8:
                break
    return None


def xlsx_hits(path):
    """Yields full rows (as tuples) for every data row whose col-A value contains a comma."""
    wb = openpyxl.load_workbook(path, read_only=True)
    detail = find_detail_sheet(wb)
    if not detail:
        wb.close()
        return
    ws = wb[detail]
    hdr = None
    hit_rownums = []
    total = 0
    for i, r in enumerate(ws.iter_rows(max_col=1, values_only=True)):
        if hdr is None:
            if r and str(r[0]).strip() == 'Cust_Code':
                hdr = True
            continue
        total += 1
        v = r[0]
        if v is not None and ',' in str(v):
            hit_rownums.append(i)
    wb.close()
    print(f'   pass1: {total} rows scanned, {len(hit_rownums)} comma hits', flush=True)
    if not hit_rownums:
        return
    hitset = set(hit_rownums)
    wb2 = openpyxl.load_workbook(path, read_only=True)
    ws2 = wb2[detail]
    hdr2 = None
    for i, r in enumerate(ws2.iter_rows(values_only=True)):
        if hdr2 is None:
            if r and str(r[0]).strip() == 'Cust_Code':
                hdr2 = list(r)
            continue
        if i in hitset:
            yield hdr2, r
    wb2.close()


def rows_tsv(path):
    with open(path, encoding='latin-1', errors='replace') as f:
        for line in f:
            yield tuple(line.rstrip('\r\n').split('\t'))


def rows_csv(path):
    with open(path, encoding='latin-1', errors='replace', newline='') as f:
        for r in csv.reader(f):
            yield tuple(r)


def NUM(v):
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        v = v.strip().replace(',', '')
        if v == '':
            return 0.0
        try:
            return float(v)
        except ValueError:
            return 0.0
    return 0.0


def extract(hdr, r):
    I = {n: i for i, n in enumerate(hdr) if n}
    g = lambda k: r[I[k]] if k in I and I[k] < len(r) else None
    code = str(g('Cust_Code') or '').strip().replace(',', '')
    prem = str(g('Prem_Code') or '').strip()
    return (code, prem, g('Name'), g('rate_class'), g('Srat_Code'),
            NUM(g('net_kwh_billed_consump')), NUM(g('net_billed_revenue')), g('cust_billed'))


def proc_text(path, rows):
    mo = parse_month(path)
    hdr = None
    hits = []
    total = 0
    for r in rows:
        if hdr is None:
            if r and str(r[0]).strip() == 'Cust_Code':
                hdr = list(r)
            continue
        total += 1
        if not r or len(r) <= 0:
            continue
        raw_code = r[0]
        if raw_code is None or ',' not in str(raw_code):
            continue
        hits.append(extract(hdr, r))
    print(f'{mo}  ({path})  rows scanned: {total}  comma-Cust_Code hits: {len(hits)}', flush=True)
    for h in hits:
        print('   ', h, flush=True)


def proc(path):
    mo = parse_month(path)
    if not mo:
        print(f'{path}: cannot parse month, SKIPPING', flush=True)
        return
    t0 = time.time()
    if path.lower().endswith('.csv'):
        proc_text(path, rows_csv(path))
    elif is_zip(path):
        print(f'{mo}  ({path})  scanning...', flush=True)
        hits = list(xlsx_hits(path))
        print(f'{mo}  ({path})  comma-Cust_Code hits: {len(hits)}  ({time.time()-t0:.0f}s)', flush=True)
        for hdr, r in hits:
            print('   ', extract(hdr, r), flush=True)
    else:
        proc_text(path, rows_tsv(path))


for f in FILES:
    try:
        proc(f)
    except Exception as e:
        print(f'{f}: ERROR {e!r}', flush=True)
print('SWEEP DONE', flush=True)
