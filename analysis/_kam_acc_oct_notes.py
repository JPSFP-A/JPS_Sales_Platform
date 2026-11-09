# -*- coding: utf-8 -*-
# Adds what we have established about the October misses to the KAM forecast accuracy workbook,
# plus a sheet of the October consumption adjustments on KAM accounts. Reads the billing-extract scan for the adjustments.
import json, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
P = r'C:\Projects\Sales_Platform\JPS_KAM_Forecast_Accuracy_Oct2026.xlsx'
wb = openpyxl.load_workbook(P)
ws = wb['Largest misses']
hdr = [c.value for c in ws[1]]
KNOW = {
    'PAC Kingston Airport Ltd.': 'The 80% reduction is on file but not in the October bill (0.83 GWh against 0.78 in September). Staged load sharing, so the cut has not started to show.',
    'Caribbean Cement Co Ltd': 'kWh are flat on September (9.11 against 9.13 GWh); the forecast was low. The J$174M revenue credit is a recurring monthly revenue item with no kWh effect.',
    'Windalco': 'Back to 1.85 GWh after the July outage. The forecast has no structural entry and runs below the run rate.',
    'Petrojam Ltd': 'Fire in September, down about two weeks (0.85 GWh). October is back to normal at 1.76 GWh. The forecast carried part of the September low.',
    'Alcoa Mins Of Ja Ltd': 'Main account bills 0.26 GWh after a 2.0 GWh billing credit in October. The forecast has zero.',
    'PriceSmart (Jamaica) Ltd': 'New club billing in October (the Montego Bay club opened on 2 October per public reports). The forecast had 0.03 GWh.',
    'Caribbean Broilers Ja Ltd': 'Billing timing: 0.08 GWh in September, 3.42 in August, 1.68 in October.',
    'West Meat Packers Ja Ltd': 'Down 0.14 GWh on September. The entry has the 70% cut starting in 2027, so this is earlier than planned.',
    'National Water Commission': 'Pumping demand: NWC rose 1.7 GWh across its accounts in October.',
}
col = len(hdr) + 1
ws.cell(1, col, 'What we know (KAM to confirm)'); ws.cell(1, col).font = ws.cell(1, col - 1).font.copy(); ws.cell(1, col).fill = ws.cell(1, col - 1).fill.copy(); ws.cell(1, col).alignment = ws.cell(1, col - 1).alignment.copy()
cust_i = hdr.index('Customer') + 1; n = 0
for r in range(2, ws.max_row + 1):
    k = KNOW.get(ws.cell(r, cust_i).value)
    if k: ws.cell(r, col, k).alignment = Alignment(wrap_text=True, vertical='top'); n += 1
ws.column_dimensions[get_column_letter(col)].width = 90
# adjustments sheet
SC = json.load(open(r'C:\Projects\Sales_Platform\analysis\_oct_anomaly_scan.json')); oc = SC['oct']
kam = {}; ws_all = wb['All accounts']; h2 = [c.value for c in ws_all[1]]; ka, ac_i = h2.index('KAM') + 1, h2.index('Account') + 1
for r in range(2, ws_all.max_row + 1): kam[str(ws_all.cell(r, ac_i).value)] = ws_all.cell(r, ka).value
rows = [(kam[a], a, o['name'], o['gross'], o['adj'], o['net']) for a, o in oc.items() if a in kam and abs(o['adj']) >= 1000]
rows.sort(key=lambda x: -abs(x[4]))
if 'October adjustments' in wb.sheetnames: del wb['October adjustments']
s = wb.create_sheet('October adjustments', 2)
s.append(['Consumption adjustments on KAM accounts in October (billed kWh less adjustment = net kWh in the platform)']); s['A1'].font = Font(bold=True, size=12)
s.append(['Large credits or catch-up bills distort the month. The net kWh is what the platform and this workbook use.']); s.append([])
s.append(['KAM', 'Account', 'Customer', 'Billed kWh', 'Adjustment kWh', 'Net kWh'])
for c in s[4]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='1F3864')
for r in rows: s.append([r[0], r[1], r[2].strip(), round(r[3]), round(r[4]), round(r[5])])
for rr in s.iter_rows(min_row=5, min_col=4, max_col=6):
    for c in rr: c.number_format = '#,##0'
for i, w in enumerate((20, 18, 38, 14, 16, 14), 1): s.column_dimensions[get_column_letter(i)].width = w
s.append([]); s.append(['Total', '', '', f'=SUM(D5:D{4 + len(rows)})', f'=SUM(E5:E{4 + len(rows)})', f'=SUM(F5:F{4 + len(rows)})'])
for c in s[s.max_row]: c.font = Font(bold=True); c.number_format = '#,##0'
m = wb['Method']
m.append(['October note: Alcoa shows a 2.0 GWh billing credit and NWC and China Harbour carry catch-up bills (see October adjustments). The "What we know" column on Largest misses records what has been established, for the KAM to confirm or correct.'])
wb.save(P); print('notes added to', n, 'rows;', len(rows), 'adjustment rows; adj total', round(sum(r[4] for r in rows)))
