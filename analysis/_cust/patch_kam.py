# -*- coding: utf-8 -*-
# One-off patch of the KAM data, model and deck scripts (layout and wording fixes).
s = open('kam_data.py', encoding='utf-8').read()
a = "    nm = ''\n    if ac in accts: nm = accts[ac]['name']"
assert a in s
if 'CACHE_NAMES' not in s:
    s = s.replace(a, a + "\n    elif ac in CACHE_NAMES: nm = CACHE_NAMES[ac]")
    s = s.replace("adj = []\nfor o in d['opadj']:", "CACHE_NAMES = json.load(open('../_kam_register_cache.json', encoding='utf-8')).get('names', {})\nadj = []\nfor o in d['opadj']:", 1)
    open('kam_data.py', 'w', encoding='utf-8').write(s)

m = open('kam_model.py', encoding='utf-8').read()
if 'def fmt_pct' not in m:
    old = "def adj_text(g):\n    v = ('+%g%%' % g['pct']) if g['pct'] > 0 else (MINUS + '%g%%' % abs(g['pct'])) if g['pct'] < 0 else ''"
    assert old in m
    m = m.replace(old, "def fmt_pct(p):\n    q = ('%.0f' if abs(p) >= 10 else '%.1f') % abs(p)\n    return ('+' if p > 0 else MINUS) + q + '%'\ndef adj_text(g):\n    v = fmt_pct(g['pct']) if g['pct'] else ''")
    m = m.replace("pct=last['pct'], reason=last['reason'] or 'Not stated', dl=dl))", "pct=last['pct'], kwh=last['kwh'], reason=last['reason'] or 'Not stated', dl=dl))")
    m = m.replace("last=f['last'], pct=f['pct'], reason=f['reason'], dl=[0, 0, 0], n=0))", "last=f['last'], pct=f['pct'], kwh=f['kwh'], reason=f['reason'], dl=[0, 0, 0], n=0))")
    open('kam_model.py', 'w', encoding='utf-8').write(m)

d = open('kam_deck.py', encoding='utf-8').read()
def rep(a, b):
    global d
    assert a in d, a[:70]
    d = d.replace(a, b, 1)
rep("""    if 'title' in nm and ph.text_frame is not None: ph.text_frame.text = 'Key Account Forecast Review'
    elif ph.placeholder_format.idx in (1, 13, 14) and ph.has_text_frame: ph.text_frame.text = 'Forecast round kick-off with the Key Account Managers | October 2026'""",
    """    if ph.placeholder_format.idx == 0: ph.text_frame.text = 'Key Account Forecast Review'
    elif ph.placeholder_format.idx == 1: ph.text_frame.text = 'Forecast round kick-off | October 2026'""")
rep("def sg(v, d=1): return ('+' if v > 0.0000001 else (MINUS if v < -0.0000001 else '')) + format(abs(v), ',.%df' % d)",
    "def sg(v, d=1):\n    if round(abs(v), d) == 0: return format(0, ',.%df' % d)\n    return ('+' if v > 0 else MINUS) + format(abs(v), ',.%df' % d)")
rep("tb(slide, x + 130000, y + 330000, w - 260000, 420000, big, 26, True, NAVY)", "tb(slide, x + 130000, y + 330000, w - 260000, 420000, big, 22, True, NAVY)")
rep("f'{len(UPCOMING)} upcoming adjustments', f'on {n_up_acc} accounts. Keep, change or remove each one in the Adjustments sheet. {n_sf} of the {n_adj} on file were entered by Sales Forecasting, not by a KAM, so they need your confirmation most.'",
    "f'{len(UPCOMING)} adjustments', f'coming up on {n_up_acc} accounts. Keep, change or remove each one in the Adjustments sheet. {n_sf} of the {n_adj} monthly entries on file were made by Sales Forecasting, not by a KAM, so they need your confirmation most.'")
rep("'New, closing, expanding',", "'Gaps and changes',")
rep("rows, row_h=322000, total=True, colors=colors + [[None] * 9])\ncallout(s, 274320, 5650000", "rows, row_h=290000, total=True, colors=colors + [[None] * 9])\ncallout(s, 274320, 5700000")
rep("    return ', '.join(sorted(r for r in rs if r)) or 'No adjustment on file'",
    "    rl = sorted(r for r in rs if r)\n    return (rl[0] + (' (+%d)' % (len(rl) - 1) if len(rl) > 1 else '')) if rl else 'No adjustment on file'")
rep("reason_for(c)[:26]] for c in lst]", "reason_for(c)] for c in lst]")
rep("s = new_slide('What Is On File', f'{n_adj} adjustments on {accounts_with} accounts take {abs(eff27):.0f} GWh out of FY2027', 'Adjustment register as at 26 October 2026.')",
    "s = new_slide('What Is On File', f'{len(GADJ)} adjustments on {accounts_with} accounts take {abs(eff27):.0f} GWh out of FY2027', f'Adjustment register as at 26 October 2026: {n_adj} monthly entries, grouped into {len(GADJ)} adjustments.')")
rep("cards = [('ADJUSTMENTS ON FILE', str(n_adj), f'{len(UPCOMING)} upcoming groups. The rest already sit in actuals.'),",
    "cards = [('MONTHLY ENTRIES ON FILE', str(n_adj), f'{len(GADJ)} adjustments, of which {len(UPCOMING)} run from October 2026 onward.'),")
rep("('ENTERED BY KAMS', str(n_kam_by), f'The other {n_sf} were entered by Sales Forecasting.'),", "('ENTERED BY KAMS', str(n_kam_by), f'Monthly entries. The other {n_sf} were entered by Sales Forecasting.'),")
rep("'Entries with 0% and 0 kWh change nothing. 9 of them are marked Confirmed defection.'", "'Entries with 0% and 0 kWh change nothing. 9 are marked Confirmed defection.'")
rep("rows = [[c['name'][:34], c['kam'].split(' ')[0], c['reason'][:22], c['last'], ('%g%%' % c['pct']).replace('-', MINUS), sg(c['dl'][1]), sg(c['dl'][2])] for c in FLAG_LIST]",
    "rows = [[c['name'][:34], c['kam'].split(' ')[0], c['reason'][:22], c['last'], (fmt_pct(c['pct']) if c['pct'] else ('%+,.0f kWh' % c['kwh']).replace('-', MINUS)), sg(c['dl'][1]), sg(c['dl'][2])] for c in FLAG_LIST]")
rep("rows, row_h=270000, size=8.5, left_cols=(0, 1, 2), total=True", "rows, row_h=232000, size=8, head_h=280000, left_cols=(0, 1, 2), total=True")
rep("callout(s, 274320, 5900000, 11650000, 420000, 'Alcoa.'", "callout(s, 274320, 5850000, 11650000, 420000, 'Alcoa.'")
rep("rows = [[c['name'][:30], c['kam'].split(' ')[0],", "rows = [[c['name'][:30], ('None' if c['kam'] == 'Not assigned' else c['kam'].split(' ')[0]),")
rep("rows[:12], row_h=330000, size=9, left_cols=(0, 1, 2, 3))", "rows, row_h=280000, size=8.5, head_h=290000, left_cols=(0, 1, 2, 3))")
open('kam_deck.py', 'w', encoding='utf-8').write(d)
print('patched')
