@echo off
REM ============================================================
REM  JPS Sales — one-command month-end.
REM  Prereqs (once): analysis\.env with SUPABASE_URL +
REM  SUPABASE_SERVICE_ROLE_KEY (for the loader), vercel CLI logged in.
REM  Monthly: drop the new "Check Consumption..." file(s) in this folder
REM  and the new "Billing Details Report ... <Mon> <YYYY>.xlsx" in
REM  Downloads (or here), then double-click this.
REM
REM  Steps: 1) upsert demand + special-adjustment corrections to Supabase
REM         2) incremental billing scan (only NEW months are processed)
REM         3) rebuild explorer dataset + top movers
REM         4) push account-level revenue components DIRECTLY to jps_actuals
REM            (the shared table both Sales Explorer and Sales Platform read
REM            from — jps_billing_components is retired) + refresh the
REM            materialized views Sales Platform's RPCs read from, so the new
REM            month is visible immediately instead of waiting for the
REM            4:30am nightly cron.
REM            NOTE: this does NOT push RT10/RT20 residential (Explorer's own
REM            pipeline has never computed that grain — see analysis notes)
REM            and does NOT populate gct_jmd (revenue_jmd itself is already
REM            correct/net-of-GCT; gct_jmd is a reconciliation aid, backfilled
REM            separately via gct_correction_scan.py when needed).
REM         5) publish the (data-free) template
REM         6) deploy to salesanalysis.jmfinancelab.com
REM  Fails loud at the first broken step — nothing deploys half-built.
REM ============================================================
cd /d "%~dp0"

echo [1/7] Supabase loaders (demand + special adjustments)...
JPS_Monthly_Loader.exe || goto :err

echo [2/7] Billing scan (incremental — already-loaded months skip)...
python corrected_scan.py || goto :err

echo [3/7] Rebuild explorer dataset...
python gen_appdata3.py || goto :err

echo [4/7] Top variance movers...
python build_top_movers.py || goto :err

echo [5/7] Push revenue components to jps_actuals (shared live table) + refresh views...
python push_actuals_direct.py || goto :err

echo [6/7] Publish template...
python build_full.py || goto :err

echo [7/7] Deploy...
copy /Y sales_explorer.html ..\salesanalysis_deploy\index.html >nul || goto :err
copy /Y jps-auth.js ..\salesanalysis_deploy\jps-auth.js >nul || goto :err
cd ..\salesanalysis_deploy
call vercel --prod --yes || goto :err
cd /d "%~dp0"

echo.
echo ==== MONTH-END COMPLETE — check https://salesanalysis.jmfinancelab.com (data stamp in the header should show the new month) ====
pause
exit /b 0

:err
echo.
echo ==== FAILED at the step above — NOTHING was deployed. Fix and rerun. ====
pause
exit /b 1
