-- Driver Forecast / Macro Assumptions / Adjustment Log schema
-- Apply via Supabase MCP the moment the connector is back (execute_sql or apply_migration).
-- Project: bhrswnbenkvflpdjhfpa

-- ============================================================
-- jps_macro_assumptions
-- Segment/industry-level driver inputs, monthly, multi-year.
-- driver_type='macro'                -> segment='commercial' | 'residential'
-- driver_type='weather'              -> segment=null (single global row)
-- driver_type='seasonality_residential' -> segment=null (single global row, residential only)
-- driver_type='industry'             -> segment=<industry name>, matches jps_industries.industry
-- ============================================================
create table if not exists public.jps_macro_assumptions (
  id bigint generated always as identity primary key,
  driver_type text not null check (driver_type in ('macro','weather','seasonality_residential','industry')),
  segment text,
  year smallint not null,
  month smallint not null check (month between 1 and 12),
  value_pct numeric not null default 0,
  updated_by text,
  updated_at timestamptz not null default now(),
  unique (driver_type, segment, year, month)
);
alter table public.jps_macro_assumptions enable row level security;
do $$ declare r record; begin
  for r in select policyname from pg_policies where schemaname='public' and tablename='jps_macro_assumptions'
  loop execute format('drop policy if exists %I on public.jps_macro_assumptions', r.policyname); end loop;
end $$;
create policy jps_macro_assumptions_select on public.jps_macro_assumptions
  for select using (auth.role()='authenticated');
create policy jps_macro_assumptions_write on public.jps_macro_assumptions
  for all using (auth.role()='authenticated') with check (auth.role()='authenticated');

-- ============================================================
-- jps_operational_adjustments
-- Append-only audit log. Current value per (jps_ac,year,month) = most recent row.
-- Non-zero operational_pct requires a reason_code + justification (enforced by CHECK).
-- Manual kwh_delta does not require a reason on its own.
-- ============================================================
create table if not exists public.jps_operational_adjustments (
  id bigint generated always as identity primary key,
  jps_ac text not null,
  year smallint not null,
  month smallint not null check (month between 1 and 12),
  operational_pct numeric not null default 0,
  manual_kwh numeric not null default 0,
  reason_code text check (reason_code in ('Renewal','Expansion','Confirmed defection','Possible defection','Win-back','Operational disruption','Other')),
  justification text,
  created_by text,
  created_at timestamptz not null default now(),
  constraint operational_needs_reason check (
    operational_pct = 0
    or (reason_code is not null and justification is not null and length(trim(justification)) > 0)
  )
);
alter table public.jps_operational_adjustments enable row level security;
do $$ declare r record; begin
  for r in select policyname from pg_policies where schemaname='public' and tablename='jps_operational_adjustments'
  loop execute format('drop policy if exists %I on public.jps_operational_adjustments', r.policyname); end loop;
end $$;
create policy jps_operational_adjustments_select on public.jps_operational_adjustments
  for select using (auth.role()='authenticated');
create policy jps_operational_adjustments_insert on public.jps_operational_adjustments
  for insert with check (auth.role()='authenticated');
-- deliberately no update/delete policy: history is immutable, corrections are new rows

create or replace view public.jps_operational_adjustments_current as
select distinct on (jps_ac, year, month) *
from public.jps_operational_adjustments
order by jps_ac, year, month, created_at desc;

-- ============================================================
-- jps_forecast_new_customers
-- "Add customer" on-ramp: no real actuals yet, expected_kwh seeds Base
-- until the account has 3 real months of jps_actuals to roll forward from.
-- ============================================================
create table if not exists public.jps_forecast_new_customers (
  id bigint generated always as identity primary key,
  jps_ac text not null unique,
  name text not null,
  rate_class text not null,
  parish text,
  industry text,
  kam text,
  expected_kwh numeric not null default 0,
  start_year smallint not null,
  start_month smallint not null check (start_month between 1 and 12),
  created_by text,
  created_at timestamptz not null default now()
);
alter table public.jps_forecast_new_customers enable row level security;
do $$ declare r record; begin
  for r in select policyname from pg_policies where schemaname='public' and tablename='jps_forecast_new_customers'
  loop execute format('drop policy if exists %I on public.jps_forecast_new_customers', r.policyname); end loop;
end $$;
create policy jps_forecast_new_customers_select on public.jps_forecast_new_customers
  for select using (auth.role()='authenticated');
create policy jps_forecast_new_customers_write on public.jps_forecast_new_customers
  for all using (auth.role()='authenticated') with check (auth.role()='authenticated');

grant select, insert, update on public.jps_macro_assumptions to authenticated;
grant select, insert on public.jps_operational_adjustments to authenticated;
grant select on public.jps_operational_adjustments_current to authenticated;
grant select, insert, update on public.jps_forecast_new_customers to authenticated;
