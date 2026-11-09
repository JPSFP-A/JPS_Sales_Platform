import io, time, requests, truststore, pandas as pd
truststore.inject_into_ssl()
HERE = r'C:\Projects\Sales_Platform\analysis'
env = {}
for l in io.open(HERE + r'\.env', encoding='utf-8'):
    if '=' in l and not l.startswith('#'): k, v = l.strip().split('=', 1); env[k] = v.strip('"')
H = {'apikey': env['SUPABASE_SERVICE_ROLE_KEY'], 'Authorization': 'Bearer ' + env['SUPABASE_SERVICE_ROLE_KEY']}
rows = []; off = 0
while True:
    for t in range(40):
        try:
            r = requests.get(env['SUPABASE_URL'] + '/rest/v1/jps_actuals', headers={**H, 'Range-Unit': 'items', 'Range': '%d-%d' % (off, off + 999)},
                             params={'year': 'eq.2026', 'month': 'eq.10', 'select': 'year,month,jps_ac,name,rate_class,parish,kwh'}, timeout=120)
            r.raise_for_status(); break
        except Exception as e:
            print('retry', off, str(e)[:60], flush=True); time.sleep(15)
    else: raise SystemExit('gave up')
    d = r.json(); rows += d
    if len(d) < 1000: break
    off += 1000
pd.DataFrame(rows).to_pickle('oct26_rows.pkl'); print('saved', len(rows))
