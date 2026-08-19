# -*- coding: utf-8 -*-
import json, sys, io
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open('_cfo_deck_data.json'))

# JSON object keys are always strings -- the month-keyed dicts inside 'assumptions'
# (e.g. {"8": 1.0, "9": -2.04, ...}) round-tripped through json.dump/json.load and
# lost their original int keys, which silently broke every `month in dct` lookup
# downstream (int 8 was never "in" a dict keyed by the string "8").
def _intify_month_keys(dct):
    return {int(k): v for k, v in dct.items()}

_a = d['assumptions']
for _key in ('macro_commercial', 'macro_residential', 'weather', 'seasonality_residential'):
    _a[_key] = _intify_month_keys(_a[_key])
_a['industry'] = {ind: _intify_month_keys(months) for ind, months in _a['industry'].items()}

# ---- Top industries overall (across all KAMs, FY2026) ----
ind_fy = {ind: sum(m.values()) for ind, m in d['ind_month'].items()}
ind_sorted = sorted(ind_fy.items(), key=lambda kv: -kv[1])
print('=== Top industries by FY2026 forecast (GWh) ===')
for name, v in ind_sorted[:15]:
    print(f'  {name:45s} {v/1e6:7.2f}')

# ---- Per-KAM: top 3 industries, rate-class mix ----
print('\n=== Per-KAM industry mix (top 3) ===')
kam_top_ind = {}
for kam, inds in d['kam_ind_fy'].items():
    top3 = sorted(inds.items(), key=lambda kv: -kv[1])[:3]
    kam_top_ind[kam] = top3
    print(f'  {kam}:')
    for name, v in top3:
        print(f'      {name:40s} {v/1e6:6.2f} GWh')

print('\n=== Per-KAM rate-class mix ===')
for kam, rcs in d['kam_rc_fy'].items():
    parts = ', '.join(f'{rc} {v/1e6:.1f}' for rc, v in sorted(rcs.items(), key=lambda kv: -kv[1]))
    print(f'  {kam}: {parts}')

# ---- Per-KAM top 3 / bottom 3 customers ----
# Top 3 = largest FY forecast volume. Bottom 3 = steepest YoY decline among customers
# with a materiality floor (50,000 kWh / 0.05 GWh of prior-year volume), so a near-zero
# noise account doesn't crowd out a real decline just because its % swing is huge --
# same convention the app's own "Bottom 10 -- Largest YoY Declines" report uses.
MATERIALITY_FLOOR = 50000.0
print('\n=== Per-KAM top 3 / bottom 3 customers ===')
kam_top_cust = {}
kam_bottom_cust = {}
for kam, custs in d['kam_customers'].items():
    # Two distinct customer numbers can share the exact same trading name (e.g. two
    # legal entities both named "Club Caribbean Limited") -- disambiguate with the
    # customer number so a slide never shows the identical name twice with no way
    # to tell the reader these are different accounts.
    name_counts = defaultdict(int)
    for c in custs.values():
        name_counts[c['name'] or ''] += 1
    entries = []
    for custno, c in custs.items():
        fy = c['fy']; py = c['py']
        chg = (fy / py - 1) * 100 if py > 1e-6 else None
        base_name = c['name'] or custno
        disp_name = f'{base_name} ({custno})' if name_counts[c['name'] or ''] > 1 else base_name
        entries.append({'name': disp_name, 'fy_gwh': fy / 1e6, 'py_gwh': py / 1e6, 'chg_pct': chg, 'n_accounts': c['n_accounts']})
    top3 = sorted(entries, key=lambda e: -e['fy_gwh'])[:3]
    declines = [e for e in entries if e['py_gwh'] * 1e6 >= MATERIALITY_FLOOR and e['chg_pct'] is not None]
    bottom3 = sorted(declines, key=lambda e: e['chg_pct'])[:3]
    kam_top_cust[kam] = top3
    kam_bottom_cust[kam] = bottom3
    print(f'  {kam}: top={[e["name"] for e in top3]}  bottom={[e["name"] for e in bottom3]}')

# ---- Assumptions summary (company-wide macro/weather, formatted for the deck) ----
a = d['assumptions']
fc_months = a['forecast_months']
MONTH_ABBR = {8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec', 1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul'}

def series_str(dct):
    return ', '.join(f'{MONTH_ABBR[m]} {dct[m]:+.1f}%' for m in fc_months if m in dct)

# Group the raw per-(account, month) adjustment rows into one row per (account, reason)
# -- e.g. Alcoa's three separate Aug/Sep/Oct -100% rows become a single "Aug-Oct: -100%"
# line, which is what a reader actually wants to see, not a repeated account three times.
opadj_groups = defaultdict(list)
for o in a['operational_adjustments']:
    opadj_groups[(o['jps_ac'], o['reason_code'])].append(o)

def month_range_str(months_pcts):
    # Sort by raw month number -- adjustments can start in an already-actual month
    # (e.g. July, before CUR_MONTH+1) and continue into the forecast window, so
    # fc_months.index() (which only knows the forecast months) isn't a valid sort key.
    months_pcts.sort(key=lambda mp: mp[0])
    pcts = {p for _, p in months_pcts}
    pct_str = f'{pcts.pop():+.0f}%' if len(pcts) == 1 else '/'.join(f'{p:+.0f}%' for _, p in months_pcts)
    labels = [MONTH_ABBR.get(m, m) for m, _ in months_pcts]
    if len(labels) > 1:
        return f'{labels[0]}-{labels[-1]}: {pct_str}'
    return f'{labels[0]}: {pct_str}'

def clean_note(text):
    # Source text has a pre-existing mojibake artifact (non-breaking spaces
    # mis-encoded as U+00C2 U+00A0, i.e. "Â " / \xc2\xa0) from whatever it was
    # originally pasted from -- normalize to a plain space for display.
    import re
    return re.sub(r' {2,}', ' ', text.replace('Â ', ' ').replace(' ', ' ')).strip()

opadj_rows_grouped = []
for (jps_ac, reason), rows in opadj_groups.items():
    rows.sort(key=lambda r: r['month'])
    note = clean_note(rows[0]['justification'] or '')
    # pptxgenjs table cells wrap and auto-grow row height, so the column can carry a
    # couple of lines -- only clip the genuinely long ones (Sutherland's is 389 chars),
    # and clip at the last word boundary rather than mid-word.
    CAP = 200
    if len(note) > CAP:
        note = note[:CAP].rsplit(' ', 1)[0] + '...'
    opadj_rows_grouped.append({
        'jps_ac': jps_ac,
        'name': rows[0]['name'] or jps_ac,
        'kam': rows[0]['kam'],
        'reason': reason,
        'period': month_range_str([(r['month'], r['operational_pct']) for r in rows]),
        'note': note,
    })
opadj_rows_grouped.sort(key=lambda r: r['jps_ac'])

def first_last(dct):
    vals = [dct[m] for m in fc_months if m in dct]
    return (vals[0], vals[-1]) if vals else (None, None)

_mc_first, _mc_last = first_last(a['macro_commercial'])
_mr_first, _mr_last = first_last(a['macro_residential'])

assumptions_summary = {
    'forecast_months_label': f'{MONTH_ABBR[fc_months[0]]}-{MONTH_ABBR[fc_months[-1]]} {d["year"]}' if fc_months else '',
    'macro_commercial_str': series_str(a['macro_commercial']),
    'macro_residential_str': series_str(a['macro_residential']),
    'macro_commercial_pct_first': _mc_first, 'macro_commercial_pct_last': _mc_last,
    'macro_residential_pct_first': _mr_first, 'macro_residential_pct_last': _mr_last,
    'weather_str': series_str(a['weather']) if any(v != 0 for v in a['weather'].values()) else 'No weather adjustment on file',
    'n_operational_adjustments': len(opadj_rows_grouped),
    'operational_adjustments': opadj_rows_grouped,
}

def kam_assumption_note(kam):
    """One-line assumption callout for a KAM's #1 industry, if it has a modeled driver."""
    top = kam_top_ind.get(kam)
    if not top:
        return None
    ind_name, _ = top[0]
    ind_pcts = a['industry'].get(ind_name)
    if not ind_pcts:
        return None
    return f'{ind_name}: {series_str(ind_pcts)}'

# ---- Save a clean, deck-ready summary ----
kams = []
for kam in d['kam_month']:
    fy = sum(d['kam_month'][kam].values())
    bud = d['kam_budget_fy'].get(kam, 0)
    py = d['kam_py_fy'].get(kam, 0)
    kams.append({
        'name': kam,
        'n_accounts': d['kam_accounts_count'].get(kam, 0),
        'n_customers': len(d['kam_customers'].get(kam, {})),
        'fy_gwh': fy / 1e6,
        'bud_gwh': bud / 1e6,
        'py_gwh': py / 1e6,
        'vs_bud_pct': (fy / bud - 1) * 100 if bud else None,
        'vs_py_pct': (fy / py - 1) * 100 if py else None,
        'top_industries': [{'name': n, 'gwh': v / 1e6} for n, v in kam_top_ind.get(kam, [])],
        'rc_mix': {rc: v / 1e6 for rc, v in d['kam_rc_fy'].get(kam, {}).items()},
        'top_customers': kam_top_cust.get(kam, []),
        'bottom_customers': kam_bottom_cust.get(kam, []),
        'assumption_note': kam_assumption_note(kam),
    })
kams.sort(key=lambda k: -k['fy_gwh'])

rc_summary = []
for rc, m in d['rc_month'].items():
    fy = sum(m.values())
    bud = d['rc_budget_fy'].get(rc, 0)
    py = d['rc_py_fy'].get(rc, 0)
    rc_summary.append({
        'rc': rc, 'fy_gwh': fy / 1e6, 'bud_gwh': bud / 1e6, 'py_gwh': py / 1e6,
        'vs_bud_pct': (fy / bud - 1) * 100 if bud else None,
        'vs_py_pct': (fy / py - 1) * 100 if py else None,
    })

RC_ORDER = ['RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']
rc_summary.sort(key=lambda r: RC_ORDER.index(r['rc']) if r['rc'] in RC_ORDER else 99)

tot_fy = sum(r['fy_gwh'] for r in rc_summary)
tot_bud = sum(r['bud_gwh'] for r in rc_summary)
tot_py = sum(r['py_gwh'] for r in rc_summary)

commercial_rcs = {'RT40', 'RT50', 'RT60-ST', 'RT70'}
managed_fy = sum(k['fy_gwh'] for k in kams)
commercial_fy = sum(r['fy_gwh'] for r in rc_summary if r['rc'] in commercial_rcs)
unmanaged_fy = commercial_fy - managed_fy

top_industries = [{'name': n, 'gwh': v / 1e6} for n, v in ind_sorted[:12]]

out = {
    'year': d['year'], 'cur_month': d['cur_month'], 'prior_year': d['prior_year'],
    'company': {'fy_gwh': tot_fy, 'bud_gwh': tot_bud, 'py_gwh': tot_py,
                'vs_bud_pct': (tot_fy / tot_bud - 1) * 100, 'vs_py_pct': (tot_fy / tot_py - 1) * 100},
    'rc_summary': rc_summary,
    'kams': kams,
    'top_industries': top_industries,
    'commercial_fy_gwh': commercial_fy,
    'managed_fy_gwh': managed_fy,
    'unmanaged_fy_gwh': unmanaged_fy,
    'assumptions': assumptions_summary,
}
json.dump(out, open('_cfo_deck_ready.json', 'w'))
print('\nSaved _cfo_deck_ready.json')
print(f"\nCommercial book: {commercial_fy:.1f} GWh total | KAM-managed: {managed_fy:.1f} GWh ({managed_fy/commercial_fy*100:.1f}%) | Unmanaged cohort: {unmanaged_fy:.1f} GWh ({unmanaged_fy/commercial_fy*100:.1f}%)")
