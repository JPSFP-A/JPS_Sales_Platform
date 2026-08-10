# -*- coding: utf-8 -*-
# Regenerates the _res_*.json extract caches consumed by build_residential_analysis.py,
# fresh off the now-cleaned jps_actuals/jps_budget/jps_le tables.
import json, requests, time

SECRET = open(r'D:\Projects\DataManager\.env').read().split('=', 1)[1].strip()
HDRS = {'apikey': SECRET, 'Authorization': 'Bearer ' + SECRET}


def get_all(table, params, select='*'):
    URL = f'https://bhrswnbenkvflpdjhfpa.supabase.co/rest/v1/{table}'
    out = []
    page = 0
    while True:
        p = dict(params)
        p['select'] = select
        p['order'] = 'id.asc'
        p['limit'] = 1000
        p['offset'] = page * 1000
        r = None
        for attempt in range(5):
            try:
                r = requests.get(URL, headers=HDRS, params=p, timeout=60)
                if r.status_code < 300:
                    break
            except Exception:
                pass
            time.sleep(2)
        rows = r.json()
        out.extend(rows)
        if len(rows) < 1000:
            break
        page += 1
    return out


# 1. Prepaid population (RT10 + RT20), May-Jul 2026 AND May-Jul 2025 (for YoY) --
#    full history now backfilled to Jan 2025 in jps_actuals; this cache stays scoped
#    to the residential workbook's 3-month CY window + matching PY window
prepaid = get_all('jps_actuals', {
    'rate_class': 'in.(RT10,RT20)',
    'consumption_bucket': 'eq.Prepaid',
    'year': 'in.(2025,2026)',
    'month': 'in.(5,6,7)',
})
json.dump(prepaid, open('_res_prepaid.json', 'w'))
print('prepaid:', len(prepaid))

# 2. Real RT20 premise population, May/Jun/Jul 2026, all consumption_bucket != 'Prepaid'
rt20_real = get_all('jps_actuals', {
    'rate_class': 'eq.RT20',
    'consumption_bucket': 'neq.Prepaid',
    'year': 'eq.2026',
    'month': 'in.(5,6,7)',
})
json.dump(rt20_real, open('_res_rt20_real.json', 'w'))
print('rt20_real:', len(rt20_real))

# 3. RT20 budget, May/Jun/Jul 2026
rt20_budget = get_all('jps_budget', {
    'rate_class': 'eq.RT20',
    'year': 'eq.2026',
    'month': 'in.(5,6,7)',
})
json.dump(rt20_budget, open('_res_jps_budget.json', 'w'))
print('rt20_budget:', len(rt20_budget))

# 4. RT20 LE, May/Jun/Jul 2026
rt20_le = get_all('jps_le', {
    'rate_class': 'eq.RT20',
    'year': 'eq.2026',
    'month': 'in.(5,6,7)',
})
json.dump(rt20_le, open('_res_jps_le.json', 'w'))
print('rt20_le:', len(rt20_le))

# 5. Unassigned-tariff PAYG population, Jul 2026 (no rate class tag in the CIS extract)
unassigned_payg = get_all('jps_actuals', {
    'rate_class': 'eq.UNASSIGNED-PAYG',
    'year': 'eq.2026',
    'month': 'eq.7',
})
json.dump(unassigned_payg, open('_res_unassigned_payg.json', 'w'))
print('unassigned_payg:', len(unassigned_payg))

print('CACHE REGEN DONE')
