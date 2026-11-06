# -*- coding: utf-8 -*-
# Detailed Sales Forecast Driver Report: the 7 September report, refreshed for the September 2026 close.
# FY2026, FY2027 and FY2028 totals are held at the financials (3,299.7 / 3,439.5 / 3,514.7 GWh).
# Account and industry tables are as in the 7 September report; only opening text, totals and basis are updated.
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
s = open(os.path.join(ROOT, 'JPS_Sales_Forecast_Driver_Report.html'), encoding='utf-8').read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (old[:70], n, count)
    s = s.replace(old, new)

# header
rep('7 September 2026 &middot; Supporting detail to the Executive Summary &middot; updated for the August close',
    '23 October 2026 &middot; Supporting detail to the Executive Summary &middot; updated for the September close')
rep('Volumes are produced by the Driver Forecast engine and are identical to those in the Executive Summary and the Sales &amp; Generation workbook. FY2026 no longer ties to the 3,281,970 MWh submitted on 19 August 2026: August has closed and the register has moved since. FY2026 now stands at 3,299.7 GWh, +17.7 GWh above the submission (Section 11).',
    'Volumes are held at the financials and are identical to those in the Sales &amp; Generation workbook. FY2026 no longer ties to the 3,281,970 MWh submitted on 19 August 2026: nine months have closed and the register has moved since. FY2026 stands at 3,299.7 GWh, +17.7 GWh above the submission, with January to September actual at 2,429.0 GWh (Section 11).')

# totals held at the financials
rep('<td>3,439.6</td><td class="pos">+4.2%</td><td>3,514.8</td>', '<td>3,439.5</td><td class="pos">+4.2%</td><td>3,514.7</td>')
rep('font-size="10">3,439.6</text>', 'font-size="10">3,439.5</text>')
rep('font-size="10">3,514.8</text>', 'font-size="10">3,514.7</text>')
rep('font-size="10">3,439.7</text>', 'font-size="10">3,439.5</text>')
rep('3,299.7 to 3,439.6', '3,299.7 to 3,439.5')
rep('3,439.7 to 3,514.8', '3,439.5 to 3,514.7')
rep('(+139.9 GWh)', '(+139.8 GWh)')
rep('they sum to +139.9.', 'they sum to +139.8.')
rep('<td class="pos">+139.9</td>', '<td class="pos">+139.8</td>')
rep('(+75.1 GWh)', '(+75.2 GWh)')
rep('<td class="pos">+75.1</td>', '<td class="pos">+75.2</td>')
rep('font-size="9.5">+16.1</text>', 'font-size="9.5">+16.2</text>')
rep('<td class="pos">+16.1</td>', '<td class="pos">+16.2</td>')
rep('netting to the +16.1 shown', 'netting to the +16.2 shown')
rep('<td class="neg">-14.6</td>', '<td class="neg">-14.7</td>')
rep('<td>Everything else</td><td>RT20 comm / RT40/50/60/70</td><td class="neg">&minus;3.1</td>', '<td>Everything else</td><td>RT20 comm / RT40/50/60/70</td><td class="neg">&minus;3.2</td>')

# section 2 paragraph on the FY2026 starting point
i = s.index('FY2026 was then updated 11 Sep 2026')
j = s.index('</div>', i)
s = s[:i] + ('At the September close FY2026 is held at 3,299.7 GWh and FY2027 at 3,439.5 GWh, so the total movement reads +139.8. '
             'The 0.1 GWh difference from the earlier +139.9 sits in Commercial load adjustment, which is a plug to the verified total and not an independently re-derived figure.') + s[j:]

# section 11 basis
i = s.index('<li>FY2025 is billed actual.'); j = s.index('</li>', i) + 5
s = s[:i] + ('<li>FY2025 is billed actual. FY2026 is January&ndash;September billed actual (2,429.0 GWh) with October&ndash;December forecast, held at the financials LE of 3,299.7 GWh. '
             'It no longer ties to the 3,281,970 MWh submitted on 19 August 2026: nine months have closed and the register has moved since the submission was pinned. '
             'FY2026 stands at 3,299.7 GWh, +17.7 GWh above the submission. September closed at 294.8 GWh, 9.1 GWh above the register forecast; the full year is held, so the fourth quarter is set 9.1 GWh lower (870.6 GWh against 879.7 GWh). '
             'The submission itself stays frozen as the number of record; this report states the live number and the gap, not a reconciled replacement for it.</li>') + s[j:]
i = s.index('<li>System losses: FY2026 closes'); j = s.index('</li>', i) + 5
s = s[:i] + ('<li>System losses: FY2026 closes the year at <b>27.1%</b>, in line with the 27.10% target and the financials LE. FY2027/FY2028 targets and their monthly loss path are unchanged '
             '(seasonality from 2024&ndash;2025 billed actuals, hurricane months excluded).</li>') + s[j:]

out_html = os.path.join(HERE, '_driver_report_detail_sep2026.html')
open(out_html, 'w', encoding='utf-8').write(s)
print('wrote', out_html)
# leftover check on figures that should no longer appear
for pat in ('3,439.6', '3,514.8', '3,439.7', '+139.9', '26.99%', 'August close'):
    print(pat, s.count(pat))
