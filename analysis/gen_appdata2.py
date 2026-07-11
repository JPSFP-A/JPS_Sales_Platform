import json
M=json.load(open('multi.json'))
LC={n:i for i,n in enumerate(M['legend_class'])}   # count,kwh,rev,energy,demand,fuel,ipp,cust_chg,kva
LA={n:i for i,n in enumerate(M['legend_acct'])}     # kwh,rev,demand,energy,fuel,kva
months=M['months']
def mlabel(m):
    y,mo=m.split('-'); MN=['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    return MN[int(mo)]+'·'+y[2:]
CLS=['RT10','RT20','RT40','RT50','RT60','RT70']
def cseries(grp,metric):
    out=[]
    for m in months:
        a=M['class'].get(m,{}).get(grp)
        out.append(round(a[LC[metric]],2) if a else 0)
    return out
clsdata={}
for c in CLS:
    clsdata[c]={k:cseries(c,k) for k in ['kwh','rev','demand','fuel','energy','ipp','cust_chg']}
# total = sum of all groups present
def totseries(metric):
    out=[]
    for m in months:
        out.append(round(sum(a[LC[metric]] for a in M['class'].get(m,{}).values()),2))
    return out
total={k:totseries(k) for k in ['kwh','rev','demand','fuel','energy','ipp','cust_chg']}
# industrial accounts: per-month [kwh,rev,demand]
accts=[]
for code,r in M['acct'].items():
    kwh=[]; rev=[]; dem=[]
    for m in months:
        v=r['m'].get(m)
        kwh.append(round((v[LA['kwh']] if v else 0)))
        rev.append(round((v[LA['rev']] if v else 0)))
        dem.append(round((v[LA['demand']] if v else 0)))
    if sum(kwh)==0 and sum(rev)==0: continue
    accts.append({'n':r['name'],'c':r['cls'],'kwh':kwh,'rev':rev,'dem':dem})
out=dict(months=months, mlabels=[mlabel(m) for m in months], classes=CLS,
         cls=clsdata, total=total, accts=accts)
json.dump(out, open('app_data2.json','w'))
print('months',len(months),'classes',len(CLS),'industrial accts',len(accts),
      '| bytes ~',len(json.dumps(out)))
