# -*- coding: utf-8 -*-
# FY2027 and FY2028 forecast review workbook. The master covers total sales (managed customers, unmanaged customers and the
# customers billed in aggregate) and ties to the company total; each KAM file holds that KAM's portfolio.
import json, os, re
import numpy as np, pandas as pd, openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as CL
from openpyxl.worksheet.datavalidation import DataValidation
HERE = r'C:\Projects\Sales_Platform\analysis'; os.chdir(HERE + r'\_cust')
OUT = r'C:\Projects\Sales_Platform\KAM_FY2027_Review'; os.makedirs(OUT, exist_ok=True)
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
MINUS = '\u2212'
ALL = pd.read_pickle('kam_fy27_accounts.pkl'); ENT = pd.read_pickle('kam_fy27_entries.pkl'); HOT = pd.read_pickle('kam_fy27_hotels.pkl')
META = json.load(open('kam_fy27_meta.json')); CLS = json.load(open('kam_fy27_class.json')); BYC = json.load(open(HERE + r'\_fy27_byclass.json')); LE = json.load(open(HERE + r'\_oct_deep.json'))['le']
M27 = ['m2027%02d' % m for m in range(1, 13)]; M28 = ['m2028%02d' % m for m in range(1, 13)]
lr27, lr28 = {}, {}
ws = openpyxl.load_workbook(r'C:\Projects\Sales_Platform\JPS_KAM_Forecast_Round_Workbook_Oct2026_v2.xlsx', read_only=True, data_only=True)['Account forecast']
for i, r in enumerate(ws.iter_rows(values_only=True)):
    if i >= 4 and r[1]: lr27[str(r[1])] = float(r[6] or 0) * 1000.0; lr28[str(r[1])] = float(r[7] or 0) * 1000.0
ALL['lr27'] = [lr27.get(a, np.nan) for a in ALL.index]; ALL['lr28'] = [lr28.get(a, np.nan) for a in ALL.index]
ALL['adj27'] = ALL.fy27 - ALL.base27 - ALL.hotel_up27; ALL['adj28'] = ALL.fy28 - ALL.base28 - ALL.hotel_up28
ALL['base_ac'] = [str(a) if str(a).startswith('NEW') else str(a).split('-')[0] for a in ALL.index]
G = 1e6
K = ALL[ALL.kam.astype(str) != ''].copy(); U = ALL[ALL.kam.astype(str) == ''].copy()
KAMS = sorted(K.kam.unique(), key=lambda k: -K[K.kam == k].fy27.sum())
NAVY, GREY, INPUT = '062552', '66788A', 'FFF2CC'
F = lambda **k: Font(name='Arial', size=k.pop('size', 10), **k)
fill = lambda c: PatternFill('solid', fgColor=c)
CN = {'RT10': 'RT10 Residential', 'RT20': 'RT20 Small commercial', 'RT40': 'RT40 Commercial', 'RT50': 'RT50 Large commercial', 'RT60-ST': 'RT60 Street lighting', 'RT70': 'RT70 Industrial'}

def header(ws, row, heads, widths):
    for j, h in enumerate(heads, 1):
        c = ws.cell(row, j, h); isin = str(h).startswith('KAM ')
        c.font = F(bold=True, color='000000' if isin else 'FFFFFF'); c.fill = fill(INPUT if isin else NAVY)
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ws.column_dimensions[CL(j)].width = widths[j - 1] if j - 1 < len(widths) else 10
    ws.row_dimensions[row].height = 34
def title(ws, t, sub=None):
    ws['A1'] = t; ws['A1'].font = F(bold=True, size=13, color=NAVY)
    if sub: ws['A2'] = sub; ws['A2'].font = F(italic=True, color=GREY)
def num(ws, r, c, v, fmt='#,##0.00', bold=False):
    x = ws.cell(r, c, None if (v is None or (isinstance(v, float) and np.isnan(v))) else float(v)); x.number_format = fmt; x.font = F(bold=bold); return x
def inp(ws, r, c, v=None):
    x = ws.cell(r, c, v); x.fill = fill(INPUT); x.font = F(); x.alignment = Alignment(wrap_text=True, vertical='top'); return x
def sg(v, d=2): return '0.00' if round(v, d) == 0 else (('+' if v > 0 else MINUS) + f'{abs(v):,.{d}f}')

def cust_row(label_kam, name, base, industry, classes, n_acc, g):
    d = dict(kam=label_kam, base=base, customer=name, industry=industry, classes=classes, accounts=n_acc,
             fy25=g.fy25.sum() / G, fy26=g.fy26_out.sum() / G, fy27=g.fy27.sum() / G, fy28=g.fy28.sum() / G,
             lr27=(g.lr27.sum() / G) if g.lr27.notna().any() else np.nan, lr28=(g.lr28.sum() / G) if g.lr28.notna().any() else np.nan,
             base27=g.base27.sum() / G, hot=g.hotel_up27.sum() / G, adj=g.adj27.sum() / G, hot28=g.hotel_up28.sum() / G, adj28=g.adj28.sum() / G,
             note='; '.join(sorted({str(n) for n in g.note if str(n)}))[:300])
    for m in M27 + M28: d[m] = g[m].sum() / G
    return d

def customers(df, label=None):
    out = []
    for (kam, base), g in df.groupby(['kam', 'base_ac']):
        big = g.sort_values('fy27', ascending=False).iloc[0]; new = str(big.name).startswith('NEW')
        out.append(cust_row(label or kam, str(big['name']).strip() + (' (new)' if new else ''), base, big.industry or '', ', '.join(sorted(set(g.rc))), len(g), g))
    return pd.DataFrame(out)

def class_rows():
    """Customers billed in aggregate: the RT20 premises that are not billed individually, and residential. Monthly from the class forecast."""
    rows = []
    a25 = ALL[(ALL.rc == 'RT20')].fy25.sum() / G
    rem25 = BYC['RT20']['fy25'] - a25
    def mk(name, classes, fy25, fy26, m27, m28):
        d = dict(kam='Billed in aggregate', base='', customer=name, industry='', classes=classes, accounts=0, fy25=fy25, fy26=fy26, fy27=sum(m27), fy28=sum(m28), lr27=np.nan, lr28=np.nan,
                 base27=sum(m27), hot=0.0, adj=0.0, hot28=0.0, adj28=0.0, note='Class level: no individual billing data.')
        for i, m in enumerate(M27): d[m] = m27[i]
        for i, m in enumerate(M28): d[m] = m28[i]
        return d
    rows.append(mk('RT20 small commercial not billed individually (parish and bucket)', 'RT20', rem25, CLS['out']['RT20']['rem26'], [x / G for x in CLS['rem27']], [x / G for x in CLS['rem28']]))
    rows.append(mk('RT10 residential', 'RT10', BYC['RT10']['fy25'], BYC['RT10']['fy26'], CLS['rt10'], CLS['rt10_28']))
    return rows

def driver(r):
    p = [f'Trend {r.base27:.2f}']
    if abs(r.hot) >= 0.005: p.append(f'hotel recovery {sg(r.hot)}')
    if abs(r.adj) >= 0.005: p.append(f'adjustments and pipeline {sg(r.adj)}')
    s = 'FY2027: ' + ', '.join(p) + ' GWh'
    d28 = r.fy28 - r.fy27
    if abs(d28) >= 0.005: s += f'. FY2028 {sg(d28)} on FY2027'
    return s + (('. ' + r.note) if r.note else '')

def build(path, kam=None):
    ks = KAMS if kam is None else [kam]
    kdf = K[K.kam.isin(ks)]; cust = customers(kdf)
    master = kam is None
    wb = Workbook()
    R = wb.active; R.title = 'Read me'
    title(R, 'FY2027 and FY2028 forecast review' + ('' if master else f': {kam}'), 'Sales Forecasting and Analysis, November 2026. Actuals to October 2026.')
    lines = [('What this is', True),
        ('Our refreshed forecast for calendar 2027 and 2028, month by month for every customer, built from the latest billing and the trend since the storm. ' + ('The Total sales sheet and the Customer forecast sheet cover every customer, managed or not, and tie to company sales. ' if master else 'This file holds your portfolio; the company total is in the master file. ') + 'It replaces the forecast you saw in the October round. Nothing here has been entered in the platform yet: your feedback changes it first.', False),
        ('What we need from you, by [date]', True),
        ('1. Customer forecast: for each customer say Agree, or Change and enter your FY2027 and FY2028 GWh in the yellow columns. If the shape through the year is different, say so in the comment.', False),
        ('2. Adjustments and changes: every adjustment on file for your accounts, how we treated it, and the changes we made. Tell us Keep, Change or Remove.', False),
        ('3. Hotels: recovery by property. Give us the reopening date, and where a property is closed or rebuilding the date it returns.', False),
        ('4. New customers: confirm start month and monthly volume, or tell us the customer is not coming.', False),
        ('', False), ('How the forecast is built', True),
        ('Trend. Each account starts from its level in August to October 2026 (the middle of the three months, so one odd month does not drive it), shaped by the usual seasonal pattern. Commercial accounts grow 1% a year from April 2027 and again in 2028; small commercial and residential grow 0.8%.', False),
        ('Hotels. A hotel recovers part of the gap to its pre-storm level: 19% of the gap in January 2027, rising to 75% by December as the room stock reopens, then 76% to 80% through 2028. A property below 30% of its pre-storm level is treated as closed or rebuilding and gets no recovery until you give us a date.', False),
        ('Adjustments. The percentage entries on file are applied to the trend forecast and manual kWh are added, through 2028. Entries that were solved against the platform engine rather than entered at face value are replaced with the face-value profile.', False),
        ('New customers. Pipeline customers enter at their expected monthly volume from the start month.', False), ('', False), ('Sheets', True),
        (('Total sales, Customer forecast (every customer, monthly 2027 and 2028), Adjustments and changes, Hotels, New customers, Method.' if master else 'Customer forecast (monthly 2027 and 2028), Adjustments and changes, Hotels, New customers, Method.'), False)]
    for i, (t, b) in enumerate(lines, 4):
        R.cell(i, 1, t).font = F(bold=b, color=NAVY if b else '000000'); R.cell(i, 1).alignment = Alignment(wrap_text=True, vertical='top')
    R.column_dimensions['A'].width = 150

    # ---------------- customer rows ----------------
    order = {k: i for i, k in enumerate(KAMS)}
    cust = cust.assign(o=cust.kam.map(order)).sort_values(['o', 'fy27'], ascending=[True, False]).drop(columns='o')
    extra = []
    if master:
        un = customers(U, 'Not managed')
        big_u = un[un.fy27 >= 0.25].sort_values('fy27', ascending=False); small_u = U[~U.base_ac.isin(big_u.base)]
        extra.append(big_u)
        agg = []
        for c in ('RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70'):
            s = small_u[small_u.rc == c]
            if len(s): agg.append(cust_row('Not managed', f'All other not managed, {CN[c]} ({s.base_ac.nunique():,} customers)', '', '', c, len(s), s))
        extra.append(pd.DataFrame(agg)); extra.append(pd.DataFrame(class_rows()))
    allc = pd.concat([cust] + extra, ignore_index=True) if extra else cust

    # ---------------- total sales ----------------
    if master:
        T0 = wb.create_sheet('Total sales', 1)
        title(T0, 'Total sales, GWh billed including prepaid', 'FY2026 is January to October actual plus our November and December forecast. FY2025 includes the storm months. Every customer is in one of the groups below.')
        header(T0, 4, ['Group', 'FY2025 actual', 'FY2026 outlook', 'FY2027 forecast', 'Growth on FY2026', 'FY2028 forecast', 'Growth on FY2027', 'FY2027 last round', 'FY2028 last round'], [48, 13, 13, 13, 12, 13, 12, 13, 13])
        r = 5
        def line(label, d, bold=False, lr=True):
            nonlocal r
            vals = [label, d['fy25'], d['fy26'], d['fy27'], (d['fy27'] / d['fy26'] - 1) if d['fy26'] else None, d['fy28'], (d['fy28'] / d['fy27'] - 1) if d['fy27'] else None, d.get('lr27') if lr else None, d.get('lr28') if lr else None]
            for j, v in enumerate(vals, 1):
                x = T0.cell(r, j, None if (isinstance(v, float) and np.isnan(v)) else v); x.font = F(bold=bold)
                if j >= 2: x.number_format = '0.0%' if j in (5, 7) else '#,##0.0'
            r += 1
        T0.cell(r, 1, 'Managed by a KAM').font = F(bold=True, color=NAVY); r += 1; first = r
        for k in KAMS:
            g = K[K.kam == k]; line('   ' + k, dict(fy25=g.fy25.sum() / G, fy26=g.fy26_out.sum() / G, fy27=g.fy27.sum() / G, fy28=g.fy28.sum() / G, lr27=g.lr27.sum() / G, lr28=g.lr28.sum() / G))
        last = r - 1
        mrow = r; T0.cell(r, 1, 'Total managed').font = F(bold=True)
        for j in (2, 3, 4, 6, 8, 9): x = T0.cell(r, j, f'=SUM({CL(j)}{first}:{CL(j)}{last})'); x.font = F(bold=True); x.number_format = '#,##0.0'
        T0.cell(r, 5, f'=D{r}/C{r}-1').number_format = '0.0%'; T0.cell(r, 7, f'=F{r}/D{r}-1').number_format = '0.0%'; r += 2
        T0.cell(r, 1, 'Not managed').font = F(bold=True, color=NAVY); r += 1; f2 = r
        for c in ('RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70'):
            s = U[U.rc == c]
            if len(s): line(f'   {CN[c]}, billed individually', dict(fy25=s.fy25.sum() / G, fy26=s.fy26_out.sum() / G, fy27=s.fy27.sum() / G, fy28=s.fy28.sum() / G), lr=False)
        urow = r; T0.cell(r, 1, 'Total not managed').font = F(bold=True)
        for j in (2, 3, 4, 6): x = T0.cell(r, j, f'=SUM({CL(j)}{f2}:{CL(j)}{r - 1})'); x.font = F(bold=True); x.number_format = '#,##0.0'
        T0.cell(r, 5, f'=D{r}/C{r}-1').number_format = '0.0%'; T0.cell(r, 7, f'=F{r}/D{r}-1').number_format = '0.0%'; r += 2
        T0.cell(r, 1, 'Billed in aggregate').font = F(bold=True, color=NAVY); r += 1; f3 = r
        for d in class_rows(): line('   ' + d['customer'], dict(fy25=d['fy25'], fy26=d['fy26'], fy27=d['fy27'], fy28=d['fy28']), lr=False)
        arow = r; T0.cell(r, 1, 'Total billed in aggregate').font = F(bold=True)
        for j in (2, 3, 4, 6): x = T0.cell(r, j, f'=SUM({CL(j)}{f3}:{CL(j)}{r - 1})'); x.font = F(bold=True); x.number_format = '#,##0.0'
        T0.cell(r, 5, f'=D{r}/C{r}-1').number_format = '0.0%'; T0.cell(r, 7, f'=F{r}/D{r}-1').number_format = '0.0%'; r += 2
        T0.cell(r, 1, 'Total sales').font = F(bold=True, size=11)
        for j in (2, 3, 4, 6): x = T0.cell(r, j, f'={CL(j)}{mrow}+{CL(j)}{urow}+{CL(j)}{arow}'); x.font = F(bold=True, size=11); x.number_format = '#,##0.0'
        T0.cell(r, 5, f'=D{r}/C{r}-1').number_format = '0.0%'; T0.cell(r, 7, f'=F{r}/D{r}-1').number_format = '0.0%'; trow = r; r += 3
        # by rate class against the plan
        T0.cell(r, 1, 'Total sales by rate class against the plan').font = F(bold=True, color=NAVY); r += 1
        hdr2 = ['Rate class', 'FY2025 actual', 'FY2026 outlook', 'FY2027 forecast', 'FY2027 plan', 'Forecast less plan', 'FY2028 forecast', 'FY2028 plan', 'Forecast less plan']
        for j, h in enumerate(hdr2, 1):
            c = T0.cell(r, j, h); c.font = F(bold=True, color='FFFFFF'); c.fill = fill(NAVY); c.alignment = Alignment(horizontal='center', wrap_text=True)
        r += 1; fc = r
        for c in ('RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70'):
            o = CLS['out'][c]; f27 = o.get('total27', o.get('acct27', 0) + o.get('rem27', 0)); f26 = o.get('total26', o.get('acct26', 0) + o.get('rem26', 0)); f28 = o.get('total28', o.get('acct28', 0) + o.get('rem28', 0))
            h27 = sum(LE[c]['%s 27' % m] for m in MON); h28 = sum(LE[c]['%s 28' % m] for m in MON)
            for j, v in enumerate([CN[c], BYC[c]['fy25'], f26, f27, h27, None, f28, h28, None], 1):
                x = T0.cell(r, j, v); x.font = F()
                if j >= 2: x.number_format = '#,##0.0'
            T0.cell(r, 6, f'=D{r}-E{r}').number_format = '+#,##0.0;-#,##0.0'; T0.cell(r, 9, f'=G{r}-H{r}').number_format = '+#,##0.0;-#,##0.0'; r += 1
        T0.cell(r, 1, 'Total').font = F(bold=True)
        for j in (2, 3, 4, 5, 7, 8): x = T0.cell(r, j, f'=SUM({CL(j)}{fc}:{CL(j)}{r - 1})'); x.font = F(bold=True); x.number_format = '#,##0.0'
        T0.cell(r, 6, f'=D{r}-E{r}').number_format = '+#,##0.0;-#,##0.0'; T0.cell(r, 9, f'=G{r}-H{r}').number_format = '+#,##0.0;-#,##0.0'
        T0.cell(r + 1, 1, f'Check: total sales above less total by rate class').font = F(italic=True, color=GREY); x = T0.cell(r + 1, 4, f'=D{trow}-D{r}'); x.number_format = '0.0'; x.font = F(italic=True, color=GREY)
        # monthly total
        r += 4
        T0.cell(r, 1, 'Total sales by month, GWh').font = F(bold=True, color=NAVY); r += 1
        hh = ['Rate class'] + [m + ' 27' for m in MON] + ['FY2027'] + [m + ' 28' for m in MON] + ['FY2028']
        for j, h in enumerate(hh, 1):
            c = T0.cell(r, j, h); c.font = F(bold=True, color='FFFFFF'); c.fill = fill(NAVY); c.alignment = Alignment(horizontal='center')
            if j > 9: T0.column_dimensions[CL(j)].width = 9
        r += 1; fm = r
        for c in ('RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70'):
            if c == 'RT10': m27, m28 = CLS['rt10'], CLS['rt10_28']
            else:
                s = ALL[ALL.rc == c]; m27 = [s[m].sum() / G for m in M27]; m28 = [s[m].sum() / G for m in M28]
                if c == 'RT20': m27 = [a + b / G for a, b in zip(m27, CLS['rem27'])]; m28 = [a + b / G for a, b in zip(m28, CLS['rem28'])]
            T0.cell(r, 1, CN[c]).font = F()
            for j, v in enumerate(m27, 2): num(T0, r, j, v, '#,##0.0')
            x = T0.cell(r, 14, f'=SUM(B{r}:M{r})'); x.number_format = '#,##0.0'; x.font = F(bold=True)
            for j, v in enumerate(m28, 15): num(T0, r, j, v, '#,##0.0')
            x = T0.cell(r, 27, f'=SUM(O{r}:Z{r})'); x.number_format = '#,##0.0'; x.font = F(bold=True); r += 1
        T0.cell(r, 1, 'Total').font = F(bold=True)
        for j in range(2, 28): x = T0.cell(r, j, f'=SUM({CL(j)}{fm}:{CL(j)}{r - 1})'); x.number_format = '#,##0.0'; x.font = F(bold=True)

    # ---------------- customer forecast ----------------
    C = wb.create_sheet('Customer forecast')
    title(C, 'Forecast by customer, GWh a month' + (': total sales' if master else ''), 'All accounts of the customer together. Yellow columns are yours.' + (' Managed customers first, then customers not managed, then customers billed in aggregate; the total ties to company sales.' if master else ''))
    heads = ['Managed by', 'Customer', 'Customer no', 'Industry', 'Rate classes', 'Accounts', 'FY2025 actual', 'FY2026 outlook'] + [m + ' 27' for m in MON] + ['FY2027 forecast', 'Growth on FY2026', 'FY2027 last round', 'Change since last round'] + [m + ' 28' for m in MON] + ['FY2028 forecast', 'Growth on FY2027', 'FY2028 last round', 'Change since last round', 'What drives it', 'KAM response', 'KAM FY2027 GWh (if changed)', 'KAM FY2028 GWh (if changed)', 'KAM comment']
    header(C, 4, heads, [20, 40, 11, 26, 14, 9, 11, 11] + [8.5] * 12 + [12, 11, 12, 12] + [8.5] * 12 + [12, 11, 12, 12, 70, 14, 14, 14, 50])
    dv = DataValidation(type='list', formula1='"Agree,Change"', allow_blank=True); C.add_data_validation(dv)
    for i, c in enumerate(allc.itertuples(), 5):
        for j, v in enumerate([c.kam, c.customer, c.base, c.industry, c.classes, c.accounts if c.accounts else None], 1): C.cell(i, j, v).font = F()
        num(C, i, 7, c.fy25); num(C, i, 8, c.fy26)
        for j, m in enumerate(M27): num(C, i, 9 + j, getattr(c, m))
        num(C, i, 21, c.fy27, bold=True); num(C, i, 22, (c.fy27 / c.fy26 - 1) if c.fy26 > 0.005 else None, '0.0%')
        num(C, i, 23, c.lr27); num(C, i, 24, (c.fy27 - c.lr27) if not np.isnan(c.lr27) else None)
        for j, m in enumerate(M28): num(C, i, 25 + j, getattr(c, m))
        num(C, i, 37, c.fy28, bold=True); num(C, i, 38, (c.fy28 / c.fy27 - 1) if c.fy27 > 0.005 else None, '0.0%')
        num(C, i, 39, c.lr28); num(C, i, 40, (c.fy28 - c.lr28) if not np.isnan(c.lr28) else None)
        C.cell(i, 41, driver(c)).font = F(size=9); C.cell(i, 41).alignment = Alignment(wrap_text=True, vertical='top')
        if c.kam not in ('Billed in aggregate', 'Not managed') or master and c.kam == 'Not managed':
            inp(C, i, 42); dv.add(C.cell(i, 42)); inp(C, i, 43); inp(C, i, 44); inp(C, i, 45)
    n = len(allc); tr_ = 5 + n
    C.cell(tr_, 2, 'Total' + (' sales' if master else ' portfolio')).font = F(bold=True)
    for j in [7, 8] + list(range(9, 22)) + list(range(25, 38)):
        x = C.cell(tr_, j, f'=SUM({CL(j)}5:{CL(j)}{tr_ - 1})'); x.font = F(bold=True); x.number_format = '#,##0.00'
    C.freeze_panes = 'C5'; C.auto_filter.ref = f'A4:{CL(len(heads))}{4 + n}'

    # ---------------- adjustments and changes ----------------
    E = ENT[ENT.kam.isin(ks)].copy(); E['mm'] = E.y * 12 + E.m; E = E.sort_values(['kam', 'customer', 'mm'])
    A = wb.create_sheet('Adjustments and changes')
    title(A, f'Adjustments on file and our changes ({len(E)} entries)', 'The treatment says what we did with each entry; where we changed or replaced it the reason is in the last-but-three column. Effect is the whole account, so rows for the same account share it and should not be added.')
    heads = ['KAM', 'Customer', 'Account', 'Month', 'Adjustment %', 'Manual kWh', 'Reason on file', 'How we treated it', 'What we did and why', 'Account effect FY2027 (GWh)', 'Account effect FY2028 (GWh)', 'Justification on file', 'KAM response', 'KAM new % or kWh', 'KAM comment']
    header(A, 4, heads, [20, 30, 16, 9, 11, 11, 20, 30, 70, 14, 14, 60, 14, 14, 40])
    dv2 = DataValidation(type='list', formula1='"Keep,Change,Remove"', allow_blank=True); A.add_data_validation(dv2)
    rows_ = []
    for e in E.itertuples():
        why = META['OVERRIDE'].get(str(e.account), '') if e.treat == 'Replaced by analyst override' else ('Class-wide storm recovery entry replaced by hotel recovery by property (Hotels sheet).' if 'hotel recovery' in e.treat else '')
        rows_.append([e.kam, e.customer, e.account, f'{MON[e.m - 1]} {str(e.y)[2:]}', e.pct, e.kwh, e.reason, e.treat, why, e.acct_adj27 / G, e.acct_adj28 / G, str(e.justification)[:400]])
    have = set(E.account.astype(str))
    for ac, why in list(META['OVERRIDE'].items()) + [('793321-1224323', ALL.at['793321-1224323', 'note'] if '793321-1224323' in ALL.index else '')]:
        if ac in ALL.index and ac not in have and ALL.at[ac, 'kam'] in ks:
            rows_.append([ALL.at[ac, 'kam'], ALL.at[ac, 'name'], ac, '', None, None, 'No entry on file', 'Analyst change', why, ALL.at[ac, 'adj27'] / G, ALL.at[ac, 'adj28'] / G, ''])
    for i, r in enumerate(rows_, 5):
        for j, v in enumerate(r, 1):
            x = A.cell(i, j, v); x.font = F(size=9 if j in (9, 12) else 10)
            if j in (10, 11): x.number_format = '#,##0.00'
            if j in (9, 12): x.alignment = Alignment(wrap_text=True, vertical='top')
        inp(A, i, 13); dv2.add(A.cell(i, 13)); inp(A, i, 14); inp(A, i, 15)
    A.freeze_panes = 'D5'

    # ---------------- hotels ----------------
    H = wb.create_sheet('Hotels')
    hh = HOT[HOT.kam.isin(ks)].copy(); hh['pct'] = hh.level / hh.ps.replace(0, np.nan)
    title(H, 'Hotel recovery by property', 'Pre-storm is the average month January to September 2025. Current is the middle month of August to October 2026. Recovery follows the reopening schedule: 19% of the gap in January 2027 rising to 75% in December, then 76% to 80% through 2028.')
    heads = ['KAM', 'Customer', 'Account', 'Rate class', 'Pre-storm MWh a month', 'Current MWh a month', 'Current as % of pre-storm', 'What we assumed', 'FY2027 recovery (GWh)', 'FY2028 recovery (GWh)', 'KAM reopening date', 'KAM expected % of pre-storm by Dec 27', 'KAM comment']
    header(H, 4, heads, [20, 34, 16, 9, 12, 12, 12, 58, 13, 13, 16, 16, 40])
    hh = hh[hh.ps > 0].sort_values(['kam', 'hotel_up27'], ascending=[True, False])
    for i, h in enumerate(hh.itertuples(), 5):
        what = ('Recovery applied' if h.hotel_up27 > 0 else ('Below 30% of pre-storm: treated as closed or rebuilding, no recovery until you give a date' if h.pct < 0.3 else 'At or above pre-storm: no recovery'))
        for j, v in enumerate([h.kam if h.kam else 'Not managed', h.name, h.Index, h.rc], 1): H.cell(i, j, v).font = F()
        num(H, i, 5, h.ps / 1000, '#,##0'); num(H, i, 6, h.level / 1000, '#,##0'); num(H, i, 7, h.pct, '0%'); H.cell(i, 8, what).font = F(size=9); num(H, i, 9, h.hotel_up27 / G); num(H, i, 10, h.hotel_up28 / G)
        inp(H, i, 11); inp(H, i, 12); inp(H, i, 13)

    # ---------------- new customers ----------------
    N = wb.create_sheet('New customers')
    title(N, 'Pipeline customers in the forecast', 'On file is what was entered. Modelled is what this forecast uses.')
    heads = ['KAM', 'Customer', 'Rate class', 'On file: start', 'On file: MWh a month', 'Modelled: start', 'Modelled: MWh a month', 'FY2027 modelled (GWh)', 'FY2028 modelled (GWh)', 'Note', 'KAM response', 'KAM start month', 'KAM MWh a month', 'KAM comment']
    header(N, 4, heads, [20, 34, 9, 12, 12, 12, 12, 12, 12, 70, 14, 12, 12, 40])
    dv4 = DataValidation(type='list', formula1='"Agree,Change,Not coming"', allow_blank=True); N.add_data_validation(dv4)
    rr = 5
    for n_ in META['newc']:
        kk = ALL.at[n_['jps_ac'], 'kam'] if n_['jps_ac'] in ALL.index and ALL.at[n_['jps_ac'], 'kam'] else (n_['kam'] or '')
        if kam is not None and kk != kam: continue
        fx = META['NEWC_FIX'].get(str(n_['id'])); on = f"{MON[int(n_['start_month']) - 1]} {str(n_['start_year'])[2:]}"
        if fx and fx[2] is None: mod_s, mod_k, g27, g28 = 'Dropped', 0, 0.0, 0.0
        else:
            mod_s, mod_k = (f'{MON[fx[1] - 1]} {str(fx[0])[2:]}', fx[2]) if fx else (on, float(n_['expected_kwh']))
            g27 = ALL.at[n_['jps_ac'], 'fy27'] / G if n_['jps_ac'] in ALL.index else 0; g28 = ALL.at[n_['jps_ac'], 'fy28'] / G if n_['jps_ac'] in ALL.index else 0
        for j, v in enumerate([kk or 'Not managed', n_['name'], n_['rate_class'], on, float(n_['expected_kwh']) / 1000, mod_s, mod_k / 1000 if isinstance(mod_k, (int, float)) else mod_k, g27, g28, (fx[3] if fx else 'As entered.')], 1): N.cell(rr, j, v).font = F()
        N.cell(rr, 10).alignment = Alignment(wrap_text=True, vertical='top')
        for j in (5, 7): N.cell(rr, j).number_format = '#,##0'
        for j in (8, 9): N.cell(rr, j).number_format = '#,##0.00'
        inp(N, rr, 11); dv4.add(N.cell(rr, 11)); inp(N, rr, 12); inp(N, rr, 13); inp(N, rr, 14); rr += 1

    M = wb.create_sheet('Method')
    for i, t in enumerate([
        'Forecast: calendar 2027 and 2028, GWh billed including prepaid. Actuals to October 2026. Account level for every commercial account, managed or not; class level for residential and for the small commercial accounts that are not billed individually.',
        'Trend level: the middle of an account\'s August, September and October 2026 kWh. Seasonal shape: the average pattern of 2024 and 2025 (75% weight on 2025), both before the storm. October to December 2027 follow the October level and the 2024 October to December pattern. 2028 is the same month of 2027 grown by the annual rate.',
        'Growth: commercial 0% January to March 2027 and 1% from April; 1% again in 2028. Small commercial and residential 0.8% a year. Street lighting and industrial accounts are held flat apart from adjustments.',
        'Hotels: share of the gap to pre-storm recovered, 19% in January 2027 rising to 75% in December and 76% to 80% through 2028. Properties below 30% of pre-storm get none until a reopening date is given.',
        'Adjustments: percentage entries apply to the trend forecast and manual kWh are added, as in the platform, through 2028. Entries solved against the engine base (Petrojam shutdown) and the class-wide storm recovery entries are replaced.',
        'Last round: the account forecast in the October round workbook (actuals to September). It covered managed customers only.',
        ('Total sales ties to the company total by construction: managed customers, plus customers not managed, plus customers billed in aggregate, equal total sales by rate class.' if master else 'Portfolio totals in this file cover your customers only and do not add to company sales.'),
    ], 1): M.cell(i, 1, t).font = F(); M.cell(i, 1).alignment = Alignment(wrap_text=True, vertical='top')
    M.column_dimensions['A'].width = 150
    wb.save(path)
    return len(allc)

if __name__ == '__main__':
    n = build(OUT + r'\JPS_KAM_Forecast_Review_FY2027-28_Master.xlsx'); print('master rows', n)
    for k in KAMS:
        nn = build(OUT + r'\JPS_KAM_Forecast_Review_FY2027-28_%s.xlsx' % re.sub(r'[^A-Za-z]+', '_', k).strip('_'), k); print(k, nn)
