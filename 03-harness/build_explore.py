#!/usr/bin/env python3
"""build_explore.py — one chart: what airlines were told the charge would be, and what it is.

Every plotted value comes from a CSV under 02-data/; the SVG is written at build time;
--check re-renders in memory and byte-diffs against explore/index.html.

    python 03-harness/build_explore.py
    python 03-harness/build_explore.py --check

Inputs:
    02-data/cpe-series.csv        the Authority's reported series and the consultant forecasts
    02-data/cpe-billed.csv        the billed charge, Table III over boardings, 2024 and 2025
    02-data/cpe-predictions.csv   dated public predictions; plot=1 rows are drawn
    02-data/cpe-chart-bands.csv   the three eras named on the chart
    02-data/documents.csv         titles for the data table
"""
import io, os, sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_explainer import page, rows, num  # noqa: E402
from charts import esc, Frame, Scale  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "explore", "index.html")
BUILT = "2026-10-20"

HEAD = ("Pittsburgh's airlines were told the new terminal would cost them about $10 a passenger. "
        "The 2025 charge was $17.01, and the airport's own forecast reaches $20.53.")
DEK = ("Cost per enplaned passenger: what the Allegheny County Airport Authority charges airlines, "
       "in dollars, for each passenger they board at Pittsburgh International.")


def fmt_date(iso):
    d = datetime.fromisoformat(iso)
    s = d.strftime("%b. %d, %Y").replace(" 0", " ")
    for a, b in (("May.", "May"), ("Jun.", "June"), ("Jul.", "July"), ("Sep.", "Sept.")):
        s = s.replace(a, b)
    return s


def text(x, y, s, cls="anno", anchor="start", extra=""):
    return f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}"{extra}>{esc(s)}</text>'


def chart(series, billed, preds, bands):
    f = Frame(w=1000, h=600, l=52, r=30, t=34, b=44)
    x = Scale(2011, 2033, f.x0, f.x1)
    y = Scale(0, 24, f.ybot, f.ytop)
    p = []

    # eras, drawn first
    for b in bands:
        x0, x1 = x(num(b["start"])), x(min(num(b["end"]), 2033))
        last = num(b["end"]) >= 2033
        p.append(f'<rect x="{x0:.1f}" y="{f.ytop}" width="{x1 - x0:.1f}" height="{f.ybot - f.ytop:.1f}" '
                 f'fill="{"url(#hatch)" if last else "var(--ink)"}" opacity="{0.6 if last else 0.045}"/>')
        lines = b["label"].split("|")
        if last:
            p.append(f'<line x1="{x0:.1f}" y1="{f.ytop}" x2="{x0:.1f}" y2="{f.ybot:.1f}" stroke="var(--ink2)" stroke-width="1" stroke-dasharray="4 3"/>')
            for i, ln in enumerate(lines):
                p.append(text(x0 + 7, f.ybot - 12 - 15 * (len(lines) - 1 - i), ln, "era"))
        else:
            for i, ln in enumerate(lines):
                p.append(text(x0 + 7, f.ytop + 15 + 15 * i, ln, "era"))

    # grid and axes
    for t in (5, 10, 15, 20):
        p.append(f'<line x1="{f.x0}" y1="{y(t):.1f}" x2="{f.x1}" y2="{y(t):.1f}" stroke="var(--grid)"/>')
        p.append(text(f.x0 - 8, y(t) + 4, f"${t}", "ax", "end"))
    p.append(f'<line x1="{f.x0}" y1="{f.ybot:.1f}" x2="{f.x1}" y2="{f.ybot:.1f}" stroke="var(--axis)"/>')
    for yr in range(2011, 2031):
        X = x(yr + 0.5)
        if yr % 2 == 1:
            p.append(text(X, f.ybot + 20, str(yr), "ax", "middle"))

    # forecast: the 2025 bond statement's consultant, dashed
    fc = [r for r in series if r["series"] == "2025 OS (base case)"]
    pts = [(x(int(r["year"]) + 0.5), y(num(r["cpe"]))) for r in fc]
    d = " ".join(("M" if i == 0 else "L") + f"{px:.1f},{py:.1f}" for i, (px, py) in enumerate(pts))
    p.append(f'<path d="{d}" fill="none" stroke="var(--ink2)" stroke-width="2.4" stroke-dasharray="7 5"/>')
    ex, ey = pts[-1]
    p.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="var(--ink2)"/>')
    p.append(text(ex, ey - 28, f"${num(fc[-1]['cpe']):.2f} by {fc[-1]['year']}", "big", "end"))
    p.append(text(ex, ey - 12, "Consultant forecast, 2025 bond statement", "sub", "end"))

    # the reported series, solid
    rep = [r for r in series if r["series"] == "Reported actual"]
    rpts = [(x(int(r["year"]) + 0.5), y(num(r["cpe"]))) for r in rep]
    d = " ".join(("M" if i == 0 else "L") + f"{px:.1f},{py:.1f}" for i, (px, py) in enumerate(rpts))
    p.append(f'<path d="{d}" fill="none" stroke="var(--ink)" stroke-width="3" stroke-linejoin="round"/>')
    for px, py in rpts:
        p.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.2" fill="var(--ink)"/>')
    peak = max(rep, key=lambda r: num(r["cpe"]))
    p.append(text(x(int(peak["year"]) + 0.5) + 8, y(num(peak["cpe"])) + 1, f"{peak['year']}: boardings collapsed, ${num(peak['cpe']):.2f}", "sub"))
    p.append(text(rpts[0][0] - 6, rpts[0][1] - 10, "Reported by the Authority", "sub", "start"))

    # the billed charge, 2025, joined by a dotted connector because it is another basis
    b25 = [r for r in billed if r["year"] == "2025"][0]
    bx, by = x(2025.5), y(num(b25["cpe_billed"]))
    p.append(f'<line x1="{rpts[-1][0]:.1f}" y1="{rpts[-1][1]:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="var(--ink)" stroke-width="2" stroke-dasharray="2 4"/>')
    p.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="7" fill="var(--ink)" stroke="var(--plane)" stroke-width="2"/>')
    p.append(text(bx - 12, by - 4, f"${num(b25['cpe_billed']):.2f} billed in 2025", "big", "end"))
    p.append(text(bx - 12, by + 12, "audited report, our division", "sub", "end"))

    # the 2021 bond statement's own opening-year figure
    f21 = [r for r in series if r["series"] == "2021 OS (base case)" and r["year"] == "2025"][0]
    qx, qy = x(2025.5), y(num(f21["cpe"]))
    p.append(f'<circle cx="{qx:.1f}" cy="{qy:.1f}" r="5.5" fill="var(--plane)" stroke="var(--ink2)" stroke-width="2.2"/>')
    p.append(text(qx + 12, qy - 3, f"${num(f21['cpe']):.2f}: what the 2021 bond statement", "anno2"))
    p.append(text(qx + 12, qy + 12, "projected for 2025", "anno2"))

    # the predictions, in the accent
    for r in preds:
        if r["plot"] != "1":
            continue
        px = x(int(r["year_for"]) + 0.5)
        lo = num(r["value_lo"])
        hi = num(r["value_hi"]) if r["value_hi"] else None
        if hi is not None:
            y0, y1 = y(hi), y(lo)
            p.append(f'<rect x="{px - 6:.1f}" y="{y0:.1f}" width="12" height="{y1 - y0:.1f}" fill="var(--red)" opacity=".9" rx="2"/>')
            py = (y0 + y1) / 2
        else:
            py = y(lo)
            p.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="6.5" fill="var(--plane)" stroke="var(--red)" stroke-width="2.6"/>')
        lx, ly = x(num(r["label_x"])), y(num(r["label_y"]))
        anchor = r["anchor"]
        # leader to the label block's nearest edge
        tx = lx if anchor == "start" else lx
        p.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{tx - 6 if anchor == "start" else tx + 6:.1f}" y2="{ly - 6:.1f}" '
                 'stroke="var(--red)" stroke-width="1" opacity=".55"/>')
        p.append(text(lx, ly, r["line1"], "pred1", anchor))
        p.append(text(lx, ly + 17, r["line2"], "pred2", anchor))

    aria = (f"Cost per enplaned passenger at Pittsburgh International, 2011 to 2030. The Authority's "
            f"reported charge runs from ${num(rep[0]['cpe']):.2f} in {rep[0]['year']} to ${num(rep[-1]['cpe']):.2f} "
            f"in {rep[-1]['year']}, with a spike to ${num(peak['cpe']):.2f} in {peak['year']}. The billed charge in "
            f"2025, from the audited report, is ${num(b25['cpe_billed']):.2f}. The 2025 bond statement's consultant "
            f"forecasts ${num(fc[0]['cpe']):.2f} in {fc[0]['year']} rising to ${num(fc[-1]['cpe']):.2f} in {fc[-1]['year']}. "
            f"The 2021 bond statement projected ${num(f21['cpe']):.2f} for 2025. Public predictions: " +
            "; ".join(f"{r['line1']} {r['line2']}" for r in preds if r["plot"] == "1") +
            ". Eras shaded: " + "; ".join(b["label"] for b in bands) + ".")
    defs = ('<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            '<line x1="0" y1="0" x2="0" y2="6" stroke="var(--ink)" stroke-width="1" opacity=".22"/></pattern></defs>')
    return (f'<svg viewBox="0 0 {f.w:.0f} {f.h:.0f}" role="img" aria-label="{esc(aria)}">{defs}'
            + "".join(p) + "</svg>")


def table(series, billed, preds, bands, docs):
    def doc(src):
        d = docs.get(src)
        return f'<a href="../documents/index.html#{esc(src)}">{esc(d["title"])}</a>' if d else esc(src)
    h = ['<div class="scroll"><table><thead><tr><th>What</th><th>Year</th><th class="num">$</th><th>Document</th><th>Page</th><th>Note</th></tr></thead><tbody>']
    for r in series:
        if r["series"] == "Reported actual":
            h.append(f'<tr><td>Reported by the Authority</td><td>{esc(r["year"])}</td><td class="num">{num(r["cpe"]):.2f}</td>'
                     f'<td>{doc("os-2025ab")}</td><td>PDF 62 (printed 52); 2014 to 2019 from the statistical section</td>'
                     f'<td>The Authority\'s own table of airline costs per enplaned passenger</td></tr>')
    for r in billed:
        h.append(f'<tr><td>Billed: {int(num(r["rate_base_fees"])):,} in rate base fees over {int(num(r["enplanements"])):,} boardings</td>'
                 f'<td>{esc(r["year"])}</td><td class="num">{num(r["cpe_billed"]):.2f}</td><td>{doc(r["source_id"])}</td>'
                 f'<td>{esc(r["source_page"])}</td><td>{esc(r["note"])}</td></tr>')
    for name, label, pg in (("2021 OS (base case)", "Consultant forecast, 2021 bond statement, base case", "PDF 185 (printed B-19)"),
                            ("2025 OS (base case)", "Consultant forecast, 2025 bond statement", "PDF 202 (printed B-16)")):
        for r in series:
            if r["series"] == name:
                h.append(f'<tr><td>{esc(label)}</td><td>{esc(r["year"])}</td><td class="num">{num(r["cpe"]):.2f}</td>'
                         f'<td>{doc("os-2021ab" if "2021" in name else "os-2025ab")}</td><td>{esc(pg)}</td>'
                         f'<td>A consultant\'s projection, a different calculation from the reported series; never subtracted across it</td></tr>')
    for r in preds:
        val = f'{num(r["value_lo"]):.2f}' + (f' to {num(r["value_hi"]):.2f}' if r["value_hi"] else "")
        drawn = "drawn" if r["plot"] == "1" else "in the record, not drawn"
        h.append(f'<tr><td>{esc(fmt_date(r["date"]))}, {esc(r["speaker"])}: “{esc(r["quote"])}” ({drawn})</td>'
                 f'<td>{esc(r["year_for"])}</td><td class="num">{val}</td><td>{doc(r["source_id"])}</td>'
                 f'<td>{esc(r["source_page"] or ("Tier " + r["tier"] + ", archived clip"))}</td><td>{esc(r["basis_note"])}</td></tr>')
    for b in bands:
        h.append(f'<tr><td>Era: {esc(b["label"])}</td><td>{esc(b["start"])} to {esc(b["end"])}</td><td class="num"></td>'
                 f'<td>{doc(b["source_id"])}</td><td>{esc(b["source_page"])}</td><td>{esc(b["note"])}</td></tr>')
    h.append("</tbody></table></div>")
    return "".join(h)


EXTRA_CSS = """
.wrap{max-width:66rem;padding-top:2rem}
h1{font-size:1.75rem;line-height:1.25;max-width:52rem;margin:0 0 .6rem}
.dek{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;font-size:.95rem;color:var(--ink2);max-width:46rem;margin:0 0 1.2rem}
.chart{overflow-x:auto}
.chart svg{min-width:760px;margin:0}
svg text{font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
.ax{font-size:12.5px;fill:var(--muted);font-variant-numeric:tabular-nums}
.era{font-size:12.5px;fill:var(--ink2);font-weight:600}
.sub{font-size:12.5px;fill:var(--ink2)}
.anno2{font-size:13px;fill:var(--ink2)}
.big{font-size:17px;font-weight:700;fill:var(--ink);font-variant-numeric:tabular-nums}
.pred1{font-size:13px;fill:var(--red);font-weight:700}
.pred2{font-size:13.5px;fill:var(--red)}
.key{font-family:system-ui,sans-serif;font-size:.8rem;color:var(--ink2);margin:.4rem 0 0;display:flex;flex-wrap:wrap;gap:.3rem 1.3rem}
.key span{display:inline-flex;align-items:center;gap:.45rem}
.key svg{width:28px;height:12px;margin:0}
figcaption{font-family:system-ui,sans-serif;font-size:.78rem;color:var(--muted);margin:.6rem 0 0}
details{margin:.9rem 0 0;font-family:system-ui,sans-serif;font-size:.85rem}
summary{cursor:pointer;color:var(--blue)}
table td{vertical-align:top}
@media print{details{display:block}details summary{display:none}}
"""


def key():
    sw = {
        "line": '<svg viewBox="0 0 28 12"><line x1="0" y1="6" x2="28" y2="6" stroke="var(--ink)" stroke-width="3"/></svg>',
        "dash": '<svg viewBox="0 0 28 12"><line x1="0" y1="6" x2="28" y2="6" stroke="var(--ink2)" stroke-width="2.4" stroke-dasharray="7 5"/></svg>',
        "pred": '<svg viewBox="0 0 28 12"><circle cx="14" cy="6" r="5" fill="var(--plane)" stroke="var(--red)" stroke-width="2.4"/></svg>',
        "open": '<svg viewBox="0 0 28 12"><circle cx="14" cy="6" r="4.5" fill="var(--plane)" stroke="var(--ink2)" stroke-width="2"/></svg>',
    }
    items = [("line", "Reported by the Authority, its own table in the 2025 bond statement"),
             ("dash", "Its consultant's forecast, filed with the 2025 bonds"),
             ("pred", "What officials said, at the year they said it for; as reported by the Post-Gazette"),
             ("open", "What the 2021 bond statement projected for the opening year")]
    return '<div class="key">' + "".join(f"<span>{sw[k]}{esc(t)}</span>" for k, t in items) + "</div>"


def build():
    series = rows("cpe-series.csv")
    billed = rows("cpe-billed.csv")
    preds = rows("cpe-predictions.csv")
    bands = rows("cpe-chart-bands.csv")
    docs = {r["id"]: r for r in rows("documents.csv")}
    body = [f"<h1>{esc(HEAD)}</h1>", f'<p class="dek">{esc(DEK)}</p>',
            '<figure><div class="chart">', chart(series, billed, preds, bands), "</div>", key(),
            "<figcaption>Dollars per enplaned passenger. The reported series and the forecast are the Authority's and its "
            "consultant's figures; $17.01 is the audited report's rate base fees over its boardings, divided here. "
            "From <code>02-data/cpe-series.csv</code>, <code>cpe-billed.csv</code>, <code>cpe-predictions.csv</code>, "
            "<code>cpe-chart-bands.csv</code>; drawn by <code>03-harness/build_explore.py</code>.</figcaption>",
            "<details><summary>Every value on the chart, with its document and page</summary>",
            table(series, billed, preds, bands, docs), "</details></figure>",
            f'<p class="src">Lena Rose Williams · Newsworks Lab · built {BUILT} · CC BY 4.0 for the page, '
            'documents as published by their issuers. Rebuild: <code>python 03-harness/build_explore.py</code>; '
            'verify: <code>python 03-harness/build_explore.py --check</code>.</p>']
    return page("What airlines were told the terminal would cost them, and what it costs", "".join(body), extra_css=EXTRA_CSS)


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
