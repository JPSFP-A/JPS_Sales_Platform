import json
A=json.load(open('_fy27_actuals.json')); R=json.load(open('_fy27_result.json')); f=R['f27']; sh=json.load(open('_fy27_shape_res.json'))
CL=['RT10','RT20','RT40','RT50','RT60-ST','RT70']
def shape(c):
    if c in sh: return sh[c]
    g=lambda y,m: A['%d-%02d'%(y,m)][c]
    return (g(2024,11)/g(2024,10), g(2024,12)/g(2024,10)) if c!='RT70' else (1.0,1.0)
out={}
for c in CL:
    a26=[A['2026-%02d'%m][c] for m in range(1,11)]; s=shape(c); a26+=[a26[9]*s[0], a26[9]*s[1]]
    out[c]=dict(fy25=sum(A['2025-%02d'%m][c] for m in range(1,13)), fy26=sum(a26), fy27=sum(f[c]), h1=sum(f[c][:6])-sum(a26[:6]), h2=sum(f[c][6:])-sum(a26[6:]))
json.dump(out,open('_fy27_byclass.json','w')); print({c:round(out[c]['fy27'],1) for c in CL}, round(sum(out[c]['fy27'] for c in CL),1))
