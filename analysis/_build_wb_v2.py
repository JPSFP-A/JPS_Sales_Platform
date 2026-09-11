# -*- coding: utf-8 -*-
import io, json, os, openpyxl, numpy as np
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

src = r'C:\Users\jwilson\Downloads\July LE Sales Gen.xlsx'
sv = openpyxl.load_workbook(src, data_only=True)
vs, dv = sv['Summary'], sv['Demand']
CLS = ['RT10','RT20','RT40','RT50','RT60-ST','RT70']

def cell(ws, r, c):
    v = ws.cell(r, c).value
    return float(v) if isinstance(v, (int, float)) else 0.0

# FY2026 monthly by class, read straight off the Driver Forecast engine after the
# submitted true-up overlay was applied. Previously this came from the July LE
# workbook and was then pinned to 3,281.97 here -- which meant the workbook tied to
# the submitted total while the app did not, and their class splits never matched.
# The engine now ties on its own, so there is nothing left to pin.
# FY2026 monthly by class, pinned to the Billed Sales (MWh) table supplied 11 Sep
# 2026 -- the current official monthly-actual/forecast register, superseding the
# Sep-7 engine snapshot previously pinned here. FY2027 and FY2028 remain pinned to
# the Driver Report's Section 1 annual totals as before; only FY2026 moved. Do not
# hand-edit this back to a live pull without also refreshing the Driver Report's
# Section 1 and Section 2 bridge at the same time -- both were updated 11 Sep 2026
# to this same FY2026 total (3,299.7 GWh, was 3,298.4/3,298.5).
m26 = {
    'RT10': [84427000, 76489000, 88278000, 87176000, 99081000, 101300000, 113613000, 117671000, 111926000, 116161000, 114197000, 112445000],
    'RT20': [44389000, 41873000, 49678000, 47362000, 55463000, 55125000, 60644000, 60610000, 59358000, 61129000, 59811000, 59230000],
    'RT40': [56014000, 52824000, 61690000, 59598000, 65914000, 64392000, 70139000, 71883000, 64637000, 68649000, 68405000, 67768000],
    'RT50': [26724000, 26712000, 29780000, 28362000, 30151000, 28210000, 28679000, 30677000, 28419000, 29235000, 29465000, 29237000],
    'RT60-ST': [2224000, 2310000, 3099000, 3413000, 2798000, 3410000, 3409000, 3413000, 3345000, 3361000, 3353000, 3334000],
    'RT70': [20371000, 21089000, 26194000, 24727000, 27727000, 26848000, 28562000, 19708000, 18032000, 18496000, 17877000, 17559000],
}

m27 = {
    'RT10': [99482070, 94597041, 97684066, 97876011, 103622665, 110794940, 115533429, 122141581, 118219142, 112535879, 98622924, 103890252],
    'RT20': [51505595, 53157163, 55364368, 53858815, 56163029, 59867633, 62135541, 62517573, 62152550, 61744813, 55499951, 57632969],
    'RT40': [69081250, 69907191, 69669746, 69897926, 70101411, 70070454, 69921950, 69989398, 70029249, 70030447, 70034635, 69866343],
    'RT50': [30013545, 30722989, 31225085, 31997182, 32676844, 33119429, 33715263, 34299974, 34864110, 35446220, 36057700, 36661659],
    'RT60-ST': [3338606, 3334042, 3336247, 3331506, 3331543, 3323479, 3317737, 3311900, 3305376, 3297015, 3291095, 3281454],
    'RT70': [15542829, 15371199, 16188143, 16500619, 16508318, 16528448, 16214993, 16197560, 16184073, 16154977, 16158884, 16149957],
}

m28 = {
    'RT10': [103455567, 96409453, 100660282, 100540141, 106066583, 113922914, 118734364, 125627469, 121466878, 115402483, 100665772, 106348094],
    'RT20': [55109458, 55887713, 58557590, 55287698, 57302576, 61182881, 63263962, 63533791, 62881261, 62235153, 55534478, 57623439],
    'RT40': [69942422, 69875018, 69785509, 69900605, 69714698, 69644540, 69594661, 69499010, 69436043, 69375381, 69281700, 69250413],
    'RT50': [36010428, 36201241, 36252398, 36120010, 36157730, 36144627, 36110197, 36108297, 36093249, 36077564, 36068108, 36056151],
    'RT60-ST': [3274143, 3266796, 3258975, 3251757, 3244330, 3236875, 3229543, 3222173, 3214820, 3207502, 3200190, 3192896],
    'RT70': [16002632, 15977772, 15957939, 15892773, 15856544, 15816613, 15769857, 15729291, 15687283, 15644558, 15603189, 15561549],
}

# FY2026 losses. Jan-Aug is real: net generation (net_gen_historical.net_gen_mwh)
# minus TRUE billed sales (jps_actuals, not net_gen_historical's own billed_mwh
# column, which is a different, less current pipeline and no longer agrees with
# jps_actuals -- e.g. Aug billed_mwh there is 307,231 vs jps_actuals' 303,962).
# Blended Jan-Aug lands at 25.98%, comfortably under the 27.10% target -- losses
# have been running better than plan all year. Sep-Dec has no real losses yet, so
# they are SOLVED (same approach as FY2027/28's RATE_M, just a flat rate here
# rather than a seasonal curve, since four months isn't enough to fit one credibly)
# to close the FULL YEAR at exactly 27.10%, not just the open months: 29.05%/mo.
_NETGEN_JAN_AUG_2026 = [325445.00, 294131.83, 346444.13, 347826.00, 364366.69, 387886.70, 399975.47, 417380.53]  # MWh, net_gen_historical
_BILLED_JAN_AUG_2026 = [234149.60905, 221297.13582, 258718.44568, 250638.54954, 281134.17319, 279285.88383, 305047.38824, 303962.13026]  # MWh, jps_actuals
l26_actual = [(ng - b) * 1000 for ng, b in zip(_NETGEN_JAN_AUG_2026, _BILLED_JAN_AUG_2026)]  # kWh
_S_actual_2026 = sum(_BILLED_JAN_AUG_2026) * 1000
_L_actual_2026 = sum(l26_actual)
_S_fcst_2026 = sum(sum(m26[rc][8:12]) for rc in CLS)
_TARGET_2026_LOSSPCT = 0.2710
_L_fcst_2026_total = _TARGET_2026_LOSSPCT / (1 - _TARGET_2026_LOSSPCT) * (_S_actual_2026 + _S_fcst_2026) - _L_actual_2026
_R_SEPDEC_2026 = _L_fcst_2026_total / (_S_fcst_2026 + _L_fcst_2026_total)
l26_fcst = [sum(m26[rc][8 + m] for rc in CLS) * _R_SEPDEC_2026 / (1 - _R_SEPDEC_2026) for m in range(4)]
l26 = l26_actual + l26_fcst
assert abs((sum(l26)) / (sum(sum(m26[rc]) for rc in CLS) + sum(l26)) * 100 - 27.10) < 0.05, 'FY2026 losses solve did not land on 27.10'

series = {rc: {2026: m26[rc], 2027: m27[rc], 2028: m28[rc]} for rc in CLS}
sales = np.array([sum(series[rc][y][m] for rc in CLS) for y in (2026, 2027, 2028) for m in range(12)])

# FY2026 no longer ties to the submitted 3,281.97 GWh, and that is expected, not a
# bug: the submitted number was locked in when the year was still mostly forecast.
# August actual ran above what the submission assumed for it, and every closed
# month is now real. This is reported, not asserted -- the point of this build is
# to move off the frozen figure, not to keep forcing the engine back onto it.
TARGET_2026 = 3281.97e6
cur26 = sum(sales[:12])
gap = cur26 - TARGET_2026
_sign = '+' if gap >= 0 else ''
print('FY2026 vs the 19-Aug submission: %.3f GWh (submission %.3f GWh, %s%.1f GWh, %s%.2f pct)'
      % (cur26/1e6, TARGET_2026/1e6, _sign, gap/1e6, _sign, gap/TARGET_2026*100))

# Monthly loss rates come straight from jps_macro_assumptions driver_type='loss_monthly'.
# They are no longer inverted out of a rolling target: inverting the old near-flat
# targets against seasonal sales implied a 0.57% January 2028, so the targets are now
# built FROM a credible monthly path and the rolling series is derived from it.
# Seasonality from 2024-2025 billed actuals (Oct-Dec 2025 excluded as storm-distorted),
# level solved so each year closes at 27.10%.
RATE_M = {
 2027: [27.75,22.78,29.34,27.39,30.72,26.53,27.56,28.21,25.35,25.45,24.75,28.34],
 2028: [27.77,22.81,29.33,27.38,30.71,26.52,27.56,28.21,25.35,25.45,24.75,28.34],
}
full = list(l26)
for y in (2027, 2028):
    off = 12 if y == 2027 else 24
    for m in range(12):
        r = RATE_M[y][m] / 100.0
        full.append(sales[off + m] * r / (1 - r))
full = np.array(full)
pct = [full[t] / (sales[t] + full[t]) * 100 for t in range(36)]
rchk = [full[t-11:t+1].sum() / (sales[t-11:t+1].sum() + full[t-11:t+1].sum()) * 100 for t in range(12, 36)]
for y, off in ((2027, 12), (2028, 24)):
    S, L = sales[off:off+12].sum(), full[off:off+12].sum()
    # The supplied rates are quoted to two decimals, so applying them to our sales
    # lands a hair off 27.10. Anything beyond 0.05pp would be a real disagreement.
    assert abs(L/(S+L)*100 - 27.10) < 0.05, 'FY%d closes at %.4f%%, not 27.10' % (y, L/(S+L)*100)
ng = [sales[t] + full[t] for t in range(36)]

# Caribbean Cement is a third of RT50's demand and is the one RT50 account the
# forecast deliberately holds out of the storm-recovery normalisation
# (_DFC_NORM_EXCLUDE in the app): its 2026 volume ROSE while the rest of the class
# fell, so the recovery uplift does not belong on it. That makes the class-level
# kVA line misleading on its own, hence the break-out below.
#
# Source is CaribCement_RT50_Projection_v3.xlsx, built on the same basis as this
# workbook: actual January to July 2026, projected from August. It is read rather
# than re-derived so the two documents cannot drift apart.
import datetime as _dt
_ccwb = openpyxl.load_workbook('C:/Projects/Sales_Platform/analysis/CaribCement_RT50_Projection_v3.xlsx', data_only=True)
_ccws = _ccwb['Projection']
CC = {}          # (year, month) -> {'kva':, 'kwh':, 'ap':}
for _r in range(4, _ccws.max_row + 1):
    _d = _ccws.cell(_r, 3).value
    if not isinstance(_d, _dt.datetime):
        continue
    CC[(_d.year, _d.month)] = {'ap': _ccws.cell(_r, 5).value,
                               'kva': float(_ccws.cell(_r, 6).value or 0),
                               'kwh': float(_ccws.cell(_r, 9).value or 0)}
_ccwb.close()
# Caribbean Cement's demand by type, scanned from the Check Consumption files
# (account 302571-686496, SCAT_CODE KVA/KVAP/KVAL/KVAO). It is a fully TOU-metered
# account: no Standard demand at all, and the three peak bands run near a third
# each. Closed months are used as billed; projected months apply the closed-month
# share mix to the projected total kVA, which keeps the split tied to the same
# projection the kVA line uses.
_CCDT = json.load(io.open(r'C:/Projects/Sales_Platform/analysis/_cc_demand_type.json', encoding='utf-8'))
DTYPES = ['Standard', 'On-Peak', 'Partial-Peak', 'Off-Peak']
_closed = {k: v for k, v in _CCDT.items() if k <= '2026-07'}
_tot = sum(sum(v.values()) for v in _closed.values())
CCSH = {t: sum(v.get(t, 0.0) for v in _closed.values()) / _tot for t in DTYPES}
print('Caribbean Cement demand mix from %d closed months: %s'
      % (len(_closed), ', '.join('%s %.1f%%' % (t, CCSH[t]*100) for t in DTYPES)))


# Demand does not follow energy one for one. Measured on Jan-Aug 2025 against the
# same months of 2026, billed kVA moved about two thirds as fast as billed kWh:
#
#     RT40   kWh -6.3%   kVA -4.1%   elasticity 0.65
#     RT50   kWh -9.6%   kVA -6.2%   elasticity 0.63
#
# The two classes land on the same number independently, which is why it is used
# rather than the old constant-load-factor assumption (elasticity of 1.0).
#
# RT70 is deliberately held at 1.0. Its forecast fall is Alcoa going self-generating,
# a customer leaving the system rather than a change in usage intensity, and when
# load exits demand goes with it roughly one for one. Applying 0.64 there would
# understate the drop by about 9,500 kVA.
ELASTICITY = {'RT40': 0.65, 'RT50': 0.63, 'RT70': 1.00}
DEMAND_CUT = 1.00   # no flat haircut on top of the elasticity


def dcut(y):
    return DEMAND_CUT if y >= 2027 else 1.0


def cc_kva(y, m):
    return CC[(y, m)]['kva'] * dcut(y)


def cc_type(y, m, t):
    k = '%d-%02d' % (y, m)
    if k in _closed:
        return _closed[k].get(t, 0.0)
    return CC[(y, m)]['kva'] * CCSH[t] * dcut(y)


# A closed month must reconcile to the same total the kVA line carries, or the two
# blocks would silently disagree about the same account.
for _k, _v in _closed.items():
    _y, _m = int(_k[:4]), int(_k[5:7])
    assert abs(sum(_v.values()) - CC[(_y, _m)]['kva']) < 1.0,         'Caribbean Cement %s: demand types sum to %.0f, kVA line says %.0f' % (
            _k, sum(_v.values()), CC[(_y, _m)]['kva'])

for _y in (2026, 2027, 2028):
    _miss = [_m for _m in range(1, 13) if (_y, _m) not in CC]
    assert not _miss, 'Caribbean Cement projection is missing %d months of FY%d: %s' % (len(_miss), _y, _miss)
print('Caribbean Cement: %d months loaded, FY2026 %.2f GWh / avg %s kVA'
      % (len(CC), sum(CC[(2026, m)]['kwh'] for m in range(1, 13))/1e6,
         format(int(sum(CC[(2026, m)]['kva'] for m in range(1, 13))/12), ',')))

# WB_DST lets a build go somewhere else when the canonical file is open in Excel,
# which holds an exclusive lock and makes the save fail outright.
dst = os.environ.get('WB_DST') or r'C:\Projects\Sales_Platform\JPS_LE_Sales_Gen_FY2026-28.xlsx'
wb = openpyxl.Workbook(); ws = wb.active; ws.title = 'Sales Wide'
HDR = PatternFill('solid', fgColor='0B3D66'); W = Font(bold=True, color='FFFFFF')
YR = PatternFill('solid', fgColor='E8EEF4')
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

ws.cell(1,1).value = 'JPS Sales Forecast - FY2026 to FY2028, monthly kWh'
ws.cell(1,1).font = Font(bold=True, size=13)
ws.cell(2,1).value = ('Actual Jan-Aug 2026; forecast thereafter. Storm recovery now runs THROUGH the driver engine '
                      '(normalisation on RT50/RT40/RT20, cement excluded; industrial recovery applied to the seven hotel accounts only) rather than as a separate overlay, so these '
                      'figures equal what the platform shows. FY2028 carries no storm uplift: recovery completes by end-2027. '
                      'Losses solved to close each fiscal year at 27.10%%: FY2027/28 via a seasonality-shaped monthly rate, FY2026 via a single '
                      'rate on the still-open Sep-Dec months (Jan-Aug is real, running at 25.98%%, comfortably under target). '
                      'FY2026 no longer ties to the 3,281.97 GWh submitted 19 Aug 2026 -- that figure is frozen as the number of record; the register '
                      'has moved since as more months closed. Currently %.1f GWh, %s%.1f GWh (%s%.2f pct) above the submission, reported here rather than forced to tie.'
                      % (cur26/1e6, _sign, gap/1e6, _sign, gap/TARGET_2026*100))
ws.cell(2,1).font = Font(italic=True, size=9)
col = 2
for y in (2026, 2027, 2028):
    ws.cell(4,col).value = 'FY%d' % y
    ws.cell(4,col).font = Font(bold=True, size=11)
    ws.cell(4,col).alignment = Alignment(horizontal='center')
    ws.merge_cells(start_row=4, start_column=col, end_row=4, end_column=col+12)
    for i, mn in enumerate(months):
        c = ws.cell(5, col+i); c.value = mn; c.fill = HDR; c.font = W
        c.alignment = Alignment(horizontal='center')
    t = ws.cell(5, col+12); t.value = 'FY%d Total' % y; t.fill = HDR; t.font = W
    col += 13
ws.cell(5,1).value = 'Rate Class'; ws.cell(5,1).fill = HDR; ws.cell(5,1).font = W

tot = {y: [0.0]*12 for y in (2026, 2027, 2028)}
for i, rc in enumerate(CLS):
    r = 6 + i
    ws.cell(r,1).value = rc; ws.cell(r,1).font = Font(bold=True)
    col = 2
    for y in (2026, 2027, 2028):
        for m in range(12):
            v = series[rc][y][m]; tot[y][m] += v
            c = ws.cell(r, col+m); c.value = round(v, 0); c.number_format = '#,##0'
        tc = ws.cell(r, col+12); tc.value = round(sum(series[rc][y]), 0)
        tc.number_format = '#,##0'; tc.font = Font(bold=True); tc.fill = YR
        col += 13
gr = 6 + len(CLS)
ws.cell(gr,1).value = 'Grand Total'; ws.cell(gr,1).font = Font(bold=True)
col = 2
for y in (2026, 2027, 2028):
    for m in range(12):
        c = ws.cell(gr, col+m); c.value = round(tot[y][m], 0)
        c.number_format = '#,##0'; c.font = Font(bold=True)
    t = ws.cell(gr, col+12); t.value = round(sum(tot[y]), 0)
    t.number_format = '#,##0'; t.font = Font(bold=True); t.fill = YR
    col += 13

ws.cell(gr+1,1).value = 'Losses (kWh)'; ws.cell(gr+1,1).font = Font(bold=True)
ws.cell(gr+2,1).value = 'Losses % (monthly)'; ws.cell(gr+2,1).font = Font(bold=True)
ws.cell(gr+3,1).value = 'Rolling 12-mth loss %'; ws.cell(gr+3,1).font = Font(bold=True)
ws.cell(gr+4,1).value = 'Net Generation'; ws.cell(gr+4,1).font = Font(bold=True)
col = 2
for yi, y in enumerate((2026, 2027, 2028)):
    for m in range(12):
        t = yi*12 + m
        lc = ws.cell(gr+1, col+m); lc.value = round(full[t], 0); lc.number_format = '#,##0'
        c = ws.cell(gr+2, col+m); c.value = pct[t]/100.0; c.number_format = '0.00%'
        if t >= 12:
            r2 = ws.cell(gr+3, col+m); r2.value = rchk[t-12]/100.0; r2.number_format = '0.00%'
        g = ws.cell(gr+4, col+m); g.value = round(ng[t], 0); g.number_format = '#,##0'
    lt = ws.cell(gr+1, col+12); lt.value = round(sum(full[yi*12:yi*12+12]), 0)
    lt.number_format = '#,##0'; lt.font = Font(bold=True); lt.fill = YR
    pt = ws.cell(gr+2, col+12)
    pt.value = sum(full[yi*12:yi*12+12]) / (sum(sales[yi*12:yi*12+12]) + sum(full[yi*12:yi*12+12]))
    pt.number_format = '0.00%'; pt.font = Font(bold=True); pt.fill = YR
    tc = ws.cell(gr+4, col+12); tc.value = round(sum(ng[yi*12:yi*12+12]), 0)
    tc.number_format = '#,##0'; tc.font = Font(bold=True); tc.fill = YR
    col += 13
ws.freeze_panes = 'B6'; ws.column_dimensions['A'].width = 20
for c in range(2, 42): ws.column_dimensions[get_column_letter(c)].width = 13

# The demand sheet is built twice: once on the measured elasticity alone, and once
# with a further 8% taken off from January 2027. Both are wanted side by side because
# they answer different questions -- the elasticity corrects HOW demand follows energy,
# the 8% is a separate judgement that the energy forecast's own recovery will not show
# up in demand. Same code path, so the two sheets cannot drift apart in anything but
# the haircut.
def build_demand_sheet(title, cut, elasticity=None):
    global DEMAND_CUT
    DEMAND_CUT = cut
    elasticity = elasticity or ELASTICITY
    d = wb.create_sheet(title)
    def rv(r): return [cell(dv, r, c) for c in range(2, 14)]
    G = {rc: (sum(m27[rc]) / sum(m26[rc]), sum(m28[rc]) / sum(m26[rc])) for rc in ('RT40', 'RT50', 'RT70')}
    print('Demand scaling factors (sales growth before elasticity): '
          + ', '.join('%s FY27 %+.1f%% / FY28 %+.1f%%' % (rc, (G[rc][0]-1)*100, (G[rc][1]-1)*100) for rc in G))
    # The Caribbean Cement split was nested inside the class table as two indented rows,
    # where it read as a footnote to RT50 and was easy to miss entirely. It is the point
    # of the sheet for anyone sizing the RT50 book, so it gets its own titled block.
    blocks = [('Total billed kVA', [(6,'RT40','RT40'), (7,'RT50','RT50'), (8,'RT70','RT70')]),
              ('RT50 with and without Caribbean Cement', [(7,'RT50','RT50 total'),
                                   ('CC','RT50','Caribbean Cement'),
                                   ('CC_EX','RT50','RT50 excl. Caribbean Cement')]),
              ('RT40 - Load Shape', [(12,'RT40','Standard'), (13,'RT40','On-Peak'), (14,'RT40','Partial-Peak'), (15,'RT40','Off-Peak')]),
              ('RT50 - Load Shape', [(19,'RT50','Standard'), (20,'RT50','On-Peak'), (21,'RT50','Partial-Peak'), (22,'RT50','Off-Peak')]),
              ('Caribbean Cement - Load Shape', [(('CCT','Standard'),'RT50','Standard'),
                                   (('CCT','On-Peak'),'RT50','On-Peak'),
                                   (('CCT','Partial-Peak'),'RT50','Partial-Peak'),
                                   (('CCT','Off-Peak'),'RT50','Off-Peak')]),
              ('RT50 - Load Shape excl. Caribbean Cement', [(('EX',19,'Standard'),'RT50','Standard'),
                                   (('EX',20,'On-Peak'),'RT50','On-Peak'),
                                   (('EX',21,'Partial-Peak'),'RT50','Partial-Peak'),
                                   (('EX',22,'Off-Peak'),'RT50','Off-Peak')]),
              ('RT70 - Load Shape', [(26,'RT70','Standard'), (27,'RT70','On-Peak'), (28,'RT70','Partial-Peak'), (29,'RT70','Off-Peak')])]
    d.cell(1,1).value = 'JPS Peak Demand Forecast - FY2026 to FY2028, billed kVA'
    d.cell(1,1).font = Font(bold=True, size=13)
    d.cell(2,1).value = ('FY2027/28 scaled from FY2026 by each class kWh growth, damped by a measured demand elasticity: '
                         'billed kVA moves about two thirds as fast as billed kWh (RT40 0.65, RT50 0.63, from Jan-Aug 2025 vs 2026). '
                         'RT70 is held at 1.0 because its fall is a customer exiting, not a change in usage intensity. '
                         'jps_demand_actuals has no per-account grain, so demand cannot run through the Driver Forecast engine.'
                     + ('' if cut >= 1.0 else
                        ' A further %.0f%% is then taken off every month from January 2027, on the view that the recovery in '
                        'the energy forecast will not show up in demand: billed kVA fell year on year through 2026 '
                        '(RT40 -4.1%%, RT50 -6.2%%). kWh is unchanged, so implied load factor rises about %.1f%%.'
                        % ((1-cut)*100, (1/cut-1)*100)))
    d.cell(2,1).font = Font(italic=True, size=9)
    r = 4
    for title, rows in blocks:
        d.cell(r,1).value = title; d.cell(r,1).font = Font(bold=True, size=11); r += 1
        hy, hm = r, r+1
        d.cell(hm,1).value = 'Demand Type' if 'Shape' in title else 'Rate Class'
        d.cell(hm,1).fill = HDR; d.cell(hm,1).font = W
        col = 2
        for y in (2026, 2027, 2028):
            d.cell(hy,col).value = 'FY%d' % y
            d.cell(hy,col).font = Font(bold=True, size=11)
            d.cell(hy,col).alignment = Alignment(horizontal='center')
            d.merge_cells(start_row=hy, start_column=col, end_row=hy, end_column=col+12)
            for i, mn in enumerate(months):
                c = d.cell(hm, col+i); c.value = mn; c.fill = HDR; c.font = W
                c.alignment = Alignment(horizontal='center')
            t = d.cell(hm, col+12); t.value = 'Avg'; t.fill = HDR; t.font = W
            col += 13
        r = hm + 1
        for srow, rc, lab in rows:
            d.cell(r,1).value = lab; col = 2
            base = rv(srow) if isinstance(srow, int) else None
            for yi, y in enumerate((2026, 2027, 2028)):
                g = 1.0 if y == 2026 else (G[rc][yi-1] ** elasticity[rc]) * DEMAND_CUT
                if isinstance(srow, tuple) and srow[0] == 'CCT':
                    vv = [cc_type(y, m+1, srow[1]) for m in range(12)]
                elif isinstance(srow, tuple) and srow[0] == 'EX':
                    _, _srow, _t = srow
                    vv = [rv(_srow)[m]*g - cc_type(y, m+1, _t) for m in range(12)]
                elif srow == 'CC':
                    # Caribbean Cement carries its own projection, deliberately NOT the
                    # class growth factor: the RT50 uplift is storm-recovery
                    # normalisation and this account is excluded from it.
                    vv = [cc_kva(y, m+1) for m in range(12)]
                elif srow == 'CC_EX':
                    vv = [rv(7)[m]*g - cc_kva(y, m+1) for m in range(12)]
                else:
                    vv = [bb*g for bb in base]
                for m in range(12):
                    c = d.cell(r, col+m); c.value = round(vv[m], 0); c.number_format = '#,##0'
                t = d.cell(r, col+12); t.value = round(sum(vv)/12.0, 0)
                t.number_format = '#,##0'; t.font = Font(bold=True); t.fill = YR
                col += 13
            r += 1
        r += 1
    # --- Caribbean Cement detail -----------------------------------------------------
    import calendar as _cal
    d.cell(r,1).value = 'Caribbean Cement Co Ltd (RT50, account 302571-686496)'
    d.cell(r,1).font = Font(bold=True, size=11); r += 1
    d.cell(r,1).value = ('Actual January to July 2026, projected thereafter. Load factor is billed kWh '
                         'over billed kVA times the hours in the month.')
    d.cell(r,1).font = Font(italic=True, size=9); r += 1
    hy, hm = r, r+1
    d.cell(hm,1).value = 'Measure'; d.cell(hm,1).fill = HDR; d.cell(hm,1).font = W
    col = 2
    for y in (2026, 2027, 2028):
        d.cell(hy,col).value = 'FY%d' % y
        d.cell(hy,col).font = Font(bold=True, size=11)
        d.cell(hy,col).alignment = Alignment(horizontal='center')
        d.merge_cells(start_row=hy, start_column=col, end_row=hy, end_column=col+12)
        for i, mn in enumerate(months):
            c = d.cell(hm, col+i); c.value = mn; c.fill = HDR; c.font = W
            c.alignment = Alignment(horizontal='center')
        t = d.cell(hm, col+12); t.value = 'Total / Avg'; t.fill = HDR; t.font = W
        col += 13
    r = hm + 1
    for lab, fld, fmt, agg in (('Billed kVA','kva','#,##0','avg'),
                               ('Billed kWh','kwh','#,##0','sum'),
                               ('Load factor','lf','0.0%','avg'),
                               ('Actual / Projected','ap',None,None)):
        d.cell(r,1).value = lab; col = 2
        for y in (2026, 2027, 2028):
            vals = []
            for m in range(12):
                rec = CC[(y, m+1)]
                if fld == 'lf':
                    hrs = _cal.monthrange(y, m+1)[1] * 24
                    v = (rec['kwh'] / (rec['kva'] * dcut(y) * hrs)) if rec['kva'] else 0.0
                elif fld == 'ap':
                    v = 'A' if str(rec['ap']).startswith('Act') else 'P'
                else:
                    v = rec[fld] * (dcut(y) if fld == 'kva' else 1.0)
                vals.append(v)
                c = d.cell(r, col+m); c.value = v if fld != 'kva' and fld != 'kwh' else round(v, 0)
                if fmt: c.number_format = fmt
                if fld == 'ap': c.alignment = Alignment(horizontal='center')
            if agg:
                nums = [v for v in vals if isinstance(v, (int, float))]
                t = d.cell(r, col+12)
                t.value = round(sum(nums), 0) if agg == 'sum' else (sum(nums)/len(nums) if nums else 0)
                t.number_format = fmt; t.font = Font(bold=True); t.fill = YR
            col += 13
        r += 1

    d.freeze_panes = 'B6'; d.column_dimensions['A'].width = 34
    for c in range(2, 42): d.column_dimensions[get_column_letter(c)].width = 12


build_demand_sheet('Demand Wide', 1.00)
build_demand_sheet('Demand Wide -4%', 0.96)
# Raw 1:1 scaling, at the user's explicit request: no elasticity damping, no haircut,
# demand grows at exactly the same rate as sales, constant load factor. This is the
# treatment every prior sheet in this workbook was built to move away from -- kept
# here, unmodified, as the reference point for what "without the guard rails" means.
build_demand_sheet('Demand Wide - Raw 1to1', 1.00, elasticity={'RT40': 1.00, 'RT50': 1.00, 'RT70': 1.00})

wb.save(dst)
print('saved', dst)
for y, off in ((2026,0), (2027,12), (2028,24)):
    S = sales[off:off+12].sum(); L = full[off:off+12].sum()
    print('FY%d: sales %.1f  losses %.1f  netgen %.1f  loss%% %.2f'
          % (y, S/1e6, L/1e6, (S+L)/1e6, L/(S+L)*100))
print('monthly loss range %.2f to %.2f pct' % (min(pct[12:]), max(pct[12:])))
print('rolling range %.2f to %.2f pct' % (min(rchk), max(rchk)))
