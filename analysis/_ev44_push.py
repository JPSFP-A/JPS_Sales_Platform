# -*- coding: utf-8 -*-
# Push the EV44 backfill month by month. A month is pushed only if the rebuilt RT10 buckets differ from the database by the EV44 kWh and nothing else.
import io, json, re, subprocess, sys, requests, truststore
truststore.inject_into_ssl()
HERE = r'C:\Projects\Sales_Platform\analysis'
env = {}
for l in io.open(HERE + r'\.env', encoding='utf-8'):
    if '=' in l and not l.startswith('#'): k, v = l.strip().split('=', 1); env[k] = v.strip('"')
H = {'apikey': env['SUPABASE_SERVICE_ROLE_KEY'], 'Authorization': 'Bearer ' + env['SUPABASE_SERVICE_ROLE_KEY']}
months = open(HERE + r'\_ev44_months.txt').read().split()
ev = {(r[0], r[1]): r[4] for r in json.load(open(HERE + r'\_driver_res_evidence.json'))['ev']}
def dbtot(y, m):
    r = requests.get(env['SUPABASE_URL'] + '/rest/v1/jps_actuals', headers=H, params={'year': 'eq.%d' % y, 'month': 'eq.%d' % m, 'rate_class': 'eq.RT10', 'select': 'consumption_bucket,kwh'}, timeout=120); r.raise_for_status()
    return sum(x['kwh'] or 0 for x in r.json() if x['consumption_bucket'] != 'Prepaid')
def run(mo, dry):
    a = [sys.executable, '_push_rt10_buckets.py', mo, '--verify', '2026-10'] + (['--dry-run'] if dry else [])
    p = subprocess.run(a, cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace', env={**__import__('os').environ, 'PYTHONIOENCODING': 'utf-8'})
    return p.stdout + p.stderr
res = []
for mo in months:
    y, m = int(mo[:4]), int(mo[5:])
    o = run(mo, True)
    g = re.search(re.escape(mo) + r': 8 buckets, ([\d.]+) GWh', o)
    if not g: print(mo, 'DRY RUN FAILED', o[-300:].replace('\n', ' | ')); res.append((mo, 'dry run failed')); continue
    new = float(g.group(1)) * 1e6; old = dbtot(y, m); delta = new - old; exp = ev[(y, m)]
    ok = abs(delta - exp) <= 500
    print(mo, 'db %.3f new %.3f delta %.1f kWh, EV44 %.1f kWh' % (old / 1e6, new / 1e6, delta, exp), 'OK' if ok else 'MISMATCH', flush=True)
    if ok:
        o2 = run(mo, False); print('   ', 'pushed' if 'pushed 8 rows' in o2 else 'PUSH FAILED ' + o2[-200:].replace('\n', ' | '), flush=True); res.append((mo, 'pushed' if 'pushed 8 rows' in o2 else 'failed'))
    else: res.append((mo, 'skipped: mismatch'))
json.dump(res, open(HERE + r'\_ev44_push_result.json', 'w'))
