# -*- coding: utf-8 -*-
# Converts a raw CIS "Billing Details Report" saved as tab-delimited text (Oct-26.xls: five-line report
# header, then the Cust_Code header row) into the comma-delimited "<Mon> <YY>.csv" form the monthly
# scripts read (rt10_zero_fix.py and _push_month_adjustments.py only take the .csv spelling).
# The source file is left untouched. Usage: python convert_billing_xls.py "Oct-26.xls" "Oct 26.csv"
import csv, sys
src, dst = sys.argv[1], sys.argv[2]
hdr = None; n = 0; short = 0; long_ = 0; blank = 0; preamble = 0
with open(src, encoding='latin-1', errors='replace') as fi, open(dst, 'w', encoding='utf-8', newline='') as fo:
    w = csv.writer(fo)
    for line in fi:
        cells = line.rstrip('\r\n').split('\t')
        if hdr is None:
            if cells and cells[0] == 'Cust_Code':
                hdr = cells; w.writerow(cells)
            else:
                preamble += 1
            continue
        if not any(c.strip() for c in cells):
            blank += 1; continue
        if len(cells) < len(hdr): short += 1; cells = cells + [''] * (len(hdr) - len(cells))   # CIS drops the trailing empty cell on .xls rows; the .csv form carries it
        if len(cells) > len(hdr): long_ += 1
        w.writerow(cells); n += 1
print('preamble lines skipped: %d | header cols: %d | data rows written: %d | blank lines dropped: %d | rows shorter than header: %d | longer: %d' % (preamble, len(hdr), n, blank, short, long_))
