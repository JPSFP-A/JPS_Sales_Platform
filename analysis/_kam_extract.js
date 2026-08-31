// Extract the Key Account Review dataset from the live engine.
//
// Run this in the browser console on https://sales.jmfinancelab.com with the
// commercial detail loaded (visit Commercial once first). It downloads
// _kam_data.json, which _build_kam_review.py renders.
//
// The engine is the only place the account chains exist, so the numbers are
// taken from it rather than recomputed in Python. Reimplementing the chain
// would give two answers to the same question and one of them would drift.
(function () {
  if (typeof _dfcBuildIndices !== 'function') { console.error('Engine not loaded.'); return; }
  if (!_commDetailLoaded) { console.error('Open the Commercial page first so account detail loads.'); return; }

  const norm = s => String(s || '').toUpperCase().replace(/[^A-Z0-9]+/g, ' ').trim();
  const idx = _dfcBuildIndices();
  const ALL = _dfcBuildCommAccounts(2027).filter(a => a.rate_class !== 'EV');
  const A = ALL.filter(a => a.kam);

  const kam = {}, mv = [];
  A.forEach(a => {
    const meta = { rate_class: a.rate_class, industry: a.industry, bucket: a.consumption_bucket || null };
    const t = {};
    [2026, 2027, 2028].forEach(yr => {
      const ch = _dfcGetChain(idx, a.ac, true, meta, a.ac, yr, null);
      let s = 0; for (let m = 1; m <= 12; m++) s += ch[m] ? ch[m].total : 0;
      t[yr] = s / 1e6;
    });
    const k = kam[a.kam] = kam[a.kam] || { accounts: 0, names: {}, y26: 0, y27: 0, y28: 0 };
    k.accounts++; k.names[norm(a.name)] = 1;
    k.y26 += t[2026]; k.y27 += t[2027]; k.y28 += t[2028];
    mv.push({ n: a.name, k: a.kam, rc: a.rate_class,
              a: +t[2026].toFixed(2), b: +t[2027].toFixed(2), d: +(t[2027] - t[2026]).toFixed(2) });
  });

  const K = {};
  Object.keys(kam).forEach(n => {
    const k = kam[n];
    K[n] = { accounts: k.accounts, customers: Object.keys(k.names).length,
             y26: +k.y26.toFixed(2), y27: +k.y27.toFixed(2), y28: +k.y28.toFixed(2) };
  });

  mv.sort((p, q) => Math.abs(q.d) - Math.abs(p.d));

  const company = {};
  [2026, 2027, 2028].forEach(y => {
    const r = _y3RcTotals(y); let t = 0;
    for (const c in r.totals) t += r.totals[c];
    company[y] = +(t / 1e6).toFixed(2);
  });

  const un = ALL.filter(a => !a.kam);
  const payload = {
    generated_from: 'sales.jmfinancelab.com engine, _y3RcTotals and _dfcGetChain, ' + new Date().toISOString().slice(0, 10),
    company,
    assigned_accounts: A.length,
    unassigned_comm_accounts: un.length,
    unassigned_comm_customers: Object.keys(un.reduce((o, a) => (o[norm(a.name)] = 1, o), {})).length,
    kam: K,
    movements: mv.slice(0, 14),
  };

  const blob = new Blob([JSON.stringify(payload, null, 1)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = '_kam_data.json';
  a.click();
  console.log('Extracted', A.length, 'assigned accounts across', Object.keys(K).length, 'managers.');
})();
