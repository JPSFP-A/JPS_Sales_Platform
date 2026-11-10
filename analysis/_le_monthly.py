# -*- coding: utf-8 -*-
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
CL = ['RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']
LE = json.load(open('_oct_deep.json'))['le']; A = json.load(open('_fy27_actuals.json')); OUT = json.load(open('_fy27_result.json'))['fy26']
hf = Font(bold=True, color='FFFFFF'); fill = PatternFill('solid', fgColor='062552')
wb = Workbook(); ws = wb.active; ws.title = 'LE 2026 monthly'
ws['A1'] = 'FY2026 latest estimate (LE) by month and rate class, GWh'; ws['A1'].font = Font(bold=True, size=13)
ws['A2'] = 'The financials LE held in the platform, 3,299.7 GWh for the year. January to September agree with billed actuals at the time the LE was struck.'
for j, h in enumerate(['Rate class'] + MON + ['FY2026'], 1):
    c = ws.cell(4, j, h); c.font = hf; c.fill = fill; c.alignment = Alignment(horizontal='center' if j > 1 else 'left')
for i, c in enumerate(CL):
    r = 5 + i; ws.cell(r, 1, c)
    for j, m in enumerate(MON): ws.cell(r, 2 + j, round(LE[c]['%s 26' % m], 4)).number_format = '#,##0.00'
    ws.cell(r, 14, f'=SUM(B{r}:M{r})').number_format = '#,##0.0'
rt = 5 + len(CL); ws.cell(rt, 1, 'Total').font = Font(bold=True)
for col in range(2, 15):
    L = get_column_letter(col); c = ws.cell(rt, col, f'=SUM({L}5:{L}{rt - 1})'); c.font = Font(bold=True); c.number_format = '#,##0.00' if col < 14 else '#,##0.0'
ws.column_dimensions['A'].width = 12
for col in range(2, 15): ws.column_dimensions[get_column_letter(col)].width = 9.5
# comparison
w2 = wb.create_sheet('LE vs actual and outlook')
w2['A1'] = 'Total energy sales by month against the LE, GWh'; w2['A1'].font = Font(bold=True, size=13)
w2['A2'] = 'January to October are billed actuals from the platform (prepaid included, EV44 included). November and December are our outlook: the full-year class outlook less January to October, split on the LE monthly shape.'
for j, h in enumerate(['', *MON, 'FY2026'], 1):
    c = w2.cell(4, j, h); c.font = hf; c.fill = fill; c.alignment = Alignment(horizontal='center' if j > 1 else 'left')
w2.cell(5, 1, 'LE'); w2.cell(6, 1, 'Actual / outlook'); w2.cell(7, 1, 'Variance'); w2.cell(8, 1, 'Variance %'); w2.cell(9, 1, 'Basis')
for j, m in enumerate(MON):
    col = get_column_letter(2 + j)
    w2.cell(5, 2 + j, f"='LE 2026 monthly'!{col}{rt}")
    if j < 10: v = sum(A['2026-%02d' % (j + 1)][c] for c in CL); w2.cell(9, 2 + j, 'Actual')
    else:
        tot = 0
        for c in CL:
            rem = OUT[c] - sum(A['2026-%02d' % k][c] for k in range(1, 11)); sh = LE[c]['%s 26' % m] / (LE[c]['Nov 26'] + LE[c]['Dec 26']); tot += rem * sh
        v = tot; w2.cell(9, 2 + j, 'Outlook')
    w2.cell(6, 2 + j, round(v, 4)); w2.cell(7, 2 + j, f'={col}6-{col}5'); w2.cell(8, 2 + j, f'={col}7/{col}5')
for r in (5, 6, 7): w2.cell(r, 14, f'=SUM(B{r}:M{r})')
w2.cell(8, 14, '=N7/N5')
for r in (5, 6, 7):
    for col in range(2, 15): w2.cell(r, col).number_format = '#,##0.00;[Red]-#,##0.00'
for col in range(2, 15): w2.cell(8, col).number_format = '0.0%;[Red]-0.0%'
w2.column_dimensions['A'].width = 18
for col in range(2, 15): w2.column_dimensions[get_column_letter(col)].width = 9.5

# ---- 2024 against the 2026 numbers ----
R24 = json.load(open(r'_cust\_raw2024.json'))
w3 = wb.create_sheet('2024 vs 2026')
w3['A1'] = '2024 billed sales against the 2026 LE and outlook, GWh'; w3['A1'].font = Font(bold=True, size=13)
w3['A2'] = '2024 is from the monthly billing extracts: billed rows, EV44 included, prepaid-tagged rows excluded. The prepaid vending data starts in 2025, so 2024 RT10 and RT20 carry no prepaid (about 2.5 to 2.8 GWh a month in 2025 and 2026).'
def hdr_row(ws_, r, labels):
    for j, h in enumerate(labels, 1):
        c = ws_.cell(r, j, h); c.font = hf; c.fill = fill; c.alignment = Alignment(horizontal='center' if j > 1 else 'left')
hdr_row(w3, 4, ['2024 actual'] + MON + ['FY2024'])
for i, c in enumerate(CL):
    r = 5 + i; w3.cell(r, 1, c)
    for j in range(12): w3.cell(r, 2 + j, round(R24['2024-%02d' % (j + 1)][c], 4)).number_format = '#,##0.00'
    w3.cell(r, 14, f'=SUM(B{r}:M{r})').number_format = '#,##0.0'
t24 = 5 + len(CL); w3.cell(t24, 1, 'Total').font = Font(bold=True)
for col in range(2, 15):
    L = get_column_letter(col); c = w3.cell(t24, col, f'=SUM({L}5:{L}{t24 - 1})'); c.font = Font(bold=True); c.number_format = '#,##0.00' if col < 14 else '#,##0.0'
b = t24 + 3; hdr_row(w3, b, ['Total energy sales'] + MON + ['FY'])
labs = ['2024 actual', '2026 LE', '2026 actual / outlook', 'LE against 2024', 'LE against 2024 %', 'Actual / outlook against 2024', 'Actual / outlook against 2024 %']
for k, l in enumerate(labs): w3.cell(b + 1 + k, 1, l)
for j in range(13):
    col = get_column_letter(2 + j)
    w3.cell(b + 1, 2 + j, f'={col}{t24}'); w3.cell(b + 2, 2 + j, f"='LE vs actual and outlook'!{col}5"); w3.cell(b + 3, 2 + j, f"='LE vs actual and outlook'!{col}6")
    w3.cell(b + 4, 2 + j, f'={col}{b + 2}-{col}{b + 1}'); w3.cell(b + 5, 2 + j, f'={col}{b + 4}/{col}{b + 1}')
    w3.cell(b + 6, 2 + j, f'={col}{b + 3}-{col}{b + 1}'); w3.cell(b + 7, 2 + j, f'={col}{b + 6}/{col}{b + 1}')
for k in (1, 2, 3, 4, 6):
    for col in range(2, 15): w3.cell(b + k, col).number_format = '#,##0.00;[Red]-#,##0.00' if col < 14 else '#,##0.0;[Red]-#,##0.0'
for k in (5, 7):
    for col in range(2, 15): w3.cell(b + k, col).number_format = '0.0%;[Red]-0.0%'
c0 = b + 10; hdr_row(w3, c0, ['By rate class, FY', 'FY2024', 'FY2026 LE', 'Change GWh', 'Change %'])
for i, c in enumerate(CL):
    r = c0 + 1 + i; w3.cell(r, 1, c); w3.cell(r, 2, f'=N{5 + i}'); w3.cell(r, 3, f"='LE 2026 monthly'!N{5 + i}"); w3.cell(r, 4, f'=C{r}-B{r}'); w3.cell(r, 5, f'=D{r}/B{r}')
rr = c0 + 1 + len(CL); w3.cell(rr, 1, 'Total').font = Font(bold=True)
for col in 'BCD': w3[f'{col}{rr}'] = f'=SUM({col}{c0 + 1}:{col}{rr - 1})'
w3[f'E{rr}'] = f'=D{rr}/B{rr}'
for r in range(c0 + 1, rr + 1):
    for col in 'BCD': w3[f'{col}{r}'].number_format = '#,##0.0;[Red]-#,##0.0'
    w3[f'E{r}'].number_format = '0.0%;[Red]-0.0%'
w3.column_dimensions['A'].width = 30
for col in range(2, 15): w3.column_dimensions[get_column_letter(col)].width = 10

wb.save(r'C:\Projects\Sales_Platform\analysis\_deliverables_Nov2026\JPS_LE_2026_Monthly.xlsx'); print('saved')
