# -*- coding: utf-8 -*-
# Alternative view of the Opportunity & Risk to P&L slide: EBITDA and net income bridges (latest estimate -> scenario).
from decimal import Decimal, ROUND_HALF_UP
from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

SRC = r'C:\Users\jwilson\Downloads\September 2026 Corporate Performance Report.pptx'
OUT = r'C:\Projects\Sales_Platform\JPS_Opportunity_Risk_PL_Sep2026_Bridge_v3.pptx'
NAVY, BLUE, CYAN, GREY, LIGHT = RGBColor(0x06, 0x25, 0x52), RGBColor(0x0E, 0x4E, 0x95), RGBColor(0x00, 0x9F, 0xDA), RGBColor(0x66, 0x78, 0x8A), RGBColor(0xD9, 0xE1, 0xF2)
RED, GREEN, WHITE, BLACK = RGBColor(0xC0, 0x00, 0x00), RGBColor(0x2E, 0x7D, 0x52), RGBColor(0xFF, 0xFF, 0xFF), RGBColor(0x1F, 0x1F, 0x1F)
RED_T, GREEN_T = RGBColor(0xF6, 0xD3, 0xD6), RGBColor(0xDD, 0xEF, 0xDF)
FONT = 'Arial'; M = '\u2212'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'

BASE_E, BASE_N = Decimal('245.2'), Decimal('55.1')   # Sep 2026 LE base (finance scenario workbook): EBITDA 247,050; net profit before dividends 55,114
TAX = Decimal(1) / Decimal(3)                       # 33 1/3%, as used in the finance scenario workbook
r1 = lambda x: x.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
E_RISK, E_OPP = Decimal('-1.5'), Decimal('0.0')
N_RISK, N_OPP = r1(Decimal('-1.5') * (1 - TAX)), r1(Decimal('9.0') * (1 - TAX))
E_END, N_END = BASE_E + E_RISK + E_OPP, BASE_N + N_RISK + N_OPP
fmtd = lambda x: (M if x < 0 else '+') + f'${abs(x):.1f}M'

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
def pill(x, y, w, text, fill, col):
    p_ = rect(x, y, w, 170000, fill, None, shape=MSO_SHAPE.ROUNDED_RECTANGLE); tf = p_.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Emu(0); tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    pp = tf.paragraphs[0]; pp.alignment = PP_ALIGN.CENTER; r = pp.add_run(); r.text = text; r.font.name = FONT; r.font.size = Pt(7.5); r.font.bold = True; r.font.color.rgb = col

# ---- header ----
tb(711812, 493325, 11000000, 523220, 'Opportunity & Risk to P&L', 28, True, NAVY)
tb(815243, 1079336, 11200000, 330000, f'O&M inflation costs EBITDA {fmtd(E_RISK).replace("\u2212", M)[0:]}, but other income lifts net income {fmtd(N_END - BASE_N)}', 16, True, BLUE)
tb(815243, 1500000, 11200000, 300000, f'From the latest estimate (EBITDA US${BASE_E}M, net income US${BASE_N}M) to the scenario with both items. US$M; net income after 33⅓% tax.', 11, False, GREY)

# ---- bridges ----
def bridge(x, y, w, h, title, base, steps, end, lo, hi, base_col, unit_note):
    rect(x, y, w, h, WHITE, LIGHT, 0.9); rect(x, y, w, 45719, BLUE if title.startswith('EBITDA') else CYAN)
    tb(x + 150000, y + 120000, w - 300000, 200000, title, 11, True, NAVY)
    top, bot = y + 650000, y + h - 800000            # plotting band
    H = bot - top
    yv = lambda v: bot - float(v - lo) / float(hi - lo) * H
    cols = 4; slot = (w - 300000) / cols; bw = slot * 0.56
    cx = lambda i: x + 150000 + slot * i + (slot - bw) / 2
    rect(x + 150000, bot, w - 300000, 9525, LIGHT)
    run = base; prev_top = None
    # column 0: latest estimate
    rect(cx(0), yv(base), bw, bot - yv(base), base_col)
    tb(cx(0) - 150000, yv(base) - 210000, bw + 300000, 180000, f'{base}', 12, True, NAVY, PP_ALIGN.CENTER)
    levels = [base]
    for i, (lab, tag, d) in enumerate(steps, 1):
        new = run + d; yt, yb = yv(max(run, new)), yv(min(run, new))
        col = GREEN if d > 0 else RED
        # connector from previous column top level
        rect(cx(i - 1) + bw, yv(run), (cx(i) - cx(i - 1) - bw), 9525, GREY)
        if d == 0:
            rect(cx(i), yv(run) - 9525, bw, 19050, GREY)
            tb(cx(i) - 150000, yv(run) - 400000, bw + 300000, 330000, [[('0.0', True, GREY)], [('below EBITDA', False, GREY)]], 8.5, False, GREY, PP_ALIGN.CENTER)
        else:
            rect(cx(i), yt, bw, max(yb - yt, 20000), col)
            lbl = f'+{d}' if d > 0 else f'({abs(d)})'
            if d > 0: tb(cx(i) - 150000, yt - 210000, bw + 300000, 180000, lbl, 12, True, col, PP_ALIGN.CENTER)
            else: tb(cx(i) - 150000, yb + 30000, bw + 300000, 180000, lbl, 12, True, col, PP_ALIGN.CENTER)
        run = new
    rect(cx(2) + bw, yv(run), cx(3) - cx(2) - bw, 9525, GREY)
    rect(cx(3), yv(end), bw, bot - yv(end), BLUE)
    tb(cx(3) - 150000, yv(end) - 210000, bw + 300000, 180000, f'{end}', 12, True, NAVY, PP_ALIGN.CENTER)
    # captions
    caps = ['LE', steps[0][0], steps[1][0], 'Scenario']
    for i, c in enumerate(caps): tb(cx(i) - 200000, bot + 70000, bw + 400000, 300000, c, 8.5, True, GREY, PP_ALIGN.CENTER)
    for i, (lab, tag, d) in enumerate(steps, 1):
        pw = 640000 if tag == 'RISK' else 960000
        pill(cx(i) + bw / 2 - pw / 2, bot + 430000, pw, tag, RED_T if tag == 'RISK' else GREEN_T, RED if tag == 'RISK' else GREEN)
    tb(x + 150000, y + h - 190000, w - 300000, 150000, unit_note, 7.5, False, GREY)

X0, Y0, GAP = 274320, 1900000, 180000
W = (11917680 - X0 - GAP) // 2; H = 3350000
steps_e = [('O&M inflation', 'RISK', E_RISK), ('Other income (NFE)', 'OPPORTUNITY', E_OPP)]
steps_n = [('O&M inflation', 'RISK', N_RISK), ('Other income (NFE)', 'OPPORTUNITY', N_OPP)]
bridge(X0, Y0, W, H, 'EBITDA bridge (US$M)', BASE_E, steps_e, E_END, Decimal('240'), Decimal('246.5'), BLUE, 'Axis starts at 240 to make the movements visible.')
bridge(X0 + W + GAP, Y0, W, H, 'Net income bridge (US$M)', BASE_N, steps_n, N_END, Decimal('50'), Decimal('62'), CYAN, 'Axis starts at 50 to make the movements visible.')

# ---- commentary ----
bul = [
 [('O&M risk ', True, NAVY), (f'of $1.5M to EBITDA (${abs(N_RISK):.1f}M to Net Income) from increased inflationary pressures.', False, BLACK)],
 [('Other income opportunity ', True, NAVY), (f'of $9.0M (NFE) sits below EBITDA: no EBITDA impact, ${N_OPP:.1f}M to Net Income after tax.', False, BLACK)],
]
box = tb(274320, 5400000, 11600000, 700000, bul, 11, False, BLACK)
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
s.notes_slide.notes_text_frame.text = (f'September 2026 LE base (Sep26_LE_Exec_PnL_by_Scenario / Presentation P&L Sep 2026 LE v6, Scenario PL): EBITDA US${BASE_E}M, net profit before dividends US${BASE_N}M. Net income impact = impact x (1 - 1/3), rounded to 0.1 before summing. '
    'Other income (NFE) $9.0M treated as pre-tax and below EBITDA. Bridge axes are truncated (EBITDA from 240, net income from 45).')
prs.save(OUT); print('saved', OUT, 'EBITDA', E_END, 'NI', N_END)
