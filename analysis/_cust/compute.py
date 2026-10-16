# -*- coding: utf-8 -*-
import json, collections
import engine as e
D, Y = e.D, e.Y
c = json.load(open('../corrected.json', encoding='utf-8'))
KVA = {}      # code -> {month: kva}
for v in c['acct'].values():
    KVA.setdefault(v['code'], {})
    for mo, arr in v['m'].items():
        if mo.startswith('2026-'):
            KVA[v['code']][int(mo[5:])] = KVA[v['code']].get(int(mo[5:]), 0) + (arr[5] or 0)

RATE = collections.defaultdict(float)
for r in D['rate']:
    if r['year'] == Y: RATE[(r['rate_class'], int(r['month']))] += float(r['rate_jmd_per_kwh'] or 0)

acts = collections.defaultdict(dict); rev = collections.defaultdict(float); meta = {}; metaym = {}
cohort_act = collections.defaultdict(dict); cohort_rows = {}
for r in D['act']:
    ac = r['jps_ac']; ym = (r['year'], r['month']); k = float(r['kwh'] or 0)
    if ac and ac not in e.PLACE:
        acts[ac][ym] = acts[ac].get(ym, 0) + k
        if r['year'] == Y: rev[ac] += float(r['revenue_jmd'] or 0)
        if ac not in metaym or ym >= metaym[ac]:
            metaym[ac] = ym; meta[ac] = r
    else:
        ck = (r['rate_class'], r['parish'], r['consumption_bucket'])
        cohort_act[ck][ym] = cohort_act[ck].get(ym, 0) + k
        cohort_rows.setdefault(ck, {'rev': 0.0})
        if r['year'] == Y: cohort_rows[ck]['rev'] += float(r['revenue_jmd'] or 0)

newc = {n['jps_ac']: n for n in D['newc'] if int(n['start_year']) <= Y and n['rate_class'] != 'EV'}
rows = []; skipped_2025only = []
for ac, m_ in meta.items():
    has26 = any(y == Y and abs(v) > 0 for (y, m), v in acts[ac].items())
    if not has26:
        skipped_2025only.append(ac); continue
    rc = m_['rate_class']; kam = e.kl(e.kamMap, ac); ind = e.kl(e.indMap, ac)
    ch = e.chain(acts[ac], rc, ind, ac)
    rows.append(dict(ac=ac, name=m_['name'] or ac, rc=rc, parish=m_['parish'], industry=ind, managed=bool(kam), kam=kam or e.KAMUSER, kind='Account', ch=ch, rev_ytd=rev[ac]))
for ac, n in newc.items():
    rc = n['rate_class']; kam = n.get('kam') or ''; ind = n.get('industry') or ''
    ch = e.chain({}, rc, ind, ac, dict(sy=int(n['start_year']), sm=int(n['start_month']), kwh=float(n['expected_kwh'] or 0)))
    rows.append(dict(ac=ac, name=n['name'], rc=rc, parish=n.get('parish') or '', industry=ind, managed=bool(kam), kam=kam or e.KAMUSER, kind='New customer (pipeline)', ch=ch, rev_ytd=0.0))
for ck, a in cohort_act.items():
    rc, parish, bucket = ck
    ch = e.chain(a, rc, None, None)
    rows.append(dict(ac=f'{rc}|{parish}|{bucket}', name=f'{rc} bulk-billed, no individual account ({parish}, {bucket})', rc=rc, parish=parish, industry='', managed=False, kam=e.KAMUSER, kind='Bulk (no account)', ch=ch, rev_ytd=cohort_rows[ck]['rev']))

# kVA + revenue
for r in rows:
    k = KVA.get(r['ac'], {}); r['has_kva'] = r['ac'] in KVA
    kv = {m: float(k.get(m, 0)) for m in range(1, 10)}
    for m in range(10, 13):
        ch = r['ch'][m]; f = (ch['total'] / ch['base']) if ch['base'] > 0 else (1.0 if ch['base'] == 0 else 1.0)
        f = max(f, 0.0) if ch['base'] > 0 else 1.0
        terms = [kv[m - j] for j in (1, 2, 3)]
        kv[m] = (sum(terms) / 3) * f if r['has_kva'] else 0.0
    r['kva'] = kv
    r['rev_fc'] = {m: r['ch'][m]['total'] * RATE[(r['rc'], m)] for m in range(10, 13)}

# platform-as-is: KAM accounts at account level, non-KAM + bulk at cohort level (industry None)
asis = collections.defaultdict(lambda: collections.defaultdict(float))
coh = collections.defaultdict(lambda: collections.defaultdict(float))
for ac, m_ in meta.items():
    if not any(y == Y and abs(v) > 0 for (y, m), v in acts[ac].items()) and not any(y == Y - 1 for (y, m) in acts[ac]): continue
for r in rows:
    if r['kind'] == 'New customer (pipeline)' or r['managed']:
        for m in range(10, 13): asis[r['rc']][m] += r['ch'][m]['total']
# cohorts for non-KAM: key from each ROW (rate_class|parish|bucket)
cohort_nonkam = collections.defaultdict(lambda: collections.defaultdict(float))
for r_ in D['act']:
    ac = r_['jps_ac']; ym = (r_['year'], r_['month'])
    if ac and ac not in e.PLACE and e.kl(e.kamMap, ac): continue
    cohort_nonkam[(r_['rate_class'], r_['parish'], r_['consumption_bucket'])][ym] = cohort_nonkam[(r_['rate_class'], r_['parish'], r_['consumption_bucket'])].get(ym, 0) + float(r_['kwh'] or 0)
for ck, a in cohort_nonkam.items():
    ch = e.chain(a, ck[0], None, None)
    for m in range(10, 13): asis[ck[0]][m] += ch[m]['total']
if __name__ == '__main__':
    print('rows', len(rows), collections.Counter((r['kind'], r['managed']) for r in rows), 'skipped (no 2026 billing)', len(skipped_2025only))
    tot = collections.defaultdict(float); ytd = collections.defaultdict(float)
    for r in rows:
        for m in range(1, 10): ytd[r['rc']] += r['ch'][m]['total']
        for m in range(10, 13): tot[r['rc']] += r['ch'][m]['total']
    print('class: YTD GWh | Q4 dump GWh | Q4 platform-as-is GWh | diff MWh')
    for rc in sorted(ytd):
        a = sum(asis[rc].values())
        print(rc, round(ytd[rc] / 1e6, 3), round(tot[rc] / 1e6, 3), round(a / 1e6, 3), round((tot[rc] - a) / 1e3, 1))
    print('TOTAL', round(sum(ytd.values()) / 1e6, 3), round(sum(tot.values()) / 1e6, 3), round(sum(sum(v.values()) for v in asis.values()) / 1e6, 3))
    sep = sum(r['ch'][9]['total'] for r in rows); print('Sep commercial GWh', round(sep / 1e6, 3))
    print('rev YTD J$bn', round(sum(r['rev_ytd'] for r in rows) / 1e9, 3), 'rev Q4 J$bn', round(sum(sum(r['rev_fc'].values()) for r in rows) / 1e9, 3))
    print('kva Sep sum', round(sum(r['kva'][9] for r in rows)), 'Q4 kva avg', round(sum(sum(r['kva'][m] for r in rows) for m in (10, 11, 12)) / 3))
    print('accounts with kva', sum(r['has_kva'] for r in rows), 'RT40+ accounts', sum(1 for r in rows if r['rc'] != 'RT20' and r['kind'] == 'Account'))
