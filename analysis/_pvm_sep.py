# -*- coding: utf-8 -*-
# September 2026 / YTD non-fuel revenue: volume, mix and rate decomposition vs budget and vs prior year.
import json
d = json.load(open('corrected.json', encoding='utf-8'))
CL = ['RT10', 'RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70']
def bucket_sum(title, months):
    t = [0.0] * 6   # kwh, rev, energy, fuel, ipp, cust
    for mo in months:
        for v in d['bucket'][mo][title].values():
            for i in range(6): t[i] += v[i + 1]
    return dict(kwh=t[0], rev=t[1], energy=t[2], fuel=t[3], ipp=t[4], cust=t[5], demand=0.0)
M26S, M25S = ['2026-09'], ['2025-09']
M26Y = ['2026-%02d' % m for m in range(1, 10)]; M25Y = ['2025-%02d' % m for m in range(1, 10)]
# RT40+ from jps_actuals (SQL, J$ and kWh), prepaid from the loaded prepaid rows
ACC = {  # (year, per): class: kwh, rev, cust, energy, demand, fuel, ipp
 (2025, 'SEP'): {'RT40': (68941054, 3204731776, 17653446, 466039382, 656333069, 1725349507, 282916279), 'RT50': (33527203, 1281256885, 1441293, 162969043, 207607325, 693708613, 203698062), 'RT60-ST': (3408535, 215250132, 1455088, 47982203, 0, 85626726, 78369845), 'RT70': (27281357, 1072760953, 208541, 135973011, 212010265, 513352476, 26367970)},
 (2026, 'SEP'): {'RT40': (67312952, 3199838484, 17863288, 455409626, 644179434, 1779129384, 258822131), 'RT50': (30252675, 1203080583, 1423267, 147566148, 195618459, 651965356, 199343450), 'RT60-ST': (3413193, 213697099, 1418528, 48052657, 0, 90531526, 72666893), 'RT70': (18642652, 874143463, 190407, 93899158, 240114857, 479227611, 37434222)},
 (2025, 'YTD'): {'RT40': (605323824, 27688024293, 158184454, 4086248346, 5862553465, 14516196706, 2665559332), 'RT50': (287170236, 11407396557, 12969457, 1390957410, 1968132066, 6117935929, 1845830081), 'RT60-ST': (30381836, 1906291497, 12602232, 427730116, 0, 738810553, 717498168), 'RT70': (226863025, 8983415598, 1885935, 1129546420, 2021334870, 4431007584, 249642369)},
 (2026, 'YTD'): {'RT40': (569766822, 27336044480, 159191412, 3846414541, 5650891046, 15091697432, 2266347514), 'RT50': (259548798, 10564400936, 12926057, 1260382748, 1823592641, 5782313372, 1647748027), 'RT60-ST': (27490451, 1738996265, 12777720, 387106820, 0, 737646092, 594501993), 'RT70': (213868492, 9127344336, 1749786, 1065840667, 1948778590, 5726574731, 276534394)},
}
PP = {  # prepaid (revenue only, no components): class: kwh, rev
 (2025, 'SEP'): {'RT10': (2509113, 140270714), 'RT20': (101891, 6064436)}, (2026, 'SEP'): {'RT10': (3009820, 173513942), 'RT20': (108857, 6568992)},
 (2025, 'YTD'): {'RT10': (20286550, 1128036330), 'RT20': (898609, 51870872)}, (2026, 'YTD'): {'RT10': (22318901, 1318025632), 'RT20': (894281, 55714320)},
}
BUD_FX = {'SEP': 141514e3, 'YTD': 1016036e3}    # budget F/X adjustment lines (customer+demand+energy), J$
BUDNF = {  # class: kwh, customer, energy, demand (J$000, MWh)
 'SEP': {'RT10': (104830, 384154, 1625216, 0), 'RT20': (57649, 94062, 589887, 0), 'RT40': (73334, 17671, 498806, 668702), 'RT50': (35268, 1452, 179719, 225277), 'RT60-ST': (3312, 1839, 46566, 0), 'RT70': (22866, 199, 117026, 221840)},
 'YTD': {'RT10': (852217, 3457384, 13211115, 0), 'RT20': (459863, 846562, 4705612, 0), 'RT40': (594517, 159038, 4043804, 6025122), 'RT50': (276034, 13071, 1415265, 2008597), 'RT60-ST': (28174, 16550, 396132, 0), 'RT70': (191229, 1795, 978671, 1995678)},
}
def _platform_actual(year, per):
    out = {}
    ms = {(2026, 'SEP'): M26S, (2025, 'SEP'): M25S, (2026, 'YTD'): M26Y, (2025, 'YTD'): M25Y}[(year, per)]
    for t in ('RT10', 'RT20'):
        b = bucket_sum(t, ms); pk, pr = PP[(year, per)][t]
        nf_rate = (b['cust'] + b['energy']) / b['kwh']          # prepaid has no components: assume the postpaid non-fuel rate
        out[t] = dict(kwh=b['kwh'] + pk, cust=b['cust'], energy=b['energy'], demand=0.0, fuel=b['fuel'], ipp=b['ipp'], rev=b['rev'] + pr, nf=b['cust'] + b['energy'] + nf_rate * pk, prepaid_kwh=pk, prepaid_rev=pr)
    for c, (k, rev, cu, en, de, fu, ip) in ACC[(year, per)].items():
        out[c] = dict(kwh=k, cust=cu, energy=en, demand=de, fuel=fu, ipp=ip, rev=rev, nf=cu + en + de)
    return out
ES_PATH = r'C:\Users\jwilson\AppData\Local\Temp\Esheet 9-26 (1).xlsx'
def es_sept():
    """September 2026 from the finance Earnings Sheet: volume and J$ components by class."""
    import openpyxl
    ws = openpyxl.load_workbook(ES_PATH, data_only=True).worksheets[0]
    rows = {i: [c.value for c in ws[i]] for i in range(9, 27)}
    col = {'RT10': 3, 'RT20': 7, 'RT40': 11, 'RT50': 15, 'RT60-ST': 19, 'RT70': 23}     # MWh column in row 10; the $ column is col-1
    n = lambda v: float(v) if isinstance(v, (int, float)) else 0.0
    out = {}
    for c, j in col.items():
        cust = n(rows[9][j - 1]) + n(rows[11][j - 1]); en = n(rows[14][j - 1]); de = n(rows[12][j - 1])
        out[c] = dict(kwh=n(rows[10][j]) * 1e3, cust=cust, energy=en, demand=de, nf=cust + en + de,
                      fuel=n(rows[16][j - 1]), fex=n(rows[18][j - 1]), ipp=n(rows[22][j - 1]) + n(rows[23][j - 1]), rev=n(rows[26][j - 1]))
    return out
def actual(year, per):
    """2026 September = Earnings Sheet; 2026 YTD = platform Jan-Aug + Earnings Sheet September; 2025 = platform."""
    out = _platform_actual(year, per)
    if year != 2026: return out
    es = es_sept()
    if per == 'SEP': return es
    sep = _platform_actual(2026, 'SEP'); new = {}
    for c in out:
        new[c] = {k: out[c].get(k, 0.0) - sep[c].get(k, 0.0) + es[c].get(k, 0.0) for k in ('kwh', 'cust', 'energy', 'demand', 'fuel', 'ipp', 'rev', 'nf')}
        new[c]['fex'] = es[c]['fex']
    return new
def budget(per):
    return {c: dict(kwh=k * 1e3, nf=(cu + en + de) * 1e3, cust=cu * 1e3, energy=en * 1e3, demand=de * 1e3) for c, (k, cu, en, de) in BUDNF[per].items()}
def pvm(A, B):
    """A, B: class -> dict(kwh, nf). Volume = total volume change at the base average rate; mix = shift between classes at base rates; rate = actual rate vs base rate on actual volume."""
    At, Bt = sum(a['kwh'] for a in A.values()), sum(b['kwh'] for b in B.values())
    Ant, Bnt = sum(a['nf'] for a in A.values()), sum(b['nf'] for b in B.values())
    avgB = Bnt / Bt
    vol = (At - Bt) * avgB
    mix = sum(A[c]['kwh'] * (B[c]['nf'] / B[c]['kwh']) for c in A) - At * avgB
    rate = sum(A[c]['nf'] - A[c]['kwh'] * (B[c]['nf'] / B[c]['kwh']) for c in A)
    byc = {c: dict(vol=(A[c]['kwh'] - B[c]['kwh'] * 0) * 0, mix=0) for c in A}
    return dict(A_kwh=At, B_kwh=Bt, A_nf=Ant, B_nf=Bnt, vol=vol, mix=mix, rate=rate, total=Ant - Bnt, check=vol + mix + rate - (Ant - Bnt), avgB=avgB, avgA=Ant / At)
if __name__ == '__main__':
    for per in ('SEP', 'YTD'):
        a26, a25, b = actual(2026, per), actual(2025, per), budget(per)
        for lab, base in (('vs budget', b), ('vs prior year', a25)):
            r = pvm(a26, base)
            print(per, lab, 'kWh %.1f -> %.1f GWh (%.2f%%)' % (r['B_kwh'] / 1e6, r['A_kwh'] / 1e6, 100 * (r['A_kwh'] / r['B_kwh'] - 1)),
                  '| non-fuel J$M %.0f -> %.0f (%+.0f, %.2f%%)' % (r['B_nf'] / 1e6, r['A_nf'] / 1e6, r['total'] / 1e6, 100 * r['total'] / r['B_nf']),
                  '| vol %+.0f mix %+.0f rate %+.0f (check %.3f) | avg rate %.2f -> %.2f' % (r['vol'] / 1e6, r['mix'] / 1e6, r['rate'] / 1e6, r['check'], r['avgB'], r['avgA']))
