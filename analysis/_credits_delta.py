# -*- coding: utf-8 -*-
# October 2026: add the billing rows flagged cust_billed = 0 that carry kWh (credits and adjustments) so the platform ties to the earnings sheet.
# PR / PC prepaid-tagged rows stay out (those premises sit in the prepaid data) and EV44 is already in. Applied once and logged so it can be reversed.
import csv, io, json, os, sys, requests, truststore
truststore.inject_into_ssl(); csv.field_size_limit(10 ** 9)
HERE = r'C:\Projects\Sales_Platform\analysis'; DL = r'C:\Users\jwilson\Downloads'
env = {}
for l in io.open(HERE + r'\.env', encoding='utf-8'):
    if '=' in l and not l.startswith('#'): k, v = l.strip().split('=', 1); env[k] = v.strip('"')
BASE = env['SUPABASE_URL'] + '/rest/v1/jps_actuals'
H = {'apikey': env['SUPABASE_SERVICE_ROLE_KEY'], 'Authorization': 'Bearer ' + env['SUPABASE_SERVICE_ROLE_KEY'], 'Content-Type': 'application/json'}
LOG = HERE + r'\_credits_delta_log.json'
if os.path.exists(LOG): raise SystemExit('already applied: see ' + LOG)
norm = lambda s: str(s).strip().upper(); num = lambda s: float(s) if s not in ('', None) else 0.0
RM = {}; RC = {}
for r in list(csv.reader(open(DL + r'\Rate categorry Data mapping.csv', encoding='utf-8-sig')))[1:]:
    if len(r) >= 3: RM[norm(r[2])] = r[0]; RC.setdefault(norm(r[1]), r[0])
PM = {norm(r[0]): r[1] for r in list(csv.reader(open(DL + r'\Parish Grouping.csv', encoding='utf-8-sig')))[1:] if len(r) >= 2}
def title(rc, s):
    s = norm(s)
    if s == 'EV44': return 'RT10'
    if s == 'RT76': return 'RT70'
    return RC.get(norm(rc)) or RM.get(s)
def bucket(k):
    if k < 0: return '<Zero'
    if k == 0: return 'Zero'
    if k < 150: return '<150'
    if k < 350: return '150>350'
    if k < 550: return '350>550'
    if k < 750: return '550>750'
    if k <= 950: return '750>950'
    return 'over 950'
rows = []
rd = csv.reader(io.open(HERE + r'\Oct 26.csv', encoding='utf-8', errors='replace')); h = next(rd); ix = {n: i for i, n in enumerate(h)}
for r in rd:
    if len(r) < 40: continue
    if r[ix['cust_billed']] == '1' or norm(r[ix['Srat_Code']]) == 'EV44' or r[ix['rate_class']] in ('PR', 'PC'): continue
    k = num(r[ix['net_kwh_billed_consump']])
    if k == 0: continue
    t = title(r[ix['rate_class']], r[ix['Srat_Code']])
    if t not in ('RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70'): continue
    g = lambda n: num(r[ix[n]])
    rows.append(dict(cls=t, ac=r[ix['Cust_Code']].replace(',', '') + '-' + r[ix['Prem_Code']], name=r[ix['Name']].strip(), parish=PM.get(norm(r[ix['Parish']]), 'UNMAPPED'), kwh=k, rev=g('net_revenue'),
                     dem=g('KVAP_KVA_Demand') + g('KVAL_Demand') + g('KVAO_Demand'), en=g('KWHP_KWH_Energy') + g('KWHL_Energy') + g('KWHO_Energy'), fuel=g('fuel') + g('FuelOffPeak') + g('FuelPartialPeak') + g('FuelOnPeak'), ipp=g('IPP_Charge'), cc=g('Cust_Charge')))
print(len(rows), 'rows;', {c: round(sum(x['kwh'] for x in rows if x['cls'] == c) / 1e3, 1) for c in ('RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70')}, 'MWh')
if 'UNMAPPED' in {x['parish'] for x in rows}: print('unmapped parishes:', {x['ac'] for x in rows if x['parish'] == 'UNMAPPED'})
if '--dry' in sys.argv: raise SystemExit('dry run: nothing written')
log = {'rt10': [], 'insert': [], 'update': []}
def get(params): r = requests.get(BASE, headers=H, params={'year': 'eq.2026', 'month': 'eq.10', **params}, timeout=120); r.raise_for_status(); return r.json()
# ---- RT10 buckets (parish ALL) ----
R10 = {x['consumption_bucket']: x for x in get({'rate_class': 'eq.RT10', 'parish': 'eq.ALL', 'select': 'id,consumption_bucket,kwh,revenue_jmd,customer_count'}) if x['consumption_bucket'] != 'Prepaid'}
agg = {}
for x in rows:
    if x['cls'] != 'RT10': continue
    a = agg.setdefault(bucket(x['kwh']), [0, 0.0, 0.0]); a[0] += 1; a[1] += x['kwh']; a[2] += x['rev']
for b, (n, k, rv) in agg.items():
    x = R10[b]; body = {'kwh': round((x['kwh'] or 0) + k, 2), 'revenue_jmd': round((x['revenue_jmd'] or 0) + rv, 2), 'customer_count': (x['customer_count'] or 0) + n}
    requests.patch(BASE, headers={**H, 'Prefer': 'return=minimal'}, params={'id': 'eq.%d' % x['id']}, data=json.dumps(body), timeout=120).raise_for_status()
    log['rt10'].append({'id': x['id'], 'bucket': b, 'before': {k_: x[k_] for k_ in ('kwh', 'revenue_jmd', 'customer_count')}, 'add': {'kwh': k, 'revenue_jmd': rv, 'customer_count': n}})
# ---- account rows (RT20 to RT70) ----
acc = {}
for x in rows:
    if x['cls'] == 'RT10': continue
    a = acc.setdefault((x['cls'], x['ac']), dict(x, kwh=0.0, rev=0.0, dem=0.0, en=0.0, fuel=0.0, ipp=0.0, cc=0.0))
    for f in ('kwh', 'rev', 'dem', 'en', 'fuel', 'ipp', 'cc'): a[f] += x[f]
for (c, ac), a in acc.items():
    ex = get({'rate_class': 'eq.' + c, 'jps_ac': 'eq.' + ac, 'select': '*'})
    if ex:
        x = ex[0]
        body = {'kwh': round((x['kwh'] or 0) + a['kwh'], 2), 'revenue_jmd': round((x['revenue_jmd'] or 0) + a['rev'], 2), 'demand_jmd': round((x['demand_jmd'] or 0) + a['dem'], 2), 'fuel_jmd': round((x['fuel_jmd'] or 0) + a['fuel'], 2),
                'energy_jmd': round((x['energy_jmd'] or 0) + a['en'], 2), 'ipp_jmd': round((x['ipp_jmd'] or 0) + a['ipp'], 2), 'customer_charge_jmd': round((x['customer_charge_jmd'] or 0) + a['cc'], 2)}
        requests.patch(BASE, headers={**H, 'Prefer': 'return=minimal'}, params={'id': 'eq.%d' % x['id']}, data=json.dumps(body), timeout=120).raise_for_status()
        log['update'].append({'id': x['id'], 'ac': ac, 'cls': c, 'before': {k_: x.get(k_) for k_ in body}})
    else:
        body = {'year': 2026, 'month': 10, 'jps_ac': ac, 'name': a['name'], 'rate_class': c, 'parish': a['parish'], 'consumption_bucket': 'Commercial', 'kwh': round(a['kwh'], 2), 'revenue_jmd': round(a['rev'], 2),
                'demand_jmd': round(a['dem'], 2), 'fuel_jmd': round(a['fuel'], 2), 'energy_jmd': round(a['en'], 2), 'ipp_jmd': round(a['ipp'], 2), 'customer_charge_jmd': round(a['cc'], 2), 'customer_count': 1, 'segment': 'Commercial' if c == 'RT20' else ''}
        p = requests.post(BASE, headers={**H, 'Prefer': 'return=representation'}, data=json.dumps(body), timeout=120); p.raise_for_status()
        log['insert'].append({'id': p.json()[0]['id'], 'ac': ac, 'cls': c, 'kwh': a['kwh']})
json.dump(log, open(LOG, 'w')); print('applied: RT10 buckets', len(log['rt10']), '| accounts updated', len(log['update']), 'inserted', len(log['insert']))
