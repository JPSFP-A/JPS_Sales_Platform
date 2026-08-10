# -*- coding: utf-8 -*-
# Rebuilds _pdf_company_totals.json and _pdf_parish.json to include ALL
# consumption_bucket types (Commercial, the residential tier buckets, Prepaid,
# and UNASSIGNED-PAYG) -- both caches had been silently excluding Prepaid
# entirely (traced: their totals matched a postpaid-only baseline exactly).
#
# _pdf_movers.json is NOT rebuilt here -- it's inherently account-level
# (individual jps_ac movers Jun->Jul), and Prepaid has no per-account identity
# in jps_actuals (parish-aggregated only, jps_ac=''), so it structurally cannot
# be included in an account-level movers list. That's a real data-grain limit,
# not a bug to fix by re-aggregating.
import json, requests

SECRET = open(r'D:\Projects\DataManager\.env').read().split('=', 1)[1].strip()
REST_HDRS = {'apikey': SECRET, 'Authorization': 'Bearer ' + SECRET}
REST_URL = 'https://bhrswnbenkvflpdjhfpa.supabase.co/rest/v1'


def get_all(table, params, select='*'):
    out = []
    page = 0
    while True:
        p = dict(params)
        p['select'] = select
        p['limit'] = 1000
        p['offset'] = page * 1000
        p['order'] = 'id.asc'
        r = requests.get(f'{REST_URL}/{table}', headers=REST_HDRS, params=p, timeout=60)
        rows = r.json()
        out.extend(rows)
        if len(rows) < 1000:
            break
        page += 1
    return out


LEGEND = ['count', 'kwh', 'rev', 'kvap', 'kval', 'kvao', 'kva', 'energy', 'fuel', 'ipp', 'cust', 'rev_adj', 'net_bill_adj']


def agg_row(rows):
    v = [0.0] * len(LEGEND)
    v[0] = len(rows)  # count = row count (matches this cache's prior convention)
    v[1] = sum(r['kwh'] or 0 for r in rows)
    v[2] = sum(r['revenue_jmd'] or 0 for r in rows)
    v[3] = sum(r['demand_jmd'] or 0 for r in rows)  # kvap -- jps_actuals doesn't split kvap/kval/kvao, put total in kvap
    v[7] = sum(r['energy_jmd'] or 0 for r in rows)
    v[8] = sum(r['fuel_jmd'] or 0 for r in rows)
    v[9] = sum(r['ipp_jmd'] or 0 for r in rows)
    v[10] = sum(r['customer_charge_jmd'] or 0 for r in rows)
    return v


# EXCLUDED: 'Postpaid' (RT40/RT50) and 'Streetlight' (RT60-ST) -- found while
# building this cache: legacy aggregate tags that coexist with the correct
# per-premise 'Commercial' population for the SAME months (Jan 2025-Apr 2026),
# the exact RT10/RT20 legacy/new duplication pattern already fixed earlier this
# session, but never checked/cleaned for these three classes. Including them
# here would double-count real revenue on top of 'Commercial'. Excluding until
# they get the same verify-then-delete treatment RT10/RT20 got -- see summary.
print('fetching Jun/Jul 2026 + Jul 2025, all consumption buckets except unverified legacy tags...', flush=True)
rows = get_all('jps_actuals',
                {'year': 'in.(2025,2026)', 'or': '(and(year.eq.2026,month.in.(6,7)),and(year.eq.2025,month.eq.7))',
                 'consumption_bucket': 'not.in.(Postpaid,Streetlight)'},
                select='year,month,rate_class,kwh,revenue_jmd,demand_jmd,energy_jmd,fuel_jmd,ipp_jmd,customer_charge_jmd')
print('rows:', len(rows), flush=True)

jun26 = [r for r in rows if r['year'] == 2026 and r['month'] == 6]
jul26 = [r for r in rows if r['year'] == 2026 and r['month'] == 7]
jul25 = [r for r in rows if r['year'] == 2025 and r['month'] == 7]

comp = {
    'legend': LEGEND,
    'jun': agg_row(jun26),
    'jul': agg_row(jul26),
    'jul25': agg_row(jul25),
    'jun_by_title': {},
    'jul_by_title': {},
}
for title in sorted(set(r['rate_class'] for r in jun26)):
    comp['jun_by_title'][title] = agg_row([r for r in jun26 if r['rate_class'] == title])
for title in sorted(set(r['rate_class'] for r in jul26)):
    comp['jul_by_title'][title] = agg_row([r for r in jul26 if r['rate_class'] == title])

json.dump(comp, open('_pdf_company_totals.json', 'w'))
print('jun rev:', comp['jun'][2], 'jul rev:', comp['jul'][2], 'jul25 rev:', comp['jul25'][2])
print('WROTE _pdf_company_totals.json (now includes Prepaid + UNASSIGNED-PAYG)')

print('fetching parish-level Jun/Jul revenue, all consumption buckets...', flush=True)
prows = get_all('jps_actuals', {'year': 'eq.2026', 'month': 'in.(6,7)'}, select='year,month,parish,revenue_jmd')
by_parish = {}
for r in prows:
    p = r['parish'] or 'UNMAPPED'
    d = by_parish.setdefault(p, {'jun_rev': 0.0, 'jul_rev': 0.0})
    key = 'jun_rev' if r['month'] == 6 else 'jul_rev'
    d[key] += r['revenue_jmd'] or 0

parish_list = []
for p, d in by_parish.items():
    parish_list.append({'parish': p, 'jun_rev': d['jun_rev'], 'jul_rev': d['jul_rev'], 'd_rev': d['jul_rev'] - d['jun_rev']})
parish_list.sort(key=lambda x: -x['d_rev'])

json.dump(parish_list, open('_pdf_parish.json', 'w'))
print('sum jul_rev:', sum(p['jul_rev'] for p in parish_list))
print('WROTE _pdf_parish.json (now includes Prepaid parish revenue)')
