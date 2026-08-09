-- add_sales_sync_derived_formulas_occ_aug09.sql
-- Closes the Medium finding from the 2026-08-09 systematic-debugging audit:
-- Sales Platform's client-side _syncDerivedFormulas() reads component fpa_facts
-- rows, computes derived values in JS, then upserts them back in a separate
-- round trip -- a read-compute-write race with no version check, unlike every
-- other fpa_facts writer on this platform (fpa_facts_write_occ, fpa_recalc_version).
--
-- Fix: move the whole read-compute-write into one atomic Postgres function call
-- (one implicit transaction), eliminating the client-side race window entirely
-- instead of patching it with a per-row version check. Mirrors the platform's
-- own existing fpa_recalc_version/fpa_calc_derived pattern (same ON CONFLICT
-- source='formula' guard, same fpa_eval_expr evaluator, already proven safe in
-- production) but kept year-scoped to match _syncDerivedFormulas' exact current
-- behavior -- fpa_recalc_version recomputes every period in the version, which
-- is a broader scope change than this specific fix calls for.

create or replace function public.sales_sync_derived_formulas(p_version_id uuid, p_year integer)
returns integer
language plpgsql
security definer
set search_path to 'public'
as $$
declare
  v_locked boolean;
  v_per int;
  v_map jsonb;
  v_val numeric;
  f record;
  n integer := 0;
begin
  if not has_app('sales') then
    raise exception 'not authorized';
  end if;

  select is_locked into v_locked from fpa_versions where id = p_version_id;
  if v_locked is null then raise exception 'version % not found', p_version_id; end if;
  if v_locked then return 0; end if; -- matches current client behavior: skip silently if locked

  for v_per in
    select distinct ff.period_id from fpa_facts ff
    where ff.version_id = p_version_id
      and ff.period_id between p_year*100+1 and p_year*100+12
  loop
    select coalesce(jsonb_object_agg(ff.line_id, coalesce(ff.value,0)), '{}'::jsonb) into v_map
      from fpa_facts ff where ff.version_id = p_version_id and ff.period_id = v_per;

    for f in select df.line_id, df.calc_expr from fpa_derived_formulas df
             where df.is_active order by df.sort_order
    loop
      v_val := fpa_eval_expr(f.calc_expr, v_map);
      v_map := jsonb_set(v_map, array[f.line_id], to_jsonb(v_val));
      insert into fpa_facts(version_id, line_id, period_id, value, source)
      values (p_version_id, f.line_id, v_per, v_val, 'formula')
      on conflict (version_id, line_id, period_id) do update
        set value = excluded.value
        where fpa_facts.source = 'formula';
      n := n + 1;
    end loop;
  end loop;

  return n;
end;
$$;

grant execute on function public.sales_sync_derived_formulas(uuid, integer) to authenticated;
