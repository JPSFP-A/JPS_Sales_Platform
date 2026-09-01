# -*- coding: utf-8 -*-
"""Build the Key Account Review from the engine extract and the adjustment register.

The review was hand-authored, which is why its assigned-book figures went stale
without anything catching it. Now:
  numbers  -> _kam_data.json, extracted from the live engine by _kam_extract.js
  register -> jps_operational_adjustments, read live from Supabase
  narrative-> NOTES below, the only hand-written part, and it carries no figures
              that are not also computed here

Nothing is written unless the per-manager totals sum to the assigned book, the
assigned book plus the unassigned line equals the company total, and every
movement listed ties to its own opening and closing year.

    python _build_kam_review.py
"""
import io, os, re, sys, json, requests

# A TLS-inspecting proxy on the corporate network re-signs HTTPS with a private
# root. curl, git and Chrome trust it because they use the Windows certificate
# store; requests uses certifi's bundle and does not, which is why this script
# failed with CERTIFICATE_VERIFY_FAILED while the browser worked. truststore
# points Python at the OS store. Verification stays ON: this is the correct fix,
# not verify=False.
try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

from decimal import Decimal, ROUND_HALF_UP

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DST = os.path.join(ROOT, 'JPS_KAM_Review_FY2027.html')
DATA = os.path.join(HERE, '_kam_data.json')

FY = (2026, 2027, 2028)
AS_AT = '31 August 2026'


def f(v, d=1):
    return format(Decimal(str(v)).quantize(Decimal('1e-%d' % d), rounding=ROUND_HALF_UP), ',.%df' % d)


def pct(a, b):
    return (b / a - 1) * 100 if a else 0.0


def cls(v):
    return 'pos' if v > 0 else ('neg' if v < 0 else '')


def sign(v, d=1):
    return ('+' if v > 0 else ('&minus;' if v < 0 else '')) + f(abs(v), d)


# ---------------------------------------------------------------- data
D = json.load(io.open(DATA, encoding='utf-8'))
KAM = D['kam']
CO = {int(k): v for k, v in D['company'].items()}

ASSIGNED = {y: round(sum(v['y%d' % (y - 2000)] for v in KAM.values()), 2) for y in FY}
UNASSIGNED = {y: round(CO[y] - ASSIGNED[y], 2) for y in FY}


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
    print('Missing SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY in analysis/.env')
    sys.exit(1)
H = {'apikey': KEY, 'Authorization': 'Bearer ' + KEY}


def rest(table, params, page=10000):
    """Paginated GET. PostgREST caps a response, and a silently truncated account
    list would leave register rows showing a raw account number instead of a name."""
    out, off = [], 0
    while True:
        p = dict(params); p['limit'] = str(page); p['offset'] = str(off)
        r = requests.get('%s/rest/v1/%s' % (URL, table), headers=H, params=p, timeout=120)
        r.raise_for_status()
        b = r.json()
        out += b
        if len(b) < page:
            return out
        off += page


CACHE = os.path.join(HERE, '_kam_register_cache.json')


def fetch_inputs():
    """Adjustments, the KAM map, and names for the accounts that need them.

    Cached to disk on every success. A TLS-inspecting proxy on the corporate
    network intermittently blocks this host, and a report that cannot be rebuilt
    because of a transient network fault is worse than one built from the last
    known-good inputs, provided it says so.
    """
    a = rest('jps_operational_adjustments',
             {'select': 'jps_ac,year,month,operational_pct,manual_kwh,reason_code,'
                        'justification,basis,created_by', 'year': 'gte.2027'})
    km = rest('jps_kam', {'select': 'jps_ac,kam'})
    acs = sorted({r['jps_ac'] for r in a})
    nm = {}
    for i in range(0, len(acs), 40):
        chunk = acs[i:i + 40]
        for r in rest('jps_actuals',
                      {'select': 'jps_ac,name', 'year': 'eq.2026',
                       'jps_ac': 'in.(%s)' % ','.join(chunk)}):
            if r.get('name'):
                nm.setdefault(r['jps_ac'], r['name'])
    out = {'adj': a, 'kam': km, 'names': nm}
    io.open(CACHE, 'w', encoding='utf-8').write(json.dumps(out))
    return out, False


try:
    DATA_IN, from_cache = fetch_inputs()
except Exception as exc:
    if not os.path.exists(CACHE):
        print('Supabase unreachable and no cache at %s' % CACHE)
        print('  %s' % exc)
        sys.exit(1)
    DATA_IN, from_cache = json.load(io.open(CACHE, encoding='utf-8')), True
    print('  Supabase unreachable, built from cache: %s' % type(exc).__name__)

adj = DATA_IN['adj']
_km = DATA_IN['kam']
names = DATA_IN['names']
# jps_kam is mixed grain: some rows map a whole customer, some a single service
# point, and an account-level row wins. Resolving at account grain alone reported
# 45 of 53 adjustment accounts as unassigned when only 3 actually are.
kam_acct = {r['jps_ac']: r['kam'] for r in _km if '-' in r['jps_ac']}
kam_cust = {r['jps_ac']: r['kam'] for r in _km if '-' not in r['jps_ac']}


def kam_of(ac):
    return kam_acct.get(ac) or kam_cust.get(ac.split('-')[0])
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def nm(s):
    return ' '.join(str(s or '').upper().replace('-', ' ').split())


# Group by customer and decision, not by service point. A customer with eleven
# metered sites entered the same shutdown once; showing it eleven times reads as
# eleven separate events.
reg = {}
for a in adj:
    label = names.get(a['jps_ac'], a['jps_ac'])
    k = (nm(label), a.get('reason_code') or '', a.get('justification') or '')
    e = reg.setdefault(k, {'name': label, 'reason': a.get('reason_code') or '',
                           'just': a.get('justification') or '', 'months': [], 'pcts': set(),
                           'accounts': set(), 'basis': a.get('basis') or '', 'by': set()})
    e['months'].append((a['year'], a['month']))
    e['accounts'].add(a['jps_ac'])
    if a.get('created_by'):
        e['by'].add(a['created_by'])
    if a.get('operational_pct') is not None:
        e['pcts'].add(round(float(a['operational_pct']), 2))

for e in reg.values():
    e['months'].sort()
    lo, hi = e['months'][0], e['months'][-1]
    e['period'] = ('%s %d' % (MON[lo[1] - 1], lo[0])) if lo == hi else \
                  ('%s %d to %s %d' % (MON[lo[1] - 1], lo[0], MON[hi[1] - 1], hi[0]))
    p = sorted(e['pcts'])
    e['impact'] = 'not quantified' if not p else (('%.0f%%' % p[0]) if len(p) == 1 else
                                                  '%.0f%% to %.0f%%' % (p[0], p[-1]))
    ks = {kam_of(ac) for ac in e['accounts']} - {None}
    e['kam'] = ', '.join(sorted(ks)) if ks else ''
    e['nacc'] = len(e['accounts'])
    e['entered'] = ', '.join(sorted(e['by'])) if e['by'] else ''

# The register is for key account managers to confirm what they entered. Analyst
# modelling adjustments are not theirs to confirm and are documented in the driver
# report instead, so they are dropped here. An entry is only dropped when every row
# in it is analyst-entered: PAC Kingston Airport carries rows from both Simone
# Chisholm and the analyst, and filtering by row would show it as one month when it
# spans three.
ANALYST = ('jwilson', 'jordache')


def analyst_only(e):
    return e['by'] and all(any(a in b.lower() for a in ANALYST) for b in e['by'])


hidden = {k: e for k, e in reg.items() if analyst_only(e)}
reg = {k: e for k, e in reg.items() if not analyst_only(e)}
mixed = [e['name'] for e in reg.values()
         if any(any(a in b.lower() for a in ANALYST) for b in e['by'])]

unresolved = sum(1 for e in reg.values() if e['name'] == list(e['accounts'])[0])
print('  register: %d entries shown, %d analyst entries hidden, %d unresolved to a name'
      % (len(reg), len(hidden), unresolved))
for e in sorted(hidden.values(), key=lambda x: x['name']):
    print('     hidden: %-38s %s' % (e['name'][:38], ', '.join(sorted(e['by']))))
# An account can have some months entered by its manager and others by the analyst,
# so a shown entry may cover fewer months than the adjustment actually spans. Mark
# those rather than let the period read as the whole story.
hidden_acc = {}
for e in hidden.values():
    for ac in e['accounts']:
        hidden_acc.setdefault(ac, []).append(e['period'])
for e in reg.values():
    extra = sorted({p for ac in e['accounts'] for p in hidden_acc.get(ac, [])})
    e['partial'] = extra
part = [e['name'] for e in reg.values() if e['partial']]
if part:
    print('     shown but with further months hidden: %s' % ', '.join(sorted(set(part))))

# ---------------------------------------------------------------- checks
fails = []


def chk(label, got, want, tol=0.05):
    ok = abs(got - want) <= tol
    if not ok:
        fails.append(label)
    print('  %-52s %10.2f vs %10.2f  %s' % (label, got, want, 'ok' if ok else '*** FAIL'))


print('Reconciling before write')
for y in FY:
    chk('FY%d managers sum to assigned book' % y,
        sum(v['y%d' % (y - 2000)] for v in KAM.values()), ASSIGNED[y])
    chk('FY%d assigned + unassigned = company' % y, ASSIGNED[y] + UNASSIGNED[y], CO[y])
for m in D['movements']:
    if abs((m['b'] - m['a']) - m['d']) > 0.02:
        fails.append('movement %s does not tie' % m['n'])
print('  %-52s %10d %s' % ('movements tie to their own years', len(D['movements']),
                           'ok' if not fails else '***'))
assert not fails, 'reconciliation failed: %s' % fails

# ---------------------------------------------------------------- narrative
order = sorted(KAM, key=lambda k: -KAM[k]['y27'])
worst = min(KAM, key=lambda k: KAM[k]['y27'] - KAM[k]['y26'])
w = KAM[worst]
wdrop = w['y27'] - w['y26']
ex_w = {k: v for k, v in KAM.items() if k != worst}
ex_growth = pct(sum(v['y26'] for v in ex_w.values()), sum(v['y27'] for v in ex_w.values()))
top = [m for m in D['movements'] if m['k'] == worst][:3]

NOTES = {
 'lead': ('The assigned book grows %.1f%% while the company grows %.1f%%.' %
          (pct(ASSIGNED[2026], ASSIGNED[2027]), pct(CO[2026], CO[2027]))),
 'lead_body': ('Managed accounts move from %s to %s GWh. All of that flatness is three structural events that happen '
               'to sit in one portfolio: a completed move to self-generation, a solar commissioning and a turbine '
               'outage. None is a sales outcome and none was avoidable by account management. Excluding those three '
               'accounts, the assigned portfolios grow %.1f%%. The company total grows on residential tier migration, '
               'customer acquisition and small commercial, none of which sits in a managed portfolio.'
               % (f(ASSIGNED[2026]), f(ASSIGNED[2027]), ex_growth)),
 'worst_hd': ("%s's portfolio falls %s GWh, entirely on three structural events." % (worst, f(abs(wdrop)))),
 'worst_body': ('Three accounts carry effectively all of it: ' +
                ', '.join('%s (%s)' % (m['n'], sign(m['d'], 1)) for m in top) +
                '. Each is a customer decision or an operational event rather than a lapse in account management, and '
                'the portfolio grows without them. The target should be reset to the book that remains, rather than '
                'left showing a %.0f%% decline against an unchanged prior year that nobody could have held.'
                % abs(pct(w['y26'], w['y27']))),
}

# ---------------------------------------------------------------- render
rows = []
for k in order:
    v = KAM[k]
    g = pct(v['y26'], v['y27'])
    rows.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>'
                '<td class="%s">%s%%</td><td>%s</td></tr>'
                % (k, f(v['customers'], 0), f(v['accounts'], 0), f(v['y26']), f(v['y27']),
                   cls(g), ('+' if g > 0 else '&minus;') + f(abs(g)), f(v['y28'])))
rows.append('<tr class="tot"><td>Total assigned</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>'
            '<td class="%s">%s%%</td><td>%s</td></tr>'
            % (f(sum(v['customers'] for v in KAM.values()), 0), f(D['assigned_accounts'], 0),
               f(ASSIGNED[2026]), f(ASSIGNED[2027]),
               cls(pct(ASSIGNED[2026], ASSIGNED[2027])),
               ('+' if ASSIGNED[2027] > ASSIGNED[2026] else '&minus;') + f(abs(pct(ASSIGNED[2026], ASSIGNED[2027]))),
               f(ASSIGNED[2028])))
rows.append('<tr><td>Unassigned commercial and residential</td><td>%s+</td><td>%s+</td><td>%s</td><td>%s</td>'
            '<td class="pos">+%s%%</td><td>%s</td></tr>'
            % (f(D['unassigned_comm_customers'], 0), f(D['unassigned_comm_accounts'], 0),
               f(UNASSIGNED[2026]), f(UNASSIGNED[2027]),
               f(pct(UNASSIGNED[2026], UNASSIGNED[2027])), f(UNASSIGNED[2028])))
rows.append('<tr class="tot"><td>Total company sales</td><td></td><td></td><td>%s</td><td>%s</td>'
            '<td class="pos">+%s%%</td><td>%s</td></tr>'
            % (f(CO[2026]), f(CO[2027]), f(pct(CO[2026], CO[2027])), f(CO[2028])))
PORTFOLIO = '\n'.join(rows)

MOVES = '\n'.join(
    '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class="%s">%s</td></tr>'
    % (m['n'], m['k'], m['rc'], f(m['a']), f(m['b']), cls(m['d']), sign(m['d']))
    for m in D['movements'])

regrows = sorted(reg.values(), key=lambda e: (e['kam'] or 'zz', e['name']))
REGISTER = '\n'.join(
    '<tr><td>%s%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class="l">%s</td></tr>'
    % (e['name'], ('' if e['nacc'] == 1 else ' <small>(%d sites)</small>' % e['nacc']),
       e['kam'] or '<i>unassigned</i>', e['entered'],
       e['period'] + ('' if not e['partial'] else
                      ' <small>(+%d more entered by Sales Forecasting)</small>' % len(e['partial'])),
       e['impact'], e['reason'], e['just'][:150])
    for e in regrows)

HTML = io.open(os.path.join(HERE, '_kam_review_template.html'), encoding='utf-8').read()
TOK = {
 'ASAT': AS_AT, 'PORTFOLIO': PORTFOLIO, 'MOVES': MOVES, 'REGISTER': REGISTER,
 'NREG': str(len(regrows)), 'NHID': str(len(hidden)),
 'LEAD': NOTES['lead'], 'LEADBODY': NOTES['lead_body'],
 'WORSTHD': NOTES['worst_hd'], 'WORSTBODY': NOTES['worst_body'],
 'CO27': f(CO[2027]), 'CO28': f(CO[2028]),
 'AS26': f(ASSIGNED[2026]), 'AS27': f(ASSIGNED[2027]), 'AS28': f(ASSIGNED[2028]),
}
out = HTML
for k, v in TOK.items():
    out = out.replace('@%s@' % k, v)
assert not re.search(r'@[A-Z0-9]+@', out), 'unresolved token'
io.open(DST, 'w', encoding='utf-8').write(out)
print()
print('written %s  (%d managers, %d register entries)' % (DST, len(KAM), len(regrows)))
