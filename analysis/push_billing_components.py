# -*- coding: utf-8 -*-
# Pushes account-level revenue-component data (kwh/fuel/energy/ipp/demand/
# customer-charge, from app_data2.json's 'accts') to the live jps_billing_components
# table, so Sales Explorer's live bootstrap (bootstrapExplorerData() in
# app2_template.html) picks up new months without a rebuild/deploy.
#
# Run after gen_appdata3.py (needs app_data2.json). Idempotent — upserts on
# (account_code, rate_class, month), same convention as the initial backfill:
# account_code is the "code~title" composite already used as accts[].id.
#
# Requires the same .env as monthly_loader.py (SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY).
import json, os, sys, requests

HERE = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(HERE)


def load_env(path):
    env = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def supabase_upsert(base_url, key, table, on_conflict, rows, batch=500):
    if not rows:
        print(f"  {table}: 0 rows, skipping")
        return
    url = f"{base_url}/rest/v1/{table}?on_conflict={on_conflict}"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }
    total = 0
    for i in range(0, len(rows), batch):
        chunk = rows[i:i + batch]
        r = requests.post(url, headers=headers, data=json.dumps(chunk), timeout=60)
        if r.status_code >= 300:
            print(f"  ERROR upserting {table} batch {i}-{i+len(chunk)}: {r.status_code} {r.text[:500]}")
            sys.exit(1)
        total += len(chunk)
        print(f"  {table}: upserted {total}/{len(rows)}")


def main():
    env = load_env(os.path.join(HERE, ".env"))
    base_url = env.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    key = env.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not base_url or not key:
        print("Missing SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY.")
        print(f"Create a .env file at {os.path.join(HERE, '.env')} with those two lines")
        print("(get the service_role key from Supabase dashboard -> Settings -> API).")
        sys.exit(1)

    D = json.load(open("app_data2.json", encoding="utf-8"))
    months = D["months"]
    rows = []
    for a in D["accts"]:
        code, title, pg = a["id"], a["c"], a.get("pg") or "UNMAPPED"
        name = a.get("n") or ""
        for j, mo in enumerate(months):
            kwh = a["kwh"][j] if j < len(a["kwh"]) else 0
            rev = a["rev"][j] if j < len(a["rev"]) else 0
            dem = a["dem"][j] if j < len(a["dem"]) else 0
            fuel = a["fuel"][j] if j < len(a["fuel"]) else 0
            energy = a["energy"][j] if j < len(a["energy"]) else 0
            ipp = a["ipp"][j] if j < len(a["ipp"]) else 0
            cust = a["cust"][j] if j < len(a["cust"]) else 0
            if not (kwh or rev):
                continue
            rows.append({
                "month": mo, "account_code": code, "name": name, "rate_class": title,
                "parish_group": pg, "kwh": kwh, "revenue_jmd": rev, "demand_jmd": dem,
                "fuel_jmd": fuel, "energy_jmd": energy, "ipp_jmd": ipp, "customer_charge_jmd": cust,
            })

    print(f"pushing {len(rows)} rows across {len(months)} months, {len(D['accts'])} accounts")
    supabase_upsert(base_url, key, "jps_billing_components", "account_code,rate_class,month", rows)
    print("Done.")


if __name__ == "__main__":
    main()
