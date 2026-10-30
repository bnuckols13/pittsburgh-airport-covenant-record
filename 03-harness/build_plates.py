#!/usr/bin/env python3
"""build_plates.py — render the plates from the CSVs.

Every coordinate is computed here from data. Run with --check to re-render in
memory and byte-diff against the committed HTML; it exits 1 on drift, which is
the SOP-104 constraint that nobody types a coordinate.

    python 03-harness/build_plates.py
    python 03-harness/build_plates.py --check
"""
import csv, hashlib, html, io, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import charts as ch
from charts import Frame, Scale, Band, Panel, C, esc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "02-data")
BUILT = "2026-10-23"          # data, never datetime.now(); --check must survive tomorrow


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


WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]


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


def plate_said():
    """Plate IX. What was said the charge would be, against the figure the record holds."""
    r = sorted(rows("cpe-said-vs-came-in.csv"), key=lambda x: int(x["order"]))
    ch.assert_plottable([{"label": x["label"], "tier": x["came_tier"]} for x in r],
                        "plate IX outcomes")
    for x in r:
        if x["said_tier"].strip() == "A" and not x["said_source_page"].strip():
            raise SystemExit(f"plate IX: {x['label']!r} is tier A with no page")
        hi = num(x["said_hi"]) if x["said_hi"].strip() else num(x["said_lo"])
        near = hi if abs(num(x["came_in"]) - hi) < abs(num(x["came_in"]) - num(x["said_lo"])) else num(x["said_lo"])
        x["_gap"] = num(x["came_in"]) - near
    vals = [num(x["said_lo"]) for x in r] + [num(x["came_in"]) for x in r] + \
           [num(x["said_hi"]) for x in r if x["said_hi"].strip()]
    f = Frame(w=980, h=72 * len(r) + 104, l=24, r=24, t=44, b=54)
    sc = Scale(0, max(vals) * 1.22, f.x0, f.x1)
    ch.assert_in_domain(sc, vals, "plate IX")
    b = Band([x["label"] for x in r], f.ytop + 10, f.ybot - 10, pad=0.6)
    ticks = [t for t in ch.nice_ticks(0, sc.d1, 6) if t > 0]
    grid = "".join(
        f'<line x1="{sc(t):.1f}" y1="{f.ytop}" x2="{sc(t):.1f}" y2="{f.ybot:.1f}" stroke="{C["grid"]}"/>'
        f'<text class="ax" x="{sc(t):.1f}" y="{f.ybot+16:.1f}" text-anchor="middle">${t:.0f}</text>'
        for t in ticks)
    body = (grid + ch.dumbbell_h(f, sc, b, r, "said_lo", "said_hi", "came_in", "label",
                                 "said_tier", "came_tier", note_key=None,
                                 gap_fmt=lambda v: f"{v:+.2f}")
            + f'<text class="ax" x="{f.x1}" y="{f.ybot+34:.1f}" text-anchor="end">dollars per enplaned passenger</text>'
            + ch.grade_key(f.x0, f.ytop - 22, C["ink2"]))
    aria = ("Five predictions of the airline charge per boarded passenger, each joined to "
            "the figure the record holds for the year predicted. The prediction is the left "
            "mark, shaped by the reliability of its source: an open ring is a newspaper "
            "quotation, a solid disc a hashed document. The outcome is the right mark, always "
            "a hashed document. Four of five outcomes came in above the prediction; the 2024 "
            "budget came in below. Bases differ by year and are named in the data table.")
    return ch.svg(f, aria, body), r


AP_MONTH = ["Jan.", "Feb.", "March", "April", "May", "June", "July", "Aug.", "Sept.", "Oct.",
            "Nov.", "Dec."]


def ap_date(iso):
    y, m, d = (int(p) for p in iso.split("-"))
    return f"{AP_MONTH[m-1]} {d}, {y}"


def year_frac(iso):
    y, m, d = (int(p) for p in iso.split("-"))
    days = [31, 29 if y % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return y + (sum(days[:m-1]) + d - 1) / sum(days)


def wrap(text, width):
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    return lines + ([cur] if cur else [])


# filed panel: one table per line, each value confirmed on its page (witness, Oct. 29: the first
# draft spliced Table IV 2014-2019 onto the bond statement's 2020-2024 table under one label).
# The stress case and the carried-forward outturn are left off this plate (plan decision 4).
FILED = [("reported", "Reported in the 2025 bond statement", "blue", None, 2.4),
         ("forecast-2021", "2021 consultant's forecast, base case", "muted", "2 3", 1.6),
         ("forecast-2023", "2023 consultant's forecast", "muted", "7 3", 1.6),
         ("forecast-2025", "2025 consultant's forecast, base case", "ink2", "7 3", 2.0)]
NOTE_2020 = "2020: enplaned passengers fell in the pandemic"
MID = 0.5   # an annual figure is drawn at mid-year, as in the motion version; posts at their dates


def page_text(source_id, pdf_page):
    """The page's text from the vault copy fetched by fetch_sources.py, whitespace collapsed."""
    import fitz
    path = os.path.join(ROOT, "01-sources-archive", "raw", f"{source_id}.pdf")
    if not os.path.exists(path):
        raise SystemExit(f"plate XI: {source_id}.pdf not in raw/; run fetch_sources.py first")
    with fitz.open(path) as doc:
        return " ".join(doc[int(pdf_page) - 1].get_text().split())


def post_text(vault_id):
    """A captured Blue Sky post's body text, tags stripped and whitespace collapsed."""
    p = os.path.join(ROOT, "01-sources-archive", "raw", f"{vault_id}.json")
    if not os.path.exists(p):
        raise SystemExit(f"plate XI: {vault_id}.json not in raw/; run fetch_sources.py first")
    d = json.load(io.open(p, encoding="utf-8"))
    t = html.unescape(re.sub(r"<[^>]+>", " ", d["content"]["rendered"]))
    return " ".join(t.replace(" ", " ").replace("\xa0", " ").split())


def plate_said_filed():
    """Plate XI. What Blue Sky printed about the charge, on the same time axis as what was filed.

    Rule 1 of the plan: a Blue Sky figure never gets a y-position. Its figures are text on the
    rail at their publication dates. Nothing joins a said mark to a filed one."""
    filed = rows("cpe-filed-xi.csv")
    rail = rows("cpe-said-rail.csv")
    lines, meta, pages = {}, {}, {}
    for key, *_ in FILED:
        rs = [x for x in filed if x["line"] == key]
        if not rs:
            raise SystemExit(f"plate XI: no rows for {key!r}")
        if len({(x["source_id"], x["pdf_page"]) for x in rs}) != 1:
            raise SystemExit(f"plate XI: {key!r} draws on more than one table; one line, one table")
        if len({x["year"] for x in rs}) != len(rs):
            raise SystemExit(f"plate XI: two values for one year in {key!r}")
        sid, pg = rs[0]["source_id"], rs[0]["pdf_page"]
        text = pages.setdefault((sid, pg), page_text(sid, pg))
        # the line's values, in year order, must appear on the page as one unbroken run of
        # whole figures: a substring search would pass a value read off the wrong row
        toks = re.findall(r"\d+\.\d{2}(?!\d)", text)
        want = [f"{num(x['cpe']):.2f}" for x in sorted(rs, key=lambda x: int(x["year"]))]
        if not any(toks[i:i + len(want)] == want for i in range(len(toks))):
            raise SystemExit(f"plate XI: {key} {want} is not a run on {sid} PDF {pg}")
        lines[key] = sorted((int(x["year"]), num(x["cpe"])) for x in rs)
        meta[key] = rs[0]
    for r in rail:
        if r["kind"] not in ("figure", "description"):
            raise SystemExit(f"plate XI: rail row {r['post']} has kind {r['kind']!r}")
        if r["kind"] == "figure" and not r["printed_figure"].strip():
            raise SystemExit(f"plate XI: figure row {r['post']} prints no figure")
        if r["callout"].strip():
            if not r["vault_id"].strip():
                raise SystemExit(f"plate XI: {r['post']} is quoted but not in the package vault")
            if r["callout"] not in post_text(r["vault_id"]):
                raise SystemExit(f"plate XI: the callout for {r['post']} is not verbatim in its capture")
    figs = [r for r in rail if r["kind"] == "figure"]
    last_fig = max(r["date"] for r in figs)
    after = [r for r in rail if r["kind"] == "description" and r["date"] > last_fig]
    last_desc = max(r["date"] for r in after)

    W, L, R = 980, 56, 250
    top = Frame(w=W, h=330, l=L, r=R, t=34, b=36)
    x_lo, x_hi = 2018, 2031
    xs = Scale(x_lo, x_hi, top.x0, top.x1)
    vals = [v for pts in lines.values() for _, v in pts]
    ys = Scale(*ch.domain(vals, pad=0.08), top.ybot, top.ytop)
    ch.assert_in_domain(ys, vals, "plate XI filed")
    ticks = ch.nice_ticks(ys.d0, ys.d1, 5)
    rail_top, row_fig, row_desc, rail_bot = top.h + 42, top.h + 60, top.h + 88, top.h + 102
    for r in rail:
        if xs.clamped(year_frac(r["date"])):
            raise SystemExit(f"plate XI: {r['post']} outside the time axis")

    out = [f'<text class="lab" x="{L}" y="16">Filed: cost per enplaned passenger in the bond '
           f'statements, dollars</text>', ch.axis_y(top, ys, ticks, lambda v: f"${v:,.2f}")]
    year_ticks = [2018, 2020, 2022, 2024, 2026, 2028, 2030]
    for yr in year_ticks:
        out.append(f'<line x1="{xs(yr):.1f}" y1="{top.ytop}" x2="{xs(yr):.1f}" y2="{rail_bot}" '
                   f'stroke="{C["grid"]}" stroke-dasharray="2 3"/>')
    ends = []
    for key, label, col, dash, width in FILED:
        pts = lines[key]
        out.append(ch.gapped_path([(xs(y + MID), ys(v)) for y, v in pts], C[col], width=width, dash=dash))
        out += [ch.mark("A", C[col], xs(y + MID), ys(v), r=3.0) for y, v in pts]
        ly, lv = pts[-1]
        if dash is None:
            fy, fv = pts[0]
            # right of its first point, two lines under the 2020 note, inside the frame
            out.append(f'<text class="lab2" x="{xs(fy + MID)+14:.1f}" y="{ys(fv)+22:.1f}">'
                       f'{esc(label)},</text>'
                       f'<text class="lab2" x="{xs(fy + MID)+14:.1f}" y="{ys(fv)+36:.1f}">'
                       f'{fy} to {ly} ({ly} unaudited)</text>')
        else:
            ends.append((ys(lv), f"{label}:", f"${lv:.2f} for {ly}", xs(ly + MID)))
    for y, txt, val, x in ends:   # two lines, so the longest label stays inside the frame
        out.append(f'<text class="lab2" x="{x+8:.1f}" y="{y-2:.1f}">{esc(txt)}</text>'
                   f'<text class="val" x="{x+8:.1f}" y="{y+12:.1f}">{esc(val)}</text>')
    rep = dict(lines["reported"])
    if 2020 in rep:
        out.append(f'<text class="ax" x="{xs(2020 + MID)+8:.1f}" y="{ys(rep[2020])+4:.1f}">'
                   f'{esc(NOTE_2020)}</text>')
    out.append(ch.axis_x_years(top, xs, year_ticks))

    # the said rail
    b0, b1 = xs(year_frac(last_fig)), xs(year_frac(last_desc))
    out.append(f'<text class="lab" x="{L}" y="{rail_top-24}">Said: Blue Sky News posts about what '
               f'airlines pay at Pittsburgh, captured through Oct. 26, 2026</text>')
    out.append(f'<rect x="{b0:.1f}" y="{rail_top}" width="{b1-b0:.1f}" '
               f'height="{rail_bot-rail_top}" fill="{C["grid"]}" opacity="0.55"/>')
    out.append(f'<text class="ax" x="{b1:.1f}" y="{rail_top-5}" text-anchor="end">'
               f'{esc(ap_date(last_fig))} to {esc(ap_date(last_desc))}: no figure for the charge</text>')
    out.append(f'<text class="lab2" x="{top.x1+8}" y="{row_fig+4}">printed a figure</text>')
    out.append(f'<text class="lab2" x="{top.x1+8}" y="{row_desc+4}">described airline costs, no figure</text>')
    seen, pos = {}, {}
    for r in rail:
        row_y = row_fig if r["kind"] == "figure" else row_desc
        k = (r["date"], row_y)
        seen[k] = seen.get(k, 0) + 1
        x = xs(year_frac(r["date"])) + (seen[k] - 1) * 5
        pos[r["post"]] = (x, row_y)
        out.append(ch.mark("D", C["ink"] if r["kind"] == "figure" else C["ink2"], x, row_y,
                           r=4.4 if r["kind"] == "figure" else 3.4))
        if r["kind"] == "figure":
            out.append(f'<text class="val" x="{x:.1f}" y="{row_y-9:.1f}" text-anchor="middle">'
                       f'{esc(r["printed_figure"])}</text>')

    # callouts: verbatim spans, in date order, each with a leader to its mark and nothing else
    quoted = [r for r in rail if r["callout"].strip()]
    cy = rail_bot + 40
    slot = (W - L - 40) / len(quoted)
    deepest = cy
    for i, r in enumerate(quoted):
        bx = L + i * slot
        px, py = pos[r["post"]]
        out.append(f'<line x1="{px:.1f}" y1="{py+4:.1f}" x2="{bx+8:.1f}" y2="{cy-14:.1f}" '
                   f'stroke="{C["muted"]}" stroke-width="0.8"/>')
        out.append(f'<text class="lab" x="{bx:.1f}" y="{cy:.1f}">{esc(ap_date(r["date"]))}</text>')
        for j, ln in enumerate(wrap("“" + r["callout"] + "”", 38)):
            yy = cy + 16 + j * 14
            deepest = max(deepest, yy)
            out.append(f'<text class="lab2" x="{bx:.1f}" y="{yy:.1f}">{esc(ln)}</text>')
    f = Frame(w=W, h=deepest + 16, l=L, r=R, t=0, b=0)
    quotes = "; ".join(f'{ap_date(r["date"])}, “{r["callout"]}”' for r in quoted)
    end_vals = "; ".join(f"{t} {v}" for _, t, v, _ in ends)
    aria = (f"Two panels on one time axis, {x_lo} to {x_hi - 1}. Top: the cost per enplaned "
            f"passenger reported in the 2025 bond statement, 2020 to 2024, with the note "
            f"“{NOTE_2020}”, and the airport consultant's forecasts in the 2021, 2023 and "
            f"2025 bond statements ({end_vals}). Bottom: {len(rail)} Blue Sky News posts about what "
            f"airlines pay at Pittsburgh. {WORDS[len(figs)].capitalize()} print a figure for the "
            f"charge, the last on {ap_date(last_fig)}. {len(after)} later posts, the last on "
            f"{ap_date(last_desc)}, describe airline costs without a figure. Blue Sky's figures are "
            f"printed as text and are not placed on the dollar scale. Quoted: {quotes}.")
    return ch.svg(f, aria, "".join(out)), {"rail": rail, "figs": figs, "after": after,
                                           "last_fig": last_fig, "last_desc": last_desc,
                                           "lines": lines, "meta": meta, "filed": filed}


def plate_airlines():
    """Plate X. Change in boardings by airline, 2019 to 2024, grouped by carrier type."""
    r = [x for x in rows("enplanements-by-airline.csv") if x["group"] != "total"]
    tot = [x for x in rows("enplanements-by-airline.csv") if x["group"] == "total"][0]
    ch.assert_plottable([{"label": x["airline"], "tier": x["tier"]} for x in r], "plate X")
    order = {"legacy": 0, "low-cost": 1, "foreign-flag": 2, "other": 3}
    for x in r:
        x["_d"] = (num(x["enpl_2024"]) - num(x["enpl_2019"])) / 1000.0
        x["_share"] = f'{x["share_2019"]}% to {x["share_2024"]}% of boardings'
        x["_grp"] = {"legacy": "legacy carriers", "low-cost": "low-cost carriers",
                     "foreign-flag": "foreign-flag carriers", "other": "other"}[x["group"]]
    r.sort(key=lambda x: (order[x["group"]], -x["_d"]))
    by_group = {}
    for x in r:
        by_group[x["group"]] = by_group.get(x["group"], 0.0) + x["_d"]
    check_total = (num(tot["enpl_2024"]) - num(tot["enpl_2019"])) / 1000.0
    if abs(sum(by_group.values()) - check_total) > 0.5:
        raise SystemExit("plate X: airline changes do not sum to the airport total")
    vals = [x["_d"] for x in r]
    f = Frame(w=980, h=26 * len(r) + 4 * 26 + 80, l=150, r=230, t=30, b=48)
    lo, hi = min(vals + [0]), max(vals + [0])
    span = hi - lo
    sc = Scale(lo - span * 0.12, hi + span * 0.12, f.x0, f.x1)
    ch.assert_in_domain(sc, vals, "plate X")
    # one slot per row plus one blank slot above each group for its header
    slots, last = [], None
    for x in r:
        if x["group"] != last:
            slots.append(f"__hdr_{x['group']}")
            last = x["group"]
        slots.append(x["airline"])
    b = Band(slots, f.ytop + 10, f.ybot - 10, pad=0.4)
    ticks = [t for t in ch.nice_ticks(sc.d0, sc.d1, 6)]
    grid = "".join(
        f'<line x1="{sc(t):.1f}" y1="{f.ytop}" x2="{sc(t):.1f}" y2="{f.ybot:.1f}" stroke="{C["grid"]}"/>'
        f'<text class="ax" x="{sc(t):.1f}" y="{f.ybot+16:.1f}" text-anchor="middle">{t:+,.0f}</text>'
        for t in ticks if t != 0)
    body = (grid + ch.change_bars_h(f, sc, b, r, "_d", "airline", group_key="_grp",
                                    right_key="_share", fmt=lambda v: f"{v:+,.0f}")
            + f'<text class="ax" x="{f.x1}" y="{f.ybot+34:.1f}" text-anchor="end">'
              f'change in enplaned passengers, thousands, 2019 to 2024</text>')
    aria = (f"Change in passengers boarded at Pittsburgh by airline between 2019 and 2024, "
            f"in thousands, grouped by carrier type. The four legacy carriers together "
            f"boarded {abs(by_group['legacy']):,.0f} thousand fewer; the low-cost carriers "
            f"{by_group['low-cost']:,.0f} thousand more, led by Spirit, which shut down "
            f"nationwide in May 2026. The airport total rose {check_total:,.0f} thousand.")
    return ch.svg(f, aria, body), r, by_group, check_total


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
    said, said_rows = plate_said()
    sf, sf_d = plate_said_filed()
    airl, airl_rows, airl_groups, airl_total = plate_airlines()

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

        card("plate-ix", "Plate IX", "What they said the charge would be, and what came in",
             f"Five predictions, each joined to the figure the record holds for the year it "
             f"was made for. {WORDS[sum(1 for x in said_rows if x['_gap'] > 0)].capitalize()} of "
             f"{WORDS[len(said_rows)]} came in above the prediction; the board's 2024 budget came "
             f"in below. The two "
             f"newspaper quotations are drawn as open rings, the house mark for an utterance: "
             f"a clip supplies the words and the date, never the figure. The outcomes are two "
             f"of the Authority's own series and are never subtracted across each other: "
             f"2023 and 2024 from its five-year table of airline costs per enplaned passenger, "
             f"2025 from what the airlines were billed, Table III over Table IV, this record's "
             f"division. The largest gap, {max(x['_gap'] for x in said_rows):+.2f}, is Sprys's "
             f"range measured from its top.",
             said,
             'Data <code>02-data/cpe-said-vs-came-in.csv</code>. Predictions: Post-Gazette '
             'Sept. 12, 2017 and Oct. 14, 2021 (tier C, utterances); <code>os-2021ab</code> '
             'PDF 185 (printed B-19), the 2025 column of both recovery cases; board minutes '
             'Nov. 17, 2023, PDF 8. Outcomes: <code>os-2025ab</code> PDF 62 (printed 52); '
             '<code>acfr-2025</code> PDF 70 and 72. Gaps computed by '
             '<code>build_plates.py</code>.',
             (["Said", "When", "For", "Said ($)", "Came in ($)", "Gap", "Outcome basis"],
              [(x["label"], x["said_date"], x["year_for"],
                (x["said_lo"] if not x["said_hi"].strip() else f'{x["said_lo"]} to {x["said_hi"]}'),
                x["came_in"], f'{x["_gap"]:+.2f}', x["note"]) for x in said_rows])),

        card("plate-xi", "Plate XI", "What Blue Sky printed about the charge, and what was filed",
             f"Blue Sky News is the Authority's own outlet. It printed a figure for the cost per "
             f"enplaned passenger in {WORDS[len(sf_d['figs'])]} posts, "
             f"{' and '.join(ap_date(r['date']) + ' (' + r['printed_figure'] + ')' for r in sf_d['figs'])}, "
             f"both budget projections, not reported results. The {len(sf_d['after'])} later posts "
             f"that describe what airlines pay at Pittsburgh, the last on "
             f"{ap_date(sf_d['last_desc'])}, print no figure for the charge. The filed lines are "
             f"the charge reported in the 2025 bond statement for 2020 to 2024 and the airport "
             f"consultant's forecasts in the 2021, 2023 and 2025 statements, one table per line. "
             f"Blue Sky's figures appear as text on the lower strip and are never placed on the "
             f"dollar scale or joined to a line. The plate covers Blue Sky only and says nothing "
             f"about what the Authority told other outlets.",
             sf,
             'Filed: <code>02-data/cpe-filed-xi.csv</code>; each value is confirmed on its page by '
             '<code>build_plates.py</code>: reported, <code>os-2025ab</code> PDF 62 (printed 52); '
             'forecasts, <code>os-2021ab</code> PDF 185 (printed B-19), <code>os-2023abc</code> '
             'PDF 208 (printed B-16), <code>os-2025ab</code> PDF 202 (printed B-16). The 2025 '
             'stress case is not drawn. Said: <code>02-data/cpe-said-rail.csv</code>, Blue Sky '
             'posts coded figure or description, tier D; an independent witness reviewed the '
             'coding Oct. 29, 2026. Quoted posts in the vault: <code>bluesky-10318</code>, '
             '<code>bluesky-10420</code>, <code>bluesky-10715</code>, <code>bluesky-49562</code>; '
             'the rest link to blueskypit.com. Annual figures are drawn at mid-year; posts at '
             'their publication dates. 2024 is unaudited on PDF 62. The 2020 note: <code>os-2025ab</code> '
             'PDF 62 attributes the 2020 increase to the decline in passengers as a result of '
             'COVID-19; <code>acfr-2020</code> PDF 16 (printed 4), '
             'which gives the 2020 decline as 62.7% (enplaned passengers) and 62.8% (passenger '
             'traffic) on that page, and 62.8% (enplaned passengers) at PDF 18 (printed 6); the '
             'note uses no figure.',
             (["Date or year", "Item", "Kind", "Value", "Source"],
              [(x["year"], x["line"], "filed", f'${num(x["cpe"]):.2f}',
                f'{x["source_id"]} PDF {x["pdf_page"]} (printed {x["printed_page"]})')
               for x in sf_d["filed"]]
              + [(r["date"], r["post"], r["kind"], r["printed_figure"],
                  (f'quoted: \u201c{r["callout"]}\u201d' if r["callout"]
                   else "blueskypit.com; link in cpe-said-rail.csv"))
                 for r in sf_d["rail"]])),

        card("plate-x", "Plate X", "Boardings by airline, 2019 to 2024",
             f"Between 2019 and 2024 the four legacy carriers boarded "
             f"{abs(airl_groups['legacy']):,.0f} thousand fewer passengers at Pittsburgh and "
             f"the low-cost carriers {airl_groups['low-cost']:,.0f} thousand more, led by "
             f"Spirit, up {max(x['_d'] for x in airl_rows):,.0f} thousand. The airport as a "
             f"whole boarded {airl_total:,.0f} thousand more. Spirit shut down nationwide in "
             f"May 2026 after two bankruptcies; the record does not connect its shutdown to the "
             f"charge at this airport, and this plate does not say it does. Orange marks a "
             f"decline, not a loss to anyone.",
             airl,
             'Data <code>02-data/enplanements-by-airline.csv</code>, from <code>os-2025ab</code> '
             'PDF 251 (printed B-65), Table 9, Authority records, scheduled passengers only; '
             'regional affiliates grouped with their mainline partner, merged airlines '
             'reported together. Spirit\'s shutdown: <code>blueskypit-spirit</code>, May 4, 2026. '
             'Differences and group sums computed by <code>build_plates.py</code>.',
             (["Airline", "Group", "2019", "2024", "Change", "Share 2019", "Share 2024"],
              [(x["airline"], x["group"], f'{num(x["enpl_2019"]):,.0f}',
                f'{num(x["enpl_2024"]):,.0f}', f'{x["_d"]*1000:+,.0f}',
                f'{x["share_2019"]}%', f'{x["share_2024"]}%') for x in airl_rows])),

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
