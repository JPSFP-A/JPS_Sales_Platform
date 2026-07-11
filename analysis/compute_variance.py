# -*- coding: utf-8 -*-
# Budget (Feb 2026 LE) vs Actual (meter scan) variance for 2026 YTD, by rate class.
# Metrics: Volume (kWh), Revenue (+ components Fuel/IPP/Energy/Demand/Customer), Demand (J$).
# All J$ . Budget revenue stored in J$000 -> x1000; budget volume MWh -> x1000 kWh.
import json,csv
DL=r'C:\Users\jwilson\Downloads'
WIN=['2026-01','2026-02','2026-03','2026-04','2026-05']   # YTD window (must match budget cols 150-154)
CLASSES=['RT10','RT20','RT40','RT50','RT60','RT70']
def norm(s): return str(s).strip().upper()
RMAP={};RCMAP={}
for r in list(csv.reader(open(DL+r'\Rate categorry Data mapping.csv')))[1:]:
    if len(r)>=3:
        RMAP[norm(r[2])]=r[0]
        if norm(r[1]) not in RCMAP: RCMAP[norm(r[1])]=r[0]
def base(t):  # collapse RT60-ST -> RT60
    return 'RT60' if t=='RT60-ST' else t
d=json.load(open('corrected.json'))
L=d['srat_legend']; ix={n:i for i,n in enumerate(L)}; SEP=d.get('sep','||')
have=[m for m in WIN if m in d['months']]
def title_of(key):
    srat,rc=key.split(SEP,1); return base(RCMAP.get(norm(rc)) or RMAP.get(norm(srat)) or 'UNMAPPED')
# ---- ACTUAL by class ----
act={c:{'kwh':0.0,'rev':0.0,'fuel':0.0,'ipp':0.0,'energy':0.0,'demand':0.0,'cust':0.0} for c in CLASSES}
for mo in have:
    for key,par in d['srat'][mo].items():
        t=title_of(key)
        if t not in act: continue
        for pg,v in par.items():
            a=act[t]
            a['kwh']+=v[ix['kwh']]; a['rev']+=v[ix['rev']]; a['fuel']+=v[ix['fuel']]
            a['ipp']+=v[ix['ipp']]; a['energy']+=v[ix['energy']]
            a['demand']+=v[ix['kvap']]+v[ix['kval']]+v[ix['kvao']]; a['cust']+=v[ix['cust']]
# ---- BUDGET by class (Feb LE) ----
b=json.load(open('budget_febLE_2026ytd.json'))
def bud(comp,c): return b.get(comp,{}).get(c,0.0)*1000.0       # J$000 -> J$
bud_ipp_total=12553.0*1e6                                       # IPP surcharge YTD J$ (total; not split by class)
budget={c:{'kwh':b['VOLUME_MWH'].get(c,0)*1000.0,
           'fuel':bud('FUEL',c),'energy':bud('ENERGY',c),'demand':bud('DEMAND',c),
           'cust':bud('CUSTOMER',c),'rev':bud('TOTAL',c)} for c in CLASSES}
out={'window':have,'classes':CLASSES,'actual':act,'budget':budget,
     'budget_ipp_total':bud_ipp_total,
     'actual_ipp_total':sum(act[c]['ipp'] for c in CLASSES),
     'note_complete': have==WIN}
json.dump(out,open('variance_data.json','w'))
# ---- print summary ----
print('window:',have,'(complete)' if have==WIN else '(PARTIAL)')
def B(x): return x/1e9
print('\n%-6s | %22s | %22s | %22s'%('Class','VOLUME GWh A/B/Var','REVENUE J$B A/B/Var','DEMAND J$B A/B/Var'))
tA=tB=0
for c in CLASSES:
    a=act[c]; bu=budget[c]
    vA,vB=a['kwh']/1e6,bu['kwh']/1e6
    rA,rB=B(a['rev']),B(bu['rev'])
    dA,dB=B(a['demand']),B(bu['demand'])
    print('%-6s | %6.1f %6.1f %+6.1f | %6.2f %6.2f %+6.2f | %6.2f %6.2f %+6.2f'%(c,vA,vB,vA-vB,rA,rB,rA-rB,dA,dB,dA-dB))
totV_a=sum(act[c]['kwh'] for c in CLASSES)/1e6; totV_b=sum(budget[c]['kwh'] for c in CLASSES)/1e6
totR_a=sum(act[c]['rev'] for c in CLASSES)/1e9; totR_b=sum(budget[c]['rev'] for c in CLASSES)/1e9
totD_a=sum(act[c]['demand'] for c in CLASSES)/1e9; totD_b=sum(budget[c]['demand'] for c in CLASSES)/1e9
print('%-6s | %6.1f %6.1f %+6.1f | %6.2f %6.2f %+6.2f | %6.2f %6.2f %+6.2f'%('TOTAL',totV_a,totV_b,totV_a-totV_b,totR_a,totR_b,totR_a-totR_b,totD_a,totD_b,totD_a-totD_b))
print('\nwrote variance_data.json')
