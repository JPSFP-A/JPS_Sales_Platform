import json
d=json.load(open('cust_accounts.json')); L={n:i for i,n in enumerate(d['_legend'])}
NM,CL,KW,RV,DM=L['name'],L['class'],L['kwh'],L['rev'],L['demand']
tariff=json.load(open('tariff_app_data.json'))
A25,A26,AAP=d['May25']['acc'],d['May26']['acc'],d['Apr26']['acc']
codes=set(A25)|set(A26)|set(AAP)
RC={'RT40','RT50','RT70'}
rows=[]
for c in codes:
    a=A25.get(c); ap=AAP.get(c); b=A26.get(c)
    ref=b or ap or a
    cls=ref[CL]
    if cls not in RC: continue
    g=lambda r,i:(round(r[i]) if r else 0)
    name=ref[NM]
    if not (g(a,KW) or g(ap,KW) or g(b,KW)): continue
    rows.append([name, cls,
        g(ap,KW),g(a,KW),g(b,KW),      # kwh apr, may25, may26
        g(ap,RV),g(a,RV),g(b,RV),      # rev
        g(ap,DM),g(a,DM),g(b,DM)])     # demand
out=dict(byClass=tariff['byClass'], total=tariff['total'], trend=tariff['trend'],
         accts=rows,
         leg=['name','cls','ka','k25','k26','ra','r25','r26','da','d25','d26'])
json.dump(out, open('app_data.json','w'))
print('industrial accts:',len(rows),'| bytes ~',len(json.dumps(out)))
# sanity: class totals both bases
for cls in ['RT40','RT50','RT70']:
    g=[r for r in rows if r[1]==cls]
    yoy=lambda f25,f26: (sum(r[f26] for r in g)/sum(r[f25] for r in g)-1)*100 if sum(r[f25] for r in g) else 0
    print(f"  {cls}: n={len(g)} YoY rev {yoy(6,7):+.1f}% demand {yoy(9,10):+.1f}% | MoM rev {yoy(5,7):+.1f}% demand {yoy(8,10):+.1f}%")
