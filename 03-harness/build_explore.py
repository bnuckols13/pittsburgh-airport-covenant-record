#!/usr/bin/env python3
"""build_explore.py — the explorer: what they said, what they filed, and the page it is on.

One page, four instruments, every one built from a data file at build time so a reader
with scripts off, a printed copy, or an archival capture gets the same figures. Script
only adds the scroll-driven states and the page viewer.

    python 03-harness/build_explore.py
    python 03-harness/build_explore.py --check     # re-render in memory, byte-diff, exit 1 on drift

Inputs, all under 02-data/ unless named:
    timeline-events.csv        the rail and the two lanes (also the video's event stream)
    coverage-three-layers.csv  the 1.25 test, taken apart
    cpe-series.csv             the audited charge, for the arc under the rail
    cited-pages.csv            every (document, page) a claim rests on
    page-highlights.json       rendered pages and highlight boxes (render_pages.py); optional
    documents.csv              ids, titles, hashes
    claims.csv                 the covenant record's claims
    ../pit-terminal-financing/v2/factcheck-v29/factcheck-v29.json       the Sept. 7 ledger
    ../pit-terminal-financing/v2/factcheck-teams/CLAIMS-2026-10-19.md   the Oct. 19 map
"""
import csv, io, json, os, re, sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_explainer import page, rows, num, CSS as BASE_CSS  # noqa: E402
from build_tools import FILTER_JS  # noqa: E402
from charts import esc, Frame, Scale  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "02-data")
CASE = os.path.join(os.path.dirname(ROOT), "pit-terminal-financing", "v2")
OUT = os.path.join(ROOT, "explore", "index.html")
BUILT = "2026-10-19"


def jload(path):
    with io.open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def fmt_date(iso, precision):
    d = datetime.fromisoformat(iso)
    if precision == "year":
        return str(d.year)
    if precision == "month":
        return d.strftime("%b. %Y").replace("May.", "May").replace("Jun.", "June").replace("Jul.", "July")
    s = d.strftime("%b. %d, %Y").replace(" 0", " ")
    return s.replace("May.", "May").replace("Jun.", "June").replace("Jul.", "July").replace("Sep.", "Sept.")


# ---------------------------------------------------------------- data

def load_events():
    ev = rows("timeline-events.csv")
    for r in ev:
        r["_dt"] = datetime.fromisoformat(r["datetime"])
        r["_year"] = r["_dt"].year + (r["_dt"].timetuple().tm_yday - 1) / 366.0
    ev.sort(key=lambda r: r["_dt"])
    return ev


def load_docs():
    return {r["id"]: r for r in rows("documents.csv")}


def load_clips():
    """Titles, dates and hashes for the archived clips, from the media sibling."""
    p = os.path.join(os.path.dirname(ROOT), "pit-tier1-media-archive", "01-sources-archive", "clips.json")
    if not os.path.exists(p):
        return {}
    d = jload(p)
    rows_ = d if isinstance(d, list) else d.get("clips", list(d.values()))
    return {r["id"]: r for r in rows_ if isinstance(r, dict) and r.get("id")}


def load_highlights():
    p = os.path.join(DATA, "page-highlights.json")
    if not os.path.exists(p):
        return {}
    out = {}
    for h in jload(p):
        out[(h["doc_id"], int(h["pdf_page"]))] = h
    return out


TEAMS_STANDING = [("**FIX**", "fix"), ("**OPEN**", "open"), ("**SLOT**", "slot"),
                  ("**DECIDE**", "decide"), ("**restore**", "restore"), ("**TIER C**", "tierc"),
                  ("**OURS**", "ours"), ("**CARRY**", "carry"), ("✔", "holds")]
V29_STANDING = {"VERIFIED": "holds", "ATTENTION": "open", "UNSOURCED": "open",
                "FAILS": "fix", "SLOT": "slot"}
PKG_STANDING = {"established": "holds", "computed": "ours", "attributed": "carry",
                "contested": "decide"}
STANDING_LABEL = {"holds": "Reproduces", "ours": "Our arithmetic", "carry": "Carried, attributed",
                  "tierc": "Tier C", "open": "Open", "fix": "Needs a fix", "decide": "Decision",
                  "slot": "Slot", "restore": "Restore"}


def load_claims():
    """Three ledgers, one shape: id, set, text, standing, docs [(doc, page)], note."""
    out = []
    for r in rows("claims.csv"):
        docs = []
        for ev in (r["evidence"] or "").split(";"):
            if "#" in ev:
                d, p = ev.split("#", 1)
                docs.append((d.strip(), int(p)))
        out.append(dict(id=r["id"], set="record", text=r["claim"],
                        standing=PKG_STANDING.get(r["status"], "open"), docs=docs,
                        note=r["note"], where=r["topic"]))
    v29 = jload(os.path.join(CASE, "factcheck-v29", "factcheck-v29.json"))
    for c in v29["claims"]:
        docs = [(m.group(1), int(m.group(2)))
                for m in re.finditer(r"([a-z0-9-]+)\s+PDF\s+(\d+)", c.get("locator") or "")]
        standing = V29_STANDING.get(c["standing"], "open")
        if standing == "holds" and (c.get("note") or "").lstrip().lower().startswith("ours"):
            standing = "ours"
        out.append(dict(id=c["id"], set="v29", text=c["claim"],
                        standing=standing, docs=docs,
                        note=(c.get("note") or ""), where=c.get("where", "")))
    md = io.open(os.path.join(CASE, "factcheck-teams", "CLAIMS-2026-10-19.md"),
                 encoding="utf-8").read()
    section = ""
    for line in md.split("\n"):
        if line.startswith("## "):
            section = line[3:].strip()
        m = re.match(r"^\| (\d+|F\d|—) \|", line)
        if not m:
            continue
        cells = [x.strip() for x in line.strip("|").split("|")]
        if len(cells) < 5:
            continue
        src = cells[3]
        docs = []
        for d in re.findall(r"`([a-z0-9-]+)`", src):
            for p in re.findall(r"PDF (\d+)", src):
                docs.append((d, int(p)))
        standing = "holds"
        for key, val in TEAMS_STANDING:
            if cells[4].startswith(key):
                standing = val
                break
        cid = "T" + m.group(1) if m.group(1) != "—" else "T-restore"
        out.append(dict(id=cid, set="teams", text=cells[2] if cells[2] != "—" else cells[1],
                        standing=standing, docs=docs, note=re.sub(r"\*\*[A-Za-z ]+\*\*\s*·?\s*", "", cells[4]),
                        where=section, draft=cells[1]))
    return out


# ---------------------------------------------------------------- the rail

TARGET_COLOUR = {"Airlines": "var(--red)", "Bondholders": "var(--blue)", "Gaming fund": "var(--yellow)",
                 "Gas lease": "var(--orange)", "Federal relief": "var(--aqua)",
                 "Coverage Account": "var(--blue-lt)", "Passengers": "var(--ink2)"}


def rail_svg(events, cpe_actual):
    """Said above the axis, filed below, 2013 to 2030 at full width and a broken tail to 2056."""
    f = Frame(w=980, h=430, l=28, r=28, t=26, b=44)
    y_axis = 175
    # two-segment x scale: 2013..2031 across 82% of the frame, 2031..2057 across the rest
    x_main = Scale(2013, 2031, f.x0, f.x0 + (f.x1 - f.x0) * 0.82)
    x_tail = Scale(2031, 2057, f.x0 + (f.x1 - f.x0) * 0.86, f.x1)

    def X(y):
        return x_main(y) if y <= 2031 else x_tail(y)

    parts = []
    # axis and the break
    parts.append(f'<line x1="{f.x0}" y1="{y_axis}" x2="{x_main(2031):.1f}" y2="{y_axis}" '
                 'stroke="var(--axis)" stroke-width="1.2"/>')
    xb0, xb1 = x_main(2031), x_tail(2031)
    parts.append(f'<path d="M{xb0:.1f} {y_axis} l6 -7 l6 14 l6 -14 l6 14 l6 -7" fill="none" '
                 'stroke="var(--axis)" stroke-width="1.2"/>')
    parts.append(f'<line x1="{xb1:.1f}" y1="{y_axis}" x2="{f.x1}" y2="{y_axis}" '
                 'stroke="var(--axis)" stroke-width="1.2"/>')
    for yr in list(range(2013, 2031, 1)) + [2040, 2050, 2056]:
        x = X(yr)
        major = yr % 5 == 0 or yr in (2013, 2028, 2056)
        parts.append(f'<line x1="{x:.1f}" y1="{y_axis}" x2="{x:.1f}" y2="{y_axis + (7 if major else 4)}" '
                     'stroke="var(--axis)" stroke-width="1"/>')
        if major or yr in (2017, 2021, 2025):
            parts.append(f'<text class="ax" x="{x:.1f}" y="{y_axis + 20}" text-anchor="middle">{yr}</text>')
    # 2028 cliff
    xc = X(2028.99)
    parts.append(f'<line x1="{xc:.1f}" y1="{f.ytop}" x2="{xc:.1f}" y2="{y_axis}" stroke="var(--red)" '
                 'stroke-width="1" stroke-dasharray="3 3"/>')
    parts.append(f'<text class="lab2" x="{xc + 4:.1f}" y="{f.ytop + 10}" fill="var(--red)">Dec. 31, 2028</text>')
    # lane labels
    parts.append(f'<text class="lab2" x="{f.x0}" y="{f.ytop + 10}">Said in public</text>')
    parts.append(f'<text class="lab2" x="{f.x0}" y="{y_axis + 40}">Filed, and who carried it</text>')
    # the arc: audited cost per enplaned passenger, 2014 to 2024, below both lanes
    arc_y0, arc_y1 = 372, 322
    ys = Scale(0, 22, arc_y0, arc_y1)
    pts = [(X(int(r["year"]) + 0.5), ys(num(r["cpe_audited"]))) for r in cpe_actual]
    d = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f} {y:.1f}" for i, (x, y) in enumerate(pts))
    parts.append(f'<path d="{d}" fill="none" stroke="var(--ink2)" stroke-width="1.6" opacity=".75"/>')
    for (x, y), r in zip(pts, cpe_actual):
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" fill="var(--ink2)"/>')
    first, last = cpe_actual[0], cpe_actual[-1]
    parts.append(f'<text class="ax" x="{pts[0][0] - 4:.1f}" y="{pts[0][1] + 4:.1f}" text-anchor="end">'
                 f'${num(first["cpe_audited"]):.2f}</text>')
    parts.append(f'<text class="ax" x="{pts[-1][0] + 4:.1f}" y="{pts[-1][1] + 4:.1f}">'
                 f'${num(last["cpe_audited"]):.2f}</text>')
    parts.append(f'<text class="ax" x="{f.x0}" y="{arc_y0 + 14}">Audited cost per boarded passenger, Table IV cost basis, '
                 f'{first["year"]} to {last["year"]}. Cuts funded from gas and gaming money ran 2013 to 2019; '
                 f'2020 to 2024 carried no terminal debt service.</text>')
    # dots
    said_y = {}
    for r in events:
        x = X(r["_year"])
        rail = r["rail"] == "1"
        if r["category"] == "a":
            # stack same-day statements upward
            key = r["_dt"].date()
            n = said_y.get(key, 0)
            said_y[key] = n + 1
            y = y_axis - 26 - n * 13
            rr = 5.2 if rail else 3.6
            parts.append(f'<a href="#{esc(r["id"])}" class="dot"><title>{esc(fmt_date(r["datetime"], r["precision"]))}'
                         f' · {esc(r["speaker"])}: {esc(r["text"])}</title>'
                         f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="var(--ink2)" opacity=".55" '
                         f'stroke="var(--plane)" stroke-width="1"/></a>')
        else:
            tgt = r["target"]
            lane_i = list(TARGET_COLOUR).index(tgt) if tgt in TARGET_COLOUR else 6
            y = y_axis + 56 + lane_i * 11
            rr = 5.6 if rail else 3.8
            col = TARGET_COLOUR.get(tgt, "var(--muted)")
            parts.append(f'<a href="#{esc(r["id"])}" class="dot"><title>{esc(fmt_date(r["datetime"], r["precision"]))}'
                         f' · {esc(tgt)}: {esc(r["text"])}</title>'
                         f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="{col}" '
                         f'stroke="var(--plane)" stroke-width="1"/></a>')
    # target key as one row under the arc
    kx = f.x0
    ky = f.h - 8
    for i, (name, col) in enumerate(TARGET_COLOUR.items()):
        x = kx + i * 118
        parts.append(f'<circle cx="{x:.1f}" cy="{ky - 3.5:.1f}" r="3.2" fill="{col}"/>'
                     f'<text class="ax" x="{x + 7:.1f}" y="{ky:.1f}">{esc(name)}</text>')
    aria = ("A timeline from 2013 to 2056. Above the axis, dated public statements by airport "
            "officials, politicians, critics and analysts. Below it, dated filings and actions, "
            "each coloured by the pot the plan reached into: airlines, bondholders, the gaming "
            "fund, the gas lease, federal relief, the Coverage Account, passengers. A dashed line "
            "marks Dec. 31, 2028, when the airline agreement and the gaming commitment end. The "
            "axis runs 2013 to 2031 at full width and is broken after 2031, with 2031 to 2057 "
            "compressed into the right-hand sixth. A small line under the filed lane traces the "
            "audited cost per boarded passenger on the Table IV cost basis, 2015 to 2024, from "
            "$12.89 to $7.34, with a 2020 spike to $20.50 when boardings collapsed.")
    return (f'<svg viewBox="0 0 {f.w} {f.h}" role="img" aria-label="{esc(aria)}">'
            + "".join(parts) + "</svg>")


def event_cards(events, docs, highlights, clips):
    out = []
    for r in events:
        said = r["category"] == "a"
        who = r["speaker"] if said else r["target"]
        lane = "Said" if said else "Filed"
        src = r["source_id"]
        doc = docs.get(src)
        clip = clips.get(src)
        srcline = []
        if doc:
            srcline.append(f'<a href="../documents/index.html#{esc(src)}">{esc(doc["title"])}</a>')
            if doc.get("sha256"):
                srcline.append(f'<code title="SHA-256 of the archived file">{esc(doc["sha256"][:12])}</code>')
        elif clip:
            srcline.append(f'{esc(clip.get("title", src))} (archived clip)')
            if clip.get("sha256"):
                srcline.append(f'<code title="SHA-256 of the archived capture">{esc(clip["sha256"][:12])}</code>')
        elif src:
            srcline.append(f'<code>{esc(src)}</code> (not in the archive)')
        else:
            srcline.append("no source on file")
        if r["pdf_page"]:
            key = (src, int(r["pdf_page"]))
            if key in highlights:
                h = highlights[key]
                srcline.append(f'<a class="pg" href="../{esc(h["image"])}" data-page="{esc(src)}-{int(r["pdf_page"])}">'
                               f'PDF {int(r["pdf_page"])}, see the page</a>')
            else:
                srcline.append(f'PDF {int(r["pdf_page"])}')
        srcline.append(f'Tier {esc(r["tier"])} · {esc(r["status"])}')
        if r["precision"] != "day":
            srcline.append("dated to the " + ("month" if r["precision"] == "month" else "year"))
        hay = " ".join([r["datetime"][:10], who, r["text"], r["detail"], src]).lower()
        out.append(
            f'<article class="ev {"said" if said else "filed"}" id="{esc(r["id"])}" data-hay="{esc(hay)}" '
            f'data-lane="{"said" if said else "filed"}" data-rail="{"1" if r["rail"] == "1" else "0"}">'
            f'<div class="evh"><span class="when">{esc(fmt_date(r["datetime"], r["precision"]))}</span>'
            f'<span class="lane">{lane}</span><span class="who">{esc(who)}</span></div>'
            f'<p class="evt">{esc(r["text"])}</p>'
            f'<p class="evd">{esc(r["detail"])}</p>'
            f'<p class="evs">{" · ".join(srcline)}</p></article>')
    return "".join(out)


# ---------------------------------------------------------------- the coverage walk

def coverage_svg(layers):
    f = Frame(w=980, h=420, l=64, r=28, t=28, b=46)
    years = [r["year"] for r in layers]
    y = Scale(0, 1.75, f.ybot, f.ytop)
    n = len(years)
    gap = (f.x1 - f.x0) / n
    bw = gap * 0.58
    parts = []
    for t in (0.25, 0.5, 0.75, 1.0, 1.25, 1.5):
        parts.append(f'<line x1="{f.x0}" y1="{y(t):.1f}" x2="{f.x1}" y2="{y(t):.1f}" stroke="var(--grid)" stroke-width="1"/>')
        parts.append(f'<text class="ax" x="{f.x0 - 8}" y="{y(t) + 3.5:.1f}" text-anchor="end">{t:.2f}</text>')
    parts.append(f'<line x1="{f.x0}" y1="{y(1.25):.1f}" x2="{f.x1}" y2="{y(1.25):.1f}" stroke="var(--red)" '
                 'stroke-width="1.6" stroke-dasharray="6 4" class="rule125"/>')
    parts.append(f'<text class="lab2" x="{f.x1}" y="{y(1.25) - 6:.1f}" text-anchor="end" fill="var(--red)">'
                 'The promise: 1.25 times debt service</text>')
    parts.append(f'<line x1="{f.x0}" y1="{y(1.0):.1f}" x2="{f.x1}" y2="{y(1.0):.1f}" stroke="var(--ink2)" '
                 'stroke-width="1" class="rule100"/>')
    for i, r in enumerate(layers):
        x0 = f.x0 + gap * i + (gap - bw) / 2
        op, pl, pr = num(r["ratio_operating"]), num(r["ratio_pledged"]), num(r["ratio_printed"])
        future = int(r["year"]) >= 2029
        cls_f = " future" if future else ""
        # operating layer
        parts.append(f'<rect class="layer op{cls_f}" x="{x0:.1f}" y="{y(op):.1f}" width="{bw:.1f}" '
                     f'height="{y(0) - y(op):.1f}" fill="var(--ink2)"/>')
        # designated gaming layer
        parts.append(f'<rect class="layer gam{cls_f}" x="{x0:.1f}" y="{y(pl):.1f}" width="{bw:.1f}" '
                     f'height="{y(op) - y(pl):.1f}" fill="var(--yellow)"/>')
        # coverage account layer
        parts.append(f'<rect class="layer cov{cls_f}" x="{x0:.1f}" y="{y(pr):.1f}" width="{bw:.1f}" '
                     f'height="{y(pl) - y(pr):.1f}" fill="var(--blue)"/>')
        cx = x0 + bw / 2
        parts.append(f'<text class="val v-printed" x="{cx:.1f}" y="{y(pr) - 6:.1f}" text-anchor="middle">{pr:.2f}</text>')
        parts.append(f'<text class="val v-pledged" x="{cx:.1f}" y="{y(pl) - 6:.1f}" text-anchor="middle">{pl:.2f}</text>')
        parts.append(f'<text class="val v-operating" x="{cx:.1f}" y="{y(op) - 6:.1f}" text-anchor="middle">{op:.2f}</text>')
        parts.append(f'<text class="ax" x="{cx:.1f}" y="{f.ybot + 18}" text-anchor="middle">{esc(r["year"])}</text>')
    # shade the years past the commitment
    xs = f.x0 + gap * 4
    parts.append(f'<rect class="past2028" x="{xs:.1f}" y="{f.ytop}" width="{gap * 2:.1f}" height="{f.ybot - f.ytop:.1f}" '
                 'fill="var(--red)" opacity="0"/>')
    parts.append(f'<text class="lab2 past2028-l" x="{xs + gap:.1f}" y="{f.ytop - 8}" text-anchor="middle" '
                 'fill="var(--red)" opacity="0">past the airline agreement and the gaming commitment</text>')
    # legend
    lx = f.x0
    for i, (lab, col, cls) in enumerate((("Operations, after expenses", "var(--ink2)", "op"),
                                         ("Designated Gaming Act money", "var(--yellow)", "gam"),
                                         ("Coverage Account deposit", "var(--blue)", "cov"))):
        parts.append(f'<rect class="layer {cls}" x="{lx + i * 230}" y="{f.h - 14}" width="10" height="10" fill="{col}"/>'
                     f'<text class="ax" x="{lx + i * 230 + 14}" y="{f.h - 5}">{lab}</text>')
    aria = ("The consultant's 2025 coverage forecast, 2025 through 2030, as three stacked layers "
            "against the 1.25 covenant line. The full stack prints 1.60, 1.37, 1.36, 1.37, 1.43 and "
            "1.44, above 1.25 in every year. Without the Coverage Account deposit the ratio is "
            "1.35, 1.12, 1.13, 1.12, 1.18 and 1.19, below 1.25 in five of six years. Without the "
            "designated Gaming Act money as well, operations alone give 1.20, 0.98, 1.00, 0.99, "
            "1.06 and 1.06, below 1.0 in 2026 and 2028. The division is this record's.")
    return (f'<svg viewBox="0 0 {f.w} {f.h}" role="img" aria-label="{esc(aria)}" class="covfig">'
            + "".join(parts) + "</svg>")


def coverage_table(layers):
    h = ("<div class=\"scroll\"><table><thead><tr><th>Year</th><th class=\"num\">Net Revenues ($k)</th>"
         "<th class=\"num\">of which designated ($k)</th><th class=\"num\">Coverage Account ($k)</th>"
         "<th class=\"num\">Debt service ($k)</th><th class=\"num\">Printed</th>"
         "<th class=\"num\">Pledged alone</th><th class=\"num\">Operations alone</th></tr></thead><tbody>")
    for r in layers:
        h += (f'<tr><td>{esc(r["year"])}</td><td class="num">{int(num(r["net_revenues_k"])):,}</td>'
              f'<td class="num">{int(num(r["designated_opr_k"])):,}</td>'
              f'<td class="num">{int(num(r["coverage_amount_k"])):,}</td>'
              f'<td class="num">{int(num(r["aggregate_annual_debt_service_k"])):,}</td>'
              f'<td class="num">{num(r["ratio_printed"]):.2f}</td><td class="num">{num(r["ratio_pledged"]):.2f}</td>'
              f'<td class="num">{num(r["ratio_operating"]):.2f}</td></tr>')
    h += "</tbody></table></div>"
    return h


STEPS = [
    ("1", "The promise",
     "When the Authority borrowed to build the terminal it promised the people buying its debt that "
     "each year's revenue available for the payments would be at least 1.25 times the payments. The "
     "consultant's forecast, filed with the 2025 bonds, prints the ratio for six years: 1.60, 1.37, "
     "1.36, 1.37, 1.43 and 1.44. Every year clears the line."),
    ("2", "Take away the deposit the Authority elects to make",
     "The indenture lets a Coverage Account count toward the test. It is filled from revenue at the "
     "Authority's monthly discretion and capped at a quarter of the year's debt payments. The forecast "
     "assumes it at that ceiling in five of the six years. The bond statement says the rates charged "
     "before the terminal opened fund its required increase, so the carriers pay into it. Without it, "
     "the same rows give 1.35, 1.12, 1.13, 1.12, 1.18 and 1.19. Five of six fall below 1.25. The "
     "division is this record's."),
    ("3", "Take away the state's gaming money",
     "Footnote 1 on the forecast table says Net Revenues include Other Pledged Revenues, which from 2025 "
     "is entirely Gaming Act money the Authority designates into the pledge. Subtract it and what the "
     "airport earns from running the airport, after expenses, is 1.20, 0.98, 1.00, 0.99, 1.06 and 1.06. "
     "In 2026 and 2028 operations do not cover debt service at all."),
    ("4", "Everything ends in 2028",
     "Under the airlines' January 2025 vote, the Authority committed $11.575 million a year of that "
     "gaming money for 2026 through 2028. The forecast carries the same figure into 2029 and 2030 on "
     "nothing firmer than an expectation. The "
     "airline agreement that makes the carriers responsible for the shortfall ends Dec. 31, 2028. The "
     "bonds run to 2056."),
    ("5", "The covenant is met",
     "The indenture does not ask where the money comes from, and on the test it sets, the forecast "
     "complies in every year it covers. The finding is what the ratio is on pledged net revenues "
     "alone, in those words, and what is underneath that."),
]


def coverage_walk(layers):
    steps = "".join(
        f'<div class="step" data-step="{n}"><h3>{esc(t)}</h3><p>{esc(b)}</p></div>' for n, t, b in STEPS)
    return (f'<section class="scrolly" id="walk" data-active="1">'
            f'<div class="sticky"><figure>{coverage_svg(layers)}'
            f'<figcaption>Official Statement 2025A/B, PDF 202 (printed B-16) and Exhibit E, PDF 316. '
            f'Bars from <code>02-data/coverage-three-layers.csv</code>, drawn by <code>build_explore.py</code>. '
            f'Years 2029 and 2030 are past the airline agreement and the gaming commitment.</figcaption>'
            f'<details><summary>Show the data</summary>{coverage_table(layers)}</details></figure></div>'
            f'<div class="steps">{steps}</div></section>')


# ---------------------------------------------------------------- every number on its page

def pages_section(cited, docs, highlights, claims):
    by_id = {c["id"]: c for c in claims}
    cards = []
    for r in cited:
        doc = docs.get(r["doc_id"])
        if not doc:
            continue
        p = int(r["pdf_page"])
        h = highlights.get((r["doc_id"], p))
        ids = [x for x in (r["claim_ids"] or "").split("|") if x]
        texts = []
        for cid in ids:
            c = by_id.get(cid)
            if not c:
                continue
            t = c["text"]
            # the Oct. 19 map's claim column is a label; the draft sentence reads as a claim
            if c["set"] == "teams" and len(t.split()) < 7 and c.get("draft"):
                t = c["draft"]
            if t not in texts:
                texts.append(t)
        texts = texts[:3]
        terms = [t for t in (r["terms"] or "").split("|") if t][:8]
        if h:
            thumb = (f'<a class="pg" href="../{esc(h["image"])}" data-page="{esc(r["doc_id"])}-{p}">'
                     f'<img src="../{esc(h["thumb"])}" alt="Page {p} of {esc(doc["title"])}" loading="lazy" '
                     f'width="{h.get("width_px", 0) // 4 if h.get("width_px") else ""}"></a>')
            printed = f' (printed {esc(h["printed_page"])})' if h.get("printed_page") else ""
        else:
            thumb = '<div class="nopage">page not rendered</div>'
            printed = ""
        found = ", ".join(esc(t) for t in (h["terms_found"].keys() if h else terms))
        cards.append(
            f'<article class="pagecard" data-hay="{esc((doc["title"] + " " + " ".join(texts) + " " + found).lower())}" '
            f'data-doc="{esc(r["doc_id"])}">'
            f'{thumb}<div class="pc">'
            f'<p class="pch"><a href="../documents/index.html#{esc(r["doc_id"])}">{esc(doc["title"])}</a>'
            f' · PDF {p}{printed}</p>'
            + "".join(f'<p class="pct">{esc(t)}</p>' for t in texts)
            + (f'<p class="pcf">On the page: {found}</p>' if found else "")
            + f'<p class="pcs"><code>{esc(doc.get("sha256", "")[:16])}</code> · Tier {esc(doc["tier"])}</p>'
            f'</div></article>')
    return "".join(cards)


def viewer_js(highlights):
    # the viewer: a dialog with the full page and the highlight boxes, keyed by doc-page
    boxes = {}
    for (d, p), h in highlights.items():
        rects = []
        for t, rs in h.get("terms_found", {}).items():
            for rc in rs:
                rects.append([t] + [round(v, 4) for v in rc])
        boxes[f"{d}-{p}"] = dict(img="../" + h["image"], rects=rects,
                                 title=f"{d}, PDF {p}" + (f" (printed {h['printed_page']})" if h.get("printed_page") else ""))
    return ("<script>var PAGES=" + json.dumps(boxes, separators=(",", ":")) + ";"
            """
(function(){
  var dlg=document.getElementById('viewer'); if(!dlg||!dlg.showModal) return;
  var img=dlg.querySelector('img'), lay=dlg.querySelector('.hl'), ttl=dlg.querySelector('.vt');
  document.addEventListener('click',function(e){
    var a=e.target.closest('a.pg'); if(!a) return;
    var k=a.dataset.page, p=PAGES[k]; if(!p) return;
    e.preventDefault();
    ttl.textContent=p.title; img.src=p.img; lay.innerHTML='';
    p.rects.forEach(function(r){
      var b=document.createElement('span'); b.className='box'; b.title=r[0];
      b.style.left=(r[1]*100)+'%'; b.style.top=(r[2]*100)+'%';
      b.style.width=((r[3]-r[1])*100)+'%'; b.style.height=((r[4]-r[2])*100)+'%';
      lay.appendChild(b);
    });
    dlg.showModal();
  });
  dlg.querySelector('.close').onclick=function(){dlg.close()};
  dlg.addEventListener('click',function(e){ if(e.target===dlg) dlg.close(); });
})();
</script>""")


# ---------------------------------------------------------------- claim explorer

SET_LABEL = {"record": "The covenant record (Sept. 1)", "v29": "The story, Sept. 7 ledger",
             "teams": "The story, Oct. 19 map"}


def claims_section(claims, docs, highlights):
    secs = []
    for key in ("teams", "v29", "record"):
        items = [c for c in claims if c["set"] == key]
        rowsh = []
        for c in items:
            links = []
            for d, p in c["docs"]:
                doc = docs.get(d)
                label = f"{d} PDF {p}"
                if (d, p) in highlights:
                    h = highlights[(d, p)]
                    links.append(f'<a class="pg" href="../{esc(h["image"])}" data-page="{esc(d)}-{p}">{esc(label)}</a>')
                elif doc:
                    links.append(f'<a href="../documents/index.html#{esc(d)}">{esc(label)}</a>')
                else:
                    links.append(esc(label))
            hay = " ".join([c["id"], c["text"], c.get("where", ""), c["note"], " ".join(d for d, _ in c["docs"])]).lower()
            docset = " ".join(sorted(set(d for d, _ in c["docs"]))) or "none"
            rowsh.append(
                f'<tr data-hay="{esc(hay)}" data-standing="{esc(c["standing"])}" data-doc="{esc(docset)}">'
                f'<td class="cid">{esc(c["id"])}</td><td>{esc(c["text"])}'
                + (f'<div class="cnote">{esc(c["note"])}</div>' if c["note"] else "")
                + f'</td><td><span class="st st-{esc(c["standing"])}">{esc(STANDING_LABEL.get(c["standing"], c["standing"]))}</span></td>'
                f'<td class="cdoc">{" · ".join(links) or "—"}</td></tr>')
        secs.append(f'<section class="topic" id="set-{key}"><h3>{esc(SET_LABEL[key])} '
                    f'<span class="gn">{len(items)} records</span></h3>'
                    f'<div class="scroll"><table class="claims"><thead><tr><th>Id</th><th>Claim</th>'
                    f'<th>Standing</th><th>Document and page</th></tr></thead><tbody>{"".join(rowsh)}</tbody></table></div></section>')
    standings = [(k, STANDING_LABEL[k]) for k in ("holds", "ours", "carry", "tierc", "open", "fix", "decide", "slot")]
    chips = "".join(f'<button class="chip" aria-pressed="false" data-group="standing" data-value="{k}">{esc(v)}</button>'
                    for k, v in standings)
    bar = (f'<div class="bar tool"><input id="q" type="search" placeholder="Search claims, notes, document ids" '
           f'aria-label="Search claims"><div class="chips"><span class="flab">Standing</span>{chips}</div>'
           f'<div class="countrow"><span class="count" id="count"></span>'
           f'<button class="clear" id="clear" hidden>Clear filters</button></div></div>')
    return bar + "".join(secs) + '<p id="empty" hidden>Nothing matches.</p>'


# ---------------------------------------------------------------- page

EXTRA_CSS = """
.wrap{max-width:64rem}
.lede{font-size:1.08rem;color:var(--ink2);max-width:46rem}
.inst{margin:3rem 0 0;border-top:2px solid var(--ink);padding-top:1rem}
.inst .kicker{margin-bottom:.2rem}
.inst h2{margin-top:0}
.evs,.pcs,.pcf,.cnote,figcaption{font-family:system-ui,sans-serif;font-size:.78rem;color:var(--muted)}
figcaption{margin:.4rem 0 .2rem}
/* rail */
.dot circle{transition:r .15s}
.dot:hover circle{r:7}
.evlist{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(19rem,100%),1fr));gap:.8rem;margin:1rem 0}
.ev{background:var(--surface);border:1px solid var(--ring);border-radius:12px;padding:.9rem 1rem;
font-family:system-ui,sans-serif;font-size:.9rem;line-height:1.5}
.ev:target{outline:2px solid var(--blue);outline-offset:2px}
.ev.filed{border-left:4px solid var(--red)}
.ev.said{border-left:4px solid var(--ink2)}
.evh{display:flex;flex-wrap:wrap;gap:.5rem;align-items:baseline;font-size:.76rem;color:var(--muted)}
.evh .when{font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}
.evh .lane{text-transform:uppercase;letter-spacing:.08em;font-size:.66rem}
.evh .who{color:var(--ink2)}
.evt{margin:.4rem 0 .3rem;color:var(--ink);font-family:Georgia,serif;font-size:.98rem}
.evd{margin:0 0 .4rem;color:var(--ink2);font-size:.84rem}
.evs{margin:0}
.evs code{font-size:.72rem}
.lanebar{display:flex;flex-wrap:wrap;gap:.4rem;margin:.6rem 0 0}
/* chips, shared look with the claims page */
.chip{font:inherit;font-family:system-ui,sans-serif;font-size:.78rem;padding:.28rem .7rem;border-radius:99px;
border:1px solid var(--ring);background:var(--surface);color:var(--ink);cursor:pointer}
.chip[aria-pressed=true]{background:var(--blue);color:#fff;border-color:var(--blue)}
.bar.tool{margin:1rem 0 .4rem;font-family:system-ui,sans-serif}
.bar input{width:100%;font:inherit;font-size:.95rem;padding:.55rem .8rem;border:1px solid var(--ring);
border-radius:10px;background:var(--surface);color:var(--ink);margin-bottom:.5rem}
.chips{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center}
.flab{font-size:.7rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-right:.2rem}
.countrow{display:flex;justify-content:space-between;align-items:center;margin-top:.5rem;font-size:.8rem;color:var(--muted)}
.clear{font:inherit;font-size:.78rem;border:none;background:none;color:var(--blue);cursor:pointer;text-decoration:underline}
/* scrolly */
.scrolly{display:grid;grid-template-columns:minmax(0,1fr) 19rem;gap:2rem;margin:1rem 0 2rem}
.scrolly .sticky{position:sticky;top:1rem;align-self:start}
.scrolly .steps{padding-top:.5rem}
.step{min-height:55vh;display:flex;flex-direction:column;justify-content:center;opacity:.35;transition:opacity .3s}
.step h3{margin:0 0 .4rem;font-size:1rem}
.step p{margin:0;font-size:.95rem}
.scrolly[data-active="1"] .step[data-step="1"],.scrolly[data-active="2"] .step[data-step="2"],
.scrolly[data-active="3"] .step[data-step="3"],.scrolly[data-active="4"] .step[data-step="4"],
.scrolly[data-active="5"] .step[data-step="5"]{opacity:1}
.covfig .layer{transition:opacity .45s}
.covfig .val{transition:opacity .45s}
.scrolly[data-active="1"] .v-pledged,.scrolly[data-active="1"] .v-operating,
.scrolly[data-active="5"] .v-pledged,.scrolly[data-active="5"] .v-operating{opacity:0}
.scrolly[data-active="2"] .layer.cov,.scrolly[data-active="2"] .v-printed,.scrolly[data-active="2"] .v-operating{opacity:.12}
.scrolly[data-active="2"] .v-operating{opacity:0}
.scrolly[data-active="3"] .layer.cov,.scrolly[data-active="3"] .layer.gam,
.scrolly[data-active="3"] .v-printed,.scrolly[data-active="3"] .v-pledged{opacity:.12}
.scrolly[data-active="4"] .layer.cov,.scrolly[data-active="4"] .v-printed,.scrolly[data-active="4"] .v-operating{opacity:.12}
.scrolly[data-active="4"] .layer.gam.future{opacity:.35}
.scrolly[data-active="4"] .past2028,.scrolly[data-active="4"] .past2028-l{opacity:.08}
.scrolly[data-active="4"] .past2028-l{opacity:1}
.scrolly.nojs .step{opacity:1;min-height:0;margin:0 0 1.2rem}
@media(max-width:760px){.scrolly{grid-template-columns:1fr}.scrolly .sticky{position:relative;top:0}
.step{min-height:0;margin:0 0 1.2rem;opacity:1}}
/* pages */
.pages{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(17rem,100%),1fr));gap:.9rem;margin:1rem 0}
.pagecard{display:grid;grid-template-columns:5.2rem 1fr;gap:.7rem;background:var(--surface);border:1px solid var(--ring);
border-radius:12px;padding:.7rem;font-family:system-ui,sans-serif;font-size:.84rem}
.pagecard img{width:100%;height:auto;border:1px solid var(--ring);border-radius:4px;background:#fff}
.nopage{width:100%;aspect-ratio:3/4;border:1px dashed var(--ring);border-radius:4px;font-size:.68rem;color:var(--muted);
display:flex;align-items:center;justify-content:center;text-align:center;padding:.3rem}
.pch{margin:0 0 .3rem;font-size:.78rem;color:var(--muted)}
.pct{margin:0 0 .3rem;color:var(--ink);font-family:Georgia,serif;font-size:.9rem;line-height:1.4}
.pcf{margin:.2rem 0 0}
.pcs{margin:.3rem 0 0}
dialog#viewer{border:none;border-radius:12px;padding:0;max-width:min(96vw,60rem);width:100%;background:var(--surface);color:var(--ink)}
dialog#viewer::backdrop{background:rgba(0,0,0,.6)}
.vh{display:flex;justify-content:space-between;align-items:center;padding:.6rem .9rem;border-bottom:1px solid var(--ring);
font-family:system-ui,sans-serif;font-size:.85rem}
.vh button{font:inherit;border:1px solid var(--ring);background:var(--surface);color:var(--ink);border-radius:99px;padding:.2rem .7rem;cursor:pointer}
.vb{position:relative;max-height:82vh;overflow:auto}
.vb img{display:block;width:100%;height:auto}
.hl{position:absolute;inset:0;pointer-events:none}
.hl .box{position:absolute;border:2px solid var(--red);background:color-mix(in srgb,var(--yellow) 35%,transparent);border-radius:2px;pointer-events:auto}
/* claims */
table.claims td{vertical-align:top}
.cid{font-family:"Cascadia Code",Consolas,monospace;font-size:.74rem;color:var(--muted);white-space:nowrap}
.cnote{margin-top:.25rem}
.cdoc{font-size:.78rem;white-space:nowrap}
.st{display:inline-block;font-size:.7rem;padding:.1rem .5rem;border-radius:99px;border:1px solid var(--ring);white-space:nowrap}
.st-holds{border-color:var(--aqua);color:var(--aqua)}
.st-ours{border-color:var(--blue);color:var(--blue)}
.st-carry{border-color:var(--ink2);color:var(--ink2)}
.st-tierc,.st-open,.st-decide,.st-slot,.st-restore{border-color:var(--yellow);color:var(--yellow)}
.st-fix{border-color:var(--red);color:var(--red)}
section.topic h3{display:flex;justify-content:space-between;align-items:baseline}
.gn{font-size:.72rem;color:var(--muted);font-weight:400}
@media print{.scrolly{display:block}.scrolly .sticky{position:static}.step{opacity:1;min-height:0}
.pagecard,.ev{break-inside:avoid}dialog{display:none}}
"""

SCROLLY_JS = """<script>
(function(){
  var s=document.getElementById('walk'); if(!s) return;
  var steps=[].slice.call(s.querySelectorAll('.step'));
  if(!steps.length){ s.classList.add('nojs'); return; }
  // The step whose centre is nearest the viewport's centre is the active one. A scroll
  // handler rather than IntersectionObserver alone, so a throttled or background tab,
  // a print preview and a keyboard scroll all land on the same answer.
  var ticking=false;
  function pick(){
    ticking=false;
    var mid=window.innerHeight/2, best=null, bd=1e9;
    steps.forEach(function(st){
      var r=st.getBoundingClientRect(), c=(r.top+r.bottom)/2, d=Math.abs(c-mid);
      if(d<bd){bd=d;best=st;}
    });
    if(best) s.setAttribute('data-active', best.dataset.step);
  }
  // setTimeout, not requestAnimationFrame: rAF is paused in a background tab, and a
  // reader who switches back should find the step they left, not the first one.
  function onscroll(){ if(!ticking){ ticking=true; setTimeout(pick, 40); } }
  window.addEventListener('scroll', onscroll, {passive:true});
  window.addEventListener('resize', onscroll);
  // While the walk is on screen, poll as well: some embedded and emulated viewports
  // never dispatch scroll events to window, and a poll costs nothing while hidden.
  // Five getBoundingClientRect calls four times a second is nothing, and it needs no
  // event the environment might withhold.
  setInterval(function(){ if(!document.hidden) pick(); }, 250);
  pick();
})();
</script>"""

LANE_JS = """<script>
(function(){
  var chips=[].slice.call(document.querySelectorAll('.lanebar .chip')), cards=[].slice.call(document.querySelectorAll('.ev'));
  var lane='all', rail=false;
  function apply(){ cards.forEach(function(c){
    var ok=(lane==='all'||c.dataset.lane===lane)&&(!rail||c.dataset.rail==='1'); c.hidden=!ok; }); }
  chips.forEach(function(ch){ ch.onclick=function(){
    if(ch.dataset.lane){ lane=ch.dataset.lane; chips.forEach(function(x){ if(x.dataset.lane) x.setAttribute('aria-pressed', x===ch?'true':'false'); }); }
    else { rail=!rail; ch.setAttribute('aria-pressed', rail?'true':'false'); }
    apply(); }; });
})();
</script>"""


def build():
    events = load_events()
    docs = load_docs()
    clips = load_clips()
    highlights = load_highlights()
    layers = rows("coverage-three-layers.csv")
    cpe = [r for r in rows("cpe-audited-acfr.csv") if r.get("cpe_audited")]
    cpe.sort(key=lambda r: int(r["year"]))
    cited = [r for r in rows("cited-pages.csv") if r["doc_id"] in docs]
    cited.sort(key=lambda r: (r["doc_id"], int(r["pdf_page"])))
    claims = load_claims()

    n_said = sum(1 for r in events if r["category"] == "a")
    n_filed = sum(1 for r in events if r["category"] == "b")
    n_pages = sum(1 for r in cited if (r["doc_id"], int(r["pdf_page"])) in highlights)
    n_boxed = sum(1 for r in cited if highlights.get((r["doc_id"], int(r["pdf_page"])), {}).get("terms_found"))
    n_rail = sum(1 for r in events if r["rail"] == "1")

    body = []
    body.append('<p class="kicker">Explore the record</p>'
                '<h1>What they said, and what they filed</h1>'
                '<p class="lede">The reporting on Pittsburgh International\'s terminal financing rests on '
                'documents the Airport Authority publishes and files. This page lets you walk the record '
                'four ways: along the years, through the 1.25 test one layer at a time, down to the page '
                'a number sits on, and across every claim the story makes. Nothing here is drawn by hand. '
                'Every figure comes from a data file in <code>02-data/</code>, every filing is hashed, '
                'every clip is an archived capture, and the command at the foot of the page rebuilds all of it.</p>')

    # 1 rail
    body.append('<section class="inst" id="rail"><p class="kicker">One</p><h2>The years, in two lanes</h2>'
                f'<p class="sub">{n_said} dated statements above the line, from the hashed filings and the '
                f'archived clips. {n_filed} dated filings and actions below it, each coloured by the pot the plan '
                'reached into. Click a dot to open its card. The axis is broken after 2031 so the end of the '
                'debt fits. The line under the filed lane is the audited cost per boarded passenger, which fell '
                'through the subsidy years and the years of capitalized interest, and rose when the debt arrived.</p>')
    body.append(rail_svg(events, cpe))
    body.append('<figcaption>Events from <code>02-data/timeline-events.csv</code>; the arc from '
                '<code>02-data/cpe-audited-acfr.csv</code> (ACAA audited reports, Table IV cost basis; the bond '
                'statement\'s series is a different basis and is not drawn). A statement is Tier C: an '
                'utterance and a date, never a figure; a figure inside a clip is attributed to the paper. '
                'Dates to the month or year are marked on the card.</figcaption>')
    body.append('<div class="lanebar"><button class="chip" aria-pressed="true" data-lane="all">All</button>'
                '<button class="chip" aria-pressed="false" data-lane="said">Said</button>'
                '<button class="chip" aria-pressed="false" data-lane="filed">Filed</button>'
                f'<button class="chip" aria-pressed="false" data-railonly="1">The rail only ({n_rail} events)</button></div>')
    body.append(f'<div class="evlist">{event_cards(events, docs, highlights, clips)}</div></section>')

    # 2 walk
    body.append('<section class="inst" id="covenant"><p class="kicker">Two</p><h2>The 1.25 test, taken apart</h2>'
                '<p class="sub">The bond covenant is a margin, not a payment. Scroll, and the forecast comes '
                'apart into the three kinds of money that meet it.</p>')
    body.append(coverage_walk(layers))
    body.append('</section>')

    # 3 pages
    body.append('<section class="inst" id="pages"><p class="kicker">Three</p><h2>Every number, on its page</h2>'
                f'<p class="sub">{len(cited)} document pages carry the story\'s figures. {n_pages} are rendered here '
                f'from the hashed PDFs, and on {n_boxed} of them the cited figure is boxed. Where a page carries no box, '
                'the figure the story takes from it is this record\'s own arithmetic, which no page prints. '
                'Open one and check it against the number in the prose.</p>')
    body.append(f'<div class="pages">{pages_section(cited, docs, highlights, claims)}</div>')
    body.append('<figcaption>Pages rendered by <code>03-harness/render_pages.py</code> from '
                '<code>01-sources-archive/raw/</code>; boxes from <code>02-data/page-highlights.json</code>. '
                'A page that is not rendered is a clip, a snapshot or a page not yet drawn.</figcaption></section>')

    # 4 claims
    body.append('<section class="inst" id="claims"><p class="kicker">Four</p><h2>Every claim, and where it stands</h2>'
                f'<p class="sub">{len(claims)} rows across three ledgers: the covenant record\'s claims, the Sept. 7 '
                'check of the story\'s forty-eighth draft, and the Oct. 19 map of the editor\'s working copy. A '
                'claim that reproduces from a document says so. One that is our arithmetic says so. One that '
                'needs a fix says that too.</p>')
    body.append(claims_section(claims, docs, highlights))
    body.append('</section>')

    # viewer
    body.append('<dialog id="viewer"><div class="vh"><span class="vt"></span><button class="close">close</button></div>'
                '<div class="vb"><img alt="Document page"><div class="hl"></div></div></dialog>')

    body.append(f'<p class="src">Lena Rose Williams · Newsworks Lab · built {BUILT} · '
                'CC BY 4.0 for the page, documents as published by their issuers. Rebuild: '
                '<code>python 03-harness/render_pages.py &amp;&amp; python 03-harness/build_explore.py</code>; '
                'verify: <code>python 03-harness/build_explore.py --check</code>.</p>')

    html = page("Explore the record: what they said, and what they filed", "".join(body),
                extra_js=SCROLLY_JS + LANE_JS + FILTER_JS + viewer_js(highlights), extra_css=EXTRA_CSS)
    return html


def main():
    html = build()
    if "--check" in sys.argv:
        if not os.path.exists(OUT):
            print("explore/index.html missing"); sys.exit(1)
        on_disk = io.open(OUT, encoding="utf-8", newline="").read()
        if on_disk != html:
            print("explore/index.html has drifted from its data"); sys.exit(1)
        print("explore/index.html reproduces"); return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write(html)
    print(f"wrote {os.path.relpath(OUT, ROOT)} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
