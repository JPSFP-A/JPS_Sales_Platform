// Runs the Sales Platform's own Driver Forecast code (extracted verbatim from the HTML) on data pulled from the database.
// Output: monthly kWh by rate class for 2026-2028, as _dfcToLERows produces it (what the platform's LE shows).
const fs = require('fs');
const vm = require('vm');
const HTML = (process.env.PLATFORM_HTML || 'C:/Projects/Sales_Platform/JPS_Sales_Platform_v1.html');
const html = fs.readFileSync(HTML, 'utf8');

function fn(name) {
  const i = html.indexOf('function ' + name + '(');
  if (i < 0) throw new Error('missing ' + name);
  let j = html.indexOf('{', i), d = 0, k = j;
  for (; ; k++) {
    const c = html[k];
    if (c === '{') d++;
    else if (c === '}') { d--; if (d === 0) break; }
  }
  return html.slice(i, k + 1);
}
const names = ['_kl', '_isComm', '_sbAllActuals', '_dfcSegment', '_dfcMacroLookup', '_dfcOpAdjLookup', '_dfcOpEntries', '_dfcOpEffective', '_dfcSolarPct', '_dfcClosedThru',
  '_dfcDriverPcts', '_dfcComputeChain', '_dfcGetChain', '_dfcBuildIndices', '_dfcBuildCommAccounts', '_dfcCommCohortsForNonKam',
  '_dfcBuildResCohorts', '_dfcResetYearChainCache', '_dfcToLERows', '_coreDataReady'];

const main = JSON.parse(fs.readFileSync('pull.json', 'utf8'));
const nc = JSON.parse(fs.readFileSync('pull_nc.json', 'utf8'));
const num = (r, ks) => { ks.forEach(k => { if (r[k] != null) r[k] = Number(r[k]); }); return r; };
const CFG = (process.argv[2] || '').endsWith('.json') ? JSON.parse(fs.readFileSync(process.argv[2], 'utf8')) : JSON.parse(process.argv[2] || '{}');
const ASOF = CFG.asof || 9;
const act = main.act.map(r => num(r, ['year', 'month', 'kwh'])).filter(r => !(r.year === 2026 && r.month > ASOF));
const actNc = nc.act_nc.map(r => num(r, ['year', 'month', 'kwh'])).filter(r => !(r.year === 2026 && r.month > ASOF));
const bud = main.bud.concat(nc.bud_nc).map(r => num(r, ['year', 'month', 'kwh_budget']));

const ctx = {
  console, Math, Number, String, Object, Set,
  sbActuals: actNc, sbActualsComm: act, sbBudget: bud,
  sbKAM: main.kam, sbIndustries: main.ind, sbMacroAssum: main.macro, sbOpAdj: (CFG.noOp ? [] : main.opadj.filter(o => (!CFG.opadjBefore || String(o.created_at).slice(0, 10) <= CFG.opadjBefore) && !(CFG.drop || []).includes(o.jps_ac))).concat(CFG.extra || []), sbRateAssum: main.rate,
  sbNewCustomers: main.newc, sbBridgeDrivers: nc.bridge,
  curMonth: ASOF, curYear: 2026, FC_BUD_YEAR: 2026, FC_PY: 2025, sbConnected: true, _commDetailLoaded: true,
  _COMM_RCS: new Set(['RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70', 'BU']),
  _DFC_NORM_EXCLUDE: new Set(['302571-686496']), _DFC_OP_ROLLS: new Set(['Confirmed defection','Possible defection','Expansion','Renewal','Win-back']), _DFC_PLACEHOLDER_ACS: new Set(['Postpaid', 'Zero-Postpaid']),
  _dfcYearChainCache: {}, _dfcSolarPctCache: null, _dfcCacheSig: null, _dfcClosedThruKey: '', _dfcClosedThruCache: 0,
  _allActCache: null, _allActKey: '', LE_LIVE_LABEL: 'Live (Driver Forecast)', out: {},
};
vm.createContext(ctx);
vm.runInContext(names.map(fn).join('\n'), ctx);
vm.runInContext(`
const accts = {}; const cls = {};
for (const y of [2026, 2027, 2028]) {
  const rows = _dfcToLERows(y);
  rows.forEach(r => { (cls[y] = cls[y] || {})[r.rate_class] = (cls[y][r.rate_class] || Array(12).fill(0)); cls[y][r.rate_class][r.month - 1] += r.kwh_le; });
  rows.forEach(r => {
    if (String(r.jps_ac).includes('|')) return;
    const a = (accts[r.jps_ac] = accts[r.jps_ac] || {ac: r.jps_ac, name: r.name, rc: r.rate_class, ind: r.industry, k: {2026: Array(12).fill(0), 2027: Array(12).fill(0), 2028: Array(12).fill(0)}});
    a.k[y][r.month - 1] += r.kwh_le;
  });
}
out.accts = Object.values(accts); out.cls = cls;
out.closedThru = _dfcClosedThru(2026);
`, ctx);
fs.writeFileSync(CFG.out || 'kam_run.json', JSON.stringify(ctx.out));
console.log('accounts', ctx.out.accts.length, 'closedThru', ctx.out.closedThru);
