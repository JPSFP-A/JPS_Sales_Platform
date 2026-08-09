-- lockdown_jps_actuals_budget_anon_aug09.sql
-- Closes anon-readable access to jps_actuals (543,250 rows: customer-level billing
-- actuals) and jps_budget (111,682 rows: customer/rate-class budget), found live
-- during the 2026-08-09 systematic-debugging audit of Sales Platform + Sales Explorer.
--
-- Root cause: jps_actuals_anon_select / jps_budget_read grant anon SELECT with
-- qual=true. RLS policies OR together, so these alone re-open both tables to the
-- public anon key regardless of the correctly-scoped authenticated-only policies
-- sitting next to them.
--
-- Safe to apply: Sales Explorer's _SB client (salesanalysis_deploy/index.html:139-140)
-- already passes JpsAuth.clientOptions(), which restores a real Supabase Auth session
-- from the shared jps_sso_v1 cookie when the user is logged into any JPS platform app.
-- Logged-in users keep working via the existing authenticated-only policies below;
-- only genuinely-unauthenticated requests lose access, which is the intended behavior.
--
-- Verified NOT to affect:
--   - jps_actuals authenticated reads -> covered by jps_actuals_auth_select (unchanged)
--   - jps_actuals admin writes        -> covered by jps_actuals_write (unchanged)
--   - jps_budget authenticated reads/writes -> covered by jps_budget_auth_all (unchanged, cmd=ALL)
--   - service_role ETL/upload scripts -> RLS does not apply to service_role

begin;

drop policy if exists jps_actuals_anon_select on public.jps_actuals;
drop policy if exists jps_budget_read on public.jps_budget;

revoke select on public.jps_actuals from anon;
revoke select on public.jps_budget from anon;

commit;

-- Post-apply verification (run separately, not part of the transaction):
--   curl "https://bhrswnbenkvflpdjhfpa.supabase.co/rest/v1/jps_actuals?select=jps_ac&limit=1" -H "apikey: <anon key>"
--   curl "https://bhrswnbenkvflpdjhfpa.supabase.co/rest/v1/jps_budget?select=jps_ac&limit=1"  -H "apikey: <anon key>"
--   Both should return [] (empty array), not rows.
--   Then load salesanalysis.jmfinancelab.com while logged into any JPS platform app
--   and confirm the Answer tab budget column + account drill-down modal still populate.
