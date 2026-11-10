# -*- coding: utf-8 -*-
# National Water Commission, June to October 2026, by parish (billing extract, every account under the NWC name).
import csv
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
MO = ['Jun', 'Jul', 'Aug', 'Sep', 'Oct']
D = {m: pd.read_pickle(r'_cust\_nwc_%s.pkl' % m.lower()) for m in MO}
PM = {r[0].strip().upper(): r[1] for r in list(csv.reader(open(r'C:\Users\jwilson\Downloads\Parish Grouping.csv')))[1:] if len(r) >= 2}
for d in D.values(): d['pg'] = d.parish.str.strip().str.upper().map(PM).fillna('Unmapped')
net = pd.DataFrame({m: D[m].groupby('pg').net.sum() for m in MO}).fillna(0); adj = pd.DataFrame({m: D[m].groupby('pg').adj.sum() for m in MO}).fillna(0)
gross = pd.DataFrame({m: D[m].groupby('pg').gross.sum() for m in MO}).fillna(0); nacc = pd.DataFrame({m: D[m].groupby('pg').acct.nunique() for m in MO}).fillna(0).max(axis=1)
order = (net['Oct'] - net['Jun']).sort_values(ascending=False).index
NAVY = '062552'; hdr = Font(bold=True, color='FFFFFF'); fill = PatternFill('solid', fgColor=NAVY); thin = Side(style='thin', color='BBBBBB'); box = Border(top=thin, bottom=thin, left=thin, right=thin)
def head(ws, r, vals):
    for i, v in enumerate(vals, 1):
        c = ws.cell(r, i, v); c.font = hdr; c.fill = fill; c.alignment = Alignment(wrap_text=True, vertical='center'); c.border = box
wb = Workbook(); ws = wb.active; ws.title = 'By parish'
ws['A1'] = 'National Water Commission: June to October 2026 by parish'; ws['A1'].font = Font(bold=True, size=14)
ws['A2'] = 'MWh billed. Net is after billed-consumption adjustments; gross is before. Source: the monthly billing extract, every account under the NWC name, all rate codes.'
# block 1: net MWh
ws['A4'] = 'Net MWh'; ws['A4'].font = Font(bold=True)
head(ws, 5, ['Parish', 'Accounts'] + MO + ['Oct vs Sep MWh', 'Oct vs Sep %', 'Oct vs Jun MWh', 'Oct vs Jun %'])
r0 = 6
for i, pg in enumerate(order):
    r = r0 + i; v = [pg, int(nacc[pg])] + [net.loc[pg, m] / 1e3 for m in MO] + [f'=G{r}-F{r}', f'=IF(F{r}=0,"",H{r}/F{r})', f'=G{r}-C{r}', f'=IF(C{r}=0,"",J{r}/C{r})']
    for j, x in enumerate(v, 1): ws.cell(r, j, x)
rl = r0 + len(order) - 1; rt = rl + 1
ws.cell(rt, 1, 'Total').font = Font(bold=True)
for col in range(2, 8): L = get_column_letter(col); ws.cell(rt, col, f'=SUM({L}{r0}:{L}{rl})').font = Font(bold=True)
ws.cell(rt, 8, f'=G{rt}-F{rt}').font = Font(bold=True); ws.cell(rt, 9, f'=H{rt}/F{rt}').font = Font(bold=True); ws.cell(rt, 10, f'=G{rt}-C{rt}').font = Font(bold=True); ws.cell(rt, 11, f'=J{rt}/C{rt}').font = Font(bold=True)
for r in range(r0, rt + 1):
    for col in (3, 4, 5, 6, 7, 8, 10): ws.cell(r, col).number_format = '#,##0;[Red]-#,##0'
    for col in (9, 11): ws.cell(r, col).number_format = '0.0%;[Red]-0.0%'
# block 2: adjustments
b2 = rt + 3; ws.cell(b2, 1, 'Billed-consumption adjustments, MWh (negative takes consumption off)').font = Font(bold=True)
head(ws, b2 + 1, ['Parish', ''] + MO)
for i, pg in enumerate(order):
    r = b2 + 2 + i; ws.cell(r, 1, pg)
    for j, m in enumerate(MO): ws.cell(r, 3 + j, adj.loc[pg, m] / 1e3).number_format = '#,##0.0;[Red]-#,##0.0'
rt2 = b2 + 2 + len(order); ws.cell(rt2, 1, 'Total').font = Font(bold=True)
for col in range(3, 8): L = get_column_letter(col); c = ws.cell(rt2, col, f'=SUM({L}{b2 + 2}:{L}{rt2 - 1})'); c.font = Font(bold=True); c.number_format = '#,##0.0;[Red]-#,##0.0'
# block 3: gross
b3 = rt2 + 3; ws.cell(b3, 1, 'Gross MWh (before adjustments)').font = Font(bold=True)
head(ws, b3 + 1, ['Parish', ''] + MO + ['Oct vs Sep %'])
for i, pg in enumerate(order):
    r = b3 + 2 + i; ws.cell(r, 1, pg)
    for j, m in enumerate(MO): ws.cell(r, 3 + j, gross.loc[pg, m] / 1e3).number_format = '#,##0'
    ws.cell(r, 8, f'=IF(F{r}=0,"",G{r}/F{r}-1)').number_format = '0.0%;[Red]-0.0%'
rt3 = b3 + 2 + len(order); ws.cell(rt3, 1, 'Total').font = Font(bold=True)
for col in range(3, 8): L = get_column_letter(col); c = ws.cell(rt3, col, f'=SUM({L}{b3 + 2}:{L}{rt3 - 1})'); c.font = Font(bold=True); c.number_format = '#,##0'
c = ws.cell(rt3, 8, f'=G{rt3}/F{rt3}-1'); c.font = Font(bold=True); c.number_format = '0.0%;[Red]-0.0%'
ws.cell(rt3 + 2, 1, 'Parishes follow the platform grouping (KSAN, KSAS and Portmore are shown separately from St. Andrew and St. Catherine proper).')
for col, w in zip('ABCDEFGHIJK', (16, 10, 12, 12, 12, 12, 12, 14, 12, 14, 12)): ws.column_dimensions[col].width = w
ws.freeze_panes = 'C6'

# movers: Sep to Oct and Jun to Oct
nets = {m: D[m].set_index('acct').net for m in MO}; info = pd.concat([D[m][['acct', 'name', 'srat', 'pg', 'addr']] for m in MO]).drop_duplicates('acct', keep='last').set_index('acct')
M = pd.DataFrame(nets).fillna(0); M = M.join(info); M['chg'] = M.Oct - M.Sep; M = M.reindex(M.chg.abs().sort_values(ascending=False).index).head(40)
w2 = wb.create_sheet('Biggest movers')
w2['A1'] = 'Largest account movements, September to October 2026, with June to August for context (net kWh)'; w2['A1'].font = Font(bold=True, size=13)
head(w2, 3, ['Account', 'Parish', 'Rate code', 'Service address'] + MO + ['Oct vs Sep kWh'])
for i, (ac, x) in enumerate(M.iterrows()):
    r = 4 + i
    for j, v in enumerate([ac, x.pg, x.srat, x.addr] + [x[m] for m in MO] + [f'=H{r}-G{r}'], 1): w2.cell(r, j, v)
    for col in range(5, 10): w2.cell(r, col).number_format = '#,##0;[Red]-#,##0'
for col, w in zip('ABCDEFGHI', (18, 15, 10, 38, 12, 12, 12, 12, 14)): w2.column_dimensions[col].width = w
w2.freeze_panes = 'A4'

# adjustments
A = pd.concat([D[m].assign(mo=m) for m in MO]); A = A[A.adj != 0].copy(); A['abs'] = A.adj.abs(); A = A.sort_values('abs', ascending=False).head(60)
w3 = wb.create_sheet('Adjustments')
w3['A1'] = 'Billed-consumption adjustments on NWC accounts, June to October 2026 (largest 60)'; w3['A1'].font = Font(bold=True, size=13)
head(w3, 3, ['Month', 'Account', 'Parish', 'Rate code', 'Gross kWh', 'Adjustment kWh', 'Net kWh'])
for i, (_, x) in enumerate(A.iterrows()):
    for j, v in enumerate([x.mo, x.acct, x.pg, x.srat, x.gross, x.adj, x.net], 1): w3.cell(4 + i, j, v)
    for col in (5, 6, 7): w3.cell(4 + i, col).number_format = '#,##0;[Red]-#,##0'
for col, w in zip('ABCDEFG', (8, 18, 15, 10, 14, 16, 14)): w3.column_dimensions[col].width = w
wb.save(r'C:\Projects\Sales_Platform\analysis\_deliverables_Nov2026\JPS_NWC_Jun-Oct2026_by_Parish.xlsx'); print('saved')
