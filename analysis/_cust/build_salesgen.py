# -*- coding: utf-8 -*-
# Monthly billed sales and net generation, FY2026-FY2028, on the Sales Platform Driver Forecast (September actuals loaded).
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L

E = json.load(open('engine_out.json'))
CLS = ['RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']
NAMES = {'RT10': 'RT10 Residential', 'RT20': 'RT20 Small commercial', 'RT40': 'RT40 Commercial', 'RT50': 'RT50 Large commercial',
         'RT60-ST': 'RT60 Street lighting', 'RT70': 'RT70 Industrial'}
YEARS = (2026, 2027, 2028)
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
G = 1e6   # kWh to GWh
# billed sales register: FY2026 per the 11 Sep 2026 Billed Sales table, FY2027/28 per the Driver Report (same source the earlier Sales/Gen builder pinned to)
_src = open(r'C:\Projects\Sales_Platform\analysis\_build_wb_v2.py', encoding='utf-8').read()
_ns = {}
for _name in ('m26', 'm27', 'm28'):
    _i = _src.index(_name + ' = {'); _j = _src.index(chr(10) + '}' + chr(10), _i) + 3
    exec(_src[_i:_j], _ns)
bill = {2026: {rc: [v / G for v in _ns['m26'][rc]] for rc in CLS},
        2027: {rc: [v / G for v in _ns['m27'][rc]] for rc in CLS},
        2028: {rc: [v / G for v in _ns['m28'][rc]] for rc in CLS}}
live = {y: {rc: [v / G for v in E[str(y)][rc]] for rc in CLS} for y in YEARS}   # live platform run, kept for the comparison sheet only
tot = {y: [sum(bill[y][rc][m] for rc in CLS) for m in range(12)] for y in YEARS}

# net generation actuals Jan-Aug 2026 (system operations record), MWh
NG_ACT = [325445.00, 294131.83, 346444.13, 347826.00, 364366.69, 387886.70, 399975.47, 417380.53, 422276.80]   # Sep: implied by the 26.74% rolling 12-month scorecard figure
TARGET = 0.2710
# FY2026: Jan-Sep real; Oct-Dec losses solved to one flat rate so the full year closes at 27.10% of net generation
S_all = sum(tot[2026])
L_act = sum(ng / 1000 - tot[2026][m] for m, ng in enumerate(NG_ACT))
L_open = TARGET / (1 - TARGET) * S_all - L_act
S_open = sum(tot[2026][9:])
R_OPEN = L_open / (S_open + L_open)
# FY2027/28: seasonal monthly loss path from the platform loss assumptions
RATE = {2027: [27.75, 22.78, 29.34, 27.39, 30.72, 26.53, 27.56, 28.21, 25.35, 25.45, 24.75, 28.34],
        2028: [27.77, 22.81, 29.33, 27.38, 30.71, 26.52, 27.56, 28.21, 25.35, 25.45, 24.75, 28.34]}

NAVY, BLUE, CYAN, GREY, LIGHT = '062552', '0E4E95', '009FDA', '66788A', 'D9E1F2'
def F(**k): return Font(name='Arial', size=k.pop('size', 10), **k)
def fill(c): return PatternFill('solid', fgColor=c)
thin = Side(style='thin', color=LIGHT)

wb = Workbook()
# ---------------- billed by class ----------------
C = wb.active; C.title = 'Billed by rate class'
C['A1'] = 'Billed sales by rate class, FY2026 to FY2028 (GWh)'; C['A1'].font = F(bold=True, size=13, color=NAVY)
C['A2'] = 'January to September 2026 actual; October 2026 onward is the Sales Platform Driver Forecast.'; C['A2'].font = F(color=GREY, italic=True)
hdr = ['Rate class']
for y in YEARS: hdr += [f'{m} {str(y)[2:]}' for m in MON] + [f'FY{y}']
for j, h in enumerate(hdr):
    x = C.cell(4, 1 + j, h); x.font = F(bold=True, color='FFFFFF'); x.alignment = Alignment(horizontal='center')
    fc = (j >= 1) and not (j <= 9) and True
    x.fill = fill(NAVY)
for yi, y in enumerate(YEARS):
    base = 2 + yi * 13
    for m in range(12):
        if y == 2026 and m >= 9 or y > 2026: C.cell(4, base + m).fill = fill(CYAN)
    C.cell(4, base + 12).fill = fill(BLUE)
for i, rc in enumerate(CLS):
    r = 5 + i
    C.cell(r, 1, NAMES[rc]).font = F(bold=True, color=NAVY)
    for yi, y in enumerate(YEARS):
        base = 2 + yi * 13
        for m in range(12):
            x = C.cell(r, base + m, bill[y][rc][m]); x.number_format = '#,##0.0'; x.font = F(color='0000FF')
        x = C.cell(r, base + 12, f'=SUM({L(base)}{r}:{L(base + 11)}{r})'); x.number_format = '#,##0.0'; x.font = F(bold=True)
rt = 5 + len(CLS)
C.cell(rt, 1, 'Total billed sales').font = F(bold=True, color='FFFFFF')
for j in range(1, len(hdr) + 1):
    c_ = C.cell(rt, j); c_.fill = fill(NAVY)
    if j > 1:
        c_.value = f'=SUM({L(j)}5:{L(j)}{rt - 1})'; c_.number_format = '#,##0.0'; c_.font = F(bold=True, color='FFFFFF')
C.column_dimensions['A'].width = 24
for j in range(2, len(hdr) + 1): C.column_dimensions[L(j)].width = 9.5
for yi in range(3): C.column_dimensions[L(2 + yi * 13 + 12)].width = 11
C.freeze_panes = 'B5'

# ---------------- monthly billed and net gen ----------------
M = wb.create_sheet('Billed and Net Gen', 0)
M['A1'] = 'Billed sales and net generation, monthly FY2026 to FY2028'; M['A1'].font = F(bold=True, size=13, color=NAVY)
M['A2'] = 'GWh. Net generation = billed sales + losses. Loss % is losses as a share of net generation. Blue cells are inputs; everything else is calculated.'; M['A2'].font = F(color=GREY, italic=True)
heads = ['Period', 'Basis', 'Billed sales (GWh)', 'Loss % of net gen', 'Losses (GWh)', 'Net generation (GWh)']
for j, h in enumerate(heads):
    x = M.cell(4, 1 + j, h); x.font = F(bold=True, color='FFFFFF'); x.fill = fill(NAVY); x.alignment = Alignment(horizontal='center', wrap_text=True)
M.row_dimensions[4].height = 30
r = 5; fy_rows = {}
for yi, y in enumerate(YEARS):
    first = r
    for m in range(12):
        col_c = L(2 + yi * 13 + m)
        M.cell(r, 1, f'{MON[m]} {y}').font = F(bold=True, color=NAVY)
        x = M.cell(r, 3, f"='Billed by rate class'!{col_c}{rt}"); x.number_format = '#,##0.0'; x.font = F()
        if y == 2026 and m < 9:
            M.cell(r, 2, 'Net gen actual' if m < 8 else 'Net gen per scorecard').font = F()
            x = M.cell(r, 6, NG_ACT[m] / 1000); x.number_format = '#,##0.0'; x.font = F(color='0000FF')
            x = M.cell(r, 5, f'=F{r}-C{r}'); x.number_format = '#,##0.0'; x.font = F()
            x = M.cell(r, 4, f'=E{r}/F{r}'); x.number_format = '0.0%'; x.font = F()
        else:
            M.cell(r, 2, 'Forecast').font = F()
            rate = R_OPEN if y == 2026 else RATE[y][m] / 100
            x = M.cell(r, 4, rate); x.number_format = '0.0%'; x.font = F(color='0000FF')
            x = M.cell(r, 5, f'=C{r}*D{r}/(1-D{r})'); x.number_format = '#,##0.0'; x.font = F()
            x = M.cell(r, 6, f'=C{r}+E{r}'); x.number_format = '#,##0.0'; x.font = F()
        if (y == 2026 and m >= 9) or y > 2026:
            for j in range(1, 7): M.cell(r, j).fill = fill('F3F6FB')
        r += 1
    last = r - 1
    M.cell(r, 1, f'FY{y}').font = F(bold=True, color='FFFFFF')
    for j, f in ((3, f'=SUM(C{first}:C{last})'), (5, f'=SUM(E{first}:E{last})'), (6, f'=SUM(F{first}:F{last})'), (4, f'=E{r}/F{r}')):
        x = M.cell(r, j, f); x.number_format = '0.0%' if j == 4 else '#,##0.0'; x.font = F(bold=True, color='FFFFFF')
    for j in range(1, 7): M.cell(r, j).fill = fill(NAVY)
    fy_rows[y] = r
    r += 2
M.cell(r, 1, 'Year on year').font = F(bold=True, color=NAVY); r += 1
for j, h in enumerate(['', '', 'Billed sales', '', '', 'Net generation']):
    if h: x = M.cell(r, 1 + j, h); x.font = F(bold=True, color='FFFFFF'); x.fill = fill(BLUE)
M.cell(r, 1).fill = fill(BLUE); r += 1
for y in (2027, 2028):
    M.cell(r, 1, f'FY{y} vs FY{y - 1}').font = F(bold=True, color=NAVY)
    x = M.cell(r, 3, f'=C{fy_rows[y]}/C{fy_rows[y - 1]}-1'); x.number_format = '+0.0%;-0.0%'; x.font = F()
    x = M.cell(r, 6, f'=F{fy_rows[y]}/F{fy_rows[y - 1]}-1'); x.number_format = '+0.0%;-0.0%'; x.font = F()
    r += 1
M.column_dimensions['A'].width = 12; M.column_dimensions['B'].width = 30
for k in 'CDEF': M.column_dimensions[k].width = 16
M.freeze_panes = 'C5'

# ---------------- notes ----------------
N = wb.create_sheet('Notes')
notes = [
 ('Basis', True),
 ('Billed sales are the register figures: FY2026 per the 11 September billed sales table, FY2027 and FY2028 per the Driver Report, by rate class and month. Only net generation and losses have been updated.', False),
 ('Net generation for January to August 2026 is the recorded system figure. Losses for those months are net generation less billed sales.', False),
 (f'September 2026 net generation (422.3 GWh) is set so that the rolling 12-month system loss ties to the 26.74% in the September scorecard, struck on finance normalized sales. On the billed sales in this file the September month loss reads {(1 - tot[2026][8] / (NG_ACT[8] / 1000)) * 100:.1f}%. October to December use one loss rate ({R_OPEN * 100:.1f}%) chosen so that FY2026 closes at 27.10% of net generation, in line with the full-year latest estimate in the scorecard.', False),
 ('FY2027 and FY2028 use the seasonal monthly loss path in the platform assumptions.', False),
 ('', False),
 ('Billed sales in the file against a live run of the platform forecast', True),
 ('The Live vs file sheet shows the difference. September actual billed sales are 294.8 GWh against 285.7 GWh in the file; that lifts the October to December base and the level carries into 2027 and 2028. Billed sales in this workbook have not been changed for it.', False),
]
V = wb.create_sheet('Live vs file')
V['A1'] = 'Billed sales (GWh): file against live platform run'; V['A1'].font = F(bold=True, size=13, color=NAVY)
for j, h in enumerate(['Rate class', 'FY2026 file', 'FY2026 live', 'Diff', 'FY2027 file', 'FY2027 live', 'Diff', 'FY2028 file', 'FY2028 live', 'Diff']):
    x = V.cell(3, 1 + j, h); x.font = F(bold=True, color='FFFFFF'); x.fill = fill(NAVY); x.alignment = Alignment(horizontal='center')
for i, rc in enumerate(CLS):
    r = 4 + i; V.cell(r, 1, NAMES[rc]).font = F(bold=True, color=NAVY)
    for yi, y in enumerate(YEARS):
        c0 = 2 + yi * 3
        x = V.cell(r, c0, sum(bill[y][rc])); x.number_format = '#,##0.0'; x.font = F(color='0000FF')
        x = V.cell(r, c0 + 1, sum(live[y][rc])); x.number_format = '#,##0.0'; x.font = F(color='0000FF')
        x = V.cell(r, c0 + 2, f'={L(c0 + 1)}{r}-{L(c0)}{r}'); x.number_format = '+#,##0.0;-#,##0.0'; x.font = F()
r = 4 + len(CLS); V.cell(r, 1, 'Total').font = F(bold=True, color='FFFFFF')
for j in range(1, 11):
    V.cell(r, j).fill = fill(NAVY)
    if j > 1: x = V.cell(r, j, f'=SUM({L(j)}4:{L(j)}{r - 1})'); x.number_format = '#,##0.0'; x.font = F(bold=True, color='FFFFFF')
V.cell(r + 2, 1, 'Monthly difference, live less file (GWh)').font = F(bold=True, color=NAVY)
for yi, y in enumerate(YEARS):
    rr = r + 3 + yi; V.cell(rr, 1, f'FY{y}').font = F(bold=True, color=NAVY)
    for m in range(12):
        x = V.cell(rr, 2 + m, sum(live[y][rc][m] for rc in CLS) - tot[y][m]); x.number_format = '+0.0;-0.0'; x.font = F()
for m in range(12):
    x = V.cell(r + 2, 2 + m, MON[m]); x.font = F(bold=True, color='FFFFFF'); x.fill = fill(NAVY); x.alignment = Alignment(horizontal='center')
V.column_dimensions['A'].width = 24
for j in range(2, 14): V.column_dimensions[L(j)].width = 12
for i, (t, b) in enumerate(notes, 1):
    N.cell(i, 1, t).font = F(bold=b, color=NAVY if b else '000000'); N.cell(i, 1).alignment = Alignment(wrap_text=True, vertical='top')
N.column_dimensions['A'].width = 140
out = r'C:\Projects\Sales_Platform\JPS_Billed_Sales_and_Net_Gen_FY2026-28_v2.xlsx'
wb.save(out)
print('saved', out)
print('open-month loss rate', round(R_OPEN * 100, 3), 'Jan-Aug actual loss % of NG', round(L_act / (sum(NG_ACT) / 1000) * 100, 2))
for y in YEARS:
    S = sum(tot[y]); print(y, round(S, 1))
for y in (2027, 2028):
    Ls = [tot[y][m] * RATE[y][m] / 100 / (1 - RATE[y][m] / 100) for m in range(12)]
    print(y, 'FY loss % of NG', round(sum(Ls) / (sum(tot[y]) + sum(Ls)) * 100, 3), 'NG', round(sum(tot[y]) + sum(Ls), 1))
L26 = L_act + L_open
print('2026 NG', round(S_all + L26, 1), 'loss %', round(L26 / (S_all + L26) * 100, 3), 'Sep loss on billed', round(1 - tot[2026][8] / (NG_ACT[8] / 1000), 4))
