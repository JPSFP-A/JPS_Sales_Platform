# -*- coding: utf-8 -*-
# KAM forecast round kick-off deck (JPS Corporate Performance Report template).
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_TICK_LABEL_POSITION, XL_TICK_MARK, XL_LEGEND_POSITION
from kam_model import *

SRC = r'C:\Users\jwilson\Downloads\September 2026 Corporate Performance Report.pptx'
OUT = r'C:\Projects\Sales_Platform\JPS_KAM_Forecast_Round_Oct2026_v2.pptx'
NAVY, BLUE, CYAN, GREY, LIGHT = RGBColor(0x06, 0x25, 0x52), RGBColor(0x0E, 0x4E, 0x95), RGBColor(0x00, 0x9F, 0xDA), RGBColor(0x66, 0x78, 0x8A), RGBColor(0xD9, 0xE1, 0xF2)
RED, GREEN, WHITE, BLACK = RGBColor(0xC0, 0x00, 0x00), RGBColor(0x2E, 0x7D, 0x52), RGBColor(0xFF, 0xFF, 0xFF), RGBColor(0x1F, 0x1F, 0x1F)
F_GOOD, F_MID, F_BAD, F_ALT = RGBColor(0xDD, 0xEF, 0xDF), RGBColor(0xFF, 0xF0, 0xC8), RGBColor(0xF6, 0xD3, 0xD6), RGBColor(0xF3, 0xF6, 0xFB)
FONT = 'Arial'

prs = Presentation(SRC)
cover = [l for l in prs.slide_layouts if l.name.strip() == 'PowerPoint Cover 1'][0]
layout = [l for l in prs.slide_layouts if l.name.strip() == 'Content Slide 1'][0]
sld = prs.slides._sldIdLst
for sldId in list(sld):
    prs.part.drop_rel(sldId.rId); sld.remove(sldId)
page = [0]

def tb(slide, x, y, w, h, text='', size=11, bold=False, color=BLACK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    s = slide.shapes.add_textbox(Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h))); tf = s.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Emu(0); tf.vertical_anchor = anchor
    lines = text if isinstance(text, list) else [text]
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.alignment = align
        runs = ln if isinstance(ln, list) else [(ln, bold, color)]
        for t, b, c in runs:
            r = p.add_run(); r.text = t; r.font.name = FONT; r.font.size = Pt(size); r.font.bold = b; r.font.color.rgb = c
    return s
def rect(slide, x, y, w, h, fill=None, line=None, lw=0.75, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    if fill is None: s.fill.background()
    else: s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None: s.line.fill.background()
    else: s.line.color.rgb = line; s.line.width = Pt(lw)
    s.shadow.inherit = False
    return s
def new_slide(title, headline, sub):
    s = prs.slides.add_slide(layout)
    for ph in list(s.placeholders): ph._element.getparent().remove(ph._element)
    page[0] += 1
    tb(s, 711812, 493325, 11000000, 523220, title, 28, True, NAVY)
    tb(s, 815243, 1079336, 11200000, 330000, headline, 16, True, BLUE)
    if sub: tb(s, 815243, 1500000, 11200000, 300000, sub, 11, False, GREY)
    tb(s, 469231, 6411345, 6621379, 266676, 'Jamaica Public Service | Key Account Forecast Review | October 2026', 9, True, NAVY)
    tb(s, 186473, 6413496, 287140, 265842, str(page[0]), 9, True, NAVY)
    return s
def cell_set(c, text, size=9, bold=False, color=BLACK, align=PP_ALIGN.CENTER, fill=None):
    c.text = ''; tf = c.text_frame; tf.word_wrap = True; p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = text; r.font.name = FONT; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color
    c.margin_left = c.margin_right = Emu(54000); c.margin_top = c.margin_bottom = Emu(18000); c.vertical_anchor = MSO_ANCHOR.MIDDLE
    if fill is None: c.fill.background()
    else: c.fill.solid(); c.fill.fore_color.rgb = fill
def table(slide, x, y, w, colw, head, rows, row_h=300000, size=9, left_cols=(0,), total=False, colors=None, head_h=320000):
    nr, nc = len(rows) + 1, len(head)
    gf = slide.shapes.add_table(nr, nc, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(row_h * len(rows) + head_h))); t = gf.table
    tblPr = gf._element.graphic.graphicData.tbl.tblPr
    for a in ('bandRow', 'firstRow'): tblPr.set(a, '0')
    sid = tblPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}tableStyleId')
    if sid is not None: sid.text = '{5940675A-B579-460E-94D1-54222C63F5DA}'
    tot = sum(colw)
    for j, cw in enumerate(colw): t.columns[j].width = Emu(int(w * cw / tot))
    t.rows[0].height = Emu(head_h)
    for i in range(1, nr): t.rows[i].height = Emu(row_h)
    for j, h in enumerate(head): cell_set(t.cell(0, j), h, size, True, WHITE, PP_ALIGN.LEFT if j in left_cols else PP_ALIGN.CENTER, NAVY)
    for i, row in enumerate(rows, 1):
        last = total and i == len(rows)
        for j, v in enumerate(row):
            fill = NAVY if last else (F_ALT if i % 2 == 0 else None)
            col = WHITE if last else (colors[i - 1][j] if colors and colors[i - 1][j] is not None else (NAVY if j in left_cols and j == 0 else BLACK))
            cell_set(t.cell(i, j), v, size, last or (j == 0), col, PP_ALIGN.LEFT if j in left_cols else PP_ALIGN.CENTER, fill)
    return t
def card(slide, x, y, w, h, label, big, sub, color=BLUE):
    rect(slide, x, y, w, h, None, LIGHT, 0.9); rect(slide, x, y, w, 45719, color)
    tb(slide, x + 130000, y + 110000, w - 260000, 170000, label, 9, True, GREY)
    tb(slide, x + 130000, y + 330000, w - 260000, 420000, big, 22, True, NAVY)
    tb(slide, x + 130000, y + 800000, w - 260000, h - 850000, sub, 9.5, False, BLACK)
def callout(slide, x, y, w, h, head, body, size=10.5):
    rect(slide, x, y, w, h, LIGHT); rect(slide, x, y, 54000, h, BLUE)
    tb(slide, x + 160000, y + 80000, w - 260000, h - 120000, [[(head + ' ', True, NAVY), (body, False, BLACK)]], size)
def box(slide, x, y, w, h, head, lines, size=10, color=BLUE):
    rect(slide, x, y, w, h, None, LIGHT, 0.9); rect(slide, x, y, w, 45719, color)
    tb(slide, x + 130000, y + 100000, w - 260000, 190000, head, 10, True, GREY)
    tb(slide, x + 130000, y + 340000, w - 260000, h - 380000, lines, size)
f1 = lambda v: format(v, ',.1f')
f2 = lambda v: format(v, ',.2f')
def sg(v, d=1):
    if round(abs(v), d) == 0: return format(0, ',.%df' % d)
    return ('+' if v > 0 else MINUS) + format(abs(v), ',.%df' % d)
def pcs(v, d=1): return sg(v * 100, d) + '%'
col = lambda v: RED if v < 0 else BLUE
def acc_fill(v): return F_GOOD if v >= 0.95 else (F_MID if v >= 0.85 else F_BAD)

# ================= 2 asks =================
n_adj, n_kam_by, n_sf = len(adj), sum(1 for a in adj if a['by'] == 'KAM'), sum(1 for a in adj if a['by'] != 'KAM')
n_up_acc = len({g['ac'] for g in UPCOMING})
s = new_slide('What We Need From You', 'Review what we hold for your accounts, correct it, and tell us what we are missing', 'The account workbook has one sheet for each ask, with a yellow column to respond in.')
xs = [274320, 4250000, 8225000]; w = 3750000
asks = [('1  CONFIRM THE ADJUSTMENTS', f'{len(UPCOMING)} adjustments', f'coming up on {n_up_acc} accounts. Keep, change or remove each one in the Adjustments sheet. {n_sf} of the {n_adj} monthly entries on file were made by Sales Forecasting, not by a KAM, so they need your confirmation most.'),
        ('2  CONFIRM WHAT IS PERMANENT', f'{len(ROLL_CUST)} customers', 'have a defection, expansion or renewal entry that now carries forward to December 2028 until the next entry. Tell us which are permanent and which should end.'),
        ('3  TELL US WHAT IS MISSING', 'Gaps and changes', 'New connections, closures, solar or self-generation, expansions. Add them in the Portfolio forecast sheet, and confirm the 13 pipeline customers.')]
for x, (lab, big, sub) in zip(xs, asks): card(s, x, 2000000, w, 2400000, lab, big, sub)
callout(s, 274320, 4750000, 11650000, 1100000, 'Why now.', f'September came in 9.1 GWh above the company forecast and {sum(1 for a in MISSES if abs(a["sep_act"] - a["sep_fc"]) > 0.05)} accounts in your portfolios missed by more than 0.05 GWh. The next forecast round starts from the adjustments on file, so any that are wrong or missing carry straight into FY2027 and FY2028.')

# ================= 3 accuracy by KAM =================
net_t, acc_t = net_acc(TOT['sep_fc'], TOT['sep_act']), acct_acc(TOT['sep_abs'], TOT['sep_act'])
s = new_slide('Forecast Accuracy: Last Round', f'September was forecast to {net_t * 100:.0f}% in total, but only {acc_t * 100:.0f}% account by account',
              f'Forecast = account forecast after the August close. Actual = September billed sales. Assigned commercial accounts, {f1(TOT["sep_act"])} GWh of the {f1(294.805)} GWh company total.')
rows, colors = [], []
for k in KAMS_SORTED:
    P = PORT[k]; n_ = net_acc(P['sep_fc'], P['sep_act']); a_ = acct_acc(P['sep_abs'], P['sep_act'])
    rows.append([k, f'{P["accounts"]:,}', f2(P['sep_fc']), f2(P['sep_act']), sg(P['sep_act'] - P['sep_fc'], 2), f'{n_ * 100:.0f}%', f'{a_ * 100:.0f}%']); colors.append([None, None, None, None, col(P['sep_act'] - P['sep_fc']), None, None])
rows.append(['Total assigned', f'{TOT["accounts"]:,}', f2(TOT['sep_fc']), f2(TOT['sep_act']), sg(TOT['sep_act'] - TOT['sep_fc'], 2), f'{net_t * 100:.1f}%', f'{acc_t * 100:.1f}%'])
t = table(s, 274320, 1950000, 7200000, [2.2, 0.9, 1.0, 1.0, 1.0, 0.9, 1.1], ['KAM', 'Accounts', 'Forecast', 'Actual', 'Variance', 'Net', 'Account level'], rows, row_h=322000, total=True, colors=colors + [[None] * 7])
for i, k in enumerate(KAMS_SORTED, 1):
    P = PORT[k]
    for j, v in ((5, net_acc(P['sep_fc'], P['sep_act'])), (6, acct_acc(P['sep_abs'], P['sep_act']))):
        c = t.cell(i, j); c.fill.solid(); c.fill.fore_color.rgb = acc_fill(v)
cd = CategoryChartData(); cd.categories = [k.split(' ')[0] for k in reversed(KAMS_SORTED)]
cd.add_series('Account level', [acct_acc(PORT[k]['sep_abs'], PORT[k]['sep_act']) for k in reversed(KAMS_SORTED)])
cd.add_series('Net', [net_acc(PORT[k]['sep_fc'], PORT[k]['sep_act']) for k in reversed(KAMS_SORTED)])
cx, cy, cw, ch = 7750000, 1950000, 4250000, 3300000
rect(s, cx - 60000, cy - 40000, cw + 120000, ch + 80000, None, LIGHT, 0.9); rect(s, cx - 60000, cy - 40000, cw + 120000, 45719, BLUE)
tb(s, cx + 40000, cy + 30000, cw, 200000, 'ACCURACY BY KAM, SEPTEMBER', 10, True, GREY)
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Emu(cx), Emu(cy + 250000), Emu(cw), Emu(ch - 270000), cd); chart = gf.chart
chart.has_title = False; chart.has_legend = True; chart.legend.include_in_layout = False; chart.legend.position = XL_LEGEND_POSITION.BOTTOM; chart.legend.font.size = Pt(9); chart.legend.font.name = FONT
plot = chart.plots[0]; plot.gap_width = 45; plot.overlap = -5
for ser, c_ in zip(plot.series, (CYAN, NAVY)): ser.format.fill.solid(); ser.format.fill.fore_color.rgb = c_; ser.invert_if_negative = False
plot.has_data_labels = True; dl = plot.data_labels; dl.number_format = '0%'; dl.number_format_is_linked = False; dl.font.size = Pt(8); dl.font.name = FONT; dl.position = XL_LABEL_POSITION.OUTSIDE_END
chart.category_axis.tick_labels.font.size = Pt(9); chart.category_axis.tick_labels.font.name = FONT; chart.category_axis.has_major_gridlines = False
va = chart.value_axis; va.has_major_gridlines = False; va.minimum_scale = 0; va.maximum_scale = 1.15; va.tick_label_position = XL_TICK_LABEL_POSITION.NONE; va.major_tick_mark = XL_TICK_MARK.NONE
callout(s, 274320, 5560000, 11650000, 700000, 'Reading it.', f'Net accuracy is high because over and under misses cancel inside a portfolio. Account level adds up every miss and is the better test of whether each account forecast is right: Ruel Barnett nets to 100% but is {acct_acc(PORT["Ruel Barnett"]["sep_abs"], PORT["Ruel Barnett"]["sep_act"]) * 100:.0f}% account by account.', 10.5)

# ================= 4 misses =================
top = MISSES[:10]
share = sum(abs(a['sep_act'] - a['sep_fc']) for a in MISSES[:5]) / TOT['sep_abs']
n_miss = sum(1 for a in MISSES if abs(a['sep_act'] - a['sep_fc']) > 0.05)
notes = {'Caribbean Broilers Ja Ltd': 'Two periods billed in August, a stub in September', 'Alcoa Mins Of Ja Ltd': 'Entered at \u2212100% from August; 0.6 GWh still billed'}
s = new_slide('Where The Misses Were', f'Five accounts make up {share * 100:.0f}% of the total miss; {n_miss} accounts missed by more than 0.05 GWh',
              'September, GWh. Variance is actual less forecast. The full list is in the Sept account misses sheet.')
rows = [[a['name'][:34], a['kam'] or 'Not assigned', a['rc'], f2(a['sep_fc']), f2(a['sep_act']), sg(a['sep_act'] - a['sep_fc'], 2), notes.get(a['name'], 'KAM to explain')] for a in top]
colors = [[None, None, None, None, None, col(a['sep_act'] - a['sep_fc']), None] for a in top]
table(s, 274320, 1950000, 11650000, [2.6, 1.5, 0.7, 0.9, 0.9, 0.9, 3.2], ['Account', 'KAM', 'Class', 'Forecast', 'Actual', 'Variance', 'What we know'], rows, row_h=315000, left_cols=(0, 1, 6), colors=colors)
callout(s, 274320, 5500000, 11650000, 760000, 'What to bring.', 'For each account above and in the sheet, the reason for the miss and whether it repeats. A one-off (billing timing, an outage) should not change the forecast; a lasting change should be entered as an adjustment for every month it applies.', 10.5)

# ================= 5 forward forecast =================
s = new_slide('The Forecast You Have Given Us', f'Assigned portfolios go from {f1(TOT["live"][0])} GWh in FY2026 to {f1(TOT["live"][1])} in FY2027 and {f1(TOT["live"][2])} in FY2028',
              'Live account forecast with September actuals and all adjustments on file. FY2026 is January to September actual plus forecast. Commercial assigned accounts only.')
rows, colors = [], []
for k in KAMS_SORTED:
    P = PORT[k]; l = P['live']
    rows.append([k, f'{P["customers"]}', f1(P['fy25']), f1(l[0]), f1(l[1]), pcs(l[1] / l[0] - 1), f1(l[2]), pcs(l[2] / l[1] - 1), sg(l[1] - P['prev'][1])])
    colors.append([None, None, None, None, None, col(l[1] - l[0]), None, col(l[2] - l[1]), col(l[1] - P['prev'][1])])
l = TOT['live']
rows.append(['Total assigned', f'{sum(p["customers"] for p in PORT.values())}', f1(TOT['fy25']), f1(l[0]), f1(l[1]), pcs(l[1] / l[0] - 1), f1(l[2]), pcs(l[2] / l[1] - 1), sg(l[1] - TOT['prev'][1])])
table(s, 274320, 1950000, 11650000, [2.2, 0.9, 1.0, 1.0, 1.0, 0.9, 1.0, 0.9, 1.3], ['KAM', 'Customers', 'FY2025', 'FY2026', 'FY2027', 'YoY', 'FY2028', 'YoY', 'FY2027 vs last round'], rows, row_h=290000, total=True, colors=colors + [[None] * 9])
callout(s, 274320, 5700000, 11650000, 650000, 'Note.', 'Portfolios cover assigned commercial accounts only, so they do not add to company sales, which also include residential and unassigned accounts. Last round is the forecast after the August close, before adjustments rolled forward, so the change includes that. Sharmica Holness falls because of Alcoa and MBJ Airports.', 10)

# ================= 6 movements =================
C = sorted(CUST.values(), key=lambda c: c['live'][1] - c['live'][0])
dec, inc = C[:8], list(reversed(C[-8:]))
def reason_for(c):
    rs = {g['reason'] for g in UPCOMING + [g for g in GADJ if g['last'] < 10] if (g['name'] and norm(g['name']) == norm(c['name']))}
    rl = sorted(r for r in rs if r)
    return (rl[0] + (' (+%d)' % (len(rl) - 1) if len(rl) > 1 else '')) if rl else 'No adjustment on file'
s = new_slide('Biggest Movements Ahead', 'The largest changes between FY2026 and FY2027, and whether an adjustment explains them', 'GWh, live forecast. Customers with no adjustment on file are moving on the base forecast, so ask whether the movement is right.')
for i, (lab, lst) in enumerate((('LARGEST INCREASES', inc), ('LARGEST DECREASES', dec))):
    x = 274320 + i * 5900000
    tb(s, x, 1900000, 5700000, 200000, lab, 10, True, GREY)
    rows = [[c['name'][:26], c['kam'].split(' ')[0], f1(c['live'][0]), f1(c['live'][1]), sg(c['live'][1] - c['live'][0]), reason_for(c)] for c in lst]
    table(s, x, 2150000, 5750000, [2.5, 1.0, 0.8, 0.8, 0.8, 2.2], ['Customer', 'KAM', 'FY26', 'FY27', 'Change', 'Adjustment'], rows, row_h=330000, size=8.5, left_cols=(0, 1, 5), colors=[[None, None, None, None, col(c['live'][1] - c['live'][0]), None] for c in lst])
callout(s, 274320, 5500000, 11650000, 700000, 'To check.', 'Any customer growing or falling by several GWh with no adjustment on file is a prompt for a conversation. Is it a rolling-average effect, or something you know about that we do not?', 10.5)

# ================= 7 register =================
eff27 = sum(effect[ac][1] for ac in effect if any(x['ac'] == ac for x in adj))
_by = collections.defaultdict(list)
for a in adj: _by[a['ac']].append(a)
zero_accts = [ac for ac, l in _by.items() if all(x['pct'] == 0 and x['kwh'] == 0 for x in l)]
n_zero_entries = sum(len(_by[ac]) for ac in zero_accts)
n_nokam = sum(1 for a in adj if not a['kam'])
accounts_with = len({a['ac'] for a in adj})
s = new_slide('What Is On File', f'{len(GADJ)} adjustments on {accounts_with} accounts take {abs(eff27):.0f} GWh out of FY2027', f'Adjustment register as at 26 October 2026: {n_adj} monthly entries, grouped into {len(GADJ)} adjustments.')
cw_ = 2800000
cards = [('MONTHLY ENTRIES ON FILE', str(n_adj), f'{len(GADJ)} adjustments, of which {len(UPCOMING)} run from October 2026 onward.'),
         ('ENTERED BY KAMS', str(n_kam_by), f'Monthly entries. The other {n_sf} were entered by Sales Forecasting.'),
         ('ENTRIES WITH NO VALUE', str(n_zero_entries), f'On {len(zero_accts)} accounts every entry is 0% and 0 kWh, so nothing changes. Three are possible defections on accounts with no KAM.'),
         ('EFFECT ON FY2027', sg(eff27, 0) + ' GWh', 'Across the assigned accounts, against the forecast with no adjustments.')]
for i, (lab, big, sub) in enumerate(cards): card(s, 274320 + i * (cw_ + 150000), 1950000, cw_, 1700000, lab, big, sub)
reasons = collections.OrderedDict()
for a in adj: reasons.setdefault(a['reason'] or 'Not stated', [0, 0])[0 if a['by'] == 'KAM' else 1] += 1
rows = [[k, str(v[0]), str(v[1]), str(v[0] + v[1])] for k, v in sorted(reasons.items(), key=lambda kv: -sum(kv[1]))]
table(s, 274320, 3850000, 5200000, [2.4, 1, 1.2, 0.8], ['Reason', 'By KAM', 'By Sales Forecasting', 'Total'], rows, row_h=290000, size=9, left_cols=(0,))
n_roll = len({g['ac'] for g in GADJ if g['kind'] == 'Rolls forward'}); n_ops = len({g['ac'] for g in GADJ if g['kind'] == 'Month only'})
box(s, 5750000, 3850000, 6175000, 2000000, 'HOW AN ENTRY WORKS', [[('Defection, expansion, renewal and win-back entries carry forward. ', True, NAVY), ('They stay in force from the month entered until the next entry for the account. Enter 0% to end one.', False, BLACK)],
    [(f'Operational disruption and Other apply only to the months entered, so an outage that runs longer needs the extra months entered. {n_roll} accounts carry a rolling entry and {n_ops} have month-only entries.', False, BLACK)],
    [('Check that each rolling entry is meant to last to December 2028.', True, NAVY)]], 10.5)

# ================= 8 rolling entries =================
ent = ROLL_CUST[:12]
tot_roll = [sum(c['eff'][k] for c in ROLL_CUST) for k in range(3)]
s = new_slide('Entries That Now Run Forward', f'{len(ROLL_CUST)} customers carry an entry to December 2028; together they take {abs(tot_roll[2]):.0f} GWh from FY2028',
              'Effect on the forecast, GWh, for the whole customer. Each stays in force until the next entry for the account. Confirm it is permanent, or tell us when it ends.')
rows = [[c['name'][:32], c['kam'].split(' ')[0], ', '.join(sorted(c['reasons']))[:24], t_label(c['first']), '; '.join(c['items'][:1])[:34], sg(c['eff'][1]), sg(c['eff'][2])] for c in ent]
table(s, 274320, 1950000, 11650000, [2.8, 1.1, 1.9, 0.9, 2.2, 1.0, 1.0], ['Customer', 'KAM', 'Reason', 'From', 'Adjustment', 'FY2027', 'FY2028'], rows, row_h=262000, size=8.5, head_h=290000, left_cols=(0, 1, 2, 4), colors=[[None, None, None, None, None, col(c['eff'][1]), col(c['eff'][2])] for c in ent])
opw = [c for c in OP_CUST if 'windalco' in c['name'].lower()]
callout(s, 274320, 5500000, 11650000, 760000, 'Month-only entries.', f'Operational disruption entries apply only to the months entered, so the forecast returns to normal afterwards. Windalco\'s turbine outage is entered for November and December 2026 only; if it runs longer, the extra months need entering. {len(OP_CUST)} customers have month-only entries.', 10.5)

# ================= 9, 10 decisions =================
def decision_slide(title_, headline, reason, sub):
    items = []
    for g in UPCOMING:
        if g['reason'] == reason: items.append(g)
    cust = collections.OrderedDict()
    for g in items:
        k = (g['kam'], norm(g['name']) or g['ac'])
        c = cust.setdefault(k, dict(name=g['name'] or g['ac'], kam=g['kam'] or 'Not assigned', accs=set(), txt=[], by=set()))
        c['accs'].add(g['ac']); c['by'].add(g['by'])
        tx = adj_text(g)
        if tx not in c['txt']: c['txt'].append(tx)
    L_ = sorted(cust.values(), key=lambda c: -abs(sum(effect[ac][1] for ac in c['accs'] if ac in effect)))[:12]
    s_ = new_slide(title_, headline, sub)
    rows = [[c['name'][:30], ('None' if c['kam'] == 'Not assigned' else c['kam'].split(' ')[0]), '; '.join(c['txt'][:2])[:58] + ('...' if len(c['txt']) > 2 else ''), ('KAM' if c['by'] == {'KAM'} else ('Sales Forecasting' if 'KAM' not in c['by'] else 'Both')), sg(sum(effect[ac][1] for ac in c['accs'] if ac in effect), 2)] for c in L_]
    table(s_, 274320, 1950000, 11650000, [2.6, 1.0, 4.0, 1.4, 1.2], ['Customer', 'KAM', 'Adjustment and months', 'Entered by', 'FY2027 effect'], rows, row_h=315000, size=9, left_cols=(0, 1, 2))
    return s_, len(cust)
s_, n1 = decision_slide('Possible Defections', 'Confirm each possible defection, or take it out of the forecast', 'Possible defection', 'Customers with a possible defection adjustment on file. A possible defection removes volume from the forecast, so it should be confirmed, dated or removed.')
s_, n2 = decision_slide('Expansions', 'Confirm each expansion, and the volume and timing behind it', 'Expansion', 'Customers with an expansion adjustment on file. Each adds volume to the forecast.')

# ================= 11+ per KAM =================
def kam_slide(kam, lst):
    s_ = new_slide('Upcoming Adjustments: ' + kam, f'{len(lst)} customers with adjustments from October 2026 onward', 'Effect is the change in the forecast for the whole customer, GWh. Keep, change or remove each one in the workbook.')
    rows = [[c['name'][:30], '; '.join(c['items'][:2])[:60] + ('...' if len(c['items']) > 2 else ''), ', '.join(sorted(c['reasons']))[:26], ('KAM' if c['by'] == {'KAM'} else ('Sales Forecasting' if 'KAM' not in c['by'] else 'Both')), sg(c['eff27'], 2), sg(c['eff28'], 2)] for c in lst[:9]]
    table(s_, 274320, 1950000, 11650000, [2.6, 3.6, 1.9, 1.3, 1.0, 1.0], ['Customer', 'Adjustment and months', 'Reason', 'Entered by', 'FY2027', 'FY2028'], rows, row_h=380000, size=9, left_cols=(0, 1, 2), colors=[[None, None, None, None, col(c['eff27']), col(c['eff28'])] for c in lst[:9]])
big = [k for k in KAMS_SORTED if len(cust_adjustments(k)) >= 4]
small = [k for k in KAMS_SORTED if k not in big]
for k in big: kam_slide(k, cust_adjustments(k))
s_ = new_slide('Upcoming Adjustments: Other Portfolios', 'Adjustments from October 2026 onward for the remaining KAMs', 'Effect is the change in the forecast for the whole customer, GWh.')
rows = []
for k in small + ['']:
    for c in cust_adjustments(k):
        rows.append([k or 'Not assigned (no effect)', c['name'][:28], '; '.join(c['items'][:2])[:52], ', '.join(sorted(c['reasons']))[:22], sg(c['eff27'], 2)])
table(s_, 274320, 1950000, 11650000, [1.8, 2.4, 3.3, 1.8, 1.0], ['KAM', 'Customer', 'Adjustment and months', 'Reason', 'FY2027'], rows, row_h=280000, size=8.5, head_h=290000, left_cols=(0, 1, 2, 3))

# ================= pipeline =================
s = new_slide('New Customers In The Forecast', f'{len(PIPE)} pipeline entries: confirm the start and the volume', 'kWh a month from the start date. These sit in the forecast until you confirm or remove them.')
rows = [[p['name'][:32], p['kam'] or 'Not assigned', p['rc'], p['start'], f'{p["kwh"]:,.0f}', p['by']] for p in PIPE]
table(s, 274320, 1950000, 11650000, [3.0, 1.6, 0.8, 1.0, 1.2, 1.6], ['Customer', 'KAM', 'Class', 'Start', 'kWh a month', 'Entered by'], rows, row_h=262000, size=8.5, left_cols=(0, 1, 5))

# ================= next steps =================
s = new_slide('Next Steps', 'Return the workbook, and we rebuild the forecast with your changes', None)
steps = [('1', 'Review your sheets', 'Adjustments, Permanent or temporary, New customers and Portfolio forecast. Respond in the yellow columns.'),
         ('2', 'Explain the misses', 'Add the reason for each account that missed in September, in the Sept account misses sheet.'),
         ('3', 'Return the workbook', 'Date to be agreed at this meeting.'),
         ('4', 'We rebuild the forecast', 'Your changes go into the register, and we share the updated portfolio forecast and accuracy for sign-off.')]
y = 1950000
for n, h, b in steps:
    c = rect(s, 400000, y, 330000, 330000, BLUE, None, shape=MSO_SHAPE.OVAL); tf = c.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Emu(0); p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = n; r.font.size = Pt(12); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT
    tb(s, 900000, y - 10000, 10800000, 800000, [[(h, True, NAVY)], [(b, False, BLACK)]], 12)
    y += 950000
prs.save(OUT)
print('saved', OUT, 'slides', len(prs.slides), 'decision rows', n1, n2, 'big kam slides', big)
