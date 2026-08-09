# -*- coding: utf-8 -*-
# Fixed version: orphans must be identified by (jps_ac, parish) pair, not jps_ac alone.
# parish is part of the unique conflict key (year,month,jps_ac,rate_class,parish,consumption_bucket),
# so a stale pre-fix row with a different parish for the same account survives the upsert untouched.
import json, requests, glob, time
from collections import defaultdict

SECRET = open(r'D:\Projects\DataManager\.env').read().split('=', 1)[1].strip()
URL = 'https://bhrswnbenkvflpdjhfpa.supabase.co/rest/v1/jps_actuals'
HDRS = {'apikey': SECRET, 'Authorization': 'Bearer ' + SECRET, 'Content-Type': 'application/json'}


def get_all(params, select='jps_ac,parish'):
    out = []
    page = 0
    while True:
        p = dict(params)
        p['select'] = select
        p['order'] = 'jps_ac.asc,parish.asc'
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


def delete_by_parish(jps_acs_by_parish, year, month):
    deleted = 0
    BATCH = 200
    for parish, acs in jps_acs_by_parish.items():
        for i in range(0, len(acs), BATCH):
            chunk = acs[i:i + BATCH]
            vals = ','.join(f'"{v}"' for v in chunk)
            params = {
                'rate_class': 'eq.RT20',
                'consumption_bucket': 'eq.Commercial',
                'year': f'eq.{year}',
                'month': f'eq.{month}',
                'parish': f'eq.{parish}',
                'jps_ac': f'in.({vals})',
            }
            ok = False
            last = None
            for attempt in range(5):
                try:
                    r = requests.delete(URL, headers=HDRS, params=params, timeout=60)
                    if r.status_code < 300:
                        ok = True
                        break
                    last = f'{r.status_code} {r.text[:200]}'
                except Exception as e:
                    last = repr(e)
                time.sleep(2)
            if not ok:
                print('  DELETE FAILED parish=', parish, 'chunk', i, last, flush=True)
                continue
            deleted += len(chunk)
    return deleted


files = sorted(glob.glob('rt20_split_20??_??.json'))
grand_orphans = 0
for fp in files:
    d = json.load(open(fp))
    Y, M = d['year'], d['month']
    correct = set((ac, info['parish']) for ac, info in d['comm'].items())
    db_rows = get_all({'rate_class': 'eq.RT20', 'consumption_bucket': 'eq.Commercial', 'year': f'eq.{Y}', 'month': f'eq.{M}'})
    db_tuples = set((r['jps_ac'], r['parish']) for r in db_rows)
    orphans = db_tuples - correct
    missing = correct - db_tuples
    if missing:
        print(f'{Y}-{M:02d}: WARNING {len(missing)} correct (ac,parish) pairs missing from DB!', flush=True)
    if orphans:
        by_parish = defaultdict(list)
        for ac, parish in orphans:
            by_parish[parish].append(ac)
        n = delete_by_parish(by_parish, Y, M)
        grand_orphans += n
        print(f'{Y}-{M:02d}: db_rows={len(db_tuples)} correct={len(correct)} orphans_deleted={n}', flush=True)
    else:
        print(f'{Y}-{M:02d}: db_rows={len(db_tuples)} correct={len(correct)} clean, no orphans', flush=True)
print('GRAND TOTAL ORPHANS DELETED:', grand_orphans, flush=True)
print('CLEANUP2 DONE', flush=True)
