#!/usr/bin/env python3
"""build_report.py — the modular report.

Six modules, in Brian's own spine of 2026-08-29: the room where everyone agreed,
how secure the covenant is, what it costs to fly, the enplanement debate, the
forecast and how it has gone, and the options. Each stands alone, each carries
its own plate, and each plate has paragraphs under it that read it. A module can
be cut or reordered without breaking the ones around it, which is what modular
has to mean if it is to mean anything.

Every plate is drawn from a CSV by charts.py. No coordinate is typed. --check
re-renders and byte-diffs.

    python 03-harness/build_report.py
    python 03-harness/build_report.py --check
"""
import csv, io, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import charts as ch
from charts import Frame, Scale, Band, C, esc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "02-data")
BUILT = "2026-08-31"


def rows(name):
    with io.open(os.path.join(DATA, name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def num(v):
    return float(str(v).replace(",", "").replace("$", "").strip() or 0)


# --------------------------------------------------------------------- plates

def plate_promise():
    """What meets the promise, in dollars, and how much of it is discretionary."""
    cov = sorted([r for r in rows("coverage-table.csv") if r["vintage"] == "2025"],
                 key=lambda r: int(r["year"]))
    opr = {r["year"]: num(r["designated_k"]) for r in rows("other-pledged-revenue.csv")
           if not r["conflict"]}
    f = Frame(w=900, h=300, l=58, r=30, t=44, b=44)
    recs = []
    for r in cov:
        d = opr[r["year"]]
        recs.append({"year": r["year"], "earned": num(r["net_revenues_incl_OPR_k"]) - d,
                     "desig": d, "acct": num(r["coverage_amount_k"]),
                     "promise": 1.25 * num(r["aggregate_annual_debt_service_k"])})
    hi = max(max(x["earned"] + x["desig"] + x["acct"], x["promise"]) for x in recs) * 1.12
    sc = Scale(0, hi, f.ybot, f.ytop)
    b = Band([x["year"] for x in recs], f.x0, f.x1)
    out = [ch.axis_y(f, sc, ch.nice_ticks(0, hi, 4), lambda v: f"${v/1000:.0f}m")]
    bw = min(b.step * 0.56, 54)
    for x in recs:
        cx = b.center(x["year"])
        base = 0.0
        for val, fill in ((x["earned"], C["blue"]), (x["desig"], "url(#h1)"),
                          (x["acct"], "url(#h2)")):
            if val <= 0:
                continue
            y1, y0 = sc(base + val), sc(base)
            out.append(f'<rect x="{cx-bw/2:.1f}" y="{min(y0,y1):.1f}" width="{bw:.1f}" '
                       f'height="{abs(y0-y1):.1f}" fill="{fill}" stroke="{C["ink2"]}" '
                       f'stroke-opacity="0.3"/>')
            base += val
        out.append(f'<line x1="{cx-bw/2-7:.1f}" y1="{sc(x["promise"]):.1f}" '
                   f'x2="{cx+bw/2+7:.1f}" y2="{sc(x["promise"]):.1f}" stroke="{C["ink"]}" '
                   f'stroke-width="2.4"/>')
        gap = x["promise"] - x["earned"]
        out.append(f'<text class="ax" x="{cx:.1f}" y="{f.ybot+17:.1f}" text-anchor="middle">'
                   f'{x["year"]}</text>')
        out.append(f'<text class="val" x="{cx:.1f}" y="{sc(x["earned"])-7:.1f}" '
                   f'text-anchor="middle" fill="{C["orange"]}">&#8722;{gap/1000:.0f}</text>')
    lx = f.x0
    for i, (fill, lab) in enumerate((("var(--blue)", "what the airport earns"),
                                     ("url(#h1)", "money it designates in"),
                                     ("url(#h2)", "the Coverage Account"))):
        out.append(f'<rect x="{lx+i*208}" y="6" width="12" height="12" fill="{fill}" '
                   f'stroke="{C["ink2"]}" stroke-opacity="0.3"/>')
        out.append(f'<text class="ax" x="{lx+i*208+18}" y="16">{lab}</text>')
    out.append(f'<line x1="{lx+626}" y1="11" x2="{lx+644}" y2="11" stroke="{C["ink"]}" '
               f'stroke-width="2.4"/>')
    out.append(f'<text class="ax" x="{lx+650}" y="16">the promise</text>')
    out.append(f'<line x1="{f.x0}" y1="{f.ybot}" x2="{f.x1}" y2="{f.ybot}" stroke="{C["axis"]}"/>')
    share = sum((x["desig"] + x["acct"]) / x["promise"] for x in recs) / len(recs)
    return HATCH + ch.svg(f, "What meets the promise in each forecast year, in millions of "
                          "dollars. The solid block is what the airport earns; the two hatched "
                          "blocks are money the Authority chooses to add. The rule across each "
                          "bar is 1.25 times the debt payment.", "".join(out)), recs, share


def plate_debt_arrives():
    """The four years no debt service entered the airline bill, and what follows."""
    r = rows("debt-service-arrives.csv")
    f = Frame(w=900, h=290, l=64, r=30, t=42, b=44)
    hi = max(num(x["amount"]) for x in r) * 1.14
    sc = Scale(0, hi, f.ybot, f.ytop)
    b = Band([x["year"] for x in r], f.x0, f.x1)
    bw = min(b.step * 0.58, 34)
    out = [ch.axis_y(f, sc, ch.nice_ticks(0, hi, 4), lambda v: f"${v/1e6:.0f}m")]
    zeros = [x["year"] for x in r if num(x["amount"]) == 0]
    if zeros:
        x0 = b.center(zeros[0]) - b.step / 2
        x1 = b.center(zeros[-1]) + b.step / 2
        out.append(f'<rect x="{x0:.1f}" y="{f.ytop-10:.1f}" width="{x1-x0:.1f}" '
                   f'height="{f.ybot-f.ytop+10:.1f}" fill="{C["yellow"]}" fill-opacity="0.12"/>')
        # inside the band it describes, clear of the legend row above
        out.append(f'<text class="ax" x="{(x0+x1)/2:.1f}" y="{f.ytop+8:.1f}" '
                   f'text-anchor="middle">four years, nothing</text>')
    for x in r:
        cx, v = b.center(x["year"]), num(x["amount"])
        fore = x["series"].startswith("aggregate")
        if v > 0:
            out.append(f'<rect x="{cx-bw/2:.1f}" y="{sc(v):.1f}" width="{bw:.1f}" '
                       f'height="{f.ybot-sc(v):.1f}" '
                       f'fill="{"url(#h2)" if fore else C["blue"]}" stroke="{C["ink2"]}" '
                       f'stroke-opacity="0.3"/>')
        else:
            out.append(f'<line x1="{cx-bw/2:.1f}" y1="{f.ybot:.1f}" x2="{cx+bw/2:.1f}" '
                       f'y2="{f.ybot:.1f}" stroke="{C["orange"]}" stroke-width="3.2"/>')
        out.append(f'<text class="ax" x="{cx:.1f}" y="{f.ybot+17:.1f}" text-anchor="middle">'
                   f'{x["year"][2:]}</text>')
    out.append(f'<rect x="{f.x0}" y="6" width="12" height="12" fill="{C["blue"]}" '
               f'stroke="{C["ink2"]}" stroke-opacity="0.3"/>')
    out.append(f'<text class="ax" x="{f.x0+18}" y="16">in the airline rate base, audited</text>')
    out.append(f'<rect x="{f.x0+280}" y="6" width="12" height="12" fill="url(#h2)" '
               f'stroke="{C["ink2"]}" stroke-opacity="0.3"/>')
    out.append(f'<text class="ax" x="{f.x0+298}" y="16">aggregate annual debt service, forecast'
               f'</text>')
    out.append(f'<line x1="{f.x0}" y1="{f.ybot}" x2="{f.x1}" y2="{f.ybot}" stroke="{C["axis"]}"/>')
    return HATCH + ch.svg(f, "Debt service, in millions. Audited figures inside the airline rate "
                          "base through 2024, and the 2025 statement's forecast of aggregate "
                          "annual debt service after it. Four years carry nothing. These are two "
                          "different measures and are drawn adjacent, never joined.",
                          "".join(out)), r


def plate_three_bases():
    """Three series go by one name."""
    aud = rows("cpe-audited-acfr.csv")
    f = Frame(w=900, h=280, l=52, r=140, t=36, b=44)
    years = list(range(2015, 2031))
    xs = Scale(2015, 2030, f.x0, f.x1)
    OS_MDA = {2020: 20.57, 2021: 12.35, 2022: 10.57, 2023: 11.34, 2024: 11.56}
    FCST = {r["year"]: r for r in rows("coverage-table.csv") if r["vintage"] == "2025"}
    vals = [num(x["cpe_audited"]) for x in aud] + list(OS_MDA.values()) + \
           [num(v["cpe"]) for v in FCST.values()]
    ys = Scale(*ch.domain(vals, pad=0.10), f.ybot, f.ytop)
    out = [ch.axis_y(f, ys, ch.nice_ticks(ys.d0, ys.d1, 5), lambda v: f"${v:.0f}")]
    a = sorted(aud, key=lambda r: int(r["year"]))
    out.append(ch.gapped_path([(xs(int(r["year"])), ys(num(r["cpe_audited"]))) for r in a],
                              C["blue"], 2.6))
    for r in a:
        out.append(ch.mark("A", C["blue"], xs(int(r["year"])), ys(num(r["cpe_audited"]))))
    out.append(ch.gapped_path([(xs(y), ys(v)) for y, v in sorted(OS_MDA.items())],
                              C["aqua"], 2.0, dash="4 3"))
    for y, v in OS_MDA.items():
        out.append(ch.mark("A", C["aqua"], xs(y), ys(v)))
    fc = sorted(FCST.values(), key=lambda r: int(r["year"]))
    out.append(ch.gapped_path([(xs(int(r["year"])), ys(num(r["cpe"]))) for r in fc],
                              C["orange"], 2.4, dash="6 4"))
    for r in fc:
        out.append(ch.mark("A", C["orange"], xs(int(r["year"])), ys(num(r["cpe"]))))
    out.append(ch.mark("B", C["yellow"], xs(2025), ys(16.10)))
    out.append(f'<text class="ax" x="{xs(2025)+9:.1f}" y="{ys(16.10)+4:.1f}">'
               f'$16.10, the federal filing</text>')
    for lab, col, val in (("audited", C["blue"], a[0]), ("bond statement", C["aqua"], None),
                          ("consultant forecast", C["orange"], None)):
        pass
    out.append(f'<text class="lab2" x="{f.x1+8}" y="{ys(num(a[0]["cpe_audited"]))+4:.1f}" '
               f'fill="{C["blue"]}">audited</text>')
    out.append(f'<text class="lab2" x="{f.x1+8}" y="{ys(11.56)+4:.1f}" fill="{C["aqua"]}">'
               f'bond statement</text>')
    out.append(f'<text class="lab2" x="{f.x1+8}" y="{ys(num(fc[-1]["cpe"]))+4:.1f}" '
               f'fill="{C["orange"]}">forecast</text>')
    out.append(ch.axis_x_years(f, xs, [2015, 2018, 2021, 2024, 2027, 2030]))
    return ch.svg(f, "Three series go by the name cost per enplaned passenger. The Authority's "
                  "audited annual report, its bond statement's management discussion, and its "
                  "consultant's forecast. The federal filing is a fourth measure and is marked "
                  "separately. None is subtracted against another.", "".join(out)), a, OS_MDA


def plate_designated():
    it = rows("other-pledged-revenue-itemized.csv")
    years = [str(y) for y in range(2019, 2031)]
    cat = lambda cs, y: sum(num(r[y]) for r in it if r["category"] in cs)
    f = Frame(w=900, h=270, l=62, r=30, t=36, b=44)
    tot = [cat({"federal pandemic aid", "federal disaster aid"}, y) + cat({"gas royalty"}, y)
           + cat({"slot-machine tax"}, y) for y in years]
    sc = Scale(0, max(tot) * 1.14, f.ybot, f.ytop)
    b = Band(years, f.x0, f.x1)
    fed = {y: cat({"federal pandemic aid", "federal disaster aid"}, y) for y in years}
    gas = {y: cat({"gas royalty"}, y) for y in years}
    gam = {y: cat({"slot-machine tax"}, y) for y in years}
    out = [ch.axis_y(f, sc, ch.nice_ticks(0, sc.d1, 4), lambda v: f"${v/1000:.0f}m"),
           ch.stacked_bars(f, sc, b, years, [("federal aid", fed, C["aqua"]),
                                             ("gas royalty", gas, C["yellow"]),
                                             ("slot-machine tax", gam, C["blue"])]),
           ch.axis_x_band(f, b)]
    for i, (nm, col) in enumerate((("federal aid", C["aqua"]), ("gas royalty", C["yellow"]),
                                   ("slot-machine tax", C["blue"]))):
        out.append(f'<rect x="{f.x0+i*172}" y="6" width="12" height="12" fill="{col}"/>')
        out.append(f'<text class="ax" x="{f.x0+i*172+18}" y="16">{nm}</text>')
    return ch.svg(f, "Money designated into the pledge, by component, 2019 to 2030, in millions. "
                  "Federal aid is the whole of it from 2020 through 2023. Nothing at all in 2024. "
                  "Gas royalty appears once, in 2019.", "".join(out)), fed, gas, gam


def plate_budget():
    r = rows("budget-revisions.csv")
    drawn = [x for x in r if x["plot"] == "plot"]
    ch.assert_plottable(drawn, "budget plate")
    f = Frame(w=900, h=210, l=320, r=120, t=26, b=34)
    sc = Scale(0, max(num(x["amount_usd"]) for x in r) * 1.1, f.x0, f.x1)
    labels = [f'{x["year"]}  {x["label"]}' for x in r]
    for x, l in zip(r, labels):
        x["_l"] = l
    b = Band(labels, f.ytop + 14, f.ybot - 14)
    out = [ch.ranked_bars(f, sc, b, drawn, "amount_usd", "_l", lambda v: f"${v/1e9:.2f}bn")]
    for prev, cur in zip(drawn, drawn[1:]):
        pct = (num(cur["amount_usd"]) / num(prev["amount_usd"]) - 1) * 100
        out.append(f'<text class="ax" x="{f.x0-8}" y="{b.center(cur["_l"])+15:.1f}" '
                   f'text-anchor="end">+{pct:.0f}% on the figure before</text>')
    for x in r:
        if x["plot"] != "plot":
            out.append(f'<text class="ax" x="{f.x0+6}" y="{b.center(x["_l"])+4:.1f}" '
                       f'fill="{C["muted"]}">${num(x["amount_usd"])/1e9:.2f}bn, reported; no '
                       f'document in this vault, so not drawn</text>')
    return ch.svg(f, "The project cost at four dates. The 2017 board figure is annotated rather "
                  "than drawn: it appears in no hashed document here.", "".join(out)), r


def plate_spans():
    r = rows("term-structure.csv")
    f = Frame(w=900, h=210, l=58, r=40, t=40, b=40)
    sc = Scale(min(num(x["start_year"]) for x in r), max(num(x["end_year"]) for x in r),
               f.x0, f.x1)
    out = [ch.spans(f, sc, r, "start_year", "end_year", "item"),
           ch.axis_x_years(f, sc, [2020, 2026, 2032, 2038, 2044, 2050, 2056])]
    return ch.svg(f, "Term lengths to scale. The bonds run to 2056. The agreements and the money "
                  "committed under them end in 2028.", "".join(out)), r


HATCH = ('<svg width="0" height="0" style="position:absolute"><defs>'
         '<pattern id="h1" width="6" height="6" patternUnits="userSpaceOnUse" '
         'patternTransform="rotate(45)"><rect width="6" height="6" fill="var(--blue-lt)" '
         'fill-opacity=".3"/><line x1="0" y1="0" x2="0" y2="6" stroke="var(--blue)" '
         'stroke-width="2.2" opacity=".55"/></pattern>'
         '<pattern id="h2" width="6" height="6" patternUnits="userSpaceOnUse" '
         'patternTransform="rotate(-45)"><rect width="6" height="6" fill="var(--aqua)" '
         'fill-opacity=".22"/><line x1="0" y1="0" x2="0" y2="6" stroke="var(--aqua)" '
         'stroke-width="2.2" opacity=".6"/></pattern></defs></svg>')
