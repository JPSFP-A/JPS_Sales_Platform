# -*- coding: utf-8 -*-
# Rebuild the 2027 AOP Revenue Management deck: narrative and KPI cards on slide 2, full measures table on slide 3.
import copy, os, sys
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from lxml import etree

SRC, OUT = sys.argv[1], sys.argv[2]
NAVY, BLUE, TINT, GREY, GREEN, RED = RGBColor(0x06, 0x25, 0x52), RGBColor(0x00, 0x9F, 0xDA), RGBColor(0xE6, 0xF3, 0xFB), RGBColor(0x5F, 0x6B, 0x7A), RGBColor(0x2E, 0x7D, 0x32), RGBColor(0xC6, 0x28, 0x28)
MINUS = '−'
p = Presentation(SRC)
s2, old, s4, s5, s6 = p.slides[1], p.slides[2], p.slides[3], p.slides[4], p.slides[5]       # slide 4 is the duplicate of slide 2 made for the table

# ---- data (J$ throughout). 2027 figures are proposals from the 2023-2026 trend. ----
M = lambda v: v
rows = [  # label, unit, 2023, 2024, 2025, 2026, 2027 proposed, kind
    ('Manual disconnections', 'No.', 215737, 184992, 214190, 209582, 205000, 'n'),
    ('Value of manual disconnections', 'J$', 4.2e9, 3.4e9, 4.7e9, 4.7e9, 4.6e9, 'm'),
    ('Manual reconnections', 'No.', 208249, 174548, 216011, 206639, 203000, 'n'),
    ('Reconnection rate', '%', 96.5, 94.35, 100.8, 98.59, 99.0, 'p'),
    ('Suspended account audits', 'No.', 17350, 24149, 24350, 11241, 18000, 'n'),
    ('Audit payments', 'J$', 85.6e6, 149.5e6, 172.8e6, 60.1e6, 99e6, 'm'),
    ('New deposits', 'No.', 44019, 43080, 40604, 31443, 32000, 'n'),
    ('Value of new deposits', 'J$', 335e6, 360.6e6, 374.4e6, 233e6, 237e6, 'm'),
    ('Upgraded deposits', 'No.', 39112, 16451, 19389, 127, None, 'n'),
    ('Value of upgraded deposits', 'J$', 235.9e6, 105.7e6, 146.2e6, 4.9e6, None, 'm'),
    ('Reduction in debt provisioning', 'J$', None, None, None, None, None, 'm'),
    ('Prepaid conversion performance', 'No.', None, None, None, None, None, 'n'),
    ('Prepaid benefits (payments)', 'J$', None, None, None, None, None, 'm'),
    ('Collections vs target (billing plus arrears)', '%', 99.23, 98.85, 97.63, 101.67, 100.0, 'p'),
    ('Collections', 'J$', 181.8e9, 184.1e9, 181.4e9, 155.4e9, None, 'm'),
]
def fmt(v, k, tbc=False):
    if v is None: return 'TBC' if tbc else 'n/a'
    if k == 'n': return f'{v:,.0f}'
    if k == 'p': return f'{v + 1e-9:.1f}%'
    a = abs(v)
    return f'J${v / 1e9:,.1f}B' if a >= 1e9 else f'J${v / 1e6:,.1f}M'.replace('.0M', 'M') if a >= 1e6 else f'J${v:,.0f}'
def chg(r):
    a, b, k = r[4], r[5], r[7]
    if a is None or b is None: return 'n/a'
    if k == 'p': d = b - a; return (f'+{d:.1f}' if d > 0 else f'{MINUS}{abs(d):.1f}') + ' pts'
    d = (b / a - 1) * 100
    return '0.0%' if round(d, 1) == 0 else (f'+{d:.1f}%' if d > 0 else f'{MINUS}{abs(d):.1f}%')

# ---- slide 2: title, narrative, cards ----
def set_title(slide, text, size):
    t = [sh for sh in slide.shapes if sh.name == 'Title 1'][0]
    paras = t.text_frame.paragraphs
    keep = [pp for pp in paras if pp.runs][0]
    for pp in paras:
        if pp is not keep: pp._p.getparent().remove(pp._p)
    runs = keep.runs
    runs[0].text = 'Revenue Management'; runs[1].text = ' '
    runs[2].text = 'Making It Easy To Do Business With Us' if text is None else text
    runs[3]._r.getparent().remove(runs[3]._r)
    for r in keep.runs: r.font.size = Pt(size)
    return t
set_title(s2, None, 24)
for _s in (s2, s4, s5, s6):
    for sh in list(_s.shapes):
        if sh.has_table: sh._element.getparent().remove(sh._element)
body = [sh for sh in s2.shapes if sh.name == 'Content Placeholder 2'][0]
paras = body.text_frame.paragraphs
H_T, B_T = copy.deepcopy(paras[0]._p), copy.deepcopy(paras[1]._p)
txb = body.text_frame._txBody
for pp in list(txb.findall('{http://schemas.openxmlformats.org/drawingml/2006/main}p')): txb.remove(pp)
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
def add_para(tpl, text, size, first=False):
    e = copy.deepcopy(tpl)
    runs = e.findall(A + 'r')
    for r in runs[1:]: e.remove(r)
    runs[0].find(A + 't').text = text
    runs[0].find(A + 'rPr').set('sz', str(size * 100))
    ppr = e.find(A + 'pPr'); ppr.set('algn', 'l')
    for x in ppr.findall(A + 'spcBef'): ppr.remove(x)
    sb = etree.SubElement(ppr, A + 'spcBef'); etree.SubElement(sb, A + 'spcPts').set('val', '0' if first else ('1400' if size == 16 else '300'))
    ppr.insert(0, sb)
    txb.append(e)
add_para(H_T, '2023 to 2025', 16, True)
add_para(B_T, 'Disconnections fell from 215,737 in 2023 to 184,992 in 2024, then rose back to 214,190 in 2025. Reconnections followed, with the rate moving from 96.5% to 94.4% to 100.8%. Collections held at J$181B to J$184B, but the share of target slipped from 99.2% to 97.6%.', 14)
add_para(H_T, '2026 outlook', 16)
add_para(B_T, 'We estimate 209,582 disconnections, 2% below 2025, at a 98.6% reconnection rate. The disconnected value stays at J$4.7B, so each disconnection is worth more. Suspended account audits drop to 11,241 and new deposits to 31,443. Upgraded deposits have almost stopped at 127.', 14)
add_para(H_T, '2027 proposal', 16)
add_para(B_T, 'We propose holding disconnections near 205,000 at a 99% reconnection rate, rebuilding audits to 18,000 and keeping new deposits near 32,000. Collections stay at 100% of target. Upgraded deposits, debt provisioning, prepaid and the collections value are still to be confirmed.', 14)
body.width = Emu(6523163); body.height = Emu(5550000)
# cards
cards = [('Manual disconnections, 2026 LE', '209,582', f'{MINUS}2.2% on 2025 (214,190)', GREEN),
         ('Reconnection rate, 2026 LE', '98.6%', f'{MINUS}2.2 pts on 2025 (100.8%)', RED),
         ('Collections vs target, 2026 LE', '101.7%', '+4.0 pts on 2025 (97.6%)', GREEN),
         ('Value of new deposits, 2026 LE', 'J$233M', f'{MINUS}37.8% on 2025 (J$374.4M)', RED)]
X0, Y0, W, Hh, GAP = 6950000, 716045, 2480000, 2680000, 190000
for i, (lab, big, sub, col) in enumerate(cards):
    x = X0 + (i % 2) * (W + GAP); y = Y0 + (i // 2) * (Hh + GAP)
    box = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(x), Emu(y), Emu(W), Emu(Hh)); box.name = 'KPI card %d' % (i + 1)
    box.fill.solid(); box.fill.fore_color.rgb = TINT; box.line.fill.background(); box.shadow.inherit = False
    tf = box.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Emu(160000)
    def para(first, text, size, bold, color):
        pp = tf.paragraphs[0] if first else tf.add_paragraph(); pp.alignment = PP_ALIGN.LEFT
        r = pp.add_run(); r.text = text; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color; r.font.name = 'Montserrat'
        return pp
    para(True, lab, 12, False, GREY); para(False, big, 32, True, NAVY); para(False, sub, 12, True, col)
    tf.paragraphs[1].space_before = Pt(6); tf.paragraphs[2].space_before = Pt(6)

# ---- slide 4 (becomes slide 3): measures table ----
set_title(s4, 'Performance Measures, 2023 to 2027', 24)
for sh in list(s4.shapes):
    if sh.name == 'Content Placeholder 2': sh._element.getparent().remove(sh._element)
cols = [3750000, 650000, 1100000, 1100000, 1100000, 1100000, 1500000, 1350000]
hdr = ['Performance measure', 'Unit', '2023 Actual', '2024 Actual', '2025 Actual', '2026 Sep LE', '2027 Proposed', '2026 LE vs 2025']
nr = len(rows) + 1
gf = s4.shapes.add_table(nr, len(cols), Emu(269993), Emu(716045), Emu(sum(cols)), Emu(330000 * nr)); gf.name = 'Performance measures'
tbl = gf.table
tblPr = tbl._tbl.tblPr
for a in ('bandRow', 'firstRow'): tblPr.set(a, '0')
sid = tblPr.find(A + 'tableStyleId')
if sid is not None: sid.text = '{2D5ABB26-0587-4C30-8999-92F81FD0307C}'   # no style, no grid
for i, w in enumerate(cols): tbl.columns[i].width = Emu(w)
for r in tbl.rows: r.height = Emu(330000)
def cell(r, c, text, size=11, bold=False, color=RGBColor(0x1F, 0x1F, 0x1F), fill=None, align=PP_ALIGN.RIGHT, italic=False):
    ce = tbl.cell(r, c); ce.text = ''
    tf = ce.text_frame; tf.word_wrap = True
    pp = tf.paragraphs[0]; pp.alignment = align
    run = pp.add_run(); run.text = text; run.font.size = Pt(size); run.font.bold = bold; run.font.italic = italic; run.font.color.rgb = color; run.font.name = 'Arial'
    ce.vertical_anchor = MSO_ANCHOR.MIDDLE; ce.margin_left = ce.margin_right = Emu(70000); ce.margin_top = ce.margin_bottom = Emu(20000)
    if fill is None: ce.fill.background()
    else: ce.fill.solid(); ce.fill.fore_color.rgb = fill
for c, h in enumerate(hdr): cell(0, c, h, 11, True, RGBColor(255, 255, 255), NAVY, PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER if c == 1 else PP_ALIGN.RIGHT)
for i, r in enumerate(rows, 1):
    band = RGBColor(0xF3, 0xF6, 0xF9) if i % 2 == 0 else None
    cell(i, 0, r[0], 11, False, fill=band, align=PP_ALIGN.LEFT); cell(i, 1, r[1], 11, False, GREY, band, PP_ALIGN.CENTER)
    for j in range(4):
        v = r[2 + j]; cell(i, 2 + j, fmt(v, r[7]), 11, j == 3, GREY if v is None else RGBColor(0x1F, 0x1F, 0x1F), band)
    v = r[6]; cell(i, 6, fmt(v, r[7], True), 11, v is not None, GREY if v is None else NAVY, TINT, italic=True)
    d = chg((None, None, None, r[4], r[5], None, None, r[7])) if False else chg((0, 0, 0, 0, r[4], r[5], r[6], r[7]))
    good_up = r[0] not in ('Manual disconnections', 'Value of manual disconnections')
    col = GREY
    if d not in ('n/a', '0.0%'): col = (GREEN if (d[0] == '+') == good_up else RED)
    cell(i, 7, d, 11, True, col, band)
fn = s4.shapes.add_textbox(Emu(269993), Emu(716045 + 330000 * nr + 60000), Emu(11650000), Emu(330000)); fn.name = 'Footnote'
tf = fn.text_frame; tf.word_wrap = True; tf.margin_left = Emu(0)
r_ = tf.paragraphs[0].add_run()
r_.text = '2027 Proposed figures are analyst proposals from the 2023 to 2026 trend, pending approval. TBC: to be confirmed with the revenue budget. n/a: not reported. 2026 Sep LE is the full-year latest estimate.'
r_.font.size = Pt(10); r_.font.color.rgb = GREY; r_.font.name = 'Arial'
notes = s4.notes_slide.notes_text_frame
notes.text = ('Basis for the 2027 proposals. Disconnections: 2026 LE less about 2%, at the 2026 value per disconnection of about J$22,400. '
              'Reconnections: 99% of disconnections. Audits: midpoint of 2026 (11,241) and 2025 (24,350), at about J$5,500 collected per audit. '
              'New deposits: held near the 2026 count at about J$7,400 per deposit. Collections vs target: 100%. '
              'Upgraded deposits, provisioning, prepaid and collections value have no usable trend or need the revenue budget, so they stay TBC.')

# ---- slide 5: by rate class table ----
import json
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_TICK_LABEL_POSITION
BC = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_fy27_byclass.json')))
set_title(s5, 'Sales by Rate Class: What Is Driving Each', 24)
for sh in list(s5.shapes):
    if sh.name == 'Content Placeholder 2': sh._element.getparent().remove(sh._element)
names = {'RT10': 'RT10 Residential', 'RT20': 'RT20 Small commercial', 'RT40': 'RT40 Commercial', 'RT50': 'RT50 Large commercial', 'RT60-ST': 'RT60 Street lighting', 'RT70': 'RT70 Industrial'}
drv = {'RT10': 'Storm recovery is complete: up 3.9% on 2025 since July. Drags: 7,742 more zero-kWh premises than before the storm, western parishes 3.5% below last year, and 857 net-export customers.',
       'RT20': 'Fully recovered, 10.4% above October 2024. October carries about 0.3 GWh of catch-up billing that will not repeat.',
       'RT40': 'Flat on last year since July (+0.1%). Water supply is back, hotels are 19% down, and billing timing at Caribbean Broilers moves single months.',
       'RT50': 'Hotel recovery: Q3 was 13% below 2025. 2027 assumes 30% of the hotel gap is closed in January, rising to 62% by December. West Meat Packers loses 70% of its load from March.',
       'RT60-ST': 'Street lighting and similar. Steady at about 3.4 GWh a month. Early 2026 was low and has recovered.',
       'RT70': 'Customers leaving the grid. Alcoa fell from 7.2 GWh a month in 2025 to 0.26 in October. PAC (4 MW) and MBJ (6 MW) solar take about 16 GWh off in 2027.'}
cols2 = [1550000, 900000, 950000, 950000, 850000, 750000, 5700000]
hdr2 = ['Rate class', 'FY2025 Actual', 'FY2026 Outlook', 'FY2027 Proposed', 'Change, GWh', 'Change, %', 'What is driving it']
CLS = ['RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']
n2 = len(CLS) + 2; RH = [330000] + [640000] * len(CLS) + [330000]
gf2 = s5.shapes.add_table(n2, len(cols2), Emu(269993), Emu(716045), Emu(sum(cols2)), Emu(sum(RH))); gf2.name = 'Sales by rate class'
tbl = gf2.table; tp = tbl._tbl.tblPr
for a_ in ('bandRow', 'firstRow'): tp.set(a_, '0')
sid = tp.find(A + 'tableStyleId')
if sid is not None: sid.text = '{2D5ABB26-0587-4C30-8999-92F81FD0307C}'
for i, w in enumerate(cols2): tbl.columns[i].width = Emu(w)
for i, h in enumerate(RH): tbl.rows[i].height = Emu(h)
for c, h in enumerate(hdr2): cell(0, c, h, 11, True, RGBColor(255, 255, 255), NAVY, PP_ALIGN.LEFT if c in (0, 6) else PP_ALIGN.RIGHT)
sg = lambda v, d=1: ('+' if v > 0 else MINUS if v < 0 else '') + f'{abs(v):,.{d}f}'
for i, c in enumerate(CLS, 1):
    b = BC[c]; band = RGBColor(0xF3, 0xF6, 0xF9) if i % 2 == 0 else None
    d = b['fy27'] - b['fy26']; pc = d / b['fy26'] * 100; col = GREEN if d > 0 else RED
    cell(i, 0, names[c], 11, True, NAVY, band, PP_ALIGN.LEFT)
    cell(i, 1, f"{b['fy25']:,.1f}", 11, False, fill=band); cell(i, 2, f"{b['fy26']:,.1f}", 11, False, fill=band)
    cell(i, 3, f"{b['fy27']:,.1f}", 11, True, NAVY, TINT, italic=True)
    cell(i, 4, sg(d), 11, True, col, band); cell(i, 5, sg(pc) + '%', 11, True, col, band)
    cell(i, 6, drv[c], 11, False, fill=band, align=PP_ALIGN.LEFT)
    tbl.cell(i, 6).margin_left = Emu(150000)
tot = {k: sum(BC[c][k] for c in CLS) for k in ('fy25', 'fy26', 'fy27')}; i = len(CLS) + 1
td = tot['fy27'] - tot['fy26']
for j, (txt, al) in enumerate([('Total', PP_ALIGN.LEFT), (f"{tot['fy25']:,.1f}", PP_ALIGN.RIGHT), (f"{tot['fy26']:,.1f}", PP_ALIGN.RIGHT), (f"{tot['fy27']:,.1f}", PP_ALIGN.RIGHT), (sg(td), PP_ALIGN.RIGHT), (sg(td / tot['fy26'] * 100) + '%', PP_ALIGN.RIGHT), ('', PP_ALIGN.LEFT)]):
    cell(i, j, txt, 11, True, NAVY, RGBColor(0xDC, 0xE6, 0xF1), al)
fn2 = s5.shapes.add_textbox(Emu(269993), Emu(716045 + sum(RH) + 60000), Emu(11650000), Emu(330000)); fn2.name = 'Footnote'
tf = fn2.text_frame; tf.word_wrap = True; tf.margin_left = Emu(0)
r_ = tf.paragraphs[0].add_run()
r_.text = 'GWh billed, prepaid included. FY2026 outlook is January to October actual plus November and December on the 2024 pattern. FY2025 includes the storm months of November and December. FY2027 is proposed.'
r_.font.size = Pt(10); r_.font.color.rgb = GREY; r_.font.name = 'Arial'

# ---- slide 6: what moves FY2027 ----
set_title(s6, 'What Moves FY2027', 24)
for sh in list(s6.shapes):
    if sh.name == 'Content Placeholder 2': sh._element.getparent().remove(sh._element)
cd = CategoryChartData(); cd.categories = [names[c].split(' ')[0] for c in CLS]
cd.add_series('January to June', [round(BC[c]['h1'], 1) for c in CLS]); cd.add_series('July to December', [round(BC[c]['h2'], 1) for c in CLS])
gfc = s6.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Emu(269993), Emu(900000), Emu(7000000), Emu(5200000), cd); gfc.name = 'Change by half'
ch = gfc.chart; ch.has_legend = True; ch.legend.position = XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout = False; ch.legend.font.size = Pt(12); ch.legend.font.name = 'Arial'
ch.has_title = True; ch.chart_title.text_frame.text = 'Change in FY2027 vs FY2026, GWh'
rr = ch.chart_title.text_frame.paragraphs[0].runs[0]; rr.font.size = Pt(14); rr.font.bold = True; rr.font.name = 'Arial'; rr.font.color.rgb = NAVY
for ser, colr in zip(ch.plots[0].series, (BLUE, NAVY)):
    ser.format.fill.solid(); ser.format.fill.fore_color.rgb = colr; ser.invert_if_negative = False
pl = ch.plots[0]; pl.gap_width = 60; pl.overlap = -5; pl.has_data_labels = True
dl = pl.data_labels; dl.number_format = '+#,##0.0;-#,##0.0;0.0'; dl.number_format_is_linked = False; dl.font.size = Pt(11); dl.font.name = 'Arial'; dl.position = XL_LABEL_POSITION.OUTSIDE_END
ch.category_axis.tick_labels.font.size = Pt(12); ch.category_axis.tick_labels.font.name = 'Arial'
ch.category_axis.tick_label_position = XL_TICK_LABEL_POSITION.LOW
ch.value_axis.tick_labels.font.size = Pt(11); ch.value_axis.tick_labels.font.name = 'Arial'; ch.value_axis.major_gridlines.format.line.color.rgb = RGBColor(0xD9, 0xDE, 0xE4); ch.value_axis.format.line.fill.background()
h1t = sum(BC[c]['h1'] for c in CLS); h2t = sum(BC[c]['h2'] for c in CLS); r70 = BC['RT70']['fy27'] - BC['RT70']['fy26']
box = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(7550000), Emu(900000), Emu(4380000), Emu(5200000)); box.name = 'Drivers'
box.fill.solid(); box.fill.fore_color.rgb = TINT; box.line.fill.background(); box.shadow.inherit = False
tf = box.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.TOP; tf.margin_left = tf.margin_right = Emu(200000); tf.margin_top = Emu(200000)
big3 = sum(BC[c]['fy27'] - BC[c]['fy26'] for c in ('RT10', 'RT20', 'RT40'))
pts = ['What moves the year',
       f'Of the {sg(td, 0)} GWh, {sg(h1t, 0)} GWh falls in January to June. That half was depressed by the storm in 2026. July to December is flat on 2026 ({sg(h2t, 0)} GWh).',
       f'Residential, RT20 and RT40 add {sg(big3, 0)} GWh, {sg(sum(BC[c]["h1"] for c in ("RT10", "RT20", "RT40")), 0)} GWh of it in January to June. That is mostly the base returning to normal, not new demand.',
       f'RT70 loses {abs(r70):.0f} GWh as customers move to their own generation. Hotels add about 23 GWh through the year.',
       f'The seasonal pattern we use moves the total by about 22 GWh either way, so the range is {tot["fy27"] - 22:,.0f} to {tot["fy27"] + 22:,.0f} GWh.']
for k, txt in enumerate(pts):
    pp = tf.paragraphs[0] if k == 0 else tf.add_paragraph(); pp.alignment = PP_ALIGN.LEFT
    r = pp.add_run(); r.text = txt; r.font.name = 'Montserrat'; r.font.color.rgb = NAVY
    r.font.size = Pt(16 if k == 0 else 13); r.font.bold = (k == 0)
    if k: pp.space_before = Pt(10)

# ---- reorder (title, narrative, table) and drop the unstyled "Old" slide ----
lst = p.slides._sldIdLst; ids = list(lst)
old_id, s4_id = ids[2], ids[3]
old_rid = old_id.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
lst.remove(old_id); p.part.drop_rel(old_rid)
p.save(OUT); print('saved', OUT)
