# -*- coding: utf-8 -*-
# October 2026 Billed Sales by Rate Class (GWh), in the layout of the September table.
# October actual: earnings sheet ESHEET 10-26 (row 10, MWh). October budget and October 2025: the platform tables.
# YTD to September (actual, budget, 2025): the September table as issued; October is added to each.
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
CL = [('Residential', 'Rate 10'), ('SME', 'Rate 20'), ('Commercial', 'Rate 40'), ('', 'Rate 50'), ('', 'Rate 60'), ('', 'Rate 70')]
OCT_ACT = [108869.1, 60864.9, 70661.5, 30886.1, 3416.0, 19423.6]          # MWh, earnings sheet
OCT_BUD = [103.01, 55.59, 73.55, 33.77, 3.21, 23.57]                      # GWh, jps_budget_class_month
OCT_25 = [105.77, 57.70, 68.35, 26.98, 3.41, 26.93]                       # GWh, jps_actuals
SEP_YTD_ACT = [882.37, 475.55, 570.16, 259.55, 27.51, 213.87]
SEP_YTD_BUD = [853.60, 461.30, 584.99, 274.11, 27.06, 192.71]
SEP_YTD_25 = [909.61, 490.07, 605.14, 287.17, 30.40, 226.86]
wb = Workbook(); ws = wb.active; ws.title = 'October 2026'; wi = wb.create_sheet('Inputs')
# inputs
wi['A1'] = 'Inputs, GWh'; wi['A1'].font = Font(bold=True, size=12)
H = ['Rate class', 'Oct 2026 actual', 'Oct 2026 budget', 'Oct 2025', 'YTD Sep 2026 actual', 'YTD Sep 2026 budget', 'YTD Sep 2025']
for j, h in enumerate(H, 1): wi.cell(3, j, h).font = Font(bold=True)
for i, (_, rc) in enumerate(CL):
    r = 4 + i; wi.cell(r, 1, rc); wi.cell(r, 2, f'={OCT_ACT[i]}/1000'); wi.cell(r, 3, OCT_BUD[i]); wi.cell(r, 4, OCT_25[i]); wi.cell(r, 5, SEP_YTD_ACT[i]); wi.cell(r, 6, SEP_YTD_BUD[i]); wi.cell(r, 7, SEP_YTD_25[i])
    for c in range(2, 8): wi.cell(r, c).number_format = '#,##0.00'
notes = ['Oct 2026 actual: earnings sheet ESHEET 10-26, row 10, MWh billed including prepaid, before the prepaid deduction line (294,121.2 MWh in total).',
         'Oct 2026 budget: platform budget table (jps_budget_class_month).',
         'Oct 2025: platform actuals table. The September table shows 2025 within 0.02 GWh of the platform by class, so the same source is used.',
         'YTD to September: taken from the September table as issued. October is added to each.']
for i, t in enumerate(notes): wi.cell(11 + i, 1, t)
wi.column_dimensions['A'].width = 14
for c in 'BCDEFG': wi.column_dimensions[c].width = 20
# table
NAVY = '062552'; GREY = 'D9D9D9'
hf = Font(bold=True, color='FFFFFF'); fill = PatternFill('solid', fgColor=NAVY)
ws.merge_cells('A1:P1'); ws['A1'] = 'October 2026 Billed Sales by Rate Class (GWh)'; ws['A1'].font = hf; ws['A1'].fill = fill; ws['A1'].alignment = Alignment(horizontal='center')
heads = ['Customer Segment', 'Rate Class', 'Actual Sales', 'Budget Sales', 'Variance', 'Var (%)', '2025', 'Variance', 'Var (%)', 'YTD Actual', 'YTD Budget', 'Variance', 'Var (%)', '2025 YTD', 'Variance', 'Var (%)']
for j, h in enumerate(heads, 1):
    c = ws.cell(2, j, h); c.font = hf; c.fill = fill; c.alignment = Alignment(horizontal='center' if j > 2 else 'left')
def row(r, vals_formulas, bold=False, shade=None):
    for j, v in enumerate(vals_formulas, 1):
        c = ws.cell(r, j, v)
        if bold: c.font = Font(bold=True)
        if shade: c.fill = PatternFill('solid', fgColor=shade)
        if j >= 3: c.number_format = '0.0%;-0.0%' if j in (6, 9, 13, 16) else '#,##0.00;-#,##0.00'
        if j >= 3: c.alignment = Alignment(horizontal='right')
def line(r, ir):   # ir: row in Inputs
    return [f'=Inputs!B{ir}', f'=Inputs!C{ir}', f'=C{r}-D{r}', f'=E{r}/D{r}', f'=Inputs!D{ir}', f'=C{r}-G{r}', f'=H{r}/G{r}',
            f'=Inputs!E{ir}+C{r}', f'=Inputs!F{ir}+D{r}', f'=J{r}-K{r}', f'=L{r}/K{r}', f'=Inputs!G{ir}+G{r}', f'=J{r}-N{r}', f'=O{r}/N{r}']
r = 3
for i, (seg, rc) in enumerate(CL):
    if i == 2: pass
    row(r, [seg, rc] + line(r, 4 + i))
    r += 1
    if i == 1: pass
# totals
tc, te = r, r + 1
def tot(rr, a, b, bold=True, shade=None):
    f = []
    for col in 'CDGJKN': f.append(f'=SUM({col}{a}:{col}{b})')
    c_, d_, g_, j_, k_, n_ = f
    vals = ['Total Commercial Sales' if rr == tc else 'Total Energy Sales', '', c_, d_, f'=C{rr}-D{rr}', f'=E{rr}/D{rr}', g_, f'=C{rr}-G{rr}', f'=H{rr}/G{rr}', j_, k_, f'=J{rr}-K{rr}', f'=L{rr}/K{rr}', n_, f'=J{rr}-N{rr}', f'=O{rr}/N{rr}']
    row(rr, vals, bold=True, shade=shade)
tot(tc, 5, 8);
# total energy = residential + SME + total commercial
vals = ['Total Energy Sales', '']
for col in 'CD': vals.append(f'={col}3+{col}4+{col}{tc}')
vals = ['Total Energy Sales', '', f'=C3+C4+C{tc}', f'=D3+D4+D{tc}', f'=C{te}-D{te}', f'=E{te}/D{te}', f'=G3+G4+G{tc}', f'=C{te}-G{te}', f'=H{te}/G{te}', f'=J3+J4+J{tc}', f'=K3+K4+K{tc}', f'=J{te}-K{te}', f'=L{te}/K{te}', f'=N3+N4+N{tc}', f'=J{te}-N{te}', f'=O{te}/N{te}']
row(te, vals, bold=True, shade=GREY)
for rr in (tc, te):
    for j in range(1, 17): ws.cell(rr, j).border = Border(top=Side(style='thin'))
ws.column_dimensions['A'].width = 24; ws.column_dimensions['B'].width = 10
for j in range(3, 17): ws.column_dimensions[get_column_letter(j)].width = 12
ws.freeze_panes = 'C3'
wb.save(r'C:\Projects\Sales_Platform\analysis\_deliverables_Nov2026\JPS_Oct2026_Billed_Sales_by_Rate_Class.xlsx'); print('saved')
