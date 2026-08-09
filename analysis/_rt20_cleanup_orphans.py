# -*- coding: utf-8 -*-
import json, requests, glob, time

SECRET = open(r'D:\Projects\DataManager\.env').read().split('=', 1)[1].strip()
URL = 'https://bhrswnbenkvflpdjhfpa.supabase.co/rest/v1/jps_actuals'
HDRS = {'apikey': SECRET, 'Authorization': 'Bearer ' + SECRET, 'Content-Type': 'application/json'}

def get_all(params, select='jps_ac'):
    out = []
    page = 0
    while True:
        p = dict(params)
        p['select'] = select
        p['order'] = 'jps_ac.asc'
        p['limit'] = 1000
        p['offset'] = page * 1000
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

def delete_batch(jps_acs, year, month):
    if not jps_acs:
        return 0
    BATCH = 200
    deleted = 0
    for i in range(0, len(jps_acs), BATCH):
        chunk = jps_acs[i:i + BATCH]
        vals = ','.join(f'"{v}"' for v in chunk)
        params = {
            'rate_class': 'eq.RT20',
            'consumption_bucket': 'eq.Commercial',
            'year': f'eq.{year}',
            'month': f'eq.{month}',
            'jps_ac': f'in.({vals})',
        }
        for attempt in range(5):
            try:
                r = requests.delete(URL, headers=HDRS, params=params, timeout=60)
                if r.status_code < 300:
                    break
                last = f'{r.status_code} {r.text[:200]}'
            except Exception as e:
                last = repr(e)
            time.sleep(2)
        else:
            print('  DELETE FAILED chunk', i, last, flush=True)
            continue
        deleted += len(chunk)
    return deleted

files = sorted(glob.glob('rt20_split_20??_??.json'))
grand_orphans = 0
for fp in files:
    d = json.load(open(fp))
    Y, M = d['year'], d['month']
    correct = set(d['comm'].keys())
    db_rows = get_all({'rate_class': 'eq.RT20', 'consumption_bucket': 'eq.Commercial', 'year': f'eq.{Y}', 'month': f'eq.{M}'})
    db_set = set(r['jps_ac'] for r in db_rows)
    orphans = sorted(db_set - correct)
    missing = sorted(correct - db_set)
    if missing:
        print(f'{Y}-{M:02d}: WARNING {len(missing)} correct accounts missing from DB!', flush=True)
    if orphans:
        n = delete_batch(orphans, Y, M)
        grand_orphans += n
        print(f'{Y}-{M:02d}: db={len(db_set)} correct={len(correct)} orphans_deleted={n}', flush=True)
    else:
        print(f'{Y}-{M:02d}: db={len(db_set)} correct={len(correct)} clean, no orphans', flush=True)
print('GRAND TOTAL ORPHANS DELETED:', grand_orphans, flush=True)
print('CLEANUP DONE', flush=True)
