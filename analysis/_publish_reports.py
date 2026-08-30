# -*- coding: utf-8 -*-
"""Publish the forecast deliverables to the private sales-reports bucket.

Runs on the service role key, which bypasses RLS. That is deliberate: the bucket
carries no insert/update/delete policy, so publishing is the only way anything
gets in or out, and no signed-in user can overwrite a published report.

Reads analysis/.env for SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY, the same file
the other push scripts use.

    python _publish_reports.py           # publish
    python _publish_reports.py --list    # show what is in the bucket
"""
import io, os, sys, json, mimetypes, requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUCKET = 'sales-reports'

# label -> filename. The label is what the app shows; keep it human.
FILES = [
    ('Executive Summary',        'JPS_Exec_Summary_FY2026-28.html'),
    ('Driver Report',            'JPS_Sales_Forecast_Driver_Report.html'),
    ('System Losses',            'JPS_System_Losses_FY2026-28.html'),
    ('Key Account Review',       'JPS_KAM_Review_FY2027.html'),
    ('Forecast Runbook',         'JPS_Forecast_Runbook.html'),
    ('Sales and Generation Workbook', 'JPS_LE_Sales_Gen_FY2026-28.xlsx'),
]


def load_env(path):
    env = {}
    if os.path.exists(path):
        for line in io.open(path, encoding='utf-8'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


env = load_env(os.path.join(HERE, '.env'))
URL = env.get('SUPABASE_URL') or os.environ.get('SUPABASE_URL')
KEY = env.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
if not URL or not KEY:
    print('Missing SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY in %s' % os.path.join(HERE, '.env'))
    sys.exit(1)
H = {'apikey': KEY, 'Authorization': 'Bearer ' + KEY}


def listing():
    r = requests.post('%s/storage/v1/object/list/%s' % (URL, BUCKET), headers=H,
                      json={'prefix': '', 'limit': 200,
                            'sortBy': {'column': 'name', 'order': 'asc'}}, timeout=60)
    r.raise_for_status()
    return r.json()


if '--list' in sys.argv:
    for o in listing():
        md = o.get('metadata') or {}
        print('  %-46s %9s bytes  %s' % (o['name'], format(md.get('size', 0), ','),
                                         (o.get('updated_at') or '')[:19]))
    sys.exit(0)

# ---- publish -------------------------------------------------------------
manifest = []
for label, fn in FILES:
    src = os.path.join(ROOT, fn)
    if not os.path.exists(src):
        print('  MISSING  %s' % fn)
        sys.exit(1)
    blob = io.open(src, 'rb').read()
    ctype = mimetypes.guess_type(fn)[0] or 'application/octet-stream'
    r = requests.post('%s/storage/v1/object/%s/%s' % (URL, BUCKET, fn),
                      headers=dict(H, **{'Content-Type': ctype, 'x-upsert': 'true'}),
                      data=blob, timeout=180)
    if r.status_code >= 300:
        print('  FAILED   %s  %s %s' % (fn, r.status_code, r.text[:300]))
        sys.exit(1)
    print('  uploaded %-46s %9s bytes' % (fn, format(len(blob), ',')))
    manifest.append({'label': label, 'file': fn, 'bytes': len(blob)})

# The manifest drives the app's list, so a new report appears without an app deploy.
mf = json.dumps({'files': manifest}, indent=1).encode('utf-8')
r = requests.post('%s/storage/v1/object/%s/manifest.json' % (URL, BUCKET),
                  headers=dict(H, **{'Content-Type': 'application/json', 'x-upsert': 'true'}),
                  data=mf, timeout=60)
r.raise_for_status()
print('  uploaded %-46s %9s bytes' % ('manifest.json', format(len(mf), ',')))
print()
print('%d files in %s' % (len(listing()), BUCKET))
