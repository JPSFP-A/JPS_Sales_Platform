# -*- coding: utf-8 -*-
# 3-way September 2026 reconciliation: Earnings Sheet vs Power BI (customer billed = 1) vs Sales Platform (MWh by class).
import openpyxl, pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as L
SP = r'C:\Users\jwilson\AppData\Local\Temp\claude\C--Projects-Sales-Platform-analysis\ad90b481-68e3-4fc1-a153-582185660fa8\scratchpad'
# ---- Earnings sheet (row 10 = MWh, row 26 = $) ----
ws = openpyxl.load_workbook(r'C:\Users\jwilson\AppData\Local\Temp\Esheet 9-26 (1).xlsx', data_only=True).worksheets[0]
r10 = [c.value for c in ws[10]]; r26 = [c.value for c in ws[26]]
cols = {'RT10': 3, 'RT20': 7, 'RT40': 11, 'RT50': 15, 'RT60-ST': 19, 'RT70': 23}   # 0-based index of the MWH column in row 10
SHEET = {k: r10[v] for k, v in cols.items()}
SHEETREV = {k: r26[v - 1] for k, v in cols.items()}
assert abs(sum(SHEET.values()) - r10[26] / 1e3) < 0.01, (sum(SHEET.values()), r10[26])   # sheet's own total kWh
# ---- Raw September billing file: not-billed rows the Sheet carries, and RT40 facts ----
import csv, bisect
csv.field_size_limit(10**9)
def _num(x):
    try: return float(str(x).replace(',', '') or 0)
    except Exception: return 0.0
CLASS_OF = {'RM': 'RT10', 'EM': 'RT10', 'PR': 'RT10', 'CM': 'RT20', 'PC': 'RT20', 'ST': 'RT60-ST'}
NBTX = []; RT40 = []
with open(r'C:\Projects\Sales_Platform\analysis\Sep 26.csv', encoding='utf-8', errors='replace', newline='') as _f:
    for _r in csv.DictReader(_f):
        _rc = (_r.get('rate_class') or '').strip(); _cb = (_r.get('cust_billed') or '').strip(); _k = _num(_r.get('net_kwh_billed_consump'))
        if _cb == '0' and _rc in CLASS_OF and _k != 0:
            NBTX.append((_r['Cust_Code'].replace(',', ''), _r['Prem_Code'], (_r.get('Name') or '').strip(), (_r.get('Srat_Code') or '').strip(), _rc, CLASS_OF[_rc],
                         (_r.get('Parish') or '').strip(), (_r.get('Account_Status') or '').strip(), _k, _num(_r.get('net_revenue'))))
        if _rc == 'LC-40' and _cb == '1':
            RT40.append((_r['Cust_Code'].replace(',', ''), _r['Prem_Code'], (_r.get('Name') or '').strip(), _k, _num(_r.get('net_revenue'))))
NBTX.sort(key=lambda x: (x[5], x[8]))
# ---- Power BI (Sep-2026 aggregated by source / rate category / rate_class / cust_billed) ----
g = pd.read_pickle(SP + r'\pbi_sep_groups.pkl'); g['kwh'] = g['kwh'].astype(float); g['rev'] = g['rev'].astype(float)
bl = g[g['cust_billed'] == 1]; nb = g[g['cust_billed'] == 0]
PBI = {}; PBIREV = {}
for _, r in bl.iterrows():
    cat = r['Rate category'] if pd.notna(r['Rate category']) else ''
    k = cat if cat else 'RT10'      # blank-category prepaid (9.0 MWh) shown in RT10, as the Platform books it
    PBI[k] = PBI.get(k, 0) + r['kwh'] / 1e3; PBIREV[k] = PBIREV.get(k, 0) + r['rev']
PBI_NB = nb['kwh'].sum() / 1e3; PBI_EV = nb[nb['Rate category'] == 'EV']['kwh'].sum() / 1e3
# ---- Platform (jps_actuals Sep-2026) ----
PLAT = {'RT10': (111556151.68 + 3009820.05) / 1e3, 'RT20': (37101742.97 + 23406970.13 + 108857.56) / 1e3, 'RT40': 67312952.00 / 1e3,
        'RT50': 30252675.00 / 1e3, 'RT60-ST': 3413193.00 / 1e3, 'RT70': 18642652.00 / 1e3}
PLATREV = {'RT10': 6451463793.33 + 173513942.16, 'RT20': 1988780636.39 + 1304136773.91 + 6568992.16, 'RT40': 3199838484.00, 'RT50': 1203080583.00,
           'RT60-ST': 213697099.00, 'RT70': 874143463.00}

def gp(df, src, cat, rc):
    m = (df['Source'] == src) & (df['Rate category'].fillna('') == cat) & (df['rate_class'].fillna('') == rc)
    return df[m]['kwh'].sum() / 1e3

H = Font(bold=True, color='FFFFFF'); HF = PatternFill('solid', fgColor='1F3864'); B = Font(bold=True)
Y = PatternFill('solid', fgColor='FFF2CC'); R = PatternFill('solid', fgColor='FCE4D6')
NUM = '#,##0.000;[Red]-#,##0.000'
wb = openpyxl.Workbook()
# =========== Sheet 1: by class ===========
s1 = wb.active; s1.title = '3-way by class'
s1['A1'] = 'September 2026 - three-way reconciliation of sales volume (MWh)'; s1['A1'].font = Font(bold=True, size=13)
s1['A2'] = 'Earnings Sheet (finance) vs Power BI (Monthly Sales report, customer billed = 1) vs Sales Platform (jps_actuals). Differences are formulas.'
for i, h in enumerate(['Class', 'Earnings Sheet', 'Power BI (billed = 1)', 'Sales Platform', 'Sheet - Power BI', 'Power BI - Platform', 'Sheet - Platform'], 1):
    c = s1.cell(4, i, h); c.font = H; c.fill = HF; c.alignment = Alignment(horizontal='center', wrap_text=True)
classes = ['RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']
for r, k in enumerate(classes, 5):
    s1.cell(r, 1, k); s1.cell(r, 2, SHEET[k]); s1.cell(r, 3, PBI.get(k, 0.0)); s1.cell(r, 4, PLAT[k])
    s1.cell(r, 5, f'=B{r}-C{r}'); s1.cell(r, 6, f'=C{r}-D{r}'); s1.cell(r, 7, f'=B{r}-D{r}')
t = 5 + len(classes)   # total row = 11
s1.cell(t, 1, 'Total').font = B
for c in range(2, 8): s1.cell(t, c, f'=SUM({L(c)}5:{L(c)}{t-1})').font = B
for r in range(5, t + 1):
    for c in range(2, 8): s1.cell(r, c).number_format = NUM
s1.cell(t + 2, 1, 'Notes').font = B
notes = [
 'Power BI and the Platform agree to within 0.01 MWh in every class: the Platform is the Power BI customer-billed = 1 line.',
 'Earnings Sheet vs the other two: (1) the Sheet includes not-billed rows (RT10 -11.5, RT20 -30.5, RT60 street lighting +1.7 MWh); (2) RT40 is 40.0 MWh lower on the Sheet, same raw file, cause not identified; (3) the Sheet puts "unassigned"-tariff prepaid (589.7 MWh) in RT20 and everything else in RT10, whereas Power BI and the Platform put only RT20-PAYG (108.9 MWh) in RT20 - this moves 480.9 MWh RT10 -> RT20 with no effect on the total (inferred: ties to the third decimal).',
 'Power BI has 9.0 MWh of prepaid with a blank rate category; it is included in RT10 above, as the Platform books it.',
 'Power BI customer-billed = 0 rows (not in any report): EV tariff +68.9 MWh and credits/adjustments -40.4 MWh, net +28.6 MWh. Power BI grand total incl. these is 294,833.6 MWh - see the Bridge sheet.',
]
for i, n in enumerate(notes):
    rr = t + 3 + i; s1.cell(rr, 1, n); s1.cell(rr, 1).alignment = Alignment(wrap_text=True, vertical='top')
    s1.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=7); s1.row_dimensions[rr].height = 62 if i == 1 else 34
s1.column_dimensions['A'].width = 22
for c in 'BCDEFG': s1.column_dimensions[c].width = 19
s1.row_dimensions[4].height = 32
# =========== Sheet 2: bridge ===========
s2 = wb.create_sheet('Bridge')
s2['A1'] = 'Bridge: Earnings Sheet -> Power BI (billed = 1) -> Sales Platform (MWh, September 2026 total)'; s2['A1'].font = Font(bold=True, size=13)
for i, h in enumerate(['Step', 'MWh', 'Running total', 'Comment'], 1):
    c = s2.cell(3, i, h); c.font = H; c.fill = HF
sheet_nb = (gp(nb, 'Postpaid', 'RT10', 'RM') + gp(nb, 'Postpaid', 'RT10', 'EM') + gp(nb, 'Postpaid', 'RT10', 'PR')
            + gp(nb, 'Postpaid', 'RT20', 'CM') + gp(nb, 'Postpaid', 'RT20', 'PC') + gp(nb, 'Postpaid', 'RT60-ST', 'ST'))   # not-billed rows the Sheet carries (excl. EV)
rt40_gap = PBI['RT40'] - SHEET['RT40']
rows = [
 (4, 'Earnings Sheet total', "='3-way by class'!B11", '=B4', 'Sheet total MWh (RT10..RT70)'),
 (5, '+ Remove not-billed rows carried on the Sheet', "=-SUM('Transactions - not billed'!I5:I%d)/1000" % (4 + len(NBTX)), '=C4+B5', '%d transactions on the "Transactions - not billed" sheet (RT10 -11.5, RT20 -30.5, RT60 street lighting +1.7)' % len(NBTX)),
 (6, '+ RT40 difference', rt40_gap, '=C5+B6', 'Same raw file, Sheet RT40 lower by this amount - transaction NOT identified, see "RT40 gap" sheet'),
 (7, '= Power BI billed = 1 (computed)', None, '=C6', ''),
 (8, 'Power BI billed = 1 (reported)', "='3-way by class'!C11", None, 'Power BI pivot, customer billed = 1 line (postpaid + prepaid), Sep-2026'),
 (9, 'Unreconciled (computed - reported)', None, '=C7-B8', 'Rounding in the Sheet class figures'),
 (10, 'Platform less Power BI billed = 1', "='3-way by class'!D11-'3-way by class'!C11", '=C8+B10', 'Rounding (whole-kWh account rows)'),
 (11, '= Sales Platform total', None, '=C10', ''),
 (12, 'Sales Platform total (jps_actuals)', "='3-way by class'!D11", None, 'Queried from jps_actuals'),
 (13, 'Unreconciled (computed - platform)', None, '=C11-B12', 'Should be 0'),
 (15, 'Memo - Power BI grand total (all rows)', "=B8+B16+B17", None, 'What the Power BI pivot shows as Grand Total'),
 (16, '   + EV tariff (customer billed = 0)', PBI_EV, None, 'In no report'),
 (17, '   + not-billed credits/adjustments', PBI_NB - PBI_EV, None, 'In no report except the Sheet'),
]
for r, lab, v, f, com in rows:
    s2.cell(r, 1, lab); s2.cell(r, 4, com)
    if v is not None: s2.cell(r, 2, v)
    if f: s2.cell(r, 3, f)
    for c in (2, 3): s2.cell(r, c).number_format = NUM
    if lab.startswith('='): s2.cell(r, 1).font = B; s2.cell(r, 3).font = B
    if lab.startswith('Unreconciled'): s2.cell(r, 3).fill = Y
s2.column_dimensions['A'].width = 44; s2.column_dimensions['B'].width = 16; s2.column_dimensions['C'].width = 16; s2.column_dimensions['D'].width = 90
# =========== Sheet 3: components ===========
s3 = wb.create_sheet('Components')
s3['A1'] = 'What each source includes (MWh). Values from the Power BI table (Sep-2026); Y/N = included in that report.'; s3['A1'].font = B
for i, h in enumerate(['Component', 'Class', 'MWh', 'Earnings Sheet', 'Power BI (billed = 1)', 'Sales Platform', 'Note'], 1):
    c = s3.cell(3, i, h); c.font = H; c.fill = HF
P = lambda src, cat, rc: gp(bl, src, cat, rc)
N = lambda src, cat, rc: gp(nb, src, cat, rc)
comp = [
 ('Postpaid billed - RT10 (RM+EM)', 'RT10', P('Postpaid', 'RT10', 'RM') + P('Postpaid', 'RT10', 'EM'), 'Y', 'Y', 'Y', ''),
 ('Prepaid-tagged billed (PR10)', 'RT10', P('Postpaid', 'RT10', 'PR'), 'Y', 'Y', 'Y', 'In the postpaid file; premise also in the prepaid report. Includes one 99.99 MWh bill (cust 1598805)'),
 ('Prepaid report - RT10-PAYG tariff', 'RT10', P('Prepaid', 'RT10', 'RT10-PAYG'), 'Y', 'Y', 'Y', ''),
 ('Prepaid report - unassigned tariff', 'RT10 (Sheet: RT20)', P('Prepaid', 'RT10', 'unassigned'), 'Y', 'Y', 'Y', 'Class differs: Sheet shows it in RT20'),
 ('Prepaid report - blank tariff', 'RT10', P('Prepaid', '', ''), 'Y', 'Y', 'Y', 'Blank rate category in Power BI'),
 ('Postpaid billed - RT20 (CM)', 'RT20', P('Postpaid', 'RT20', 'CM'), 'Y', 'Y', 'Y', ''),
 ('Prepaid-tagged billed (PC / PR20)', 'RT20', P('Postpaid', 'RT20', 'PC'), 'Y', 'Y', 'Y', ''),
 ('Prepaid report - RT20-PAYG tariff', 'RT20 (Sheet: RT10)', P('Prepaid', 'RT20', 'RT20-PAYG'), 'Y', 'Y', 'Y', 'Class differs: Sheet shows it in RT10'),
 ('RT40 billed (LC-40)', 'RT40', P('Postpaid', 'RT40', 'LC-40'), 'Y (less 40.0)', 'Y', 'Y', 'Sheet RT40 is 40.002 MWh lower - unexplained'),
 ('RT50 billed (LC-50)', 'RT50', P('Postpaid', 'RT50', 'LC-50'), 'Y', 'Y', 'Y', ''),
 ('RT60 billed (ST+TL)', 'RT60-ST', P('Postpaid', 'RT60-ST', 'ST') + P('Postpaid', 'RT60-ST', 'TL'), 'Y', 'Y', 'Y', ''),
 ('RT70 billed (WT)', 'RT70', P('Postpaid', 'RT70', 'WT'), 'Y', 'Y', 'Y', ''),
 ('Not-billed rows - RT10 (RM+EM+PR)', 'RT10', N('Postpaid', 'RT10', 'RM') + N('Postpaid', 'RT10', 'EM') + N('Postpaid', 'RT10', 'PR'), 'Y', 'N', 'N', 'Credits/adjustments flagged cust_billed = 0'),
 ('Not-billed rows - RT20 (CM+PC)', 'RT20', N('Postpaid', 'RT20', 'CM') + N('Postpaid', 'RT20', 'PC'), 'Y', 'N', 'N', ''),
 ('Not-billed rows - RT60 (ST)', 'RT60-ST', N('Postpaid', 'RT60-ST', 'ST'), 'Y', 'N', 'N', ''),
 ('EV tariff (26 premises) - not billed', 'EV', N('Postpaid', 'EV', 'EV'), 'N', 'N', 'N', 'Flagged cust_billed = 0; in no report'),
]
for i, row in enumerate(comp, 4):
    for j, v in enumerate(row, 1): s3.cell(i, j, v)
    s3.cell(i, 3).number_format = NUM
    for j in (4, 5, 6):
        if str(row[j - 1]).startswith('N') or 'less' in str(row[j - 1]): s3.cell(i, j).fill = R
e = 4 + len(comp)
s3.cell(e, 1, 'Total of components included in Power BI (billed = 1)').font = B
s3.cell(e, 3, f'=SUMIF(E4:E{e-1},"Y",C4:C{e-1})').font = B; s3.cell(e, 3).number_format = NUM
s3.cell(e + 1, 1, 'Power BI billed = 1 total (check)'); s3.cell(e + 1, 3, "='3-way by class'!C11"); s3.cell(e + 1, 3).number_format = NUM
s3.cell(e + 2, 1, 'Difference'); s3.cell(e + 2, 3, f'=C{e}-C{e+1}'); s3.cell(e + 2, 3).number_format = NUM; s3.cell(e + 2, 3).fill = Y
s3.cell(e + 3, 1, 'All components (= Power BI grand total)'); s3.cell(e + 3, 3, f'=SUM(C4:C{e-1})'); s3.cell(e + 3, 3).number_format = NUM
for c, w in zip('ABCDEFG', (48, 22, 14, 16, 22, 16, 70)): s3.column_dimensions[c].width = w
# =========== Sheet 4: revenue (indicative) ===========
s4 = wb.create_sheet('Revenue (indicative)')
s4['A1'] = 'Revenue by class, J$ - indicative only, the sources are NOT on the same basis'; s4['A1'].font = B
for i, h in enumerate(['Class', 'Earnings Sheet', 'Power BI billed = 1 (postpaid net_revenue; model has no prepaid revenue)', 'Sales Platform (net of GCT)', 'Sheet - Platform'], 1):
    c = s4.cell(3, i, h); c.font = H; c.fill = HF; c.alignment = Alignment(wrap_text=True)
for r, k in enumerate(classes, 4):
    s4.cell(r, 1, k); s4.cell(r, 2, SHEETREV[k]); s4.cell(r, 3, PBIREV.get(k, 0)); s4.cell(r, 4, PLATREV[k]); s4.cell(r, 5, f'=B{r}-D{r}')
    for c in range(2, 6): s4.cell(r, c).number_format = '#,##0'
tr = 4 + len(classes)
s4.cell(tr, 1, 'Total').font = B
for c in range(2, 6): s4.cell(tr, c, f'=SUM({L(c)}4:{L(c)}{tr-1})').font = B; s4.cell(tr, c).number_format = '#,##0'
s4.cell(tr + 2, 1, 'The Sheet revenue includes items the other two do not carry (fuel exchange, rate adjustments, true-ups, RPD interest). Power BI has no prepaid revenue. Not bridged.')
s4.column_dimensions['A'].width = 12
for c in 'BCDE': s4.column_dimensions[c].width = 26
s4.row_dimensions[3].height = 62
# =========== Sheet 5: not-billed transactions ===========
s5 = wb.create_sheet('Transactions - not billed')
s5['A1'] = 'Not-billed transactions the Earnings Sheet carries in RT10 / RT20 / RT60 (cust_billed = 0, kWh <> 0), September 2026 raw billing file'; s5['A1'].font = B
s5['A2'] = 'Power BI (billed = 1) and the Platform exclude these. Total kWh feeds the Bridge sheet.'
for i, h in enumerate(['Cust code', 'Premise', 'Name', 'Srat code', 'Rate class', 'Class', 'Parish', 'Account status', 'kWh', 'Net revenue J$'], 1):
    c = s5.cell(4, i, h); c.font = H; c.fill = HF
for i, row in enumerate(NBTX, 5):
    for j, v in enumerate(row, 1): s5.cell(i, j, v)
    s5.cell(i, 9).number_format = '#,##0.00;[Red]-#,##0.00'; s5.cell(i, 10).number_format = '#,##0.00;[Red]-#,##0.00'
last = 4 + len(NBTX)
s5.cell(last + 2, 3, 'Total').font = B; s5.cell(last + 2, 9, f'=SUM(I5:I{last})').font = B; s5.cell(last + 2, 10, f'=SUM(J5:J{last})').font = B
for k, cl in enumerate(('RT10', 'RT20', 'RT60-ST')):
    s5.cell(last + 3 + k, 3, cl); s5.cell(last + 3 + k, 9, f'=SUMIF(F5:F{last},"{cl}",I5:I{last})'); s5.cell(last + 3 + k, 10, f'=SUMIF(F5:F{last},"{cl}",J5:J{last})')
for rr in range(last + 2, last + 6):
    s5.cell(rr, 9).number_format = '#,##0.00;[Red]-#,##0.00'; s5.cell(rr, 10).number_format = '#,##0.00;[Red]-#,##0.00'
for c, w in zip('ABCDEFGHIJ', (11, 11, 40, 10, 10, 10, 18, 10, 14, 16)): s5.column_dimensions[c].width = w
s5.freeze_panes = 'A5'; s5.auto_filter.ref = f'A4:J{last}'
# =========== Sheet 6: RT40 gap ===========
s6 = wb.create_sheet('RT40 gap')
s6['A1'] = 'RT40: Earnings Sheet vs raw billing file (same September 2026 billing data)'; s6['A1'].font = Font(bold=True, size=13)
tot40 = sum(r[3] for r in RT40); prem40 = len({(r[0], r[1]) for r in RT40})
facts = [
 ('Raw file, RT40 (LC-40) billed rows', len(RT40), 'count'),
 ('Raw file, distinct RT40 premises (billed)', prem40, 'count'),
 ('Earnings Sheet, RT40 customers', 1962, 'count'),
 ('Raw file RT40 kWh', tot40, 'kWh'),
 ('Earnings Sheet RT40 kWh', SHEET['RT40'] * 1000, 'kWh'),
 ('Gap (raw - Sheet)', tot40 - SHEET['RT40'] * 1000, 'kWh'),
]
for i, h in enumerate(['Item', 'Value', 'Unit'], 1):
    c = s6.cell(3, i, h); c.font = H; c.fill = HF
for i, (a, b_, u) in enumerate(facts, 4):
    s6.cell(i, 1, a); s6.cell(i, 2, b_); s6.cell(i, 3, u); s6.cell(i, 2).number_format = '#,##0.00'
T = tot40 - SHEET['RT40'] * 1000
srt = sorted(RT40, key=lambda r: r[3]); ks = [r[3] for r in srt]
cands = [r for r in RT40 if abs(r[3] - T) < 2.0]
pairs = []
for i, r in enumerate(srt):
    j = bisect.bisect_left(ks, T - r[3] - 0.6)
    while j < len(ks) and ks[j] <= T - r[3] + 0.6:
        if j > i: pairs.append((r, srt[j]))
        j += 1
base = 4 + len(facts) + 1
s6.cell(base, 1, 'What this shows').font = B
msgs = [
 'The Sheet customer count (1,962) equals the number of distinct RT40 premises in the raw file, so no whole account is missing from the Sheet: the gap is a kWh difference on accounts that are counted.',
 'No single RT40 bill equals the gap. The only round-number bill near it is Salada Foods Jamaica Ltd, 40,000.00 kWh, J$2,019,806 (cust 100826, premise 101454), about 2 kWh from the gap. Candidate only, not confirmed.',
 '%d pairs of RT40 bills also sum to the gap within +/-0.6 kWh, so matching on the amount alone cannot identify the transaction. The billing run or the finance adjustment listing is needed to confirm.' % len(pairs),
]
for i, m in enumerate(msgs, 1):
    s6.cell(base + i, 1, m); s6.cell(base + i, 1).alignment = Alignment(wrap_text=True, vertical='top')
    s6.merge_cells(start_row=base + i, start_column=1, end_row=base + i, end_column=3); s6.row_dimensions[base + i].height = 48
r0 = base + len(msgs) + 2
s6.cell(r0, 1, 'Candidate transactions').font = B
for i, h in enumerate(['Name / premise', 'kWh', 'Net revenue J$'], 1):
    c = s6.cell(r0 + 1, i, h); c.font = H; c.fill = HF
rr = r0 + 2
for r in cands:
    s6.cell(rr, 1, f'{r[2]} ({r[0]}-{r[1]}) - single bill'); s6.cell(rr, 2, r[3]); s6.cell(rr, 3, r[4]); rr += 1
for a, b_ in sorted(pairs, key=lambda p: -max(p[0][3], p[1][3]))[:3]:
    s6.cell(rr, 1, f'{a[2]} ({a[0]}-{a[1]}) + {b_[2]} ({b_[0]}-{b_[1]}) - two bills'); s6.cell(rr, 2, a[3] + b_[3]); s6.cell(rr, 3, a[4] + b_[4]); rr += 1
for x in range(r0 + 2, rr):
    s6.cell(x, 2).number_format = '#,##0.00'; s6.cell(x, 3).number_format = '#,##0.00'
s6.column_dimensions['A'].width = 100; s6.column_dimensions['B'].width = 16; s6.column_dimensions['C'].width = 16
out = r'C:\Projects\Sales_Platform\JPS_Sep2026_3Way_Recon_v4.xlsx'
wb.save(out); print('saved', out)
print('SHEET', {k: round(v, 3) for k, v in SHEET.items()}, round(sum(SHEET.values()), 3))
print('PBI billed', {k: round(v, 3) for k, v in PBI.items()}, round(sum(PBI.values()), 3))
print('PLAT', {k: round(v, 3) for k, v in PLAT.items()}, round(sum(PLAT.values()), 3))
print('sheet_nb', round(sheet_nb, 3), 'rt40_gap', round(rt40_gap, 3), 'PBI_EV', round(PBI_EV, 3), 'PBI_NB all', round(PBI_NB, 3))
print('components in PBI billed', round(sum(c[2] for c in comp if c[4] == 'Y'), 3), 'all', round(sum(c[2] for c in comp), 3))
