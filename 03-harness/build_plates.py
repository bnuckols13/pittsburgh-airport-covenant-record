#!/usr/bin/env python3
"""build_plates.py — render the plates from the CSVs.

Every coordinate is computed here from data. Run with --check to re-render in
memory and byte-diff against the committed HTML; it exits 1 on drift, which is
the SOP-104 constraint that nobody types a coordinate.

    python 03-harness/build_plates.py
    python 03-harness/build_plates.py --check
"""
import csv, hashlib, html, io, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import charts as ch
from charts import Frame, Scale, Band, Panel, C, esc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "02-data")
BUILT = "2026-08-31"          # data, never datetime.now(); --check must survive tomorrow


def rows(name):
    """Strict reader. A ragged row is a silently truncated field."""
    p = os.path.join(DATA, name)
    with io.open(p, encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        out = []
        for i, r in enumerate(rd, 2):
            if None in r or any(k is None for k in r):
                raise SystemExit(f"{name} line {i}: ragged row")
            out.append(r)
    if not out:
        raise SystemExit(f"{name}: empty")
    return out


def num(v):
    return float(str(v).replace(",", "").replace("$", "").strip())


# ---------------------------------------------------------------- the plates

def plate_mechanism():
    n = rows("flow-of-funds.csv")
    e = rows("flow-of-funds-edges.csv")
    f = Frame(w=980, h=520, l=20, r=20, t=26, b=20)
    body = ch.flow_diagram(f, n, e)
    aria = ("The flow of funds. Revenues less operation and maintenance become Net "
            "Revenues. Other Pledged Revenues are designated into Net Revenues at the "
            "Authority's annual discretion. Eleven priorities follow in order, and the "
            "Coverage Account is ninth, funded monthly at the Authority's discretion and "
            "capped at 25 percent of annual debt service. The 1.25 test counts Net "
            "Revenues together with the Coverage Account.")
    return ch.svg(f, aria, body), n


def plate_reveal():
    r = [x for x in rows("coverage-table.csv") if x["vintage"] == "2025"]
    r.sort(key=lambda x: int(x["year"]))
    years = [x["year"] for x in r]
    printed = [num(x["coverage_as_printed"]) for x in r]
    alone = [num(x["coverage_on_net_revenues_alone"]) for x in r]

    f = Frame(w=980, h=330, l=52, r=20, t=64, b=46)
    shared = Scale(*ch.domain(printed + alone, include=[1.25]), f.ybot, f.ytop)
    ticks = ch.nice_ticks(shared.d0, shared.d1, 5)
    ch.assert_in_domain(shared, printed + alone, "plate E-2")

    def panel_printed(fr, sc):
        b = Band(years, fr.x0, fr.x1)
        out = []
        pts = [(b.center(x["year"]), sc(num(x["coverage_as_printed"]))) for x in r]
        out.append(ch.gapped_path(pts, C["blue"]))
        for x in r:
            out.append(ch.mark("A", C["blue"], b.center(x["year"]),
                               sc(num(x["coverage_as_printed"]))))
        out.append(ch.axis_x_band(fr, b))
        return "".join(out)

    def panel_account(fr, sc):
        b = Band(years, fr.x0, fr.x1)
        out = []
        for x in r:
            cx = b.center(x["year"])
            lo, hi = num(x["coverage_on_net_revenues_alone"]), num(x["coverage_as_printed"])
            out.append(f'<line x1="{cx:.1f}" y1="{sc(lo):.1f}" x2="{cx:.1f}" y2="{sc(hi):.1f}" '
                       f'stroke="{C["aqua"]}" stroke-width="7" opacity="0.5"/>')
            out.append(ch.mark("A", C["blue"], cx, sc(lo)))
            out.append(f'<circle cx="{cx:.1f}" cy="{sc(hi):.1f}" r="4.2" fill="none" '
                       f'stroke="{C["blue"]}" stroke-width="1.6"/>')
        out.append(ch.axis_x_band(fr, b))
        return "".join(out)

    def panel_alone(fr, sc):
        b = Band(years, fr.x0, fr.x1)
        out = []
        pts = [(b.center(x["year"]), sc(num(x["coverage_on_net_revenues_alone"]))) for x in r]
        out.append(ch.gapped_path(pts, C["blue"]))
        for x in r:
            v = num(x["coverage_on_net_revenues_alone"])
            cx = b.center(x["year"])
            out.append(ch.mark("A", C["blue"], cx, sc(v)))
            if x["below_1_25"] == "yes":
                out.append(f'<text class="val" x="{cx:.1f}" y="{sc(v)+16:.1f}" '
                           f'text-anchor="middle">{v:.2f}</text>')
        out.append(ch.axis_x_band(fr, b))
        return "".join(out)

    panels = [
        Panel("1. As printed", "every year clears", panel_printed),
        Panel("2. The account", "the discretionary deposit", panel_account),
        Panel("3. Pledged alone", "five of six under the line", panel_alone),
    ]
    body = ch.small_multiples(f, panels, shared, ticks,
                              rules=[(1.25, "1.25")], fmt=lambda v: f"{v:.2f}")
    n_below = sum(1 for x in r if x["below_1_25"] == "yes")
    aria = (f"Three panels sharing one vertical scale from {shared.d0:.2f} to {shared.d1:.2f}. "
            f"As printed, every forecast year clears 1.25. The middle panel shows the "
            f"Coverage Account's contribution as the segment between the two readings. On "
            f"pledged Net Revenues alone, {n_below} of {len(r)} years come in under 1.25.")
    return ch.svg(f, aria, body), shared, r


def plate_dumbbell():
    r = rows("coverage-table.csv")
    labels = [f'{x["vintage"]} {x["scenario"].split()[0]} {x["year"]}' for x in r]
    for x, lab in zip(r, labels):
        x["_lab"] = lab
    lo = [num(x["coverage_on_net_revenues_alone"]) for x in r]
    hi = [num(x["coverage_as_printed"]) for x in r]
    f = Frame(w=980, h=380, l=56, r=24, t=30, b=96)
    sc = Scale(*ch.domain(lo + hi, include=[1.25]), f.ybot, f.ytop)
    ch.assert_in_domain(sc, lo + hi, "plate II")
    b = Band(labels, f.x0, f.x1)
    ticks = ch.nice_ticks(sc.d0, sc.d1, 5)
    body = (ch.axis_y(f, sc, ticks, lambda v: f"{v:.2f}")
            + ch.rule_h(f, sc, 1.25, "1.25, the covenant")
            + ch.dumbbell(f, sc, b, r, "coverage_on_net_revenues_alone",
                          "coverage_as_printed", "_lab", C["blue"], C["blue"])
            + ch.axis_x_band(f, b, rotate=True))
    n_below = sum(1 for x in r if x["below_1_25"] == "yes")
    aria = ("One dumbbell for each forecast year in the 2021 and 2025 statements, kept "
            "apart by vintage and by recovery case and never added together. The open dot "
            "is the ratio as printed; the filled dot is the ratio on pledged Net Revenues "
            "alone. In the 2025 forecast, five of six filled dots fall below the 1.25 line.")
    return ch.svg(f, aria, body), r, sc.d0, sc.d1


def plate_opr():
    it = rows("other-pledged-revenue-itemized.csv")
    years = [str(y) for y in range(2019, 2031)]
    fed = {y: 0.0 for y in years}
    gas = {y: 0.0 for y in years}
    gam = {y: 0.0 for y in years}
    for row in it:
        cat = row["category"]
        tgt = {"federal pandemic aid": fed, "federal disaster aid": fed,
               "gas royalty": gas, "slot-machine tax": gam}.get(cat)
        if tgt is None:
            continue
        for y in years:
            tgt[y] += num(row[y])
    f = Frame(w=980, h=340, l=62, r=24, t=34, b=54)
    tot = [fed[y] + gas[y] + gam[y] for y in years]
    sc = Scale(0, max(tot) * 1.12, f.ybot, f.ytop)
    b = Band(years, f.x0, f.x1)
    ticks = ch.nice_ticks(0, sc.d1, 5)
    body = (ch.axis_y(f, sc, ticks, lambda v: f"${v/1000:.0f}m")
            + ch.stacked_bars(f, sc, b, years,
                              [("federal aid", fed, C["aqua"]),
                               ("gas royalty", gas, C["yellow"]),
                               ("slot-machine tax", gam, C["blue"])])
            + ch.axis_x_band(f, b))
    # Direct labels, not a legend: the reader should not have to look away.
    key = []
    for i, (nm, col) in enumerate([("federal aid", C["aqua"]), ("gas royalty", C["yellow"]),
                                   ("slot-machine tax", C["blue"])]):
        kx = f.x0 + i * 168
        key.append(f'<rect x="{kx}" y="{f.ytop-22}" width="11" height="11" fill="{col}"/>')
        key.append(f'<text class="ax" x="{kx+16}" y="{f.ytop-12}">{nm}</text>')
    body += "".join(key)
    aria = ("Other Pledged Revenues by component, 2019 to 2030, in thousands. Federal "
            "pandemic and disaster aid is the whole of the designation from 2020 through "
            "2023. Nothing is designated in 2024. Gas royalty is designated only in 2019. "
            "Slot-machine tax is designated in 2019 and then not again until the 2025 "
            "forecast year.")
    return ch.svg(f, aria, body), {"federal": fed, "gas": gas, "gaming": gam, "years": years}


def plate_2026():
    r = rows("cpe-2026-claims.csv")
    r.sort(key=lambda x: int(x["order"]))
    labels = [x["label"] for x in r]
    vals = [num(x["cpe"]) for x in r]
    f = Frame(w=980, h=250, l=300, r=180, t=30, b=48)
    sc = Scale(*ch.domain(vals, pad=0.16), f.x0, f.x1)
    b = Band(labels, f.ytop + 18, f.ybot - 18)
    grades = {x["source_id"]: x for x in rows("source-grades.csv")}

    def gr(row):
        return grades.get(row.get("source", ""), {}).get("reliability", "C")

    body = ch.dot_plot(f, sc, b, r, "cpe", "label", gr, plot_key="plot")
    aria = ("What each bond document said 2026 would cost an airline per boarded "
            "passenger. Ordered by the vintage of the document, never by value. The "
            "$17.64 rests on no primary document and is annotated beside the axis "
            "rather than plotted.")
    return ch.svg(f, aria, body), r


def plate_budget():
    r = [x for x in rows("budget-revisions.csv")]
    drawn = [x for x in r if x["plot"] == "plot"]
    annotated = [x for x in r if x["plot"] != "plot"]
    labels = [f'{x["year"]} {x["label"]}' for x in r]
    for x, lab in zip(r, labels):
        x["_lab"] = lab
    vals = [num(x["amount_usd"]) for x in r]
    f = Frame(w=980, h=250, l=330, r=150, t=30, b=44)
    sc = Scale(0, max(vals) * 1.1, f.x0, f.x1)
    b = Band(labels, f.ytop + 18, f.ybot - 18)
    # The guard runs on the rows actually handed to the renderer, not on a list
    # already filtered, or it passes on evidence it was never shown.
    ch.assert_plottable(drawn, "plate VIII")
    body = ch.ranked_bars(f, sc, b, drawn, "amount_usd", "_lab",
                          fmt=lambda v: f"${v/1e9:.2f}bn")
    # Escalations are derived only between hashed figures. A percentage computed
    # off a newspaper number is that newspaper number wearing arithmetic.
    steps = []
    for prev, cur in zip(drawn, drawn[1:]):
        pct = (num(cur["amount_usd"]) / num(prev["amount_usd"]) - 1) * 100
        yrs = int(cur["year"]) - int(prev["year"])
        steps.append(f'<text class="ax" x="{f.x0-8}" y="{b.center(cur["_lab"])+16:.1f}" '
                     f'text-anchor="end">+{pct:.0f}% over {yrs} years</text>')
    for x in annotated:
        steps.append(f'<text class="ax" x="{f.x0+6}" y="{b.center(x["_lab"])+4:.1f}" '
                     f'fill="{C["muted"]}">${num(x["amount_usd"])/1e9:.2f}bn &#8212; reported, '
                     f'no document in this vault; not drawn</text>')
    aria = ("The project cost at four dates. The 2017 board figure is annotated from news "
            "coverage and carries no hashed document in this vault; the 2021, 2023 and "
            "2025 figures are the Authority's own.")
    return ch.svg(f, aria, body + "".join(steps)), r


def plate_cpe():
    r = rows("cpe-record.csv")
    rec = [x for x in r if x["series"] == "record"]
    f25 = sorted([x for x in r if x["series"] == "forecast25"], key=lambda x: int(x["year"]))

    # The document line is ONE table: the Authority's five-year statement of airline
    # costs per enplaned passenger at os-2025ab PDF 62. Taking the best-graded row per
    # year instead would silently pick between two Authority figures for one year, and
    # for 2024 it picked the budget over the actual. A line drawn through a set the
    # reader cannot name is not a series. Everything else is a mark.
    doc = sorted([x for x in rec if x["tier"] == "A" and x["basis"] == "acaa_residual"
                  and x["source_page"] == "PDF 62 (printed 52)"],
                 key=lambda x: int(x["year"]))
    if len({x["year"] for x in doc}) != len(doc):
        raise SystemExit("plate I: two values for one year on the line. Name one table.")
    off_line = [x for x in rec if x["tier"] == "A" and x["basis"] == "acaa_residual"
                and x not in doc]
    ch.assert_single_basis(doc, where="plate I document line")
    ch.assert_plottable(doc, "plate I document line")
    ch.assert_single_basis(f25, where="plate I forecast line")

    years = list(range(2011, 2031))
    vals = [num(x["cpe"]) for x in rec + f25]
    f = Frame(w=980, h=360, l=56, r=120, t=34, b=96)
    xs = Scale(2011, 2030, f.x0, f.x1)
    ys = Scale(*ch.domain(vals, pad=0.10), f.ybot, f.ytop)
    ch.assert_in_domain(ys, vals, "plate I")
    ticks = ch.nice_ticks(ys.d0, ys.d1, 5)

    # gaps: a year absent from the document record is a break, never a segment
    have = {int(x["year"]): x for x in doc}
    pts = []
    for y in range(min(have), max(have) + 1):
        pts.append((xs(y), ys(num(have[y]["cpe"]))) if y in have else None)

    out = [ch.axis_y(f, ys, ticks, lambda v: f"${v:,.2f}")]
    out.append(ch.gapped_path(pts, C["blue"]))
    out.append(ch.gapped_path([(xs(int(x["year"])), ys(num(x["cpe"]))) for x in f25],
                              C["orange"], dash="6 4"))
    for x in rec:
        out.append(ch.mark(x["tier"], C["aqua"] if x["basis"] == "faa_5100_127" else C["blue"],
                           xs(int(x["year"])), ys(num(x["cpe"]))))
    for x in f25:
        out.append(ch.mark(x["tier"], C["orange"], xs(int(x["year"])), ys(num(x["cpe"]))))
    out.append(ch.axis_x_years(f, xs, [2011, 2015, 2019, 2023, 2026, 2030]))
    out.append(ch.grade_key(f.x0, f.ybot + 42, C["ink2"]))

    missing = [y for y in range(min(have), max(have) + 1) if y not in have]
    cpe_lo, cpe_hi = ys.d0, ys.d1
    aria = ("What an airline was charged per boarded passenger at Pittsburgh. The solid "
            "line joins only the Authority's own documents on its own residual basis. "
            "Newspaper figures and the federal filing are drawn as marks and are never "
            "joined to it. Years absent from the record are gaps, not segments.")
    return ch.svg(f, aria, "".join(out)), {"doc": doc, "rec": rec, "missing": missing,
                                           "lo": cpe_lo, "hi": cpe_hi, "off": off_line}


def plate_spans():
    r = rows("term-structure.csv")
    f = Frame(w=980, h=230, l=56, r=40, t=44, b=44)
    starts = [num(x["start_year"]) for x in r]
    ends = [num(x["end_year"]) for x in r]
    sc = Scale(min(starts), max(ends), f.x0, f.x1)
    body = (ch.spans(f, sc, r, "start_year", "end_year", "item")
            + ch.axis_x_years(f, sc, [2021, 2028, 2035, 2042, 2049, 2056]))
    aria = ("Term lengths to scale. The bonds run to 2056. The airline agreements and the "
            "money committed under them end in 2028.")
    return ch.svg(f, aria, body), r


# ---------------------------------------------------------------- page

CSS = """
:root{--plane:#fbfaf7;--surface:#fff;--surface2:#f4f2ec;--ink:#1a1a1a;--ink2:#4a4a4a;
--muted:#6b6b6b;--grid:#e6e2d8;--axis:#b9b3a5;--ring:#d9d4c8;--blue:#1c5cab;
--blue-lt:#7ba7de;--aqua:#2b8a8a;--yellow:#b8860b;--orange:#c2570f;--red:#a8321e;}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--plane:#0f130f;
--surface:#181a17;--surface2:#1f221e;--ink:#f4f2e9;--ink2:#c3c2b7;--muted:#9a988d;
--grid:#26302a;--axis:#4a544c;--ring:#26302a;--blue:#5598e7;--blue-lt:#2f4f74;
--aqua:#5fc0bd;--yellow:#d8ad4a;--orange:#e8843f;--red:#ff9b86;}}
:root[data-theme=dark]{--plane:#0f130f;--surface:#181a17;--surface2:#1f221e;--ink:#f4f2e9;
--ink2:#c3c2b7;--muted:#9a988d;--grid:#26302a;--axis:#4a544c;--ring:#26302a;--blue:#5598e7;
--blue-lt:#2f4f74;--aqua:#5fc0bd;--yellow:#d8ad4a;--orange:#e8843f;--red:#ff9b86;}
*{box-sizing:border-box}
body{margin:0;background:var(--plane);color:var(--ink);
font-family:system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.6}
.wrap{max-width:64rem;margin:0 auto;padding:2.6rem 1.3rem 5rem}
h1{font-size:1.9rem;line-height:1.15;margin:0 0 .4rem;letter-spacing:-.01em}
.sub{color:var(--ink2);margin:0 0 2rem;max-width:46rem}
.card{background:var(--surface);border:1px solid var(--ring);border-radius:12px;
padding:1.3rem 1.4rem;margin:0 0 1.6rem}
.card h2{font-size:1.12rem;margin:0 0 .2rem;line-height:1.3}
.card .roman{font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--blue);
margin:0 0 .5rem}
.card .finding{color:var(--ink2);margin:0 0 1rem;font-size:.95rem}
svg{width:100%;height:auto;overflow:visible;display:block;margin:.4rem 0 .8rem}
text{font-family:system-ui,-apple-system,sans-serif;font-variant-numeric:tabular-nums}
.ax{font-size:10.5px;fill:var(--muted)}
.lab{font-size:12.5px;fill:var(--ink);font-weight:600}
.lab2{font-size:11.5px;fill:var(--ink2)}
.val{font-size:11.5px;fill:var(--ink);font-weight:600}
.src{font-size:.78rem;color:var(--muted);border-top:1px solid var(--ring);
padding-top:.6rem;margin-top:.8rem}
.src code{background:var(--surface2);padding:.08rem .35rem;border-radius:4px;font-size:.92em}
details{margin-top:.7rem}summary{cursor:pointer;font-size:.85rem;color:var(--blue)}
table{border-collapse:collapse;width:100%;font-size:.8rem;margin-top:.6rem}
th,td{text-align:left;padding:.3rem .5rem;border-bottom:1px solid var(--ring)}
th{font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
td.num{text-align:right;font-variant-numeric:tabular-nums}
.held{border-left:3px solid var(--yellow);background:color-mix(in srgb,var(--yellow) 8%,transparent)}
.held .roman{color:var(--yellow)}
.toggle{position:fixed;top:.8rem;right:.8rem;font:inherit;font-size:.8rem;padding:.3rem .7rem;
border-radius:99px;border:1px solid var(--ring);background:var(--surface);color:var(--ink);
cursor:pointer;z-index:9}
@media print{.toggle{display:none}.card{break-inside:avoid;border-color:#bbb}
body{background:#fff}}
a{color:var(--blue)}
"""


def card(pid, roman, title, finding, svg_markup, srcline, table=None, held=False):
    t = ""
    if table:
        head, body = table
        t = ("<details><summary>Show data</summary><table><thead><tr>"
             + "".join(f"<th>{esc(h)}</th>" for h in head) + "</tr></thead><tbody>"
             + "".join("<tr>" + "".join(
                 f'<td class="num">{esc(c)}</td>' if isinstance(c, (int, float))
                 else f"<td>{esc(c)}</td>" for c in row) + "</tr>" for row in body)
             + "</tbody></table></details>")
    cls = "card held" if held else "card"
    return (f'<section class="{cls}" id="{pid}">'
            f'<p class="roman">{esc(roman)}</p><h2>{esc(title)}</h2>'
            f'<p class="finding">{esc(finding)}</p>{svg_markup}'
            f'<p class="src">{srcline}</p>{t}</section>')


def held_card(pid, roman, title, what, blocker, acquisition):
    return (f'<section class="card held" id="{pid}"><p class="roman">{esc(roman)} &#183; held</p>'
            f'<h2>{esc(title)}</h2><p class="finding">{esc(what)}</p>'
            f'<p><strong>Blocked by:</strong> {esc(blocker)}</p>'
            f'<p><strong>To unblock:</strong> {esc(acquisition)}</p>'
            f'<p class="src">Held {BUILT}. Not drawn.</p></section>')


def build():
    mech, mech_rows = plate_mechanism()
    reveal, shared, rev_rows = plate_reveal()
    dumb, dumb_rows, sc_lo, sc_hi = plate_dumbbell()
    opr, opr_d = plate_opr()
    dot, dot_rows = plate_2026()
    budget, bud_rows = plate_budget()
    cpe, cpe_d = plate_cpe()
    span, span_rows = plate_spans()

    n_below = sum(1 for x in dumb_rows if x["below_1_25"] == "yes")
    parts = [
        '<!doctype html><html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>The Plates &#183; Pittsburgh Airport Covenant Record</title>",
        f"<style>{CSS}</style></head><body>",
        '<button class="toggle">&#9686; theme</button><div class="wrap">',
        "<h1>The Plates</h1>",
        '<p class="sub">Every value is read from a CSV in <code>02-data/</code> that names the '
        'document, the page and the hash it came from. No coordinate in this page was typed by '
        'hand. Rebuild with <code>python 03-harness/build_plates.py</code> and check with '
        '<code>--check</code>.</p>',

        card("exhibit-e1", "Exhibit E-1", "How the money moves, and where the discretion is",
             "Dashed means the Authority chooses. Four of the eleven priorities are funded at "
             "its discretion, the eighth through the eleventh, and only one of them counts "
             "toward the 1.25 test. It is the ninth. The remaining dashed stroke is the "
             "designation entering Net Revenues from the left, which is the second lever "
             "and the one that works on the numerator.",
             mech,
             'Data <code>02-data/flow-of-funds.csv</code>, <code>flow-of-funds-edges.csv</code>. '
             'Priority order transcribed from os-2025ab PDF 31 and PDF 32; the 1.25 test from '
             'PDF 34. No colour on this plate asserts failure: the covenant as written is met.',
             (["node", "kind", "order", "discretion", "locator"],
              [[r["label"], r["kind"], r["priority_order"] or "", r["discretion"],
                f'{r["source_id"]} PDF {r["pdf_page"]}'] for r in mech_rows])),

        card("exhibit-e2", "Exhibit E-2", "The same six years, read three ways",
             f"All three panels share one vertical scale, {shared.d0:.2f} to {shared.d1:.2f}, and "
             f"the 1.25 rule sits at the identical height in each. Panel 2 is a decomposition of "
             f"panel 1, not a third independent reading.",
             reveal,
             'Data <code>02-data/coverage-table.csv</code>, 2025 vintage. The division into '
             'pledged Net Revenues alone is ours; the statement prints only the combined ratio. '
             'Recomputing the printed column from the same rows reproduces every printed value '
             'to within rounding, which is the check that the reading is right.',
             (["year", "as printed", "recomputed", "pledged alone", "under 1.25", "gap $k"],
              [[x["year"], x["coverage_as_printed"], x["coverage_recomputed_with_account"],
                x["coverage_on_net_revenues_alone"], x["below_1_25"],
                x["shortfall_to_1_25_k"]] for x in rev_rows])),

        card("plate-ii", "Plate II", "Without the discretionary account, the ratio runs from 1.12 to 1.35",
             f"Five of the six years in the 2025 forecast come in under 1.25 on pledged Net "
             f"Revenues alone; so do two of the four base-case years and all four of the "
             f"slow-recovery years in the 2021 forecast. Two documents, two bets. The dots sit "
             f"side by side and are not added together. Vertical scale {sc_lo:.2f} to {sc_hi:.2f}.",
             dumb,
             'Data <code>02-data/coverage-table.csv</code>. Open dot as printed, filled dot on '
             'pledged Net Revenues alone.',
             (["vintage", "scenario", "year", "printed", "alone", "under"],
              [[x["vintage"], x["scenario"], x["year"], x["coverage_as_printed"],
                x["coverage_on_net_revenues_alone"], x["below_1_25"]] for x in dumb_rows])),

        card("plate-v", "Plate V", "What the Authority designated, and what it was",
             "Federal pandemic aid is the whole of the designation from 2020 through 2023, and "
             "nothing at all was designated in 2024. Gas royalty was designated once, in 2019, "
             "and is zero in every year after it, forecast included. Slot-machine money also "
             "stops after 2019, and it alone returns, in the 2025 forecast year.",
             opr,
             'Data <code>02-data/other-pledged-revenue-itemized.csv</code>, from os-2025ab '
             'PDF 316 (Exhibit E). The 2023 total conflicts inside the same statement, $3,029k '
             'at PDF 61 against $4,040k at PDF 316. Neither is chosen.',
             (["year", "federal aid $k", "gas $k", "slot-machine tax $k"],
              [[y, f'{opr_d["federal"][y]:,.0f}', f'{opr_d["gas"][y]:,.0f}',
                f'{opr_d["gaming"][y]:,.0f}'] for y in opr_d["years"]])),

        card("plate-i", "Plate I", "What the Authority itself has reported, and what it has not",
             f"The line joins only the Authority's own documents on its own residual basis. "
             f"Newspaper figures and the federal Form 5100-127 filing are drawn as marks and are "
             f"never joined to it, because a clip may be an utterance and never a figure, and "
             f"because the two bases are two series. Years the Authority has not published on "
             f"this basis are gaps, never drawn through: "
             f"{', '.join(str(y) for y in cpe_d['missing']) or 'none, the table is continuous'}. "
             f"The line is one table, the five-year statement at os-2025ab PDF 62. Where a second "
             f"Authority document gives a different figure for a year already on it, that figure "
             f"is a mark beside the line and not a point on it: "
             f"{'; '.join(x['year'] + ' $' + x['cpe'] + ' (' + x['label'] + ')' for x in cpe_d['off']) or 'none'}. "
             f"Vertical scale ${cpe_d['lo']:.2f} to ${cpe_d['hi']:.2f}.",
             cpe,
             'Data <code>02-data/cpe-record.csv</code>. Mark shape carries source grade. The '
             'federal Form 5100-127 figure is drawn in a second colour and is never joined to '
             'the residual series.',
             (["year", "$", "series", "tier", "basis", "source"],
              [[x["year"], x["cpe"], x["series"], x["tier"], x["basis"], x["source_id"]]
               for x in cpe_d["rec"]])),

        card("plate-vii", "Plate VII", "What each bond document said 2026 would cost",
             "Ordered by the vintage of the document, never by value. The $17.64 reaches the "
             "case at two removes from the Authority and one from any document, so it is "
             "annotated beside the axis rather than plotted on it.",
             dot,
             'Data <code>02-data/cpe-2026-claims.csv</code>, which carries its own plot and '
             'annotate column.',
             (["label", "$", "vintage", "tier", "drawn"],
              [[x["label"], x["cpe"], x["vintage"], x["tier"], x["plot"]] for x in dot_rows])),

        card("plate-viii", "Plate VIII", "The budget, four revisions",
             "Each step carries its own escalation on the year before, so the reader sees the "
             "escalation rather than only the endpoint. The 2017 board figure is annotated: it "
             "appears in no hashed document in this vault.",
             budget,
             'Data <code>02-data/budget-revisions.csv</code>. Anchors: os-2021ab PDF 479, '
             'os-2023abc PDF 18, os-2025ab PDF 16.',
             (["year", "figure", "$", "tier", "locator"],
              [[x["year"], x["label"], f'${num(x["amount_usd"])/1e9:.3f}bn', x["tier"],
                f'{x["source_id"]} PDF {x["pdf_page"]}' if x["pdf_page"] else "clip only"]
               for x in bud_rows])),

        card("plate-iii", "Plate III", "A nine-year contract holding up a thirty-five-year debt",
             "Bar lengths are terms, to scale. The commitment is drawn as its term, not its "
             "amount.", span,
             'Data <code>02-data/term-structure.csv</code>.',
             (["item", "from", "to", "note"],
              [[x["item"], x["start_year"], x["end_year"], x.get("note", "")] for x in span_rows])),

        held_card("held-peers", "Held &#183; peer comparison", "Pittsburgh against sixteen larger hubs",
                  "A ranked bar chart of what an airline pays per boarded passenger at "
                  "Pittsburgh against sixteen larger airports.",
                  "Eleven of the sixteen named airports carry no dollar value anywhere in this "
                  "case, and the rank of fifth of thirty-two medium hubs rests on a secondary "
                  "dashboard graded C. Drawing sixteen bars from five numbers would be the "
                  "most attackable figure in the story.",
                  "Pull each airport's own FAA Form 5100-127 filing. None has been pulled."),

        held_card("held-capacity", "Held &#183; capacity", "The terminal's design capacity against use",
                  "A capacity band drawn against passengers actually boarded.",
                  "The 13-to-15 million figure appears in one local article and in no Official "
                  "Statement. The Post-Gazette of Sept. 12, 2017 reports the opposite scale, a "
                  "complex able to accommodate more than 18 million and expandable to 25 million.",
                  "The master plan, by FOIA to the FAA, or a Right-to-Know answer from the "
                  "Authority. Neither has been sent."),

        '<p class="src">Figures for <em>Pittsburgh built a $1.7 billion airport terminal</em>, reported by Lena Rose Williams for Newsworks Lab and the Tribune-Review. Unpublished draft, not edited or accepted by the outlet. Built ' + BUILT + ' from the CSVs in <code>02-data/</code>; rebuild with <code>python 03-harness/build_plates.py</code> and check with <code>--check</code>. Data CC BY 4.0, code MIT. Figures attributed to the Authority are its own, archived and hashed, not independently audited here.</p>',
        "</div><script>document.querySelector('.toggle').onclick=function(){"
        "var r=document.documentElement,d=r.getAttribute('data-theme')==='dark';"
        "r.setAttribute('data-theme',d?'light':'dark')};</script></body></html>",
    ]
    return "".join(parts)


def main():
    check = "--check" in sys.argv
    out = os.path.join(ROOT, "appendix-dataviz", "index.html")
    html_out = build()
    if check:
        if not os.path.exists(out):
            print("appendix-dataviz/index.html missing; run without --check first")
            return 1
        have = io.open(out, encoding="utf-8").read()
        if have != html_out:
            for i, (a, b) in enumerate(zip(have.split("\n"), html_out.split("\n"))):
                if a != b:
                    print(f"drift at line {i+1}")
                    break
            print("FAIL: committed page does not match a rebuild from the CSVs")
            return 1
        print("plates --check OK: every coordinate recomputes from the data")
        return 0
    os.makedirs(os.path.dirname(out), exist_ok=True)
    io.open(out, "w", encoding="utf-8", newline="\n").write(html_out)
    print(f"wrote {os.path.relpath(out, ROOT)}  ({len(html_out):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
