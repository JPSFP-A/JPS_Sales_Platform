# -*- coding: utf-8 -*-
# Alcoa (100185-607213) RT70 — 3-year revenue projection, sensitivity model.
# History pulled live from jps_actuals (Jan 2025-Jul 2026, 19 months) via Supabase
# MCP earlier in-session; hardcoded here as the model's source data (blue inputs,
# sourced). Multiplier (48000x) and current billed kVA (21,025.01) pulled from the
# raw July 2026 Billing Details Report (multilpier / kva_billed_consump columns) --
# jps_actuals' kwh/revenue already have the multiplier applied; the Drivers-tab
# multiplier is an ADDITIONAL override for scenario testing, not a re-application.
#
# IMPORTANT: jps_actuals' 5 named components (demand/fuel/energy/ipp/customer
# charge) only explain ~39% of this account's actual billed revenue -- the
# remaining ~61% is a large, $/kWh-consistent residual (avg $26.01/kWh vs.
# revenue/kWh swings of $23-32/kWh across all 19 months) not broken out in the
# DB schema (likely base energy tariff + Tariff_Adj/FEX/EEIF/rint from the raw
# billing file, which HAS those columns but jps_actuals doesn't). Modeled here
# as its own tracked "Other/Base Tariff" component so Total Revenue reconciles
# to real historical actuals instead of silently understating it by ~2/3.
#
# Demand/Energy/IPP/Fuel/Other are all modeled as $/kWh rates derived from
# history and escalated by driver %, since no per-month kVA history is
# available for this specific account (jps_demand_actuals is rate-class-level,
# not per-account) -- documented as an assumption on the Drivers tab.
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import LineChart, Reference

FONT = 'Arial'
BLUE = Font(name=FONT, color='0000FF', size=10)
BLACK = Font(name=FONT, color='000000', size=10)
GREEN = Font(name=FONT, color='008000', size=10)
BOLD = Font(name=FONT, color='000000', size=10, bold=True)
HDR = Font(name=FONT, color='FFFFFF', size=10, bold=True)
TITLE = Font(name=FONT, color='FFFFFF', size=13, bold=True)
YELLOW = PatternFill('solid', start_color='FFFF00')
NAVY = PatternFill('solid', start_color='0C3547')
GREY = PatternFill('solid', start_color='F0F4F8')
THIN = Side(style='thin', color='CBD5E1')
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
MONEY = '$#,##0;($#,##0);"-"'
KWHFMT = '#,##0;(#,##0);"-"'
PCT = '0.0%;(0.0%);"-"'
RATE = '$#,##0.0000;($#,##0.0000);"-"'

wb = Workbook()

# ============================================================ HISTORY ============
hs = wb.active
hs.title = 'History'
hs.sheet_view.showGridLines = False
for c, w in zip('ABCDEFGHIJKLMNO', [6, 10, 12, 14, 15, 13, 13, 13, 14, 11, 15, 15, 15, 15, 15]):
    hs.column_dimensions[c].width = w
hs['A1'] = 'ALCOA MINS OF JA LTD — RT70 — HISTORICAL ACTUALS'
hs['A1'].font = TITLE
hs.merge_cells('A1:O1')
hs['A1'].fill = NAVY
hs['A1'].alignment = Alignment(vertical='center', indent=1)
hs.row_dimensions[1].height = 22
hs['A2'] = 'Account 100185-607213 · Source: jps_actuals (Supabase bhrswnbenkvflpdjhfpa), pulled 2026-08-11 · GCT-exempt (0 in all 19 months) · Fuel $0 in all 19 months'
hs['A2'].font = Font(name=FONT, italic=True, size=9, color='6B7A99')
hs.merge_cells('A2:O2')

HDRS = ['Year', 'Month#', 'Period', 'kWh', 'Revenue $', 'Demand $', 'Fuel $', 'Energy $', 'IPP $',
        'Cust Chg $', 'GCT $', 'Demand $/kWh', 'Energy $/kWh', 'Other/Base $', 'Other $/kWh']
r0 = 4
for j, h in enumerate(HDRS):
    c = hs.cell(r0, j + 1, h)
    c.font = HDR
    c.fill = NAVY
    c.alignment = Alignment(horizontal='center', wrap_text=True)
    c.border = BORDER
hs.row_dimensions[r0].height = 28

# (year, month, kwh, revenue, demand, fuel, energy, ipp, custchg, gct) — None = null in DB
ROWS = [
    (2025, 1, 7283162, 266092728, 47668312, 0, 35614660, 6356502, 9067, 0),
    (2025, 2, 7558914, 338431883, 98780063, 0, 36963087, 15370340, 9067, 0),
    (2025, 3, 9220246, 347997726, 62116062, 0, 45087002, 6840302, 9067, 0),
    (2025, 4, 6776457, 306339672, 99821400, 0, 33136874, 14980429, 9067, 0),
    (2025, 5, 6360004, 304760808, 96646281, 0, 31100421, 12528312, 9067, 0),
    (2025, 6, 6112234, 254803373, 58048083, 0, 29888823, 7104539, 9067, 0),
    (2025, 7, 7807153, 285797656, 56361244, 0, 38176979, 9708956, 9067, 0),
    (2025, 8, 6836301, 257804420, 57679201, 0, 33429511, 9124644, 9066, 0),
    (2025, 9, 6921867, 273820535, 55312236, 0, 33847930, 7948863, 9067, 0),
    (2025, 10, 7047477, 322020733, 84597439, 0, 34462161, 11382804, 9067, 0),
    (2025, 11, 3374336, 201961923, 81023034, 0, 16500501, 11610645, 9067, 0),
    (2025, 12, 1864266, 92527465, 26065364, 0, 9116260, 2813669, 9067, 0),
    (2026, 1, 3618112, 154329498, 36146527, 0, 17692567, 7872014, 9067, 0),
    (2026, 2, 6153753, 252683564, 38373999, 0, 30091855, 7675975, 9067, 0),
    (2026, 3, 8480800, 401358542, 75273321, 0, 41471114, 14501754, 9067, 0),
    (2026, 4, 8347849, 313688892, 51555757, 0, 40820984, 4411433, 9067, 0),
    (2026, 5, 9056910, 344070135, 50765228, 0, 44288292, 6643840, 9067, None),
    (2026, 6, 8590490, 388387586, 99821400, 0, 42007496, 15274424, 9067, 0),
    (2026, 7, 9004421, 347336115, 59964170, 0, 44031617, 9457813, 9067, None),
]
MNAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
r = r0 + 1
first_data_row = r
for (y, m, kwh, rev, dem, fuel, en, ipp, cc, gct) in ROWS:
    vals = [y, m, MNAMES[m - 1] + "'" + str(y)[2:], kwh, rev, dem, fuel, en, ipp, cc, gct]
    for j, v in enumerate(vals):
        cell = hs.cell(r, j + 1, v)
        cell.font = BLUE
        cell.border = BORDER
        if j == 3:
            cell.number_format = KWHFMT
        elif j >= 4:
            cell.number_format = MONEY
        if j == 1:
            cell.alignment = Alignment(horizontal='center')
    dcell = hs.cell(r, 12)
    dcell.value = f'=IF(OR(F{r}="",D{r}=0),"",F{r}/D{r})'
    dcell.font = BLACK; dcell.number_format = RATE; dcell.border = BORDER
    ecell = hs.cell(r, 13)
    ecell.value = f'=IF(OR(H{r}="",D{r}=0),"",H{r}/D{r})'
    ecell.font = BLACK; ecell.number_format = RATE; ecell.border = BORDER
    # Other/Base $ = Revenue - (Demand+Fuel+Energy+IPP+CustChg+GCT). Blank only when the
    # 5 CORE components are missing (the Jul-2025 pre-migration gap) — GCT null is treated
    # as 0 (matches every other month; this account is GCT-exempt), not as missing data,
    # so a lone-null GCT month (May/Jul-2026) doesn't wrongly blank out Other too.
    ocell = hs.cell(r, 14)
    ocell.value = f'=IF(OR(F{r}="",G{r}="",H{r}="",I{r}="",J{r}=""),"",E{r}-F{r}-G{r}-H{r}-I{r}-J{r}-IF(K{r}="",0,K{r}))'
    ocell.font = BLACK; ocell.number_format = MONEY; ocell.border = BORDER
    oratecell = hs.cell(r, 15)
    oratecell.value = f'=IF(OR(N{r}="",D{r}=0),"",N{r}/D{r})'
    oratecell.font = BLACK; oratecell.number_format = RATE; oratecell.border = BORDER
    r += 1
last_data_row = r - 1
hs.cell(r, 3, 'AVERAGE').font = BOLD
for col in range(4, 16):
    cl = get_column_letter(col)
    fcell = hs.cell(r, col)
    fcell.value = f'=AVERAGE({cl}{first_data_row}:{cl}{last_data_row})'
    fcell.font = BOLD
    fcell.number_format = KWHFMT if col == 4 else (RATE if col in (12, 13, 15) else MONEY)
    fcell.border = BORDER
hs.freeze_panes = 'A5'
hs['A' + str(r + 2)] = ('Note: Jul/Aug-2025 corrected 2026-08-11. Jul-2025 (7,807,153 kWh / $285,797,656) was a normal, correctly-billed month, including its component breakout (Demand $56,361,244 / Energy $38,176,979 / IPP $9,708,956 / Cust Chg $9,067) -- '
                         'the raw file actually had TWO Jul rows for this account: the real bill (comma-formatted Cust_Code, cust_billed=1) and an unrelated all-zero row (clean code, cust_billed=0); jps_actuals had picked up kWh/revenue from the real row but lost the component detail to the same comma-parsing gap. '
                         'The Aug-2025 raw extract separately carried BOTH a positive 14,643,454 kWh / $543,602,076 charge AND an exact reversal of the Jul bill (-7,807,153 kWh / -$285,797,656, comma-formatted Cust_Code) -- '
                         'the reversal was silently dropped by the same bug, so jps_actuals kept Aug\'s raw positive figure un-netted, double-counting Jul\'s consumption on top of the real Jul bill. '
                         'Aug-2025 is now the net of both rows: 6,836,301 kWh / $257,804,420 (demand/energy/IPP/customer-charge components netted the same way; the customer-charge net of 9,066 vs. every other month\'s ~9,067 corroborates this reading). '
                         '"Other/Base $" = Revenue - (Demand+Fuel+Energy+IPP+CustChg+GCT) — the 5 named components explain only ~39% of actual revenue; the residual is remarkably $/kWh-consistent ($23-32/kWh across all months), '
                         'consistent with a base energy tariff + Tariff_Adj/FEX/EEIF/rint that the raw billing file carries but jps_actuals does not break out separately.')
hs['A' + str(r + 2)].font = Font(name=FONT, italic=True, size=8.5, color='B87800')
hs['A' + str(r + 2)].alignment = Alignment(wrap_text=True, vertical='top')
hs.merge_cells(f'A{r+2}:O{r+2}')
hs.row_dimensions[r + 2].height = 100

AVG_ROW = r

# ============================================================ SEASONALITY ========
ss = wb.create_sheet('Seasonality')
ss.sheet_view.showGridLines = False
for c, w in zip('ABCDE', [6, 10, 16, 18, 12]):
    ss.column_dimensions[c].width = w
ss['A1'] = 'MONTHLY SEASONALITY INDEX (derived from History, all available years per calendar month)'
ss['A1'].font = TITLE
ss.merge_cells('A1:E1')
ss['A1'].fill = NAVY
ss.row_dimensions[1].height = 22
hdrs2 = ['Month#', 'Month', 'Avg Historical kWh', 'Avg Historical Revenue $', 'Seasonality Index']
for j, h in enumerate(hdrs2):
    c = ss.cell(3, j + 1, h); c.font = HDR; c.fill = NAVY; c.border = BORDER
    c.alignment = Alignment(horizontal='center', wrap_text=True)
ss.row_dimensions[3].height = 28
for i in range(12):
    rr = 4 + i
    ss.cell(rr, 1, i + 1).font = BLACK
    ss.cell(rr, 1).alignment = Alignment(horizontal='center')
    ss.cell(rr, 2, MNAMES[i]).font = BLACK
    kc = ss.cell(rr, 3)
    kc.value = f'=AVERAGEIF(History!$B${first_data_row}:$B${last_data_row},A{rr},History!$D${first_data_row}:$D${last_data_row})'
    kc.font = GREEN; kc.number_format = KWHFMT
    rc = ss.cell(rr, 4)
    rc.value = f'=AVERAGEIF(History!$B${first_data_row}:$B${last_data_row},A{rr},History!$E${first_data_row}:$E${last_data_row})'
    rc.font = GREEN; rc.number_format = MONEY
    ic = ss.cell(rr, 5)
    ic.value = f'=C{rr}/AVERAGE($C$4:$C$15)'
    ic.font = BLACK; ic.number_format = '0.00"x"'
    for col in range(1, 6):
        ss.cell(rr, col).border = BORDER
ss.cell(16, 2, 'AVERAGE (=1.00x baseline)').font = BOLD
ss.cell(16, 3).value = '=AVERAGE(C4:C15)'; ss.cell(16, 3).font = BOLD; ss.cell(16, 3).number_format = KWHFMT
ss.cell(16, 4).value = '=AVERAGE(D4:D15)'; ss.cell(16, 4).font = BOLD; ss.cell(16, 4).number_format = MONEY
ss.cell(16, 5).value = '=AVERAGE(E4:E15)'; ss.cell(16, 5).font = BOLD; ss.cell(16, 5).number_format = '0.00"x"'
for col in range(1, 6):
    ss.cell(16, col).border = BORDER
ss.freeze_panes = 'A4'

# ============================================================ DRIVERS ============
ds = wb.create_sheet('Drivers')
ds.sheet_view.showGridLines = False
for c, w in zip('ABCDE', [42, 15, 42, 15, 40]):
    ds.column_dimensions[c].width = w
ds['A1'] = 'DRIVER / SENSITIVITY PANEL — toggle any blue cell to flex the projection'
ds['A1'].font = TITLE
ds.merge_cells('A1:E1')
ds['A1'].fill = NAVY
ds.row_dimensions[1].height = 22

def section(row, text):
    ds.cell(row, 1, text).font = Font(name=FONT, bold=True, size=10.5, color='0C3547')
    ds.merge_cells(f'A{row}:E{row}')
    for col in range(1, 6):
        ds.cell(row, col).fill = GREY

def drow(row, label, value, fmt, note='', input_cell=True):
    ds.cell(row, 1, label).font = BLACK
    c = ds.cell(row, 2, value)
    c.font = BLUE if input_cell else BLACK
    c.number_format = fmt
    c.fill = YELLOW if input_cell else PatternFill()
    c.border = BORDER
    ds.cell(row, 1).border = BORDER
    if note:
        ds.cell(row, 3, note).font = Font(name=FONT, italic=True, size=8.5, color='6B7A99')
        ds.merge_cells(f'C{row}:E{row}')

section(3, 'VOLUME SCENARIO')
drow(4, 'Volume adjustment vs. seasonal baseline (%)', -0.50, PCT, 'User scenario: 50% volume reduction, applied flat across all 36 projected months')
drow(5, 'Apply seasonality? (1 = Yes, 0 = No / use flat monthly average)', 1, '0', 'Set to 0 to test a flat (non-seasonal) run-rate instead')
drow(6, 'Meter multiplier override (x)', 1.00, '0.00"x"', 'jps_actuals kWh already reflects the current 48,000x CT/PT multiplier (see reference below) — this is an ADDITIONAL scenario multiplier on top, 1.00x = no change')

section(8, 'RATE ESCALATION (% per year, compounding from Year 1)')
drow(9, 'Energy rate escalation (%/yr)', 0.00, PCT)
drow(10, 'Demand rate escalation (%/yr)', 0.00, PCT, 'Demand modeled as $/kWh — no per-month kVA history available for this account (see modeling note below)')
drow(11, 'IPP rate escalation (%/yr)', 0.00, PCT)
drow(12, 'Other/base tariff rate escalation (%/yr)', 0.00, PCT, 'Covers the ~61% of revenue not broken into the 4 named components — see modeling note below')
drow(13, 'Fuel rate escalation (%/yr)', 0.00, PCT, 'Fuel has been $0 in all 19 historical months — escalating 0% stays 0. Use the override below to test a hypothetical fuel charge.')
drow(14, 'Fuel rate override ($/kWh, replaces history if >0)', 0.00, RATE)
drow(15, 'Customer charge escalation (%/yr)', 0.00, PCT, 'Applied to the flat monthly customer charge, not volume-driven')

section(17, 'OTHER')
drow(18, 'GCT rate applied (%)', 0.00, PCT, 'Account has been GCT-exempt in all 19 historical months')
drow(19, 'Projection start (Year 1, Month 1)', '2026-08', '@', 'Format YYYY-MM — first projected month')

section(21, 'REFERENCE (informational, not scenario inputs)')
drow(22, 'Current meter multiplier', 48000, '#,##0"x"', 'Source: Billing Details Report_Jul 2026.xls, multilpier field, account 100185-607213', input_cell=False)
ds.cell(22, 2).font = BLACK
drow(23, 'Current billed demand (kVA, Jul-2026)', 21025.01, '#,##0.00', 'Source: Billing Details Report_Jul 2026.xls, kva_billed_consump field', input_cell=False)
ds.cell(23, 2).font = BLACK

section(25, 'HISTORICAL BASELINE UNIT RATES (computed from History tab averages — feed the projection)')
def rate_row(row, label, num_col, den_col='D'):
    ds.cell(row, 1, label).font = BLACK
    ds.cell(row, 2).value = f'=History!{num_col}{AVG_ROW}/History!{den_col}{AVG_ROW}'
    ds.cell(row, 2).font = GREEN; ds.cell(row, 2).number_format = RATE
    ds.cell(row, 2).border = BORDER; ds.cell(row, 1).border = BORDER

rate_row(26, 'Avg Demand $/kWh (History col F/D)', 'F')
rate_row(27, 'Avg Energy $/kWh (History col H/D)', 'H')
rate_row(28, 'Avg IPP $/kWh (History col I/D)', 'I')
rate_row(29, 'Avg Other/Base $/kWh (History col N/D)', 'N')
rate_row(30, 'Avg Fuel $/kWh (History col G/D)', 'G')
ds.cell(31, 1, 'Avg Customer Charge $/mo (History col J avg)').font = BLACK
ds.cell(31, 2).value = f'=History!J{AVG_ROW}'
ds.cell(31, 2).font = GREEN; ds.cell(31, 2).number_format = MONEY
ds.cell(31, 2).border = BORDER; ds.cell(31, 1).border = BORDER

ds['A33'] = ('MODELING NOTES: (1) Demand is billed on peak kVA in reality; per-month kVA history isn\'t available for this single account '
             '(jps_demand_actuals is rate-class-level, not account-level), so Demand $ is modeled as a $/kWh rate consistent with history — flex the Demand escalation driver to stress-test. '
             '(2) jps_actuals\' Demand+Fuel+Energy+IPP+Cust Charge columns explain only ~39% of this account\'s actual historical revenue; the remaining ~61% ("Other/Base Tariff") is a real, '
             'consistent $/kWh charge (see History tab note) not broken out in the DB schema — tracked here as its own component so the projection reconciles to actual revenue.')
ds['A33'].font = Font(name=FONT, italic=True, size=8.5, color='B87800')
ds.merge_cells('A33:E33')
ds.row_dimensions[33].height = 44
for rr in (33,):
    ds.cell(rr, 1).alignment = Alignment(wrap_text=True, vertical='top')

# ============================================================ PROJECTION =========
ps = wb.create_sheet('Projection')
ps.sheet_view.showGridLines = False
PW = [6, 6, 10, 12, 15, 14, 15, 13, 13, 13, 13, 15, 14, 15, 13, 16]
for c, w in zip('ABCDEFGHIJKLMNOP', PW):
    ps.column_dimensions[c].width = w
ps['A1'] = '3-YEAR PROJECTION — ALCOA RT70 (36 months, seasonality + volume/rate drivers)'
ps['A1'].font = TITLE
ps.merge_cells('A1:P1')
ps['A1'].fill = NAVY
ps.row_dimensions[1].height = 22
hdrs3 = ['Per#', 'FY', 'Month', 'Cal Mo#', 'Seasonal kWh', 'Volume-Adj kWh', 'Final kWh\n(x multiplier)',
         'Demand $', 'Energy $', 'IPP $', 'Fuel $', 'Other/Base $', 'Cust Chg $', 'Subtotal $', 'GCT $', 'Total Revenue $']
for j, h in enumerate(hdrs3):
    c = ps.cell(3, j + 1, h); c.font = HDR; c.fill = NAVY; c.border = BORDER
    c.alignment = Alignment(horizontal='center', wrap_text=True)
ps.row_dimensions[3].height = 30

pr0 = 4
for i in range(36):
    rr = pr0 + i
    fy = i // 12 + 1
    ps.cell(rr, 1, i + 1).font = BLACK
    ps.cell(rr, 2, f'FY{fy}').font = BLACK
    ps.cell(rr, 2).alignment = Alignment(horizontal='center')
    ps.cell(rr, 3).value = f'=EDATE(DATEVALUE(Drivers!$B$19&"-01"),{i})'
    ps.cell(rr, 3).number_format = 'mmm-yy'
    ps.cell(rr, 3).font = BLACK
    ps.cell(rr, 4).value = f'=MONTH(C{rr})'
    ps.cell(rr, 4).font = BLACK
    ps.cell(rr, 4).alignment = Alignment(horizontal='center')
    ps.cell(rr, 5).value = f'=IF(Drivers!$B$5=1,INDEX(Seasonality!$C$4:$C$15,MATCH(D{rr},Seasonality!$A$4:$A$15,0)),Seasonality!$C$16)'
    ps.cell(rr, 5).font = GREEN
    ps.cell(rr, 5).number_format = KWHFMT
    ps.cell(rr, 6).value = f'=E{rr}*(1+Drivers!$B$4)'
    ps.cell(rr, 6).font = BLACK
    ps.cell(rr, 6).number_format = KWHFMT
    ps.cell(rr, 7).value = f'=F{rr}*Drivers!$B$6'
    ps.cell(rr, 7).font = BLACK
    ps.cell(rr, 7).number_format = KWHFMT
    yexp = f'(ROUNDUP(A{rr}/12,0)-1)'
    ps.cell(rr, 8).value = f'=$G{rr}*Drivers!$B$26*(1+Drivers!$B$10)^{yexp}'
    ps.cell(rr, 8).font = BLACK; ps.cell(rr, 8).number_format = MONEY
    ps.cell(rr, 9).value = f'=$G{rr}*Drivers!$B$27*(1+Drivers!$B$9)^{yexp}'
    ps.cell(rr, 9).font = BLACK; ps.cell(rr, 9).number_format = MONEY
    ps.cell(rr, 10).value = f'=$G{rr}*Drivers!$B$28*(1+Drivers!$B$11)^{yexp}'
    ps.cell(rr, 10).font = BLACK; ps.cell(rr, 10).number_format = MONEY
    ps.cell(rr, 11).value = f'=$G{rr}*IF(Drivers!$B$14>0,Drivers!$B$14,Drivers!$B$30)*(1+Drivers!$B$13)^{yexp}'
    ps.cell(rr, 11).font = BLACK; ps.cell(rr, 11).number_format = MONEY
    ps.cell(rr, 12).value = f'=$G{rr}*Drivers!$B$29*(1+Drivers!$B$12)^{yexp}'
    ps.cell(rr, 12).font = BLACK; ps.cell(rr, 12).number_format = MONEY
    ps.cell(rr, 13).value = f'=Drivers!$B$31*(1+Drivers!$B$15)^{yexp}'
    ps.cell(rr, 13).font = BLACK; ps.cell(rr, 13).number_format = MONEY
    ps.cell(rr, 14).value = f'=SUM(H{rr}:M{rr})'
    ps.cell(rr, 14).font = BOLD; ps.cell(rr, 14).number_format = MONEY
    ps.cell(rr, 15).value = f'=N{rr}*Drivers!$B$18'
    ps.cell(rr, 15).font = BLACK; ps.cell(rr, 15).number_format = MONEY
    ps.cell(rr, 16).value = f'=N{rr}+O{rr}'
    ps.cell(rr, 16).font = BOLD; ps.cell(rr, 16).number_format = MONEY
    for col in range(1, 17):
        ps.cell(rr, col).border = BORDER
    if fy % 2 == 0:
        band = PatternFill('solid', start_color='F8FAFC')
        for col in range(1, 17):
            ps.cell(rr, col).fill = band
ps.freeze_panes = 'C4'
last_proj_row = pr0 + 35

# ============================================================ SUMMARY ============
sm = wb.create_sheet('Summary')
sm.sheet_view.showGridLines = False
for c, w in zip('ABCDEFGHIJ', [28, 14, 14, 14, 14, 14, 14, 14, 12, 16]):
    sm.column_dimensions[c].width = w
sm['A1'] = 'SUMMARY — ANNUAL ROLLUP & TTM COMPARISON'
sm['A1'].font = TITLE
sm.merge_cells('A1:J1')
sm['A1'].fill = NAVY
sm.row_dimensions[1].height = 22
sm['A2'] = 'Alcoa Mins Of Ja Ltd · Account 100185-607213 · RT70 · Scenario: see Drivers tab'
sm['A2'].font = Font(name=FONT, italic=True, size=9, color='6B7A99')
sm.merge_cells('A2:J2')

hdrs4 = ['', 'kWh', 'Demand $', 'Energy $', 'IPP $', 'Fuel $', 'Other/Base $', 'Cust Chg $', 'GCT $', 'Total Revenue $']
for j, h in enumerate(hdrs4):
    c = sm.cell(4, j + 1, h); c.font = HDR; c.fill = NAVY; c.border = BORDER
    c.alignment = Alignment(horizontal='center', wrap_text=True)
sm.row_dimensions[4].height = 26

ttm_start = first_data_row + 7  # Aug-25 (row 8 offset from first_data_row=Jan-25)
sm.cell(5, 1, 'TTM Actual (Aug-2025 to Jul-2026)').font = BOLD
sm.cell(5, 2).value = f'=SUM(History!D{ttm_start}:D{last_data_row})'
sm.cell(5, 3).value = f'=SUM(History!F{ttm_start}:F{last_data_row})'
sm.cell(5, 4).value = f'=SUM(History!H{ttm_start}:H{last_data_row})'
sm.cell(5, 5).value = f'=SUM(History!I{ttm_start}:I{last_data_row})'
sm.cell(5, 6).value = f'=SUM(History!G{ttm_start}:G{last_data_row})'
sm.cell(5, 7).value = f'=SUM(History!N{ttm_start}:N{last_data_row})'
sm.cell(5, 8).value = f'=SUM(History!J{ttm_start}:J{last_data_row})'
sm.cell(5, 9).value = f'=SUM(History!K{ttm_start}:K{last_data_row})'
sm.cell(5, 10).value = f'=SUM(History!E{ttm_start}:E{last_data_row})'
for col in range(2, 11):
    sm.cell(5, col).font = GREEN
    sm.cell(5, col).number_format = KWHFMT if col == 2 else MONEY

fy_rows = {1: (pr0, pr0 + 11), 2: (pr0 + 12, pr0 + 23), 3: (pr0 + 24, pr0 + 35)}
for k, fy in enumerate([1, 2, 3]):
    rr = 6 + k
    a, b = fy_rows[fy]
    sm.cell(rr, 1, f'Projected FY{fy} ({("Aug-26 to Jul-27","Aug-27 to Jul-28","Aug-28 to Jul-29")[k]})').font = BOLD
    sm.cell(rr, 2).value = f'=SUM(Projection!G{a}:G{b})'
    sm.cell(rr, 3).value = f'=SUM(Projection!H{a}:H{b})'
    sm.cell(rr, 4).value = f'=SUM(Projection!I{a}:I{b})'
    sm.cell(rr, 5).value = f'=SUM(Projection!J{a}:J{b})'
    sm.cell(rr, 6).value = f'=SUM(Projection!K{a}:K{b})'
    sm.cell(rr, 7).value = f'=SUM(Projection!L{a}:L{b})'
    sm.cell(rr, 8).value = f'=SUM(Projection!M{a}:M{b})'
    sm.cell(rr, 9).value = f'=SUM(Projection!O{a}:O{b})'
    sm.cell(rr, 10).value = f'=SUM(Projection!P{a}:P{b})'
    for col in range(2, 11):
        sm.cell(rr, col).font = GREEN
        sm.cell(rr, col).number_format = KWHFMT if col == 2 else MONEY

for row in (5, 6, 7, 8):
    for col in range(1, 11):
        sm.cell(row, col).border = BORDER

sm.cell(10, 1, 'Δ FY1 vs TTM Actual (%)').font = BOLD
for col in range(2, 11):
    cl = get_column_letter(col)
    sm.cell(10, col).value = f'=IF({cl}5=0,"n/a",{cl}6/{cl}5-1)'
    sm.cell(10, col).font = BLACK
    sm.cell(10, col).number_format = PCT
    sm.cell(10, col).border = BORDER
sm.cell(10, 1).border = BORDER

sm['A12'] = 'kWh & Total Revenue by month — FY1-FY3 (see chart)'
sm['A12'].font = BOLD

chart1 = LineChart()
chart1.title = 'Projected Total Revenue by Month (J$)'
chart1.y_axis.title = 'J$'
chart1.x_axis.title = 'Period'
chart1.height, chart1.width = 9, 22
data = Reference(ps, min_col=16, min_row=3, max_row=last_proj_row)
cats = Reference(ps, min_col=3, min_row=pr0, max_row=last_proj_row)
chart1.add_data(data, titles_from_data=True)
chart1.set_categories(cats)
sm.add_chart(chart1, 'A14')

chart2 = LineChart()
chart2.title = 'Projected Final kWh by Month'
chart2.y_axis.title = 'kWh'
chart2.x_axis.title = 'Period'
chart2.height, chart2.width = 9, 22
data2 = Reference(ps, min_col=7, min_row=3, max_row=last_proj_row)
chart2.add_data(data2, titles_from_data=True)
chart2.set_categories(cats)
sm.add_chart(chart2, 'A32')

wb._sheets = [wb['Drivers'], wb['History'], wb['Seasonality'], wb['Projection'], wb['Summary']]

import sys
OUT = sys.argv[1] if len(sys.argv) > 1 else 'Alcoa_RT70_3Year_Projection.xlsx'
wb.save(OUT)
print('WROTE', OUT)
