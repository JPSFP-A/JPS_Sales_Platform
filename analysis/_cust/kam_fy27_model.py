# -*- coding: utf-8 -*-
# FY2027 account-level sales forecast for the KAM review (actuals to October 2026).
# Trend base per account (Aug-Oct 2026 median level x class seasonal index x growth), hotel recovery by account,
# KAM adjustments on file (platform semantics: % on the forecast plus manual kWh), analyst overrides, pipeline customers.
import json, re, collections, os
import numpy as np, pandas as pd
HERE = r'C:\Projects\Sales_Platform\analysis'
os.chdir(HERE + r'\_cust')
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
m_ = json.load(open('pull_oct.json'))
act = pd.DataFrame(m_['act'])[['year', 'month', 'jps_ac', 'name', 'rate_class', 'parish', 'kwh']]
act = act[act.jps_ac.astype(str).str.len() > 0].copy(); act['kwh'] = act.kwh.astype(float)
# the cached pull predates the October RT20 account rows: replace October 2026 with the live table
import io, requests, truststore; truststore.inject_into_ssl()
_env = {}
for _l in io.open(HERE + r'\.env', encoding='utf-8'):
    if '=' in _l and not _l.startswith('#'): _k, _v = _l.strip().split('=', 1); _env[_k] = _v.strip('"')
_H = {'apikey': _env['SUPABASE_SERVICE_ROLE_KEY'], 'Authorization': 'Bearer ' + _env['SUPABASE_SERVICE_ROLE_KEY']}
_oct = pd.read_pickle('oct26_rows.pkl').to_dict('records')   # cached by fetch_oct_rows.py
_oct = pd.DataFrame(_oct); _oct = _oct[_oct.jps_ac.fillna('').astype(str).str.len() > 0].copy(); _oct['kwh'] = _oct.kwh.astype(float)
act = pd.concat([act[~((act.year == 2026) & (act.month == 10))], _oct[act.columns.intersection(_oct.columns)]], ignore_index=True)
print('October rows refreshed:', len(_oct), 'GWh', round(_oct.kwh.sum() / 1e6, 2))
act['t'] = act.year * 12 + act.month
base_of = lambda ac: str(ac).split('-')[0]
# ---- reference maps ----
kam_map = {}
for r in sorted(m_['kam'], key=lambda r: r['created_at']): kam_map[str(r['jps_ac'])] = r['kam']
def kam_of(ac):
    return kam_map.get(str(ac)) or kam_map.get(base_of(ac)) or ''
ind_map = {str(r['jps_ac']): r['industry'] for r in m_['ind']}
ind_of = lambda ac: ind_map.get(str(ac)) or ind_map.get(base_of(ac)) or ''
HOTEL = re.compile(r'hotel|motel|resort|accommodation|casino', re.I)
# ---- account table and monthly matrix ----
T = lambda y, m: y * 12 + m
piv = act.pivot_table(index='jps_ac', columns='t', values='kwh', aggfunc='sum')
last = act.sort_values('t').groupby('jps_ac').tail(1).set_index('jps_ac')
acc = pd.DataFrame({'name': last.name.fillna(''), 'rc': last.rate_class, 'parish': last.parish})
acc['kam'] = [kam_of(a) for a in acc.index]; acc['industry'] = [ind_of(a) for a in acc.index]
acc['hotel'] = [bool(HOTEL.search(i or '')) for i in acc.industry]
g = lambda ac, y, m: piv.at[ac, T(y, m)] if (T(y, m) in piv.columns and ac in piv.index) else np.nan
# ---- class seasonal index and shapes, same method as the class forecast ----
A = json.load(open(HERE + r'\_fy27_actuals.json')); R24 = json.load(open(HERE + r'\_fy27_res24.json')); SHR = json.load(open(HERE + r'\_fy27_shape_res.json'))
cg = lambda y, m, c: A['%d-%02d' % (y, m)][c]
def ser(y, c, m): return R24['2024-%02d' % m][c] if (y == 2024 and c in ('RT10', 'RT20')) else cg(y, m, c)
W = {2024: 0.25, 2025: 0.75}
IDX = {c: {m: sum(W[y] * ser(y, c, m) / ((ser(y, c, 8) + ser(y, c, 9)) / 2) for y in (2024, 2025)) for m in range(1, 10)} for c in ('RT10', 'RT20', 'RT40', 'RT50')}
SHAPE = {c: (cg(2024, 11, c) / cg(2024, 10, c), cg(2024, 12, c) / cg(2024, 10, c)) for c in ('RT40', 'RT50', 'RT60-ST')}
SHAPE['RT20'] = tuple(SHR['RT20']); SHAPE['RT10'] = tuple(SHR['RT10']); SHAPE['RT70'] = (1.0, 1.0)
G_RES = 0.008; G_COM = lambda m: 0.0 if m <= 3 else 0.010
HF = [0.19, 0.23, 0.30, 0.36, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75]   # share of the hotel gap to pre-storm that is back, Jan to Dec 2027
# ---- level per account: median of Aug, Sep, Oct 2026 (robust to one-month timing and outages) ----
def level(ac):
    v = [g(ac, 2026, m) for m in (8, 9, 10)]; v = [x for x in v if not np.isnan(x)]
    return float(np.median(v)) if v else 0.0
acc['level'] = [level(a) for a in acc.index]
acc['oct26'] = [g(a, 2026, 10) for a in acc.index]
acc['fy25'] = [float(np.nansum([g(a, 2025, m) for m in range(1, 13)])) for a in acc.index]
acc['ytd26'] = [float(np.nansum([g(a, 2026, m) for m in range(1, 11)])) for a in acc.index]
acc['ps'] = [float(np.nanmean([g(a, 2025, m) for m in range(1, 10)])) if any(not np.isnan(g(a, 2025, m)) for m in range(1, 10)) else 0.0 for a in acc.index]  # pre-storm mean Jan-Sep 2025
# ---- analyst overrides (replace the entries on file for these accounts) ----
# ac -> list of (effective t, pct, kwh, roll)
def ov(ac, y, m, pct, kwh=0): return [(T(y, m), pct, kwh, True)]
OVERRIDE = {
    '100185-607213': (ov('', 2026, 11, -100), 'Alcoa main account: zero from November (KAM entry -100%; October shows 0.26 GWh after a 2.0 GWh billing credit).'),
    '1411748-834411': (ov('', 2026, 11, -80), 'PAC Kingston Airport: KAM entry -80% from October; October billing still full (0.83 GWh), so applied from November.'),
    '804282-768320': (ov('', 2027, 1, -47), 'MBJ Airports: KAM entry is -77%; public record supports about -47% (6 MW PV, 60% solar target). Analyst view -47% from January 2027.'),
    '100312-100512': (ov('', 2027, 3, -70), 'West Meat Packers: KAM says 70% of load leaves by Q1 2027; entry moved from January to March.'),
    '101188-101755': ([(T(2027, 1), -50, 0, False), (T(2027, 2), -50, 0, False), (T(2027, 4), 10, 0, False), (T(2027, 5), 10, 0, False), (T(2027, 6), 10, 0, False)], 'Petrojam: planned 70-day maintenance shutdown from January 2027 (KAM recorded 77 days). Face-value profile: 50% of trend in January and February, trend in March, 10% above trend April to June. The entries on file are solved against the engine base, so they are replaced here.'),
    '1164542-1098473': (ov('', 2026, 11, -15), 'Sutherland Global: KAM entry -80% but billing shows no drop (100 kW PV is about 17% of load). Analyst view -15%.'),
    '100187-100277': (ov('', 2026, 11, -25), 'Clarendon Distillers: CHP installed but idle. Held at -25% until the units run.'),
}
# ---- adjustments on file ----
op = pd.DataFrame(m_['opadj']); op['t'] = op.year * 12 + op.month
ROLLS = {'Confirmed defection', 'Possible defection', 'Expansion', 'Renewal', 'Win-back'}
def entries(ac):
    seen = set(); out = []
    for r in op.itertuples():
        rac = str(r.jps_ac)
        if not (rac == ac or rac == base_of(ac) or ac == rac.split('-')[0]): continue
        if str(r.justification or '').startswith('Hurricane storm recovery'): continue   # replaced by the account-level hotel recovery below
        pct, kwh = float(r.operational_pct or 0), float(r.manual_kwh or 0)
        roll = (r.reason_code in ROLLS) or (pct == 0 and kwh == 0)
        k = ('R' if roll else 'M') + str(r.t)
        if k in seen: continue
        seen.add(k); out.append((int(r.t), pct, kwh, roll, r.reason_code))
    return sorted(out)
def effective(es, t):
    pct = kwh = 0.0; lastr = None
    for e in es:
        if e[0] > t: break
        if e[3]: lastr = e
        elif e[0] == t: pct += e[1]; kwh += e[2]
    if lastr: pct += lastr[1]; kwh += lastr[2]
    return pct, kwh
def reflected(ac, e):
    # an entry effective on or before October is "in actuals" when the account has already moved by at least half of the entered percentage
    t0, pct = e[0], e[1]
    if pct == 0 or t0 > T(2026, 10): return False
    pre = [piv.at[ac, t] for t in range(t0 - 3, t0) if t in piv.columns and ac in piv.index and not np.isnan(piv.at[ac, t])]
    if not pre or np.mean(pre) <= 0: return False
    obs = acc.at[ac, 'level'] / np.mean(pre) - 1
    return (obs <= pct / 100 * 0.5) if pct < 0 else (obs >= pct / 100 * 0.5)
# ---- pipeline customers ----
newc = pd.DataFrame(m_['newc'])
NEWC_FIX = {   # id -> (start year, start month, kwh per month or None to drop, note)
    2: (None, None, None, 'Dropped: the Kingston club is now confirmed for December 2026 and is carried by the PriceSmart entry from January 2027 (id 4).'),
    8: (None, None, None, 'Dropped: duplicate of the Progressive Grocers Westmoreland entry (id 9).'),
    9: (2026, 12, 70000, 'Progressive Grocers: deck has the new load in December 2026 (was December 2027).'),
}
# ---- forecast ----
months = [(2026, 11), (2026, 12)] + [(2027, m) for m in range(1, 13)] + [(2028, m) for m in range(1, 13)]
G28 = {'RT20': 0.008, 'RT40': 0.010, 'RT50': 0.010, 'RT60-ST': 0.0, 'RT70': 0.0}   # 2028 growth on the same month of 2027
HF28 = list(np.linspace(0.76, 0.80, 12))                                              # hotel gap recovered through 2028 (slower: arrivals and fixed load)
rows = []
for ac, a in acc.iterrows():
    c = a.rc; L = a.level
    es = entries(ac); note = ''
    if ac in OVERRIDE: es = [(t, p, k, r, 'Analyst') for (t, p, k, r) in OVERRIDE[ac][0]]; note = OVERRIDE[ac][1]
    skipped = [e for e in es if e[4] != 'Analyst' and reflected(ac, e)]
    use = [e for e in es if e not in skipped]
    ADJR = ''
    if ac in OVERRIDE: ADJR = 'Planned outage' if ac == '101188-101755' else 'Defection or self-generation'
    elif use:
        rs = [e[4] for e in use]; ADJR = 'Defection or self-generation' if any(x in ('Confirmed defection', 'Possible defection') for x in rs) else ('Expansion' if 'Expansion' in rs else ('Other' if rs else ''))
    if skipped and not use and ac not in OVERRIDE: L = a.oct26 if not np.isnan(a.oct26) else L   # change already in the bills: anchor on October
    if ac == '793321-1224323': L = 0.0; note = 'New PriceSmart club billing from October; carried by the new-customer entry from November.'
    fc = {}; base27 = 0.0; base28 = 0.0; b27 = {}; base27_ng = 0.0
    for (y, m) in months:
        if y == 2028:
            b = b27[m] * (1 + G28.get(c, 0.0))
        elif c in ('RT20', 'RT40', 'RT50'):
            if y == 2027 and m <= 9: b = L * IDX[c][m] * (1 + (G_RES if c == 'RT20' else G_COM(m)))
            elif y == 2027: b = L * (1 + (G_RES if c == 'RT20' else 0.01)) * {10: 1.0, 11: SHAPE[c][0], 12: SHAPE[c][1]}[m]
            else: b = L * {11: SHAPE[c][0], 12: SHAPE[c][1]}[m]
        else:
            b = L * (SHAPE[c][0] if (c in SHAPE and (y, m) == (2026, 11)) else SHAPE[c][1] if (c in SHAPE and (y, m) == (2026, 12)) else 1.0)
        if y == 2027:
            b27[m] = b
            gf = (G_RES if c == 'RT20' else (G_COM(m) if m <= 9 else 0.01)) if c in ('RT20', 'RT40', 'RT50') else 0.0
            base27_ng += b / (1 + gf)
        up = 0.0
        if y in (2027, 2028) and a.hotel and a.ps > 0 and 0.3 * a.ps <= L < a.ps: up = (a.ps - L) * (HF[m - 1] if y == 2027 else HF28[m - 1])
        pct, kwh = effective(use, T(y, m))
        fc[(y, m)] = (b + up) * (1 + max(-100.0, pct) / 100) + kwh
        fc[('up', y, m)] = up
        if y == 2027: base27 += b
        if y == 2028: base28 += b
    rows.append(dict(ac=ac, name=a['name'], rc=c, kam=a.kam, industry=a.industry, hotel=a.hotel, level=L, fy25=a.fy25, ytd26=a.ytd26,
                     entries=len(es), skipped=len(skipped), note=note, **{'m%d%02d' % (y, m): fc[(y, m)] for (y, m) in months}, hotel_up27=sum(fc[('up', 2027, m)] for m in range(1, 13)), base27=base27, base27_ng=base27_ng, adjr=ADJR, hotel_up28=sum(fc[('up', 2028, m)] for m in range(1, 13)), base28=base28))
F = pd.DataFrame(rows).set_index('ac')
# pipeline rows
nrows = []
for r in newc.itertuples():
    fix = NEWC_FIX.get(r.id); y0, m0, k0, nt = (r.start_year, r.start_month, r.expected_kwh, '')
    if fix:
        y0, m0, k0, nt = fix
        if k0 is None: continue
    d = dict(ac=r.jps_ac, name=r.name, rc=r.rate_class, kam=r.kam or kam_of(r.jps_ac) or '', industry=r.industry, hotel=False, level=0.0, fy25=0.0, ytd26=0.0, entries=0, skipped=0, note=nt or 'New customer on file.', hotel_up27=0.0, base27=0.0, base27_ng=0.0, adjr='Pipeline', hotel_up28=0.0, base28=0.0)
    for (y, m) in months: d['m%d%02d' % (y, m)] = float(k0) if T(y, m) >= T(y0, m0) else 0.0
    nrows.append(d)
N = pd.DataFrame(nrows).set_index('ac') if nrows else pd.DataFrame()
cols27 = ['m2027%02d' % m for m in range(1, 13)]; cols28 = ['m2028%02d' % m for m in range(1, 13)]
F['fy27'] = F[cols27].sum(axis=1); F['fy28'] = F[cols28].sum(axis=1); F['fy26_out'] = F.ytd26 + F.m202611 + F.m202612
if len(N): N['fy27'] = N[cols27].sum(axis=1); N['fy28'] = N[cols28].sum(axis=1); N['fy26_out'] = N.m202611 + N.m202612
ALL = pd.concat([F, N]) if len(N) else F
ALL.to_pickle('kam_fy27_accounts.pkl')
# ---- class totals ----
# account-level classes; RT20 non-account remainder and RT10 stay class-level
out = {}
for c in ('RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70'):
    s = ALL[ALL.rc == c]; out[c] = dict(acct27=s.fy27.sum() / 1e6, acct26=s.fy26_out.sum() / 1e6, acct28=s.fy28.sum() / 1e6)
# RT20 remainder: class total less account-level sum, forecast with the class method
rem = {}
for (y, m) in [(2025, mm) for mm in range(1, 13)] + [(2026, mm) for mm in range(1, 11)]:
    tot = cg(y, m, 'RT20') * 1e6 if '%d-%02d' % (y, m) in A else 0.0
    rem[(y, m)] = tot - float(np.nansum([g(a, y, m) for a in acc.index[acc.rc == 'RT20']]))
Lr = (rem[(2026, 8)] + rem[(2026, 9)]) / 2
rem27 = [Lr * IDX['RT20'][m] * (1 + G_RES) if m <= 9 else rem[(2026, 10)] * (1 + G_RES) * {10: 1.0, 11: SHAPE['RT20'][0], 12: SHAPE['RT20'][1]}[m] for m in range(1, 13)]
rem26 = sum(rem[(2026, m)] for m in range(1, 11)) + rem[(2026, 10)] * (SHAPE['RT20'][0] + SHAPE['RT20'][1])
out['RT20']['rem27'] = sum(rem27) / 1e6; out['RT20']['rem26'] = rem26 / 1e6
RT10b = json.load(open(HERE + r'\_fy27_rt10_base.json'))          # class-level RT10 before the weather and EV overlays
RT10 = list(RT10b['rt10'])
# ---- weather and EV chargers in the base ----
# Weather: the temperature anomaly profile and 1.93% of residential load per degree Celsius carried by the 7 September engine; a very strong El Nino
# through February 2027 (WMO, 3 September 2026) supports a warm year. FY2028 is the flat 0.090C placeholder of that report.
ANOM27 = [0.262, 0.270, 0.367, 0.252, 0.289, 0.177, 0.153, 0.133, 0.133, 0.097, 0.112, 0.068]; ANOM28 = [0.090] * 12; SENS = 0.0193
_ev = json.load(open(HERE + r'\_driver_nov_evidence.json')); R20SH = _ev['rt20r_27'] / sum(RT10)         # RT20 residential as a share of RT10, same monthly shape
wx10_27 = [RT10[i] * ANOM27[i] * SENS for i in range(12)]; wx20_27 = [RT10[i] * R20SH * ANOM27[i] * SENS for i in range(12)]
RT10_28b = [x * 1.008 for x in RT10]
wx10_28 = [RT10_28b[i] * ANOM28[i] * SENS for i in range(12)]; wx20_28 = [RT10_28b[i] * R20SH * ANOM28[i] * SENS for i in range(12)]
# EV chargers (EV44): in the base at the August to October level once the history is reloaded; the 2026 monthly trend is the overlay
_evs = {(r[0], r[1]): r[4] for r in json.load(open(HERE + r'\_driver_res_evidence.json'))['ev']}
EV_SLOPE = float(np.polyfit(range(10), [_evs[(2026, m)] for m in range(1, 11)], 1)[0])                    # kWh a month, each month
ev27 = [EV_SLOPE * k / 1e6 for k in range(3, 15)]; ev28 = [EV_SLOPE * k / 1e6 for k in range(15, 27)]
RT10 = [RT10[i] + wx10_27[i] + ev27[i] for i in range(12)]
rem27_b = list(rem27); rem27 = [rem27[i] + wx20_27[i] * 1e6 for i in range(12)]
out['RT20']['rem27'] = sum(rem27) / 1e6
out['RT10'] = dict(total27=sum(RT10), total26=RT10b['fy26'])
rem28 = [rem27_b[i] * 1.008 + wx20_28[i] * 1e6 for i in range(12)]; out['RT20']['rem28'] = sum(rem28) / 1e6
RT10_28 = [RT10_28b[i] + wx10_28[i] + ev28[i] for i in range(12)]; out['RT10']['total28'] = sum(RT10_28)
OVERLAY = dict(wx10_27=sum(wx10_27), wx20_27=sum(wx20_27), wx10_28=sum(wx10_28), wx20_28=sum(wx20_28), ev_ov_27=sum(ev27), ev_ov_28=sum(ev28), ev_slope_kwh=EV_SLOPE)
json.dump(dict(out=out, rem27=rem27, rem28=rem28, rt10=RT10, rt10_28=RT10_28, overlay=OVERLAY), open('kam_fy27_class.json', 'w'))
print('overlay GWh', {k: round(v, 2) for k, v in OVERLAY.items()})
for c in ('RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70'):
    o = out[c]
    t27 = o.get('total27', o.get('acct27', 0) + o.get('rem27', 0)); t26 = o.get('total26', o.get('acct26', 0) + o.get('rem26', 0))
    print('%-8s FY26 out %8.1f  FY27 %8.1f  (%+.1f%%)' % (c, t26, t27, (t27 / t26 - 1) * 100), {k: round(v, 1) for k, v in o.items()})
tot27 = sum(o.get('total27', o.get('acct27', 0) + o.get('rem27', 0)) for o in out.values()); print('TOTAL FY27 %.1f' % tot27)
print('hotel uplift GWh', round(F.hotel_up27.sum() / 1e6, 1), 'hotel accounts with uplift', int((F.hotel_up27 > 0).sum()))
print('KAM accounts', int((F.kam != '').sum()), 'KAM FY27 GWh', round(F[F.kam != ''].fy27.sum() / 1e6, 1), '+ pipeline', round(N.fy27.sum() / 1e6, 2) if len(N) else 0)

# ---- tables for the KAM workbook ----
ent_rows = []
for r in op.itertuples():
    rac = str(r.jps_ac)
    matched = [a for a in acc.index if a == rac or base_of(a) == base_of(rac) and ('-' not in rac)]
    if not matched: continue
    ac0 = max(matched, key=lambda a: F.at[a, 'fy27'] if a in F.index else 0)
    just = str(r.justification or '')
    if ac0 in OVERRIDE or any(a in OVERRIDE for a in matched if '-' in rac and a == rac): tr = 'Replaced by analyst override'
    elif just.startswith('Hurricane storm recovery'): tr = 'Replaced by account-level hotel recovery'
    elif r.t > T(2028, 12): tr = 'Beyond 2028'
    elif r.t <= T(2026, 10) and (r.reason_code in ROLLS) and reflected(ac0, (int(r.t), float(r.operational_pct or 0), float(r.manual_kwh or 0), True)): tr = 'Already in the bills, not applied'
    elif r.t <= T(2026, 10) and r.reason_code not in ROLLS: tr = 'Past month, in actuals'
    else: tr = 'Applied'
    ent_rows.append(dict(kam=acc.at[ac0, 'kam'], customer=acc.at[ac0, 'name'], account=rac, y=int(r.year), m=int(r.month), pct=float(r.operational_pct or 0), kwh=float(r.manual_kwh or 0),
                         reason=r.reason_code, treat=tr, justification=just, by=r.created_by, acct_adj27=float((F.at[ac0, 'fy27'] - F.at[ac0, 'base27'] - F.at[ac0, 'hotel_up27'])) if ac0 in F.index else 0.0, acct_adj28=float((F.at[ac0, 'fy28'] - F.at[ac0, 'base28'] - F.at[ac0, 'hotel_up28'])) if ac0 in F.index else 0.0))
pd.DataFrame(ent_rows).to_pickle('kam_fy27_entries.pkl')
hot = F[F.hotel].copy(); hot['ps'] = [acc.at[a, 'ps'] for a in hot.index]
hot.to_pickle('kam_fy27_hotels.pkl')
json.dump({'OVERRIDE': {k: v[1] for k, v in OVERRIDE.items()}, 'NEWC_FIX': {str(k): v for k, v in NEWC_FIX.items()}, 'HF': HF, 'newc': newc.to_dict('records')}, open('kam_fy27_meta.json', 'w'), default=str)
print('entries', len(ent_rows), pd.DataFrame(ent_rows).treat.value_counts().to_dict())

S = ALL.copy(); S['adj27'] = S.fy27 - S.base27 - S.hotel_up27
print('BRIDGE FY27 account classes (GWh): trend base %.1f | hotel recovery %.1f | KAM adjustments and overrides %.1f | pipeline %.1f' % (F.base27.sum() / 1e6, F.hotel_up27.sum() / 1e6, (F.fy27 - F.base27 - F.hotel_up27).sum() / 1e6, N.fy27.sum() / 1e6 if len(N) else 0))
for ac in ('100185-607213', '1411748-834411', '804282-768320', '101188-101755', '689250-102172', '100058-1154117', '302571-686496', '1164542-1098473', '100187-100277', '100312-100512'):
    if ac in F.index: r = F.loc[ac]; print('%-16s %-28s L %8.0f oct26 %9s | fy27 %8.1f MWh | %s' % (ac, str(r['name'])[:28], r.level / 1e3, '%.0f' % (acc.at[ac, 'oct26'] / 1e3) if not np.isnan(acc.at[ac, 'oct26']) else 'nan', r.fy27 / 1e3, [round(r['m2027%02d' % m] / 1e3) for m in (1, 3, 6, 9, 12)]))
big = ALL[(ALL.fy27 > 2e6) | (ALL.ytd26 > 2e6)].copy(); big['ann'] = big.ytd26 / 10 * 12
big['ratio'] = big.fy27 / big.ann.replace(0, np.nan)
print(big.sort_values('ratio').head(6)[['name', 'rc', 'ytd26', 'fy27', 'ratio']].round(2).to_string())
print(big.sort_values('ratio').tail(8)[['name', 'rc', 'ytd26', 'fy27', 'ratio']].round(2).to_string())

t28 = sum(o.get('total28', o.get('acct28', 0) + o.get('rem28', 0)) for o in out.values()); print('TOTAL FY28 %.1f' % t28, {c: round(o.get('total28', o.get('acct28', 0) + o.get('rem28', 0)), 1) for c, o in out.items()})
