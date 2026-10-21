// Runs the Sales Platform's own Driver Forecast code (extracted verbatim from the HTML) on data pulled from the database.
// Output: monthly kWh by rate class for 2026-2028, as _dfcToLERows produces it (what the platform's LE shows).
const fs = require('fs');
const vm = require('vm');
const HTML = 'C:/Projects/Sales_Platform/JPS_Sales_Platform_v1.html';
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
const names = ['_kl', '_isComm', '_sbAllActuals', '_dfcSegment', '_dfcMacroLookup', '_dfcOpAdjLookup', '_dfcSolarPct', '_dfcClosedThru',
  '_dfcDriverPcts', '_dfcComputeChain', '_dfcGetChain', '_dfcBuildIndices', '_dfcBuildCommAccounts', '_dfcCommCohortsForNonKam',
  '_dfcBuildResCohorts', '_dfcResetYearChainCache', '_dfcToLERows', '_coreDataReady'];

const main = JSON.parse(fs.readFileSync('pull.json', 'utf8'));
const nc = JSON.parse(fs.readFileSync('pull_nc.json', 'utf8'));
const num = (r, ks) => { ks.forEach(k => { if (r[k] != null) r[k] = Number(r[k]); }); return r; };
const act = main.act.map(r => num(r, ['year', 'month', 'kwh']));
const actNc = nc.act_nc.map(r => num(r, ['year', 'month', 'kwh']));
const bud = main.bud.concat(nc.bud_nc).map(r => num(r, ['year', 'month', 'kwh_budget']));

const ctx = {
  console, Math, Number, String, Object, Set,
  sbActuals: actNc, sbActualsComm: act, sbBudget: bud,
  sbKAM: main.kam, sbIndustries: main.ind, sbMacroAssum: main.macro, sbOpAdj: main.opadj, sbRateAssum: main.rate,
  sbNewCustomers: main.newc, sbBridgeDrivers: nc.bridge,
  curMonth: 9, curYear: 2026, FC_BUD_YEAR: 2026, FC_PY: 2025, sbConnected: true, _commDetailLoaded: true,
  _COMM_RCS: new Set(['RT20', 'RT40', 'RT50', 'RT60-ST', 'RT70', 'BU']),
  _DFC_NORM_EXCLUDE: new Set(['302571-686496']), _DFC_PLACEHOLDER_ACS: new Set(['Postpaid', 'Zero-Postpaid']),
  _dfcYearChainCache: {}, _dfcSolarPctCache: null, _dfcCacheSig: null, _dfcClosedThruKey: '', _dfcClosedThruCache: 0,
  _allActCache: null, _allActKey: '', LE_LIVE_LABEL: 'Live (Driver Forecast)', out: {},
};
vm.createContext(ctx);
vm.runInContext(names.map(fn).join('\n'), ctx);
vm.runInContext(`
for (const y of [2026, 2027, 2028]) {
  const rows = _dfcToLERows(y);
  const byClass = {};
  rows.forEach(r => { const rc = r.rate_class; (byClass[rc] = byClass[rc] || Array(12).fill(0))[r.month - 1] += r.kwh_le; });
  out[y] = byClass;
}
out.closedThru = _dfcClosedThru(2026);
`, ctx);
fs.writeFileSync('engine_out.json', JSON.stringify(ctx.out, null, 1));
for (const y of [2026, 2027, 2028]) {
  const tot = Array(12).fill(0);
  Object.values(ctx.out[y]).forEach(a => a.forEach((v, i) => tot[i] += v));
  console.log(y, (tot.reduce((a, b) => a + b, 0) / 1e6).toFixed(1), 'GWh', Object.keys(ctx.out[y]).join(','));
}
console.log('closedThru', ctx.out.closedThru);
