# -*- coding: utf-8 -*-
# October 2026: platform vs earnings sheet, item by item. Items are the billing-extract rows flagged cust_billed = 0.
import csv, io, json
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HERE = r'C:\Projects\Sales_Platform\analysis'
OUT = r'C:\Projects\Sales_Platform\JPS_Oct2026_Sales_Gap_Reconciliation_v2.xlsx'
CLASS = {'EV44': 'RT10', 'RT76': 'RT70', 'L130': 'RT60-ST', 'M125': 'RT60-ST', 'M160': 'RT60-ST', 'M250': 'RT60-ST'}
rm = {}
import requests, truststore
truststore.inject_into_ssl()
env = {}
for l in io.open(HERE + r'\.env', encoding='utf-8'):
    if '=' in l and not l.startswith('#'): k, v = l.strip().split('=', 1); env[k] = v.strip('"')
H = {'apikey': env['SUPABASE_SERVICE_ROLE_KEY'], 'Authorization': 'Bearer ' + env['SUPABASE_SERVICE_ROLE_KEY']}
for x in requests.get(env['SUPABASE_URL'] + '/rest/v1/sales_rate_map', headers=H, params={'select': 'srat_code,title', 'limit': '500'}, timeout=60).json(): rm[x['srat_code']] = x['title']

sep = json.load(open(HERE + r'\_oct_anomaly_scan.json'))['sep']
num = lambda s: float(s) if s not in ('', None) else 0.0
acc = {}; tot_net = 0.0
rd = csv.reader(io.open(HERE + r'\Oct 26.csv', encoding='utf-8', errors='replace')); h = next(rd); ix = {n: i for i, n in enumerate(h)}
for row in rd:
    if len(row) < 40: continue
    g = lambda n: row[ix[n]] if ix[n] < len(row) else ''
    tot_net += num(g('net_kwh_billed_consump'))
    if g('cust_billed') != '0': continue
    srat = g('Srat_Code'); cls = CLASS.get(srat) or rm.get(srat)
    if cls not in ('RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70'): continue
    k = g('Cust_Code') + '-' + g('Prem_Code')
    a = acc.setdefault(k, {'name': g('Name'), 'srat': srat, 'cls': cls, 'parish': g('Parish'), 'gross': 0.0, 'adj': 0.0, 'net': 0.0, 'rows': 0})
    a['gross'] += num(g('kwh_billed_consump')); a['adj'] += num(g('kwh_billed_consump_adj')); a['net'] += num(g('net_kwh_billed_consump')); a['rows'] += 1
items = []
n_zero = 0
for k, a in acc.items():
    if abs(a['net']) < 0.005: n_zero += 1; continue
    if a['srat'] == 'EV44': why = 'EV44: JPS EV chargers, not billed, srat not in the rate map'
    elif a['srat'] in ('PR10', 'PR20'): why = 'Prepaid code (PR10/PR20): reversal or load outside the postpaid billing'
    elif a['gross'] <= 0 and a['net'] < 0: why = 'Credit adjustment with no usage in the month'
    elif a['adj'] != 0: why = 'Adjustment against usage'
    else: why = 'Usage on a row flagged not billed'
    s = sep.get(k); sn = s['net'] if s else None
    items.append([a['cls'], k, a['name'], a['srat'], a['parish'], a['rows'], round(a['gross'], 2), round(a['adj'], 2), round(a['net'], 2), sn, why])
items.sort(key=lambda r: (r[0], -abs(r[8])))

PLAT = {'RT10': 108943.25509, 'RT20': 60868.59, 'RT40': 70760.38, 'RT50': 30886.10, 'RT60-ST': 3414.28, 'RT70': 19423.64}   # platform extract, MWh (database sums)
SHEET = {'RT10': 108869.1, 'RT20': 60864.9, 'RT40': 70661.5, 'RT50': 30886.1, 'RT60-ST': 3416.0, 'RT70': 19423.6}          # earnings sheet row 10

wb = Workbook()
NAVY = '062552'; hdr = Font(bold=True, color='FFFFFF'); fill = PatternFill('solid', fgColor=NAVY)
thin = Side(style='thin', color='BBBBBB'); box = Border(top=thin, bottom=thin, left=thin, right=thin)
def head(ws, r, vals):
    for i, v in enumerate(vals, 1):
        c = ws.cell(r, i, v); c.font = hdr; c.fill = fill; c.alignment = Alignment(wrap_text=True, vertical='center'); c.border = box

# ---------- Items ----------
wi = wb.active; wi.title = 'Items'
wi['A1'] = 'October 2026: billing rows flagged not billed (cust_billed = 0) that carry kWh'; wi['A1'].font = Font(bold=True, size=13)
wi['A2'] = 'The earnings sheet counts these rows. The platform load drops them. Effect on the platform is the negative of the net kWh.'
head(wi, 4, ['Class', 'Account', 'Name', 'Rate code', 'Parish', 'Rows', 'Gross kWh', 'Adjustment kWh', 'Net kWh', 'September net kWh', 'Net MWh', 'Effect on platform minus sheet (MWh)', 'What it is'])
r0 = 5
for i, it in enumerate(items):
    r = r0 + i
    for j, v in enumerate(it[:10], 1): wi.cell(r, j, v)
    wi.cell(r, 11, f'=I{r}/1000'); wi.cell(r, 12, f'=-K{r}'); wi.cell(r, 13, it[10])
rl = r0 + len(items) - 1
wi.cell(rl + 2, 1, 'Total').font = Font(bold=True)
for col in (6, 7, 8, 9, 11, 12):
    L = get_column_letter(col); c = wi.cell(rl + 2, col, f'=SUM({L}{r0}:{L}{rl})'); c.font = Font(bold=True)
wi.cell(rl + 4, 1, f'{n_zero:,} further rows flagged not billed carry zero kWh and have no effect. They are not listed.')
for col, w in zip('ABCDEFGHIJKLM', (9, 18, 38, 10, 14, 7, 14, 14, 14, 16, 12, 18, 62)): wi.column_dimensions[col].width = w
for r in range(r0, rl + 3):
    for col in (7, 8, 9, 10): wi.cell(r, col).number_format = '#,##0;[Red]-#,##0'
    for col in (11, 12): wi.cell(r, col).number_format = '#,##0.0;[Red]-#,##0.0'
wi.freeze_panes = 'A5'; wi.auto_filter.ref = f'A4:M{rl}'

# ---------- Summary ----------
ws = wb.create_sheet('Summary', 0)
ws['A1'] = 'October 2026 sales: platform against the earnings sheet'; ws['A1'].font = Font(bold=True, size=14)
ws['A2'] = 'MWh billed, prepaid included. Platform is the loaded October extract; the sheet is ESHEET 10-26, row 10.'
head(ws, 4, ['Class', 'Platform (MWh)', 'Earnings sheet (MWh)', 'Difference (MWh)', 'Explained by items (MWh)', 'Unexplained (MWh)'])
cl = ['RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']
for i, c in enumerate(cl):
    r = 5 + i
    ws.cell(r, 1, c); ws.cell(r, 2, PLAT[c]); ws.cell(r, 3, SHEET[c]); ws.cell(r, 4, f'=B{r}-C{r}')
    ws.cell(r, 5, f'=SUMIF(Items!$A${r0}:$A${rl},A{r},Items!$L${r0}:$L${rl})'); ws.cell(r, 6, f'=D{r}-E{r}')
rt = 5 + len(cl)
ws.cell(rt, 1, 'Total').font = Font(bold=True)
for col in range(2, 7):
    L = get_column_letter(col); c = ws.cell(rt, col, f'=SUM({L}5:{L}{rt - 1})'); c.font = Font(bold=True)
for r in range(5, rt + 1):
    for col in range(2, 7): ws.cell(r, col).number_format = '#,##0.0;[Red]-#,##0.0'
ws.cell(rt + 1, 1, 'Unexplained is rounding on the sheet (one decimal) and the database class totals; every class is within 1 MWh.').font = Font(italic=True)

ws.cell(rt + 3, 1, 'What causes the difference').font = Font(bold=True, size=12)
head(ws, rt + 4, ['Cause', 'Rows', 'Effect on platform minus sheet (MWh)', 'Largest items'])
causes = [('Credit adjustment with no usage in the month', 'Caribbean Maritime University -96.2 MWh and Nearshore Inbound Call Experts -2.6 MWh (both RT40); 44 smaller RT10 and RT20 credits, the largest -11.7 MWh'),
          ('Prepaid code (PR10/PR20): reversal or load outside the postpaid billing', 'Tomlinson, Kyle R. -100.0 MWh in October after +99.99 MWh in September'),
          ('EV44: JPS EV chargers, not billed, srat not in the rate map', '25 accounts with kWh (26 rows flagged), all in the name of Jamaica Public Service, in RT10 on the sheet'),
          ('Adjustment against usage', ''), ('Usage on a row flagged not billed', '')]
for i, (cz, big) in enumerate(causes):
    r = rt + 5 + i
    ws.cell(r, 1, cz); ws.cell(r, 2, f'=COUNTIF(Items!$M${r0}:$M${rl},A{r})'); ws.cell(r, 3, f'=SUMIF(Items!$M${r0}:$M${rl},A{r},Items!$L${r0}:$L${rl})'); ws.cell(r, 4, big)
    ws.cell(r, 3).number_format = '#,##0.0;[Red]-#,##0.0'
re_ = rt + 5 + len(causes)
ws.cell(re_, 1, 'Total').font = Font(bold=True); ws.cell(re_, 2, f'=SUM(B{rt + 5}:B{re_ - 1})'); ws.cell(re_, 3, f'=SUM(C{rt + 5}:C{re_ - 1})'); ws.cell(re_, 3).number_format = '#,##0.0;[Red]-#,##0.0'
ws.cell(re_, 3).font = Font(bold=True)

ws.cell(re_ + 2, 1, 'What it is not').font = Font(bold=True, size=12)
for i, t in enumerate(['Prepaid: both sides carry about 2.8 GWh inside the class totals (platform 2,833.2 MWh, sheet 2,820.9 MWh). The 12.3 MWh difference is offset by 12.3 MWh of billing rows tagged PR that the sheet counts and the platform excludes, so prepaid does not move the gap.',
                       'Column shift: every MWh and customer cell on the sheet sits in its own class column and the six classes foot to the sheet total of 294,121.2 MWh.',
                       'Missing accounts: RT40, RT50 and RT70 have the same account counts on both sides (1,962, 157, 21).']):
    ws.cell(re_ + 3 + i, 1, t)
ws.cell(re_ + 7, 1, 'Check').font = Font(bold=True, size=12)
ws.cell(re_ + 8, 1, 'Extract net kWh, all rows, MWh'); ws.cell(re_ + 8, 2, round(tot_net / 1000, 1))
ws.cell(re_ + 9, 1, 'Sheet "total less prepaid", MWh'); ws.cell(re_ + 9, 2, 291300.3)
ws.cell(re_ + 10, 1, 'Difference'); ws.cell(re_ + 10, 2, f'=B{re_ + 8}-B{re_ + 9}')
for r in range(re_ + 8, re_ + 11): ws.cell(r, 2).number_format = '#,##0.0;[Red]-#,##0.0'
ws.cell(re_ + 12, 1, 'After EV44 was added to the October load (live data, MWh)').font = Font(bold=True, size=12)
head(ws, re_ + 13, ['Class', 'Platform before', 'Platform now', 'Earnings sheet', 'Left over'])
NEW = {'RT10': 109015.0, 'RT20': 60868.6, 'RT40': 70760.4, 'RT50': 30886.1, 'RT60-ST': 3414.3, 'RT70': 19423.6}
for i, c in enumerate(cl):
    r = re_ + 14 + i
    ws.cell(r, 1, c); ws.cell(r, 2, PLAT[c]); ws.cell(r, 3, NEW[c]); ws.cell(r, 4, SHEET[c]); ws.cell(r, 5, f'=C{r}-D{r}')
rr = re_ + 14 + len(cl)
ws.cell(rr, 1, 'Total').font = Font(bold=True)
for col in range(2, 6):
    L = get_column_letter(col); ws.cell(rr, col, f'=SUM({L}{re_ + 14}:{L}{rr - 1})').font = Font(bold=True)
for r in range(re_ + 14, rr + 1):
    for col in range(2, 6): ws.cell(r, col).number_format = '#,##0.0;[Red]-#,##0.0'
ws.cell(rr + 1, 1, 'EV44 was only offsetting the other items, so the platform now sits 246.9 MWh above the sheet. That is the rest of the list: credits with no usage (+155.7), the PR reversal (+99.2, excluded on purpose because those premises sit in JUICE) and small adjustments (-8.0). The credits are with Finance to confirm.').font = Font(italic=True)
ws.column_dimensions['A'].width = 62
for col in 'BCDEF': ws.column_dimensions[col].width = 24
ws.column_dimensions['D'].width = 70
ws.sheet_view.showGridLines = False
wb.save(OUT); print('saved', OUT, len(items), 'items', n_zero, 'zero rows')
