# -*- coding: utf-8 -*-
# Builds the October 2026 KAM forecast accuracy workbook (live formulas) and a one-page PDF source.
import collections, json, os, sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from kam_acc_oct import *
import kam_data as kd

OUT = r'C:\Projects\Sales_Platform'
MON = {7: 'Jul', 8: 'Aug', 9: 'Sep'}
ctx = collections.defaultdict(dict)
for r in d['act']:
    if r['jps_ac'] and r['year'] == 2026 and r['month'] in (7, 8, 9):
        ctx[r['jps_ac']][r['month']] = ctx[r['jps_ac']].get(r['month'], 0.0) + float(r['kwh'] or 0) / G
sep = collections.defaultdict(lambda: dict(f=0.0, a=0.0, ab=0.0))
for a in kd.accts.values():
    if a['kam'] in KAMS:
        t = sep[a['kam']]; t['f'] += a['sep_fc']; t['a'] += a['sep_act']; t['ab'] += abs(a['sep_act'] - a['sep_fc'])
SEP = {k: (1 - abs(t['a'] - t['f']) / t['a'], 1 - t['ab'] / t['a']) for k, t in sep.items()}
SEP_TOT = (1 - abs(sum(t['a'] for t in sep.values()) - sum(t['f'] for t in sep.values())) / sum(t['a'] for t in sep.values()), 1 - sum(t['ab'] for t in sep.values()) / sum(t['a'] for t in sep.values()))

def adj_text(a):
    if not a['adj']: return ''
    p, k, rc, j = a['adj'][0]
    return ('%+.0f%%' % p if p else '') + (' %s' % rc if rc else '') + ((': ' + j[:110]) if j else '')

NAVY, BLUE, LIGHT, GREY = '062552', '0E4E95', 'D9E1F2', '66788A'
HF = Font(name='Arial', bold=True, color='FFFFFF', size=10); HFILL = PatternFill('solid', fgColor=NAVY)
BF = Font(name='Arial', size=10); BB = Font(name='Arial', size=10, bold=True)
thin = Side(style='thin', color=LIGHT); BORD = Border(bottom=thin)
wb = openpyxl.Workbook()

# ---------------- All accounts (inputs) ----------------
wa = wb.active; wa.title = 'All accounts'
hdr = ['KAM', 'Account', 'Customer', 'Rate class', 'Forecast Oct (GWh)', 'Actual Oct (GWh)', 'Miss (GWh)', 'Absolute miss (GWh)', 'Jul (GWh)', 'Aug (GWh)', 'Sep (GWh)', 'Adjustment on file for Oct']
wa.append(hdr)
rows = sorted([a for a in A.values() if a['kam'] in KAMS], key=lambda a: -abs(a['miss']))
for i, a in enumerate(rows, start=2):
    c = ctx.get(a['ac'], {})
    wa.append([a['kam'], a['ac'], a['name'], a['rc'], round(a['fc'], 6), round(a['act'], 6), f'=F{i}-E{i}', f'=ABS(G{i})', round(c.get(7, 0.0), 6), round(c.get(8, 0.0), 6), round(c.get(9, 0.0), 6), adj_text(a)])
n = len(rows) + 1
for c in range(1, len(hdr) + 1):
    cell = wa.cell(row=1, column=c); cell.font = HF; cell.fill = HFILL; cell.alignment = Alignment(wrap_text=True, vertical='center')
for r in range(2, n + 1):
    for c in range(5, 12): wa.cell(row=r, column=c).number_format = '#,##0.000;(#,##0.000)'
    for c in range(1, 13): wa.cell(row=r, column=c).font = BF
for col, w in zip('ABCDEFGHIJKL', (18, 18, 36, 9, 13, 13, 11, 13, 10, 10, 10, 70)): wa.column_dimensions[col].width = w
wa.freeze_panes = 'A2'; wa.auto_filter.ref = f'A1:L{n}'

# ---------------- Summary (formulas over All accounts) ----------------
ws = wb.create_sheet('Summary', 0)
ws['A1'] = 'KAM forecast accuracy: October 2026'; ws['A1'].font = Font(name='Arial', bold=True, size=14, color=NAVY)
ws['A2'] = ('Forecast = the Driver Forecast after the September close (actuals through September, every adjustment on file). Actual = October billing per account. '
            'Net accuracy = 1 - |actual - forecast| / actual on the total. Account-level accuracy = 1 - sum of the individual account misses / actual.')
ws['A2'].alignment = Alignment(wrap_text=True, vertical='top'); ws['A2'].font = Font(name='Arial', size=9, color=GREY); ws.merge_cells('A2:K2'); ws.row_dimensions[2].height = 40
h = ['KAM', 'Accounts', 'Forecast (GWh)', 'Actual (GWh)', 'Variance (GWh)', 'Net accuracy', 'Account-level accuracy', 'Sep net accuracy', 'Sep account-level', 'Change in account-level (pts)']
for i, t in enumerate(h, start=1):
    c = ws.cell(row=4, column=i, value=t); c.font = HF; c.fill = HFILL; c.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center')
ws.row_dimensions[4].height = 32
R = f"'All accounts'!"
r0 = 5
for j, k in enumerate(sorted(KAMS, key=lambda k: -BYK[k]['act'])):
    r = r0 + j
    ws.cell(row=r, column=1, value=k)
    ws.cell(row=r, column=2, value=f'=COUNTIF({R}$A:$A,A{r})')
    ws.cell(row=r, column=3, value=f'=SUMIFS({R}$E:$E,{R}$A:$A,A{r})')
    ws.cell(row=r, column=4, value=f'=SUMIFS({R}$F:$F,{R}$A:$A,A{r})')
    ws.cell(row=r, column=5, value=f'=D{r}-C{r}')
    ws.cell(row=r, column=6, value=f'=1-ABS(D{r}-C{r})/D{r}')
    ws.cell(row=r, column=7, value=f'=1-SUMIFS({R}$H:$H,{R}$A:$A,A{r})/D{r}')
    ws.cell(row=r, column=8, value=round(SEP[k][0], 4)); ws.cell(row=r, column=9, value=round(SEP[k][1], 4))
    ws.cell(row=r, column=10, value=f'=(G{r}-I{r})*100')
rl = r0 + len(KAMS) - 1; rt = rl + 1
ws.cell(row=rt, column=1, value='Total')
ws.cell(row=rt, column=2, value=f'=SUM(B{r0}:B{rl})'); ws.cell(row=rt, column=3, value=f'=SUM(C{r0}:C{rl})'); ws.cell(row=rt, column=4, value=f'=SUM(D{r0}:D{rl})')
ws.cell(row=rt, column=5, value=f'=D{rt}-C{rt}'); ws.cell(row=rt, column=6, value=f'=1-ABS(D{rt}-C{rt})/D{rt}')
ws.cell(row=rt, column=7, value=f'=1-SUM({R}$H:$H)/D{rt}'); ws.cell(row=rt, column=8, value=round(SEP_TOT[0], 4)); ws.cell(row=rt, column=9, value=round(SEP_TOT[1], 4)); ws.cell(row=rt, column=10, value=f'=(G{rt}-I{rt})*100')
for r in range(r0, rt + 1):
    for c in range(1, 11): ws.cell(row=r, column=c).font = BB if r == rt else BF; ws.cell(row=r, column=c).border = BORD
    for c in (3, 4, 5): ws.cell(row=r, column=c).number_format = '#,##0.00;(#,##0.00)'
    for c in (6, 7, 8, 9): ws.cell(row=r, column=c).number_format = '0.0%'
    ws.cell(row=r, column=2).number_format = '#,##0'; ws.cell(row=r, column=10).number_format = '+0.0;-0.0;0.0'
for c in range(1, 11): ws.cell(row=rt, column=c).fill = PatternFill('solid', fgColor=LIGHT)
for col, w in zip('ABCDEFGHIJ', (20, 10, 14, 13, 13, 12, 14, 12, 14, 16)): ws.column_dimensions[col].width = w
ws.cell(row=rt + 2, column=1, value='Where the miss sits').font = Font(name='Arial', bold=True, color=NAVY, size=11)
pos = sum(a['miss'] for a in rows if a['miss'] > 0); neg = sum(a['miss'] for a in rows if a['miss'] < 0)
notes = [f'The forecast was low by {TOTAL["var"]:.2f} GWh: accounts above forecast added {pos:.2f} GWh and accounts below it took away {abs(neg):.2f} GWh.',
         f'{sum(1 for a in rows if abs(a["miss"]) > 0.05)} accounts missed by more than 0.05 GWh and {sum(1 for a in rows if abs(a["miss"]) > 0.01)} by more than 0.01 GWh, out of {len(rows):,}.',
         f'The five largest account misses are {sum(abs(a["miss"]) for a in MISSES[:5]) / TOTAL["abs"] * 100:.0f}% of the total miss (September: 29%), so the miss is more spread out than last month.',
         'The forecast is a reconstruction of the Driver Forecast as it stood after the September close, using the engine as it was before the roll-forward change. It is not a stored snapshot.']
for i, t in enumerate(notes): ws.cell(row=rt + 3 + i, column=1, value=t).font = BF
ws.sheet_view.showGridLines = False

# ---------------- Largest misses ----------------
wm = wb.create_sheet('Largest misses', 1)
hm = ['KAM', 'Customer', 'Rate class', 'Forecast (GWh)', 'Actual (GWh)', 'Miss (GWh)', 'Jul', 'Aug', 'Sep', 'Adjustment on file for October', 'Reason from KAM (to add)']
wm.append(hm)
for i, a in enumerate(MISSES[:40], start=2):
    c = ctx.get(a['ac'], {})
    wm.append([a['kam'], a['name'], a['rc'], round(a['fc'], 3), round(a['act'], 3), round(a['miss'], 3), round(c.get(7, 0.0), 3), round(c.get(8, 0.0), 3), round(c.get(9, 0.0), 3), adj_text(a), ''])
    for cc in range(4, 10): wm.cell(row=i, column=cc).number_format = '#,##0.000;(#,##0.000)'
for cc in range(1, len(hm) + 1):
    x = wm.cell(row=1, column=cc); x.font = HF; x.fill = HFILL; x.alignment = Alignment(wrap_text=True, vertical='center')
for r in range(2, 42):
    for cc in range(1, 12): wm.cell(row=r, column=cc).font = BF
for col, w in zip('ABCDEFGHIJK', (18, 38, 9, 12, 12, 11, 8, 8, 8, 70, 40)): wm.column_dimensions[col].width = w
wm.freeze_panes = 'A2'

wn = wb.create_sheet('Method')
for i, t in enumerate(['Forecast: Driver Forecast engine as it stood after the September close (actuals through September 2026; all operational adjustments on file; the engine before the 26 October roll-forward change). Account level for KAM-assigned accounts.',
    'Actual: October 2026 billed kWh per account from the loaded billing file (prepaid does not affect KAM accounts).',
    'Population: every account with a named KAM plus accounts that billed in October but had no forecast (forecast zero). September figures use the same method.',
    'Net accuracy = 1 - |actual - forecast| / actual on the KAM total. Account-level accuracy = 1 - sum(|actual - forecast| per account) / actual.',
    'Rows with an adjustment note show the entry on file for October. KAMs: use the last column on Largest misses for the reason.'], start=1):
    wn.cell(row=i, column=1, value=t).font = BF
wn.column_dimensions['A'].width = 160
fn = os.path.join(OUT, 'JPS_KAM_Forecast_Accuracy_Oct2026.xlsx'); wb.save(fn); print('saved', fn)
json.dump({'by_kam': BYK, 'total': TOTAL, 'sep': SEP, 'sep_tot': SEP_TOT, 'pos': pos, 'neg': neg}, open('_kam_acc_oct_summary.json', 'w'))
