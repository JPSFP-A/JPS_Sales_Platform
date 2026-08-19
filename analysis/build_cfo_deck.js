const pptxgen = require("pptxgenjs");
const fs = require("fs");

const D = JSON.parse(fs.readFileSync("_cfo_deck_ready.json", "utf8"));

// ---- Palette: "Midnight Executive" adapted to JPS's own report colors ----
const NAVY = "0B2545";
const NAVY2 = "132A46";
const STEEL = "1B4965";
const ICE = "CADCFC";
const WHITE = "FFFFFF";
const TEAL = "00C2A8";
const RED = "E84040";
const GREEN = "27C485";
const GREY = "5A6472";
const LIGHT = "F4F7FB";
const AMBER = "F0AD4E";
const TEAL_DARK = "017A6B"; // teal is too low-contrast on white at small sizes; use this for on-white kickers
const SUBTLE_ON_NAVY = "AFC3E3"; // lighter than the old 8FA6C7 for better contrast on NAVY backgrounds

const HEAD_FONT = "Georgia";
const BODY_FONT = "Calibri";

const RC_ORDER = ["RT10", "RT20", "RT40", "RT50", "RT60-ST", "RT70"];
const RC_LABEL = {
  RT10: "RT10 — Residential", RT20: "RT20 — Residential Large",
  RT40: "RT40 — Commercial", RT50: "RT50 — Commercial Large", RT60ST: "RT60-ST",
  "RT60-ST": "RT60-ST — Street Lighting", RT70: "RT70 — Industrial",
};

// Full industry names from the DB run 60-70 chars — too long for a chart category
// label. Shorten only the handful that actually appear as chart labels rather than
// truncating generically (truncation cut mid-word, e.g. "...and Mo" for "Motels").
const SHORT_INDUSTRY = {
  "Wired and Wireless Telecommunications Carriers (except Satellite)": "Telecom Carriers (Wired/Wireless)",
  "Hotels (except Casino Hotels) and Motels": "Hotels & Motels",
  "Supermarkets and Other Grocery Retailers (except Convenience Retailers)": "Supermarkets & Grocery Retailers",
  "General Medical and Surgical Hospitals": "Medical & Surgical Hospitals",
  "Water Supply and Irrigation Systems": "Water Supply & Irrigation",
};
const shortIndustry = (name) => SHORT_INDUSTRY[name] || name;

const fmt1 = (v) => (v == null ? "—" : v.toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 }));
const fmtPct = (v) => (v == null ? "—" : (v >= 0 ? "+" : "") + v.toFixed(1) + "%");
const varColor = (v) => (v == null ? GREY : v >= 0 ? GREEN : RED);

let pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
pres.author = "JPS Sales Analytics Team";
pres.title = `FY${D.year} Sales Forecast — KAM & Industry Review`;
const PW = 13.33, PH = 7.5, M = 0.6;

// ---------------------------------------------------------------------------
// Shared slide chrome
// ---------------------------------------------------------------------------
function footer(slide, pageLabel) {
  slide.addText(`Jamaica Public Service Company · FY${D.year} Sales Forecast — KAM & Industry Review`, {
    x: M, y: PH - 0.42, w: 8, h: 0.3, fontSize: 8.5, color: GREY, fontFace: BODY_FONT,
  });
  slide.addText(pageLabel || "", {
    x: PW - 3 - M, y: PH - 0.42, w: 3, h: 0.3, fontSize: 8.5, color: GREY, fontFace: BODY_FONT, align: "right",
  });
}

function lightSlide() {
  const s = pres.addSlide();
  s.background = { color: WHITE };
  return s;
}

function titleBar(slide, kicker, title, sub) {
  slide.addText(kicker.toUpperCase(), { x: M, y: 0.42, w: 10, h: 0.3, fontSize: 11, bold: true, color: TEAL_DARK, fontFace: BODY_FONT, charSpacing: 2 });
  slide.addText(title, { x: M, y: 0.72, w: 11.5, h: 0.7, fontSize: 30, bold: true, color: NAVY, fontFace: HEAD_FONT });
  if (sub) slide.addText(sub, { x: M, y: 1.34, w: 11.5, h: 0.4, fontSize: 13, color: GREY, fontFace: BODY_FONT });
}

function statCard(slide, x, y, w, h, label, value, sub, accent) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h, fill: { color: WHITE }, line: { color: "E2E8F0", width: 1 },
    shadow: { type: "outer", color: "0B2545", blur: 8, offset: 3, angle: 135, opacity: 0.08 },
  });
  slide.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.06, h, fill: { color: accent || TEAL }, line: { type: "none" } });
  slide.addText(label.toUpperCase(), { x: x + 0.25, y: y + 0.18, w: w - 0.4, h: 0.3, fontSize: 9.5, bold: true, color: GREY, fontFace: BODY_FONT, charSpacing: 1 });
  slide.addText(value, { x: x + 0.25, y: y + 0.42, w: w - 0.4, h: 0.62, fontSize: 30, bold: true, color: NAVY, fontFace: HEAD_FONT });
  if (sub) slide.addText(sub, { x: x + 0.25, y: y + h - 0.4, w: w - 0.4, h: 0.32, fontSize: 11, color: varColor(sub.startsWith("+") ? 1 : sub.startsWith("-") ? -1 : null), bold: true, fontFace: BODY_FONT });
}

// ---------------------------------------------------------------------------
// SLIDE 1 — Title
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: PW, h: 0.14, fill: { color: TEAL }, line: { type: "none" } });
  s.addText("JAMAICA PUBLIC SERVICE COMPANY", { x: M, y: 1.5, w: 10, h: 0.4, fontSize: 13, bold: true, color: TEAL, fontFace: BODY_FONT, charSpacing: 3 });
  s.addText(`FY${D.year} Sales Forecast`, { x: M, y: 2.0, w: 11, h: 1.0, fontSize: 46, bold: true, color: WHITE, fontFace: HEAD_FONT });
  s.addText("KAM & Industry Performance Review", { x: M, y: 2.95, w: 11, h: 0.6, fontSize: 22, color: ICE, fontFace: HEAD_FONT, italic: true });
  s.addText(
    `Actuals through month ${D.cur_month} of ${D.year} · Driver Forecast engine for the remainder · Prepared for Key Account Managers`,
    { x: M, y: 3.7, w: 10.5, h: 0.5, fontSize: 12.5, color: SUBTLE_ON_NAVY, fontFace: BODY_FONT }
  );
  s.addShape(pres.shapes.LINE, { x: M, y: 5.7, w: 4.5, h: 0, line: { color: TEAL, width: 2 } });
  s.addText([
    { text: `${fmt1(D.company.fy_gwh)} GWh`, options: { bold: true, fontSize: 20, color: WHITE, breakLine: true } },
    { text: "Full-Year Forecast, All Rate Classes", options: { fontSize: 11, color: SUBTLE_ON_NAVY } },
  ], { x: M, y: 5.9, w: 4, h: 1, fontFace: BODY_FONT });
  s.addText([
    { text: fmtPct(D.company.vs_bud_pct), options: { bold: true, fontSize: 20, color: D.company.vs_bud_pct >= 0 ? "6FE3C4" : "FF9B9B", breakLine: true } },
    { text: "Variance vs. Budget", options: { fontSize: 11, color: SUBTLE_ON_NAVY } },
  ], { x: 5.2, y: 5.9, w: 4, h: 1, fontFace: BODY_FONT });
  s.addText([
    { text: `${D.kams.length} KAMs`, options: { bold: true, fontSize: 20, color: WHITE, breakLine: true } },
    { text: `${fmt1(D.managed_fy_gwh)} GWh Managed Book`, options: { fontSize: 11, color: SUBTLE_ON_NAVY } },
  ], { x: 9.4, y: 5.9, w: 3.4, h: 1, fontFace: BODY_FONT });
}

// ---------------------------------------------------------------------------
// SLIDE 2 — Executive Summary
// ---------------------------------------------------------------------------
{
  const s = lightSlide();
  titleBar(s, "Executive Summary", `FY${D.year} Load Forecast vs. Budget & Prior Year`,
    `Actuals through month ${D.cur_month}; remainder is Driver Forecast engine output. All rate classes, company-wide.`);

  const cw = (11.9 - 0.4 * 3) / 4;
  statCard(s, M, 1.95, cw, 1.55, "FY Forecast", `${fmt1(D.company.fy_gwh)}`, "GWh · all rate classes", NAVY);
  statCard(s, M + (cw + 0.4) * 1, 1.95, cw, 1.55, "vs. Budget", fmtPct(D.company.vs_bud_pct), `Budget ${fmt1(D.company.bud_gwh)} GWh`, D.company.vs_bud_pct >= 0 ? GREEN : RED);
  statCard(s, M + (cw + 0.4) * 2, 1.95, cw, 1.55, "vs. Prior Year", fmtPct(D.company.vs_py_pct), `FY${D.prior_year} ${fmt1(D.company.py_gwh)} GWh`, D.company.vs_py_pct >= 0 ? GREEN : RED);
  statCard(s, M + (cw + 0.4) * 3, 1.95, cw, 1.55, "Commercial Book", `${fmt1(D.commercial_fy_gwh)}`, `GWh · ${fmt1(D.managed_fy_gwh / D.commercial_fy_gwh * 100)}% KAM-managed`, TEAL);

  const rows = [[
    { text: "Rate Class", options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 10 } },
    { text: `FY${D.year} Forecast (GWh)`, options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 10, align: "right" } },
    { text: "Budget (GWh)", options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 10, align: "right" } },
    { text: "Var vs Budget", options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 10, align: "right" } },
    { text: `FY${D.prior_year} Actual (GWh)`, options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 10, align: "right" } },
    { text: "Var vs PY", options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 10, align: "right" } },
  ]];
  D.rc_summary.forEach((r, i) => {
    const shade = i % 2 === 1 ? LIGHT : WHITE;
    rows.push([
      { text: RC_LABEL[r.rc] || r.rc, options: { fill: { color: shade }, fontSize: 10.5, bold: true, color: NAVY } },
      { text: fmt1(r.fy_gwh), options: { fill: { color: shade }, fontSize: 10.5, align: "right" } },
      { text: fmt1(r.bud_gwh), options: { fill: { color: shade }, fontSize: 10.5, align: "right", color: GREY } },
      { text: fmtPct(r.vs_bud_pct), options: { fill: { color: shade }, fontSize: 10.5, align: "right", bold: true, color: varColor(r.vs_bud_pct) } },
      { text: fmt1(r.py_gwh), options: { fill: { color: shade }, fontSize: 10.5, align: "right", color: GREY } },
      { text: fmtPct(r.vs_py_pct), options: { fill: { color: shade }, fontSize: 10.5, align: "right", bold: true, color: varColor(r.vs_py_pct) } },
    ]);
  });
  const totRow = [
    { text: "TOTAL", options: { fill: { color: ICE }, fontSize: 10.5, bold: true, color: NAVY } },
    { text: fmt1(D.company.fy_gwh), options: { fill: { color: ICE }, fontSize: 10.5, align: "right", bold: true } },
    { text: fmt1(D.company.bud_gwh), options: { fill: { color: ICE }, fontSize: 10.5, align: "right", bold: true } },
    { text: fmtPct(D.company.vs_bud_pct), options: { fill: { color: ICE }, fontSize: 10.5, align: "right", bold: true, color: varColor(D.company.vs_bud_pct) } },
    { text: fmt1(D.company.py_gwh), options: { fill: { color: ICE }, fontSize: 10.5, align: "right", bold: true } },
    { text: fmtPct(D.company.vs_py_pct), options: { fill: { color: ICE }, fontSize: 10.5, align: "right", bold: true, color: varColor(D.company.vs_py_pct) } },
  ];
  rows.push(totRow);
  s.addTable(rows, { x: M, y: 3.85, w: 11.9, colW: [3.3, 1.8, 1.6, 1.55, 1.8, 1.55], border: { pt: 0.5, color: "E2E8F0" }, autoPage: false });

  // Two short one-line footnotes (not the full driver detail, which has its own
  // slide) — the earlier two-line-each version wrapped to 4 lines total and ran
  // into the footer; kept tight here so it clears with room to spare.
  s.addText(
    `Key assumption: commercial macro ${fmtPct(D.assumptions.macro_commercial_pct_first)} → ${fmtPct(D.assumptions.macro_commercial_pct_last)}, residential ${fmtPct(D.assumptions.macro_residential_pct_first)} → ${fmtPct(D.assumptions.macro_residential_pct_last)} (${D.assumptions.forecast_months_label}) — full detail on the Key Assumptions slide.`,
    { x: M, y: 6.35, w: 11.9, h: 0.28, fontSize: 9, italic: true, color: GREY, fontFace: BODY_FONT }
  );
  s.addText(
    "Methodology: rolling 3-month trailing average × (1 + macro% + weather% + industry-or-seasonality% + operational%) + manual override, per KAM account or non-KAM cohort.",
    { x: M, y: 6.65, w: 11.9, h: 0.28, fontSize: 9, italic: true, color: GREY, fontFace: BODY_FONT }
  );
  footer(s, "2");
}

// ---------------------------------------------------------------------------
// SLIDE 3 — Key Assumptions
// ---------------------------------------------------------------------------
{
  const s = lightSlide();
  titleBar(s, "Key Assumptions", "What's Driving the Forecast",
    `Macro/weather drivers for ${D.assumptions.forecast_months_label}, plus every confirmed operational adjustment applied this forecast cycle.`);

  s.addText("MACRO & WEATHER DRIVERS", { x: M, y: 1.85, w: 11.9, h: 0.3, fontSize: 11, bold: true, color: NAVY, fontFace: BODY_FONT, charSpacing: 1 });
  const macroRows = [[
    { text: "Driver", options: { bold: true, color: WHITE, fill: { color: STEEL }, fontSize: 10 } },
    { text: `${D.assumptions.forecast_months_label} (monthly %)`, options: { bold: true, color: WHITE, fill: { color: STEEL }, fontSize: 10 } },
  ], [
    { text: "Commercial macro", options: { fill: { color: WHITE }, fontSize: 10.5, bold: true, color: NAVY } },
    { text: D.assumptions.macro_commercial_str || "—", options: { fill: { color: WHITE }, fontSize: 10.5, color: GREY } },
  ], [
    { text: "Residential macro", options: { fill: { color: LIGHT }, fontSize: 10.5, bold: true, color: NAVY } },
    { text: D.assumptions.macro_residential_str || "—", options: { fill: { color: LIGHT }, fontSize: 10.5, color: GREY } },
  ], [
    { text: "Weather", options: { fill: { color: WHITE }, fontSize: 10.5, bold: true, color: NAVY } },
    { text: D.assumptions.weather_str || "—", options: { fill: { color: WHITE }, fontSize: 10.5, color: GREY } },
  ]];
  s.addTable(macroRows, { x: M, y: 2.2, w: 11.9, colW: [2.4, 9.5], border: { pt: 0.5, color: "E2E8F0" }, autoPage: false });

  s.addText(
    `Applied to every rate class based on its segment (RT10/RT20 = residential; RT40/RT50/RT60-ST/RT70 = commercial). Industry-level drivers apply on top of the macro driver, only for KAM-assigned key accounts — see each KAM's detail slide for their book's specific industry driver.`,
    { x: M, y: 3.85, w: 11.9, h: 0.5, fontSize: 9.5, italic: true, color: GREY, fontFace: BODY_FONT }
  );

  s.addText("CONFIRMED OPERATIONAL ADJUSTMENTS", { x: M, y: 4.55, w: 11.9, h: 0.3, fontSize: 11, bold: true, color: NAVY, fontFace: BODY_FONT, charSpacing: 1 });
  const oaRows = [[
    { text: "Customer", options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 9.5 } },
    { text: "KAM", options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 9.5 } },
    { text: "Period", options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 9.5 } },
    { text: "Reason", options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 9.5 } },
    { text: "Note", options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 9.5 } },
  ]];
  D.assumptions.operational_adjustments.forEach((o, i) => {
    const shade = i % 2 === 1 ? LIGHT : WHITE;
    oaRows.push([
      { text: o.name, options: { fill: { color: shade }, fontSize: 9.5, bold: true, color: NAVY } },
      { text: o.kam || "—", options: { fill: { color: shade }, fontSize: 9, color: GREY } },
      { text: o.period, options: { fill: { color: shade }, fontSize: 9, bold: true, color: RED } },
      { text: o.reason, options: { fill: { color: shade }, fontSize: 9, color: GREY } },
      { text: o.note, options: { fill: { color: shade }, fontSize: 8.5, color: GREY } },
    ]);
  });
  s.addTable(oaRows, { x: M, y: 4.9, w: 11.9, colW: [2.2, 1.5, 1.15, 1.35, 5.7], border: { pt: 0.5, color: "E2E8F0" }, autoPage: false });
  footer(s, "3");
}

// ---------------------------------------------------------------------------
// SLIDE 4 — Commercial Book: Managed vs Unmanaged
// ---------------------------------------------------------------------------
{
  const s = lightSlide();
  titleBar(s, "Commercial Book Composition", "KAM-Managed vs. Unmanaged Accounts",
    `RT40 / RT50 / RT60-ST / RT70 — ${fmt1(D.commercial_fy_gwh)} GWh total commercial forecast for FY${D.year}`);

  s.addChart(pres.charts.DOUGHNUT, [{
    name: "Commercial Book",
    labels: ["KAM-Managed", "Unmanaged Cohort"],
    values: [D.managed_fy_gwh, D.unmanaged_fy_gwh],
  }], {
    x: M, y: 1.95, w: 5.2, h: 4.6,
    chartColors: [TEAL, "D8E2F0"],
    showLegend: true, legendPos: "b", legendColor: NAVY, legendFontSize: 11,
    // NAVY (not WHITE) — WHITE-on-D8E2F0 (the light "Unmanaged" wedge) was
    // near-invisible; NAVY reads clearly against both the teal and light wedge.
    showPercent: true, dataLabelColor: NAVY, dataLabelFontSize: 12, dataLabelFontBold: true,
    chartArea: { fill: { color: WHITE } },
  });

  const rx = 6.1;
  statCard(s, rx, 1.95, 5.7, 1.3, "KAM-Managed Volume", `${fmt1(D.managed_fy_gwh)} GWh`, `${fmt1(D.managed_fy_gwh / D.commercial_fy_gwh * 100)}% of commercial book`, TEAL);
  statCard(s, rx, 3.45, 5.7, 1.3, "Unmanaged Cohort Volume", `${fmt1(D.unmanaged_fy_gwh)} GWh`, `${fmt1(D.unmanaged_fy_gwh / D.commercial_fy_gwh * 100)}% of commercial book — no assigned KAM`, AMBER);

  s.addShape(pres.shapes.RECTANGLE, { x: rx, y: 5.0, w: 5.7, h: 1.55, fill: { color: NAVY2 }, line: { type: "none" } });
  s.addText("Growth angle", { x: rx + 0.25, y: 5.13, w: 5.2, h: 0.3, fontSize: 10, bold: true, color: TEAL, fontFace: BODY_FONT, charSpacing: 1 });
  s.addText(
    `${fmt1(D.unmanaged_fy_gwh)} GWh of commercial load — nearly one-fifth of the book — sits in cohorts with no assigned account manager. Assigning KAM coverage to the largest of these accounts is the most direct lever to grow managed volume without acquiring a single new customer.`,
    { x: rx + 0.25, y: 5.42, w: 5.2, h: 1.05, fontSize: 10.5, color: WHITE, fontFace: BODY_FONT }
  );
  footer(s, "4");
}

// ---------------------------------------------------------------------------
// SLIDE 4 — Industry Overview
// ---------------------------------------------------------------------------
{
  const s = lightSlide();
  titleBar(s, "Industry Focus", "Top Industries by FY Forecast Volume (GWh)",
    "KAM-assigned key accounts only. The unmanaged \"No KAM / Cohort\" pool (largest single bucket, 265.9 GWh) is covered on the prior slide, not repeated here.");

  // Exclude the unmanaged pool -- it's not an industry, and showing it again here
  // (it would otherwise be the single largest bar) duplicates the prior slide and
  // reads as if it were the #1 "industry" at a glance.
  const realIndustries = D.top_industries.filter((i) => i.name !== "No KAM / Cohort");
  // pptxgenjs renders horizontal-bar categories bottom-to-top, so the array must be
  // reversed for the largest (rank #1) value to land at the top of the chart.
  const inds = realIndustries.slice(0, 10).slice().reverse();
  s.addChart(pres.charts.BAR, [{
    name: `FY${D.year} GWh`,
    labels: inds.map((i) => shortIndustry(i.name)),
    values: inds.map((i) => +i.gwh.toFixed(1)),
  }], {
    x: M, y: 1.85, w: 11.9, h: 5.1, barDir: "bar",
    chartColors: [TEAL],
    chartArea: { fill: { color: WHITE } },
    catAxisLabelColor: NAVY, catAxisLabelFontSize: 10,
    valAxisLabelColor: GREY, valAxisLabelFontSize: 9,
    valGridLine: { color: "E2E8F0", size: 0.5 }, catGridLine: { style: "none" },
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: NAVY, dataLabelFontSize: 9, dataLabelFontBold: true,
    showLegend: false, showTitle: false,
    barGapWidthPct: 40,
  });
  footer(s, "5");
}

// ---------------------------------------------------------------------------
// SLIDE 5 — KAM Performance Summary
// ---------------------------------------------------------------------------
{
  const s = lightSlide();
  titleBar(s, "KAM Performance", "Book Performance by Key Account Manager",
    `FY${D.year} forecast vs. budget vs. FY${D.prior_year} actual, ranked by book size.`);

  const rows = [[
    { text: "KAM", options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 10 } },
    { text: "Accts", options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 10, align: "right" } },
    { text: "Custs", options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 10, align: "right" } },
    { text: `FY${D.year} (GWh)`, options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 10, align: "right" } },
    { text: "Budget (GWh)", options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 10, align: "right" } },
    { text: "vs Budget", options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 10, align: "right" } },
    { text: `FY${D.prior_year} (GWh)`, options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 10, align: "right" } },
    { text: "vs PY", options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 10, align: "right" } },
  ]];
  D.kams.forEach((k, i) => {
    const shade = i % 2 === 1 ? LIGHT : WHITE;
    rows.push([
      { text: k.name, options: { fill: { color: shade }, fontSize: 10.5, bold: true, color: NAVY } },
      { text: String(k.n_accounts), options: { fill: { color: shade }, fontSize: 10.5, align: "right", color: GREY } },
      { text: String(k.n_customers), options: { fill: { color: shade }, fontSize: 10.5, align: "right", color: GREY } },
      { text: fmt1(k.fy_gwh), options: { fill: { color: shade }, fontSize: 10.5, align: "right" } },
      { text: fmt1(k.bud_gwh), options: { fill: { color: shade }, fontSize: 10.5, align: "right", color: GREY } },
      { text: fmtPct(k.vs_bud_pct), options: { fill: { color: shade }, fontSize: 10.5, align: "right", bold: true, color: varColor(k.vs_bud_pct) } },
      { text: fmt1(k.py_gwh), options: { fill: { color: shade }, fontSize: 10.5, align: "right", color: GREY } },
      { text: fmtPct(k.vs_py_pct), options: { fill: { color: shade }, fontSize: 10.5, align: "right", bold: true, color: varColor(k.vs_py_pct) } },
    ]);
  });
  s.addTable(rows, { x: M, y: 1.95, w: 11.9, colW: [2.5, 0.85, 0.95, 1.6, 1.6, 1.4, 1.6, 1.3], border: { pt: 0.5, color: "E2E8F0" }, autoPage: false, fontSize: 10.5 });
  footer(s, "6");
}

// ---------------------------------------------------------------------------
// SLIDE 6 — KAM Performance Chart
// ---------------------------------------------------------------------------
{
  const s = lightSlide();
  titleBar(s, "KAM Performance", "Forecast vs. Budget, by KAM", "Sorted by book size (GWh).");

  s.addChart(pres.charts.BAR, [
    { name: `FY${D.year} Forecast`, labels: D.kams.map((k) => k.name), values: D.kams.map((k) => +k.fy_gwh.toFixed(1)) },
    { name: "Budget", labels: D.kams.map((k) => k.name), values: D.kams.map((k) => +k.bud_gwh.toFixed(1)) },
  ], {
    x: M, y: 1.85, w: 11.9, h: 5.1, barDir: "col", barGrouping: "clustered",
    chartColors: [NAVY, "B9C7DE"],
    chartArea: { fill: { color: WHITE } },
    catAxisLabelColor: NAVY, catAxisLabelFontSize: 9.5,
    valAxisLabelColor: GREY, valAxisLabelFontSize: 9,
    valGridLine: { color: "E2E8F0", size: 0.5 }, catGridLine: { style: "none" },
    showLegend: true, legendPos: "t", legendColor: NAVY, legendFontSize: 10.5,
    showTitle: false,
  });
  footer(s, "7");
}

// ---------------------------------------------------------------------------
// SLIDE 7 — Watch List
// ---------------------------------------------------------------------------
{
  const s = lightSlide();
  titleBar(s, "Watch List", "Books Furthest Off Budget", "For discussion with each KAM — not a scorecard.");

  const belowBudget = D.kams.filter((k) => k.vs_bud_pct != null).sort((a, b) => a.vs_bud_pct - b.vs_bud_pct).slice(0, 3);
  const aboveBudget = D.kams.filter((k) => k.vs_bud_pct != null).sort((a, b) => b.vs_bud_pct - a.vs_bud_pct).slice(0, 3);

  s.addText("BELOW BUDGET", { x: M, y: 1.85, w: 5.6, h: 0.3, fontSize: 12, bold: true, color: RED, fontFace: BODY_FONT, charSpacing: 1 });
  belowBudget.forEach((k, i) => {
    const y = 2.25 + i * 1.55;
    s.addShape(pres.shapes.RECTANGLE, { x: M, y, w: 5.6, h: 1.35, fill: { color: WHITE }, line: { color: "E2E8F0", width: 1 } });
    s.addShape(pres.shapes.RECTANGLE, { x: M, y, w: 0.06, h: 1.35, fill: { color: RED }, line: { type: "none" } });
    s.addText(k.name, { x: M + 0.25, y: y + 0.12, w: 3.4, h: 0.35, fontSize: 14, bold: true, color: NAVY, fontFace: HEAD_FONT });
    s.addText(fmtPct(k.vs_bud_pct), { x: M + 3.7, y: y + 0.1, w: 1.7, h: 0.4, fontSize: 18, bold: true, color: RED, fontFace: HEAD_FONT, align: "right" });
    const top = k.top_industries[0];
    s.addText(
      `${fmt1(k.fy_gwh)} GWh forecast vs ${fmt1(k.bud_gwh)} GWh budget (${fmt1(k.py_gwh)} GWh in FY${D.prior_year}).` +
      (top ? ` Largest industry in book: ${top.name} (${fmt1(top.gwh)} GWh).` : ""),
      { x: M + 0.25, y: y + 0.62, w: 5.15, h: 0.65, fontSize: 9.5, color: GREY, fontFace: BODY_FONT }
    );
  });

  s.addText("AHEAD OF BUDGET", { x: 6.7, y: 1.85, w: 5.6, h: 0.3, fontSize: 12, bold: true, color: GREEN, fontFace: BODY_FONT, charSpacing: 1 });
  aboveBudget.forEach((k, i) => {
    const y = 2.25 + i * 1.55;
    s.addShape(pres.shapes.RECTANGLE, { x: 6.7, y, w: 5.6, h: 1.35, fill: { color: WHITE }, line: { color: "E2E8F0", width: 1 } });
    s.addShape(pres.shapes.RECTANGLE, { x: 6.7, y, w: 0.06, h: 1.35, fill: { color: GREEN }, line: { type: "none" } });
    s.addText(k.name, { x: 6.95, y: y + 0.12, w: 3.4, h: 0.35, fontSize: 14, bold: true, color: NAVY, fontFace: HEAD_FONT });
    s.addText(fmtPct(k.vs_bud_pct), { x: 10.4, y: y + 0.1, w: 1.7, h: 0.4, fontSize: 18, bold: true, color: GREEN, fontFace: HEAD_FONT, align: "right" });
    const top = k.top_industries[0];
    s.addText(
      `${fmt1(k.fy_gwh)} GWh forecast vs ${fmt1(k.bud_gwh)} GWh budget (${fmt1(k.py_gwh)} GWh in FY${D.prior_year}).` +
      (top ? ` Largest industry in book: ${top.name} (${fmt1(top.gwh)} GWh).` : ""),
      { x: 6.95, y: y + 0.62, w: 5.15, h: 0.65, fontSize: 9.5, color: GREY, fontFace: BODY_FONT }
    );
  });
  footer(s, "8");
}

// ---------------------------------------------------------------------------
// SLIDES 9+ — Per-KAM detail
// ---------------------------------------------------------------------------
// Compact mini-bar row: label line, then a track+fill bar with the value label in a
// fixed white-background column to the right (never overlaid on the colored fill --
// that was the earlier contrast bug when a #1-ranked bar rendered at ~100% width).
function miniBar(slide, x, y, w, label, valueStr, frac, color) {
  const trackW = w - 1.0;
  slide.addText(label, { x, y, w, h: 0.28, fontSize: 9.5, bold: true, color: NAVY, fontFace: BODY_FONT });
  slide.addShape(pres.shapes.RECTANGLE, { x, y: y + 0.29, w: trackW, h: 0.18, fill: { color: LIGHT }, line: { type: "none" } });
  slide.addShape(pres.shapes.RECTANGLE, { x, y: y + 0.29, w: trackW * Math.max(0.08, frac), h: 0.18, fill: { color }, line: { type: "none" } });
  slide.addText(valueStr, { x: x + trackW + 0.06, y: y + 0.27, w: 0.9, h: 0.22, fontSize: 8.5, bold: true, color: NAVY, fontFace: BODY_FONT, align: "left", valign: "middle" });
}

// Top/Bottom-3 customer mini-table.
function custTable(slide, x, y, w, title, titleColor, entries) {
  slide.addText(title, { x, y, w, h: 0.28, fontSize: 10, bold: true, color: titleColor, fontFace: BODY_FONT, charSpacing: 1 });
  const rows = [[
    { text: "Customer", options: { bold: true, color: WHITE, fill: { color: STEEL }, fontSize: 8.5 } },
    { text: `FY${D.year}`, options: { bold: true, color: WHITE, fill: { color: STEEL }, fontSize: 8.5, align: "right" } },
    { text: "YoY", options: { bold: true, color: WHITE, fill: { color: STEEL }, fontSize: 8.5, align: "right" } },
  ]];
  entries.forEach((c, i) => {
    const shade = i % 2 === 1 ? LIGHT : WHITE;
    rows.push([
      { text: c.name, options: { fill: { color: shade }, fontSize: 8.8, bold: true, color: NAVY } },
      { text: fmt1(c.fy_gwh), options: { fill: { color: shade }, fontSize: 8.8, align: "right", color: GREY } },
      { text: fmtPct(c.chg_pct), options: { fill: { color: shade }, fontSize: 8.8, align: "right", bold: true, color: varColor(c.chg_pct) } },
    ]);
  });
  if (!entries.length) rows.push([{ text: "No qualifying customers", options: { fill: { color: WHITE }, fontSize: 8.5, italic: true, color: GREY, colspan: 3 } }]);
  slide.addTable(rows, { x, y: y + 0.32, w, colW: [w - 1.5, 0.75, 0.75], border: { pt: 0.5, color: "E2E8F0" }, autoPage: false });
}

D.kams.forEach((k, idx) => {
  const s = lightSlide();
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: PW, h: 1.55, fill: { color: NAVY }, line: { type: "none" } });
  s.addText("KEY ACCOUNT MANAGER", { x: M, y: 0.32, w: 8, h: 0.3, fontSize: 10.5, bold: true, color: TEAL, fontFace: BODY_FONT, charSpacing: 2 });
  s.addText(k.name, { x: M, y: 0.58, w: 9, h: 0.75, fontSize: 32, bold: true, color: WHITE, fontFace: HEAD_FONT });
  s.addText(`${k.n_accounts} accounts · ${k.n_customers} customers under management`, { x: M, y: 1.24, w: 9, h: 0.3, fontSize: 11.5, color: ICE, fontFace: BODY_FONT });

  // Card height 1.35 (not the tighter 1.05 tried initially) -- statCard()'s sub-text
  // is positioned at y+h-0.4, and at h=1.05 that put the caption line directly under
  // the 30pt value glyphs' descenders, overlapping on every "vs. Budget"/"vs. Prior
  // Year" card (visible on every KAM slide). 1.35 is the height already proven clean
  // on the Executive Summary slide's identical card row.
  const cw = (11.9 - 0.35 * 2) / 3;
  statCard(s, M, 1.7, cw, 1.35, `FY${D.year} Forecast`, `${fmt1(k.fy_gwh)} GWh`, null, NAVY);
  statCard(s, M + cw + 0.35, 1.7, cw, 1.35, "vs. Budget", fmtPct(k.vs_bud_pct), `Budget ${fmt1(k.bud_gwh)} GWh`, varColor(k.vs_bud_pct));
  statCard(s, M + (cw + 0.35) * 2, 1.7, cw, 1.35, "vs. Prior Year", fmtPct(k.vs_py_pct), `FY${D.prior_year} ${fmt1(k.py_gwh)} GWh`, varColor(k.vs_py_pct));

  // Four columns: Rate Class Mix | Top Industries | Top 3 Customers | Bottom 3 Customers
  const colY = 3.35;
  const gA = M, wA = 1.95;
  const gB = gA + wA + 0.12, wB = 2.95;
  const gC = gB + wB + 0.12, wC = 3.35;
  const gD = gC + wC + 0.12, wD = 3.35;

  s.addText("RATE CLASS MIX", { x: gA, y: colY, w: wA, h: 0.28, fontSize: 10, bold: true, color: NAVY, fontFace: BODY_FONT, charSpacing: 0.5 });
  const rcEntries = Object.entries(k.rc_mix).sort((a, b) => b[1] - a[1]);
  const maxRc = rcEntries.length ? rcEntries[0][1] : 1;
  rcEntries.forEach((e, i) => miniBar(s, gA, colY + 0.35 + i * 0.55, wA, e[0], `${fmt1(e[1])}`, e[1] / maxRc, TEAL));

  s.addText("TOP INDUSTRIES IN BOOK", { x: gB, y: colY, w: wB, h: 0.28, fontSize: 10, bold: true, color: NAVY, fontFace: BODY_FONT, charSpacing: 0.5 });
  const maxInd = k.top_industries.length ? k.top_industries[0].gwh : 1;
  k.top_industries.forEach((ind, i) => miniBar(s, gB, colY + 0.35 + i * 0.95, wB, ind.name, `${fmt1(ind.gwh)}`, ind.gwh / maxInd, STEEL));

  custTable(s, gC, colY, wC, "TOP 3 CUSTOMERS", GREEN, k.top_customers);
  custTable(s, gD, colY, wD, "BOTTOM 3 (BY YOY DECLINE)", RED, k.bottom_customers);

  if (k.assumption_note) {
    s.addShape(pres.shapes.RECTANGLE, { x: M, y: 6.45, w: 11.9, h: 0.5, fill: { color: LIGHT }, line: { type: "none" } });
    s.addText([
      { text: "Key assumption — ", options: { bold: true, color: NAVY } },
      { text: k.assumption_note, options: { color: GREY } },
    ], { x: M + 0.2, y: 6.45, w: 11.5, h: 0.5, fontSize: 9.5, fontFace: BODY_FONT, valign: "middle" });
  }

  footer(s, `KAM ${idx + 1} of ${D.kams.length}`);
});

// ---------------------------------------------------------------------------
// FINAL SLIDE — Methodology
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("METHODOLOGY & SOURCES", { x: M, y: 0.7, w: 10, h: 0.4, fontSize: 13, bold: true, color: TEAL, fontFace: BODY_FONT, charSpacing: 2 });
  s.addText("How This Forecast Is Built", { x: M, y: 1.15, w: 10, h: 0.6, fontSize: 26, bold: true, color: WHITE, fontFace: HEAD_FONT });

  const bullets = [
    `Actuals through month ${D.cur_month} of ${D.year}; the remainder of the year is projected by the Driver Forecast engine.`,
    "Each KAM-assigned account is forecast individually; unassigned accounts are pooled into cohorts by rate class, parish, and consumption bucket.",
    "Base = rolling 3-month trailing average (actual or already-forecast). Total = Base × (1 + macro% + weather% + industry-or-seasonality% + operational%) + manual kWh override.",
    "Industry drivers apply only to KAM-assigned key accounts — pooled cohorts carry no individual industry signal.",
    "Operational adjustments (confirmed defections, disruptions) are applied per account from the live adjustment log, not estimated.",
    "Figures exclude the EV rate class. Source: jps_actuals, jps_kam, jps_industries, jps_macro_assumptions, jps_operational_adjustments_current, jps_budget.",
  ];
  s.addText(
    bullets.map((b, i) => ({ text: b, options: { bullet: { code: "2022" }, breakLine: i < bullets.length - 1, paraSpaceAfter: 10 } })),
    { x: M, y: 2.0, w: 11.8, h: 4.5, fontSize: 13, color: ICE, fontFace: BODY_FONT }
  );
  s.addText(`Generated from the JPS Sales Analytics Platform · Confidential — for internal KAM review`, {
    x: M, y: PH - 0.55, w: 10, h: 0.3, fontSize: 9.5, color: SUBTLE_ON_NAVY, fontFace: BODY_FONT,
  });
}

pres.writeFile({ fileName: "JPS_FY" + D.year + "_KAM_Industry_Forecast_Review_v2.pptx" }).then(() => {
  console.log("Deck written.");
});
