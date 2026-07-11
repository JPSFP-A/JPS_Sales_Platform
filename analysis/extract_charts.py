import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')
from lxml import etree

CHART_DIR = r'D:\Projects\Sales_Platform\analysis\corp_perf_unpacked\ppt\charts'

# Read standard charts
for fname in sorted(os.listdir(CHART_DIR)):
    if not fname.startswith('chart') or not fname.endswith('.xml'):
        continue
    path = os.path.join(CHART_DIR, fname)
    with open(path, encoding='utf-8') as f:
        content = f.read()
    tree = etree.fromstring(content.encode('utf-8'))
    ns = {'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart',
          'cx': 'http://schemas.microsoft.com/office/drawing/2016/5/9/chartex'}
    print(f'\n=== {fname} ===')
    # Try standard chart series
    for ser in tree.findall('.//c:ser', ns):
        tx = ser.find('.//c:tx//c:v', ns)
        name = tx.text if tx is not None else '?'
        vals = [v.text for v in ser.findall('.//c:val//c:v', ns)]
        cats = [v.text for v in ser.findall('.//c:cat//c:v', ns)]
        print(f'  Series: {name}')
        print(f'  Categories: {cats[:12]}')
        print(f'  Values: {vals[:12]}')
    # Try chartEx series
    for ser in tree.findall('.//cx:series', ns):
        tx = ser.find('.//cx:tx//cx:v', ns)
        name = tx.text if tx is not None else '?'
        vals = [pt.text for pt in ser.findall('.//cx:pt', ns)]
        cats = []
        for cat_elem in ser.findall('.//cx:strDim//cx:f', ns):
            cats.append(cat_elem.text or '')
        print(f'  Series: {name}')
        print(f'  Categories: {cats[:12]}')
        print(f'  Values: {vals[:12]}')
