#!/usr/bin/env python3
"""build_explore.py — one chart: cost per enplaned passenger, predicted, reported, forecast.

Every plotted value comes from a CSV under 02-data/; the SVG is written at build time;
--check re-renders in memory and byte-diffs against explore/index.html.

    python 03-harness/build_explore.py
    python 03-harness/build_explore.py --check

Inputs:
    02-data/cpe-series.csv        the Authority's reported series and the two consultant forecasts
    02-data/cpe-predictions.csv   public predictions and budget figures, dated and sourced
    02-data/cpe-billed.csv        the billed charge for 2024 and 2025, Table III over boardings
    02-data/documents.csv         titles and hashes
"""
import io, os, sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_explainer import page, rows, num  # noqa: E402
from charts import esc, Frame, Scale, axis_y, gapped_path  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "02-data")
OUT = os.path.join(ROOT, "explore", "index.html")
BUILT = "2026-10-20"

TITLE = "Cost per enplaned passenger at Pittsburgh International: predicted, reported, forecast"

SERIES = {
    "Reported actual": ("Reported by the Authority (2025 bond statement, PDF 62; 2014 to 2019 from the "
                        "statistical section)", "var(--ink)", None, 2.2),
    "2021 OS (base case)": ("Consultant forecast, 2021 bond statement (PDF 185), base case",
                            "var(--blue)", "6 4", 1.8),
    "2025 OS (base case)": ("Consultant forecast, 2025 bond statement (PDF 202)",
                            "var(--orange)", "6 4", 1.8),
}


def fmt_date(iso):
    d = datetime.fromisoformat(iso)
    s = d.strftime("%b. %d, %Y").replace(" 0", " ")
    for a, b in (("May.", "May"), ("Jun.", "June"), ("Jul.", "July"), ("Sep.", "Sept.")):
        s = s.replace(a, b)
    return s


def chart(series, preds, billed):
    f = Frame(w=980, h=540, l=58, r=26, t=22, b=46)
    x = Scale(2011, 2031, f.x0, f.x1)
    y = Scale(0, 26, f.ybot, f.ytop)
    parts = []
    parts.append(axis_y(f, y, [0, 5, 10, 15, 20, 25], fmt=lambda v: f"${v:.0f}"))
    parts.append(f'<line x1="{f.x0}" y1="{f.ybot:.1f}" x2="{f.x1}" y2="{f.ybot:.1f}" stroke="var(--axis)"/>')
    for yr in range(2011, 2031):
        X = x(yr + 0.5)
        parts.append(f'<line x1="{X:.1f}" y1="{f.ybot:.1f}" x2="{X:.1f}" y2="{f.ybot + 4:.1f}" stroke="var(--axis)"/>')
        if yr % 2 == 1 or yr == 2030:
            parts.append(f'<text class="ax" x="{X:.1f}" y="{f.ybot + 18:.1f}" text-anchor="middle">{yr}</text>')
    # Dec. 31, 2028
    xc = x(2029.0)
    parts.append(f'<line x1="{xc:.1f}" y1="{f.ytop}" x2="{xc:.1f}" y2="{f.ybot:.1f}" stroke="var(--red)" '
                 'stroke-width="1.2" stroke-dasharray="3 3"/>')
    parts.append(f'<text class="lab2" x="{xc - 5:.1f}" y="{f.ytop + 11}" text-anchor="end" fill="var(--red)">'
                 'Airline agreement and gaming commitment end, Dec. 31, 2028</text>')
    # the three series
    for name, (label, colour, dash, width) in SERIES.items():
        pts = [(x(int(r["year"]) + 0.5), y(num(r["cpe"]))) for r in series if r["series"] == name]
        parts.append(gapped_path(pts, colour, width=width, dash=dash))
        for px, py in pts:
            parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.6" fill="{colour}"/>')
    # billed, squares
    for r in billed:
        px, py = x(int(r["year"]) + 0.5), y(num(r["cpe_billed"]))
        parts.append(f'<rect x="{px - 4.5:.1f}" y="{py - 4.5:.1f}" width="9" height="9" fill="var(--ink)" '
                     'stroke="var(--plane)" stroke-width="1"/>')
        parts.append(f'<text class="lab2" x="{px - 7:.1f}" y="{py - 8:.1f}" text-anchor="end">'
                     f'${num(r["cpe_billed"]):.2f} billed</text>')
    # predictions
    for r in preds:
        px = x(int(r["year_for"]) + 0.5)
        lo = num(r["value_lo"])
        hi = num(r["value_hi"]) if r["value_hi"] else None
        open_mark = r["tier"] != "A"
        fill = "var(--plane)" if open_mark else "var(--red)"
        if hi is not None:
            y0, y1 = y(hi), y(lo)
            parts.append(f'<line x1="{px:.1f}" y1="{y0:.1f}" x2="{px:.1f}" y2="{y1:.1f}" stroke="var(--red)" stroke-width="2.4"/>')
            for yy in (y0, y1):
                parts.append(f'<line x1="{px - 5:.1f}" y1="{yy:.1f}" x2="{px + 5:.1f}" y2="{yy:.1f}" stroke="var(--red)" stroke-width="2"/>')
            py = (y0 + y1) / 2
        else:
            py = y(lo)
            parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="{fill}" stroke="var(--red)" stroke-width="2"/>')
        pos = r["label_pos"]
        if pos == "leader":
            # the label sits where the data file puts it, in chart units, with a leader to the mark
            lx, ly, anchor = x(num(r["label_x"])), y(num(r["label_y"])), "middle"
            parts.append(f'<line x1="{px:.1f}" y1="{py + (6 if ly > py else -6):.1f}" x2="{lx:.1f}" '
                         f'y2="{ly - 10 if ly > py else ly + 3:.1f}" stroke="var(--red)" stroke-width=".8" opacity=".7"/>')
            ly = ly + 3
        elif pos == "right":
            lx, ly, anchor = px + 9, py + 4, "start"
        elif pos == "left":
            lx, ly, anchor = px - 9, py + 4, "end"
        elif pos == "above":
            lx, ly, anchor = px, py - 10, "middle"
        else:
            lx, ly, anchor = px, py + 20, "middle"
        parts.append(f'<text class="lab2" x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" fill="var(--red)">'
                     f'{esc(r["label"])}</text>')
    rep = [r for r in series if r["series"] == "Reported actual"]
    f21 = [r for r in series if r["series"] == "2021 OS (base case)"]
    f25 = [r for r in series if r["series"] == "2025 OS (base case)"]
    aria = (f"Cost per enplaned passenger at Pittsburgh International, dollars, 2011 to 2030. The "
            f"Authority's reported figure runs from ${num(rep[0]['cpe']):.2f} in {rep[0]['year']} to "
            f"${num(rep[-1]['cpe']):.2f} in {rep[-1]['year']}, with a pandemic spike of "
            f"${max(num(r['cpe']) for r in rep):.2f} in 2020. The 2021 bond statement's consultant forecast "
            f"runs from ${num(f21[0]['cpe']):.2f} in {f21[0]['year']} to ${num(f21[-1]['cpe']):.2f} in "
            f"{f21[-1]['year']}; the 2025 statement's forecast from ${num(f25[0]['cpe']):.2f} in {f25[0]['year']} "
            f"to ${num(f25[-1]['cpe']):.2f} in {f25[-1]['year']}. Public predictions and budget figures are "
            f"marked at the year they were made for: " +
            "; ".join(f"{esc(r['label'])}" for r in preds) +
            f". The billed charge, total rate base fees over boardings in the audited report, the record's own "
            f"division, is ${num(billed[0]['cpe_billed']):.2f} in {billed[0]['year']} and "
            f"${num(billed[-1]['cpe_billed']):.2f} in {billed[-1]['year']}. A dashed line marks Dec. 31, 2028, "
            f"when the airline agreement and the gaming commitment end.")
    return (f'<svg viewBox="0 0 {f.w:.0f} {f.h:.0f}" role="img" aria-label="{esc(aria)}">'
            + "".join(parts) + "</svg>")


def legend():
    items = [(SERIES["Reported actual"][0], "var(--ink)", "line"),
             (SERIES["2021 OS (base case)"][0], "var(--blue)", "dash"),
             (SERIES["2025 OS (base case)"][0], "var(--orange)", "dash"),
             ("Public predictions and budget figures, at the year they were made for. Open marks: "
              "reported in the Post-Gazette, not a document the record holds", "var(--red)", "dot"),
             ("Billed charge, audited report Table III over Table IV boardings, the record's own division",
              "var(--ink)", "square")]
    out = []
    for text, colour, kind in items:
        if kind == "line":
            sw = f'<svg width="26" height="10" viewBox="0 0 26 10"><line x1="0" y1="5" x2="26" y2="5" stroke="{colour}" stroke-width="2.2"/></svg>'
        elif kind == "dash":
            sw = f'<svg width="26" height="10" viewBox="0 0 26 10"><line x1="0" y1="5" x2="26" y2="5" stroke="{colour}" stroke-width="1.8" stroke-dasharray="6 4"/></svg>'
        elif kind == "dot":
            sw = f'<svg width="26" height="12" viewBox="0 0 26 12"><circle cx="7" cy="6" r="4.5" fill="{colour}" stroke="{colour}" stroke-width="2"/><circle cx="19" cy="6" r="4.5" fill="var(--plane)" stroke="{colour}" stroke-width="2"/></svg>'
        else:
            sw = f'<svg width="26" height="10" viewBox="0 0 26 10"><rect x="8" y="0.5" width="9" height="9" fill="{colour}"/></svg>'
        out.append(f'<span>{sw}{esc(text)}</span>')
    return '<div class="legend">' + "".join(out) + "</div>"


def data_table(series, preds, billed, docs):
    def doc(src):
        d = docs.get(src)
        if d:
            return f'<a href="../documents/index.html#{esc(src)}">{esc(d["title"])}</a>'
        return esc(src)
    h = ['<div class="scroll"><table><thead><tr><th>Series</th><th>Year</th><th class="num">$</th>'
         '<th>Document</th><th>Page</th><th>Basis</th></tr></thead><tbody>']
    for name, (label, _, _, _) in SERIES.items():
        for r in series:
            if r["series"] != name:
                continue
            src_id = {"Reported actual": "os-2025ab", "2021 OS (base case)": "os-2021ab",
                      "2025 OS (base case)": "os-2025ab"}[name]
            pg = {"Reported actual": "PDF 62 (printed 52); 2014 to 2019 statistical section",
                  "2021 OS (base case)": "PDF 185 (printed B-19)",
                  "2025 OS (base case)": "PDF 202 (printed B-16)"}[name]
            basis = ("The Authority's own table of airline costs per enplaned passenger" if name == "Reported actual"
                     else "Consultant's forecast; a different calculation from the reported series")
            h.append(f'<tr><td>{esc(label.split(" (")[0])}</td><td>{esc(r["year"])}</td>'
                     f'<td class="num">{num(r["cpe"]):.2f}</td><td>{doc(src_id)}</td><td>{esc(pg)}</td><td>{esc(basis)}</td></tr>')
    for r in preds:
        val = f'{num(r["value_lo"]):.2f}' + (f' to {num(r["value_hi"]):.2f}' if r["value_hi"] else "")
        h.append(f'<tr><td>{esc(fmt_date(r["date"]))}, {esc(r["speaker"])}: “{esc(r["quote"])}”</td>'
                 f'<td>{esc(r["year_for"])}</td><td class="num">{val}</td><td>{doc(r["source_id"])}</td>'
                 f'<td>{esc(r["source_page"] or ("Tier " + r["tier"] + ", archived clip"))}</td><td>{esc(r["basis_note"])}</td></tr>')
    for r in billed:
        h.append(f'<tr><td>Billed, {int(num(r["rate_base_fees"])):,} over {int(num(r["enplanements"])):,} boardings</td>'
                 f'<td>{esc(r["year"])}</td><td class="num">{num(r["cpe_billed"]):.2f}</td><td>{doc(r["source_id"])}</td>'
                 f'<td>{esc(r["source_page"])}</td><td>{esc(r["note"])}</td></tr>')
    h.append("</tbody></table></div>")
    return "".join(h)


EXTRA_CSS = """
.wrap{max-width:62rem}
h1{font-size:1.5rem}
.legend{display:flex;flex-wrap:wrap;gap:.4rem 1.2rem;margin:.6rem 0 0;font-family:system-ui,sans-serif;font-size:.8rem;color:var(--ink2)}
.legend span{display:inline-flex;align-items:center;gap:.45rem}
.legend svg{flex:none;width:26px;height:12px;margin:0}
.lab2{font-size:11px}
figure{margin:1rem 0 0}
figcaption{font-family:system-ui,sans-serif;font-size:.78rem;color:var(--muted);margin:.5rem 0 0}
details{margin:.8rem 0 0;font-family:system-ui,sans-serif;font-size:.85rem}
summary{cursor:pointer;color:var(--blue)}
table td{vertical-align:top}
@media print{details{display:block}details summary{display:none}}
"""


def build():
    series = rows("cpe-series.csv")
    preds = rows("cpe-predictions.csv")
    billed = rows("cpe-billed.csv")
    docs = {r["id"]: r for r in rows("documents.csv")}
    body = [f"<h1>{esc(TITLE)}</h1>",
            "<figure>", chart(series, preds, billed), legend(),
            "<figcaption>Dollars per enplaned passenger. Series from <code>02-data/cpe-series.csv</code>, "
            "predictions from <code>02-data/cpe-predictions.csv</code>, billed charge from "
            "<code>02-data/cpe-billed.csv</code>. Drawn by <code>03-harness/build_explore.py</code>.</figcaption>",
            "<details><summary>Every plotted value, with document and page</summary>",
            data_table(series, preds, billed, docs), "</details></figure>",
            f'<p class="src">Lena Rose Williams · Newsworks Lab · built {BUILT} · CC BY 4.0 for the page, '
            'documents as published by their issuers. Rebuild: <code>python 03-harness/build_explore.py</code>; '
            'verify: <code>python 03-harness/build_explore.py --check</code>.</p>']
    return page(TITLE, "".join(body), extra_css=EXTRA_CSS)


def main():
    html = build()
    if "--check" in sys.argv:
        if not os.path.exists(OUT):
            print("explore/index.html missing"); sys.exit(1)
        if io.open(OUT, encoding="utf-8", newline="").read() != html:
            print("explore/index.html has drifted from its data"); sys.exit(1)
        print("explore/index.html reproduces"); return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write(html)
    print(f"wrote {os.path.relpath(OUT, ROOT)} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
