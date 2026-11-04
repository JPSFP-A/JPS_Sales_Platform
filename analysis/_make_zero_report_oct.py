# -*- coding: utf-8 -*-
# Derives build_zero_anomaly_report_2026_10.py from the August builder: new input/output names, the window and
# streak-length wording computed from the data instead of typed in, and one extra sheet with the monthly trend of
# accounts billed at zero. The August builder is left untouched.
s = open('build_zero_anomaly_report.py', encoding='utf-8').read()

def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)

rep('d = json.load(open("_zero_streak_result.json"))', 'import sys\nMO = sys.argv[1] if len(sys.argv) > 1 else "2026-10"\nd = json.load(open("_zero_streak_result_%s.json" % MO))\n_MN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]\nWIN_END = "%s %s" % (_MN[int(MO[5:7]) - 1], MO[:4])\nMAXSTREAK = max(x["streak_len"] for x in d["streaks"])')
rep('"dataset window (up to 19 straight months) and are being billed at a default minimum instead. Billing",', '"dataset window (up to %d straight months) and are being billed at a default minimum instead. Billing" % MAXSTREAK,')
rep('window (Jan 2025-Jul 2026) with no positive-consumption month "', 'window (Jan 2025-" + WIN_END + ") with no positive-consumption month "')
rep('wb.save("Zero_Consumption_Anomaly_Report.xlsx")', '''# ===== Monthly trend of accounts billed at zero =====
ws = wb.create_sheet("Monthly Trend")
ws.sheet_view.showGridLines = False
ws["B2"] = "Accounts Billed at Zero kWh, by Month"
ws["B2"].font = TITLE_FONT
ws["B4"] = "Account-level rows only (RT20 commercial, RT40, RT50, RT60-ST, RT70). RT10 and RT20 residential have no account identity, so their zero-consumption customers are counted on the next sheet. December 2025 to February 2026 is the hurricane restoration period."
ws["B4"].font = Font(name=FONT, size=10)
hdr = ["Month", "Accounts billed", "At zero kWh", "RT20", "RT40 to RT70", "Zero as % of accounts"]
row = 6
for i, h in enumerate(hdr):
    ws.cell(row=row, column=2 + i, value=h)
style_header(ws, row, len(hdr), start_col=2)
row += 1
for k in sorted(d["monthly_zero_accounts"]):
    t = d["monthly_zero_accounts"][k]
    vals = [k, t["accounts"], t["zero"], t["RT20"], t["RT40-RT70"], t["zero"] / t["accounts"] if t["accounts"] else 0]
    for i, v in enumerate(vals):
        c = ws.cell(row=row, column=2 + i, value=v)
        if i in (1, 2, 3, 4): c.number_format = NUMFMT
        if i == 5: c.number_format = "0.0%"
    row += 1
autosize(ws, [3, 12, 16, 14, 10, 14, 20])
wb.save("Zero_Consumption_Anomaly_Report_%s.xlsx" % MO.replace("-", "_"))''')
open('build_zero_anomaly_report_2026_10.py', 'w', encoding='utf-8').write(s)
print('wrote build_zero_anomaly_report_2026_10.py')
