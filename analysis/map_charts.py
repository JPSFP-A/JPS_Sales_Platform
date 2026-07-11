import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')

rels_dir = r'D:\Projects\Sales_Platform\analysis\corp_perf_unpacked\ppt\slides\_rels'
for fname in sorted(os.listdir(rels_dir), key=lambda x: int(re.search(r'\d+', x).group())):
    path = os.path.join(rels_dir, fname)
    with open(path, encoding='utf-8') as f:
        content = f.read()
    charts = re.findall(r'charts/(chart[^"]+?)\.xml', content)
    imgs = re.findall(r'media/(image\d+\.[a-z]+)', content)
    slide_num = re.search(r'\d+', fname).group()
    if charts or imgs:
        print(f'Slide {slide_num}: charts={charts}  images={imgs}')

# Also check theme colors
theme_path = r'D:\Projects\Sales_Platform\analysis\corp_perf_unpacked\ppt\theme\theme1.xml'
with open(theme_path, encoding='utf-8') as f:
    theme = f.read()
colors = re.findall(r'<a:(dk1|dk2|lt1|lt2|accent[1-6])[^>]*>.*?<a:srgbClr val="([A-F0-9]+)"', theme, re.DOTALL)
print('\nTheme colors:')
for name, val in colors:
    print(f'  {name}: #{val}')
