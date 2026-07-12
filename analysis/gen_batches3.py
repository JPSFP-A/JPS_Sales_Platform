import json

with open('app_data2.json', encoding='utf-8') as f:
    D = json.load(f)

months = D['months']
accts = D['accts']
NEW_MONTHS = {'2025-01','2025-02','2025-03','2025-04','2025-06','2025-07','2025-08','2025-09'}
new_idx = [j for j, mo in enumerate(months) if mo in NEW_MONTHS]

def esc(s):
    if s is None:
        return 'NULL'
    return "'" + str(s).replace("'", "''") + "'"

rows = []
for a in accts:
    full_id, title, pg = a['id'], a['c'], a.get('pg') or 'UNMAPPED'
    name = a.get('n') or ''
    for j in new_idx:
        mo = months[j]
        kwh = a['kwh'][j] if j < len(a['kwh']) else 0
        rev = a['rev'][j] if j < len(a['rev']) else 0
        dem = a['dem'][j] if j < len(a['dem']) else 0
        fuel = a['fuel'][j] if j < len(a['fuel']) else 0
        energy = a['energy'][j] if j < len(a['energy']) else 0
        ipp = a['ipp'][j] if j < len(a['ipp']) else 0
        cust = a['cust'][j] if j < len(a['cust']) else 0
        if not (kwh or rev):
            continue
        rows.append((mo, full_id, name, title, pg, kwh, rev, dem, fuel, energy, ipp, cust))

print('rows to push (new months only):', len(rows))
print('distinct accounts:', len(set(r[1] for r in rows)))

BATCH = 400
n_batches = (len(rows) + BATCH - 1) // BATCH
for i in range(n_batches):
    chunk = rows[i*BATCH:(i+1)*BATCH]
    lines = []
    for r in chunk:
        vals = (esc(r[0]), esc(r[1]), esc(r[2]), esc(r[3]), esc(r[4]),
                r[5], r[6], r[7], r[8], r[9], r[10], r[11])
        lines.append("(%s,%s,%s,%s,%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f)" % vals)
    sql = ("insert into public.jps_billing_components "
           "(month,account_code,name,rate_class,parish_group,kwh,revenue_jmd,demand_jmd,fuel_jmd,energy_jmd,ipp_jmd,customer_charge_jmd) values\n"
           + ",\n".join(lines) +
           "\non conflict (account_code, rate_class, month) do update set name=excluded.name, "
           "parish_group=excluded.parish_group, kwh=excluded.kwh, revenue_jmd=excluded.revenue_jmd, "
           "demand_jmd=excluded.demand_jmd, fuel_jmd=excluded.fuel_jmd, energy_jmd=excluded.energy_jmd, "
           "ipp_jmd=excluded.ipp_jmd, customer_charge_jmd=excluded.customer_charge_jmd, updated_at=now();\n")
    with open('billing_batch3_%03d.sql' % i, 'w', encoding='utf-8') as f:
        f.write(sql)

print('wrote', n_batches, 'batch files (billing_batch3_000.sql .. billing_batch3_%03d.sql)' % (n_batches-1))
