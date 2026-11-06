# -*- coding: utf-8 -*-
# Forecast reassessment workbook: run rate vs live engine and held forecast, account review, timing, hotels, evidence, decision checklist.
# Nothing here writes to the platform. Inputs are the saved engine run (26 Oct 2026, adjustments unchanged at 187 rows) and Supabase actuals to Sep 2026.
import json, collections, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
sys.stdout.reconfigure(encoding='utf-8')

OUT = r'C:\Projects\Sales_Platform\JPS_Forecast_Reassessment_Nov2026.xlsx'
rows = {r['ac']: r for r in json.load(open('fc_reassess_rows.json'))}
adj = json.load(open('fc_reassess_adj.json'))
CL = json.load(open('fc_reassess_class.json'))

NAVY, BLUE, LIGHT, GREY = '062552', '0E4E95', 'D9E1F2', 'F3F6FB'
HF = Font(name='Arial', bold=True, color='FFFFFF', size=10); BF = Font(name='Arial', size=10); BB = Font(name='Arial', size=10, bold=True)
INP = Font(name='Arial', size=10, color='0000FF'); TF = Font(name='Arial', size=14, bold=True, color=NAVY); NF = Font(name='Arial', size=9, italic=True, color='666666')
FILL_H = PatternFill('solid', fgColor=NAVY); FILL_G = PatternFill('solid', fgColor=GREY); FILL_L = PatternFill('solid', fgColor=LIGHT); FILL_Y = PatternFill('solid', fgColor='FFF2CC')
thin = Side(style='thin', color='BFC7D5'); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
WRAP = Alignment(wrap_text=True, vertical='top'); CEN = Alignment(horizontal='center', vertical='top', wrap_text=True)

wb = Workbook()
def sheet(name, widths, title, note=None):
    ws = wb.create_sheet(name); ws.sheet_view.showGridLines = False
    for i, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(i)].width = w
    ws['A1'] = title; ws['A1'].font = TF
    if note: ws['A2'] = note; ws['A2'].font = NF
    return ws
def header(ws, r, labels):
    for j, t in enumerate(labels, 1):
        c = ws.cell(r, j, t); c.font = HF; c.fill = FILL_H; c.alignment = CEN; c.border = BOX
    ws.row_dimensions[r].height = 32
def put(ws, r, vals, fonts=None, fmt=None, fill=None, bold=False):
    for j, v in enumerate(vals, 1):
        c = ws.cell(r, j, v); c.font = (fonts[j - 1] if fonts and fonts[j - 1] else (BB if bold else BF)); c.alignment = WRAP; c.border = BOX
        if fmt and fmt.get(j): c.number_format = fmt[j]
        if fill: c.fill = fill

# ------------------------------------------------------------------ data helpers
def r_(ac): return rows[ac]
def ishotel(r):
    i = (r['ind'] or '').lower(); return any(k in i for k in ('hotel', 'motel', 'resort', 'accommodation'))
MS = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
hot26 = [0] * 12; hot27 = [0] * 12; hot25 = [0] * 12
for r in rows.values():
    if r['rc'] != 'RT10' and ishotel(r):
        for m in range(12): hot26[m] += r['k26'][m] / 1e6; hot27[m] += r['k27'][m] / 1e6; hot25[m] += r['p25'][m] / 1e6
q3_25_avg = sum(hot25[6:9]) / 3; sep26 = hot26[8]

# ------------------------------------------------------------------ 1. Decision checklist (built last so it can be first)
# columns: id, area, item, finding, action, q4_26, fy27, rng, basis, rec, sources
ITEMS = [
 ('A1', 'Residential', 'RT10 Q4 2026 phasing', 'Engine and held both run Oct-Dec at about 115 GWh a month, flat on September. By design the 2026 chain has no residential seasonality (it is gated to 2027 on, to tie to the submission). Seasonal shape from the 2026 budget gives 311-320 GWh for Q4 against 340 held (346 engine).', 'Apply a seasonal step-down to Oct-Dec 2026 RT10 (overlay on the Driver Forecast).', -25.0, 0.0, 'Q4: -20 to -30', 'Inferred (3 methods agree; engine design verified in code)', 'Accept', 'Run-rate by class; method sheet'),
 ('A2', 'Residential', 'RT20 Q4 2026 phasing', 'Same cause as A1. RT20 is held at 59-61 GWh a month against a budget-shape run rate of 167-169 GWh for the quarter (held 178.9).', 'Same overlay for RT20.', -11.0, 0.0, 'Q4: -10 to -12', 'Inferred', 'Accept', 'Run-rate by class'),
 ('A3', 'Commercial', 'RT40-RT70 Q4 2026 net', 'Commercial Q4 is at or slightly below run rate: RT40 held 202 vs 202-212; RT50 86 vs 87-88; RT70 53 vs about 54 after removing Alcoa and PAC. Small upside only.', 'Leave RT50/RT70; lift RT40 modestly or leave and accept as headroom.', 7.0, 0.0, 'Q4: +2 to +14', 'Inferred', 'Accept', 'Run-rate by class'),
 ('A4', 'Residential', 'RT10 Q4 2027 shape (seasonality table)', 'The 2027 residential seasonality table is "derived from jps_actuals 2025 monthly kWh". That includes Nov-Dec 2025, the Hurricane Melissa months (heavier buckets show -31% to -42% in November). Result: engine RT10 Q4 2027 is 316.9 GWh, 8.5% BELOW Q4 2026 (346.4) in a year it grows 4%. Nov 2027 (99.1) sits below Dec 2027 (104.5), the reverse of normal.', 'Rebuild Nov and Dec indices without 2025 storm months (use Jan-Oct 2025 shape plus 2026 budget shape for Nov-Dec).', 0.0, 11.0, 'FY27: +6 to +16', 'Verified cause; size inferred', 'Accept', 'Run-rate by class; macro table'),
 ('A5', 'Residential', 'RT10 FY2027 level', 'Held 1,275.0 (engine 1,283.0) is consistent with Q3 2026 annualised and de-seasonalised (about 1,265-1,290). Q3 YoY is +4%, customers +1.5%. No level change needed. El Nino (warmer, drier into 2027) is an upside of about 3-6 GWh not included; net billing expansion is a downside not included.', 'Hold the FY2027 residential level. Do not add weather or solar overlays yet.', 0.0, 0.0, 'n/a', 'Inferred', 'Hold', 'Evidence: weather, net billing'),
 ('B1', 'Commercial', 'Hotel recovery: timing and size', 'Engine ramps hotels smoothly from 14.9 GWh (Sep) to 17.3 (Dec 2027) and totals 199 GWh in 2027, 83% of the pre-storm run rate. Public schedule: about 1,900 rooms back in December (Sandals Montego Bay, Sandals Royal Caribbean, Iberostar, Bahia Principe), Hyatt seven properties in H1 2027, Royalton Negril and Blue Waters already back in Aug-Sep. See Hotels sheet (inputs are editable).', 'Key the storm recovery to the hotel accounts on the reopening schedule instead of a smooth class-wide ramp.', 1.7, 21.7, 'Q4: +1 to +4; FY27: +10 to +30', 'Inferred (deck schedule + public reports; arrivals still down about 20%)', 'Accept after KAM confirms', 'Hotels sheet; evidence E1-E5'),
 ('B2', 'Commercial', 'Non-hotel RT50 recovery uplift', 'Storm normalisation is keyed to rate class (RT50 +4.66% a month, uncapped through 2027). 88 non-hotel RT50 accounts (dairies, poultry, JDF, orange groves) are ramped 13% above run rate (+33 GWh) and exit 2027 at +24%, while the 34 hotel accounts, the real recovery, get +17% and stay 11% below pre-storm. GDP is still contracting in Q3 2026; growth only expected from Q2 2027.', 'Move the RT50 normalisation to hotel accounts (B1) and cap unaffected accounts at about +3% over run rate by Dec 2027.', 0.0, -17.0, 'FY27: -10 to -25', 'Verified distribution; haircut is judgement', 'Accept after KAM confirms', 'Account review; evidence E6-E7'),
 ('C1', 'Account', 'Sutherland Global (1164542-1098473)', 'KAM: 100 kW PV at three sites, completed end April and May. Platform has -50% from Jul and -80% from Aug. Actual kWh: Jun 64, Jul 76, Aug 79, Sep 77 MWh, no drop at all. 100 kW is about 13 MWh a month, 17% of this account. Deck lists Sutherland as planning stage (J$53M/yr).', 'Replace -80% with about -15% (or 0% until billing shows it).', 0.17, 0.64, 'FY27: +0.5 to +0.8', 'Verified (actuals vs entry)', 'Accept', 'Account review'),
 ('C2', 'Account', 'Clarendon Distillers (100187-100277)', 'KAM: two 333 kW CHP units being tested, -70% by year end 2026, rising to -85% from Mar 2027 (platform). Deck (tracker 1 Oct): CHP installed but idle, LNG too costly. KAM claims 450 MWh/month loss; this account bills about 176 MWh/month, so scale does not reconcile.', 'Hold at about -25% (probability-weighted) until the CHP runs; ask the KAM which accounts the 450 MWh covers.', 0.12, 1.33, 'FY27: 0 to +1.85', 'Verified conflict; weight assumed', 'Accept after KAM confirms', 'Account review; deck slide 5'),
 ('C3', 'Account', 'West Meat Packers (100312-100512)', 'KAM: 70% of load leaves "by Q1 2027" once its solar farm and two LNG units are repaired. Entered from Jan 2027, the earliest possible date.', 'Move the -70% start from Jan to Mar 2027.', 0.0, 0.47, 'FY27: +0.2 to +0.5', 'Verified text', 'Accept', 'Timing sheet'),
 ('C4', 'Account', 'MBJ Airports (804282-768320)', 'KAM: 6 MW PV commissioned by end 2026 takes grid draw to 360 MWh a month (-77%, -15.1 GWh vs run rate). Public record: 3 MW installed, a further 3 MW in progress, airport targeting "60% solar"; no commissioning date found. 60% solar implies about -45%, not -77%. Passenger volumes are down about 24% (Aug).', 'Confirm commissioning date and storage with the KAM. If -47% instead, FY27 is about +6 GWh; if the date slips to mid-2027, about +8.', 0.0, 6.0, 'FY27: 0 to +8', 'Inferred from public sources', 'Accept after KAM confirms', 'Account review; evidence E8'),
 ('C5', 'Account', 'Alcoa / Jamalco (100185-607213)', 'TG4 online early August; refinery "an island within the island". Grid draw 9.0 GWh Jul, 1.2 Aug, 0.6 Sep; forecast is zero from Nov. If 0.6 GWh a month is a standby floor, FY27 is understated by about 7 GWh. Deck: load not expected back.', 'Keep at zero. Check the October bill (due mid-November); ask the KAM for the standby level.', 0.0, 0.0, 'FY27: 0 to +7', 'Verified status; floor unknown', 'Hold', 'Account review; evidence E9'),
 ('C6', 'Account', 'PAC Kingston Airport (1411748-834411)', 'KAM: 4 MW PV from 13 Jul, staged load sharing to Sep; -80% from Oct. Deck: lost in October. Actuals: Jul 916, Aug 839, Sep 784 MWh, forecast Oct 161. Consistent.', 'No change. Confirm against the October bill.', 0.0, 0.0, 'n/a', 'Verified', 'Hold', 'Account review'),
 ('C7', 'Account', 'Windalco Ewarton (689250-102172)', 'Run rate is depressed by the July outage (Jun 2.2 GWh, Jul 1.7, Aug 1.2, Sep 1.5). Forecast 2027 averages 1.37 GWh a month, 38% below June, without any structural entry. Deck: pilot to cut up to 70% (J$346M/yr, the largest planning-stage risk). Rusal is sounding out buyers for Windalco (Sep 2026).', 'Ask the KAM for the steady-state level after the outage. Swing is about +10 GWh if it returns to June; about -12 GWh a year if the pilot goes ahead. Keep the pilot out of the base.', 0.0, 0.0, 'FY27: -12 to +10', 'Inferred', 'Hold', 'Account review; evidence E10'),
 ('D1', 'Timing', 'Restore KAM dates moved by the FY2026 lock', 'Six entries were moved later on 28 Aug "forecaster direction: FY2026 is locked to the 19 August submission": Plantation Inn (Sep), Cocalapalm (Aug), Greater Portmore Health Centre (Dec), Rainforest Seafood (Nov), Progressive Grocers Harbour View (Christmas 2026), Clarendon (Nov/Dec). Net effect on Q4 2026 is only about -0.2 GWh, but KAM-level accuracy will be measured against the dates the KAMs gave.', 'Restore the KAM-stated dates now that FY2026 is re-based to actuals.', -0.2, 0.0, 'Q4: -0.2', 'Verified', 'Accept', 'Timing sheet'),
 ('E1', 'New load', 'PriceSmart new clubs', 'Platform holds three new-customer entries: Kgn Sep 2026 (100 MWh/mo), Nov 2026 (258) and Jan 2027 (268) = 7.5 GWh in 2027, about 2.5 clubs. Existing clubs bill about 250 MWh a month each. Public: Montego Bay club opened 2 Oct 2026; Kingston (South Camp Road) now expected in 2027, no date. Deck still shows South Camp in Dec 2026.', 'One club of 250 MWh/mo from Oct 2026 (Montego Bay); one from Jul 2027 as a placeholder (Kingston).', -0.06, -3.0, 'FY27: -2 to -4', 'Verified facts; Kingston date assumed', 'Accept', 'Timing sheet; evidence E11'),
 ('E2', 'New load', 'Western Children and Adolescent Hospital (and Cornwall Regional)', 'Deck lists both hospitals as December 2026 new load; nothing in the platform. Public: the 220-bed Western Children and Adolescent Hospital is "almost ready" (Jun 2026); Cornwall Regional has its own delays.', 'Add as new customers once the Ministry of Health KAM gives kVA or kWh. Size not in the totals.', 0.0, 0.0, 'TBC', 'Missing data', 'Accept after KAM confirms', 'Timing sheet; evidence E12'),
 ('E3', 'New load', 'Progressive Grocers duplicates', 'Two identical new-customer entries (70 MWh, Dec 2027, KAM recorded as "Sheryl" and "Sheryl Davis"). Deck puts the new load in December 2026. Harbour View +40% expansion is also entered a month late (D1).', 'Delete one duplicate; confirm which store the new-customer entry is and move to the deck date.', 0.0, -0.07, 'FY27: -0.07', 'Verified', 'Accept', 'New customers table'),
 ('E4', 'New load', 'Caribbean Broilers egg farm', 'Deck: connected September 2026. Platform: new customer from Jan 2027 (132 MWh/mo). Low priority per your note on Broilers.', 'Ask the KAM for the actual connection month.', 0.4, 0.0, 'Q4: 0 to +0.4', 'Verified conflict', 'Accept after KAM confirms', 'Timing sheet'),
 ('F1', 'Watch', 'Risk register, not in the base', 'FLOW (800 cell sites planning alternative supply), Digicel solar expansion, NWC 5 MW solar (22 projects over five years), US Embassy battery-backed solar (delayed), Jamaica National solar, Jewel Paradise Cove microturbine, Windalco pilot (C7), net billing expansion (government says 100 MW distributed, online platform due Dec 2026). Rule of thumb: 10 MW of PV removes about 14-15 GWh a year.', 'Keep out of the base; probability-weight in the revenue-at-risk register (Feb 2027).', 0.0, 0.0, 'n/a', 'Assumed', 'Watch', 'Evidence E13-E14'),
]

ws = wb.active; ws.title = 'Decision checklist'; ws.sheet_view.showGridLines = False
for i, w in enumerate([5, 12, 26, 62, 42, 11, 11, 17, 24, 17, 15, 28], 1): ws.column_dimensions[get_column_letter(i)].width = w
ws['A1'] = 'Forecast reassessment: decision checklist'; ws['A1'].font = TF
ws['A2'] = 'GWh billed. Impacts are against the HELD forecast (financials LE: FY2026 3,299.7; FY2027 3,439.5). Blue cells are inputs you can overwrite. Choose a decision in column L; the totals recalculate. Nothing has been changed in the platform.'; ws['A2'].font = NF
ws['A4'] = 'Held FY2026'; ws['C4'] = 3299.661; ws['A5'] = 'Held FY2027'; ws['C5'] = 3439.5
ws['A6'] = 'Live engine FY2026 / FY2027 (26 Oct run)'; ws['C6'] = 3318.2; ws['D6'] = 3479.7
for r in (4, 5, 6): ws.cell(r, 1).font = BB; ws.cell(r, 3).font = INP; ws.cell(r, 3).number_format = '#,##0.0'
ws['D6'].font = INP; ws['D6'].number_format = '#,##0.0'
HR = 8; header(ws, HR, ['#', 'Area', 'Item', 'What we found', 'Proposed action', 'Q4 2026 GWh', 'FY2027 GWh', 'Range', 'Basis', 'My recommendation', 'Evidence', 'YOUR DECISION'])
r0 = HR + 1
for k, it in enumerate(ITEMS):
    r = r0 + k
    vals = [it[0], it[1], it[2], it[3], it[4], it[5], it[6], it[7], it[8], it[9], it[10], None]
    put(ws, r, vals, fonts=[None, None, BB, None, None, INP, INP, None, None, BB, None, None], fmt={6: '+0.0;-0.0;0.0', 7: '+0.0;-0.0;0.0'})
    ws.cell(r, 12).fill = FILL_Y
    ws.row_dimensions[r].height = max(60, 15 * (len(it[3]) // 70 + 2))
rl = r0 + len(ITEMS) - 1
dv = DataValidation(type='list', formula1='"Accept,Modify,Reject,Defer"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'L{r0}:L{rl}')
T = rl + 2
ws.cell(T, 3, 'Result if I accept my recommendations (rows marked Accept)').font = BB
ws.cell(T + 1, 3, 'Result if I also accept the "after KAM confirms" rows').font = BB
ws.cell(T + 2, 3, 'Result from YOUR decisions (Accept + Modify)').font = BB
for j, (lab, col) in enumerate((('FY2026', 'F'), ('FY2027', 'G'))):
    base = '$C$4' if col == 'F' else '$C$5'; cc = 6 + j
    ws.cell(T, cc, f'={base}+SUMIFS({col}{r0}:{col}{rl},$J{r0}:$J{rl},"Accept")')
    ws.cell(T + 1, cc, f'={base}+SUMIFS({col}{r0}:{col}{rl},$J{r0}:$J{rl},"Accept")+SUMIFS({col}{r0}:{col}{rl},$J{r0}:$J{rl},"Accept after KAM confirms")')
    ws.cell(T + 2, cc, f'={base}+SUMIFS({col}{r0}:{col}{rl},$L{r0}:$L{rl},"Accept")+SUMIFS({col}{r0}:{col}{rl},$L{r0}:$L{rl},"Modify")')
    for rr in (T, T + 1, T + 2): ws.cell(rr, cc).number_format = '#,##0.0'; ws.cell(rr, cc).font = BB; ws.cell(rr, cc).fill = FILL_L
ws.cell(T + 3, 3, 'Change vs held, my recommendations').font = BB
ws.cell(T + 3, 6, f'=F{T}-$C$4'); ws.cell(T + 3, 7, f'=G{T}-$C$5')
ws.cell(T + 4, 3, 'Change vs held, incl. KAM-confirm rows').font = BB
ws.cell(T + 4, 6, f'=F{T + 1}-$C$4'); ws.cell(T + 4, 7, f'=G{T + 1}-$C$5')
for rr in (T + 3, T + 4):
    for cc in (6, 7): ws.cell(rr, cc).number_format = '+#,##0.0;-#,##0.0'; ws.cell(rr, cc).font = BB
ws.cell(T + 6, 3, 'Reading the result').font = BB
ws.cell(T + 7, 3, 'FY2026: the correction is almost all residential and RT20 Q4 phasing (A1, A2), partly offset by commercial and hotels. It lands near the 19 August submission (3,282) and the three run-rate methods (3,275-3,290). FY2027: net upward, because the residential Q4 shape fix (A4) and hotel timing (B1) outweigh the non-hotel haircut (B2). B1 and B2 depend on one judgement (how fast hotels recover), so treat the pair together.').alignment = WRAP
ws.merge_cells(start_row=T + 7, start_column=3, end_row=T + 7, end_column=8); ws.row_dimensions[T + 7].height = 78
ws.freeze_panes = ws.cell(r0, 4)

# ------------------------------------------------------------------ 2. Run-rate by class
ws2 = sheet('Run-rate by class', [14, 11, 11, 13, 13, 13, 11, 11, 11, 4, 13, 13, 13, 13], 'Run rate against held and live engine, by rate class',
            'GWh. Q4 2026 run-rate methods: A = Sep actual x budget shape; B = Aug-Sep average x budget shape; C = Q3 actual/budget ratio x Q4 budget (C is distorted for RT70: Alcoa and PAC drop out in Q4).')
header(ws2, 4, ['Class', 'Held Q4 26', 'Engine Q4 26', 'A: Sep x shape', 'B: Aug-Sep x shape', 'C: Q3 ratio', 'Held - A', 'Held - B', 'Held - C'])
held, eng, bud, act = CL['held'], CL['eng'], CL['bud'], CL['act']
r = 5
for rc in ['RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']:
    b, a = bud[rc], act[rc]
    vals = [rc, round(sum(held[rc][9:12]), 2), round(sum(eng[rc][9:12]), 2), round(a[8] * sum(b[9:12]) / b[8], 2), round((a[7] + a[8]) / 2 * sum(b[9:12]) / ((b[7] + b[8]) / 2), 2), round(sum(a[6:9]) / sum(b[6:9]) * sum(b[9:12]), 2), f'=B{r}-D{r}', f'=B{r}-E{r}', f'=B{r}-F{r}']
    put(ws2, r, vals, fonts=[BB, INP, INP, INP, INP, INP, None, None, None], fmt={j: '#,##0.0' for j in range(2, 10)}); r += 1
put(ws2, r, ['Total', f'=SUM(B5:B{r - 1})', f'=SUM(C5:C{r - 1})', f'=SUM(D5:D{r - 1})', f'=SUM(E5:E{r - 1})', f'=SUM(F5:F{r - 1})', f'=B{r}-D{r}', f'=B{r}-E{r}', f'=B{r}-F{r}'], bold=True, fill=FILL_L, fmt={j: '#,##0.0' for j in range(2, 10)})
rt = r; r += 2
ws2.cell(r, 1, 'FY2026 if Q4 = method').font = BB
ytd = sum(sum(v) for v in act.values())
ws2.cell(r + 1, 1, 'Jan-Sep actual'); ws2.cell(r + 1, 2, round(ytd, 3)); ws2.cell(r + 1, 2).font = INP
ws2.cell(r + 2, 1, 'FY2026 (A / B / C)'); ws2.cell(r + 2, 4, f'=B{r + 1}+D{rt}'); ws2.cell(r + 2, 5, f'=B{r + 1}+E{rt}'); ws2.cell(r + 2, 6, f'=B{r + 1}+F{rt}')
ws2.cell(r + 3, 1, 'Held FY2026'); ws2.cell(r + 3, 2, 3299.661); ws2.cell(r + 3, 2).font = INP
ws2.cell(r + 4, 1, 'Submitted 19 Aug (figure of record)'); ws2.cell(r + 4, 2, 3281.97); ws2.cell(r + 4, 2).font = INP
for rr in range(r + 1, r + 5):
    for cc in range(2, 7): ws2.cell(rr, cc).number_format = '#,##0.0'
r += 7
ws2.cell(r, 1, 'FY2027 level check (GWh)').font = BB
header(ws2, r + 1, ['Class', 'Held FY27', 'Engine FY27', 'Q3-26 x 12', 'Seasonal factor', 'Run-rate level', 'Held vs level', 'Engine vs level'])
q3 = lambda rc: sum(act[rc][6:9]) / 3
LV = [('RT10', 1275.0, 1283.0, q3('RT10') * 12, 1.09), ('RT20', 691.6, 695.0, q3('RT20') * 12, 1.05), ('RT40', 838.6, 854.2, q3('RT40') * 12, 1.00), ('RT50', 400.8, 410.0, q3('RT50') * 12, 1.00), ('RT60-ST', 39.8, 40.3, q3('RT60-ST') * 12, 1.00), ('RT70', 193.7, 197.1, act['RT70'][8] * 12, 1.00)]
rr = r + 2
for rc, h, e, q, f in LV:
    put(ws2, rr, [rc, h, e, round(q, 1), f, f'=D{rr}/E{rr}', f'=B{rr}-F{rr}', f'=C{rr}-F{rr}'], fonts=[BB, INP, INP, INP, INP, None, None, None], fmt={2: '#,##0.0', 3: '#,##0.0', 4: '#,##0.0', 5: '0.00', 6: '#,##0.0', 7: '+#,##0.0;-#,##0.0', 8: '+#,##0.0;-#,##0.0'}); rr += 1
ws2.cell(rr + 1, 1, 'Notes: seasonal factor = Q3 average over annual average from Jan-Oct 2025 (pre-storm). RT10 about 1.09, RT20 about 1.05; commercial classes are close to flat (2024 named accounts: Q3 about 0.985 of annual). RT70 level uses Sep x 12 because Q3 includes Alcoa at 9 GWh in July. RT50 level is 358 against held 401: that +42 GWh is the hotel recovery, carried by the whole class (see B1, B2). RT70: Sep x 12 is 224; less Alcoa to zero (-7), PAC at -80% (-8) and MBJ at -77% (-14) gives about 195, against held 193.7, so the RT70 gap is explained by the three defections.').alignment = WRAP
ws2.merge_cells(start_row=rr + 1, start_column=1, end_row=rr + 1, end_column=9); ws2.row_dimensions[rr + 1].height = 62

# ------------------------------------------------------------------ 3. Account review
ws3 = sheet('Account review', [16, 30, 7, 9, 9, 9, 9, 10, 11, 11, 12, 11, 13, 40, 44], 'Accounts that need a decision',
            'MWh a month unless stated. Run rate = Jul-Sep 2026 actual average. Forecast = live engine run of 26 Oct 2026 (actuals to Sep). ADJ = an operational adjustment is on file.')
header(ws3, 4, ['Account', 'Name', 'Class', 'Jun 26', 'Jul 26', 'Aug 26', 'Sep 26', 'Q3 avg', 'Oct-Dec fcst avg', 'FY27 fcst (MWh)', 'Q3 avg x 12 (MWh)', 'FY27 vs run rate', 'On file', 'Finding', 'Recommendation'])
def arow(ac, finding, rec):
    r = r_(ac); a = adj.get(ac); onfile = ''
    if a:
        pcts = sorted({x[2] for x in a}); first = min((x[0], x[1]) for x in a)
        onfile = '%s from %d-%02d (%s%%)' % (a[0][3] or 'blank', first[0], first[1], ', '.join('%g' % p for p in pcts[:3]))
    return [ac, r['name'], r['rc'], r['j26'][5] / 1e3, r['j26'][6] / 1e3, r['j26'][7] / 1e3, r['j26'][8] / 1e3, r['q3'] / 1e3, sum(r['k26'][9:12]) / 3 / 1e3, sum(r['k27']) / 1e3, r['q3'] * 12 / 1e3, None, onfile, finding, rec]
ACC = [
 ('100185-607213', 'Self-generating since Aug (TG4). Draw 9.0, 1.2, 0.6 GWh Jul-Sep; forecast zero from Nov.', 'Hold at zero; confirm October bill and standby floor.'),
 ('804282-768320', 'Forecast cuts 77% from Jan 2027 on KAM 6 MW PV. Public record shows 3 MW + 3 MW in progress, "60% solar" target, no commissioning date.', 'Confirm date and storage; model -45% to -50% if only 60% solar.'),
 ('1411748-834411', '4 MW PV from 13 Jul; -80% from Oct. Matches deck (lost Oct). Actuals still falling slowly.', 'No change; check October bill.'),
 ('1164542-1098473', 'Entered -80% from Aug; actuals show no reduction in Jul-Sep. 100 kW PV is about 17% of this account.', 'Change to about -15% (or 0 until billing shows it).'),
 ('100187-100277', 'KAM: CHP defection from Dec (-70% rising to -85%). Deck: CHP idle, LNG too costly. KAM loss (450 MWh/mo) exceeds the account (176).', 'Hold at about -25% until CHP runs; reconcile accounts with KAM.'),
 ('100312-100512', 'KAM: -70% by Q1 2027 once solar and LNG units are repaired. Entered Jan 2027.', 'Start in Mar 2027.'),
 ('689250-102172', 'Run rate depressed by July outage; forecast 38% below June with no structural entry. Deck: pilot up to -70%.', 'Ask KAM for post-outage steady state; keep pilot as risk.'),
 ('571874-1063043', 'KAM: solar reinstated by Nov 2026 (-35%); moved to Jan 2027 on the FY2026 lock.', 'Restore Nov 2026.'),
 ('793321-700972', 'Existing PriceSmart club: 253 MWh a month. Sets the size of a new club.', 'Use about 250 MWh/mo per new club.'),
 ('NEW-1787589454716', 'New customer from Nov 2026 (258 MWh). One of three PriceSmart entries.', 'Replace the three entries with Montego Bay (Oct 2026) and Kingston (2027).'),
 ('NEW-1787590572137', 'New customer from Jan 2027 (268 MWh).', 'See above.'),
 ('NEW-1783578247973', 'New customer Sep 2026 (100 MWh), KAM blank.', 'See above.'),
 ('100012-100248', 'NWC Ferry Booster +60% from Feb 2027; forecast 3.2 GWh vs 1.8 run rate.', 'Keep; KAM dated Feb 2027.'),
 ('815011-1165890', 'Harbour View +40% entered Jan 2027; KAM says store opens for Christmas 2026.', 'Restore Dec 2026.'),
 ('923684-804869', 'Poly Pet +15% from Dec 2026, matches KAM and deck.', 'No change.'),
]
r = 5
for ac, f, rec in ACC:
    if ac not in rows: continue
    v = arow(ac, f, rec); put(ws3, r, v, fmt={4: '#,##0', 5: '#,##0', 6: '#,##0', 7: '#,##0', 8: '#,##0', 9: '#,##0', 10: '#,##0', 11: '#,##0'}); ws3.cell(r, 12, f'=IF(K{r}=0,"n/a",J{r}/K{r}-1)'); ws3.cell(r, 12).number_format = '+0%;-0%;0%'; ws3.cell(r, 12).border = BOX; ws3.cell(r, 12).font = BF
    ws3.row_dimensions[r].height = 48; r += 1
r += 1
ws3.cell(r, 1, 'Largest unadjusted accounts where the forecast sits above run rate (excluding NWC sub-accounts)').font = BB
r += 1
header(ws3, r, ['Account', 'Name', 'Class', 'Jun 26', 'Jul 26', 'Aug 26', 'Sep 26', 'Q3 avg', 'Oct-Dec fcst avg', 'FY27 fcst (MWh)', 'Q3 avg x 12 (MWh)', 'FY27 vs run rate', 'On file', 'Finding', 'Recommendation'])
r += 1
cand = [(x['f27'] - x['q3'] * 12, x) for x in rows.values() if x['ac'] not in adj and not x['ac'].startswith('NEW') and x['rc'] != 'RT10' and 'NATIONAL WATER' not in (x['name'] or '').upper() and x['q3'] > 0]
for d, x in sorted(cand, key=lambda t: -t[0])[:14]:
    v = arow(x['ac'], 'No adjustment on file. Forecast is above the Jul-Sep run rate: class storm-normalisation and macro drivers, not account evidence.' + (' Hotel account.' if ishotel(x) else ''), 'Review with KAM; apply B1/B2 (hotel timing, cap).')
    put(ws3, r, v, fmt={4: '#,##0', 5: '#,##0', 6: '#,##0', 7: '#,##0', 8: '#,##0', 9: '#,##0', 10: '#,##0', 11: '#,##0'}); ws3.cell(r, 12, f'=IF(K{r}=0,"n/a",J{r}/K{r}-1)'); ws3.cell(r, 12).number_format = '+0%;-0%;0%'; ws3.cell(r, 12).border = BOX; ws3.cell(r, 12).font = BF
    ws3.row_dimensions[r].height = 40; r += 1
r += 1
ws3.cell(r, 1, 'Pattern: across unadjusted key accounts (ex hotels) Q3-26 x 12 is 1,014 GWh; the engine has them at 1,049 GWh in 2027 (+34), all of it in H2 2027 (monthly 89-90 GWh against a run rate of 84.5). See B2.').alignment = WRAP
ws3.merge_cells(start_row=r, start_column=1, end_row=r, end_column=12); ws3.row_dimensions[r].height = 34
ws3.freeze_panes = 'C5'

# ------------------------------------------------------------------ 4. Timing
ws4 = sheet('Timing realignment', [26, 34, 30, 30, 40, 26, 40], 'Timing: KAM-stated dates against the platform, the deck and public reports',
            'Where the entered month differs from the KAM date, the reason is shown. "FY2026 lock" = moved on 28 Aug 2026 so FY2026 stayed tied to the 19 Aug submission.')
header(ws4, 4, ['Item', 'KAM-stated timing', 'Entered in platform', 'Deck (Sept 2026 update)', 'Public record', 'Recommended timing', 'Why'])
TM = [
 ('Alcoa / Jamalco', 'Self-generating (entered Aug 2026)', '-100% from Aug 2026, rolling', 'Lost in Aug; load not expected back', 'TG4 online early Aug; Century: runs entirely on self-generated power', 'No change', 'All sources agree.'),
 ('PAC Kingston Airport', '4 MW PV from 13 Jul; load sharing to Sep', '-80% Oct-Dec 2026 (moved back from Jan 2027 on 8 Sep)', 'Lost Oct', 'n/a', 'No change', 'Actuals fall Jul-Sep as stated; check Oct bill.'),
 ('MBJ Airports', '6 MW PV commissioned by end 2026', '-77.2% from Jan 2027', 'Decision already taken', '3 MW installed; further 3 MW in progress; no commissioning date; target 60% solar', 'Hold Jan 2027 only if KAM confirms date; size -45% to -50% unless storage is added', 'Public record does not support -77%.'),
 ('Sutherland Global', 'PV completed end Apr and May', '-50% Jul, -80% Aug', 'Planning stage (100 kW at three sites)', 'n/a', 'About -15% now', 'Billing shows no reduction through September.'),
 ('Clarendon Distillers', 'CHP units testing; defect by year end 2026', '-70% Dec 2026 (moved from Nov), -80% Jan-Feb 2027 (disruption), -85% Mar-Jun 2027', 'CHP installed but idle; LNG too costly', 'n/a', 'Defer; -25% until the CHP runs', 'KAM and deck conflict; KAM scale exceeds the account.'),
 ('West Meat Packers', '-70% by Q1 2027', '-70% from Jan 2027', 'Not in deck', 'n/a', 'Mar 2027', 'KAM said "by Q1": end of quarter, not the start.'),
 ('Windalco Ewarton', 'Turbines offline Nov-Dec for maintenance', '-50% Nov-Dec 2026 (month only)', 'Pilot: up to -70% (J$346M/yr)', 'Rusal sounding out buyers (Sep 2026)', 'Keep Nov-Dec; ask steady state; pilot as risk', 'Base depressed by July outage.'),
 ('Windalco Kirkvine', 'Not in platform as a separate entry', 'None found', 'Own generator primary from Oct (J$62M/yr)', 'Kirkvine refinery mothballed since 2009', 'Ask KAM which Kirkvine accounts and load', 'Deck item has no matching adjustment.'),
 ('Rainforest Seafood', 'Solar reinstated by Nov 2026', '-35% from Jan 2027 (FY2026 lock)', 'Not in deck', 'n/a', 'Nov 2026', 'Restore KAM date.'),
 ('Plantation Inn', 'AC units from Sep 2026', '+5% from Jan 2027 (FY2026 lock)', 'Not in deck', 'n/a', 'Oct 2026', 'Restore KAM date.'),
 ('Cocalapalm (hotel)', 'Winter-season occupancy +30% (entered Aug 2026)', '+30% from Jan 2027 (FY2026 lock)', 'Hotel recovery (see Hotels)', 'Winter season opened mid-Dec', 'Dec 2026', 'Season-driven, not August.'),
 ('Greater Portmore Health Centre', '+50% by Dec 2026', '+50% from Jan 2027 (FY2026 lock)', 'Not in deck', 'n/a', 'Dec 2026', 'Restore KAM date.'),
 ('Progressive Grocers, Harbour View', 'Store open for Christmas 2026', '+40% from Jan 2027', 'New load Dec', 'n/a', 'Dec 2026', 'Opens before the entered month.'),
 ('Progressive Grocers new customer', 'n/a', 'Two entries, 70 MWh, Dec 2027', 'Dec 2026 (deck)', 'n/a', 'One entry; confirm store and date', 'Duplicate and 12 months off the deck.'),
 ('Poly Pet', 'Two blow-mould machines by Nov 2026', '+15% Dec 2026 (moved back from Jan 2027 on 8 Sep)', 'Dec', 'n/a', 'No change', 'Consistent.'),
 ('PriceSmart', 'South Camp store Dec 2026 (deck); KAM entries Sep, Nov 2026 and Jan 2027', 'Three new customers: Sep 2026, Nov 2026, Jan 2027', 'South Camp Dec 2026', 'Montego Bay club opened 2 Oct 2026; Kingston expected 2027', 'Montego Bay Oct 2026; Kingston about mid-2027', 'Three entries is about 2.5 clubs.'),
 ('Hospitals: Western Children and Adolescent; Cornwall Regional', 'n/a', 'None', 'Dec 2026', '220-bed hospital "almost ready" (Jun 2026)', 'Dec 2026, size from KAM', 'Missing from the forecast.'),
 ('Caribbean Broilers egg farm', 'n/a', 'New customer Jan 2027 (132 MWh/mo)', 'Connected Sep 2026', 'n/a', 'Ask KAM', 'Low priority.'),
 ('National Water Commission boosters', 'Consumption +50-60% by Feb 2027', '+50-60% Feb 2027', 'NWC pipeline 18.5 GWh in 2027', 'n/a', 'No change', 'Consistent.'),
 ('University of Technology', '-50% by June 2027; -80% in 2028', '-50% from Jul 2027; -95% Jan-Feb 2028', 'Not in deck', 'n/a', 'No change', 'First entry is the month after the KAM date, which matches billing lag.'),
 ('Hotel reopenings', 'Per hotel KAM', 'None per hotel; smooth class ramp', 'Dec 2026: 6 hotels, 1,982 rooms; H1 2027: 8 hotels, 2,524; 2028: 1 hotel, 512', 'About 1,900 rooms Dec; Hyatt seven properties H1 2027; Royalton Negril and Blue Waters open', 'Per schedule, see Hotels sheet', 'Largest timing item by volume.'),
]
for i, t in enumerate(TM): put(ws4, 5 + i, list(t)); ws4.row_dimensions[5 + i].height = 52
ws4.freeze_panes = 'B5'

# ------------------------------------------------------------------ 5. Hotels
ws5 = sheet('Hotels', [34, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11], 'Hotel recovery: schedule-implied path against the engine',
            'GWh a month, hotel and accommodation accounts in RT20-RT70 (144 accounts). Blue cells are inputs. Shares follow the deck: 39.5% of closed rooms in Dec 2026, 50.3% spread over Jan-Jun 2027, 10.2% in 2028.')
ws5['A4'] = 'Pre-storm monthly level (Q3 2025 average)'; ws5['B4'] = round(q3_25_avg, 2)
ws5['A5'] = 'September 2026 actual'; ws5['B5'] = round(sep26, 2)
ws5['A6'] = 'Remaining gap a month'; ws5['B6'] = '=B4-B5'
ws5['A7'] = 'Share back Dec 2026'; ws5['B7'] = 0.395
ws5['A8'] = 'Share back across Jan-Jun 2027'; ws5['B8'] = 0.503
ws5['A9'] = 'Oct 2026 step (Royalton Negril and Blue Waters full month, Half Moon, Zoetry), GWh'; ws5['B9'] = 0.9
ws5['A10'] = 'Energy per reopened room vs pre-storm (occupancy still about 20% down)'; ws5['B10'] = 0.7
for rr in range(4, 11):
    ws5.cell(rr, 1).font = BB; ws5.cell(rr, 2).font = INP if rr != 6 else BF; ws5.cell(rr, 2).number_format = '0.00' if rr not in (7, 8, 10) else '0.0%'
    ws5.cell(rr, 1).alignment = WRAP
ws5.row_dimensions[9].height = 30; ws5.row_dimensions[10].height = 30
header(ws5, 12, ['', 'Oct 26', 'Nov 26', 'Dec 26', 'Jan 27', 'Feb 27', 'Mar 27', 'Apr 27', 'May 27', 'Jun 27', 'Jul 27', 'Aug 27', 'Sep 27', 'Oct 27', 'Nov 27', 'Dec 27'])
eng_path = hot26[9:12] + hot27
ws5.cell(13, 1, 'Engine (live run)').font = BB
for j, v in enumerate(eng_path): c = ws5.cell(13, 2 + j, round(v, 2)); c.font = INP; c.number_format = '0.0'
ws5.cell(14, 1, 'Schedule-implied step (GWh, before energy factor)').font = BB
for j in range(15):
    col = get_column_letter(2 + j)
    if j == 0: f = '=$B$9'
    elif j == 1: f = '=0'
    elif j == 2: f = '=$B$7*$B$6'
    elif 3 <= j <= 8: f = '=$B$8*$B$6/6'
    else: f = '=0'
    ws5.cell(14, 2 + j, f).number_format = '0.00'
ws5.cell(15, 1, 'Schedule-implied level').font = BB
for j in range(15):
    col = get_column_letter(2 + j); prev = f'$B$5' if j == 0 else f'{get_column_letter(1 + j)}15'
    ws5.cell(15, 2 + j, f'={prev}+{col}14*IF({col}14=$B$9,1,$B$10)' if False else f'={prev}+{col}14*$B$10').number_format = '0.0'
ws5.cell(16, 1, 'Schedule-implied less engine').font = BB
for j in range(15):
    col = get_column_letter(2 + j); ws5.cell(16, 2 + j, f'={col}15-{col}13').number_format = '+0.0;-0.0;0.0'
ws5.cell(18, 1, 'Q4 2026 difference (Oct-Dec), GWh').font = BB; ws5.cell(18, 2, '=SUM(B16:D16)').number_format = '+0.0;-0.0'
ws5.cell(19, 1, 'FY2027 difference (Jan-Dec), GWh').font = BB; ws5.cell(19, 2, '=SUM(E16:P16)').number_format = '+0.0;-0.0'
ws5.cell(20, 1, 'Engine FY2027 hotels, GWh').font = BB; ws5.cell(20, 2, '=SUM(E13:P13)').number_format = '0.0'
ws5.cell(21, 1, 'Q3 2025 x 12 (pre-storm run rate), GWh').font = BB; ws5.cell(21, 2, '=B4*12').number_format = '0.0'
for rr in range(18, 22): ws5.cell(rr, 2).font = BB; ws5.cell(rr, 2).fill = FILL_L
ws5.cell(23, 1, 'Public reopening reports used (search summaries, not full articles): Royalton Negril 25 Aug (573 rooms); Royalton Blue Waters 15 Sep (578); Half Moon phases Oct-Nov; Zoetry Oct (49); Sandals South Coast Nov (392); about 1,900 rooms in Dec (Bahia Principe 1 Dec, Sandals Montego Bay, Sandals Royal Caribbean, Iberostar Rose Hall); about 3,500 rooms in Q1 2027; Hyatt seven properties phased in H1 2027 (target Q1 2027, dates not announced). Room totals conflict between sources (6,000 of 15,000 reopened vs 70% recovered): treat as unresolved. At the default inputs the sheet gives the +1.7 GWh (Q4 2026) and +21.7 GWh (FY2027) used in checklist item B1.').alignment = WRAP
ws5.merge_cells('A23:P23'); ws5.row_dimensions[23].height = 78

# ------------------------------------------------------------------ 6. Evidence
ws6 = sheet('Evidence', [6, 22, 56, 70, 12], 'Evidence log', 'Public sources came from web searches on 3 Nov 2026. I read the search summaries, not the full articles; open the link before quoting externally.')
header(ws6, 4, ['Ref', 'Topic', 'Source', 'What it supports', 'Date'])
EV = [
 ('E1', 'Hotel rooms', 'https://jamaica-gleaner.com/article/news/20260914/ja-recovers-70-tourism-room-stock-hit-melissa-over-11000-more-expected-back', 'About 70% of affected room stock back; more than 11,000 rooms to return through 2027.', '14 Sep 2026'),
 ('E2', 'Hotel rooms', 'https://www.travelpulse.com/news/hotels-and-resorts/jamaica-resorts-update-reopen-timelines-for-sandals-hyatt-princess-and-more', 'Reopening timelines for Sandals, Hyatt, Princess and others.', '2026'),
 ('E3', 'Hotel rooms', 'https://www.travelpulse.com/news/hotels-and-resorts/royalton-negril-reopens-as-jamaica-tourism-recovery-gains-steam', 'Royalton Negril reopened 25 Aug with 573 rooms; Blue Waters 15 Sep.', 'Aug 2026'),
 ('E4', 'Hyatt delay', 'https://www.caribjournal.com/2026/04/12/jamaica-hyatt-all-inclusive-resorts-delays/', 'Seven Hyatt resorts delayed to Q1 2027; per-property dates to follow.', '12 Apr 2026'),
 ('E5', 'Arrivals', 'https://www.caribjournal.com/2026/07/13/jamaica-tourism-arrivals-down-27/', 'Stayover arrivals -27.5% in Q1 2026.', '13 Jul 2026'),
 ('E5b', 'Arrivals', 'https://www.riotimesonline.com/jamaica-arrivals-fall-montego-bay-hurricane-melissa-2026/', 'Sangster international arrivals -23.65% in Aug 2026, attributed to closed hotels.', '2026'),
 ('E6', 'Macro', 'https://www.jamaicaobserver.com/2026/08/19/recovery-ahead-schedule/', 'PIOJ: Jul-Sep quarter -0.5% to -1.5%; FY2026/27 growth 1-3%; growth expected from Q2 2027.', '19 Aug 2026'),
 ('E7', 'Macro', 'https://boj.org.jm/wp-content/uploads/2026/02/QMPR-Press-Presentation-24-Feb-2026-web.pdf', 'BOJ: full recovery within 2-3 years; FY2026/27 growth 1-3%.', 'Feb 2026'),
 ('E8', 'MBJ solar', 'https://jis.gov.jm/features/mbj-invests-in-solar-project/', '3 MW installed, a further 3 MW in progress, airport on track to be 60% solar. No commissioning date.', 'Dec 2024'),
 ('E8b', 'MBJ solar', 'https://jamaica-gleaner.com/article/news/20260703/mbj-presses-ahead-airport-expansion-despite-passenger-slump', 'July 2026: more solar and battery storage being installed; passenger slump.', '3 Jul 2026'),
 ('E9', 'Jamalco', 'https://jamaica-gleaner.com/article/business/20260809/jamalco-unplugs-grid-power-turbine-set-save-us28m-year', 'TG4 online early August; refinery fully self-generated.', '9 Aug 2026'),
 ('E10', 'Windalco', 'https://www.jamaicaobserver.com/2026/09/25/govt-queries-windalco-sale/', 'Rusal approaching buyers for Windalco; early stage.', '25 Sep 2026'),
 ('E11', 'PriceSmart', 'https://jamaica-gleaner.com/article/news/20261002/pricesmart-opens-mobay-club-us28m-investment', 'Montego Bay club opened; Kingston (South Camp Road) expected next year.', '2 Oct 2026'),
 ('E12', 'Hospital', 'https://jamaica-gleaner.com/article/news/20260620/tufton-promises-better-healthcare-around-corner-jamaicans-north-coast', 'Western Child and Adolescent Hospital (220 beds) almost ready.', '20 Jun 2026'),
 ('E13', 'Solar policy', 'https://jamaica-gleaner.com/article/business/20260322/hurricane-melissa-damage-prompts-rethink-solar-reliance-220mw-auction', 'Post-Melissa solar planning and the 220 MW auction. The 100 MW net billing programme and Dec 2026 online platform come from a JIS report seen only in a search summary (URL not retrieved).', 'Mar-May 2026'),
 ('E14', 'Demand and weather', 'https://www.jamaicaobserver.com/2026/07/08/heat-sends-power-demand-2026-high/', 'System demand hit its 2026 high on 1 July on heat.', '8 Jul 2026'),
 ('E14b', 'Weather', 'https://wmo.int/node/39136', 'El Nino strengthening Nov 2026-Jan 2027; Met Service expects it to peak in December and persist into 2027 (warmer, drier).', 'Oct 2026'),
 ('E15', 'Cement', 'https://jamaica-gleaner.com/article/business/20260730/cement-production-hits-record-2nd-quarter-profit-surges-fivefold', 'Record Q2 2026 volumes on reconstruction demand; supports the Caribbean Cement forecast.', '30 Jul 2026'),
 ('D1', 'Internal', 'Client Relations and Commercial Update (Sep2026)_v4.pptx', 'Hotel schedule (slide 7), planning-stage defections and tracker of 1 Oct (slide 5), new load and pipeline (slide 6).', 'Oct 2026'),
 ('D2', 'Internal', 'jps_macro_assumptions, driver_type = seasonality_residential, year 2027', 'Source note: derived from 2025 monthly kWh by class and bucket. Nov 2025 buckets -11% to -42%.', 'DB 3 Nov 2026'),
 ('D3', 'Internal', 'JPS_Sales_Platform_v1.html, _dfcDriverPcts()', '2026 residential seasonality and storm normalisation gated to years after the budget year; normalisation keyed by rate class.', 'Code'),
 ('D4', 'Internal', 'jps_operational_adjustments_current (187 rows); jps_forecast_new_customers (13 rows)', 'KAM text and dates; notes on the 28 Aug FY2026 lock moves.', 'DB 3 Nov 2026'),
]
for i, e in enumerate(EV): put(ws6, 5 + i, list(e)); ws6.row_dimensions[5 + i].height = 34

# ------------------------------------------------------------------ 7. Method
ws7 = sheet('Method and caveats', [110], 'Method and caveats')
NT = [
 'Held forecast = financials LE (FY2026 3,299.7; FY2027 3,439.5 GWh billed). It is the baseline for every impact in the checklist. Nothing here changes the platform or the held figures.',
 'Live engine = Driver Forecast run of 26 Oct 2026 with the roll-forward change, actuals to September 2026. I did not re-run it on 3 Nov; the operational adjustments table is unchanged since (187 rows) and no October actuals exist yet.',
 'Run rate = Jul-Sep 2026 average. It is distorted for accounts with one-offs (Alcoa July 9 GWh, Windalco July outage, Caribbean Broilers September billing timing). Those are flagged on the Account review sheet.',
 'Q4 2026 seasonality: the 2026 budget monthly shape applied to September (A), to the August-September average (B) and through the Q3 actual/budget ratio (C). The three methods bracket FY2026 at 3,275-3,290. The budget shape itself has quirks (September dips against August), which is why three methods are shown. Q4 2025 cannot be used: Hurricane Melissa struck on 28 October 2025.',
 'Hotels = accounts whose industry contains hotel, motel, resort or accommodation (144 in RT20-RT70). The deck says 100 GWh a year is closed; the billing gap to pre-storm is about 56 GWh a year, so the Hotels sheet uses the billing gap. The reopened-room energy factor (default 70%) is a judgement: arrivals are still about 20% down and hotels have a large fixed load.',
 'Impacts are central estimates with a range column. B1 and B2 are linked: B2 removes recovery from accounts that were not storm-affected, B1 puts it where reopenings are scheduled. Accepting only one changes the FY2027 result by about 20 GWh.',
 'Not quantified: new hospital load (size unknown), FLOW cell sites, NWC solar, net billing expansion, El Nino. The 10 MW = 14-15 GWh rule of thumb assumes about 1,450 kWh per kW a year.',
 'Public-domain items are from search summaries. Several conflict (hotel room counts, recovery percentages, Jamalco start-up date). Confidence is labelled in the checklist: verified = checked against the database, code or deck; inferred = derived from data and public reports; assumed = my judgement.',
 'Customer billing data stays inside this workbook. It contains account names and volumes: keep it internal.',
]
for i, t in enumerate(NT):
    c = ws7.cell(3 + i, 1, '%d. %s' % (i + 1, t)); c.alignment = WRAP; c.font = BF; ws7.row_dimensions[3 + i].height = 48

from openpyxl.worksheet.properties import PageSetupProperties
for _ws in wb.worksheets:
    _ws.page_setup.orientation = 'landscape'; _ws.page_setup.fitToWidth = 1; _ws.page_setup.fitToHeight = 0
    _ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
wb.move_sheet('Decision checklist', offset=-wb.index(wb['Decision checklist']))
wb.save(OUT); print('saved', OUT)
