# -*- coding: utf-8 -*-
# Third view of the Opportunity & Risk to P&L slide: navy impact panel, impact table and diverging-bar view.
from decimal import Decimal, ROUND_HALF_UP
from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

SRC = r'C:\Users\jwilson\Downloads\September 2026 Corporate Performance Report.pptx'
OUT = r'C:\Projects\Sales_Platform\JPS_Opportunity_Risk_PL_Sep2026_Impact.pptx'
NAVY, BLUE, CYAN, GREY, LIGHT = RGBColor(0x06, 0x25, 0x52), RGBColor(0x0E, 0x4E, 0x95), RGBColor(0x00, 0x9F, 0xDA), RGBColor(0x66, 0x78, 0x8A), RGBColor(0xD9, 0xE1, 0xF2)
RED, GREEN, WHITE, BLACK = RGBColor(0xC0, 0x00, 0x00), RGBColor(0x2E, 0x7D, 0x52), RGBColor(0xFF, 0xFF, 0xFF), RGBColor(0x1F, 0x1F, 0x1F)
RED_T, GREEN_T, ALT = RGBColor(0xF6, 0xD3, 0xD6), RGBColor(0xDD, 0xEF, 0xDF), RGBColor(0xF3, 0xF6, 0xFB)
SOFT, MINT = RGBColor(0x9F, 0xC3, 0xF0), RGBColor(0x8F, 0xE3, 0xB0)
FONT = 'Arial'; M = '\u2212'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'

BASE_E, BASE_N = Decimal('245.2'), Decimal('53.9')
TAX = Decimal('0.25')
r1 = lambda x: x.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
ITEMS = [('Increased inflationary pressures \u2013 O&M', 'RISK', Decimal('-1.5'), r1(Decimal('-1.5') * (1 - TAX))),
         ('Other income (NFE)', 'OPPORTUNITY', Decimal('0.0'), r1(Decimal('9.0') * (1 - TAX)))]
TE, TN = sum(i[2] for i in ITEMS), sum(i[3] for i in ITEMS)
sg = lambda x: ('+' if x > 0 else M) + f'{abs(x):.1f}' if x != 0 else '0.0'
sgd = lambda x: ('+' if x > 0 else M) + f'${abs(x):.1f}M'
par = lambda x: f'({abs(x):.1f})' if x < 0 else (f'+{x:.1f}' if x > 0 else '0.0')

prs = Presentation(SRC)
layout = [l for l in prs.slide_layouts if l.name.strip() == 'Content Slide 1'][0]
sld = prs.slides._sldIdLst
for sldId in list(sld):
    prs.part.drop_rel(sldId.rId); sld.remove(sldId)
s = prs.slides.add_slide(layout)
for ph in list(s.placeholders): ph._element.getparent().remove(ph._element)

def tb(x, y, w, h, text, size=11, bold=False, color=BLACK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    sh = s.shapes.add_textbox(Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h))); tf = sh.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Emu(0); tf.vertical_anchor = anchor
    lines = text if isinstance(text, list) else [text]
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.alignment = align
        for t, b, c in (ln if isinstance(ln, list) else [(ln, bold, color)]):
            r = p.add_run(); r.text = t; r.font.name = FONT; r.font.size = Pt(size); r.font.bold = b; r.font.color.rgb = c
    return sh
def rect(x, y, w, h, fill=None, line=None, lw=0.75, shape=MSO_SHAPE.RECTANGLE):
    sh = s.shapes.add_shape(shape, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    if fill is None: sh.fill.background()
    else: sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None: sh.line.fill.background()
    else: sh.line.color.rgb = line; sh.line.width = Pt(lw)
    sh.shadow.inherit = False
    return sh

# ---- header ----
tb(711812, 493325, 11000000, 523220, 'Opportunity & Risk to P&L', 28, True, NAVY)
tb(815243, 1079336, 11200000, 330000, f'Net of both items, EBITDA moves {sgd(TE)} and net income {sgd(TN)} against the latest estimate', 16, True, BLUE)
tb(815243, 1500000, 11200000, 300000, f'FY2026 latest estimate: EBITDA US${BASE_E}M, net income US${BASE_N}M. US$M; net income impacts after {int(TAX * 100)}% tax.', 11, False, GREY)

# ---- left navy panel ----
LX, LY, LW, LH = 274320, 1900000, 3500000, 3380000
rect(LX, LY, LW, LH, NAVY); rect(LX, LY, LW, 45719, CYAN)
tb(LX + 200000, LY + 150000, LW - 400000, 180000, 'NET IMPACT OF BOTH ITEMS', 10, True, SOFT)
def stat(y, label, val, scen, col):
    tb(LX + 200000, y, LW - 400000, 180000, label, 11, True, WHITE)
    tb(LX + 200000, y + 230000, LW - 400000, 560000, val, 36, True, col)
    tb(LX + 200000, y + 880000, LW - 400000, 250000, scen, 11, False, SOFT)
stat(LY + 520000, 'EBITDA', sgd(TE).replace('$', '$'), f'to ${BASE_E + TE}M from ${BASE_E}M', RGBColor(0xFF, 0xB3, 0xB3))
rect(LX + 200000, LY + 1830000, LW - 400000, 9525, RGBColor(0x3C, 0x5A, 0x8C))
stat(LY + 1950000, 'Net income', sgd(TN), f'to ${BASE_N + TN}M from ${BASE_N}M', MINT)

# ---- right: impact table ----
RX, RW = LX + LW + 180000, 11917680 - (LX + LW + 180000)
rect(RX, LY, RW, 1700000, WHITE, LIGHT, 0.9); rect(RX, LY, RW, 45719, BLUE)
tb(RX + 150000, LY + 110000, RW - 300000, 180000, 'IMPACT BY ITEM (US$M)', 10, True, GREY)
rows = [('Item', 'Type', 'EBITDA impact', 'Net income impact', 'EBITDA scenario', 'Net income scenario')]
for lab, tag, e, n in ITEMS: rows.append((lab, tag, par(e), par(n), f'{BASE_E + e}', f'{BASE_N + n}'))
rows.append(('Total of both items', '', par(TE), par(TN), f'{BASE_E + TE}', f'{BASE_N + TN}'))
gf = s.shapes.add_table(len(rows), 6, Emu(RX + 150000), Emu(LY + 340000), Emu(RW - 300000), Emu(1250000)); t = gf.table
tblPr = gf._element.graphic.graphicData.tbl.tblPr
for a in ('bandRow', 'firstRow'): tblPr.set(a, '0')
sid = tblPr.find(A + 'tableStyleId')
if sid is not None: sid.text = '{5940675A-B579-460E-94D1-54222C63F5DA}'
cw = [3.0, 1.15, 1.1, 1.2, 1.1, 1.2]
for j, c in enumerate(cw): t.columns[j].width = Emu(int((RW - 300000) * c / sum(cw)))
for i in range(len(rows)): t.rows[i].height = Emu(300000 if i else 330000)
def cell(c, text, size=9.5, bold=False, color=BLACK, align=PP_ALIGN.CENTER, fill=None):
    c.text = ''; p = c.text_frame.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = text; r.font.name = FONT; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color
    c.margin_left = c.margin_right = Emu(60000); c.margin_top = c.margin_bottom = Emu(20000); c.vertical_anchor = MSO_ANCHOR.MIDDLE
    if fill is None: c.fill.background()
    else: c.fill.solid(); c.fill.fore_color.rgb = fill
for j, h in enumerate(rows[0]): cell(t.cell(0, j), h, 9, True, WHITE, PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER, BLUE)
for i, row in enumerate(rows[1:], 1):
    last = i == len(rows) - 1
    for j, v in enumerate(row):
        fill = NAVY if last else (ALT if i % 2 == 0 else None)
        col = WHITE if last else BLACK
        if j in (2, 3) and not last: col = RED if v.startswith('(') else (GREEN if v.startswith('+') else GREY)
        if j == 1 and v:
            fill = RED_T if v == 'RISK' else GREEN_T; col = RED if v == 'RISK' else GREEN
        cell(t.cell(i, j), v, 9.5, bool(j in (0, 1, 2, 3) or last), col, PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER, fill)

# ---- right: diverging bars ----
DY = LY + 1700000 + 150000; DH = LH - 1700000 - 150000
rect(RX, DY, RW, DH, WHITE, LIGHT, 0.9); rect(RX, DY, RW, 45719, CYAN)
tb(RX + 150000, DY + 110000, 3000000, 180000, 'EBITDA AND NET INCOME IMPACT', 10, True, GREY)
for k, (nm, col) in enumerate((('EBITDA', BLUE), ('Net income', CYAN))):
    rect(RX + RW - 2300000 + k * 1100000, DY + 125000, 120000, 120000, col); tb(RX + RW - 2300000 + k * 1100000 + 170000, DY + 105000, 900000, 160000, nm, 8.5, False, GREY)
AX = RX + 4100000; SCALE = 360000
rect(AX, DY + 330000, 9525, DH - 400000, GREY)
for k, (lab, tag, e, n) in enumerate(ITEMS):
    ry = DY + 360000 + k * 560000
    tb(RX + 150000, ry + 20000, 2650000, 420000, lab, 9.5, True, NAVY)
    for m, (val, col, nm) in enumerate(((e, BLUE, 'EBITDA'), (n, CYAN, 'Net income'))):
        by = ry + m * 230000; w = int(abs(float(val)) * SCALE)
        if val == 0:
            tb(AX + 60000, by + 20000, 2200000, 170000, '0.0  \u2013  below EBITDA', 8.5, False, GREY)
        elif val > 0:
            rect(AX + 9525, by, w, 190000, col); tb(AX + w + 80000, by + 10000, 700000, 170000, par(val), 10, True, GREEN)
        else:
            rect(AX - w, by, w, 190000, col); tb(AX - w - 760000, by + 10000, 700000, 170000, par(val), 10, True, RED, PP_ALIGN.RIGHT)

# ---- commentary ----
bul = [
 [('O&M risk ', True, NAVY), (f'of $1.5M to EBITDA (${abs(ITEMS[0][3]):.1f}M to Net Income) from increased inflationary pressures.', False, BLACK)],
 [('Other income opportunity ', True, NAVY), (f'of $9.0M (NFE) sits below EBITDA: no EBITDA impact, ${ITEMS[1][3]:.1f}M to Net Income after tax.', False, BLACK)],
]
box = tb(274320, 5420000, 11600000, 700000, bul, 11, False, BLACK)
for p in box.text_frame.paragraphs:
    pPr = p._p.get_or_add_pPr(); pPr.set('marL', '228600'); pPr.set('indent', '-228600')
    bu = etree.SubElement(pPr, A + 'buChar'); bu.set('char', '\u2022'); p.space_after = Pt(4)
tb(469231, 6411345, 6621379, 266676, 'Jamaica Public Service | Sept 2026 Corporate Performance Report', 9, True, NAVY)
pn = tb(186473, 6413496, 287140, 265842, '', 9, True, NAVY)
p = pn.text_frame.paragraphs[0]._p
for r_ in p.findall(A + 'r'): p.remove(r_)
fld = etree.SubElement(p, A + 'fld'); fld.set('id', '{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}'); fld.set('type', 'slidenum')
rpr = etree.SubElement(fld, A + 'rPr'); rpr.set('lang', 'en-US'); rpr.set('sz', '900'); rpr.set('b', '1')
sf = etree.SubElement(rpr, A + 'solidFill'); c_ = etree.SubElement(sf, A + 'srgbClr'); c_.set('val', '062552')
lat = etree.SubElement(rpr, A + 'latin'); lat.set('typeface', 'Arial'); t_ = etree.SubElement(fld, A + 't'); t_.text = '13'
end = p.find(A + 'endParaRPr')
if end is not None: p.remove(end); p.append(end)
s.notes_slide.notes_text_frame.text = (f'Latest estimate (September deck slide 3): EBITDA US${BASE_E}M, net income US${BASE_N}M. Net income impact = impact x (1 - {TAX}), rounded to 0.1 before summing. '
    'Other income (NFE) $9.0M treated as pre-tax and below EBITDA. Likelihood ratings not shown.')
prs.save(OUT); print('saved', OUT, TE, TN)
