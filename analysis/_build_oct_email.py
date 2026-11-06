# -*- coding: utf-8 -*-
# October 2026 monthly sales highlights, in the format of the September email (metrics table, anomalies, insights, prepaid), plus outside context.
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = r'C:\Projects\Sales_Platform\JPS_Sales_Highlights_Oct2026_v2.docx'
NAVY = RGBColor(0x0B, 0x3C, 0x6F); RED = RGBColor(0xC0, 0x00, 0x00); GREEN = RGBColor(0x1F, 0x8F, 0x5A); GREY = RGBColor(0x59, 0x59, 0x59)
M = '\u2212'

doc = Document()
sec = doc.sections[0]; sec.left_margin = sec.right_margin = Cm(2); sec.top_margin = sec.bottom_margin = Cm(1.8)
st = doc.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')

def para(text='', bold=False, size=None, color=None, space_after=4, italic=False):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(space_after); p.paragraph_format.space_before = Pt(0)
    if text:
        r = p.add_run(text); r.bold = bold; r.italic = italic
        if size: r.font.size = Pt(size)
        if color: r.font.color.rgb = color
    return p
def bullet(lead, rest):
    p = doc.add_paragraph(style='List Bullet'); p.paragraph_format.space_after = Pt(3)
    r = p.add_run(lead + ' '); r.bold = True
    p.add_run(rest)
def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement('w:shd'); shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hexcolor); tcPr.append(shd)

para('See key highlights for the month. The one-page analysis is attached.', bold=True, space_after=8)

rows = [('Metric', 'Oct 2025', 'Oct 2026', 'Change'),
        ('Customers', '729,348', '740,030', '+10,682 (+1.46%)'),
        ('Sales (GWh, month)', '289.13', '294.30', '+5.17 (+1.8%)'),
        ('Sales YTD (GWh, Jan\u2013Oct)', '2,839.1', '2,723.3', f'{M}115.8 ({M}4.1%)'),
        ('Revenue YTD (J$M)', '145,075', '143,680', f'{M}1,395 ({M}0.96%)')]
t = doc.add_table(rows=len(rows), cols=4); t.alignment = WD_TABLE_ALIGNMENT.LEFT; t.autofit = False
widths = [Cm(6.2), Cm(3.0), Cm(3.0), Cm(4.4)]
for i, r in enumerate(rows):
    for j, v in enumerate(r):
        c = t.cell(i, j); c.width = widths[j]; c.text = ''
        p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(1); p.paragraph_format.space_before = Pt(1)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run(v); run.font.size = Pt(10)
        if i == 0: run.bold = True; run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF); shade(c, '0B3C6F')
        else:
            if i % 2 == 0: shade(c, 'F3F6FB')
            if j == 3: run.font.color.rgb = GREEN if v.startswith('+') else RED
para('', space_after=6)

para('Anomalies', bold=True, size=11.5, color=NAVY, space_after=3)
bullet('Caribbean Broilers:', 'back to normal. It billed 2.5 GWh in October after 4.2 GWh in August and 0.8 GWh in September. The three months together are about 0.4 GWh above normal (2.2\u20132.4 a month).')
bullet('Petrojam:', '1.8 GWh, back to its usual level (1.5\u20131.7 GWh in most months) after 0.9 GWh in September, its lowest month this year. It is level with last October (1.7).')
bullet('Caribbean Cement:', '9.1 GWh, flat on September and more than double last October (4.3). The September decline against last year was last year\u2019s strong September (10.8), not weaker demand: it has billed 8.5 to 9.1 GWh for three months running. Year to date it is up 22% (91.4 vs 75.2 GWh).')

para('Insights', bold=True, size=11.5, color=NAVY, space_after=3)
bullet('The split narrowed.', f'Residential-side sales were up 4.9% year over year (126.2 to 132.4 GWh). Commercial was down 0.6% (163.0 to 161.9 GWh). Alcoa explains 6.8 GWh of that. Excluding Alcoa, commercial is up 3.7%. October 2025 includes the days after Hurricane Melissa (28 October), so the comparison is easier than normal.')
bullet('Alcoa is now close to zero.', '0.26 GWh in October, after 1.2 in August and 0.6 in September, against 7.0 a year ago.')
bullet('Hotels are recovering slowly.', f'Their year-over-year decline is {M}18.8% in October ({M}19.1% in September) and {M}24.5% year to date ({M}25.2%): 17.3 GWh against 21.3 GWh a year ago. The reopenings in late August and September (Royalton Negril and Blue Waters, about 1,150 rooms) are not showing in the bills yet. The bigger steps are expected from December.')
bullet('Month on month, the drop is the season.', f'Sales were flat on September ({M}0.2%) with one extra day, so per day volume fell 3.4%, a normal step as temperatures ease (the budget assumes {M}4.7% per day). National Heroes Day fell on Monday 19 October. Billing cycles do not map exactly to calendar days, so treat that as approximate.')
bullet('Active RT10 customers rose again.', f'RT10 added 449 accounts and zero-consumption accounts fell by 153, so active RT10 customers are up about 600 on the month, after falling in September. Zero-consumption accounts are still 15% above last October (58,886 vs 51,144).')
bullet('Small-business accounts are still shrinking.', f'RT20 commercial accounts are down 3.2% over a year (24,170 to 23,393) and lost 89 in October.')

import json as _json, os as _os
_G = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '_cust', 'bridge_sep_oct.json')))
def _ch(g, y): return _G[g]['%d-10' % y] - _G[g]['%d-9' % y]
_ORD = [('Caribbean Cement', ['Caribbean Cement']), ('Other RT40–RT70 accounts', ['Other RT40-RT70 accounts']), ('Caribbean Broilers', ['Caribbean Broilers']), ('Petrojam', ['Petrojam']),
        ('RT20 mass market and other RT20', ['RT20 mass market (no account)', 'Other RT20 accounts']), ('Windalco', ['Windalco']), ('Hotels', ['Hotels']), ('Alcoa', ['Alcoa']), ('Residential RT10 (incl. prepaid)', ['Residential RT10 (incl prepaid)'])]
_rows = [(n, sum(_ch(g, 2025) for g in gs), sum(_ch(g, 2026) for g in gs)) for n, gs in _ORD]
_t25 = sum(r[1] for r in _rows); _t26 = sum(r[2] for r in _rows)
fm = lambda v: ('+' if v > 0.005 else (M if v < -0.005 else '')) + f'{abs(v):.1f}'
para('Why October held up against September', bold=True, size=11.5, color=NAVY, space_after=3)
para(f'Last year sales fell {abs(_t25):.1f} GWh from September to October. This year they fell {abs(_t26):.1f} GWh. Three one-off items explain 9.3 GWh of the {_t26 - _t25:.1f} GWh difference: Caribbean Cement, which was down last October, and September billing timing at Caribbean Broilers and Petrojam. Adding September’s timing items back to their normal levels, sales fell about 1.0% from September to October this year, against about 2.1% last year excluding Cement. Both years have the same number of days.', space_after=4)
bt = doc.add_table(rows=len(_rows) + 2, cols=4); bt.alignment = WD_TABLE_ALIGNMENT.LEFT; bt.autofit = False
bw = [Cm(7.0), Cm(3.2), Cm(3.2), Cm(3.2)]
_all = [('GWh', 'Sep→Oct 2025', 'Sep→Oct 2026', 'Difference')] + [(n, fm(a), fm(b), fm(b - a)) for n, a, b in _rows] + [('Total', fm(_t25), fm(_t26), fm(_t26 - _t25))]
for i, r in enumerate(_all):
    for j, v in enumerate(r):
        c = bt.cell(i, j); c.width = bw[j]; c.text = ''
        p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(1); p.paragraph_format.space_before = Pt(1)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run(v); run.font.size = Pt(10)
        if i == 0: run.bold = True; run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF); shade(c, '0B3C6F')
        else:
            if i == len(_all) - 1: run.bold = True; shade(c, 'D9E1F2')
            elif i % 2 == 0: shade(c, 'F3F6FB')
            if j == 3 and i > 0: run.font.color.rgb = GREEN if v.startswith('+') else (RED if v.startswith(M) else RGBColor(0, 0, 0))
para('', space_after=4)
doc.add_picture(r'C:\Projects\Sales_Platform\JPS_Sep_to_Oct_Bridge_2026.png', width=Cm(16.5))
para('Residential fell more than last year (prepaid usage per customer dropped to 151 kWh from 167 in September). The other commercial gain is spread over 7,600 accounts, with no single account above 0.7 GWh.', space_after=6, size=9.5)

para('Prepaid', bold=True, size=11.5, color=NAVY, space_after=3)
bullet('Customers are up 10.5% year over year', '(16,371 to 18,090) and 66 on the month, so growth continues.')
bullet('Volume was 2.7 GWh,', f'up 18% year over year but 9% below September. Usage per customer fell to 151 kWh from 167 in September (141 a year ago). Including RT20 prepaid the total is 2.8 GWh and 18,591 customers.')

para('Outside context', bold=True, size=11.5, color=NAVY, space_after=3)
bullet('Tourism is still well below last year.', 'Stayover arrivals were down 27.5% in the first quarter and international arrivals at Sangster were down 23.7% in August, which fits hotel volume still being about 19% below last year. Just over 1,900 rooms are expected back in December and Hyatt\u2019s seven resorts have moved to the first half of 2027.')
bullet('The economy is still contracting, but less.', 'The PIOJ expects July to September to fall 0.5% to 1.5% after a 2.9% fall in April to June, with output back to pre-Melissa levels as early as April to June 2027. That fits commercial volume near last year, not above it.')
bullet('Alcoa is permanent.', 'Century says the new Jamalco turbine came online in early August and the refinery now runs entirely on its own power.')
bullet('Cement has momentum.', 'Caribbean Cement reported record second-quarter volumes (110,647 tonnes). Last year its output was held back by an extended planned shutdown, kiln stoppages and the storm, which is the likely reason for the low October 2025 base. Third-quarter results are not out yet.')
bullet('Petrojam is under review.', 'The refinery lost its gasoline unit for 23 days from April (about US$3.6M) and a review of its operating options is due this quarter. A decision there would be a risk to this account.')
bullet('Weather points warm and dry.', 'The WMO expects El Ni\u00f1o to strengthen into early 2027 and the Met Service expects warmer, drier conditions. June rainfall was at 30-year lows in 11 parishes and JPS set its 2026 demand high on 1 July on heat. The official October summary is not out yet.')

para('', space_after=2)
para('Sources', bold=True, size=9, color=GREY, space_after=2)
for u in ['https://www.caribjournal.com/2026/07/13/jamaica-tourism-arrivals-down-27/', 'https://www.riotimesonline.com/jamaica-arrivals-fall-montego-bay-hurricane-melissa-2026/',
          'https://www.travelpulse.com/news/hotels-and-resorts/royalton-negril-reopens-as-jamaica-tourism-recovery-gains-steam', 'https://www.travelpulse.com/news/hotels-and-resorts/jamaica-resorts-update-reopen-timelines-for-sandals-hyatt-princess-and-more',
          'https://www.caribjournal.com/2026/04/12/jamaica-hyatt-all-inclusive-resorts-delays/', 'https://www.jamaicaobserver.com/2026/08/19/recovery-ahead-schedule/',
          'https://jamaica-gleaner.com/article/business/20260809/jamalco-unplugs-grid-power-turbine-set-save-us28m-year', 'https://jamaica-gleaner.com/article/business/20260730/cement-production-hits-record-2nd-quarter-profit-surges-fivefold',
          'https://jamaica-gleaner.com/article/business/20260703/petrojam-absorbs-us156000-day-loss-after-gas-unit-shuts-down-april', 'https://wmo.int/node/39136',
          'https://jis.gov.jm/met-service-says-11-parishes-recorded-30-year-low-rainfall-in-june/', 'https://www.jamaicaobserver.com/2026/07/08/heat-sends-power-demand-2026-high/']:
    p = para(u, size=8, color=GREY, space_after=0)
doc.save(OUT); print('saved', OUT)
