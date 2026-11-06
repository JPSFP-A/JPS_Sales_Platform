# -*- coding: utf-8 -*-
# "Opportunity & Risk to P&L" slide on the current JPS Corporate Performance Report template.
from decimal import Decimal, ROUND_HALF_UP
from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

SRC = r'C:\Users\jwilson\Downloads\September 2026 Corporate Performance Report.pptx'
OUT = r'C:\Projects\Sales_Platform\JPS_Opportunity_Risk_PL_Sep2026.pptx'
NAVY, BLUE, CYAN, GREY, LIGHT = RGBColor(0x06, 0x25, 0x52), RGBColor(0x0E, 0x4E, 0x95), RGBColor(0x00, 0x9F, 0xDA), RGBColor(0x66, 0x78, 0x8A), RGBColor(0xD9, 0xE1, 0xF2)
RED, GREEN, WHITE, BLACK = RGBColor(0xC0, 0x00, 0x00), RGBColor(0x2E, 0x7D, 0x52), RGBColor(0xFF, 0xFF, 0xFF), RGBColor(0x1F, 0x1F, 0x1F)
RED_T, GREEN_T = RGBColor(0xF6, 0xD3, 0xD6), RGBColor(0xDD, 0xEF, 0xDF)
FONT = 'Arial'
M = '\u2212'

# ---------------- inputs ----------------
BASE_EBITDA, BASE_NI = Decimal('245.2'), Decimal('53.9')       # FY latest estimate, slide 3 of the September deck
TAX = Decimal('0.25')                                           # rate implied by the previous risk and opportunity slide
ITEMS = [   # label, tag, EBITDA impact, pre-tax impact to net income (before tax)
 ('Increased inflationary pressures \u2013 O&M', 'RISK', Decimal('-1.5'), Decimal('-1.5')),
 ('Other income (NFE)', 'OPPORTUNITY', Decimal('0.0'), Decimal('9.0')),       # other income sits below EBITDA
]
r1 = lambda x: x.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
def scen(e, n): return dict(e=e, n=n, ebase=BASE_EBITDA + e, nbase=BASE_NI + n)
cards = []
for lab, tag, e, pre in ITEMS:
    n = r1(pre * (1 - TAX)); cards.append((lab, tag, e, n))   # round first so the cards add up as shown
tot_e = sum(c[2] for c in cards); tot_n = sum(c[3] for c in cards)
cards.insert(0, ('Total of both items', 'TOTAL', tot_e, tot_n))
fmt = lambda x: (M if x < 0 else '+') + f'{abs(r1(x)):.1f}' if r1(x) != 0 else '0.0'
fmtd = lambda x: (M if x < 0 else '+') + f'${abs(r1(x)):.1f}M'

prs = Presentation(SRC)
layout = [l for l in prs.slide_layouts if l.name.strip() == 'Content Slide 1'][0]
sld = prs.slides._sldIdLst
for sldId in list(sld):
    prs.part.drop_rel(sldId.rId); sld.remove(sldId)
s = prs.slides.add_slide(layout)
for ph in list(s.placeholders): ph._element.getparent().remove(ph._element)

def tb(x, y, w, h, text, size=11, bold=False, color=BLACK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    sh = s.shapes.add_textbox(Emu(x), Emu(y), Emu(w), Emu(h)); tf = sh.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Emu(0); tf.vertical_anchor = anchor
    lines = text if isinstance(text, list) else [text]
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.alignment = align
        for t, b, c in (ln if isinstance(ln, list) else [(ln, bold, color)]):
            r = p.add_run(); r.text = t; r.font.name = FONT; r.font.size = Pt(size); r.font.bold = b; r.font.color.rgb = c
    return sh
def rect(x, y, w, h, fill=None, line=None, lw=0.75, shape=MSO_SHAPE.RECTANGLE):
    sh = s.shapes.add_shape(shape, Emu(x), Emu(y), Emu(w), Emu(h))
    if fill is None: sh.fill.background()
    else: sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None: sh.line.fill.background()
    else: sh.line.color.rgb = line; sh.line.width = Pt(lw)
    sh.shadow.inherit = False
    return sh

# ---------------- header ----------------
tb(711812, 493325, 11000000, 523220, 'Opportunity & Risk to P&L', 28, True, NAVY)
tb(815243, 1079336, 11200000, 330000, f'Other income more than offsets the O&M inflation risk at net income: EBITDA {fmtd(tot_e)}, net income {fmtd(tot_n)}', 16, True, BLUE)
tb(815243, 1500000, 11200000, 300000, f'FY2026 latest estimate: EBITDA US${BASE_EBITDA}M, net income US${BASE_NI}M. Impacts in US$M; net income shown after {int(TAX * 100)}% tax.', 11, False, GREY)

# ---------------- cards ----------------
X0, Y0, GAP = 274320, 1950000, 180000
CW = (11917680 - X0 - 2 * GAP) // 3; CH = 3250000
SC = 76000            # EMU per US$1M of bar height
ZERO = Y0 + 1790000   # bar baseline
for k, (lab, tag, e, n) in enumerate(cards):
    x = X0 + k * (CW + GAP)
    rect(x, Y0, CW, CH, WHITE, LIGHT, 0.9); rect(x, Y0, CW, 45719, BLUE if tag == 'TOTAL' else (RED if tag == 'RISK' else GREEN))
    # tag + title
    tcol, tfill = (WHITE, NAVY) if tag == 'TOTAL' else ((RED, RED_T) if tag == 'RISK' else (GREEN, GREEN_T))
    pill = rect(x + 130000, Y0 + 130000, 1000000 if tag == 'OPPORTUNITY' else 640000, 200000, tfill, None, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    tf = pill.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Emu(0); tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; r = p.add_run(); r.text = tag; r.font.name = FONT; r.font.size = Pt(8); r.font.bold = True; r.font.color.rgb = tcol
    tb(x + 130000, Y0 + 400000, CW - 260000, 380000, lab, 12, True, NAVY)
    # scenario EBITDA
    tb(x + 130000, Y0 + 840000, 1500000, 160000, 'EBITDA', 9, True, GREY)
    tb(x + CW - 130000 - 1900000, Y0 + 780000, 1900000, 330000, f'${r1(BASE_EBITDA + e)}M', 20, True, NAVY, PP_ALIGN.RIGHT)
    # bars
    bw = 560000; cx1 = x + CW // 3 - bw // 2; cx2 = x + 2 * CW // 3 - bw // 2
    rect(x + 130000, ZERO, CW - 260000, 9525, LIGHT)
    for cxb, val, col, nm in ((cx1, e, BLUE, 'EBITDA'), (cx2, n, CYAN, 'Net income')):
        hgt = int(abs(float(val)) * SC)
        vcol = BLACK if r1(val) == 0 else (GREEN if val > 0 else RED)
        if r1(val) == 0:
            tb(cxb - 200000, ZERO - 190000, bw + 400000, 170000, 'No EBITDA impact', 8.5, False, GREY, PP_ALIGN.CENTER)
        else:
            if val > 0:
                rect(cxb, ZERO - hgt, bw, hgt, col); tb(cxb - 100000, ZERO - hgt - 200000, bw + 200000, 180000, fmt(val), 12, True, vcol, PP_ALIGN.CENTER)
            else:
                rect(cxb, ZERO + 9525, bw, hgt, col); tb(cxb - 100000, ZERO + hgt + 40000, bw + 200000, 180000, f'({abs(r1(val)):.1f})', 12, True, vcol, PP_ALIGN.CENTER)
        tb(cxb - 200000, Y0 + 2440000, bw + 400000, 160000, nm, 8.5, True, GREY, PP_ALIGN.CENTER)
    # scenario net income
    tb(x + 130000, Y0 + 2780000, 1500000, 160000, 'Net income', 9, True, GREY)
    tb(x + CW - 130000 - 1900000, Y0 + 2720000, 1900000, 330000, f'${r1(BASE_NI + n)}M', 20, True, NAVY, PP_ALIGN.RIGHT)

# ---------------- commentary ----------------
by = 5350000
risk, opp, tot = cards[1], cards[2], cards[0]
bul = [
 [('O&M risk ', True, NAVY), (f'of ${abs(r1(risk[2])):.1f}M to EBITDA (${abs(r1(risk[3])):.1f}M to Net Income) from increased inflationary pressures.', False, BLACK)],
 [('Other income opportunity ', True, NAVY), (f'of $9.0M (NFE) sits below EBITDA, so there is no EBITDA impact; ${r1(opp[3]):.1f}M to Net Income after tax.', False, BLACK)],
 [('Together ', True, NAVY), (f'EBITDA moves to ${r1(BASE_EBITDA + tot[2])}M ({fmtd(tot[2])}) and Net Income to ${r1(BASE_NI + tot[3])}M ({fmtd(tot[3])}) against the latest estimate.', False, BLACK)],
]
box = tb(274320, by, 11780000, 800000, bul, 11, False, BLACK)
for p in box.text_frame.paragraphs:
    pPr = p._p.get_or_add_pPr(); pPr.set('marL', '228600'); pPr.set('indent', '-228600')
    for tag_ in ('a:buNone', 'a:buChar'):
        for e_ in pPr.findall('{http://schemas.openxmlformats.org/drawingml/2006/main}' + tag_.split(':')[1]): pPr.remove(e_)
    bu = etree.SubElement(pPr, '{http://schemas.openxmlformats.org/drawingml/2006/main}buChar'); bu.set('char', '\u2022')
    p.space_after = Pt(4)
# footer and auto page number
tb(469231, 6411345, 6621379, 266676, 'Jamaica Public Service | Sept 2026 Corporate Performance Report', 9, True, NAVY)
pn = tb(186473, 6413496, 287140, 265842, '', 9, True, NAVY)
p = pn.text_frame.paragraphs[0]._p
for r_ in p.findall('{http://schemas.openxmlformats.org/drawingml/2006/main}r'): p.remove(r_)
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
fld = etree.SubElement(p, A + 'fld'); fld.set('id', '{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}'); fld.set('type', 'slidenum')
rpr = etree.SubElement(fld, A + 'rPr'); rpr.set('lang', 'en-US'); rpr.set('sz', '900'); rpr.set('b', '1')
sf = etree.SubElement(rpr, A + 'solidFill'); c_ = etree.SubElement(sf, A + 'srgbClr'); c_.set('val', '062552')
lat = etree.SubElement(rpr, A + 'latin'); lat.set('typeface', 'Arial')
t_ = etree.SubElement(fld, A + 't'); t_.text = '13'
# keep a:fld before endParaRPr if present
end = p.find(A + 'endParaRPr')
if end is not None: p.remove(end); p.append(end)
s.notes_slide.notes_text_frame.text = (
    f'Latest estimate (September deck, slide 3): EBITDA US${BASE_EBITDA}M, net income US${BASE_NI}M. '
    f'Net income impact = impact x (1 - {TAX}); the 25% rate is the one implied by the previous risk and opportunity slide (2.0 -> 1.5, 1.1 -> 0.9). '
    'Other income (NFE) of $9.0M is treated as a pre-tax item below EBITDA: no EBITDA impact. Likelihood ratings (the old slide showed Medium) are not shown; add once agreed. '
    'Note: the bullets on the previous slide had EBITDA and net income labels reversed for the O&M opportunity (chart: EBITDA 1.7, net income 1.3).')
prs.save(OUT); print('saved', OUT)
for c in cards: print(c[0], c[1], 'EBITDA', r1(BASE_EBITDA + c[2]), fmt(c[2]), 'NI', r1(BASE_NI + c[3]), fmt(c[3]))
