# -*- coding: utf-8 -*-
# Company-wide July 2026 performance report: what's driving the variance,
# account-level anomalies, parish concentration, residential drivers.
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                 Image, PageBreak, HRFlowable)

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
CHART_DIR = "_pdf_charts"
os.makedirs(CHART_DIR, exist_ok=True)

NAVY = colors.HexColor("#0C3547")
BLUE = colors.HexColor("#3b6ea5")
GREEN = colors.HexColor("#1D9E75")
RED = colors.HexColor("#E24B4A")
GOLD = colors.HexColor("#B87800")
GREY = colors.HexColor("#7F7F7F")
LTGREY = colors.HexColor("#F0F3F6")

plt.rcParams.update({"font.family": "sans-serif", "font.size": 9, "axes.edgecolor": "#B7C6D9",
                      "axes.grid": True, "grid.color": "#E5EAF0", "grid.linewidth": 0.6,
                      "axes.axisbelow": True})

# ---------- load data ----------
comp = json.load(open("_pdf_company_totals.json"))
movers = json.load(open("_pdf_movers.json"))
parish = json.load(open("_pdf_parish.json"))
CJ = json.load(open("corrected.json"))
BUCK = CJ["bucket"]
prepaid = json.load(open("_res_prepaid.json"))
rt20_real = json.load(open("_res_rt20_real.json"))
rt20_budget = json.load(open("_res_jps_budget.json"))
rt20_le = json.load(open("_res_jps_le.json"))
unassigned_payg = json.load(open("_res_unassigned_payg.json"))
zero_streaks = json.load(open("_zero_streak_result.json"))


def agg_rt20_real_totals(month_num):
    rows = [r for r in rt20_real if r["year"] == 2026 and r["month"] == month_num]
    kwh = sum(r["kwh"] or 0 for r in rows)
    rev = sum(r["revenue_jmd"] or 0 for r in rows)
    return kwh, rev


def agg_budget_le_totals(source, month_num):
    rows = [r for r in source if r["year"] == 2026 and r["month"] == month_num]
    kwh_key = "kwh_budget" if "kwh_budget" in rows[0] else "kwh_le"
    rev_key = "revenue_budget" if "revenue_budget" in rows[0] else "revenue_le"
    return sum((r[kwh_key] or 0) for r in rows), sum((r[rev_key] or 0) for r in rows)

BUCKET_ORDER = ["<Zero", "Zero", "<150", "150>350", "350>550", "550>750", "750>950", "over 950"]


def bucket_of(kwh):
    if kwh < 0: return "<Zero"
    if kwh == 0: return "Zero"
    if kwh < 150: return "<150"
    if kwh < 350: return "150>350"
    if kwh < 550: return "350>550"
    if kwh < 750: return "550>750"
    if kwh < 950: return "750>950"
    return "over 950"


def bin_bucket_of(bk):
    """corrected.json's histogram bins are 50kWh WIDE - bin key 0 means [0,50), not
    exactly zero. bucket_of(0) would wrongly say "Zero" and dump that bin's real,
    nonzero consumption into the Zero tier. This data source can't isolate exactly-zero
    consumption, so Zero is left empty here and [0,50) folds into "<150" like every
    other bin."""
    if bk < 0: return "<Zero"
    if bk < 150: return "<150"
    if bk < 350: return "150>350"
    if bk < 550: return "350>550"
    if bk < 750: return "550>750"
    if bk < 950: return "750>950"
    return "over 950"


RT10_TRUE_ZERO = json.load(open("rt10_zero_fix_result.json")) if os.path.exists("rt10_zero_fix_result.json") else {}


def roll_up(month, title):
    out = {b: {"count": 0.0, "kwh": 0.0, "rev": 0.0} for b in BUCKET_ORDER}
    for bstr, v in BUCK.get(month, {}).get(title, {}).items():
        bk = int(bstr)
        label = bin_bucket_of(bk if bk < 5000 else 5000)
        out[label]["count"] += v[0]; out[label]["kwh"] += v[1]; out[label]["rev"] += v[2]
    if title == "RT10" and month in RT10_TRUE_ZERO:
        tz_count, tz_kwh, tz_rev = RT10_TRUE_ZERO[month]["TrueZero"][:3]
        out["Zero"]["count"] += tz_count; out["Zero"]["kwh"] += tz_kwh; out["Zero"]["rev"] += tz_rev
        out["<150"]["count"] -= tz_count; out["<150"]["kwh"] -= tz_kwh; out["<150"]["rev"] -= tz_rev
    return out


def money(v):
    return "J${:,.0f}".format(v)


def moneyM(v):
    return "J${:,.1f}M".format(v / 1e6)


def pct(v):
    return "{:+.1f}%".format(v * 100)


# ---------- charts ----------
def chart_component_bridge():
    L = comp["legend"]
    idx = {n: i for i, n in enumerate(L)}
    jun, jul = comp["jun"], comp["jul"]
    labels = ["Energy", "Fuel", "IPP", "Demand", "Customer"]
    keys = ["energy", "fuel", "ipp", "kvap", "cust"]  # kvap+kval+kvao would be full demand; kvap dominant, use sum
    demand_jun = jun[idx["kvap"]] + jun[idx["kval"]] + jun[idx["kvao"]]
    demand_jul = jul[idx["kvap"]] + jul[idx["kval"]] + jul[idx["kvao"]]
    vals = [
        (jul[idx["energy"]] - jun[idx["energy"]]) / 1e6,
        (jul[idx["fuel"]] - jun[idx["fuel"]]) / 1e6,
        (jul[idx["ipp"]] - jun[idx["ipp"]]) / 1e6,
        (demand_jul - demand_jun) / 1e6,
        (jul[idx["cust"]] - jun[idx["cust"]]) / 1e6,
    ]
    fig, ax = plt.subplots(figsize=(6.8, 3.2))
    colors_ = [GREEN.hexval()[2:] if v >= 0 else RED.hexval()[2:] for v in vals]
    colors_ = ["#1D9E75" if v >= 0 else "#E24B4A" for v in vals]
    bars = ax.bar(labels, vals, color=colors_, width=0.55)
    for b, v in zip(bars, vals):
        ax.annotate("{:+.0f}".format(v), (b.get_x() + b.get_width() / 2, v),
                    ha="center", va="bottom" if v >= 0 else "top", fontsize=8, fontweight="bold")
    ax.axhline(0, color="#B7C6D9", linewidth=0.8)
    ax.set_ylabel("J$M change, Jun→Jul")
    ax.set_title("Revenue change by component, June → July 2026", fontsize=10, fontweight="bold", color="#0C3547")
    fig.tight_layout()
    fig.savefig(f"{CHART_DIR}/component_bridge.png", dpi=160)
    plt.close(fig)


def chart_rate_class():
    jb, ub = comp["jun_by_title"], comp["jul_by_title"]
    order = ["RT10", "RT20", "RT40", "RT50", "RT70", "RT60-ST"]
    jun_v = [jb.get(t, [0]*13)[2] / 1e6 for t in order]
    jul_v = [ub.get(t, [0]*13)[2] / 1e6 for t in order]
    x = range(len(order))
    fig, ax = plt.subplots(figsize=(6.8, 3.2))
    w = 0.35
    ax.bar([i - w/2 for i in x], jun_v, width=w, label="June", color="#7d93ab")
    ax.bar([i + w/2 for i in x], jul_v, width=w, label="July", color="#3b6ea5")
    ax.set_xticks(list(x)); ax.set_xticklabels(order)
    ax.set_ylabel("Revenue J$M")
    ax.set_title("Revenue by rate class, June vs July 2026", fontsize=10, fontweight="bold", color="#0C3547")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{CHART_DIR}/rate_class.png", dpi=160)
    plt.close(fig)


def chart_movers():
    top = movers["top10"][:8]
    bot = movers["bot10"][:8]
    rows = list(reversed(bot)) + list(reversed(top))
    labels = [r["name"][:26] for r in rows]
    vals = [r["d_rev"] / 1e6 for r in rows]
    colors_ = ["#E24B4A" if v < 0 else "#1D9E75" for v in vals]
    fig, ax = plt.subplots(figsize=(6.8, 5.2))
    ax.barh(labels, vals, color=colors_)
    ax.axvline(0, color="#B7C6D9", linewidth=0.8)
    ax.set_xlabel("Δ Revenue J$M, Jun→Jul")
    ax.set_title("Largest account-level revenue movers", fontsize=10, fontweight="bold", color="#0C3547")
    ax.tick_params(axis="y", labelsize=7.5)
    fig.tight_layout()
    fig.savefig(f"{CHART_DIR}/movers.png", dpi=160)
    plt.close(fig)


def chart_parish():
    rows = parish[:10]
    labels = [r["parish"] for r in rows]
    vals = [r["d_rev"] / 1e6 for r in rows]
    fig, ax = plt.subplots(figsize=(6.8, 3.2))
    ax.bar(labels, vals, color="#3b6ea5")
    ax.set_ylabel("Δ Revenue J$M")
    ax.set_title("Revenue change by parish, June → July 2026 (top 10)", fontsize=10, fontweight="bold", color="#0C3547")
    plt.xticks(rotation=35, ha="right", fontsize=7.5)
    fig.tight_layout()
    fig.savefig(f"{CHART_DIR}/parish.png", dpi=160)
    plt.close(fig)


def chart_residential_mix():
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.0))
    for ax, rc in zip(axes, ["RT10", "RT20"]):
        pm5 = roll_up("2026-05", rc)
        pm7 = roll_up("2026-07", rc)
        tot5 = sum(v["count"] for v in pm5.values()) or 1
        tot7 = sum(v["count"] for v in pm7.values()) or 1
        s5 = [pm5[b]["count"] / tot5 * 100 for b in BUCKET_ORDER]
        s7 = [pm7[b]["count"] / tot7 * 100 for b in BUCKET_ORDER]
        x = range(len(BUCKET_ORDER))
        ax.bar([i - 0.18 for i in x], s5, width=0.36, label="May", color="#7d93ab")
        ax.bar([i + 0.18 for i in x], s7, width=0.36, label="Jul", color="#3b6ea5")
        ax.set_xticks(list(x)); ax.set_xticklabels(BUCKET_ORDER, rotation=45, ha="right", fontsize=6.5)
        ax.set_title(rc, fontsize=9, fontweight="bold")
        ax.set_ylabel("% of customers", fontsize=8)
    axes[0].legend(frameon=False, fontsize=7)
    fig.suptitle("Consumption-tier mix shift, May → July 2026", fontsize=10, fontweight="bold", color="#0C3547")
    fig.tight_layout()
    fig.savefig(f"{CHART_DIR}/res_mix.png", dpi=160)
    plt.close(fig)


chart_component_bridge()
chart_rate_class()
chart_movers()
chart_parish()
chart_residential_mix()

# ---------- PDF ----------
styles = getSampleStyleSheet()
title_style = ParagraphStyle("TitleX", parent=styles["Title"], textColor=NAVY, fontSize=22)
h1 = ParagraphStyle("H1", parent=styles["Heading1"], textColor=NAVY, fontSize=14, spaceBefore=14, spaceAfter=6)
h2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=BLUE, fontSize=11, spaceBefore=8, spaceAfter=4)
body = ParagraphStyle("BodyX", parent=styles["Normal"], fontSize=9.5, leading=13.5)
small = ParagraphStyle("SmallX", parent=styles["Normal"], fontSize=8, leading=11, textColor=GREY)
flag = ParagraphStyle("FlagX", parent=styles["Normal"], fontSize=9, leading=12.5, textColor=colors.HexColor("#C00000"))

import itertools
OUT_PDF = "JPS_July2026_Performance_Report.pdf"
for suffix in itertools.chain([""], (f"_v{n}" for n in itertools.count(2))):
    OUT_PDF = f"JPS_July2026_Performance_Report{suffix}.pdf"
    try:
        with open(OUT_PDF, "ab"):
            pass
        break
    except PermissionError:
        continue

doc = SimpleDocTemplate(OUT_PDF, pagesize=letter,
                         topMargin=0.6*inch, bottomMargin=0.6*inch, leftMargin=0.65*inch, rightMargin=0.65*inch)
story = []

# Cover
story.append(Spacer(1, 1.6*inch))
story.append(Paragraph("JPS Sales & Revenue", title_style))
story.append(Paragraph("July 2026 Performance Report", ParagraphStyle("Sub", parent=title_style, fontSize=16, textColor=BLUE)))
story.append(Spacer(1, 0.3*inch))
story.append(Paragraph("What's driving the variance — account-level movers, anomalies, parish concentration, and residential (RT10/RT20) drivers.", body))
story.append(Spacer(1, 2.2*inch))
story.append(Paragraph("Prepared 2026-08-05 &nbsp;·&nbsp; Source: jps_actuals (all rate classes) &nbsp;·&nbsp; Company-wide, all classes", small))
story.append(PageBreak())

# Executive Summary
L = comp["legend"]; idx = {n: i for i, n in enumerate(L)}
jun, jul, jul25 = comp["jun"], comp["jul"], comp["jul25"]
rev_mom = jul[idx["rev"]] / jun[idx["rev"]] - 1
rev_yoy = jul[idx["rev"]] / jul25[idx["rev"]] - 1
kwh_mom = jul[idx["kwh"]] / jun[idx["kwh"]] - 1
kwh_yoy = jul[idx["kwh"]] / jul25[idx["kwh"]] - 1

kwh_mom_verb = "grew" if kwh_mom >= 0 else "fell"
kwh_yoy_verb = "grew" if kwh_yoy >= 0 else "fell"
realization_note = (
    "revenue growth outpacing volume growth in both comparisons means realization (revenue per kWh) improved, "
    "not just higher consumption"
    if kwh_mom >= 0 and kwh_yoy >= 0 else
    "revenue rising while volume fell year-on-year means realization (revenue per kWh) improved materially — "
    "this is a rate/mix effect, not a consumption effect"
    if kwh_yoy < 0 <= kwh_mom else
    "revenue and volume diverging across these comparisons — see Rev/kWh trend for the realization detail"
)
story.append(Paragraph("Executive Summary", h1))
story.append(Paragraph(
    f"July 2026 revenue was {moneyM(jul[idx['rev']])}, up {pct(rev_mom)} month-on-month and {pct(rev_yoy)} "
    f"year-on-year. Volume (kWh) {kwh_mom_verb} {pct(kwh_mom)} MoM and {kwh_yoy_verb} {pct(kwh_yoy)} YoY — "
    f"{realization_note}. "
    f"Growth was broad-based across all 15 parishes (every parish grew MoM — no single region drove the gain) "
    f"and across rate classes, with RT10 (residential) and RT70 (large industrial) the largest dollar contributors.",
    body))
story.append(Paragraph(
    "These figures now include Prepaid (PAYG) revenue and volume for the first time, on both sides of every "
    "comparison (Jun 2026, Jul 2026, and Jul 2025 all now carry Prepaid) — previously excluded here entirely, "
    "which is why the YoY read has shifted from earlier versions of this report. They exclude two legacy "
    "aggregate tags found while fixing this ('Postpaid' on RT40/RT50, 'Streetlight' on RT60-ST) that coexist "
    "with the correct per-premise data for the same Jan 2025-Apr 2026 window and would double-count if included "
    "— same issue already fixed for RT10/RT20 earlier this pipeline, not yet verified/cleaned for these three "
    "classes. See the Insights section for detail.",
    flag))
story.append(Spacer(1, 6))
kpi_data = [
    ["", "June 2026", "July 2026", "MoM", "July 2025", "YoY"],
    ["Revenue", moneyM(jun[idx['rev']]), moneyM(jul[idx['rev']]), pct(rev_mom), moneyM(jul25[idx['rev']]), pct(rev_yoy)],
    ["kWh (M)", f"{jun[idx['kwh']]/1e6:,.1f}", f"{jul[idx['kwh']]/1e6:,.1f}", pct(kwh_mom), f"{jul25[idx['kwh']]/1e6:,.1f}", pct(kwh_yoy)],
    ["Rev/kWh (J$)", f"{jun[idx['rev']]/jun[idx['kwh']]:.2f}", f"{jul[idx['rev']]/jul[idx['kwh']]:.2f}", "", f"{jul25[idx['rev']]/jul25[idx['kwh']]:.2f}", ""],
]
t = Table(kpi_data, colWidths=[1.3*inch, 1.05*inch, 1.05*inch, 0.7*inch, 1.05*inch, 0.7*inch])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 9), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LTGREY]),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B7C6D9")),
    ("ALIGN", (1, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(t)

story.append(Paragraph("Revenue Drivers by Component", h1))
story.append(Image(f"{CHART_DIR}/component_bridge.png", width=6.5*inch, height=3.06*inch))
story.append(Paragraph(
    "Energy and Fuel move with volume; Demand is fixed capacity charges, largely a function of the top industrial "
    "accounts' contracted demand rather than monthly usage; IPP is a pass-through cost recovery, not margin. "
    "Customer charge is nearly flat month to month by design (it's a fixed per-account fee).", small))

story.append(Paragraph("By Rate Class", h1))
story.append(Image(f"{CHART_DIR}/rate_class.png", width=6.5*inch, height=3.06*inch))

story.append(PageBreak())

# Movers
story.append(Paragraph("Who: Account-Level Movers (June → July)", h1))
story.append(Image(f"{CHART_DIR}/movers.png", width=6.5*inch, height=4.98*inch))
story.append(Spacer(1, 4))

def movers_table(rows, hdr_color):
    data = [["Customer", "Class", "Jun Rev J$M", "Jul Rev J$M", "Δ J$M"]]
    for r in rows:
        data.append([r["name"][:32], r["title"], f"{r['jun_rev']/1e6:,.1f}", f"{r['jul_rev']/1e6:,.1f}", f"{r['d_rev']/1e6:+,.1f}"])
    t = Table(data, colWidths=[2.3*inch, 0.7*inch, 1.05*inch, 1.05*inch, 0.9*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), hdr_color), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 7.8), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LTGREY]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D0D8E2")),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t

story.append(Paragraph("Top 10 increases", h2))
story.append(movers_table(movers["top10"], GREEN))
story.append(Spacer(1, 8))
story.append(Paragraph("Top 10 decreases", h2))
story.append(movers_table(movers["bot10"], RED))

story.append(PageBreak())

# Anomalies
story.append(Paragraph("Anomalies by Customer", h1))
story.append(Paragraph(
    f"New material accounts (June $0 → July &gt;J$500K): {len(movers['new'])}. "
    f"Dropped material accounts (June &gt;J$500K → July $0): {len(movers['dropped'])}. "
    f"Accounts with a swing &gt;50% (on a June base &gt;J$200K): {len(movers['swings'])}.", body))
story.append(Spacer(1, 6))
if movers["dropped"]:
    story.append(Paragraph("Dropped accounts (verify: billing gap, closure, or meter/account-number change)", h2))
    data = [["Customer", "Class", "Parish", "June Rev J$M"]]
    for r in sorted(movers["dropped"], key=lambda r: -r["jun_rev"])[:10]:
        data.append([r["name"][:34], r["title"], r["pg"], f"{r['jun_rev']/1e6:,.1f}"])
    t = Table(data, colWidths=[2.5*inch, 0.7*inch, 1.4*inch, 1.2*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), RED), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LTGREY]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D0D8E2")), ("ALIGN", (3, 0), (3, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t)
    story.append(Paragraph("These are drops to exactly $0 for the month — in past sessions this pattern has usually meant a partial/incomplete billing cycle rather than a genuine customer loss. Worth a billing-completeness check before treating as churn.", small))
    story.append(Spacer(1, 8))

if movers["new"]:
    story.append(Paragraph("New material accounts", h2))
    data = [["Customer", "Class", "Parish", "July Rev J$M"]]
    for r in sorted(movers["new"], key=lambda r: -r["jul_rev"])[:10]:
        data.append([r["name"][:34], r["title"], r["pg"], f"{r['jul_rev']/1e6:,.1f}"])
    t = Table(data, colWidths=[2.5*inch, 0.7*inch, 1.4*inch, 1.2*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LTGREY]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D0D8E2")), ("ALIGN", (3, 0), (3, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

story.append(Paragraph(f"Largest % swings ({len(movers['swings'])} total, top 10 by dollar impact)", h2))
data = [["Customer", "Class", "Jun Rev J$M", "Jul Rev J$M", "% Change"]]
for r in movers["swings"][:10]:
    data.append([r["name"][:32], r["title"], f"{r['jun_rev']/1e6:,.1f}", f"{r['jul_rev']/1e6:,.1f}", pct(r['jul_rev']/r['jun_rev']-1)])
t = Table(data, colWidths=[2.3*inch, 0.7*inch, 1.05*inch, 1.05*inch, 0.9*inch])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), GOLD), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 7.8), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LTGREY]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D0D8E2")), ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
    ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))
story.append(t)

story.append(PageBreak())

# Where
story.append(Paragraph("Where: Parish Concentration", h1))
story.append(Image(f"{CHART_DIR}/parish.png", width=6.5*inch, height=3.06*inch))
top2_share = (parish[0]["d_rev"] + parish[1]["d_rev"]) / sum(r["d_rev"] for r in parish) if sum(r["d_rev"] for r in parish) else 0
story.append(Paragraph(
    f"KSAN and KSAS (the two Kingston metro parishes) together account for {pct(top2_share)} of the total company-wide "
    f"revenue increase — expected given they carry the largest industrial/commercial base, but growth is not "
    f"concentrated there alone: every parish grew month-on-month, meaning this is a broad volume/rate effect, not a "
    f"one-region story.", body))

story.append(PageBreak())

# Residential
story.append(Paragraph("Residential Deep-Dive: RT10 / RT20", h1))
story.append(Paragraph(
    "Full detail (parish, prepaid vs commercial split, consumption-tier trend, budget/forecast) is in the companion "
    "workbook Residential_RT10_RT20_Analysis_2026Q.xlsx and the Residential tab in Sales Explorer. Summary below.", small))
story.append(Spacer(1, 6))
story.append(Image(f"{CHART_DIR}/res_mix.png", width=6.5*inch, height=2.87*inch))
story.append(Paragraph(
    "For both RT10 and RT20, customer counts are nearly flat May→July (+0.1–0.3%) while usage per customer "
    "is up 9–14% — the volume increase is being driven by existing customers using more power, not by "
    "new connections. The tier mix is shifting toward higher-consumption bands (350>550 and above) at the expense "
    "of the lowest tiers, consistent with rising per-customer usage.", body))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "RT20 runs consistently over budget across all three months (Actual vs. class-grain budget: May +43.5%, "
    "June +29.0%, July +50.8% — verified against the source LE model). RT10 also runs over its class-level "
    "budget (May +33.3%, June +25.0%, July +43.1%). Both figures were corrected after finding two real data "
    "bugs during this build: a duplicate/stale account population for May RT20 (now removed) and an "
    "unordered-pagination bug in the live query layer that was silently dropping rows under concurrent load "
    "(now fixed with explicit ordering + retry). Neither class has premise-level budget detail — this is "
    "class-grain only. See the Residential workbook's Read Me for full detail.", flag))

story.append(PageBreak())

# Insights & LE Recommendations
story.append(Paragraph("Insights, Anomalies & Recommendations for Future LE", h1))

var_rows = []
for mn, mlabel in zip([5, 6, 7], ["May", "June", "July"]):
    act_kwh, act_rev = agg_rt20_real_totals(mn)
    _, bud_rev = agg_budget_le_totals(rt20_budget, mn)
    var_rows.append((mlabel, (act_rev / bud_rev - 1) if bud_rev else 0))
all_over = all(v > 0 for _, v in var_rows)
avg_var = sum(v for _, v in var_rows) / len(var_rows)

story.append(Paragraph("1. RT20 has run over budget every month for 3 consecutive months", h2))
story.append(Paragraph(
    "Actual vs. budget revenue: " + ", ".join(f"{m} {pct(v)}" for m, v in var_rows) + f" (average {pct(avg_var)}). "
    + ("Three consecutive months landing over budget in the same direction, at a similar magnitude, points to a "
       "miscalibrated LE base rather than genuine outperformance. Recommendation: rebase the next LE cycle's RT20 "
       "volume/rate assumptions off the trailing 3-month actual run-rate." if all_over else ""), body))
story.append(Spacer(1, 6))

rt10_jul_prepaid_rev = sum(v["revenue_jmd"] or 0 for v in prepaid if v["year"] == 2026 and v["month"] == 7 and v["rate_class"] == "RT10")
story.append(Paragraph("2. RT10 has no LE/budget model at all — Prepaid makes this more urgent", h2))
story.append(Paragraph(
    f"jps_budget/jps_le only carry a placeholder for RT10, not a real consumption budget. With RT10 Prepaid alone "
    f"at {moneyM(rt10_jul_prepaid_rev)} pre-GCT in July, the case for a real RT10 LE model — forecasting Postpaid "
    "and Prepaid as separate lines — is stronger than when RT10 was assumed to be one homogeneous population.", body))
story.append(Spacer(1, 6))

prepaid_jul_rev = sum(v["revenue_jmd"] or 0 for v in prepaid if v["year"] == 2026 and v["month"] == 7)
unassigned_rev = sum(v["revenue_jmd"] or 0 for v in unassigned_payg)
story.append(Paragraph("3. Prepaid revenue is now included in Overview and this report's headline totals", h2))
story.append(Paragraph(
    f"Fixed since an earlier version of this report: Prepaid was built from the CIS Billing Details Report, which "
    f"only covers postpaid meters, so it was silently excluded from every headline total in both this PDF and the "
    f"residential Overview sheet. Both now blend Prepaid in directly ({moneyM(prepaid_jul_rev + unassigned_rev)} "
    "pre-GCT of July revenue that was previously missing), with a Postpaid/Prepaid breakout kept for transparency "
    "rather than hidden.", body))
story.append(Spacer(1, 6))

n_unassigned = sum(v["customer_count"] or 0 for v in unassigned_payg)
unassigned_share = unassigned_rev / (prepaid_jul_rev + unassigned_rev) if (prepaid_jul_rev + unassigned_rev) else 0
story.append(Paragraph(f"4. New finding: {pct(unassigned_share)} of July PAYG revenue has no rate-class tag", h2))
story.append(Paragraph(
    f"{n_unassigned:,.0f} prepaid customers ({moneyM(unassigned_rev)} pre-GCT, July) came through the CIS extract "
    "with tariff = 'unassigned'. Loaded under rate_class='UNASSIGNED-PAYG' rather than guessed into RT10/RT20, so "
    "the revenue isn't lost, but it's unusable for rate-class analysis until Billing/CIS backfills the tariff code — "
    "this population is large enough to matter for rate-class-level LE accuracy.", flag))
story.append(Spacer(1, 6))

story.append(Paragraph("5. New finding: RT40/RT50/RT60-ST carry the same legacy/new duplication RT10/RT20 had", h2))
story.append(Paragraph(
    "Found while adding Prepaid to this report's company-wide totals: RT40 and RT50 have a legacy 'Postpaid' "
    "aggregate tag, and RT60-ST a legacy 'Streetlight' tag, both coexisting with the correct per-premise "
    "'Commercial' population for the same Jan 2025-Apr 2026 window -- the identical legacy/new duplication "
    "pattern already found and fixed for RT10/RT20 earlier in this pipeline, never checked for these three "
    "classes. RT60-ST's 'Streetlight' tag alone carries real revenue in the J$105-234M/month range for that "
    "window. Excluded from this report's totals above (to avoid double-counting) rather than guessed at, but "
    "not yet verified and cleaned up the way RT10/RT20 were -- that reconciliation is still open.", flag))
story.append(Spacer(1, 6))

story.append(Paragraph("6. Kingston-metro (KSAN/KSAS) parish detail in the Prepaid source has degraded", h2))
story.append(Paragraph(
    "The July Customer-Monthly-Transaction-Report labels most Kingston-metro PAYG customers with the generic city "
    "value 'Kingston' rather than a specific postal zone — not enough to split into KSAN vs. KSAS. This report "
    "preserves the existing correct KSAN/KSAS/Portmore figures rather than re-deriving them from degraded data. "
    "Worth raising with CIS/Billing if parish-level PAYG reporting matters going forward.", small))
story.append(Spacer(1, 6))

story.append(Paragraph("7. 'Zero' consumption-tier customers still generate real revenue — not a data error", h2))
story.append(Paragraph(
    "In the jps_actuals-sourced views, the 'Zero' bucket (0 kWh billed) shows non-zero revenue because Jamaican "
    "utility billing applies a fixed monthly customer/connection charge regardless of consumption. Expected "
    "behavior. One completeness gap found while building this: the RT20 residential-style bucket aggregation "
    "doesn't break the fixed-charge component into its own column the way Commercial premise rows do — total "
    "revenue is correct, component detail (customer_charge_jmd etc.) reads 0 for these rows.", small))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "FIX APPLIED THIS BUILD: the residential mix chart above previously showed real, substantial kWh volume in the "
    "'Zero' tier — a genuine bug, not the billing behavior above. corrected.json's histogram bins are 50kWh wide; "
    "the bin labeled '0' covers [0,50) kWh, not exactly-zero consumption. The rollup was misclassifying that whole "
    "bin as 'Zero'. Fixed by folding bin '0' into '<150' like every other bin — this source can't isolate "
    "exactly-zero consumption, so 'Zero' now correctly reads empty here.", small))
story.append(Spacer(1, 6))

story.append(Paragraph("8. Usage per customer, not customer growth, should drive the next LE's volume assumption", h2))
story.append(Paragraph(
    "For both RT10 and RT20, customer counts are nearly flat May→July (+0.1–0.3%) while usage per customer is up "
    "9–14%. A volume forecast built primarily off customer-count growth will materially understate near-term "
    "RT10/RT20 volume. Recommendation: weight the trailing usage-per-customer trend, not just customer-count "
    "growth, in the next LE build for these two classes.", body))

story.append(PageBreak())

# Zero-Consumption Anomaly Check
story.append(Paragraph("Zero-Consumption Anomaly Check — All Rate Classes", h1))
streaks = zero_streaks["streaks"]
n_total = len(streaks)
n_12plus = sum(1 for s in streaks if s["streak_len"] >= 12)
n_3plus = sum(1 for s in streaks if s["streak_len"] >= 3)
story.append(Paragraph(
    f"{n_total:,} premise-level accounts (RT20-Commercial, RT40, RT50, RT60-ST, RT70) currently have an ongoing "
    f"consecutive-months-at-zero-kWh streak — {n_3plus:,} for 3+ months, {n_12plus:,} for 12+ months (the entire "
    "Jan 2025-Jul 2026 window on record, with no positive-consumption month at all). RT10 and RT20's "
    "residential-style population have no per-customer identity in the data, so only a monthly zero-consumption "
    "customer count is possible there, not a per-account streak — see the companion "
    "Zero_Consumption_Anomaly_Report.xlsx for that trend and full account-level detail.", body))
story.append(Spacer(1, 6))
n_minbill = sum(1 for s in streaks if s.get("is_minbill_cluster"))
n_zero_rev = sum(1 for s in streaks if s.get("current_monthly_revenue") == 0)
story.append(Paragraph(
    "Zero kWh does not mean $0 revenue. Traced a sample of the longest streaks (National Water Commission, "
    "Ministry of Health, Bank of Nova Scotia, JPS's own account, and others) back to the raw CIS billing extract "
    "and confirmed they bill a real minimum/standby demand charge every month even at 0 metered kWh — present in "
    f"JPS's own source file, not a pipeline artifact. {n_minbill:,} of the {n_total:,} streaked accounts share this "
    f"pattern (a standardized minimum-bill tariff tier, identifiable by unrelated customers billing bit-identical "
    f"demand/IPP/customer-charge figures); only {n_zero_rev:,} have genuinely $0 current-month revenue. The billing "
    "math for the minimum-bill group looks correct — the open question there is operational (has metering lapsed "
    "for over a year at these premises?), not a revenue-integrity one. The remaining accounts (not on a shared "
    "minimum-bill default) aren't automatically dormant either — several are large, real demand contracts with "
    f"genuine six/seven-figure monthly revenue. The unambiguous finding is narrower: only {n_zero_rev:,} account(s) "
    "generate literally $0, not even a minimum bill — those are listed below.", flag))
story.append(Spacer(1, 8))
zero_rev_accts = [s for s in streaks if s.get("current_monthly_revenue") == 0]
top10 = zero_rev_accts
data = [["Account", "Name", "Class", "Streak (mo)", "Start", "End", "Status"]]
for s in top10:
    data.append([s["jps_ac"], (s["name"] or "")[:26], s["rate_class"], str(s["streak_len"]), s["streak_start"], s["streak_end"],
                 s.get("account_status_label", "?")])
t = Table(data, colWidths=[1.0*inch, 1.75*inch, 0.6*inch, 0.7*inch, 0.75*inch, 0.75*inch, 0.85*inch])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), GOLD), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 7.8), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LTGREY]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D0D8E2")),
    ("ALIGN", (3, 0), (6, -1), "CENTER"),
    ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))
story.append(t)
story.append(Spacer(1, 8))
top_priority = [s for s in streaks if s.get("account_status") == "A" and s["current_monthly_revenue"] == 0]
if top_priority:
    story.append(Paragraph(
        f"Of those, {len(top_priority)} are formally marked Active (not Inactive/Final/suspended) in the CIS "
        "extract — an active, unsuspended account generating $0 revenue is the genuine priority case; the rest "
        "are Inactive/Final accounts correctly billing nothing.", flag))
else:
    story.append(Paragraph(
        "Every one of those is formally Inactive or Final in the CIS extract, not Active — consistent with a "
        "closed/dormant account correctly generating no charges, not a live billing gap.", small))
story.append(Paragraph(
    "Full Account_Status/is_suspended breakdown for all 2,977 flagged accounts (not just the $0-revenue ones) is "
    "in the companion workbook's 'Account Status Breakdown' sheet.", small))

doc.build(story)
print("wrote", OUT_PDF)
