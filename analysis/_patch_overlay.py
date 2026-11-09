# -*- coding: utf-8 -*-
# Weather and EV chargers in the base: overlays on RT10 and on the RT20 residential remainder, written into kam_fy27_class.json.
def edit(p, pairs):
    s = open(p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:70], s.count(a)); s = s.replace(a, b)
    open(p, 'w', encoding='utf-8').write(s)

A1 = r"json.dump({'f27': f27, 'fy26': fy26, 'held': heldfy, 'le': lefy, 'ratio': ratio, 'hotel': hot}, open(HERE + r'\analysis\_fy27_result.json', 'w'))"
B1 = A1 + "\njson.dump({'rt10': f27['RT10'], 'fy26': fy26['RT10']}, open(HERE + r'\\analysis\\_fy27_rt10_base.json', 'w'))   # class-level RT10 before the weather and EV overlays"
B1 = B1.replace(r"r'\\analysis\\_fy27_rt10_base.json'", r"r'\analysis\_fy27_rt10_base.json'")
edit('_fy27_forecast.py', [(A1, B1)])

A2 = r"""RT10 = json.load(open(HERE + r'\_fy27_result.json'))['f27']['RT10']
out['RT10'] = dict(total27=sum(RT10), total26=json.load(open(HERE + r'\_fy27_result.json'))['fy26']['RT10'])
rem28 = [x * 1.008 for x in rem27]; out['RT20']['rem28'] = sum(rem28) / 1e6; RT10_28 = [x * 1.008 for x in RT10]; out['RT10']['total28'] = sum(RT10_28)
json.dump(dict(out=out, rem27=rem27, rem28=rem28, rt10=RT10, rt10_28=RT10_28), open('kam_fy27_class.json', 'w'))"""
B2 = r"""RT10b = json.load(open(HERE + r'\_fy27_rt10_base.json'))          # class-level RT10 before the weather and EV overlays
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
print('overlay GWh', {k: round(v, 2) for k, v in OVERLAY.items()})"""
edit('_cust/kam_fy27_model.py', [(A2, B2)])
print('overlay patch applied')
