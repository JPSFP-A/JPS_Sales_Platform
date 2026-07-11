import json
DATA=open('app_data2.json','r',encoding='utf-8').read().strip()
TPL=open('app2_template.html','r',encoding='utf-8').read()
out=TPL.replace('__DATA__',DATA)
open('sales_explorer.html','w',encoding='utf-8').write(out)
open('index.html','w',encoding='utf-8').write(out)
print('wrote sales_explorer.html + index.html',len(out),'bytes')
