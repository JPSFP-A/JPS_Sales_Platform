import json
DATA=open('app_data.json','r',encoding='utf-8').read().strip()
TPL=open('app_template.html','r',encoding='utf-8').read()
out=TPL.replace('__DATA__',DATA)
open('tariff_app.html','w',encoding='utf-8').write(out)
open('index.html','w',encoding='utf-8').write(out)
print('wrote tariff_app.html + index.html',len(out),'bytes')
