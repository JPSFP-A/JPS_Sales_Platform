# -*- coding: utf-8 -*-
# Top Variance Movers: actual vs ESTIMATED budget by customer (RT40/50/70) and RT10 bucket.
# Estimated budget = customer's Jan+Feb actual share of class x budgeted class total (which carries
# the 2026 monthly/seasonal shape). Variance = actual - estimated budget. YTD Jan-May 2026.
import json
B=json.load(open('budget_monthly.json'))      # class budget by month (2026)
D=json.load(open('app_data2.json'))            # customer actuals (9 months, split by class)
import os
_cf='corrected.json' if (os.path.exists('corrected.json') and len(json.load(open('corrected.json')).get('months',[]))>=9) else 'corrected_noRT20acct.json'
COR=json.load(open(_cf))          # RT10 buckets (use full backup while a re-scan is mid-flight)
AM=D['months']; YTD=[m for m in AM if m.startswith('2026')]; JF=['2026-01','2026-02']
ai={m:AM.index(m) for m in AM}
bi={m:B['months'].index(m) for m in B['months']}
def bclassYTD(metric,cls):
    if metric=='vol': arr=B['VOLUME_MWH'].get(cls,[0]*12); k=1.0
    elif metric=='dem': arr=B['components']['DEMAND'].get(cls,[0]*12); k=1000.0
    else: arr=B['components']['TOTAL'].get(cls,[0]*12); k=1000.0
    return sum(arr[bi[m]] for m in YTD)*k
# actual accessors (MWh, J$, J$ ex-IPP)
def av(a,i): return a['kwh'][i]/1000.0
def ad(a,i): return a['dem'][i]
def ar(a,i): return a['fuel'][i]+a['energy'][i]+a['dem'][i]+a['cust'][i]
MET={'vol':av,'dem':ad,'rev':ar}
_MLAB={'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun','07':'Jul','08':'Aug','09':'Sep','10':'Oct','11':'Nov','12':'Dec'}
_ytd_lbl=('%s-%s %s'%(_MLAB[YTD[0][5:7]],_MLAB[YTD[-1][5:7]],YTD[0][:4])) if len(YTD)>1 else ('%s %s'%(_MLAB[YTD[0][5:7]],YTD[0][:4]) if YTD else 'n/a')
out={'window':_ytd_lbl,'note':'Estimated budget = Jan+Feb actual share x budgeted class total (seasonally shaped). Variance = Actual - Est. Budget.',
     'byCustomer':{},'byBucketRT10':{}}
CLS=['RT40','RT50','RT70']
for metric,fn in MET.items():
    rows=[]
    for cls in CLS:
        accts=[a for a in D['accts'] if a['c']==cls]
        clsJF=sum(fn(a,ai[m]) for a in accts for m in JF) or 1.0
        budYTD=bclassYTD(metric,cls)
        for a in accts:
            jf=sum(fn(a,ai[m]) for m in JF)
            share=jf/clsJF
            est=share*budYTD
            act=sum(fn(a,ai[m]) for m in YTD)
            if abs(act)<1e-6 and abs(est)<1e-6: continue
            rows.append({'name':a['n'],'cls':cls,'act':round(act,2),'bud':round(est,2),'var':round(act-est,2)})
    rows.sort(key=lambda r:-abs(r['var']))
    out['byCustomer'][metric]=rows[:40]
# RT10 buckets (vol + rev only; no demand)
binkeys=set()
for mo in YTD: binkeys|=set(COR['bucket'].get(mo,{}).get('RT10',{}).keys())
def bucketYTD(bn,idx):  # idx: 1=kwh,2=rev  (bucket_legend: count,kwh,rev,energy,fuel,ipp,cust)
    return sum(COR['bucket'].get(mo,{}).get('RT10',{}).get(bn,[0]*7)[idx] for mo in YTD)
def bucketJF(bn,idx):
    return sum(COR['bucket'].get(mo,{}).get('RT10',{}).get(bn,[0]*7)[idx] for mo in JF)
BIN=COR.get('bin',50)
def blabel(bn):
    b=int(bn)
    if b<0: return 'credits/<0'
    return '%d-%d kWh'%(b,b+BIN)
for metric,idx,kfac in [('vol',1,1/1000.0),('rev',2,1.0)]:
    budYTD=bclassYTD(metric,'RT10')
    jfTot=sum(bucketJF(bn,idx) for bn in binkeys) or 1.0
    rows=[]
    for bn in binkeys:
        share=bucketJF(bn,idx)/jfTot
        est=share*budYTD/(kfac if metric=='vol' else 1)  # careful units below
        act=bucketYTD(bn,idx)
        # normalise: vol bucket kwh -> MWh; budget vol MWh. rev J$.
        actN=act*kfac; estN=share*budYTD
        rows.append({'bucket':blabel(bn),'bin':int(bn),'act':round(actN,1),'bud':round(estN,1),'var':round(actN-estN,1)})
    rows.sort(key=lambda r:-abs(r['var']))
    out['byBucketRT10'][metric]=rows[:30]
json.dump(out,open('top_movers.json','w'))
# merge into app_data2.json so the explorer can embed it
AD=json.load(open('app_data2.json')); AD['movers']=out; json.dump(AD,open('app_data2.json','w'))
# print top 8 movers per metric (customers)
for metric in MET:
    print('=== TOP %s movers (customer) ==='%metric.upper())
    for r in out['byCustomer'][metric][:8]:
        print('  %-30s %-5s act=%11.1f bud=%11.1f var=%+11.1f'%(r['name'][:30],r['cls'],r['act'],r['bud'],r['var']))
