# -*- coding: utf-8 -*-
# Rework the KAM model, deck, workbook and email for the roll-forward engine.
m = open('kam_model.py', encoding='utf-8').read()
i = m.index('# end-date flags'); j = m.index('PIPE = [')
new_block = '''# how each adjustment applies on the roll-forward engine
ROLLS = {'Confirmed defection', 'Possible defection', 'Expansion', 'Renewal', 'Win-back'}
for g in GADJ:
    g['kind'] = 'No value' if not (g['pct'] or g['kwh']) else ('Rolls forward' if g['reason'] in ROLLS else 'Month only')
def kind_customers(kind):
    out = collections.OrderedDict()
    for g in GADJ:
        if g['kind'] != kind or not g['kam']: continue
        k = (g['kam'], norm(g['name']) or g['ac'])
        c = out.setdefault(k, dict(kam=g['kam'], name=g['name'] or g['ac'], accounts=set(), items=[], reasons=set(), first=g['first'], last=g['last'], by=set()))
        c['accounts'].add(g['ac']); c['reasons'].add(g['reason'] or 'Not stated'); c['by'].add(g['by'])
        c['first'] = min(c['first'], g['first']); c['last'] = max(c['last'], g['last'])
        tx = adj_text(g)
        if tx not in c['items']: c['items'].append(tx)
    for c in out.values():
        c['eff'] = [sum(effect[ac][i] for ac in c['accounts'] if ac in effect) for i in range(3)]
    return list(out.values())
ROLL_CUST = sorted(kind_customers('Rolls forward'), key=lambda c: -abs(c['eff'][2]))
OP_CUST = sorted(kind_customers('Month only'), key=lambda c: -abs(c['eff'][0]))

'''
m = m[:i] + new_block + m[j:]
m = m.replace("EXT = json.load(open('kam_run_extend.json')); IX = {a['ac']: a for a in EXT['accts']}\n", "")
m = m.replace("    print([ (f['name'][:20], f['last'], [round(v,1) for v in f['dl']]) for f in FLAG_LIST[:5]])", "    print('rolling customers', len(ROLL_CUST), 'month-only customers', len(OP_CUST))")
m = m.replace("print('customers', len(CUST), 'upcoming groups', len(UPCOMING), 'flag customers', len(FLAG_LIST))", "print('customers', len(CUST), 'upcoming groups', len(UPCOMING))")
open('kam_model.py', 'w', encoding='utf-8').write(m)

# ---------------- deck ----------------
d = open('kam_deck.py', encoding='utf-8').read()
def rep(a, b):
    global d
    assert a in d, a[:70]
    d = d.replace(a, b, 1)
rep("('2  CHECK THE END DATES', f'{len(FLAG_LIST)} customers', 'have a loss adjustment that stops before December 2028. The forecast drifts back once an entry ends. Tell us which losses are permanent.'),",
    "('2  CONFIRM WHAT IS PERMANENT', f'{len(ROLL_CUST)} customers', 'have a defection, expansion or renewal entry that now carries forward to December 2028 until the next entry. Tell us which are permanent and which should end.'),")
# register slide: mechanism box
i = d.index("nwc = accts['100012-100248']"); j = d.index("# ================= 8 end dates")
box = '''n_roll = len({g['ac'] for g in GADJ if g['kind'] == 'Rolls forward'}); n_ops = len({g['ac'] for g in GADJ if g['kind'] == 'Month only'})
box(s, 5750000, 3850000, 6175000, 2000000, 'HOW AN ENTRY WORKS', [[('Defection, expansion, renewal and win-back entries carry forward. ', True, NAVY), ('They stay in force from the month entered until the next entry for the account. Enter 0% to end one.', False, BLACK)],
    [(f'Operational disruption and Other apply only to the months entered, so an outage that runs longer needs the extra months entered. {n_roll} accounts carry a rolling entry and {n_ops} have month-only entries.', False, BLACK)],
    [('Check that each rolling entry is meant to last to December 2028.', True, NAVY)]], 10.5)

'''
d = d[:i] + box + d[j:]
# slide 8
i = d.index("# ================= 8 end dates"); j = d.index("# ================= 9, 10 decisions")
s8 = '''# ================= 8 rolling entries =================
ent = ROLL_CUST[:12]
tot_roll = [sum(c['eff'][k] for c in ROLL_CUST) for k in range(3)]
s = new_slide('Entries That Now Run Forward', f'{len(ROLL_CUST)} customers carry an entry to December 2028; together they take {abs(tot_roll[2]):.0f} GWh from FY2028',
              'Effect on the forecast, GWh, for the whole customer. Each stays in force until the next entry for the account. Confirm it is permanent, or tell us when it ends.')
rows = [[c['name'][:32], c['kam'].split(' ')[0], ', '.join(sorted(c['reasons']))[:24], t_label(c['first']), '; '.join(c['items'][:1])[:34], sg(c['eff'][1]), sg(c['eff'][2])] for c in ent]
table(s, 274320, 1950000, 11650000, [2.8, 1.1, 1.9, 0.9, 2.2, 1.0, 1.0], ['Customer', 'KAM', 'Reason', 'From', 'Adjustment', 'FY2027', 'FY2028'], rows, row_h=262000, size=8.5, head_h=290000, left_cols=(0, 1, 2, 4), colors=[[None, None, None, None, None, col(c['eff'][1]), col(c['eff'][2])] for c in ent])
opw = [c for c in OP_CUST if 'windalco' in c['name'].lower()]
callout(s, 274320, 5500000, 11650000, 760000, 'Month-only entries.', f'Operational disruption entries apply only to the months entered, so the forecast returns to normal afterwards. Windalco\\'s turbine outage is entered for November and December 2026 only; if it runs longer, the extra months need entering. {len(OP_CUST)} customers have month-only entries.', 10.5)

'''
d = d[:i] + s8 + d[j:]
open('kam_deck.py', 'w', encoding='utf-8').write(d)

# ---------------- workbook ----------------
w = open('kam_workbook.py', encoding='utf-8').read()
def repw(a, b):
    global w
    assert a in w, a[:70]
    w = w.replace(a, b, 1)
repw("('2. End dates sheet: an adjustment applies only to the months entered. For a loss or gain that is permanent, tell us the date it starts and we will enter every month to December 2028.', False),",
     "('2. Permanent or temporary sheet: defection, expansion, renewal and win-back entries now carry forward until the next entry for the account (enter 0% to end one). Operational disruption entries apply only to the months entered. Tell us which are permanent and when any should end.', False),")
repw("('End dates: adjustments that stop before December 2028 and what running them on would change.', False),", "('Permanent or temporary: how each customer\\'s entries apply and what they do to the forecast.', False),")
# adjustments sheet: add 'How it applies'
repw("heads = ['KAM', 'Customer', 'Account', 'Month', 'Adjustment %', 'Manual kWh', 'Reason', 'Justification', 'Entered by', 'Date entered', 'Status', 'Account effect FY2027 (GWh)', 'Account effect FY2028 (GWh)', 'KAM response', 'New % or kWh', 'Months it applies to', 'Comment']",
     "heads = ['KAM', 'Customer', 'Account', 'Month', 'Adjustment %', 'Manual kWh', 'Reason', 'How it applies', 'Justification', 'Entered by', 'Date entered', 'Status', 'Account effect FY2027 (GWh)', 'Account effect FY2028 (GWh)', 'KAM response', 'New % or kWh', 'Months it applies to', 'Comment']")
repw("[20, 34, 17, 10, 12, 12, 20, 60, 18, 12, 18, 14, 14, 14, 13, 20, 40])", "[20, 34, 17, 10, 12, 12, 20, 18, 60, 18, 12, 18, 14, 14, 14, 13, 20, 40])")
repw("""    A_.cell(i, 7, a['reason'] or 'Not stated'); A_.cell(i, 8, a['just']); A_.cell(i, 9, a['by_name'] or 'Sales Forecasting'); A_.cell(i, 10, a['created'])
    A_.cell(i, 11, 'Upcoming' if t >= 10 else 'Already in actuals')
    if a['ac'] in effect:
        A_.cell(i, 12, effect[a['ac']][1]).number_format = '+#,##0.00;-#,##0.00;0.00'; A_.cell(i, 13, effect[a['ac']][2]).number_format = '+#,##0.00;-#,##0.00;0.00'
    for j in range(14, 18): A_.cell(i, j).fill = fill(INPUT)
    for j in range(1, 14): A_.cell(i, j).font = F()
    A_.cell(i, 8).alignment = Alignment(wrap_text=True, vertical='top')""",
"""    A_.cell(i, 7, a['reason'] or 'Not stated')
    A_.cell(i, 8, 'No value' if not (a['pct'] or a['kwh']) else ('Rolls forward' if a['reason'] in ROLLS else 'Months entered only'))
    A_.cell(i, 9, a['just']); A_.cell(i, 10, a['by_name'] or 'Sales Forecasting'); A_.cell(i, 11, a['created'])
    A_.cell(i, 12, 'Upcoming' if t >= 10 else 'Already in actuals')
    if a['ac'] in effect:
        A_.cell(i, 13, effect[a['ac']][1]).number_format = '+#,##0.00;-#,##0.00;0.00'; A_.cell(i, 14, effect[a['ac']][2]).number_format = '+#,##0.00;-#,##0.00;0.00'
    for j in range(15, 19): A_.cell(i, j).fill = fill(INPUT)
    for j in range(1, 15): A_.cell(i, j).font = F()
    A_.cell(i, 9).alignment = Alignment(wrap_text=True, vertical='top')""")
repw("dv = DataValidation(type='list', formula1='\"Keep,Change,Remove\"', allow_blank=True); A_.add_data_validation(dv); dv.add('N5:N%d' % (4 + len(order)))\nA_.freeze_panes = 'D5'; A_.auto_filter.ref = 'A4:Q%d' % (4 + len(order))",
     "dv = DataValidation(type='list', formula1='\"Keep,Change,Remove\"', allow_blank=True); A_.add_data_validation(dv); dv.add('O5:O%d' % (4 + len(order)))\nA_.freeze_panes = 'D5'; A_.auto_filter.ref = 'A4:R%d' % (4 + len(order))")
# end dates sheet -> permanent or temporary
i = w.index("# ---------------- end dates ----------------"); j = w.index("# ---------------- new customers ----------------")
ps = '''# ---------------- permanent or temporary ----------------
E_ = wb.create_sheet('Permanent or temporary')
title(E_, 'How each customer\\'s entries apply', 'Rolling entries stay in force until the next entry for the account (0% ends one). Months-only entries apply to the months entered. Effect is the whole customer, GWh.')
header(E_, 4, ['KAM', 'Customer', 'How it applies', 'Reason', 'From', 'Last month entered', 'Adjustment', 'Effect FY2026', 'Effect FY2027', 'Effect FY2028', 'Permanent? (Yes / No / Until when)', 'Comment'], [20, 36, 20, 24, 10, 14, 34, 12, 12, 12, 24, 40])
r_ = 5
for kind, lst in (('Rolls forward', ROLL_CUST), ('Months entered only', OP_CUST)):
    for c in lst:
        E_.cell(r_, 1, c['kam']); E_.cell(r_, 2, c['name']); E_.cell(r_, 3, kind); E_.cell(r_, 4, ', '.join(sorted(c['reasons']))); E_.cell(r_, 5, t_label(c['first'])); E_.cell(r_, 6, t_label(c['last']))
        E_.cell(r_, 7, '; '.join(c['items'][:2]))
        for j in range(3): E_.cell(r_, 8 + j, c['eff'][j]).number_format = '+#,##0.00;-#,##0.00;0.00'
        E_.cell(r_, 11).fill = fill(INPUT); E_.cell(r_, 12).fill = fill(INPUT)
        for j in range(1, 11): E_.cell(r_, j).font = F()
        r_ += 1

'''
w = w[:i] + ps + w[j:]
open('kam_workbook.py', 'w', encoding='utf-8').write(w)
print('patched model, deck, workbook')
