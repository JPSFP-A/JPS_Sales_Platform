# -*- coding: utf-8 -*-
# Non-fuel revenue walk with live formulas: customer charge, then energy line split into volume, mix, FX and other yield.
# Inputs sheet holds every source number; each comparison sheet is formulas only.
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as L
import _pvm_sep as P

CL = ['RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']
FXADJ = {'SEP': dict(cust=15125e3, demand=33795e3, energy=92594e3), 'YTD': dict(cust=116815e3, demand=260552e3, energy=638669e3)}
H = Font(bold=True, color='FFFFFF'); HF = PatternFill('solid', fgColor='1F3864'); B = Font(bold=True)
INP = PatternFill('solid', fgColor='DDEBF7'); Y = PatternFill('solid', fgColor='FFF2CC'); G = PatternFill('solid', fgColor='E2EFDA')
N0 = '#,##0;[Red]-#,##0'; N2 = '#,##0.00'; PCT = '0.0%;[Red]-0.0%'

def bud_energy_line(per):
    """Budget energy+demand and customer charge by class (J$), with the F/X adjustment lines allocated pro rata within each component."""
    b = P.budget(per); tot = {k: sum(b[c][k] for c in b) for k in ('cust', 'energy', 'demand')}; out = {}
    for c, v in b.items():
        cu = v['cust'] * (1 + FXADJ[per]['cust'] / tot['cust'])
        ed = v['energy'] * (1 + FXADJ[per]['energy'] / tot['energy']) + (v['demand'] * (1 + FXADJ[per]['demand'] / tot['demand']) if tot['demand'] else 0.0)
        out[c] = dict(kwh=v['kwh'], cust=cu, ed=ed)
    return out
def act_energy_line(d):
    return {c: dict(kwh=v['kwh'], cust=v['cust'], ed=v['nf'] - v['cust']) for c, v in d.items()}

# ---------------- finance workbook ----------------
fw = openpyxl.load_workbook(r'C:\Users\jwilson\AppData\Local\Temp\JPSCo Financials_09-26 (1).xlsx', read_only=True, data_only=True)['Revenues']
R = {i: r for i, r in enumerate(fw.iter_rows(values_only=True), 1)}
fv = lambda row, col: float(R[row][col - 1])
COLS = {('SEP', 'A'): 3, ('SEP', 'B'): 6, ('SEP', 'P'): 23, ('YTD', 'A'): 12, ('YTD', 'B'): 13, ('YTD', 'P'): 20}
FROW = {'Energy line (US$000)': 13, 'Customer charge (US$000)': 14, 'Sales, normalized (MWh)': 46, 'Billing FX rate (J$/US$)': 32}

wb = Workbook()
# =================== Inputs ===================
si = wb.active; si.title = 'Inputs'
si['A1'] = 'Inputs - every number used in the walk (blue cells are source values)'; si['A1'].font = Font(bold=True, size=13)
si['A3'] = '1. Finance (JPSCo Financials 09-26, Revenues sheet)'; si['A3'].font = B
heads = ['Item', 'Sept actual', 'Sept budget', 'Sept prior year', 'YTD actual', 'YTD budget', 'YTD prior year', 'Source']
for i, h in enumerate(heads, 1):
    c = si.cell(4, i, h); c.font = H; c.fill = HF; c.alignment = Alignment(horizontal='center', wrap_text=True)
FIN = {}   # (item, per, kind) -> cell address on Inputs
order = [('SEP', 'A'), ('SEP', 'B'), ('SEP', 'P'), ('YTD', 'A'), ('YTD', 'B'), ('YTD', 'P')]
for ri, (item, row) in enumerate(FROW.items(), 5):
    si.cell(ri, 1, item)
    for ci, (per, kind) in enumerate(order, 2):
        c = si.cell(ri, ci, fv(row, COLS[(per, kind)])); c.fill = INP; c.number_format = '#,##0.000' if 'FX' in item else '#,##0'
        FIN[(item, per, kind)] = f"Inputs!${L(ci)}${ri}"
    si.cell(ri, 8, f'Revenues row {row}; columns: month actual C, budget F, prior year W; YTD actual L, budget M, prior YTD T')
si.cell(9, 1, 'Finance FX effect, YTD vs budget (US$000)'); c = si.cell(9, 5, 89); c.fill = INP
si.cell(9, 8, 'Corporate Performance Report slide 11 (Non-Fuel Revenue Variance Analysis, FX bar)')
FXFIN = 'Inputs!$E$9'

si['A11'] = '2. Class detail from billed data (used only for the class shares)'; si['A11'].font = B
si['A12'] = ('MWh and energy+demand revenue (J$000). Sept actual = Earnings Sheet; YTD actual = platform Jan-Aug + Earnings Sheet Sept; prior year = platform (customer billed = 1); '
             'budget = budget file with the F/X adjustment lines allocated pro rata. Customer charge is carried separately on the finance line.')
si.merge_cells('A12:N12'); si['A12'].alignment = Alignment(wrap_text=True, vertical='top'); si.row_dimensions[12].height = 44
sets = {}
for per in ('SEP', 'YTD'):
    sets[(per, 'A')] = act_energy_line(P.actual(2026, per)); sets[(per, 'P')] = act_energy_line(P.actual(2025, per)); sets[(per, 'B')] = bud_energy_line(per)
hdr = ['Class'] + [f'{p} {k} {m}' for p in ('Sept', 'YTD') for k in ('actual', 'budget', 'prior year') for m in ('MWh', 'energy+demand J$000')]
# order columns: for each (per, kind): MWh then J$000
cols = [(per, kind) for per in ('SEP', 'YTD') for kind in ('A', 'B', 'P')]
names = {'A': 'actual', 'B': 'budget', 'P': 'prior year'}; pn = {'SEP': 'Sept', 'YTD': 'YTD'}
si.cell(13, 1, 'Class').font = H; si.cell(13, 1).fill = HF
CLS = {}   # (per, kind, 'mwh'|'ed', class) -> address
for j, (per, kind) in enumerate(cols):
    cm, cr = 2 + 2 * j, 3 + 2 * j
    for cc, m in ((cm, 'MWh'), (cr, 'energy+demand J$000')):
        h = si.cell(13, cc, f'{pn[per]} {names[kind]} {m}'); h.font = H; h.fill = HF; h.alignment = Alignment(wrap_text=True, horizontal='center')
    for ri, c in enumerate(CL, 14):
        si.cell(ri, 1, c)
        d = sets[(per, kind)][c]
        x = si.cell(ri, cm, d['kwh'] / 1e3); x.fill = INP; x.number_format = N0
        y = si.cell(ri, cr, d['ed'] / 1e3); y.fill = INP; y.number_format = N0
        CLS[(per, kind, 'mwh', c)] = f"Inputs!${L(cm)}${ri}"; CLS[(per, kind, 'ed', c)] = f"Inputs!${L(cr)}${ri}"
    CLS[(per, kind, 'mwh_rng')] = f"Inputs!${L(cm)}$14:${L(cm)}$19"; CLS[(per, kind, 'ed_rng')] = f"Inputs!${L(cr)}$14:${L(cr)}$19"
si['A22'] = '3. Customers (average for the period)'; si['A22'].font = B
si['A23'] = 'Actual and prior year: platform customer counts (postpaid + prepaid + commercial accounts). Budget: customer count in the budget file (flat at 727,245 from March). YTD = average of months 1-9.'
si.merge_cells('A23:H23'); si['A23'].alignment = Alignment(wrap_text=True, vertical='top'); si.row_dimensions[23].height = 32
for i, h in enumerate(['Item', 'Sept actual', 'Sept budget', 'Sept prior year', 'YTD actual', 'YTD budget', 'YTD prior year'], 1):
    c = si.cell(24, i, h); c.font = H; c.fill = HF; c.alignment = Alignment(horizontal='center', wrap_text=True)
import _sep_data as _D
_a26 = [_D.cust('post', 2026, m) + _D.cust('pp', 2026, m) + _D.cust('com', 2026, m) for m in range(1, 10)]
_a25 = [_D.cust('post', 2025, m) + _D.cust('pp', 2025, m) + _D.cust('com', 2025, m) for m in range(1, 10)]
_bud = [726442, 727246] + [727245] * 7
CUST = {}
si.cell(25, 1, 'Customers')
for ci, (per, kind) in enumerate(order, 2):
    v = {('SEP', 'A'): _a26[8], ('SEP', 'B'): _bud[8], ('SEP', 'P'): _a25[8], ('YTD', 'A'): sum(_a26) / 9, ('YTD', 'B'): sum(_bud) / 9, ('YTD', 'P'): sum(_a25) / 9}[(per, kind)]
    c = si.cell(25, ci, v); c.fill = INP; c.number_format = N0; CUST[(per, kind)] = f"Inputs!${L(ci)}$25"
si.cell(26, 1, 'Months in period')
for ci, (per, kind) in enumerate(order, 2):
    c = si.cell(26, ci, 1 if per == 'SEP' else 9); c.fill = INP; CUST[('m', per, kind)] = f"Inputs!${L(ci)}$26"
si.row_dimensions[13].height = 44; si.column_dimensions['A'].width = 40
for cc in range(2, 16): si.column_dimensions[L(cc)].width = 14
si.column_dimensions['H'].width = 14

# =================== comparison sheets ===================
def calc_sheet(name, per, kind, title):
    s = wb.create_sheet(name)
    fa = lambda item: FIN[(item, per, 'A')]; fb = lambda item: FIN[(item, per, kind)]
    s['A1'] = title; s['A1'].font = Font(bold=True, size=13)
    s['A2'] = "US$'000 unless stated. Every cell below is a formula on the Inputs sheet.";
    # Step 1
    s['A4'] = 'Step 1 - finance totals'; s['A4'].font = B
    for i, h in enumerate(['', 'Actual', 'Comparison', 'Variance', 'Var %'], 1):
        c = s.cell(5, i, h); c.font = H; c.fill = HF
    rows1 = [('Energy line (energy + demand + F/X)', 'Energy line (US$000)'), ('Customer charge', 'Customer charge (US$000)'), ('Sales, normalized (MWh)', 'Sales, normalized (MWh)'), ('Billing FX rate (J$/US$)', 'Billing FX rate (J$/US$)')]
    for ri, (lab, item) in enumerate(rows1, 6):
        s.cell(ri, 1, lab); s.cell(ri, 2, f'={fa(item)}'); s.cell(ri, 3, f'={fb(item)}'); s.cell(ri, 4, f'=B{ri}-C{ri}'); s.cell(ri, 5, f'=D{ri}/C{ri}')
        for cc in (2, 3, 4): s.cell(ri, cc).number_format = '#,##0.000' if 'FX' in lab else N0
        s.cell(ri, 5).number_format = PCT
    s.cell(10, 1, 'Non-fuel revenue (energy line + customer charge)').font = B
    s.cell(10, 2, '=B6+B7'); s.cell(10, 3, '=C6+C7'); s.cell(10, 4, '=B10-C10'); s.cell(10, 5, '=D10/C10')
    for cc in (2, 3, 4): s.cell(10, cc).number_format = N0; s.cell(10, cc).font = B
    s.cell(10, 5).number_format = PCT
    # Step 2: scaling
    s['A12'] = 'Step 2 - scale the class data to the finance totals'; s['A12'].font = B
    s['A13'] = 'Volume factor, actual = finance MWh / sum of billed class MWh'; s['B13'] = f"=B8/SUM({CLS[(per, 'A', 'mwh_rng')]})"
    s['A14'] = 'Volume factor, comparison'; s['B14'] = f"=C8/SUM({CLS[(per, kind, 'mwh_rng')]})"
    s['A15'] = 'Revenue factor, actual = finance energy line / sum of class energy+demand'; s['B15'] = f"=B6/(SUM({CLS[(per, 'A', 'ed_rng')]})/1)"
    s['A16'] = 'Revenue factor, comparison'; s['B16'] = f"=C6/(SUM({CLS[(per, kind, 'ed_rng')]})/1)"
    for r in (13, 14, 15, 16): s.cell(r, 2).number_format = '0.0000'
    # Step 3: class table
    s['A18'] = 'Step 3 - volume, class mix and rate on the energy line, by class'; s['A18'].font = B
    hd = ['Class', 'Comparison MWh', 'Actual MWh', 'Comparison US$000', 'Actual US$000', 'Comparison US cents/kWh', 'Actual US cents/kWh', 'Volume', 'Class mix', 'Rate (within class)', 'Total']
    for i, h in enumerate(hd, 1):
        c = s.cell(19, i, h); c.font = H; c.fill = HF; c.alignment = Alignment(wrap_text=True, horizontal='center')
    first = 20; last = first + len(CL) - 1; tot = last + 1
    for k, c_ in enumerate(CL):
        r = first + k
        s.cell(r, 1, c_)
        s.cell(r, 2, f"={CLS[(per, kind, 'mwh', c_)]}*$B$14")
        s.cell(r, 3, f"={CLS[(per, 'A', 'mwh', c_)]}*$B$13")
        s.cell(r, 4, f"={CLS[(per, kind, 'ed', c_)]}*$B$16")
        s.cell(r, 5, f"={CLS[(per, 'A', 'ed', c_)]}*$B$15")
        s.cell(r, 6, f'=D{r}/B{r}*100'); s.cell(r, 7, f'=E{r}/C{r}*100')
        s.cell(r, 8, f'=(C${tot}*B{r}/B${tot}-B{r})*(D{r}/B{r})')      # volume: total MWh change at the comparison class rate, in comparison shares
        s.cell(r, 9, f'=(C{r}-C${tot}*B{r}/B${tot})*(D{r}/B{r})')       # mix: shift in class shares at comparison class rates
        s.cell(r, 10, f'=E{r}-C{r}*(D{r}/B{r})')                        # rate: actual vs comparison US cents/kWh on actual MWh
        s.cell(r, 11, f'=SUM(H{r}:J{r})')
        for cc in range(2, 12): s.cell(r, cc).number_format = N2 if cc in (6, 7) else N0
    s.cell(tot, 1, 'Total').font = B
    for cc in (2, 3, 4, 5, 8, 9, 10, 11):
        s.cell(tot, cc, f'=SUM({L(cc)}{first}:{L(cc)}{last})').font = B; s.cell(tot, cc).number_format = N0
    s.cell(tot, 6, f'=D{tot}/B{tot}*100'); s.cell(tot, 7, f'=E{tot}/C{tot}*100')
    for cc in (6, 7): s.cell(tot, cc).number_format = N2
    s.cell(tot + 1, 1, 'Check: energy-line variance - (volume + mix + rate)'); s.cell(tot + 1, 11, f'=D6-K{tot}'); s.cell(tot + 1, 11).fill = Y; s.cell(tot + 1, 11).number_format = '0.000'
    # Step 4: FX
    r0 = tot + 3
    s.cell(r0, 1, 'Step 4 - take FX out of rate').font = B
    s.cell(r0 + 1, 1, 'FX if all revenue were J$-denominated (upper bound) = actual energy line x (comparison FX / actual FX - 1)'); s.cell(r0 + 1, 2, '=B6*(C9/B9-1)')
    s.cell(r0 + 2, 1, 'Share of revenue actually exposed to FX = finance YTD FX effect / YTD upper bound');
    s.cell(r0 + 2, 2, f"={FXFIN}/({FIN[('Energy line (US$000)', 'YTD', 'A')]}*({FIN[('Billing FX rate (J$/US$)', 'YTD', 'B')]}/{FIN[('Billing FX rate (J$/US$)', 'YTD', 'A')]}-1))")
    s.cell(r0 + 3, 1, 'FX effect used (upper bound x exposed share)'); s.cell(r0 + 3, 2, f'=B{r0+1}*B{r0+2}'); s.cell(r0 + 3, 2).fill = G
    s.cell(r0 + 4, 1, 'Within-class yield = rate - FX'); s.cell(r0 + 4, 2, f'=J{tot}-B{r0+3}'); s.cell(r0 + 4, 2).fill = G
    for rr, f in ((r0 + 1, N0), (r0 + 2, '0.0%'), (r0 + 3, N0), (r0 + 4, N0)): s.cell(rr, 2).number_format = f
    # Step 5: customer charge driver
    c0 = r0 + 6
    s.cell(c0, 1, 'Step 5 - customer charge driver (fixed charge, per customer)').font = B
    CA, CB = CUST[(per, 'A')], CUST[(per, kind)]
    mA, mB = CUST[('m', per, 'A')], CUST[('m', per, kind)]
    s.cell(c0 + 1, 1, 'Average customers: actual / comparison / change %'); s.cell(c0 + 1, 2, f'={CA}'); s.cell(c0 + 1, 3, f'={CB}'); s.cell(c0 + 1, 4, f'=B{c0+1}/C{c0+1}-1')
    s.cell(c0 + 2, 1, 'Customer charge US$ per customer per month: actual / comparison / change %'); s.cell(c0 + 2, 2, f'=B7*1000/B{c0+1}/{mA}'); s.cell(c0 + 2, 3, f'=C7*1000/C{c0+1}/{mB}'); s.cell(c0 + 2, 4, f'=B{c0+2}/C{c0+2}-1')
    s.cell(c0 + 3, 1, 'More customers = (actual customers - comparison customers) x comparison customer charge per customer'); s.cell(c0 + 3, 2, f'=(B{c0+1}-C{c0+1})/C{c0+1}*C7'); s.cell(c0 + 3, 2).fill = G
    s.cell(c0 + 4, 1, 'Charge per customer = customer charge variance - more customers'); s.cell(c0 + 4, 2, f'=D7-B{c0+3}'); s.cell(c0 + 4, 2).fill = G
    for rr in (c0 + 1,): 
        for cc in (2, 3): s.cell(rr, cc).number_format = N0
    for rr in (c0 + 2,):
        for cc in (2, 3): s.cell(rr, cc).number_format = N2
    for rr in (c0 + 1, c0 + 2): s.cell(rr, 4).number_format = PCT
    for rr in (c0 + 3, c0 + 4): s.cell(rr, 2).number_format = N0
    # Step 6: walk
    w0 = c0 + 6
    s.cell(w0, 1, 'Step 6 - the walk').font = B
    walk = [('Customer charge - more customers', f'=B{c0+3}'), ('Customer charge - charge per customer', f'=B{c0+4}'),
            ('Energy line - volume', f'=H{tot}'), ('Energy line - class mix (between classes)', f'=I{tot}'),
            ('Energy line - FX', f'=B{r0+3}'), ('Energy line - within-class yield', f'=B{r0+4}')]
    for k, (lab, f) in enumerate(walk, 1):
        s.cell(w0 + k, 1, lab); s.cell(w0 + k, 2, f); s.cell(w0 + k, 2).number_format = N0
    t = w0 + len(walk) + 1
    s.cell(t, 1, 'Non-fuel revenue variance').font = B; s.cell(t, 2, f'=SUM(B{w0+1}:B{t-1})').font = B; s.cell(t, 2).number_format = N0; s.cell(t, 2).fill = Y
    s.cell(t + 1, 1, 'Check against finance (D10 variance)'); s.cell(t + 1, 2, f'=D10-B{t}'); s.cell(t + 1, 2).number_format = '0.000'
    s.column_dimensions['A'].width = 78
    for cc in range(2, 12): s.column_dimensions[L(cc)].width = 15
    return s
calc_sheet('Sep vs budget', 'SEP', 'B', 'September 2026 vs budget - non-fuel revenue walk')
calc_sheet('Sep vs prior year', 'SEP', 'P', 'September 2026 vs September 2025 - non-fuel revenue walk')
calc_sheet('YTD vs budget', 'YTD', 'B', 'January-September 2026 vs budget - non-fuel revenue walk')
calc_sheet('YTD vs prior year', 'YTD', 'P', 'January-September 2026 vs prior year - non-fuel revenue walk')
# =================== Explain ===================
se = wb.create_sheet('How to read', 0)
lines = [
 ('Non-fuel revenue walk, September 2026', True),
 ('Non-fuel revenue = Energy line (energy + demand + F/X) + Customer charge, from the finance Revenues sheet. The walk explains the variance in six pieces:', False),
 ('Customer charge: the fixed monthly charge per customer. It is its own driver, not tied to kWh: part comes from having more customers than the comparison, the rest from a different charge per customer (customer mix between classes and any indexation). Customer counts: platform for actual and prior year; the budget file holds a flat count.', False),
 ('Volume: total normalized sales (MWh) above or below the comparison, valued at the comparison average rate. Only the change in how much was sold.', False),
 ('Class mix: the shift of those MWh between rate classes. Classes earn different amounts per kWh (RT10 earns the most, RT50 the least), so selling relatively more RT10 raises the average even if nothing is repriced. It is between-class.', False),
 ('FX: the change in US$ revenue from J$ billing at a different exchange rate. Estimated from the billing FX rates, scaled to the share of revenue finance shows as FX-exposed (their YTD FX bar of US$89K).', False),
 ('Within-class yield: what is left of the per-kWh change after FX, inside each class: customers moving up the residential consumption blocks, demand (kVA) billing, indexation and billing/accrual timing. There has been no base-rate increase; this is not a price change.', False),
 ('Sheets: Inputs holds every source number (blue). Each comparison sheet is formulas only, so clicking a cell shows how it was built. The yellow check cells must read 0.', False),
 ('Class detail is allocated: the financials have no class split of normalized sales or non-fuel revenue, so billed class data is scaled to the finance totals (Step 2). Class mix and within-class yield are therefore estimates; the totals tie to finance.', False),
]
for i, (t, b) in enumerate(lines, 1):
    c = se.cell(i, 1, t); c.alignment = Alignment(wrap_text=True, vertical='top'); c.font = Font(bold=b, size=13 if b else 11); se.row_dimensions[i].height = 24 if b else 50
se.column_dimensions['A'].width = 150
out = r'C:\Projects\Sales_Platform\JPS_Sep2026_NonFuel_Walk_v2.xlsx'
wb.save(out); print('saved', out)
