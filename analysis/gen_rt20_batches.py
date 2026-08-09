import json

def esc(s):
    if s is None:
        return 'NULL'
    return "'" + str(s).replace("'", "''") + "'"

d = json.load(open('rt20_split_jun26.json', encoding='utf-8'))

rows = []
# Commercial (NAICS-having) individual accounts: (jps_ac, name, bucket, parish, kwh, rev, dem, fu, en, ipp, cust_chg, gct, cnt, segment)
for jps_ac, b in d['comm'].items():
    kwh, rev, dem, fu, en, ipp, cust_chg, gct = b['v']
    rows.append((jps_ac, b['name'], 'Commercial', b['parish'], kwh, rev, dem, fu, en, ipp, cust_chg, gct, None, 'Commercial'))

# Residential (no-NAICS) buckets
for key, v in d['res'].items():
    parish, bucket = key.split('||', 1)
    kwh, rev, gct, cnt = v
    rows.append(('', None, bucket, parish, kwh, rev, 0.0, 0.0, 0.0, 0.0, 0.0, gct, cnt, 'Residential'))

print('total rows:', len(rows))

BATCH = 400
n_batches = (len(rows) + BATCH - 1) // BATCH
for i in range(n_batches):
    chunk = rows[i*BATCH:(i+1)*BATCH]
    lines = []
    for r in chunk:
        jps_ac, name, bucket, parish, kwh, rev, dem, fu, en, ipp, cust_chg, gct, cnt, segment = r
        cnt_sql = str(int(cnt)) if cnt is not None else 'NULL'
        lines.append("(%s,2026,6,'RT20',%s,%s,%s,%.4f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%s,%s)" % (
            esc(jps_ac), esc(name), esc(bucket), esc(parish), kwh, rev, dem, fu, en, ipp, cust_chg, gct, cnt_sql, esc(segment)
        ))
    sql = ("insert into public.jps_actuals "
           "(jps_ac,year,month,rate_class,name,consumption_bucket,parish,kwh,revenue_jmd,demand_jmd,fuel_jmd,energy_jmd,ipp_jmd,customer_charge_jmd,gct_jmd,customer_count,segment) values\n"
           + ",\n".join(lines) + ";\n")
    with open('rt20_batch_%03d.sql' % i, 'w', encoding='utf-8') as f:
        f.write(sql)

print('wrote', n_batches, 'batch files')
