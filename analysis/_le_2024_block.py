# -*- coding: utf-8 -*-
# Adds the "2024 vs 2026" sheet to _le_monthly.py (inserted before the workbook is saved).
s = open('_le_monthly.py', encoding='utf-8').read()
BLOCK = r'''
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
'''
i = s.index('wb.save(')
open('_le_monthly.py', 'w', encoding='utf-8').write(s[:i] + BLOCK + '\n' + s[i:])
print('2024 block added')
