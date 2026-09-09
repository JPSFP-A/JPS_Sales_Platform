# -*- coding: utf-8 -*-
# Caribbean Cement Co Ltd (302571-686496) — RT50 — same treatment as the Alcoa RT70
# model, adapted to this account's different data characteristics:
#  - jps_actuals is ALREADY clean here (fuel_jmd is real, ~40-50% of revenue, unlike
#    Alcoa's $0 bug) -- no Fuel reclassification needed.
#  - This account is NOT GCT-exempt (GCT ~13-16% of revenue). revenue_jmd (jps_actuals,
#    2025/2026) is GCT-EXCLUSIVE; the raw files' net_billed_revenue (used for the 2024
#    backfill) is GCT-INCLUSIVE -- confirmed by comparing Jul-2025 raw ($324,362,115)
#    vs jps_actuals ($282,054,013): the $42,308,102 gap exactly matches that month's
#    GCT. 2024 revenue below is raw net_billed_revenue MINUS raw GCT, to match
#    jps_actuals' GCT-exclusive convention -- confirmed reconciling to within $25K/mo.
#  - No hurricane flag applied: Oct-2025 (4,340,075 kWh) is actually LOWER than Nov-2025
#    (7,600,392) for this account, and monthly volume swings 2.9M-11M kWh routinely
#    (cement kiln maintenance/demand cycles), so there's no clear storm-driven dip to
#    normalize the way Alcoa's was -- flagged as an open question, not assumed.
#  - No given future KVA schedule or negotiated demand/IPP-fixed/fuel rates exist for
#    this account (unlike Alcoa's user-provided Aug25-Jul28 schedule + $2,852.04/KVA
#    etc.) -- Projected months (Aug-2026 to Dec-2028) use the SAME seasonality +
#    escalation-driver mechanism, with Demand/IPP/Fuel/Other all modeled as historical
#    $/kWh rates (like Alcoa's original template, before account-specific inputs).
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
for c, w in zip('ABCDEFGHIJKLMNOPQ', [6, 10, 12, 14, 15, 13, 13, 13, 14, 11, 15, 15, 15, 15, 15, 12, 13]):
    hs.column_dimensions[c].width = w
hs['A1'] = 'CARIBBEAN CEMENT CO LTD — RT50 — HISTORICAL ACTUALS'
hs['A1'].font = TITLE
hs.merge_cells('A1:Q1')
hs['A1'].fill = NAVY
hs['A1'].alignment = Alignment(vertical='center', indent=1)
hs.row_dimensions[1].height = 22
hs['A2'] = '32 months, Jan-2024 to Aug-2026 · Account 302571-686496 · 2024: raw "<Mon> 24.csv" (GCT backed out to match jps_actuals convention) · 2025-2026: jps_actuals, GCT backfilled from the raw file where jps_actuals has it null · Fuel/GCT already reliable in source data, no reclassification needed · No Hurricane flag applied (see note)'
hs['A2'].font = Font(name=FONT, italic=True, size=9, color='6B7A99')
hs.merge_cells('A2:Q2')

HDRS = ['Year', 'Month#', 'Period', 'kWh', 'Revenue $', 'Demand $', 'Fuel $', 'Energy $', 'IPP $',
        'Cust Chg $', 'GCT $', 'Demand $/kWh', 'Energy $/kWh', 'Other/Base $', 'Other $/kWh', 'Flag', 'KVA (true meter)']
r0 = 4
for j, h in enumerate(HDRS):
    c = hs.cell(r0, j + 1, h)
    c.font = HDR
    c.fill = NAVY
    c.alignment = Alignment(horizontal='center', wrap_text=True)
    c.border = BORDER
hs.row_dimensions[r0].height = 28

# (year, month, kwh, revenue[GCT-excl], demand, fuel, energy, ipp, custchg, gct)
ROWS = [
    (2024, 1, 9010981, 216171468, 53643111, 77752482, 40874947, 43917183, 8321, 32425720),
    (2024, 2, 9473251, 219030121, 52230712, 93804060, 43104982, 29184103, 8346, 32854519),
    (2024, 3, 8631765, 200907235, 51942138, 71259124, 39047329, 37814999, 8285, 30136085),
    (2024, 4, 10032628, 219516796, 50158603, 84033566, 45912222, 39553894, 8394, 32927519),
    (2024, 5, 10121419, 223169398, 50846141, 86147656, 46190473, 39012111, 8389, 33505410),
    (2024, 6, 7996774, 194336413, 48610422, 72327639, 35869105, 37163640, 8225, 29150463),
    (2024, 7, 7720195, 191330750, 49910520, 66998406, 34650060, 39197782, 8217, 28699613),
    (2024, 8, 4741842, 130152356, 47253494, 31753565, 20485937, 29767324, 7934, 19522854),
    (2024, 9, 8080100, 195447369, 50411890, 71528238, 37326660, 34799752, 8467, 29317105),
    (2024, 10, 8767488, 223638435, 50684121, 88114568, 40750024, 38824178, 8514, 33019331),
    (2024, 11, 5368988, 141479991, 38780633, 49272630, 24068305, 28008214, 8209, 21221999),
    (2024, 12, 9056977, 230129945, 50723170, 109857584, 42055589, 26345732, 8522, 34510736),
    (2025, 1, 9513636, 242523912, 51049185, 115352570, 44444761, 30970716, 8556, 36378587.49),
    (2025, 2, 8003489, 204035126, 49537484, 90411868, 36922838, 26066708, 8452, 30605269.47),
    (2025, 3, 7597128, 205638754, 49678981, 95381103, 34996933, 24553724, 8414, 30845813.11),
    (2025, 4, 4170162, 135942038, 48228377, 47433053, 18408016, 20710241, 8068, 20391305.88),
    (2025, 5, 2942654, 84670561, 27920972, 27604078, 11170217, 17067924, 6940, 12700583.74),
    (2025, 6, 7698994, 207313042, 50570423, 100076326, 35528717, 18851576, 8454, 31096955.90),
    (2025, 7, 11021019, 282054013, 55962892, 136171332, 52424952, 34485724, 8697, 42308101.72),
    (2025, 8, 9044298, 235890354, 54537645, 103872990, 42497472, 31843978, 8609, 35383553.66),
    (2025, 9, 10829030, 271429779, 56119069, 121361047, 51478262, 39078483, 8707, 40714466.40),
    (2025, 10, 4340075, 138380411, 50365172, 41994631, 19275383, 24499973, 8136, 20757061.30),
    (2025, 11, 7600392, 218861307, 53935867, 100216575, 35246500, 26478481, 8477, 32829196.33),
    (2025, 12, 9362698, 268664032, 54772050, 148053448, 43943685, 18725094, 8602, 40299605.64),
    (2026, 1, 9051552, 241149634, 53404650, 113215214, 42450839, 29725513, 8583, 36172445.89),
    (2026, 2, 10150144, 323836987, 56226344, 186774095, 47803677, 31659262, 8623, 48575547.83),
    (2026, 3, 9895989, 246759030, 56327291, 105330072, 46526207, 37365413, 8617, 37013854.82),
    (2026, 4, 9198915, 235756440, 55312719, 120098757, 43019790, 15497284, 8579, 35363466.63),
    (2026, 5, 9748626, 238353218, 55784593, 114968147, 45854276, 20080750, 8598, 35752982),
    (2026, 6, 8887583, 230897456, 56264574, 104855189, 42751880, 25258312, 8813, 34634618.92),
    (2026, 7, 7711091, 206989236, 53275048, 81463293, 36797085, 33811926, 8718, 31048385),
    (2026, 8, 8535830, 219221982, 54637768, 86606221, 40865471, 34892644, 8775, 32883297.39),
]
# True metered KVA. 2024 + most of 2025/2026 from Billing Details Report's
# kva_billed_consump field. The 6 months with no Billing Details Report raw file
# (Jan/Feb/Mar/Apr/Jun/Sep-2025) are filled 2026-08-12 from the Check Consumption
# Report files instead (SUM of SCAT_CODE KVAP+KVAL+KVAO, physical kVA by TOU period)
# -- cross-checked against Jul-2025's already-confirmed true KVA (65,430.00): the
# same sum from that month's Check Consumption file matches to the exact kVA, so
# this source is equally authoritative, just structured differently.
KVA_TRUE = {
    (2024, 1): 65181.00, (2024, 2): 63851.00, (2024, 3): 63600.00, (2024, 4): 60940.00,
    (2024, 5): 61605.00, (2024, 6): 60276.00, (2024, 7): 61938.00, (2024, 8): 60525.00,
    (2024, 9): 60609.00, (2024, 10): 60525.00, (2024, 11): 48652.80, (2024, 12): 60525.00,
    (2025, 1): 60774.00, (2025, 2): 59860.00, (2025, 3): 60109.00, (2025, 4): 60609.00,
    (2025, 5): 43698.00, (2025, 6): 60941.00, (2025, 7): 65430.00, (2025, 8): 64598.00,
    (2025, 9): 65679.00, (2025, 10): 62355.00, (2025, 11): 64765.00, (2025, 12): 64931.00,
    (2026, 1): 63601.00, (2026, 2): 65929.00, (2026, 3): 66345.00, (2026, 4): 65347.00,
    (2026, 5): 65930.00, (2026, 6): 65098.00, (2026, 7): 62604.00, (2026, 8): 63185.00,
}
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
    # Other/Base $ = Revenue - (Demand+Fuel+Energy+IPP+CustChg) -- NOT subtracting GCT:
    # Revenue here is already GCT-exclusive (see header note), unlike Alcoa where GCT
    # was always $0 so subtracting it was harmless either way.
    ocell = hs.cell(r, 14)
    ocell.value = f'=IF(OR(F{r}="",G{r}="",H{r}="",I{r}="",J{r}=""),"",E{r}-F{r}-G{r}-H{r}-I{r}-J{r})'
    ocell.font = BLACK; ocell.number_format = MONEY; ocell.border = BORDER
    oratecell = hs.cell(r, 15)
    oratecell.value = f'=IF(OR(N{r}="",D{r}=0),"",N{r}/D{r})'
    oratecell.font = BLACK; oratecell.number_format = RATE; oratecell.border = BORDER
    fcell2 = hs.cell(r, 16, 'Normal')  # no hurricane adjustment applied -- see note
    fcell2.font = BLACK
    fcell2.border = BORDER
    fcell2.alignment = Alignment(horizontal='center')
    kva_true = KVA_TRUE.get((y, m))
    kcell = hs.cell(r, 17, kva_true if kva_true is not None else '')
    kcell.font = BLUE if kva_true is not None else BLACK
    kcell.number_format = '#,##0.00'
    kcell.border = BORDER
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
hs['A' + str(r + 2)] = ('Note (2026-08-12): This account\'s jps_actuals data is already clean -- fuel_jmd is real (~40-50% of revenue) in every month, unlike Alcoa\'s $0 bug, so no Fuel reclassification was needed. '
                         'This account is NOT GCT-exempt (GCT ~13-16% of revenue) -- jps_actuals.revenue_jmd (used for 2025/2026) is GCT-exclusive; the raw files\' net_billed_revenue (used for the 2024 backfill) is GCT-inclusive, confirmed by comparing Jul-2025 raw ($324,362,115) vs jps_actuals ($282,054,013) -- the $42,308,102 gap exactly matches that month\'s GCT. '
                         '2024 Revenue above is raw net_billed_revenue minus raw GCT, to match the GCT-exclusive convention -- reconciles to within ~$25K/month via Demand+Fuel+Energy+IPP+CustCharge. '
                         'NO HURRICANE FLAG: unlike Alcoa, this account shows no clear storm-driven dip in Nov/Dec-2025 -- Oct-2025 (4,340,075 kWh) is actually LOWER than Nov-2025 (7,600,392), and this account routinely swings 2.9M-11M kWh/month (cement kiln maintenance/demand cycles). Flagged as an open question rather than assumed; all 32 months are averaged as "Normal".'
                         '2025 Jan/Feb/Mar/Apr/Jun/Sep have no Billing Details Report raw file -- KVA for those 6 months (2026-08-12) comes instead from the Check Consumption Report files (SUM of SCAT_CODE KVAP+KVAL+KVAO), cross-checked exact against Jul-2025\'s already-confirmed value. '
                         'GCT FIX (2026-08-12): jps_actuals had GCT as null for May/Jul-2026, but the raw files for those two months DO exist and carry a real GCT figure ($35,752,982 / $31,048,385) -- backfilled here from the raw file rather than left blank. '
                         'Aug-2026 added (2026-09-09): kwh/revenue/demand/fuel/energy/ipp/custchg from jps_actuals (component sums reconcile exactly to the raw file\'s KVAP/KVAL/KVAO, FuelOffPeak/PartialPeak/OnPeak and KWHP/KWHL/KWHO fields). jps_actuals GCT is null for this month too -- backfilled from the raw file\'s GCT column ($32,883,297.39), same as May/Jul above. KVA (63,185) is the raw file\'s own kva_billed_consump field, the same primary source used for every other actual month.')
hs['A' + str(r + 2)].font = Font(name=FONT, italic=True, size=8.5, color='B87800')
hs['A' + str(r + 2)].alignment = Alignment(wrap_text=True, vertical='top')
hs.merge_cells(f'A{r+2}:Q{r+2}')
hs.row_dimensions[r + 2].height = 130

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
    monthnum = i + 1
    ss.cell(rr, 1, monthnum).font = BLACK
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
drow(4, 'Volume adjustment vs. seasonal baseline (%)', 0.00, PCT, 'No scenario applied by default — flex to test a volume change')
drow(5, 'Apply seasonality? (1 = Yes, 0 = No / use flat monthly average)', 1, '0', 'Set to 0 to test a flat (non-seasonal) run-rate instead')
drow(6, 'Multiplier override (x)', 1.00, '0.00"x"', 'Additional scenario multiplier on top of the seasonality-derived volume, 1.00x = no change')

section(8, 'RATE ESCALATION (% per year, compounding from Year 1 of the Projected period)')
drow(9, 'Demand rate escalation (%/yr)', 0.00, PCT, 'Demand modeled as $/kWh — no given future KVA schedule/contract rate exists for this account (unlike Alcoa)')
drow(10, 'Energy rate escalation (%/yr)', 0.00, PCT)
drow(11, 'IPP rate escalation (%/yr)', 0.00, PCT)
drow(12, 'Fuel rate escalation (%/yr)', 0.00, PCT)
drow(13, 'Other/base tariff rate escalation (%/yr)', 0.00, PCT, 'Small residual — see History tab note')
drow(14, 'Customer charge escalation (%/yr)', 0.00, PCT)

section(16, 'OTHER')
drow(17, 'GCT rate applied (%)', 0.14, PCT, 'This account is NOT GCT-exempt — 0.14 approximates the ~13-16% historical GCT/revenue ratio; flex to test')
drow(18, 'Projection start (first row of Projection tab)', '2024-01', '@', 'Format YYYY-MM')

section(20, 'REFERENCE (informational, not scenario inputs)')
drow(21, 'Latest true billed KVA (Aug-2026)', 63185.00, '#,##0.00', 'Source: Aug 26.csv, kva_billed_consump field', input_cell=False)
ds.cell(21, 2).font = BLACK

section(23, 'HISTORICAL BASELINE UNIT RATES (computed from History tab averages — feed the Projected months)')
def rate_row(row, label, num_col, den_col='D'):
    ds.cell(row, 1, label).font = BLACK
    ds.cell(row, 2).value = f'=History!{num_col}{AVG_ROW}/History!{den_col}{AVG_ROW}'
    ds.cell(row, 2).font = GREEN; ds.cell(row, 2).number_format = RATE
    ds.cell(row, 2).border = BORDER; ds.cell(row, 1).border = BORDER

rate_row(24, 'Avg Demand $/kWh (History col F/D)', 'F')
rate_row(25, 'Avg Energy $/kWh (History col H/D)', 'H')
rate_row(26, 'Avg IPP $/kWh (History col I/D)', 'I')
rate_row(27, 'Avg Fuel $/kWh (History col G/D)', 'G')
rate_row(28, 'Avg Other/Base $/kWh (History col N/D)', 'N')
ds.cell(29, 1, 'Avg Customer Charge $/mo (History col J avg)').font = BLACK
ds.cell(29, 2).value = f'=History!J{AVG_ROW}'
ds.cell(29, 2).font = GREEN; ds.cell(29, 2).number_format = MONEY
ds.cell(29, 2).border = BORDER; ds.cell(29, 1).border = BORDER

ds['A31'] = ('MODELING NOTES: (1) Unlike Alcoa, there is no user-provided future KVA schedule or negotiated $/KVA rate for this account — every kWh-driven component (Demand, Energy, IPP, Fuel, Other) uses a history-derived $/kWh rate with an escalation driver, same as Alcoa\'s ORIGINAL template before account-specific inputs were given. '
             '(2) GCT is real for this account (~13-16% of revenue) — applied via the GCT rate driver, unlike Alcoa which was GCT-exempt. '
             '(3) No hurricane normalization applied — see History tab note; Nov/Dec-2025 are included in all averages as "Normal".')
ds['A31'].font = Font(name=FONT, italic=True, size=8.5, color='B87800')
ds.merge_cells('A31:E31')
ds.row_dimensions[31].height = 44
ds['A31'].alignment = Alignment(wrap_text=True, vertical='top')

# ============================================================ PROJECTION =========
# 60 months, Jan-2024 to Dec-2028 — same "actuals where we have actuals" structure as
# the Alcoa model. Jan-2024 to Aug-2026 (32 months) pulled straight from History, not
# re-derived. Sep-2026 to Dec-2028 (28 months) uses seasonality + history-derived rates
# (no given future schedule for this account, unlike Alcoa's KVA-driven approach).
ACTUAL_ROWS = 32
PROJ_ROWS = 28
TOTAL_ROWS = ACTUAL_ROWS + PROJ_ROWS

ps = wb.create_sheet('Projection')
ps.sheet_view.showGridLines = False
PW = [6, 6, 10, 10, 10, 13, 15, 14, 15, 13, 13, 13, 13, 15, 14, 15, 13, 16]
for c, w in zip('ABCDEFGHIJKLMNOPQR', PW):
    ps.column_dimensions[c].width = w
ps['A1'] = 'PROJECTION — CARIBBEAN CEMENT RT50 (60 months, Jan-2024 to Dec-2028; Actual through Aug-2026, then modeled)'
ps['A1'].font = TITLE
ps.merge_cells('A1:R1')
ps['A1'].fill = NAVY
ps.row_dimensions[1].height = 22
hdrs3 = ['Per#', 'CY', 'Month', 'Cal Mo#', 'A/P', 'KVA', 'Seasonal kWh', 'Volume-Adj kWh', 'Final kWh\n(x multiplier)',
         'Demand $', 'Energy $', 'IPP $', 'Fuel $', 'Other/Base $', 'Cust Chg $', 'Subtotal $', 'GCT $', 'Total Revenue $']
for j, h in enumerate(hdrs3):
    c = ps.cell(3, j + 1, h); c.font = HDR; c.fill = NAVY; c.border = BORDER
    c.alignment = Alignment(horizontal='center', wrap_text=True)
ps.row_dimensions[3].height = 30

pr0 = 4
for i in range(TOTAL_ROWS):
    rr = pr0 + i
    is_actual = i < ACTUAL_ROWS
    ps.cell(rr, 1, i + 1).font = BLACK
    ps.cell(rr, 2).value = f'=YEAR(C{rr})'
    ps.cell(rr, 2).font = BLACK
    ps.cell(rr, 2).alignment = Alignment(horizontal='center')
    ps.cell(rr, 3).value = f'=EDATE(DATEVALUE(Drivers!$B$18&"-01"),{i})'
    ps.cell(rr, 3).number_format = 'mmm-yy'
    ps.cell(rr, 3).font = BLACK
    ps.cell(rr, 4).value = f'=MONTH(C{rr})'
    ps.cell(rr, 4).font = BLACK
    ps.cell(rr, 4).alignment = Alignment(horizontal='center')
    apcell = ps.cell(rr, 5, 'Actual' if is_actual else 'Projected')
    apcell.font = BLACK
    apcell.alignment = Alignment(horizontal='center')

    if is_actual:
        hr = first_data_row + i
        ps.cell(rr, 6).value = f'=History!Q{hr}'
        ps.cell(rr, 6).font = GREEN; ps.cell(rr, 6).number_format = '#,##0.00'
        ps.cell(rr, 7).value = ''
        ps.cell(rr, 8).value = ''
        ps.cell(rr, 9).value = f'=History!D{hr}'
        ps.cell(rr, 9).font = GREEN; ps.cell(rr, 9).number_format = KWHFMT
        ps.cell(rr, 10).value = f'=History!F{hr}'
        ps.cell(rr, 10).font = GREEN; ps.cell(rr, 10).number_format = MONEY
        ps.cell(rr, 11).value = f'=History!H{hr}'
        ps.cell(rr, 11).font = GREEN; ps.cell(rr, 11).number_format = MONEY
        ps.cell(rr, 12).value = f'=History!I{hr}'
        ps.cell(rr, 12).font = GREEN; ps.cell(rr, 12).number_format = MONEY
        ps.cell(rr, 13).value = f'=History!G{hr}'
        ps.cell(rr, 13).font = GREEN; ps.cell(rr, 13).number_format = MONEY
        ps.cell(rr, 14).value = f'=History!N{hr}'
        ps.cell(rr, 14).font = GREEN; ps.cell(rr, 14).number_format = MONEY
        ps.cell(rr, 15).value = f'=History!J{hr}'
        ps.cell(rr, 15).font = GREEN; ps.cell(rr, 15).number_format = MONEY
        ps.cell(rr, 16).value = f'=SUM(J{rr}:O{rr})'
        ps.cell(rr, 16).font = BOLD; ps.cell(rr, 16).number_format = MONEY
        ps.cell(rr, 17).value = f'=History!K{hr}'
        ps.cell(rr, 17).font = GREEN; ps.cell(rr, 17).number_format = MONEY
        ps.cell(rr, 18).value = f'=History!E{hr}'
        ps.cell(rr, 18).font = GREEN; ps.cell(rr, 18).number_format = MONEY
    else:
        ps.cell(rr, 6).value = ''  # no given future KVA schedule for this account
        ps.cell(rr, 7).value = f'=IF(Drivers!$B$5=1,INDEX(Seasonality!$C$4:$C$15,MATCH(D{rr},Seasonality!$A$4:$A$15,0)),Seasonality!$C$16)'
        ps.cell(rr, 7).font = GREEN; ps.cell(rr, 7).number_format = KWHFMT
        ps.cell(rr, 8).value = f'=G{rr}*(1+Drivers!$B$4)'
        ps.cell(rr, 8).font = BLACK; ps.cell(rr, 8).number_format = KWHFMT
        ps.cell(rr, 9).value = f'=H{rr}*Drivers!$B$6'
        ps.cell(rr, 9).font = BLACK; ps.cell(rr, 9).number_format = KWHFMT
        yexp = f'(ROUNDUP((A{rr}-{ACTUAL_ROWS+1})/12,0)-1)'
        ps.cell(rr, 10).value = f'=$I{rr}*Drivers!$B$24*(1+Drivers!$B$9)^{yexp}'
        ps.cell(rr, 10).font = BLACK; ps.cell(rr, 10).number_format = MONEY
        ps.cell(rr, 11).value = f'=$I{rr}*Drivers!$B$25*(1+Drivers!$B$10)^{yexp}'
        ps.cell(rr, 11).font = BLACK; ps.cell(rr, 11).number_format = MONEY
        ps.cell(rr, 12).value = f'=$I{rr}*Drivers!$B$26*(1+Drivers!$B$11)^{yexp}'
        ps.cell(rr, 12).font = BLACK; ps.cell(rr, 12).number_format = MONEY
        ps.cell(rr, 13).value = f'=$I{rr}*Drivers!$B$27*(1+Drivers!$B$12)^{yexp}'
        ps.cell(rr, 13).font = BLACK; ps.cell(rr, 13).number_format = MONEY
        ps.cell(rr, 14).value = f'=$I{rr}*Drivers!$B$28*(1+Drivers!$B$13)^{yexp}'
        ps.cell(rr, 14).font = BLACK; ps.cell(rr, 14).number_format = MONEY
        ps.cell(rr, 15).value = f'=Drivers!$B$29*(1+Drivers!$B$14)^{yexp}'
        ps.cell(rr, 15).font = BLACK; ps.cell(rr, 15).number_format = MONEY
        ps.cell(rr, 16).value = f'=SUM(J{rr}:O{rr})'
        ps.cell(rr, 16).font = BOLD; ps.cell(rr, 16).number_format = MONEY
        ps.cell(rr, 17).value = f'=P{rr}*Drivers!$B$17'
        ps.cell(rr, 17).font = BLACK; ps.cell(rr, 17).number_format = MONEY
        ps.cell(rr, 18).value = f'=P{rr}+Q{rr}'
        ps.cell(rr, 18).font = BOLD; ps.cell(rr, 18).number_format = MONEY

    for col in range(1, 19):
        ps.cell(rr, col).border = BORDER
    y_i = 2024 + i // 12
    band = None
    if not is_actual and y_i % 2 == 0:
        band = PatternFill('solid', start_color='F8FAFC')
    elif is_actual and y_i % 2 == 1:
        band = PatternFill('solid', start_color='EFF6FF')
    if band:
        for col in range(1, 19):
            ps.cell(rr, col).fill = band
ps.freeze_panes = 'C4'
last_proj_row = pr0 + TOTAL_ROWS - 1
# Placed two rows below the LAST data row, not a hardcoded row number: a fixed 'A62'
# here used to collide with whichever real month happened to land on row 62 once
# ACTUAL_ROWS/PROJ_ROWS changed the row count's shape (Nov-2028 was silently wiped
# by the merge_cells call below, which discards every cell but the top-left when a
# range is merged) -- discovered when adding Aug-2026 exposed it. last_proj_row+2
# always lands after every data row, whatever ACTUAL_ROWS/PROJ_ROWS are.
_footer_row = last_proj_row + 2
ps.cell(_footer_row, 1).value = ('Jan-2024 to Aug-2026 (32 rows, "Actual") pulled directly from History, row for row. Sep-2026 to Dec-2028 (28 rows, "Projected") use seasonality-derived kWh + history-derived $/kWh rates for every component -- there is no given future KVA schedule or negotiated demand/IPP/fuel rate for this account, unlike Alcoa, so Demand here stays modeled as $/kWh (Drivers tab note). '
             'No hurricane normalization was applied to the seasonality baseline (History tab note) -- if you have reason to believe this account was storm-affected in Nov/Dec-2025, flag it and I\'ll rebuild that portion the same way as Alcoa\'s.')
ps.cell(_footer_row, 1).font = Font(name=FONT, italic=True, size=8.5, color='B87800')
ps.merge_cells(start_row=_footer_row, start_column=1, end_row=_footer_row, end_column=18)
ps.row_dimensions[_footer_row].height = 44
ps.cell(_footer_row, 1).alignment = Alignment(wrap_text=True, vertical='top')

# ============================================================ SUMMARY ============
sm = wb.create_sheet('Summary')
sm.sheet_view.showGridLines = False
for c, w in zip('ABCDEFGHIJ', [28, 13, 14, 14, 14, 14, 14, 14, 12, 16]):
    sm.column_dimensions[c].width = w
sm['A1'] = 'SUMMARY — ANNUAL ROLLUP (CALENDAR YEAR)'
sm['A1'].font = TITLE
sm.merge_cells('A1:J1')
sm['A1'].fill = NAVY
sm.row_dimensions[1].height = 22
sm['A2'] = 'Caribbean Cement Co Ltd · Account 302571-686496 · RT50 · Scenario: see Drivers tab'
sm['A2'].font = Font(name=FONT, italic=True, size=9, color='6B7A99')
sm.merge_cells('A2:J2')

hdrs4 = ['', 'kWh', 'Demand $', 'Energy $', 'IPP $', 'Fuel $', 'Other/Base $', 'Cust Chg $', 'GCT $', 'Total Revenue $']
for j, h in enumerate(hdrs4):
    c = sm.cell(4, j + 1, h); c.font = HDR; c.fill = NAVY; c.border = BORDER
    c.alignment = Alignment(horizontal='center', wrap_text=True)
sm.row_dimensions[4].height = 26

year_labels = {
    2024: 'CY2024 (all Actual)', 2025: 'CY2025 (all Actual)',
    2026: 'CY2026 (Jan-Aug Actual + Sep-Dec Projected, blended)',
    2027: 'CY2027 (all Projected)', 2028: 'CY2028 (all Projected)',
}
for k, yr in enumerate([2024, 2025, 2026, 2027, 2028]):
    rr = 5 + k
    sm.cell(rr, 1, year_labels[yr]).font = BOLD
    sm.cell(rr, 2).value = f'=SUMIF(Projection!$B${pr0}:$B${last_proj_row},{yr},Projection!$I${pr0}:$I${last_proj_row})'
    sm.cell(rr, 3).value = f'=SUMIF(Projection!$B${pr0}:$B${last_proj_row},{yr},Projection!$J${pr0}:$J${last_proj_row})'
    sm.cell(rr, 4).value = f'=SUMIF(Projection!$B${pr0}:$B${last_proj_row},{yr},Projection!$K${pr0}:$K${last_proj_row})'
    sm.cell(rr, 5).value = f'=SUMIF(Projection!$B${pr0}:$B${last_proj_row},{yr},Projection!$L${pr0}:$L${last_proj_row})'
    sm.cell(rr, 6).value = f'=SUMIF(Projection!$B${pr0}:$B${last_proj_row},{yr},Projection!$M${pr0}:$M${last_proj_row})'
    sm.cell(rr, 7).value = f'=SUMIF(Projection!$B${pr0}:$B${last_proj_row},{yr},Projection!$N${pr0}:$N${last_proj_row})'
    sm.cell(rr, 8).value = f'=SUMIF(Projection!$B${pr0}:$B${last_proj_row},{yr},Projection!$O${pr0}:$O${last_proj_row})'
    sm.cell(rr, 9).value = f'=SUMIF(Projection!$B${pr0}:$B${last_proj_row},{yr},Projection!$Q${pr0}:$Q${last_proj_row})'
    sm.cell(rr, 10).value = f'=SUMIF(Projection!$B${pr0}:$B${last_proj_row},{yr},Projection!$R${pr0}:$R${last_proj_row})'
    for col in range(2, 11):
        sm.cell(rr, col).font = GREEN
        sm.cell(rr, col).number_format = KWHFMT if col == 2 else MONEY

for row in range(5, 10):
    for col in range(1, 11):
        sm.cell(row, col).border = BORDER

sm['A11'] = 'Every $ column reconciles exactly to Projection: Actual rows (Jan-2024/Aug-2026) are pulled straight from History; Projected rows (Sep-2026/Dec-2028) use history-derived $/kWh rates (no given future schedule exists for this account, unlike Alcoa). GCT is real here (~13-16% of revenue) and applied via the Drivers rate.'
sm['A11'].font = Font(name=FONT, italic=True, size=8.5, color='B87800')
sm.merge_cells('A11:J11')
sm.row_dimensions[11].height = 28
sm['A11'].alignment = Alignment(wrap_text=True, vertical='top')

sm['A13'] = 'kWh & Total Revenue by month — full Jan-2024 to Dec-2028 timeline (see chart)'
sm['A13'].font = BOLD

chart1 = LineChart()
chart1.title = 'Total Revenue by Month, Jan-2024 to Dec-2028 (J$) — Actual through Aug-2026, then Projected'
chart1.y_axis.title = 'J$'
chart1.x_axis.title = 'Period'
chart1.height, chart1.width = 9, 24
data = Reference(ps, min_col=18, min_row=3, max_row=last_proj_row)
cats = Reference(ps, min_col=3, min_row=pr0, max_row=last_proj_row)
chart1.add_data(data, titles_from_data=True)
chart1.set_categories(cats)
sm.add_chart(chart1, 'A15')

chart2 = LineChart()
chart2.title = 'Final kWh by Month — Actual through Aug-2026, then Projected'
chart2.y_axis.title = 'kWh'
chart2.x_axis.title = 'Period'
chart2.height, chart2.width = 9, 24
data2 = Reference(ps, min_col=9, min_row=3, max_row=last_proj_row)
chart2.add_data(data2, titles_from_data=True)
chart2.set_categories(cats)
sm.add_chart(chart2, 'A32')

wb._sheets = [wb['Drivers'], wb['History'], wb['Seasonality'], wb['Projection'], wb['Summary']]

import sys
OUT = sys.argv[1] if len(sys.argv) > 1 else 'CaribCement_RT50_Projection.xlsx'
wb.save(OUT)
print('WROTE', OUT)
