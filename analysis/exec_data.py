# -*- coding: utf-8 -*-
# Apr -> May 2026 MONTH-ON-MONTH movement by account, tied to the CFO's explanations.
import json
D=json.load(open('app_data2.json'))
AM=D['months']; iA=AM.index('2026-04'); iC=AM.index('2026-05')
def g(a,k,i): return a[k][i] if (k in a and i<len(a[k])) else 0
def revx(a,i): return g(a,'rev',i)-g(a,'fuel',i)   # revenue EX-FUEL (fuel is a margin-less pass-through)
NAMED=[
 ('wigton',('IPP','IPP account; granted a demand break for equipment failure, effective May')),
 ('musson international dairies',('Adjustment','Debit adjustment in April — billed with an incorrect multiplier (April overstated)')),
 ('jamaica private power',('IPP','IPP account; usage depends on self-generation')),
 ('bay roc',('Ratchet','Ratcheted demand since the hurricane; steps down MoM toward ~80% of actual usage')),
 ('x fund',('Ratchet','Ratcheted demand since the hurricane; steps down MoM toward ~80% of actual usage')),
 ('west kingston power',('IPP','IPP account; usage depends on self-generation')),
 ('baking enterprise',('Ratchet','Ratcheted demand since the hurricane; steps down MoM toward ~80% of actual usage')),
 ('continental baking',('Ratchet','Ratcheted demand since the hurricane; steps down MoM toward ~80% of actual usage')),
 ('jamaica energy partners',('IPP','IPP account; usage depends on self-generation')),
 ('german ship',('Normal','Normal billing, in keeping with usage pattern')),
 ('content solar',('IPP','IPP account; usage depends on self-generation')),
 ('gleaner',('Operational','Property recently sold; operations have decreased')),
 ('seawind',('Ratchet','Ratcheted demand since the hurricane; steps down MoM toward ~80% of actual usage')),
 ('kingston free port',('Normal','Normal billing, in keeping with usage pattern')),
 ('alcoa',('IPP','IPP account; usage depends on self-generation')),
 ('playa hall',('Operational','RT50 idle; RT70 billed a higher demand in May than April')),
 ('windalco',('Normal','Normal billing, in keeping with usage pattern')),
 ('hodges',('Adjustment','Credit adjustment — no power after hurricane; demand charges written off')),
 ('bay juices',('Adjustment','Debit adjustment in April — delay in account set-up (April overstated)')),
 ('supreme ventures racing',('Normal','6 active RT40 accounts, within normal usage pattern')),
 ('convenient brands',('Operational','All accounts inactive as of April')),
 ('caribbean broilers',('Normal','Normal billing')),
]
def mom(accs):
    dA=sum(g(a,'dem',iA) for a in accs); dC=sum(g(a,'dem',iC) for a in accs)
    rA=sum(revx(a,iA) for a in accs); rC=sum(revx(a,iC) for a in accs)
    kA=sum(g(a,'kwh',iA) for a in accs); kC=sum(g(a,'kwh',iC) for a in accs)
    return {'dem':round((dC-dA)/1e6,1),'demp':round((dC/dA-1)*100,1) if dA else 0,
            'rev':round((rC-rA)/1e6,1),'revp':round((rC/rA-1)*100,1) if rA else 0,
            'vol':round((kC-kA)/1e6,2),'volp':round((kC/kA-1)*100,1) if kA else 0}
rows=[]; named_pats=[p for p,_ in NAMED]
for pat,(cat,note) in NAMED:
    accs=[a for a in D['accts'] if pat in a['n'].lower()]
    if not accs: continue
    m=mom(accs); m.update(name=accs[0]['n'],cls=' & '.join(sorted(set(a['c'] for a in accs))),cat=cat,note=note)
    rows.append(m)
cats={}
for r in rows:
    c=cats.setdefault(r['cat'],{'dem':0,'rev':0,'n':0}); c['dem']+=r['dem']; c['rev']+=r['rev']; c['n']+=1
# investigate: biggest Apr->May MoM movers (demand or revenue J$M) not annotated
agg={}
for a in D['accts']:
    if any(p in a['n'].lower() for p in named_pats): continue
    agg.setdefault(a['n'],[]).append(a)
inv=[]
for nm,accs in agg.items():
    m=mom(accs)
    if max(abs(m['dem']),abs(m['rev']))<5: continue
    m.update(name=nm,cls=' & '.join(sorted(set(a['c'] for a in accs))))
    inv.append(m)
inv.sort(key=lambda r:-max(abs(r['dem']),abs(r['rev']))); inv=inv[:9]
for r in inv:
    r['flag']=('Volume up but demand down MoM — possible dilution' if r['volp']>1 and r['demp']<-3 else
               'Large MoM swing — confirm driver' if max(abs(r['demp']),abs(r['revp']))>15 else
               'Large RT70 — confirm self-generation / IPP' if 'RT70' in r['cls'] else 'Material MoM move — confirm driver')
out={'window':'April -> May 2026 (MoM)','rows':rows,'cats':{k:{'dem':round(v['dem'],1),'rev':round(v['rev'],1),'n':v['n']} for k,v in cats.items()},'investigate':inv}
# --- REVENUE QUALITY: accounts where revenue & demand DIVERGE, with component breakdown ---
def ck(accs,k): return (sum(g(a,k,iC) for a in accs)-sum(g(a,k,iA) for a in accs))/1e6
allg={}
for a in D['accts']: allg.setdefault(a['n'],[]).append(a)
div=[]
for nm,accs in allg.items():
    dR=(sum(revx(a,iC) for a in accs)-sum(revx(a,iA) for a in accs))/1e6; dD=ck(accs,'dem')
    if abs(dR)<1.5 or (dR>0)==(dD>0): continue   # keep only divergent, material
    div.append({'name':nm,'cls':' & '.join(sorted(set(a['c'] for a in accs))),'rev':round(dR,1),'dem':round(dD,1),
                'energy':round(ck(accs,'energy'),1),'ipp':round(ck(accs,'ipp'),1),'cust':round(ck(accs,'cust'),1)})
# also force-include accounts flagged by CFO as "Normal" where demand fell regardless of ex-fuel threshold
force=['kingston free port','windalco','caribbean broilers']
for nm,accs in allg.items():
    if not any(p in nm.lower() for p in force): continue
    if any(r['name']==nm for r in div): continue
    dR=(sum(revx(a,iC) for a in accs)-sum(revx(a,iA) for a in accs))/1e6; dD=ck(accs,'dem')
    div.append({'name':nm,'cls':' & '.join(sorted(set(a['c'] for a in accs))),'rev':round(dR,1),'dem':round(dD,1),
                'energy':round(ck(accs,'energy'),1),'ipp':round(ck(accs,'ipp'),1),'cust':round(ck(accs,'cust'),1)})
div.sort(key=lambda r:-abs(r['dem'])); out['divergence']=div[:7]
al=[a for a in D['accts'] if 'alcoa' in a['n'].lower()]
if al:
    dR=(sum(revx(a,iC) for a in al)-sum(revx(a,iA) for a in al))/1e6; comp=sum(ck(al,k) for k in ['energy','ipp','cust','dem']); out['alcoa_adj']={'rev':round(dR,1),'comp':round(comp,1),'adj':round(dR-comp,1)}
json.dump(out,open('exec_data.json','w'))
print('\nREVENUE-DEMAND DIVERGENCE:')
for r in div[:7]: print('  %-30s %-12s rev %+6.1f dem %+6.1f energy %+6.1f ipp %+6.1f'%(r['name'][:30],r['cls'],r['rev'],r['dem'],r['energy'],r['ipp']))
print('Alcoa adj:',out.get('alcoa_adj'))
import io,sys; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
print('APR->MAY MoM CATEGORY ROLLUP (J$M change):')
for k,v in sorted(cats.items(),key=lambda x:x[1]['dem']):
    print('  %-12s n=%-2d demChg=%+8.1f revChg=%+8.1f'%(k,v['n'],v['dem'],v['rev']))
print('\nNAMED ACCOUNTS (Apr->May):')
for r in sorted(rows,key=lambda x:x['dem']):
    print('  %-30s %-12s %-11s dem %+6.1fM (%+6.1f%%)  rev %+6.1fM'%(r['name'][:30],r['cls'],r['cat'],r['dem'],r['demp'],r['rev']))
print('\nINVESTIGATE (top MoM movers, not annotated):')
for r in inv:
    print('  %-28s %-12s dem %+6.1fM (%+6.1f%%)  rev %+6.1fM (%+6.1f%%)  [%s]'%(r['name'][:28],r['cls'],r['dem'],r['demp'],r['rev'],r['revp'],r['flag']))
