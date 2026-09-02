# -*- coding: utf-8 -*-
"""Push RT10's eight consumption-bucket rows for a month into jps_actuals.

RT10 mass-market volume is held as one row per bucket at parish='ALL' (RT20's
equivalent rows are per-parish and come from rt20_split.py instead). Nothing in
this folder built those rows -- they were loaded by hand -- so a new month had no
route in. This is that route.

Two sources, because neither is sufficient alone:

  corrected.json   50 kWh-wide bins per month, from the raw billing export. Gives
                   every tier's kWh, revenue and customer count. Its bin 0 spans
                   [0,50), so it cannot separate a true zero-consumption account
                   from one that used 30 kWh.
  rt10_zero_fix_result.json
                   the exact-zero-aware rescan of the same export, which splits
                   that first bin into Zero (kwh==0 exactly) and the rest of <150.

Components (fuel/energy/ipp/customer charge/demand/GCT) are written as zero, which
is what every RT10 bucket row already in the table carries -- this grain has never
held a component split.

Before pushing anything, the month named by --verify (default: the month before the
target) is rebuilt from these same two files and compared against what is already in
jps_actuals. A mapping error would reproduce silently in the new month and look
plausible, so the run aborts unless the check month reconciles exactly.

    python _push_rt10_buckets.py 2026-08
    python _push_rt10_buckets.py 2026-08 --dry-run
    python _push_rt10_buckets.py 2026-08 --verify 2026-06
"""
import io, json, os, sys, time, requests

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

URL = 'https://bhrswnbenkvflpdjhfpa.supabase.co/rest/v1/jps_actuals'
CONFLICT = 'year,month,jps_ac,rate_class,parish,consumption_bucket'
KEYS = ['jps_ac', 'year', 'month', 'rate_class', 'name', 'consumption_bucket', 'parish', 'kwh',
        'revenue_jmd', 'demand_jmd', 'fuel_jmd', 'energy_jmd', 'ipp_jmd', 'customer_charge_jmd',
        'gct_jmd', 'customer_count', 'segment']

# Bin lower bound -> tier. binof() in corrected_scan.py floors to 50 kWh and uses -1
# for anything negative, so a tier is a contiguous run of those bins.
TIERS = [('<Zero', lambda b: b < 0),
         ('<150', lambda b: 0 <= b < 150),
         ('150>350', lambda b: 150 <= b < 350),
         ('350>550', lambda b: 350 <= b < 550),
         ('550>750', lambda b: 550 <= b < 750),
         ('750>950', lambda b: 750 <= b < 950),
         ('over 950', lambda b: b >= 950)]


def secret():
    return io.open(r'C:\Projects\DataManager\.env', encoding='utf-8').read().split('=', 1)[1].strip()


def build(mo, M, Z):
    """Return {bucket: (kwh, revenue, customer_count)} for month 'YYYY-MM'."""
    bins = M['bucket'].get(mo, {}).get('RT10')
    if not bins:
        raise SystemExit('corrected.json has no RT10 bins for %s' % mo)
    out = {}
    for label, test in TIERS:
        sel = [v for b, v in bins.items() if test(int(b))]
        out[label] = [sum(v[1] for v in sel), sum(v[2] for v in sel), int(sum(v[0] for v in sel))]
    # Split the [0,150) tier into Zero and <150 using the exact-zero rescan. kWh is
    # untouched by definition (a true zero contributes none); the customer count and
    # revenue are what actually move.
    z = Z.get(mo)
    if not z:
        raise SystemExit('rt10_zero_fix_result.json has no %s -- run: python rt10_zero_fix.py %s' % (mo, mo))
    zcnt, zkwh, zrev = z['TrueZero'][0], z['TrueZero'][1], z['TrueZero'][2]
    ncnt, nkwh, nrev = z['<150'][0], z['<150'][1], z['<150'][2]
    combined = out['<150']
    if abs((zkwh + nkwh) - combined[0]) > 1.0 or (int(zcnt) + int(ncnt)) != combined[2]:
        raise SystemExit('%s: the zero rescan and the bin histogram disagree on [0,150) '
                         '(%.2f+%.2f vs %.2f kWh, %d+%d vs %d accounts) -- one of the two '
                         'was built from a different export'
                         % (mo, zkwh, nkwh, combined[0], int(zcnt), int(ncnt), combined[2]))
    out['Zero'] = [zkwh, zrev, int(zcnt)]
    out['<150'] = [nkwh, nrev, int(ncnt)]
    return out


def rows_for(mo, built):
    Y, Mo = int(mo[:4]), int(mo[5:7])
    rows = []
    for bucket, (kwh, rev, cnt) in sorted(built.items()):
        rows.append({'jps_ac': '', 'year': Y, 'month': Mo, 'rate_class': 'RT10', 'name': None,
                     'consumption_bucket': bucket, 'parish': 'ALL', 'kwh': kwh, 'revenue_jmd': rev,
                     'demand_jmd': 0.0, 'fuel_jmd': 0.0, 'energy_jmd': 0.0, 'ipp_jmd': 0.0,
                     'customer_charge_jmd': 0.0, 'gct_jmd': 0.0, 'customer_count': cnt,
                     'segment': 'Residential'})
    for r in rows:
        assert set(r.keys()) == set(KEYS)
    return rows


def fetch_live(mo, key):
    Y, Mo = int(mo[:4]), int(mo[5:7])
    r = requests.get(URL, headers={'apikey': key, 'Authorization': 'Bearer ' + key},
                     params={'year': 'eq.%d' % Y, 'month': 'eq.%d' % Mo, 'rate_class': 'eq.RT10',
                             'parish': 'eq.ALL',
                             'select': 'consumption_bucket,kwh,revenue_jmd,customer_count'},
                     timeout=60)
    r.raise_for_status()
    return {x['consumption_bucket']: (float(x['kwh']), float(x['revenue_jmd']), int(x['customer_count']))
            for x in r.json()}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        raise SystemExit(__doc__)
    target = args[0]
    dry = '--dry-run' in sys.argv
    if '--verify' in sys.argv:
        check = sys.argv[sys.argv.index('--verify') + 1]
    else:
        y, m = int(target[:4]), int(target[5:7])
        check = '%04d-%02d' % (y - 1, 12) if m == 1 else '%04d-%02d' % (y, m - 1)

    M = json.load(open('corrected.json'))
    Z = json.load(open('rt10_zero_fix_result.json'))
    key = secret()

    # --- gate: rebuild the check month and reconcile it against the live table ---
    print('verifying %s against jps_actuals before touching %s' % (check, target))
    live = fetch_live(check, key)
    if not live:
        raise SystemExit('no RT10 parish=ALL rows in jps_actuals for %s -- nothing to verify '
                         'against; pass --verify <month> naming a month that is already loaded' % check)
    rebuilt = build(check, M, Z)
    bad = []
    for bucket in sorted(set(list(live) + list(rebuilt))):
        if bucket not in live or bucket not in rebuilt:
            bad.append('  %-9s present in %s only' % (bucket, 'jps_actuals' if bucket in live else 'the rebuild'))
            continue
        lk, lr, lc = live[bucket]
        bk, br, bc = rebuilt[bucket]
        ok = abs(lk - bk) <= 0.5 and abs(lr - br) <= 0.5 and lc == bc
        print('  %-9s %14.2f kWh %16.2f rev %8d cust   %s'
              % (bucket, bk, br, bc, 'ok' if ok else 'MISMATCH'))
        if not ok:
            bad.append('  %-9s rebuilt %.2f/%.2f/%d vs live %.2f/%.2f/%d'
                       % (bucket, bk, br, bc, lk, lr, lc))
    if bad:
        print('\n%s does not reproduce. Refusing to push %s:' % (check, target))
        for b in bad:
            print(b)
        raise SystemExit(1)
    print('  %s reconciles exactly\n' % check)

    # --- build and push the target ---
    built = build(target, M, Z)
    rows = rows_for(target, built)
    tot = sum(v[0] for v in built.values())
    print('%s: %d buckets, %.3f GWh, %d accounts' % (target, len(rows), tot / 1e6,
                                                     sum(v[2] for v in built.values())))
    for bucket, (kwh, rev, cnt) in sorted(built.items()):
        print('  %-9s %14.2f kWh %16.2f rev %8d cust' % (bucket, kwh, rev, cnt))
    if dry:
        print('DRY RUN - not pushing')
        return

    hdrs = {'apikey': key, 'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json',
            'Prefer': 'resolution=merge-duplicates,return=minimal'}
    for attempt in range(5):
        resp = requests.post(URL + '?on_conflict=' + CONFLICT, headers=hdrs,
                             data=json.dumps(rows), timeout=60)
        if resp.status_code < 300:
            print('pushed %d rows' % len(rows))
            return
        print('  attempt %d: %s %s' % (attempt + 1, resp.status_code, resp.text[:200]))
        time.sleep(2)
    raise SystemExit('push failed')


if __name__ == '__main__':
    main()
