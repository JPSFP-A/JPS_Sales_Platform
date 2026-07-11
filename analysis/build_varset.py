# -*- coding: utf-8 -*-
# Combine budget (Feb LE monthly) + actual (scan) into varset.json, normalised to J$M and MWh,
# by rate class & metric, with the matched YTD window (= actual 2026 months available).
import json, csv
DL=r'C:\Users\jwilson\Downloads'
def norm(s): return str(s).strip().upper()
RMAP={};RCMAP={}
for r in list(csv.reader(open(DL+r'\Rate categorry Data mapping.csv')))[1:]:
    if len(r)>=3:
        RMAP[norm(r[2])]=r[0]
        if norm(r[1]) not in RCMAP: RCMAP[norm(r[1])]=r[0]
def baseT(t): return 'RT60' if t=='RT60-ST' else t
B=json.load(open('budget_monthly.json'))
CLASSES=B['classes']; BMON=B['months']
d=json.load(open('corrected.json'))
L=d['srat_legend']; ix={n:i for i,n in enumerate(L)}; SEP=d.get('sep','||')
amons=[m for m in BMON if m in d['months']]            # actual months available within 2026
def title_of(key):
    s,rc=key.split(SEP,1); return baseT(RCMAP.get(norm(rc)) or RMAP.get(norm(s)) or 'UNMAPPED')
# ACTUAL monthly by class (J$M, MWh)
A={c:{k:{} for k in ['vol','demand','energy','fuel','ipp','cust','rev']} for c in CLASSES}
for mo in amons:
    for key,par in d['srat'][mo].items():
        t=title_of(key)
        if t not in A: continue
        for pg,v in par.items():
            A[t]['vol'][mo]=A[t]['vol'].get(mo,0)+v[ix['kwh']]/1000.0       # kWh->MWh
            A[t]['demand'][mo]=A[t]['demand'].get(mo,0)+(v[ix['kvap']]+v[ix['kval']]+v[ix['kvao']])/1e6
            A[t]['energy'][mo]=A[t]['energy'].get(mo,0)+v[ix['energy']]/1e6
            A[t]['fuel'][mo]=A[t]['fuel'].get(mo,0)+v[ix['fuel']]/1e6
            A[t]['ipp'][mo]=A[t]['ipp'].get(mo,0)+v[ix['ipp']]/1e6
            A[t]['cust'][mo]=A[t]['cust'].get(mo,0)+v[ix['cust']]/1e6
            # revenue ex-IPP (fuel+energy+demand+customer) to match budget TOTAL (excludes IPP pass-through)
            A[t]['rev'][mo]=A[t]['rev'].get(mo,0)+(v[ix['fuel']]+v[ix['energy']]+v[ix['cust']]+v[ix['kvap']]+v[ix['kval']]+v[ix['kvao']])/1e6
# BUDGET monthly by class (J$M, MWh)
def bcomp(name,c,mo):
    j=BMON.index(mo); return B['components'][name][c][j]/1000.0
Bud={c:{'vol':{},'demand':{},'energy':{},'fuel':{},'cust':{},'rev':{}} for c in CLASSES}
for c in CLASSES:
    for mo in BMON:
        j=BMON.index(mo)
        Bud[c]['vol'][mo]=B['VOLUME_MWH'][c][j]
        Bud[c]['demand'][mo]=bcomp('DEMAND',c,mo)
        Bud[c]['energy'][mo]=bcomp('ENERGY',c,mo)
        Bud[c]['fuel'][mo]=bcomp('FUEL',c,mo)
        Bud[c]['cust'][mo]=bcomp('CUSTOMER',c,mo)
        Bud[c]['rev'][mo]=bcomp('TOTAL',c,mo)
out={'classes':CLASSES,'budget_months':BMON,'actual_months':amons,'win':amons,
     'actual':A,'budget':Bud,'units':{'vol':'MWh','rev':'J$M','demand':'J$M','energy':'J$M'}}
json.dump(out,open('varset.json','w'))
# YTD summary print (matched window)
def ytdA(c,k): return sum(A[c][k].get(m,0) for m in amons)
def ytdB(c,k): return sum(Bud[c][k][m] for m in amons)
print('matched window:',amons)
print('%-6s %10s %10s %8s'%('Class','ActDem','BudDem','Var'))
for c in ['RT40','RT50','RT70']:
    print('%-6s %10.0f %10.0f %+8.0f'%(c,ytdA(c,'demand'),ytdB(c,'demand'),ytdA(c,'demand')-ytdB(c,'demand')))
print('wrote varset.json')
