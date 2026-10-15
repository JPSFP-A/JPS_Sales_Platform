# -*- coding: utf-8 -*-
# September 2026 component breakdown vs budget / forecast / prior year, and volume-mix-rate movement (Sept and YTD).
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
import _pvm_sep as P

CL = ['RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']
FX = {'SEP': dict(cust=15125e3, demand=33795e3, energy=92594e3), 'YTD': dict(cust=116815e3, demand=260552e3, energy=638669e3)}
FCST = {'SEP': dict(zip(CL, [110.4, 59.7, 65.8, 28.1, 3.3, 18.3])), 'YTD': dict(zip(CL, [873.7, 475.9, 564.7, 256.5, 27.2, 213.6]))}
H = Font(bold=True, color='FFFFFF'); HF = PatternFill('solid', fgColor='1F3864'); B = Font(bold=True)
Y = PatternFill('solid', fgColor='FFF2CC'); G = PatternFill('solid', fgColor='E2EFDA')
M = '#,##0.0;[Red]-#,##0.0'; M0 = '#,##0;[Red]-#,##0'; PCT = '0.0%;[Red]-0.0%'

def bud_with_fx(per):
    """Budget non-fuel by class, with the budget F/X adjustment lines allocated to classes pro rata within each component."""
    b = P.budget(per); out = {}
    tot = {k: sum(b[c][k] for c in b) for k in ('cust', 'energy', 'demand')}
    for c, v in b.items():
        cu = v['cust'] * (1 + FX[per]['cust'] / tot['cust']); en = v['energy'] * (1 + FX[per]['energy'] / tot['energy'])
        de = v['demand'] * (1 + FX[per]['demand'] / tot['demand']) if tot['demand'] else 0.0
        out[c] = dict(kwh=v['kwh'], cust=cu, energy=en, demand=de, nf=cu + en + de)
    return out

def pvm_detail(A, Bs):
    At, Bt = sum(a['kwh'] for a in A.values()), sum(b['kwh'] for b in Bs.values())
    Bnt = sum(b['nf'] for b in Bs.values()); avgB = Bnt / Bt
    rows = {}
    for c in A:
        br = Bs[c]['nf'] / Bs[c]['kwh']; s = Bs[c]['kwh'] / Bt
        rows[c] = dict(B_kwh=Bs[c]['kwh'], A_kwh=A[c]['kwh'], B_rate=br, A_rate=A[c]['nf'] / A[c]['kwh'],
                       vol=(At * s - Bs[c]['kwh']) * br, mix=(A[c]['kwh'] - At * s) * br, rate=A[c]['nf'] - A[c]['kwh'] * br,
                       B_nf=Bs[c]['nf'], A_nf=A[c]['nf'])
    return rows, At, Bt, Bnt, sum(a['nf'] for a in A.values())

wb = Workbook()
# =================== Summary ===================
s0 = wb.active; s0.title = 'Summary'
s0['A1'] = 'September 2026 - why volume is down and revenue is up'; s0['A1'].font = Font(bold=True, size=13)
s0['A2'] = 'Deck figures in US$M (slide 5). September actuals are the finance Earnings Sheet (J$, by class); budget and prior year come from the Sales Platform.'
for i, h in enumerate(['', 'September vs budget', 'YTD vs budget'], 1):
    c = s0.cell(4, i, h); c.font = H; c.fill = HF
def bridge(per, kind, fx=True):
    a26 = P.actual(2026, per)
    base = (bud_with_fx(per) if fx else P.budget(per)) if kind == 'b' else P.actual(2025, per)
    det, At, Bt, Bnt, Ant = pvm_detail(a26, base)
    return dict(At=At, Bt=Bt, Ant=Ant, Bnt=Bnt, **{k: sum(d[k] for d in det.values()) for k in ('vol', 'mix', 'rate')})
SB, SP_, YB, YBx, YP = bridge('SEP', 'b'), bridge('SEP', 'p'), bridge('YTD', 'b'), bridge('YTD', 'b', fx=False), bridge('YTD', 'p')
g1 = lambda x: f'{x / 1e6:+,.1f}'
pc1 = lambda a, b: f'{(a / b - 1) * 100:+.1f}%'
jm = lambda x: f'{x / 1e6:+,.0f}'
rows = [
 ('Sales volume, GWh (Earnings Sheet for September)', f"{g1(SB['At'] - SB['Bt'])} ({pc1(SB['At'], SB['Bt'])})", f"{g1(YB['At'] - YB['Bt'])} ({pc1(YB['At'], YB['Bt'])}) per budget file; +35.2 (+1.5%) per platform budget"),
 ('Total revenue, US$M (deck)', '+6.4 (+6.5%)  106.1 vs 99.7', '+6.0 (+0.7%)  816.8 vs 810.8'),
 ('  of which fuel surplus/(penalty)', '+4.8  (force majeure heat-rate reversal)', '+2.3'),
 ('  of which non-fuel revenue', '+1.2 (+3.9%)', '+7.1 (+2.8%)'),
 ('  other (other operating revenue etc.)', '+0.4', '-3.4'),
]
for r, row in enumerate(rows, 5):
    for c, v in enumerate(row, 1): s0.cell(r, c, v)
s0.cell(11, 1, 'Reading').font = B
notes = [
 'Volume is not what is driving revenue. In September about three quarters of the revenue beat (US$4.8M of US$6.4M) is the fuel surplus line, a force majeure heat-rate reversal that has nothing to do with kWh.',
 f"The non-fuel beat is price and mix, not volume. Earnings Sheet components against budget (J$M): volume {jm(SB['vol'])}, mix {jm(SB['mix'])}, rate {jm(SB['rate'])}, net {jm(SB['Ant'] - SB['Bnt'])} ({pc1(SB['Ant'], SB['Bnt'])}). See Vol-Mix-Rate.",
 f"Against prior year the same pattern holds: September volume {pc1(SP_['At'], SP_['Bt'])} but non-fuel revenue {pc1(SP_['Ant'], SP_['Bnt'])}: volume {jm(SP_['vol'])}, mix {jm(SP_['mix'])}, rate {jm(SP_['rate'])}. Year to date volume {pc1(YP['At'], YP['Bt'])} costs J${abs(YP['vol']) / 1e6:,.0f}M of non-fuel revenue and mix and rate give back J${(YP['mix'] + YP['rate']) / 1e6:,.0f}M, so non-fuel revenue falls {abs((YP['Ant'] / YP['Bnt'] - 1) * 100):.1f}%.",
 f"Year to date against budget the answer depends on the budget F/X adjustment lines (J$1,016M): without them non-fuel is {jm(YBx['Ant'] - YBx['Bnt'])}M ({pc1(YBx['Ant'], YBx['Bnt'])}); with them {jm(YB['Ant'] - YB['Bnt'])}M ({pc1(YB['Ant'], YB['Bnt'])}). The deck shows +2.8%, so confirm how finance treats those lines. See Basis.",
 'Mix: residential and RT20 (the highest non-fuel yield) are above plan while RT50 and RT70 (lowest yield) are well below, so each kWh sold earns more on average. Rate: tariff and FX movements.',
]
for i, n in enumerate(notes):
    c = s0.cell(12 + i, 1, n); c.alignment = Alignment(wrap_text=True, vertical='top'); s0.merge_cells(start_row=12 + i, start_column=1, end_row=12 + i, end_column=3); s0.row_dimensions[12 + i].height = 52
s0.column_dimensions['A'].width = 44; s0.column_dimensions['B'].width = 42; s0.column_dimensions['C'].width = 62

# =================== Components ===================
s1 = wb.create_sheet('Components')
s1['A1'] = 'Component breakdown, J$M (net of GCT) and volume in GWh - all classes'; s1['A1'].font = Font(bold=True, size=13)
r = 3
for per, lab in (('SEP', 'September 2026'), ('YTD', 'January - September 2026')):
    a26, a25, bud = P.actual(2026, per), P.actual(2025, per), bud_with_fx(per)
    sm = lambda d, k: sum(d[c].get(k, 0.0) for c in d)
    s1.cell(r, 1, lab).font = Font(bold=True, size=12); r += 1
    for i, h in enumerate(['Component', 'Actual', 'Budget', 'Var', 'Var %', 'Prior year', 'Var', 'Var %', 'Submitted forecast (volume)', 'Var'], 1):
        c = s1.cell(r, i, h); c.font = H; c.fill = HF; c.alignment = Alignment(wrap_text=True, horizontal='center')
    r += 1; start = r
    fc = sum(FCST[per].values())
    lines = [
     ('Volume (GWh)', sm(a26, 'kwh') / 1e6, sm(bud, 'kwh') / 1e6, sm(a25, 'kwh') / 1e6, fc),
     ('Customer charge', sm(a26, 'cust') / 1e6 + 0, sm(bud, 'cust') / 1e6, sm(a25, 'cust') / 1e6, None),
     ('Energy charge', sm(a26, 'energy') / 1e6, sm(bud, 'energy') / 1e6, sm(a25, 'energy') / 1e6, None),
     ('Demand charge', sm(a26, 'demand') / 1e6, sm(bud, 'demand') / 1e6, sm(a25, 'demand') / 1e6, None),
     ('Prepaid non-fuel (estimated at the postpaid RT10/RT20 rate)', sum(a26[c]['nf'] - a26[c]['cust'] - a26[c]['energy'] for c in ('RT10', 'RT20')) / 1e6, 0.0,
        sum(a25[c]['nf'] - a25[c]['cust'] - a25[c]['energy'] for c in ('RT10', 'RT20')) / 1e6, None),
    ]
    for lab2, a, b, p, f in lines:
        s1.cell(r, 1, lab2); s1.cell(r, 2, a); s1.cell(r, 3, b if lab2 != 'Prepaid non-fuel (estimated at the postpaid RT10/RT20 rate)' else None); s1.cell(r, 6, p)
        s1.cell(r, 4, f'=B{r}-C{r}' if b is not None and not lab2.startswith('Prepaid') else None); s1.cell(r, 5, f'=IF(C{r}=0,"",D{r}/C{r})' if not lab2.startswith('Prepaid') else None)
        if lab2.startswith('Prepaid') and per == 'SEP':
            s1.cell(r, 1, 'Prepaid non-fuel (prior-year estimate; in September it is inside the class lines above)')
        else:
            s1.cell(r, 7, f'=B{r}-F{r}'); s1.cell(r, 8, f'=IF(F{r}=0,"",G{r}/F{r})')
        if f is not None: s1.cell(r, 9, f); s1.cell(r, 10, f'=B{r}-I{r}')
        r += 1
    nf_r = r
    s1.cell(r, 1, 'Non-fuel revenue').font = B
    s1.cell(r, 2, f'=SUM(B{start+1}:B{start+4})').font = B; s1.cell(r, 3, f'=SUM(C{start+1}:C{start+3})').font = B; s1.cell(r, 4, f'=B{r}-C{r}'); s1.cell(r, 5, f'=D{r}/C{r}')
    s1.cell(r, 6, f'=SUM(F{start+1}:F{start+4})'); s1.cell(r, 7, f'=B{r}-F{r}'); s1.cell(r, 8, f'=G{r}/F{r}'); r += 1
    for lab2, k in (('Fuel', 'fuel'), ('For exchange (Earnings Sheet, September only)', 'fex'), ('IPP (purchased power)', 'ipp')):
        s1.cell(r, 1, lab2); s1.cell(r, 2, sm(a26, k) / 1e6); s1.cell(r, 3, 'n/a')
        if k != 'fex': s1.cell(r, 6, sm(a25, k) / 1e6); s1.cell(r, 7, f'=B{r}-F{r}'); s1.cell(r, 8, f'=G{r}/F{r}')
        r += 1
    s1.cell(r, 1, 'Net revenue, all classes (incl. prepaid; Earnings Sheet total for September)').font = B; s1.cell(r, 2, sm(a26, 'rev') / 1e6).font = B; s1.cell(r, 6, sm(a25, 'rev') / 1e6); s1.cell(r, 7, f'=B{r}-F{r}'); s1.cell(r, 8, f'=G{r}/F{r}'); s1.cell(r, 3, 'n/a'); r += 1
    s1.cell(r, 1, 'Net revenue per kWh (J$)'); s1.cell(r, 2, f'=B{r-1}/B{start}'); s1.cell(r, 6, f'=F{r-1}/F{start}'); s1.cell(r, 7, f'=B{r}-F{r}'); s1.cell(r, 8, f'=G{r}/F{r}'); r += 1
    for rr in range(start, r):
        for cc in (2, 3, 4, 6, 7, 9, 10): s1.cell(rr, cc).number_format = M
        for cc in (5, 8): s1.cell(rr, cc).number_format = PCT
    s1.cell(r, 1, 'Budget non-fuel includes the budget F/X adjustment lines (allocated to classes pro rata). Budget fuel and IPP are not broken out in the budget file, and the submitted forecast carries volume only.').alignment = Alignment(wrap_text=True)
    s1.merge_cells(start_row=r, start_column=1, end_row=r, end_column=10); s1.row_dimensions[r].height = 30
    r += 2
for c, w in zip('ABCDEFGHIJ', (52, 12, 12, 12, 9, 12, 12, 9, 16, 10)): s1.column_dimensions[c].width = w

# =================== Volume - Mix - Rate ===================
s2 = wb.create_sheet('Vol-Mix-Rate')
s2['A1'] = 'Non-fuel revenue movement: volume, mix and rate (J$M)'; s2['A1'].font = Font(bold=True, size=13)
s2['A2'] = ('Volume = change in total GWh at the base average non-fuel rate. Mix = shift of GWh between rate classes at base rates. '
            'Rate = actual vs base non-fuel J$/kWh within each class (tariff, FX, billing-determinant effects). The three add to the total movement.')
s2.merge_cells('A2:K2'); s2['A2'].alignment = Alignment(wrap_text=True); s2.row_dimensions[2].height = 32
r = 4; RESULT = {}
for per, lab in (('SEP', 'September 2026'), ('YTD', 'January - September 2026')):
    a26 = P.actual(2026, per)
    for kind, base in (('Budget', bud_with_fx(per)), ('Prior year', P.actual(2025, per))):
        if kind == 'Budget' and per == 'YTD':
            # YTD volumes must come from the same budget file as the revenue components
            pass
        det, At, Bt, Bnt, Ant = pvm_detail(a26, base)
        vol, mix, rate = (sum(d[k] for d in det.values()) for k in ('vol', 'mix', 'rate'))
        RESULT[(per, kind)] = (At, Bt, Ant, Bnt, vol, mix, rate)
        s2.cell(r, 1, f'{lab} vs {kind.lower()}').font = Font(bold=True, size=12); r += 1
        for i, h in enumerate(['Class', f'{kind} GWh', 'Actual GWh', f'{kind} J$/kWh', 'Actual J$/kWh', f'{kind} non-fuel', 'Actual non-fuel', 'Volume', 'Mix', 'Rate', 'Total'], 1):
            c = s2.cell(r, i, h); c.font = H; c.fill = HF; c.alignment = Alignment(wrap_text=True, horizontal='center')
        r += 1; first = r
        for c_, d in det.items():
            vals = [c_, d['B_kwh'] / 1e6, d['A_kwh'] / 1e6, d['B_rate'], d['A_rate'], d['B_nf'] / 1e6, d['A_nf'] / 1e6, d['vol'] / 1e6, d['mix'] / 1e6, d['rate'] / 1e6]
            for i, v in enumerate(vals, 1): s2.cell(r, i, v)
            s2.cell(r, 11, f'=SUM(H{r}:J{r})')
            for cc in range(2, 12): s2.cell(r, cc).number_format = '#,##0.00' if cc in (4, 5) else M
            r += 1
        s2.cell(r, 1, 'Total').font = B
        for cc in (2, 3, 6, 7, 8, 9, 10, 11):
            s2.cell(r, cc, f'=SUM({chr(64+cc)}{first}:{chr(64+cc)}{r-1})').font = B; s2.cell(r, cc).number_format = M
        s2.cell(r, 4, f'=F{r}/B{r}'); s2.cell(r, 5, f'=G{r}/C{r}')
        for cc in (4, 5): s2.cell(r, cc).number_format = '#,##0.00'
        r += 1
        s2.cell(r, 1, 'Check: movement - (volume + mix + rate)'); s2.cell(r, 11, f'=(G{r-1}-F{r-1})-K{r-1}'); s2.cell(r, 11).fill = Y; s2.cell(r, 11).number_format = '0.000'
        r += 2
s2.column_dimensions['A'].width = 34
for c in 'BCDEFGHIJK': s2.column_dimensions[c].width = 13
# =================== Basis ===================
s3 = wb.create_sheet('Basis')
basis = [
 'Actuals: September 2026 is the finance Earnings Sheet (volume and J$ components by class, including prepaid and not-billed rows, 294,724.6 MWh). Year to date is the platform (customer billed = 1) for January-August plus the Earnings Sheet for September. Prior year is the platform (customer billed = 1), net of GCT.',
 'Prepaid carries revenue only (no component split). Its non-fuel is estimated at the postpaid RT10 / RT20 non-fuel rate, about 1% of non-fuel revenue.',
 'Budget: budget file components (customer, energy, demand by class, J$000) plus the budget F/X adjustment lines allocated to classes pro rata. Budget volume for YTD comes from the same file (2,402.0 GWh Jan-Sep).',
 'The Platform\'s own YTD budget volume (2,393.7 GWh) sets January and February equal to actuals, so it differs from the budget file by 8.3 GWh. The deck\'s year-to-date variance to budget (+35.3 GWh) uses the Platform figure; on the budget file it is +27.0 GWh. Confirm which the deck should use.',
 "YTD vs budget on this sheet is basis-sensitive: finance's actual non-fuel (US$260.8M) is about 3.7% above the platform billing components, which flips the sign of the rate effect. The September bridges and the vs-prior-year bridges do not rely on that tie.",
 'Submitted forecast: version 3, submitted 19 Aug 2026 (actuals through July, forecast thereafter). It holds volume by class only; there is no revenue forecast.',
 'Deck US$ figures (slide 5) are finance\'s and are not reproduced here; the J$ billing-component view is directional and ties to the deck within about 1% for September and about 3-4% year to date.',
]
for i, t in enumerate(basis, 1):
    s3.cell(i, 1, t).alignment = Alignment(wrap_text=True, vertical='top'); s3.row_dimensions[i].height = 48
s3.column_dimensions['A'].width = 150

# =================== Finance basis (JPSCo Financials 09-26, Revenues sheet, US$'000) ===================
import openpyxl as _ox
_fw = _ox.load_workbook(r'C:\Users\jwilson\AppData\Local\Temp\JPSCo Financials_09-26 (1).xlsx', read_only=True, data_only=True)['Revenues']
_R = {i: r for i, r in enumerate(_fw.iter_rows(values_only=True), 1)}
fv = lambda row, col: float(_R[row][col - 1])
# columns: month actual 3, month budget 6, month prior year 23; YTD actual 12, YTD budget 13, prior YTD 20
FIN = {'SEP': dict(act=3, bud=6, py=23), 'YTD': dict(act=12, bud=13, py=20)}
FXR = {'SEP': fv(32, 3), 'YTD': fv(32, 12)}
s4 = wb.create_sheet('Finance basis', 1)
s4['A1'] = "Non-fuel revenue on the finance numbers (JPSCo Financials 09-26, Revenues sheet, US$'000)"; s4['A1'].font = Font(bold=True, size=13)
s4['A2'] = ("Non-fuel = Energy (which carries demand and F/X) + Customer charge. Volume is finance's Sales (MWh) from the same sheet. "
            "Volume effect = change in MWh x base US cents/kWh. Mix is estimated from class volumes (Earnings Sheet vs budget file, J$ at the actual billing FX rate); rate is the remainder.")
s4.merge_cells('A2:G2'); s4['A2'].alignment = Alignment(wrap_text=True, vertical='top'); s4.row_dimensions[2].height = 44
r = 4; FINRES = {}
for per, plab in (('SEP', 'September 2026'), ('YTD', 'January - September 2026')):
    for kind, kcol in (('Budget', 'bud'), ('Prior year', 'py')):
        c = FIN[per]
        en_a, cu_a, en_b, cu_b = fv(13, c['act']), fv(14, c['act']), fv(13, c[kcol]), fv(14, c[kcol])
        mw_a, mw_b = fv(46, c['act']), fv(46, c[kcol])
        mix_j = RESULT[(per, 'Budget' if kind == 'Budget' else 'Prior year')][5]
        mix_usd = mix_j / FXR[per] / 1e3                     # J$ -> US$'000
        s4.cell(r, 1, f'{plab} vs {kind.lower()}').font = Font(bold=True, size=12); r += 1
        for i, h in enumerate(['', 'Actual', kind, 'Variance', 'Var %'], 1):
            cc = s4.cell(r, i, h); cc.font = H; cc.fill = HF; cc.alignment = Alignment(horizontal='center')
        r += 1; r0 = r
        for lab, a, b in (('Energy (incl. demand and F/X)', en_a, en_b), ('Customer charge', cu_a, cu_b)):
            s4.cell(r, 1, lab); s4.cell(r, 2, a); s4.cell(r, 3, b); s4.cell(r, 4, f'=B{r}-C{r}'); s4.cell(r, 5, f'=D{r}/C{r}'); r += 1
        s4.cell(r, 1, 'Non-fuel revenue').font = B
        for cc in (2, 3): s4.cell(r, cc, f'=SUM({chr(64+cc)}{r0}:{chr(64+cc)}{r-1})').font = B
        s4.cell(r, 4, f'=B{r}-C{r}').font = B; s4.cell(r, 5, f'=D{r}/C{r}'); nf = r; r += 1
        s4.cell(r, 1, 'Sales (MWh), finance'); s4.cell(r, 2, mw_a); s4.cell(r, 3, mw_b); s4.cell(r, 4, f'=B{r}-C{r}'); s4.cell(r, 5, f'=D{r}/C{r}'); mw = r; r += 1
        s4.cell(r, 1, 'Non-fuel US cents/kWh'); s4.cell(r, 2, f'=B{nf}/B{mw}*100'); s4.cell(r, 3, f'=C{nf}/C{mw}*100'); s4.cell(r, 4, f'=B{r}-C{r}'); s4.cell(r, 5, f'=D{r}/C{r}'); rate_r = r; r += 1
        for rr in range(r0, r):
            for cc in (2, 3, 4): s4.cell(rr, cc).number_format = '#,##0.00' if rr == rate_r else '#,##0;[Red]-#,##0'
            s4.cell(rr, 5).number_format = PCT
        s4.cell(r, 1, "Bridge (US$'000)").font = B; r += 1
        s4.cell(r, 1, 'Volume'); s4.cell(r, 4, f'=D{mw}*C{rate_r}/100'); vol_r = r; r += 1
        s4.cell(r, 1, 'Mix (estimated from class volumes)'); s4.cell(r, 4, mix_usd); mix_r = r; r += 1
        s4.cell(r, 1, 'Rate and other (remainder)'); s4.cell(r, 4, f'=D{nf}-D{vol_r}-D{mix_r}'); r += 1
        s4.cell(r, 1, 'Total movement').font = B; s4.cell(r, 4, f'=SUM(D{vol_r}:D{r-1})').font = B; s4.cell(r, 4).fill = Y
        for rr in range(vol_r, r + 1): s4.cell(rr, 4).number_format = '#,##0;[Red]-#,##0'
        FINRES[(per, kind)] = (en_a, cu_a, en_b, cu_b, mw_a, mw_b, mix_usd)
        r += 3
s4.cell(r, 1, 'Finance reports Sales (MWh) on a normalized basis (September 300,194 MWh, against 294,725 MWh billed on the Earnings Sheet), so volume here differs from the billed volumes used on the other sheets.').alignment = Alignment(wrap_text=True)
s4.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5); s4.row_dimensions[r].height = 32
s4.column_dimensions['A'].width = 44
for cc in 'BCDE': s4.column_dimensions[cc].width = 16
# =================== Finance mix by class (normalized sales) ===================
s5 = wb.create_sheet('Finance mix by class', 2)
s5['A1'] = 'Volume, mix and rate by class on the finance totals (normalized sales, non-fuel US$000)'; s5['A1'].font = Font(bold=True, size=13)
s5['A2'] = ("The financials carry normalized Sales (MWh) and non-fuel revenue for the whole system only. Class detail is allocated: each class's billed volume and non-fuel revenue "
            "(Earnings Sheet / platform / budget file) is scaled by one factor so the class totals equal the finance totals. The class mix therefore comes from the billed data; "
            "the totals, and so the volume effect, come from finance.")
s5.merge_cells('A2:K2'); s5['A2'].alignment = Alignment(wrap_text=True, vertical='top'); s5.row_dimensions[2].height = 58
r = 4; MIXRES = {}
for per, plab in (('SEP', 'September 2026'), ('YTD', 'January - September 2026')):
    for kind, kcol in (('Budget', 'bud'), ('Prior year', 'py')):
        c = FIN[per]
        A = P.actual(2026, per); Bs = bud_with_fx(per) if kind == 'Budget' else P.actual(2025, per)
        fa_nf, fb_nf = fv(13, c['act']) + fv(14, c['act']), fv(13, c[kcol]) + fv(14, c[kcol])
        fa_mw, fb_mw = fv(46, c['act']), fv(46, c[kcol])
        sA_k, sB_k = fa_mw / (sum(a['kwh'] for a in A.values()) / 1e3), fb_mw / (sum(b['kwh'] for b in Bs.values()) / 1e3)
        sA_r, sB_r = fa_nf / (sum(a['nf'] for a in A.values()) / 1e3), fb_nf / (sum(b['nf'] for b in Bs.values()) / 1e3)
        a2 = {k: dict(kwh=v['kwh'] / 1e3 * sA_k, nf=v['nf'] / 1e3 * sA_r) for k, v in A.items()}      # MWh, US$000
        b2 = {k: dict(kwh=v['kwh'] / 1e3 * sB_k, nf=v['nf'] / 1e3 * sB_r) for k, v in Bs.items()}
        det, At, Bt, Bnt, Ant = pvm_detail(a2, b2)
        s5.cell(r, 1, f'{plab} vs {kind.lower()}').font = Font(bold=True, size=12); r += 1
        for i, h in enumerate(['Class', f'{kind} MWh', 'Actual MWh', f'{kind} US cents/kWh', 'Actual US cents/kWh', f'{kind} non-fuel', 'Actual non-fuel', 'Volume', 'Mix', 'Rate', 'Total'], 1):
            cc = s5.cell(r, i, h); cc.font = H; cc.fill = HF; cc.alignment = Alignment(wrap_text=True, horizontal='center')
        r += 1; first = r
        for k, d in det.items():
            vals = [k, d['B_kwh'], d['A_kwh'], d['B_rate'] * 100, d['A_rate'] * 100, d['B_nf'], d['A_nf'], d['vol'], d['mix'], d['rate']]
            for i, v in enumerate(vals, 1): s5.cell(r, i, v)
            s5.cell(r, 11, f'=SUM(H{r}:J{r})')
            for cc in range(2, 12): s5.cell(r, cc).number_format = '0.00' if cc in (4, 5) else '#,##0;[Red]-#,##0'
            r += 1
        s5.cell(r, 1, 'Total').font = B
        for cc in (2, 3, 6, 7, 8, 9, 10, 11):
            s5.cell(r, cc, f'=SUM({chr(64+cc)}{first}:{chr(64+cc)}{r-1})').font = B; s5.cell(r, cc).number_format = '#,##0;[Red]-#,##0'
        s5.cell(r, 4, f'=F{r}/B{r}*100'); s5.cell(r, 5, f'=G{r}/C{r}*100')
        for cc in (4, 5): s5.cell(r, cc).number_format = '0.00'
        r += 1
        s5.cell(r, 1, 'Check: finance variance - (volume + mix + rate)'); s5.cell(r, 11, f'=({fa_nf}-{fb_nf})-K{r-1}'); s5.cell(r, 11).fill = Y; s5.cell(r, 11).number_format = '0.000'
        MIXRES[(per, kind)] = (At, Bt, Ant, Bnt, sum(d['vol'] for d in det.values()), sum(d['mix'] for d in det.values()), sum(d['rate'] for d in det.values()), det)
        r += 2
s5.column_dimensions['A'].width = 34
for cc in 'BCDEFGHIJK': s5.column_dimensions[cc].width = 14
# =================== Non-fuel focus: drop the billed-basis / fuel sheets, rewrite Summary and Basis ===================
for nm in ('Components', 'Vol-Mix-Rate', 'Summary', 'Basis'): wb.remove(wb[nm])
sm0 = wb.create_sheet('Summary', 0)
sm0['A1'] = 'September 2026 non-fuel revenue: volume, mix and rate (finance numbers, normalized sales)'; sm0['A1'].font = Font(bold=True, size=13)
sm0['A2'] = "US$'000. Non-fuel = Energy (incl. demand and F/X) + Customer charge, from JPSCo Financials 09-26. Volume = normalized Sales (MWh)."
for i, h in enumerate(['', 'Sept vs budget', 'Sept vs prior year', 'YTD vs budget', 'YTD vs prior year'], 1):
    cc = sm0.cell(4, i, h); cc.font = H; cc.fill = HF; cc.alignment = Alignment(horizontal='center', wrap_text=True)
order = [('SEP', 'Budget'), ('SEP', 'Prior year'), ('YTD', 'Budget'), ('YTD', 'Prior year')]
labels = [('Normalized sales, MWh (variance)', lambda v: v[0] - v[1], '#,##0;[Red]-#,##0'), ('  % change', lambda v: v[0] / v[1] - 1, PCT),
          ('Non-fuel revenue, actual', lambda v: v[2], '#,##0'), ('Non-fuel revenue, comparison', lambda v: v[3], '#,##0'),
          ('Variance', lambda v: v[2] - v[3], '#,##0;[Red]-#,##0'), ('  % change', lambda v: v[2] / v[3] - 1, PCT),
          ('  Volume', lambda v: v[4], '#,##0;[Red]-#,##0'), ('  Mix', lambda v: v[5], '#,##0;[Red]-#,##0'), ('  Rate and other', lambda v: v[6], '#,##0;[Red]-#,##0')]
for ri, (lab, fn, fmt) in enumerate(labels, 5):
    sm0.cell(ri, 1, lab)
    for ci, key in enumerate(order, 2):
        c_ = sm0.cell(ri, ci, fn(MIXRES[key])); c_.number_format = fmt
        if lab.strip() in ('Variance',): c_.font = B
sm0.cell(5 + len(labels) + 1, 1, 'Reading').font = B
def top(det, k, n=2, neg=False):
    xs = sorted(det.items(), key=lambda kv: kv[1][k], reverse=neg)[:n]
    return ', '.join(f"{c} {d[k]:+,.0f}" for c, d in xs)
sb, sp_, yb, yp = (MIXRES[k] for k in order)
reads = [
 f"September vs budget: volume {sb[4]:+,.0f} (sales {sb[0] / sb[1] - 1:+.1%}), mix {sb[5]:+,.0f}, rate and other {sb[6]:+,.0f}; the {sb[2] - sb[3]:+,.0f} (+{(sb[2] / sb[3] - 1) * 100:.1f}%) beat is price and mix, not volume. Mix is carried by {top(sb[7], 'mix', 2, True)}, against {top(sb[7], 'mix', 3, False)}.",
 f"September vs prior year: finance sales are {sp_[0] / sp_[1] - 1:+.1%} (normalized), so volume adds {sp_[4]:+,.0f} and mix {sp_[5]:+,.0f}. On billed volume September is down 2.3%; the normalization adds about 5.5 GWh in September.",
 f"Year to date vs budget: {yb[2] - yb[3]:+,.0f} (+{(yb[2] / yb[3] - 1) * 100:.1f}%), of which volume {yb[4]:+,.0f} ({yb[0] / yb[1] - 1:+.1%} sales), mix {yb[5]:+,.0f}, rate and other {yb[6]:+,.0f}. Volume is the main support year to date; the September month is where it turns.",
 f"Year to date vs prior year: sales {yp[0] / yp[1] - 1:+.1%} take {yp[4]:+,.0f} of non-fuel revenue; mix ({yp[5]:+,.0f}) and rate ({yp[6]:+,.0f}) give back {yp[5] + yp[6]:,.0f}, so non-fuel revenue is {yp[2] / yp[3] - 1:+.1%}.",
]
for i, t in enumerate(reads):
    rr = 5 + len(labels) + 2 + i
    sm0.cell(rr, 1, t).alignment = Alignment(wrap_text=True, vertical='top'); sm0.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=5); sm0.row_dimensions[rr].height = 58
sm0.column_dimensions['A'].width = 38
for cc in 'BCDE': sm0.column_dimensions[cc].width = 20
bs = wb.create_sheet('Basis')
for i, t in enumerate([
    "Totals: JPSCo Financials 09-26, Revenues sheet. Non-fuel = Energy + Customer charge (US$'000); Sales (MWh) is finance's normalized sales. The Energy line carries demand and F/X.",
    "Class detail: the financials have no class split of normalized sales or non-fuel revenue. Each class's billed volume and non-fuel revenue (September: Earnings Sheet; year to date: platform January-August plus the Earnings Sheet; budget: budget file with its F/X adjustment lines allocated pro rata; prior year: platform) is scaled by one factor so the class totals equal the finance totals.",
    "So the class mix (shares) comes from billed data and the totals come from finance. Mix and rate by class are therefore estimates; the system volume effect and the total variance tie to the financials.",
    "Volume effect = change in total MWh at the base average non-fuel rate. Mix = shift of MWh between classes at base class rates. Rate = actual vs base US cents/kWh within each class (tariff, F/X, demand and billing effects).",
    "Finance's normalized sales differ from billed sales (September 300,194 MWh normalized against 294,725 MWh billed, Earnings Sheet).",
], 1):
    bs.cell(i, 1, t).alignment = Alignment(wrap_text=True, vertical='top'); bs.row_dimensions[i].height = 48
bs.column_dimensions['A'].width = 140
wb._sheets = [wb['Summary'], wb['Finance mix by class'], wb['Finance basis'], wb['Basis']]
out = r'C:\Projects\Sales_Platform\JPS_Sep2026_NonFuel_Volume_Mix.xlsx'
wb.save(out); print('saved', out)
for k, v in RESULT.items():
    print(k, 'GWh %.1f->%.1f' % (v[1] / 1e6, v[0] / 1e6), 'nf %.0f->%.0f' % (v[3] / 1e6, v[2] / 1e6), 'vol %+.0f mix %+.0f rate %+.0f' % (v[4] / 1e6, v[5] / 1e6, v[6] / 1e6), 'total %+.0f' % ((v[2] - v[3]) / 1e6))
