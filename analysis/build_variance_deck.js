"use strict";
const pptxgen = require("pptxgenjs");
const path = require("path");

const MEDIA = path.resolve(__dirname, "template_media");
const BRAND = path.resolve(__dirname, "brand_ref_2026", "Brand Reference 2026 - Copy");
const OUT   = path.resolve(__dirname, "JPS_Sales_Variance_Explained_Exec.pptx");

const C = {
  navy:    "062552",   // Oxford Blue
  blue:    "0E4E95",   // Royal Blue
  lBlue:   "009FDA",   // Electric Blue
  yellow:  "FFF000",   // Cyber Yellow
  white:   "FFFFFF",
  gray:    "44546A",
  bgGrad:  "1C60A4",   // gradient mid-stop
};
const F = { head: "Aptos Black", body: "Aptos" };
const DECK_FOOTER = "Sales Variance Explained  ·  Apr → May 2026";

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";  // 10" x 5.625"

// ─── HELPERS ────────────────────────────────────────────────────────────────

function addLogo(s) {
  // Official JPS primary logo — 806x274 px (2.94:1 ratio)
  s.addImage({ path: path.join(BRAND, "JPS-Logo-Primary-FullColour.png"), x: 8.73, y: 0.07, w: 1.15, h: 0.39 });
}

// Vertical accent bar + title for white slides
function addWhiteTitle(s, title, subtitleText, accentColor, fontSize) {
  const ac = accentColor || C.lBlue;
  const fs = fontSize || 24;
  // Taller bar if subtitle present
  const barH = subtitleText ? 0.82 : 0.55;
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.2, y: 0.06, w: 0.07, h: barH,
    fill: { color: ac }, line: { color: ac, width: 0 },
  });
  s.addText(title, {
    x: 0.35, y: 0.06, w: 8.7, h: 0.52,
    fontSize: fs, bold: true, color: C.navy,
    fontFace: F.head, valign: "middle", margin: 0,
  });
  if (subtitleText) {
    s.addText(subtitleText, {
      x: 0.35, y: 0.6, w: 8.7, h: 0.26,
      fontSize: 9.5, color: C.lBlue,
      fontFace: F.body, valign: "top", margin: 0,
    });
  }
}

// Footer for white content slides
function addWhiteFooter(s) {
  s.addText(DECK_FOOTER, {
    x: 0.12, y: 5.05, w: 9.6, h: 0.14,
    fontSize: 7.5, bold: true, color: C.navy, align: "right", valign: "middle",
    fontFace: F.body, margin: 0,
  });
  // Official Continuous Line — Oxford→Electric Blue gradient (1920x93 px)
  s.addImage({ path: path.join(BRAND, "JPS-BrandMark-(Oxford-Gradient).png"), x: 0, y: 5.14, w: 10, h: 0.484 });
}

// Footer for blue/dark slides (white text)
function addDarkFooter(s) {
  s.addText(DECK_FOOTER, {
    x: 0.12, y: 5.05, w: 9.6, h: 0.14,
    fontSize: 7.5, bold: true, color: C.white, align: "right", valign: "middle",
    fontFace: F.body, margin: 0,
  });
  // Official Continuous Line — white variant (1920x93 px)
  s.addImage({ path: path.join(BRAND, "JPS-BrandMark-(White).png"), x: 0, y: 5.14, w: 10, h: 0.484 });
}

// ─── SLIDE 1: COVER ─────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  // Full gradient background image
  s.addImage({ path: path.join(MEDIA, "bg_gradient.png"), x: 0, y: 0, w: 10, h: 5.625 });
  // JPS logo
  addLogo(s);
  // FP&A label
  s.addText("FP&A  ·  SALES ANALYSIS", {
    x: 1, y: 1.7, w: 8, h: 0.38,
    fontSize: 12, bold: true, color: C.yellow, align: "center",
    fontFace: F.body, charSpacing: 3, margin: 0,
  });
  // Main title: SALES VARIANCE EXPLAINED
  s.addText([
    { text: "SALES VARIANCE", options: { breakLine: true } },
    { text: "EXPLAINED" },
  ], {
    x: 0.8, y: 2.08, w: 8.4, h: 1.32,
    fontSize: 52, bold: true, color: C.white, align: "center",
    fontFace: F.head, valign: "middle", margin: 0,
  });
  // Subtitle
  s.addText("APR → MAY  2026", {
    x: 1, y: 3.42, w: 8, h: 0.48,
    fontSize: 20, bold: true, color: C.yellow, align: "center",
    fontFace: F.body, charSpacing: 2, margin: 0,
  });
  // Key finding
  s.addText("KEY FINDING", {
    x: 3.2, y: 3.95, w: 3.6, h: 0.22,
    fontSize: 8, bold: true, color: C.yellow, align: "center",
    fontFace: F.body, charSpacing: 2, margin: 0,
  });
  s.addShape(pres.shapes.LINE, { x: 3.2, y: 4.17, w: 3.6, h: 0, line: { color: C.white, width: 0.5, transparency: 40 } });
  s.addText("Demand fell on one-off factors (Wigton equipment break, ratchet step-down, April adjustment reversals)—offset by Alcoa IPP uplift. All drivers well-understood; no structural trend break.", {
    x: 2.0, y: 4.2, w: 6, h: 0.68,
    fontSize: 9.5, color: C.white, align: "center", italic: true,
    fontFace: F.body, valign: "top", margin: 0,
  });
  // Footer: official Continuous Line (white) + tagline
  s.addText("Powering What Matters", {
    x: 5.3, y: 5.05, w: 4.3, h: 0.16,
    fontSize: 10, bold: true, color: C.white, align: "right", valign: "middle",
    fontFace: F.body, margin: 0,
  });
  s.addImage({ path: path.join(BRAND, "JPS-BrandMark-(White).png"), x: 0, y: 5.14, w: 10, h: 0.484 });
}

// ─── SLIDE 2: MOVEMENT BY DRIVER ────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  addLogo(s);
  addWhiteTitle(s,
    "April → May movement by driver",
    "Month-on-month change by cause — demand & revenue (J$M)"
  );

  const cats = ["IPP self-gen", "Billing adj.", "Hurricane ratchet", "Operational", "Normal billing"];
  const demVals  = [-11.7, -5.8, -4.1, -1.2, -3.3];
  const revVals  = [11.4,  -9.1, -4.5, -1.7,  0.7];

  s.addChart(pres.charts.BAR, [
    { name: "Δ Demand (J$M)",  labels: cats, values: demVals },
    { name: "Δ Revenue (J$M)", labels: cats, values: revVals },
  ], {
    x: 0.15, y: 1.02, w: 6.1, h: 4.25,
    barDir: "col",
    barGapWidthPct: 70,
    chartColors: ["009FDA", "0E4E95"],
    showValue: true,
    dataLabelFontSize: 8,
    dataLabelColor: "333333",
    catAxisLabelFontSize: 9,
    catAxisLabelColor: C.gray,
    valAxisHidden: true,
    catGridLine: { style: "none" },
    valGridLine: { style: "none" },
    chartArea: { fill: { color: C.white } },
    plotArea: { fill: { color: C.white } },
    showLegend: true,
    legendPos: "b",
    legendFontSize: 9,
  });

  // Right: 3 finding callouts
  const findings = [
    { num: "01", head: "DEMAND FELL", body: "Wigton demand break −J$8.8M (equipment failure) + ratchet step-down + April adjustment reversals (Hodges, Musson, Bay Juices)." },
    { num: "02", head: "REVENUE MIXED", body: "Alcoa IPP up +J$32M and normal accounts higher, offset by April-overstated adjustments reversing (Musson −J$12M)." },
    { num: "03", head: "NET READ", body: "Almost all MoM movement is one-off — adjustments, demand break, ratchet unwind, IPP self-gen. No structural trend break." },
  ];

  findings.forEach(({ num, head, body }, i) => {
    const fy = 1.08 + i * 1.42;
    // Numbered badge
    s.addShape(pres.shapes.OVAL, {
      x: 6.48, y: fy, w: 0.38, h: 0.38,
      fill: { color: C.navy }, line: { color: C.navy, width: 0 },
    });
    s.addText(num, {
      x: 6.48, y: fy, w: 0.38, h: 0.38,
      fontSize: 11, bold: true, color: C.white, align: "center", valign: "middle",
      fontFace: F.body, margin: 0,
    });
    // Heading
    s.addText(head, {
      x: 6.92, y: fy, w: 2.88, h: 0.38,
      fontSize: 11, bold: true, color: C.navy, valign: "middle",
      fontFace: F.head, margin: 0,
    });
    // Body
    s.addText(body, {
      x: 6.55, y: fy + 0.42, w: 3.28, h: 0.92,
      fontSize: 9, color: C.gray, valign: "top",
      fontFace: F.body, margin: 0,
    });
    // Divider
    if (i < 2) {
      s.addShape(pres.shapes.LINE, { x: 6.5, y: fy + 1.38, w: 3.3, h: 0, line: { color: "D0D7E3", width: 0.5 } });
    }
  });

  addWhiteFooter(s);
}

// ─── SLIDE 3: BY DRIVER — ACCOUNTS ─────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  addLogo(s);
  addWhiteTitle(s,
    "By driver — accounts behind each",
    "Apr → May change per account (J$M)  ·  demand & revenue"
  );

  const CATS = [
    {
      title: "IPP SELF-GEN",
      dem: "Dem −J$11.7M", rev: "Rev +J$11.4M",
      color: C.navy,
      accounts: [
        { name: "Wigton Windfarm",      dem: "−J$8.8M", rev: "Rev −J$16.0M" },
        { name: "Jamaica Private Power", dem: "−J$1.4M", rev: "Rev −J$1.3M" },
        { name: "West Kingston Power",  dem: "−J$0.7M", rev: "Rev −J$1.4M" },
        { name: "Alcoa Mins Of",        dem: "−J$0.4M", rev: "Rev +J$31.3M" },
      ],
    },
    {
      title: "BILLING ADJ.",
      dem: "Dem −J$5.8M", rev: "Rev −J$9.1M",
      color: C.blue,
      accounts: [
        { name: "Hodges, George",    dem: "−J$2.5M", rev: "Rev −J$3.3M" },
        { name: "Musson Intl",       dem: "−J$2.1M", rev: "Rev −J$4.2M" },
        { name: "Bay Juices Ltd",    dem: "−J$1.2M", rev: "Rev −J$1.6M" },
      ],
    },
    {
      title: "HURRICANE RATCHET",
      dem: "Dem −J$4.1M", rev: "Rev −J$4.5M",
      color: "1C60A4",
      accounts: [
        { name: "Seawind Apartments",  dem: "−J$1.9M", rev: "Rev −J$2.4M" },
        { name: "Bay Roc Hotel",       dem: "−J$0.9M", rev: "Rev −J$1.0M" },
        { name: "X Fund Properties",   dem: "−J$0.7M", rev: "Rev −J$1.2M" },
        { name: "Baking Enterprise",   dem: "−J$0.3M", rev: "Rev +J$0.0M" },
      ],
    },
    {
      title: "OPERATIONAL",
      dem: "Dem −J$1.2M", rev: "Rev −J$1.7M",
      color: C.lBlue,
      accounts: [
        { name: "Convenient Brands",  dem: "−J$0.8M", rev: "Rev −J$1.4M" },
        { name: "Playa Hall Jamaican", dem: "−J$0.3M", rev: "Rev −J$0.2M" },
        { name: "Gleaner Co Ltd",     dem: "−J$0.1M", rev: "Rev −J$0.1M" },
      ],
    },
    {
      title: "NORMAL BILLING",
      dem: "Dem −J$3.3M", rev: "Rev +J$0.7M",
      color: "44546A",
      accounts: [
        { name: "Kingston Free Port",      dem: "−J$1.6M", rev: "Rev −J$0.8M" },
        { name: "Supreme Ventures",        dem: "−J$0.7M", rev: "Rev −J$0.7M" },
        { name: "Caribbean Broilers",      dem: "−J$0.6M", rev: "Rev +J$1.3M" },
        { name: "German Ship Repairs",     dem: "−J$0.2M", rev: "Rev −J$0.4M" },
      ],
    },
  ];

  const colW = 1.88;
  const colGap = 0.05;
  const startX = 0.12;
  const contentY = 0.97;
  const contentH = 4.45;

  CATS.forEach((cat, ci) => {
    const cx = startX + ci * (colW + colGap);
    // Header block
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: contentY, w: colW, h: 0.55,
      fill: { color: cat.color }, line: { color: cat.color, width: 0 },
    });
    s.addText(cat.title, {
      x: cx + 0.06, y: contentY, w: colW - 0.1, h: 0.36,
      fontSize: 8, bold: true, color: C.white, valign: "middle",
      fontFace: F.body, margin: 0,
    });
    s.addText(cat.dem + "  |  " + cat.rev, {
      x: cx + 0.06, y: contentY + 0.34, w: colW - 0.1, h: 0.21,
      fontSize: 7, color: C.white, valign: "top",
      fontFace: F.body, margin: 0,
    });
    // Account rows
    cat.accounts.forEach((acc, ai) => {
      const ay = contentY + 0.6 + ai * 0.96;
      s.addShape(pres.shapes.RECTANGLE, {
        x: cx, y: ay, w: colW, h: 0.92,
        fill: { color: ai % 2 === 0 ? "F4F6FA" : C.white },
        line: { color: "D8DCE8", width: 0.4 },
      });
      // Left accent bar
      s.addShape(pres.shapes.RECTANGLE, {
        x: cx, y: ay, w: 0.05, h: 0.92,
        fill: { color: cat.color }, line: { color: cat.color, width: 0 },
      });
      s.addText(acc.name, {
        x: cx + 0.09, y: ay + 0.05, w: colW - 0.14, h: 0.34,
        fontSize: 8, bold: true, color: C.navy, valign: "top",
        fontFace: F.body, margin: 0,
      });
      s.addText("Dem " + acc.dem, {
        x: cx + 0.09, y: ay + 0.38, w: colW - 0.14, h: 0.22,
        fontSize: 7.5, color: C.gray, valign: "top",
        fontFace: F.body, margin: 0,
      });
      s.addText(acc.rev, {
        x: cx + 0.09, y: ay + 0.58, w: colW - 0.14, h: 0.22,
        fontSize: 7.5, color: acc.rev.includes("+") ? "1B6B35" : "9B1C1C", valign: "top",
        fontFace: F.body, margin: 0,
      });
    });
  });

  addWhiteFooter(s);
}

// ─── SLIDE 4: REVENUE QUALITY ────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  addLogo(s);
  addWhiteTitle(s,
    "Revenue quality — demand vs energy divergence",
    "Inside 'Normal billing': revenue (ex-fuel) rose while billed demand fell or was flat.",
    C.lBlue, 18
  );

  // Table header
  const cols = ["Account", "Class", "Δ Rev x-fuel", "Δ Demand", "Δ Energy", "Δ IPP"];
  const colWidths = [2.5, 1.1, 1.2, 1.2, 1.2, 1.2];
  const tableX = 0.25;
  const tableY = 1.0;
  const hdrH = 0.34;
  const rowH = 0.42;

  // Header row
  let cx = tableX;
  cols.forEach((col, ci) => {
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: tableY, w: colWidths[ci], h: hdrH,
      fill: { color: C.navy }, line: { color: C.navy, width: 0 },
    });
    s.addText(col, {
      x: cx + 0.05, y: tableY, w: colWidths[ci] - 0.05, h: hdrH,
      fontSize: 9, bold: true, color: C.white, valign: "middle",
      fontFace: F.body, margin: 0,
    });
    cx += colWidths[ci];
  });

  const rows = [
    ["Caribbean Broilers Ja Ltd", "RT40 & RT50", "+J$1.3M", "−J$0.6M", "+J$0.9M", "+J$1.0M"],
    ["Windalco",                  "RT50 & RT70", "+J$1.3M", "−J$0.2M", "+J$0.8M", "+J$0.7M"],
    ["National Irrigation Commission", "RT40",   "+J$3.3M", "+J$0.0M",  "+J$2.2M", "+J$0.5M"],
    ["Sandals Whitehouse Management",  "RT50",   "+J$1.5M", "+J$0.0M",  "+J$1.2M", "+J$0.4M"],
  ];

  rows.forEach((row, ri) => {
    const ry = tableY + hdrH + ri * rowH;
    cx = tableX;
    const bg = ri % 2 === 0 ? "F4F6FA" : C.white;
    row.forEach((cell, ci) => {
      s.addShape(pres.shapes.RECTANGLE, {
        x: cx, y: ry, w: colWidths[ci], h: rowH,
        fill: { color: bg }, line: { color: "D0D7E3", width: 0.4 },
      });
      const isNeg = cell.startsWith("−");
      const isPos = cell.startsWith("+J$") || cell.startsWith("+J");
      const txtColor = ci >= 2 ? (isNeg ? "9B1C1C" : isPos ? "1B6B35" : C.navy) : C.navy;
      s.addText(cell, {
        x: cx + 0.06, y: ry, w: colWidths[ci] - 0.08, h: rowH,
        fontSize: ci === 0 ? 8.5 : 9, bold: ci === 0,
        color: txtColor, valign: "middle",
        fontFace: F.body, margin: 0,
      });
      cx += colWidths[ci];
    });
  });

  // Two callout boxes
  const callouts = [
    {
      label: "WHY IT MATTERS",
      color: C.navy,
      body: "Demand is the capacity charge — the margin. Revenue rising while demand falls means accounts are consuming more energy but billing is not capturing it in capacity charges. Investigate load-factor shift, ratchet application, or multiplier settings.",
    },
    {
      label: "ALCOA FLAG",
      color: "C05400",
      body: "Of the +J$31.3M revenue (ex-fuel) jump, ~+J$25.5M appears to be a billing adjustment (only +J$5.9M from energy/demand/IPP). Confirm the true-up nature before treating as a trend.",
    },
  ];

  callouts.forEach(({ label, color, body }, i) => {
    const bx = i === 0 ? 0.25 : 5.2;
    const bw = 4.7;
    const by = tableY + hdrH + rows.length * rowH + 0.22;
    s.addShape(pres.shapes.RECTANGLE, {
      x: bx, y: by, w: bw, h: 1.22,
      fill: { color: i === 0 ? "EDF0F7" : "FFF4E8" },
      line: { color: color, width: 1 },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: bx, y: by, w: bw, h: 0.3,
      fill: { color: color }, line: { color: color, width: 0 },
    });
    s.addText(label, {
      x: bx + 0.1, y: by, w: bw - 0.12, h: 0.3,
      fontSize: 8.5, bold: true, color: C.white, valign: "middle",
      fontFace: F.body, charSpacing: 1, margin: 0,
    });
    s.addText(body, {
      x: bx + 0.1, y: by + 0.33, w: bw - 0.18, h: 0.86,
      fontSize: 8.5, color: C.navy, valign: "top",
      fontFace: F.body, margin: 0,
    });
  });

  addWhiteFooter(s);
}

// ─── SLIDE 5: AREAS FLAGGED ──────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  addLogo(s);
  addWhiteTitle(s,
    "Areas flagged for investigation",
    "Left: large MoM movers (unreviewed).  Right: revenue quality alerts."
  );

  // LEFT column: Large Movers
  const moversX = 0.18;
  const moversW = 4.7;
  const startY = 1.0;

  s.addShape(pres.shapes.RECTANGLE, {
    x: moversX, y: startY, w: moversW, h: 0.36,
    fill: { color: C.navy }, line: { color: C.navy, width: 0 },
  });
  s.addText("LARGE MOVERS  —  unreviewed", {
    x: moversX + 0.1, y: startY, w: moversW - 0.1, h: 0.36,
    fontSize: 9, bold: true, color: C.white, valign: "middle",
    fontFace: F.body, charSpacing: 1, margin: 0,
  });

  // Sub-header
  const mHdrH = 0.24;
  const mHdrY = startY + 0.36;
  const mCols = ["Account", "Class", "Δ Dem", "Δ Rev"];
  const mColW = [2.3, 1.2, 0.6, 0.6];
  let mcx = moversX;
  mCols.forEach((h, i) => {
    s.addShape(pres.shapes.RECTANGLE, {
      x: mcx, y: mHdrY, w: mColW[i], h: mHdrH,
      fill: { color: "D0D7E3" }, line: { color: "B8C0D4", width: 0.3 },
    });
    s.addText(h, {
      x: mcx + 0.04, y: mHdrY, w: mColW[i] - 0.04, h: mHdrH,
      fontSize: 8, bold: true, color: C.navy, valign: "middle",
      fontFace: F.body, margin: 0,
    });
    mcx += mColW[i];
  });

  const movers = [
    ["National Water Commission",  "RT40 & RT50",         "+J$0.1M",  "+J$18.6M"],
    ["Caribbean Cement Co Ltd",    "RT50",                "+J$0.5M",  "+J$7.7M"],
    ["St James Parish Council",    "RT50 & RT60",         "+J$0.0M",  "−J$6.9M"],
    ["MBJ Airports Limited",       "RT40 & RT50 & RT70",  "+J$3.8M",  "+J$6.7M"],
    ["Riu Jamaicotel Limited",     "RT50 & RT70",         "+J$1.4M",  "+J$5.2M"],
    ["Kgn & St Andrew Corp",       "RT60",                "+J$0.0M",  "−J$5.0M"],
  ];

  const mRowH = 0.56;
  movers.forEach((row, ri) => {
    const ry = mHdrY + mHdrH + ri * mRowH;
    mcx = moversX;
    mColW.forEach((cw, ci) => {
      s.addShape(pres.shapes.RECTANGLE, {
        x: mcx, y: ry, w: cw, h: mRowH,
        fill: { color: ri % 2 === 0 ? "F4F6FA" : C.white },
        line: { color: "D0D7E3", width: 0.3 },
      });
      const isNeg = row[ci].startsWith("−");
      const isPos = row[ci].startsWith("+J$");
      const tc = ci >= 2 ? (isNeg ? "9B1C1C" : isPos ? "1B6B35" : C.navy) : C.navy;
      s.addText(row[ci], {
        x: mcx + 0.05, y: ry, w: cw - 0.06, h: mRowH,
        fontSize: ci === 0 ? 8.5 : 8.5, bold: ci === 0, color: tc, valign: "middle",
        fontFace: F.body, margin: 0,
      });
      mcx += cw;
    });
  });

  // RIGHT column: Revenue Flags
  const flagsX = 5.1;
  const flagsW = 4.7;

  s.addShape(pres.shapes.RECTANGLE, {
    x: flagsX, y: startY, w: flagsW, h: 0.36,
    fill: { color: "C05400" }, line: { color: "C05400", width: 0 },
  });
  s.addText("REVENUE FLAGS  —  demand / energy divergence", {
    x: flagsX + 0.1, y: startY, w: flagsW - 0.1, h: 0.36,
    fontSize: 9, bold: true, color: C.white, valign: "middle",
    fontFace: F.body, charSpacing: 1, margin: 0,
  });

  const flags = [
    {
      name: "Caribbean Broilers Ja Ltd", cls: "RT40 & RT50",
      metrics: "Rev +J$1.3M  ·  Dem −J$0.6M  ·  Energy +J$0.9M",
      note: "Revenue up, demand flat/down — capacity charge not keeping pace (see slide 4)",
    },
    {
      name: "Windalco", cls: "RT50 & RT70",
      metrics: "Rev +J$1.3M  ·  Dem −J$0.2M  ·  Energy +J$0.8M",
      note: "Revenue up, demand flat/down — capacity charge not keeping pace",
    },
    {
      name: "National Irrigation Commission", cls: "RT40",
      metrics: "Rev +J$3.3M  ·  Dem +J$0.0M  ·  Energy +J$2.2M",
      note: "Revenue up, demand flat — capacity charge not keeping pace",
    },
    {
      name: "Sandals Whitehouse Management", cls: "RT50",
      metrics: "Rev +J$1.5M  ·  Dem +J$0.0M  ·  Energy +J$1.2M",
      note: "Revenue up, demand flat — capacity charge not keeping pace",
    },
  ];

  const fRowH = 1.05;
  flags.forEach(({ name, cls, metrics, note }, fi) => {
    const fy = startY + 0.36 + fi * fRowH + 0.06;
    s.addShape(pres.shapes.RECTANGLE, {
      x: flagsX, y: fy, w: flagsW, h: fRowH - 0.08,
      fill: { color: fi % 2 === 0 ? "FFF8F0" : C.white },
      line: { color: "EDCFA0", width: 0.4 },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: flagsX, y: fy, w: 0.05, h: fRowH - 0.08,
      fill: { color: "C05400" }, line: { color: "C05400", width: 0 },
    });
    s.addText(name, {
      x: flagsX + 0.12, y: fy + 0.05, w: flagsW - 0.18, h: 0.24,
      fontSize: 9, bold: true, color: C.navy, valign: "top",
      fontFace: F.body, margin: 0,
    });
    s.addText(cls, {
      x: flagsX + 0.12, y: fy + 0.28, w: flagsW - 0.18, h: 0.2,
      fontSize: 7.5, color: C.gray, valign: "top",
      fontFace: F.body, margin: 0,
    });
    s.addText(metrics, {
      x: flagsX + 0.12, y: fy + 0.46, w: flagsW - 0.18, h: 0.2,
      fontSize: 7.5, bold: true, color: "C05400", valign: "top",
      fontFace: F.body, margin: 0,
    });
    s.addText(note, {
      x: flagsX + 0.12, y: fy + 0.64, w: flagsW - 0.18, h: 0.26,
      fontSize: 7.5, color: C.gray, italic: true, valign: "top",
      fontFace: F.body, margin: 0,
    });
  });

  addWhiteFooter(s);
}

// ─── SLIDE 6: OUTLOOK ────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  // Dark blue gradient background
  s.addImage({ path: path.join(MEDIA, "bg_gradient.png"), x: 0, y: 0, w: 10, h: 5.625 });
  addLogo(s);

  // Yellow accent bar + white title
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.2, y: 0.1, w: 0.07, h: 0.6,
    fill: { color: C.yellow }, line: { color: C.yellow, width: 0 },
  });
  s.addText("What it means / outlook", {
    x: 0.35, y: 0.08, w: 8.5, h: 0.55,
    fontSize: 24, bold: true, color: C.white,
    fontFace: F.head, valign: "middle", margin: 0,
  });

  const quadrants = [
    {
      label: "ONE-OFF",
      color: C.blue,
      body: "Wigton’s demand break and April-overstated adjustments (Musson, Bay Juices, Hodges) are corrections. They reverse naturally — not run-rate.",
      tag: "Reversing",
    },
    {
      label: "TEMPORARY",
      color: "1C60A4",
      body: "Hurricane-ratchet accounts (Bay Roc, X Fund, Seawind, the bakeries) step down each month until demand settles at ~80% of actual.",
      tag: "Winding down",
    },
    {
      label: "STRUCTURAL — BY DESIGN",
      color: C.lBlue,
      body: "IPP accounts (Alcoa, Wigton, JPPC, West Kingston, JEP, Content Solar) swing with self-generation; Alcoa lifted May revenue as self-gen fell.",
      tag: "Monitor monthly",
    },
    {
      label: "TO INVESTIGATE",
      color: "C05400",
      body: "A set of large accounts moved materially MoM outside the reviewed list. Assign for explanation before next reporting cycle (see slide 5).",
      tag: "Action required",
    },
  ];

  const qs = [
    { x: 0.2, y: 0.84 },
    { x: 5.1, y: 0.84 },
    { x: 0.2, y: 3.14 },
    { x: 5.1, y: 3.14 },
  ];
  const qW = 4.65, qH = 2.18;

  quadrants.forEach(({ label, color, body, tag }, qi) => {
    const { x, y } = qs[qi];
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: qW, h: qH,
      fill: { color: C.white },
      line: { color: C.white, width: 0 },
    });
    // Label bar
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: qW, h: 0.36,
      fill: { color: color }, line: { color: color, width: 0 },
    });
    s.addText(label, {
      x: x + 0.12, y, w: qW - 0.22, h: 0.36,
      fontSize: 10, bold: true, color: C.white, valign: "middle",
      fontFace: F.body, charSpacing: 1, margin: 0,
    });
    // Tag badge
    s.addShape(pres.shapes.RECTANGLE, {
      x: x + qW - 1.12, y: y + 0.38, w: 1.08, h: 0.24,
      fill: { color: color }, line: { color: C.white, width: 0.3 },
    });
    s.addText(tag, {
      x: x + qW - 1.12, y: y + 0.38, w: 1.08, h: 0.24,
      fontSize: 7, bold: true, color: C.white, align: "center", valign: "middle",
      fontFace: F.body, margin: 0,
    });
    // Body text
    s.addText(body, {
      x: x + 0.12, y: y + 0.68, w: qW - 0.22, h: qH - 0.78,
      fontSize: 9.5, color: C.navy, valign: "top",
      fontFace: F.body, margin: 0,
    });
  });

  addDarkFooter(s);
}

// ─── WRITE ──────────────────────────────────────────────────────────────────
pres.writeFile({ fileName: OUT })
  .then(() => console.log("Done: " + OUT))
  .catch(e => { console.error(e); process.exit(1); });
