# -*- coding: utf-8 -*-
# FY2027 sales forecast (GWh billed, prepaid included), refreshed on actuals to October 2026.
# Method: class level run rate (2025 clean shape x post-recovery ratio) with account overlays for RT70 and hotels.
import json, csv, collections, os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
HERE = r'C:\Projects\Sales_Platform'
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
CL = ['RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']
# actuals by class, GWh (jps_actuals, prepaid included from 2025). 2024 is RT40 and above only.
A = json.load(open(HERE + r'\analysis\_fy27_actuals.json'))   # {'2025-01': {'RT10': x, ...}, ...}
g = lambda y, m, c: A['%d-%02d' % (y, m)][c]
# LE and held plan by class (financials workbook, 'Billed by rate class')
ws = openpyxl.load_workbook(HERE + r'\JPS_Billed_Sales_and_Net_Gen_FY2026-28_v5.xlsx', data_only=True)['Billed by rate class']
hdr = [c.value for c in ws[1]]
rows = {r[0].value: [c.value for c in r] for r in ws.iter_rows(min_row=2)}
def held(c, y):
    return sum(rows[c][hdr.index('%s %d' % (m, y % 100))] for m in MON) if ('%s %d' % ('Jan', y % 100)) in hdr else None
ORDK = {'RT10': 'RT10', 'RT20': 'RT20', 'RT40': 'RT40', 'RT50': 'RT50', 'RT60-ST': 'RT60-ST', 'RT70': 'RT70'}
LEY = json.load(open(HERE + r'\analysis\_oct_deep.json'))['le']
yr = lambda c, y: sum(LEY[c]['%s %d' % (m, y % 100)] for m in MON)

# --- assumptions ---------------------------------------------------------------------------------
ratio = {}   # post-recovery year-on-year ratio, Jul-Sep 2026 over Jul-Sep 2025 (October added where the 2025 base was not storm affected)
for c in CL:
    mons = (7, 8, 9, 10) if c in ('RT10', 'RT20', 'RT40', 'RT60-ST') else (7, 8, 9)
    ratio[c] = sum(g(2026, m, c) for m in mons) / sum(g(2025, m, c) for m in mons)
G_RES = 0.008                               # 2027 organic growth on the post-recovery base, RT10 and RT20: customers +1.5%, solar and efficiency drag
G_COM = lambda m: 0.0 if m <= 3 else 0.010  # commercial: no growth until the economy turns (Q2 2027)
# seasonal index for January to September: month over the August-September mean of the same year, averaged over 2024 and 2025 (both pre-storm)
R24 = json.load(open(os.path.join(HERE, 'analysis', '_fy27_res24.json')))
def ser(y, c, m):
    if y == 2024 and c in ('RT10', 'RT20'): return R24['2024-%02d' % m][c]
    return g(y, m, c)
W = {2024: 0.25, 2025: 0.75}   # 2025 is the latest clean year and carries prepaid; 2024 is postpaid only
IDX = {}; LEVEL = {}
for c in ('RT10', 'RT20', 'RT40', 'RT50'):
    IDX[c] = {m: sum(W[y] * ser(y, c, m) / (sum(ser(y, c, k) for k in (8, 9)) / 2) for y in (2024, 2025)) for m in range(1, 10)}
    LEVEL[c] = sum(g(2026, k, c) for k in (8, 9)) / 2      # post-recovery level: August and September 2026 mean (July 2024 was hurricane Beryl, so July is left out of both)
# Nov and Dec 2027 follow 2024's pre-storm pattern off October
shape = {}
for c in ('RT40', 'RT50', 'RT60-ST', 'RT70'):
    shape[c] = (g(2024, 11, c) / g(2024, 10, c), g(2024, 12, c) / g(2024, 10, c))
sh = json.load(open(HERE + r'\analysis\_fy27_shape_res.json')); shape['RT10'] = tuple(sh['RT10']); shape['RT20'] = tuple(sh['RT20'])
shape['RT70'] = (1.0, 1.0)
# hotels: share of the remaining gap to pre-storm that is back, by month of 2027
HOTEL_GAP = 4.0                     # GWh a month: Oct 2026 hotels 17.3 vs 21.3 in Oct 2025
hf = [0.30, 0.34, 0.38, 0.42, 0.46, 0.50, 0.52, 0.54, 0.56, 0.58, 0.60, 0.62]   # Dec reopenings (1,982 rooms), Hyatt in H1 and the rest of the 2,524 rooms
HOTEL_SPLIT = {'RT50': 0.60, 'RT40': 0.20, 'RT70': 0.10, 'RT20': 0.10}
# RT70 account overlays, GWh a month vs the October 2026 level
RT70_OVR = {'Alcoa to zero from November (main account 0.26 in October)': -0.259,
            'PAC Kingston Airport: 80% on-site PV, not yet visible in October billing': -0.825 * 0.8,
            'MBJ Airports: grid draw down 47% (public record: about 60% solar)': -1.503 * 0.47,
            'Windalco: October 1.86 reset to the Jul-Oct average of 1.57': -(1.855 - 1.57),
            'Petrojam: October 1.76 reset to the July, August and October average of 1.69 (September 0.85 was the fire outage)': -(1.764 - (1.694 + 1.607 + 1.764) / 3)}
WMP = 0.209 * 0.70   # West Meat Packers (RT50 group): 70% of load leaves from March 2027

f27 = {c: [0.0] * 12 for c in CL}
for c in CL:
    for m in range(1, 13):
        if c == 'RT60-ST': f27[c][m - 1] = g(2026, 10, c); continue
        gr = G_RES if c in ('RT10', 'RT20') else G_COM(m)
        if c == 'RT70':
            base = g(2026, 10, c) + sum(RT70_OVR.values())
            f27[c][m - 1] = base; continue
        if m <= 9: v = LEVEL[c] * IDX[c][m] * (1 + gr)
        else:
            s = {10: 1.0, 11: shape[c][0], 12: shape[c][1]}[m]
            v = g(2026, 10, c) * (1 + (G_RES if c in ('RT10', 'RT20') else 0.01)) * s
        f27[c][m - 1] = v
for c, sp in HOTEL_SPLIT.items():
    for m in range(12): f27[c][m] += HOTEL_GAP * hf[m] * sp
for m in range(2, 12): f27['RT50'][m] -= WMP     # March onward
tot = {c: sum(f27[c]) for c in CL}; T = sum(tot.values())
# FY2026 outlook: January to October actual plus November and December on the 2024 pattern (same as the October deck)
fy26 = {}
for c in CL:
    a = sum(g(2026, m, c) for m in range(1, 11)); s = shape[c]
    fy26[c] = a + g(2026, 10, c) * (s[0] + s[1])
heldfy = {c: yr(c, 27) for c in CL}; lefy = {c: yr(c, 26) for c in CL}
print('ratios', {c: round(ratio[c], 3) for c in CL})
print('%-8s %8s %8s %8s %8s %8s %8s' % ('class', 'FY26LE', 'FY26out', 'held27', 'new27', 'vs held', 'vs 26out'))
for c in CL: print('%-8s %8.1f %8.1f %8.1f %8.1f %+8.1f %+7.1f%%' % (c, lefy[c], fy26[c], heldfy[c], tot[c], tot[c] - heldfy[c], (tot[c] / fy26[c] - 1) * 100))
print('%-8s %8.1f %8.1f %8.1f %8.1f %+8.1f %+7.1f%%' % ('Total', sum(lefy.values()), sum(fy26.values()), sum(heldfy.values()), T, T - sum(heldfy.values()), (T / sum(fy26.values()) - 1) * 100))
hot = sum(HOTEL_GAP * hf[m] for m in range(12)); print('hotel uplift', round(hot, 1), 'RT70 overlay/month', round(sum(RT70_OVR.values()), 2), 'WMP', round(WMP * 10, 2))
json.dump({'f27': f27, 'fy26': fy26, 'held': heldfy, 'le': lefy, 'ratio': ratio, 'hotel': hot}, open(HERE + r'\analysis\_fy27_result.json', 'w'))
json.dump({'rt10': f27['RT10'], 'fy26': fy26['RT10']}, open(HERE + r'\analysis\_fy27_rt10_base.json', 'w'))   # class-level RT10 before the weather and EV overlays

# --- workbook ------------------------------------------------------------------------------------
wb = openpyxl.Workbook(); H = Font(bold=True, color='FFFFFF'); HF = PatternFill('solid', fgColor='1F3864'); B = Font(bold=True)
s1 = wb.active; s1.title = 'Summary'
s1.append(['FY2027 sales forecast: GWh billed including prepaid. Actuals to October 2026.']); s1['A1'].font = Font(bold=True, size=13)
s1.append(['Central case. Held = financials plan (FY2027 3,439.5). Nothing in the platform has been changed.']); s1.append([])
s1.append(['Class', 'FY2026 LE', 'FY2026 outlook', 'FY2027 held', 'FY2027 new view', 'New vs held', 'New vs held %', 'New vs FY2026 outlook %'])
for c in CL: s1.append([c, round(lefy[c], 1), round(fy26[c], 1), round(heldfy[c], 1), round(tot[c], 1)])
r0, r1 = 5, 4 + len(CL)
for r in range(r0, r1 + 1):
    s1.cell(r, 6, f'=E{r}-D{r}'); s1.cell(r, 7, f'=E{r}/D{r}-1'); s1.cell(r, 8, f'=E{r}/C{r}-1')
tr = r1 + 1; s1.cell(tr, 1, 'Total').font = B
for col in 'BCDE': s1[f'{col}{tr}'] = f'=SUM({col}{r0}:{col}{r1})'; s1[f'{col}{tr}'].font = B
s1[f'F{tr}'] = f'=E{tr}-D{tr}'; s1[f'G{tr}'] = f'=E{tr}/D{tr}-1'; s1[f'H{tr}'] = f'=E{tr}/C{tr}-1'
for r in range(r0, tr + 1):
    for col in 'BCDEF': s1[f'{col}{r}'].number_format = '#,##0.0'
    for col in 'GH': s1[f'{col}{r}'].number_format = '0.0%'
s2 = wb.create_sheet('Monthly 2027'); s2.append(['Class'] + MON + ['FY2027'])
for c in CL: s2.append([c] + [round(v, 2) for v in f27[c]])
for r in range(2, 2 + len(CL)): s2.cell(r, 14, f'=SUM(B{r}:M{r})')
n = 2 + len(CL); s2.cell(n, 1, 'Total').font = B
for ci in range(2, 15): s2.cell(n, ci, f'=SUM({get_column_letter(ci)}2:{get_column_letter(ci)}{n - 1})').font = B
for r in range(2, n + 1):
    for ci in range(2, 15): s2.cell(r, ci).number_format = '#,##0.0'
s3 = wb.create_sheet('Assumptions')
A3 = [['Assumption', 'Value', 'Basis'],
      ['Method, RT10 RT20 RT40 RT50', 'January to September 2027 = post-recovery level x seasonal index x 2027 growth. October to December = October 2026 actual x growth x 2024 October-to-December pattern.', 'Seasonal index blends 2025 (75%) and 2024 (25%), both pre-storm. November and December 2025 are storm months and are not used.'],
      ['Post-recovery level RT10 (GWh a month)', round(LEVEL['RT10'], 2), 'August and September 2026 mean, prepaid included.'],
      ['Post-recovery level RT20', round(LEVEL['RT20'], 2), 'August and September 2026 mean.'],
      ['Post-recovery level RT40', round(LEVEL['RT40'], 2), 'August and September 2026 mean.'],
      ['Post-recovery level RT50', round(LEVEL['RT50'], 2), 'August and September 2026 mean. Carries the hotel gap as at Q3.'],
      ['Residential growth 2027', G_RES, 'Customers about +1.5%, less solar and efficiency drag. Zero-consumption premises coming back is not included (upside about 1.3% of RT10).'],
      ['Commercial growth 2027', '0% Jan-Mar, +1.0% from April', 'GDP still contracting in Q3 2026; growth expected from Q2 2027.'],
      ['Hotel gap closed by month (Jan to Dec)', ', '.join('%.0f%%' % (x * 100) for x in hf), 'Share of the 4.0 GWh a month gap to pre-storm that is back. December 2026 reopenings (1,982 rooms), Hyatt in H1 2027 (2,524 rooms in total), energy factor about 70% per reopened room.'],
      ['Hotel uplift split', 'RT50 60%, RT40 20%, RT70 10%, RT20 10%', 'By where the 144 hotel accounts bill.'],
      ['Hotel uplift FY2027 (GWh)', round(hot, 1), '']]
for k, v in RT70_OVR.items(): A3.append(['RT70 overlay: ' + k, round(v, 3), 'GWh a month from January 2027'])
A3.append(['West Meat Packers', round(-WMP, 3), 'GWh a month from March 2027: 70% of load leaves (KAM, solar plus LNG)'])
A3.append(['Not in the base (risk)', 'Windalco pilot (-12 GWh), FLOW cell sites, NWC solar, net billing expansion, Alcoa standby floor (+3 GWh)', 'Probability-weight in the revenue-at-risk register.'])
A3.append(['Not in the base (upside)', 'Zero-consumption premises returning, El Nino, new hospitals, PriceSmart Kingston', ''])
for r in A3: s3.append(r)
alt = {}; alt_eq = {}
for c in ('RT10', 'RT20', 'RT40', 'RT50'):
    i25 = {m: ser(2025, c, m) / (sum(ser(2025, c, k) for k in (8, 9)) / 2) for m in range(1, 10)}
    gr_ = lambda m: G_RES if c in ('RT10', 'RT20') else G_COM(m)
    alt[c] = sum(LEVEL[c] * (i25[m] - IDX[c][m]) * (1 + gr_(m)) for m in range(1, 10))
    i24 = {m: ser(2024, c, m) / (sum(ser(2024, c, k) for k in (8, 9)) / 2) for m in range(1, 10)}
    alt_eq[c] = sum(LEVEL[c] * (0.5 * i24[m] + 0.5 * i25[m] - IDX[c][m]) * (1 + gr_(m)) for m in range(1, 10))
print('equal-weight delta', round(sum(alt_eq.values()), 1)); print('alt index (2025 only) delta', {c: round(v, 1) for c, v in alt.items()}, 'total', round(sum(alt.values()), 1))
print('monthly total', [round(sum(f27[c][m] for c in CL), 1) for m in range(12)])
s4 = wb.create_sheet('Sensitivities'); s4.append(['Lever', 'FY2027 GWh impact', 'Note'])
sens = [['Each 1% on residential (RT10)', tot['RT10'] / 100, ''], ['Each 1% on RT20', tot['RT20'] / 100, ''], ['Each 1% on RT40', tot['RT40'] / 100, ''],
        ['MBJ at -77% instead of -47%', -1.503 * 0.30 * 12, 'KAM view of the 6 MW PV'], ['Hotel gap closed at +/-10 points all year', HOTEL_GAP * 0.10 * 12, ''],
        ['Zero-consumption premises back by mid-2027', tot['RT10'] * 0.013 / 2, 'About 7,742 premises x 181 kWh a month, half a year'],
        ['Alcoa holds 0.26 GWh a month standby', 0.259 * 12, ''],
        ['Seasonal index weights 50/50 for 2024 and 2025', sum(alt_eq.values()), 'Central case weights 2025 at 75%'],
        ['Seasonal index from 2025 only instead of the 75/25 blend', sum(alt.values()), 'RT10 %.1f, RT20 %.1f, RT40 %.1f, RT50 %.1f' % tuple(alt[c] for c in ('RT10', 'RT20', 'RT40', 'RT50'))]]
for r in sens: s4.append([r[0], round(r[1], 1), r[2]])
for sh_ in wb.worksheets:
    for cell in sh_[1 if sh_.title != 'Summary' else 4]: cell.font = H if sh_.title != 'Summary' or cell.row == 4 else cell.font
    for col in sh_.columns: sh_.column_dimensions[col[0].column_letter].width = 18
for sh_ in (s1,):
    for cell in s1[4]: cell.font = H; cell.fill = HF
for sh_ in (s2, s3, s4):
    for cell in sh_[1]: cell.font = H; cell.fill = HF
s3.column_dimensions['A'].width = 52; s3.column_dimensions['B'].width = 60; s3.column_dimensions['C'].width = 80
for r in s3.iter_rows():
    for cell in r: cell.alignment = Alignment(wrap_text=True, vertical='top')
p = HERE + r'\JPS_Sales_Forecast_FY2027_Nov2026.xlsx'; wb.save(p); print('saved', p)
