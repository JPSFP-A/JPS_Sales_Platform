# -*- coding: utf-8 -*-
# FY2027 sales forecast workbook, refreshed to the account-level forecast (3,440 GWh).
import json, os, sys
import numpy as np, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as CL
HERE = r'C:\Projects\Sales_Platform\analysis'; os.chdir(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else r'C:\Projects\Sales_Platform\JPS_Sales_Forecast_FY2027_Nov2026.xlsx'
RES = json.load(open('_fy27_result.json')); BYC = json.load(open('_fy27_byclass.json')); META = json.load(open(r'_cust\kam_fy27_meta.json')); OVL = json.load(open(r'_cust\kam_fy27_class.json'))['overlay']; WX27 = OVL['wx10_27'] + OVL['wx20_27']; WX28 = OVL['wx10_28'] + OVL['wx20_28']
HOT = pd.read_pickle(r'_cust\kam_fy27_hotels.pkl'); ALL = pd.read_pickle(r'_cust\kam_fy27_accounts.pkl')
CLS = ['RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']; MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
NAME = {'RT10': 'RT10 Residential', 'RT20': 'RT20 Small commercial', 'RT40': 'RT40 Commercial', 'RT50': 'RT50 Large commercial', 'RT60-ST': 'RT60 Street lighting', 'RT70': 'RT70 Industrial'}
EARLIER = {'RT10': 1279.3, 'RT20': 695.7, 'RT40': 825.9, 'RT50': 375.4, 'RT60-ST': 41.0, 'RT70': 211.6}   # class-level view of 6 November (3,428.8)
NAVY = '062552'; H = Font(name='Arial', bold=True, color='FFFFFF', size=10); HF = PatternFill('solid', fgColor=NAVY); B = Font(name='Arial', bold=True, size=10); N = Font(name='Arial', size=10)
def hdr(ws, row, heads, widths):
    for j, h in enumerate(heads, 1):
        c = ws.cell(row, j, h); c.font = H; c.fill = HF; c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True); ws.column_dimensions[CL(j)].width = widths[j - 1]
    ws.row_dimensions[row].height = 32
def ttl(ws, t, s=None):
    ws['A1'] = t; ws['A1'].font = Font(name='Arial', bold=True, size=13, color=NAVY)
    if s: ws['A2'] = s; ws['A2'].font = Font(name='Arial', italic=True, size=10, color='66788A')
NACC = int((~ALL.index.astype(str).str.startswith('NEW')).sum()); NREC = int((HOT.hotel_up27 > 0).sum()); NCLOSED = int(((HOT.ps > 0) & (HOT.level < 0.3 * HOT.ps)).sum())
wb = Workbook()
# ---- Summary ----
s = wb.active; s.title = 'Summary'
ttl(s, 'FY2027 sales forecast, GWh billed including prepaid', 'Refreshed on actuals to October 2026 and the account-level forecast the KAMs are reviewing. Nothing in the platform has been changed.')
hdr(s, 4, ['Rate class', 'FY2025 actual', 'FY2026 LE (financials)', 'FY2026 outlook', 'FY2027 held plan', 'FY2027 forecast', 'Forecast less held', 'vs held %', 'vs FY2026 outlook %'], [24, 13, 14, 14, 14, 14, 14, 11, 14])
for i, c in enumerate(CLS, 5):
    vals = [NAME[c], BYC[c]['fy25'], RES['le'][c], BYC[c]['fy26'], RES['held'][c], BYC[c]['fy27']]
    for j, v in enumerate(vals, 1):
        x = s.cell(i, j, v); x.font = N
        if j > 1: x.number_format = '#,##0.0'
    s.cell(i, 7, f'=F{i}-E{i}'); s.cell(i, 8, f'=F{i}/E{i}-1'); s.cell(i, 9, f'=F{i}/D{i}-1')
t = 5 + len(CLS); s.cell(t, 1, 'Total').font = B
for j in range(2, 7): x = s.cell(t, j, f'=SUM({CL(j)}5:{CL(j)}{t - 1})'); x.font = B
s.cell(t, 7, f'=F{t}-E{t}'); s.cell(t, 8, f'=F{t}/E{t}-1'); s.cell(t, 9, f'=F{t}/D{t}-1')
for r in range(5, t + 1):
    for j in (2, 3, 4, 5, 6, 7): s.cell(r, j).number_format = '#,##0.0'
    for j in (8, 9): s.cell(r, j).number_format = '0.0%'
s.cell(t + 2, 1, 'FY2026 outlook is January to October actual plus our November and December forecast. FY2025 includes the storm months of November and December.').font = Font(name='Arial', italic=True, size=9, color='66788A')
# ---- Monthly ----
m = wb.create_sheet('Monthly 2027')
ttl(m, 'FY2027 forecast by month, GWh', 'Residential at class level; commercial classes are the sum of the account forecast.')
hdr(m, 4, ['Rate class'] + MON + ['FY2027'], [24] + [9] * 12 + [11])
for i, c in enumerate(CLS, 5):
    m.cell(i, 1, NAME[c]).font = N
    for j, v in enumerate(RES['f27'][c], 2): x = m.cell(i, j, round(v, 3)); x.number_format = '#,##0.0'; x.font = N
    x = m.cell(i, 14, f'=SUM(B{i}:M{i})'); x.number_format = '#,##0.0'; x.font = B
m.cell(t, 1, 'Total').font = B
for j in range(2, 15): x = m.cell(t, j, f'=SUM({CL(j)}5:{CL(j)}{t - 1})'); x.number_format = '#,##0.0'; x.font = B
# ---- Rationale ----
r = wb.create_sheet('Rationale')
ttl(r, 'What drives each rate class', 'FY2027 against the FY2026 outlook. The first half of 2026 was depressed by the storm, so most of the growth is the base returning to normal.')
hdr(r, 4, ['Rate class', 'FY2026 outlook', 'FY2027 forecast', 'Change GWh', 'Change %', 'January to June', 'July to December', 'What is driving it', 'What we would want to be sure of'], [24, 12, 12, 11, 10, 11, 11, 80, 60])
drv = {
 'RT10': ('Storm recovery is complete: up 3.9% on 2025 since July. We grow the August to October level 0.8% a year and follow the usual seasonal pattern. Weather and the EV44 charging accounts are in the base. Drags are 7,742 more zero-kWh premises than before the storm, western parishes 3.5% below last year and 857 customers whose bill nets to a credit.', 'Weather: the base carries a warm 2027 (about +' + f'{WX27:.0f}' + ' GWh), so a normal year takes it out. Whether the zero-kWh premises return (worth about 8 GWh if they all do by mid-year). Net billing growth. EV chargers keep growing at the 2026 pace.'),
 'RT20': ('Back above its pre-storm level, 10.4% above October 2024. Account level for the accounts billed individually and class level for the rest, grown 0.8% a year. October carries about 0.3 GWh of catch-up billing that is not repeated.', 'Whether the new accounts that ramped through 2026 hold.'),
 'RT40': ('Flat on last year since July. Built account by account from the middle of August to October, no growth until April, then 1% a year. The adjustments on file and the pipeline customers (National Water Commission expansions, PriceSmart, Restaurants of Jamaica, CB Egg Farm) are in.', 'National Water Commission pumping demand (about 1.7 GWh up in October). Pipeline start dates.'),
 'RT50': ('Hotel recovery. Q3 was 13% below 2025. Each hotel recovers part of its own gap to pre-storm, following the reopening schedule: 19% of the gap in January rising to 75% by December. West Meat Packers loses 70% of its load from March.', 'Reopening dates by property. ' + f'{NCLOSED} hotel accounts are below 30% of pre-storm and get no recovery until a KAM gives a date.'),
 'RT60-ST': ('Street lighting and similar, steady at about 3.4 GWh a month. Early 2026 was low and has recovered.', 'Nothing material.'),
 'RT70': ('Customers leaving the grid. Alcoa has fallen from 7.2 GWh a month in 2025 to 0.26 in October and goes to zero. PAC (4 MW) is taken down 80% from November and MBJ (6 MW) 47% from January. Petrojam has a planned 70-day shutdown from January. Windalco and Petrojam are held at their run rates, not the outage months.', 'MBJ commissioning date and storage (KAM says -77%). Whether Alcoa keeps a standby load. When PAC\'s cut shows in the bills.'),
}
for i, c in enumerate(CLS, 5):
    b = BYC[c]
    for j, v in enumerate([NAME[c], b['fy26'], b['fy27'], b['fy27'] - b['fy26'], b['fy27'] / b['fy26'] - 1, b['h1'], b['h2'], drv[c][0], drv[c][1]], 1):
        x = r.cell(i, j, v); x.font = N
        if j in (2, 3, 4, 6, 7): x.number_format = '#,##0.0;-#,##0.0'
        if j == 5: x.number_format = '0.0%'
        if j >= 8: x.alignment = Alignment(wrap_text=True, vertical='top')
    r.row_dimensions[i].height = 78
tt = 5 + len(CLS); r.cell(tt, 1, 'Total').font = B
for j in (2, 3, 4, 6, 7): x = r.cell(tt, j, f'=SUM({CL(j)}5:{CL(j)}{tt - 1})'); x.font = B; x.number_format = '#,##0.0'
r.cell(tt, 5, f'=C{tt}/B{tt}-1').number_format = '0.0%'
# ---- Build-up ----
bu = wb.create_sheet('Build-up')
ttl(bu, 'How the 3,440 GWh is built', f'Account-level classes are the sum of {NACC:,} accounts; residential and the RT20 accounts not billed individually are class level.')
hdr(bu, 4, ['Step', 'GWh', 'Note'], [52, 12, 90])
acc27 = sum(sum(RES['f27'][c]) for c in ('RT40', 'RT50', 'RT60-ST', 'RT70')) + (sum(RES['f27']['RT20']) - 0)
rem = json.load(open(r'_cust\kam_fy27_class.json'))['out']['RT20']['rem27']
steps = [('Trend, account-level classes', RES['base'], 'August to October 2026 level, seasonal pattern, growth. RT20 accounts, RT40, RT50, RT60, RT70.'),
         ('Hotel recovery', RES['hotel'], 'Part of each hotel\'s gap to pre-storm. 79 properties.'),
         ('Adjustments on file and analyst changes', RES['adj'], 'KAM entries applied to the trend; Alcoa, PAC, MBJ, West Meat Packers, Petrojam, Sutherland and Clarendon Distillers adjusted as listed.'),
         ('Pipeline customers', RES['pipe'], 'Thirteen entries, two dropped and two re-timed.'),
         ('RT20 not billed individually', rem, 'Class level, same method.'),
         ('RT10 Residential', sum(RES['f27']['RT10']), 'Class level.')]
for i, (a, v, n) in enumerate(steps, 5):
    bu.cell(i, 1, a).font = N; x = bu.cell(i, 2, v); x.number_format = '#,##0.0'; x.font = N; bu.cell(i, 3, n).font = N
tb = 5 + len(steps); bu.cell(tb, 1, 'FY2027 forecast').font = B; x = bu.cell(tb, 2, f'=SUM(B5:B{tb - 1})'); x.number_format = '#,##0.0'; x.font = B
bu.cell(tb + 2, 1, 'Against other views of FY2027').font = B
oth = [('Held plan (financials)', sum(RES['held'].values())), ('Class-level view of 6 November', sum(EARLIER.values())), ('Platform engine, October run', 3485.1)]
for i, (a, v) in enumerate(oth, tb + 3):
    bu.cell(i, 1, a).font = N; x = bu.cell(i, 2, v); x.number_format = '#,##0.0'; x.font = N; x2 = bu.cell(i, 3, f'=B{tb}-B{i}'); x2.number_format = '+#,##0.0;-#,##0.0'; x2.font = N
bu.cell(tb + 2, 3, 'Forecast less each view').font = B
# ---- Assumptions ----
a = wb.create_sheet('Assumptions')
ttl(a, 'Assumptions and changes to entries on file')
hdr(a, 3, ['Assumption', 'Value', 'Basis'], [52, 46, 90])
AS = [('Trend level (RT20, RT40, RT50 accounts)', 'Middle of August, September and October 2026 kWh', 'The middle value, so one odd month (timing, an outage) does not drive an account.'),
      ('Seasonal pattern', '2025 at 75%, 2024 at 25%', 'Both before the storm. November and December 2025 are not used. October to December 2027 follow the October level and the 2024 October to December pattern.'),
      ('Growth', 'Commercial 0% January to March, 1% from April. RT20 and RT10 0.8%', 'GDP still contracting in Q3 2026, growth expected from Q2 2027. Customers about +1.5% less solar and efficiency drag for residential.'),
      ('Weather', 'Anomaly of 0.07 to 0.37C a month over the 2023-2025 mean in 2027, flat 0.09C in 2028, at 1.93% of residential load per degree', 'The 7 September engine profile. The WMO expects a very strong El Nino through February 2027. About +' + f'{WX27:.1f}' + ' GWh in FY2027 and +' + f'{WX28:.1f}' + ' in FY2028, RT10 and RT20 residential.'),
      ('EV chargers (EV44)', 'August to October level in the base plus the 2026 monthly trend of about 4.6 MWh a month', 'Charging accounts in the name of JPS. The billing report flags them not billed in error, so they are now counted in sales from January 2025. About ' + f'{OVL["ev_ov_27"] + 0.9:.1f}' + ' GWh in FY2027.'),
      ('Hotel recovery', '19% of the gap in January 2027 rising to 75% in December, 76% to 80% through 2028', 'About 1,900 rooms reopen in December 2026 and just under 3,500 in the first quarter of 2027 (Ministry of Tourism, 14 September 2026). Recovery follows the share of rooms back at an energy factor of about 75%. Properties below 30% of pre-storm get none until a date is confirmed.'),
      ('Adjustments on file', 'Percentage on the trend forecast, manual kWh added', 'Same rule as the platform. Entries solved against the engine base (Petrojam) and the 84 class-wide storm recovery entries are replaced.')]
for k, v in META['OVERRIDE'].items(): AS.append(('Analyst change: ' + k, '', v))
AS += [('Not in the base (risk)', 'Windalco pilot (-12 GWh), FLOW cell sites, NWC solar, net billing expansion, Alcoa standby load (+3 GWh)', 'To be probability-weighted in the revenue-at-risk register.'),
       ('Not in the base (upside)', 'Zero-kWh premises returning, new hospitals', '')]
for i, row in enumerate(AS, 4):
    for j, v in enumerate(row, 1): x = a.cell(i, j, v); x.font = N; x.alignment = Alignment(wrap_text=True, vertical='top')
# ---- Sensitivities ----
v = wb.create_sheet('Sensitivities')
ttl(v, 'Sensitivities, FY2027 GWh')
hdr(v, 3, ['Lever', 'FY2027 GWh', 'Note'], [58, 14, 80])
hh = HOT[(HOT.hotel_up27 > 0)]; gap = float((hh.ps - hh.level).sum()) / 1e6
sens = [('Each 1% on residential (RT10)', sum(RES['f27']['RT10']) / 100, ''), ('Each 1% on RT20', sum(RES['f27']['RT20']) / 100, ''), ('Each 1% on RT40', sum(RES['f27']['RT40']) / 100, ''),
        ('Hotel gap closed 10 points higher all year', gap * 0.10 * 12, 'On the properties that get recovery'),
        ('MBJ at -77% instead of -47%', -0.30 * ALL.at['804282-768320', 'level'] * 12 / 1e6, 'KAM view of the 6 MW PV'),
        ('PAC cut slips to July 2027', 0.8 * ALL.at['1411748-834411', 'level'] * 6 / 1e6, ''),
        ('Alcoa keeps its October standby load', 259407 * 12 / 1e6, 'October 0.26 GWh a month'),
        ('Zero-kWh premises back by mid-2027', sum(RES['f27']['RT10']) * 0.013 / 2, 'About 7,742 premises at 181 kWh a month, half a year'),
        ('Seasonal pattern: 2025 only, or equal weight 2024 and 2025', 22.0, 'Plus or minus, from the class-level test of 6 November')]
for i, (a_, v_, n_) in enumerate(sens, 4):
    v.cell(i, 1, a_).font = N; x = v.cell(i, 2, round(v_, 1)); x.number_format = '+#,##0.0;-#,##0.0'; x.font = N; v.cell(i, 3, n_).font = N
wb.save(OUT); print('saved', OUT)
