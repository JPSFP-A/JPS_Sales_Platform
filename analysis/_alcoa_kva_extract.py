# -*- coding: utf-8 -*-
# Pull the TRUE kva_billed_consump (actual metered KVA, not demand$/rate) for Alcoa
# for every locally available raw file -- demand$/rate doesn't always match the true
# reading (ratchet/minimum-demand clauses), confirmed for 3 of 12 2024 months.
import csv, time
from python_calamine import CalamineWorkbook

FILES = {
    '2025-05': 'Billing Details Report May 2025.xlsx',
    '2025-07': 'Jul 25.csv',
    '2025-08': 'Aug 25.csv',
    '2025-10': 'Billing Details Report - October-2025.xlsx',
    '2025-11': 'Billing Details Report - November-2025.xlsx',
    '2025-12': 'Billing Details Report - December-2025.xlsx',
    '2026-01': 'Billing Details Report_Jan 2026.xlsx',
    '2026-02': 'Billing Details Report_Feb 2026.xlsx',
    '2026-03': 'Billing Details Report_Mar 2026.xlsx',
    '2026-04': 'Billing Details Report_Apr 2026.xlsx',
    '2026-05': 'Billing Details Report_May 2026.xlsx',
    '2026-06': 'Billing Details Report_Jun 2026.xlsx',
    '2026-07': 'Billing Details Report_Jul 2026.xls',
}


def is_zip(path):
    with open(path, 'rb') as f:
        return f.read(2) == b'PK'


def norm_id(v):
    if v is None:
        return ''
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    if isinstance(v, int):
        return str(v)
    return str(v).strip().replace(',', '')


def match(code, prem):
    return norm_id(code) == '100185' and norm_id(prem) == '607213'


def find_detail_sheet_data(path):
    wb = CalamineWorkbook.from_path(path)
    for sn in wb.sheet_names:
        data = wb.get_sheet_by_name(sn).to_python()
        for i, r in enumerate(data[:10]):
            if r and str(r[0]).strip() == 'Cust_Code':
                return data, i
    return None, None


def xlsx_rows(path):
    data, hdr_i = find_detail_sheet_data(path)
    if data is None:
        return None, []
    hdr = data[hdr_i]
    I = {str(n).strip(): i for i, n in enumerate(hdr) if n}
    ci, pi = I.get('Cust_Code'), I.get('Prem_Code')
    out = []
    for r in data[hdr_i + 1:]:
        if len(r) > max(ci, pi) and match(r[ci], r[pi]):
            out.append(r)
    return hdr, out


def tsv_rows(path):
    hdr = None
    out = []
    with open(path, encoding='latin-1', errors='replace') as f:
        for line in f:
            r = tuple(line.rstrip('\r\n').split('\t'))
            if hdr is None:
                if r and str(r[0]).strip() == 'Cust_Code':
                    hdr = list(r)
                continue
            if len(r) > 1 and match(r[0], r[1]):
                out.append(r)
    return hdr, out


def csv_rows(path):
    hdr = None
    out = []
    with open(path, encoding='latin-1', errors='replace', newline='') as f:
        for r in csv.reader(f):
            if hdr is None:
                if r and str(r[0]).strip() == 'Cust_Code':
                    hdr = list(r)
                continue
            if len(r) > 1 and match(r[0], r[1]):
                out.append(r)
    return hdr, out


def NUM(v):
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    v = str(v).strip().replace(',', '')
    if v == '':
        return 0.0
    try:
        return float(v)
    except ValueError:
        return 0.0


def get(hdr, r, k):
    I = {str(n).strip(): i for i, n in enumerate(hdr) if n}
    return r[I[k]] if k in I and I[k] < len(r) else None


for mo, fn in FILES.items():
    t0 = time.time()
    if fn.lower().endswith('.csv'):
        hdr, rows = csv_rows(fn)
    elif is_zip(fn):
        hdr, rows = xlsx_rows(fn)
    else:
        hdr, rows = tsv_rows(fn)
    if not rows:
        print(f'{mo}: NOT FOUND', flush=True)
        continue
    for r in rows:
        kva = NUM(get(hdr, r, 'kva_billed_consump'))
        cb = get(hdr, r, 'cust_billed')
        kwh = NUM(get(hdr, r, 'net_kwh_billed_consump'))
        demand_calc = NUM(get(hdr, r, 'KVAP_KVA_Demand')) + NUM(get(hdr, r, 'KVAL_Demand')) + NUM(get(hdr, r, 'KVAO_Demand'))
        implied = demand_calc / 2852.04 if demand_calc else 0
        print(f'{mo}: cust_billed={cb} kwh={kwh:,.0f} true_kva={kva:,.2f} implied_kva={implied:,.2f} match={abs(kva-implied)<1} ({time.time()-t0:.0f}s)', flush=True)
