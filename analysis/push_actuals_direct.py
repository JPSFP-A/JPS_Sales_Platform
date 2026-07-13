# -*- coding: utf-8 -*-
# Pushes account-level revenue-component data (kwh/fuel/energy/ipp/demand/
# customer-charge, from app_data2.json's 'accts') directly to the live jps_actuals
# table — the shared table both Sales Explorer and Sales Platform read from
# (jps_billing_components, this script's predecessor, is retired).
#
# Run after gen_appdata3.py (needs app_data2.json). Idempotent — upserts on
# (jps_ac, year, month, rate_class), matching jps_actuals' own convention.
#
# Two things this deliberately does NOT do, both by design:
#   - gct_jmd is left NULL for newly-pushed rows. revenue_jmd from app_data2.json
#     is already net-of-GCT (Explorer's own methodology has always used
#     net_revenue, never the GCT-inclusive net_billed_revenue) so the REVENUE
#     FIGURE ITSELF IS CORRECT without gct_jmd — that column is only a
#     reconciliation aid. Backfilling it needs a separate GCT-specific scan
#     (see gct_correction_scan.py) against the raw extracts, which is slower
#     and can be run periodically rather than every month-end.
#   - RT10/RT20 residential is NOT pushed here — Explorer's own pipeline has
#     never computed per-account/per-bucket data for those two classes at the
#     grain jps_actuals expects; that data comes from a separate manual export
#     process (see the "prepaid file"/bucketed-export conversation).
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


def refresh_materialized_views(base_url, key):
    # jps_actuals' consumers (get_comm_actuals, get_res_actuals, get_rc_agg, etc.)
    # read from materialized views, not the live table - a write here is invisible
    # to Sales Platform until this runs (or the 4:30am nightly cron catches up).
    url = f"{base_url}/rest/v1/rpc/refresh_sales_mvs"
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    r = requests.post(url, headers=headers, data="{}", timeout=120)
    if r.status_code >= 300:
        print(f"  WARNING: refresh_sales_mvs failed: {r.status_code} {r.text[:500]}")
        print("  Data is pushed but Sales Platform won't see it until the next nightly refresh (4:30am) or a manual retry.")
    else:
        print("  refresh_sales_mvs: OK")


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
        full_id, title, pg = a["id"], a["c"], a.get("pg") or "UNMAPPED"
        if "~" not in full_id:
            continue
        jps_ac = full_id.split("~")[0]
        # jps_actuals keeps the raw "RT60-ST" label (not the canonicalized "RT60"
        # gen_appdata3.py's baseT() produces) - pushing the canonicalized value
        # here creates a second, duplicate set of rows under a different spelling
        # of the same rate class (this happened once already this session - see
        # the Jul-12 RT60/RT60-ST dedup fix - don't repeat it).
        rate_class = "RT60-ST" if title == "RT60" else title
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
            yr, mth = mo.split("-")
            rows.append({
                "jps_ac": jps_ac, "year": int(yr), "month": int(mth), "name": name,
                "rate_class": rate_class, "parish": pg, "consumption_bucket": "Commercial",
                "kwh": kwh, "revenue_jmd": rev, "demand_jmd": dem,
                "fuel_jmd": fuel, "energy_jmd": energy, "ipp_jmd": ipp, "customer_charge_jmd": cust,
                "customer_count": 1,
            })

    print(f"pushing {len(rows)} rows across {len(months)} months, {len(D['accts'])} accounts")
    # Must match jps_actuals' actual unique index exactly (verified via pg_indexes) -
    # a 4-column on_conflict here would be rejected by PostgREST outright, or worse,
    # silently create duplicate rows if it happened to match some other constraint.
    supabase_upsert(base_url, key, "jps_actuals", "year,month,jps_ac,rate_class,parish,consumption_bucket", rows)
    print("Refreshing materialized views so Sales Platform sees this immediately...")
    refresh_materialized_views(base_url, key)
    print("Done.")


if __name__ == "__main__":
    main()
