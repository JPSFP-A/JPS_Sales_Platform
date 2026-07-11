# -*- coding: utf-8 -*-
# Rebuild explorer data from corrected.json: proper rate classes (rate_class-aware),
# per-account components (fuel/ipp/energy/demand/cust) + parish, all 9 months.
import json, csv
DL=r'C:\Users\jwilson\Downloads'
def norm(s): return str(s).strip().upper()
RMAP={};RCMAP={}
for r in list(csv.reader(open(DL+r'\Rate categorry Data mapping.csv')))[1:]:
    if len(r)>=3:
        RMAP[norm(r[2])]=r[0]
        if norm(r[1]) not in RCMAP: RCMAP[norm(r[1])]=r[0]
CLASSES=['RT10','RT20','RT40','RT50','RT60','RT70','Other']
def baseT(t):
    if t=='RT60-ST': return 'RT60'
    return t if t in CLASSES else 'Other'
d=json.load(open('corrected.json'))
L=d['srat_legend']; ix={n:i for i,n in enumerate(L)}; SEP=d.get('sep','||')
AL=d['acct_legend']; aix={n:i for i,n in enumerate(AL)}
months=d['months']; M=len(months)
MLAB={'2025-05':'May·25','2025-10':'Oct·25','2025-11':'Nov·25','2025-12':'Dec·25','2026-01':'Jan·26','2026-02':'Feb·26','2026-03':'Mar·26','2026-04':'Apr·26','2026-05':'May·26','2026-06':'Jun·26'}
mlabels=[MLAB.get(m,m) for m in months]
def title_of(key):
    s,rc=key.split(SEP,1); return baseT(RCMAP.get(norm(rc)) or RMAP.get(norm(s)) or 'Other')
KEYS=['kwh','rev','demand','fuel','energy','ipp','cust_chg']
cls={c:{k:[0.0]*M for k in KEYS} for c in CLASSES}
parishAgg={}   # parish -> per-month kwh,rev
for j,mo in enumerate(months):
    for key,par in d['srat'][mo].items():
        t=title_of(key)
        for pg,v in par.items():
            cc=cls[t]
            cc['kwh'][j]+=v[ix['kwh']]; cc['rev'][j]+=v[ix['rev']]
            cc['demand'][j]+=v[ix['kvap']]+v[ix['kval']]+v[ix['kvao']]
            cc['fuel'][j]+=v[ix['fuel']]; cc['energy'][j]+=v[ix['energy']]; cc['ipp'][j]+=v[ix['ipp']]; cc['cust_chg'][j]+=v[ix['cust']]
            pa=parishAgg.setdefault(pg,{k:[0.0]*M for k in KEYS})
            pa['kwh'][j]+=v[ix['kwh']]; pa['rev'][j]+=v[ix['rev']]
            pa['demand'][j]+=v[ix['kvap']]+v[ix['kval']]+v[ix['kvao']]
            pa['fuel'][j]+=v[ix['fuel']]; pa['energy'][j]+=v[ix['energy']]; pa['ipp'][j]+=v[ix['ipp']]; pa['cust_chg'][j]+=v[ix['cust']]
total={k:[sum(cls[c][k][j] for c in CLASSES) for j in range(M)] for k in KEYS}
# accounts (non RT10/RT20) with components + parish
accts=[]
for code,a in d['acct'].items():
    t=baseT(a['title'])
    rec={'id':code,'n':a['name'],'c':t,'pg':a.get('pg','UNMAPPED'),
         'kwh':[0]*M,'rev':[0]*M,'dem':[0]*M,'fuel':[0]*M,'energy':[0]*M,'ipp':[0]*M,'cust':[0]*M}
    for j,mo in enumerate(months):
        v=a['m'].get(mo)
        if not v: continue
        rec['kwh'][j]=v[aix['kwh']]; rec['rev'][j]=v[aix['rev']]
        rec['dem'][j]=v[aix['kvap']]+v[aix['kval']]+v[aix['kvao']]
        rec['fuel'][j]=v[aix['fuel']]; rec['energy'][j]=v[aix['energy']]; rec['ipp'][j]=v[aix['ipp']]; rec['cust'][j]=v[aix['cust']]
    if any(rec['kwh']) or any(rec['rev']): accts.append(rec)
# round
for c in cls.values():
    for k in c: c[k]=[round(x,1) for x in c[k]]
for k in total: total[k]=[round(x,1) for x in total[k]]
parishes=sorted(parishAgg.keys())
for p in parishAgg:
    for k in parishAgg[p]: parishAgg[p][k]=[round(x,1) for x in parishAgg[p][k]]
out={'months':months,'mlabels':mlabels,'classes':['RT10','RT20','RT40','RT50','RT60','RT70','Other'],
     'cls':cls,'total':total,'accts':accts,'parishes':parishes,'parish':parishAgg}
json.dump(out,open('app_data2.json','w'))
print('wrote app_data2.json | classes rev YTD(last5) J$B:',{c:round(sum(cls[c]['rev'][-5:])/1e9,2) for c in CLASSES})
print('accts:',len(accts),'| parishes:',len(parishes),'| acct has components:',[k for k in accts[0] if k not in ("n","c","pg")])
