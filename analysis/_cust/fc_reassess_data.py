# -*- coding: utf-8 -*-
# Run-rate vs engine forecast, by account. Inputs: kam_run_live2.json (live engine, actuals to Sep 2026), pull.json (billed actuals 2025-26).
import json, re, collections, sys
sys.stdout.reconfigure(encoding='utf-8')
E = json.load(open('kam_run_live2.json'))
P = json.load(open('pull.json'))
act = collections.defaultdict(float)       # (ac, year, month) -> kWh
nm = {}
for r in P['act']:
    if not r.get('jps_ac'): continue
    act[(r['jps_ac'], r['year'], r['month'])] += float(r['kwh'] or 0)
    nm[r['jps_ac']] = r.get('name')
ind = {str(k['jps_ac']).strip(): k['industry'] or '' for k in P['ind']}
kam = {}
for k in P.get('kam', []):
    kam[str(k.get('jps_ac')).strip()] = k.get('kam')
rows = []
for a in E['accts']:
    ac = a['ac']; k26, k27 = a['k']['2026'], a['k']['2027']
    j = [act.get((ac, 2026, m), 0) for m in range(1, 10)]
    p25 = [act.get((ac, 2025, m), 0) for m in range(1, 13)]
    q3 = sum(j[6:9]) / 3; sep = j[8]; jun_aug = sum(j[5:8]) / 3
    q4f = sum(k26[9:12]) / 3; f27 = sum(k27); a25 = sum(p25)
    rows.append(dict(ac=ac, name=a['name'], rc=a['rc'], ind=a['ind'], kam=kam.get(ac.split('-')[0], ''), sep=sep, q3=q3, jun_aug=jun_aug, q4f=q4f, f27=f27, a25=a25, ytd26=sum(j), q4_25=sum(p25[9:12]), k26=k26, k27=k27, p25=p25, j26=j))
json.dump(rows, open('fc_reassess_rows.json', 'w'))
print('accounts', len(rows))
if __name__ == '__main__':
    pat = re.compile(sys.argv[1], re.I) if len(sys.argv) > 1 else None
    for r in rows:
        if pat and (pat.search(r['name'] or '') or pat.search(r['ac'])):
            print('%-15s %-34s %-5s Q3avg %7.0f Sep %7.0f Q4f %7.0f FY27 %9.0f FY25 %9.0f YTD26 %9.0f' % (r['ac'], (r['name'] or '')[:34], r['rc'], r['q3'] / 1e3, r['sep'] / 1e3, r['q4f'] / 1e3, r['f27'] / 1e3, r['a25'] / 1e3, r['ytd26'] / 1e3))
