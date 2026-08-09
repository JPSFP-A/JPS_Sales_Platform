# Splits RT20 (General Service) for June 2026 per business rule: customers WITH a
# NAICS Code are real registered businesses -> individual commercial accounts
# (premise-level, matching the RT40+ pattern). Customers WITHOUT a NAICS Code are
# residential-style -> bucketed by kWh consumption range + parish, matching the
# scheme already used for RT10 (data (6).xlsx export): <Zero, Zero, <150, 150>350,
# 350>550, 550>750, 750>950, over 950.
import json

def num(v):
    if v is None:
        return 0.0
    v = str(v).strip()
    if v == '':
        return 0.0
    try:
        return float(v)
    except ValueError:
        return 0.0

def bucket_of(kwh):
    if kwh < 0:
        return '<Zero'
    if kwh == 0:
        return 'Zero'
    if kwh < 150:
        return '<150'
    if kwh < 350:
        return '150>350'
    if kwh < 550:
        return '350>550'
    if kwh < 750:
        return '550>750'
    if kwh < 950:
        return '750>950'
    return 'over 950'

comm = {}   # jps_ac -> {name, v:[kwh,rev,dem,fuel,energy,ipp,cust,gct]}
res = {}    # (parish, bucket) -> [kwh,rev,gct,cust_count]

with open('Billing Details Report_Jun 2026.xlsx', encoding='latin-1', errors='replace') as f:
    hdr = None
    idx = None
    n_total = 0
    n_billed = 0
    for line in f:
        r = line.rstrip('\n').split('\t')
        if r and r[0] == 'Cust_Code':
            hdr = r
            idx = {name: i for i, name in enumerate(hdr)}
            continue
        if hdr is None:
            continue
        code = r[idx['Cust_Code']] if idx.get('Cust_Code', -1) < len(r) else None
        if code in (None, '', 'Cust_Code'):
            continue
        rc = r[idx['Srat_Code']] if idx.get('Srat_Code', -1) < len(r) else ''
        if rc != 'RT20':
            continue
        n_total += 1
        cb = r[idx['cust_billed']] if 'cust_billed' in idx and idx['cust_billed'] < len(r) else None
        if cb is not None and str(cb).strip() in ('0', '0.0'):
            continue
        n_billed += 1

        naics = (r[idx['NAICS Code']] if 'NAICS Code' in idx and idx['NAICS Code'] < len(r) else '').strip()
        prem = str(r[idx['Prem_Code']] or '').strip() if idx.get('Prem_Code', -1) < len(r) else ''
        parish = str(r[idx['Parish']] or '').strip() if idx.get('Parish', -1) < len(r) else 'UNMAPPED'
        name = str(r[idx['Name']] or '').strip() if idx.get('Name', -1) < len(r) else ''

        kwh = num(r[idx['net_kwh_billed_consump']]) if 'net_kwh_billed_consump' in idx else 0.0
        rev = num(r[idx['net_revenue']]) if 'net_revenue' in idx else 0.0
        gct = num(r[idx['GCT']]) if 'GCT' in idx else 0.0
        dem = (num(r[idx['KVAP_KVA_Demand']]) if 'KVAP_KVA_Demand' in idx else 0.0)
        en = (num(r[idx['KWHP_KWH_Energy']]) if 'KWHP_KWH_Energy' in idx else 0.0) + \
             (num(r[idx['KWHL_Energy']]) if 'KWHL_Energy' in idx else 0.0) + \
             (num(r[idx['KWHO_Energy']]) if 'KWHO_Energy' in idx else 0.0)
        fu = (num(r[idx['fuel']]) if 'fuel' in idx else 0.0) + \
             (num(r[idx['FuelOffPeak']]) if 'FuelOffPeak' in idx else 0.0) + \
             (num(r[idx['FuelPartialPeak']]) if 'FuelPartialPeak' in idx else 0.0) + \
             (num(r[idx['FuelOnPeak']]) if 'FuelOnPeak' in idx else 0.0)
        ipp = num(r[idx['IPP_Charge']]) if 'IPP_Charge' in idx else 0.0
        cust_chg = num(r[idx['Cust_Charge']]) if 'Cust_Charge' in idx else 0.0

        if naics:
            if not prem:
                continue
            jps_ac = code + '-' + prem
            b = comm.get(jps_ac)
            if b is None:
                b = comm[jps_ac] = {'name': name, 'parish': parish, 'v': [0.0]*8}
            v = b['v']
            v[0] += kwh; v[1] += rev; v[2] += dem; v[3] += fu; v[4] += en; v[5] += ipp; v[6] += cust_chg; v[7] += gct
        else:
            bucket = bucket_of(kwh)
            key = (parish, bucket)
            b = res.get(key)
            if b is None:
                b = res[key] = [0.0, 0.0, 0.0, 0]
            b[0] += kwh; b[1] += rev; b[2] += gct; b[3] += 1

print('RT20 raw rows:', n_total, '| billed (cust_billed<>0):', n_billed)
print('commercial (NAICS) accounts:', len(comm))
print('residential bucket cells:', len(res))

json.dump({'comm': comm, 'res': {f'{k[0]}||{k[1]}': v for k, v in res.items()}},
          open('rt20_split_jun26.json', 'w'))
