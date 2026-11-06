# -*- coding: utf-8 -*-
# Pull Caribbean Cement Co Ltd (302571-686496, RT50) full component detail + true
# kva_billed_consump for every locally available raw file -- same treatment as Alcoa,
# but this account's jps_actuals data is already clean (no Fuel pipeline bug), so this
# is mainly for 2024 backfill + true KVA (not a reconciliation fix).
import csv, time
from python_calamine import CalamineWorkbook

FILES = {
    '2024-01': 'Jan 24.csv', '2024-02': 'Feb 24.csv', '2024-03': 'Mar 24.csv',
    '2024-04': 'Apr 24.csv', '2024-05': 'May 24.csv', '2024-06': 'Jun 24.csv',
    '2024-07': 'Jul 24.csv', '2024-08': 'Aug 24.csv', '2024-09': 'Sep 24.csv',
    '2024-10': 'Oct 24.csv', '2024-11': 'Nov 24.csv', '2024-12': 'Dec 24.csv',
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
TARGET_CODE, TARGET_PREM = '302571', '686496'
NEED = ['KVAP_KVA_Demand', 'KVAL_Demand', 'KVAO_Demand', 'kva_billed_consump',
        'KWHP_KWH_Energy', 'KWHL_Energy', 'KWHO_Energy',
        'fuel', 'FuelOffPeak', 'FuelPartialPeak', 'FuelOnPeak',
        'IPP_Charge', 'Cust_Charge', 'GCT', 'FEX', 'Tariff_Adj', 'rint', 'EEIF',
        'Net_Billing_Adj', 'revenue_adj']


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
    return norm_id(code) == TARGET_CODE and norm_id(prem) == TARGET_PREM


def find_detail_sheet_data(path):
    wb = CalamineWorkbook.from_path(path)
    for sn in wb.sheet_names:
        data = wb.get_sheet_by_name(sn).to_python()
        for i, r in enumerate(data[:10]):
            if r and str(r[0]).strip() == 'Cust_Code':
                return data, i
    return None, None


def xlsx_row(path):
    data, hdr_i = find_detail_sheet_data(path)
    if data is None:
        return None
    hdr = data[hdr_i]
    I = {str(n).strip(): i for i, n in enumerate(hdr) if n}
    ci, pi = I.get('Cust_Code'), I.get('Prem_Code')
    if ci is None or pi is None:
        return None
    for r in data[hdr_i + 1:]:
        if len(r) > max(ci, pi) and match(r[ci], r[pi]):
            return hdr, r
    return None


def tsv_row(path):
    with open(path, encoding='latin-1', errors='replace') as f:
        hdr = None
        for line in f:
            r = tuple(line.rstrip('\r\n').split('\t'))
            if hdr is None:
                if r and str(r[0]).strip() == 'Cust_Code':
                    hdr = list(r)
                continue
            if len(r) > 1 and match(r[0], r[1]):
                return (hdr, r)
    return None


def csv_row(path):
    with open(path, encoding='latin-1', errors='replace', newline='') as f:
        rdr = csv.reader(f)
        hdr = None
        rows = []
        for r in rdr:
            if hdr is None:
                if r and str(r[0]).strip() == 'Cust_Code':
                    hdr = list(r)
                continue
            if len(r) > 1 and match(r[0], r[1]):
                rows.append(r)
        return hdr, rows


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


def breakdown(hdr, r):
    vals = {k: NUM(get(hdr, r, k)) for k in NEED}
    kwh = NUM(get(hdr, r, 'net_kwh_billed_consump'))
    rev = NUM(get(hdr, r, 'net_billed_revenue'))
    cb = get(hdr, r, 'cust_billed')
    demand = vals['KVAP_KVA_Demand'] + vals['KVAL_Demand'] + vals['KVAO_Demand']
    energy = vals['KWHP_KWH_Energy'] + vals['KWHL_Energy'] + vals['KWHO_Energy']
    fuel = vals['fuel'] + vals['FuelOffPeak'] + vals['FuelPartialPeak'] + vals['FuelOnPeak']
    known = demand + fuel + energy + vals['IPP_Charge'] + vals['Cust_Charge']
    other = rev - known
    return dict(kwh=kwh, rev=rev, demand=demand, energy=energy, fuel=fuel, ipp=vals['IPP_Charge'],
                cust=vals['Cust_Charge'], gct=vals['GCT'], fex=vals['FEX'], kva=vals['kva_billed_consump'],
                unexplained=other, cust_billed=cb)


results = {}
for mo, fn in FILES.items():
    t0 = time.time()
    if fn.lower().endswith('.csv'):
        hdr, rows = csv_row(fn)
        if not rows:
            print(f'{mo}: NOT FOUND', flush=True); continue
        agg = None
        for r in rows:
            d = breakdown(hdr, r)
            print(f'{mo}: row cust_billed={d["cust_billed"]} kwh={d["kwh"]:,.0f} rev={d["rev"]:,.0f} kva={d["kva"]:,.2f} demand={d["demand"]:,.0f} fuel={d["fuel"]:,.0f} energy={d["energy"]:,.0f} ipp={d["ipp"]:,.0f} cust={d["cust"]:,.0f} gct={d["gct"]:,.0f} unexplained={d["unexplained"]:,.0f} ({time.time()-t0:.0f}s)', flush=True)
            if agg is None:
                agg = {k: 0.0 for k in d if k not in ('cust_billed',)}
            for k in agg:
                agg[k] += d[k]
        if len(rows) > 1:
            print(f'{mo}: SUM of {len(rows)} rows: kwh={agg["kwh"]:,.0f} rev={agg["rev"]:,.0f} kva={agg["kva"]:,.2f}', flush=True)
        results[mo] = agg
    else:
        row = xlsx_row(fn) if is_zip(fn) else tsv_row(fn)
        if not row:
            print(f'{mo}: NOT FOUND ({time.time()-t0:.0f}s)', flush=True); continue
        hdr, r = row
        d = breakdown(hdr, r)
        print(f'{mo}: kwh={d["kwh"]:,.0f} rev={d["rev"]:,.0f} kva={d["kva"]:,.2f} demand={d["demand"]:,.0f} fuel={d["fuel"]:,.0f} energy={d["energy"]:,.0f} ipp={d["ipp"]:,.0f} cust={d["cust"]:,.0f} gct={d["gct"]:,.0f} unexplained={d["unexplained"]:,.0f} ({time.time()-t0:.0f}s)', flush=True)
        results[mo] = d

print(flush=True)
print('SUMMARY:', flush=True)
for mo, d in sorted(results.items()):
    print(f'  {mo}: kwh={d["kwh"]:,.0f} rev={d["rev"]:,.0f} kva={d["kva"]:,.2f} demand={d["demand"]:,.0f} unexplained={d["unexplained"]:,.0f}', flush=True)
