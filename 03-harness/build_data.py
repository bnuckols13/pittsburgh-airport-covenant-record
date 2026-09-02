#!/usr/bin/env python3
"""build_data.py — an index for 02-data/.

The front door linked to the directory, and GitHub Pages does not serve directory
listings, so that link 404'd. A listing would have been the minimum fix. What a
reader actually needs is what each table holds and which finding it carries, so
this generates that instead, and every row is read from the file it describes:
the row count and the columns are counted, not typed.

    python 03-harness/build_data.py
    python 03-harness/build_data.py --check
"""
import csv, glob, io, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_explainer import page
from charts import esc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "02-data")
BUILT = "2026-09-01"

# What each table is for. A file with no entry still lists, marked unannotated, so
# adding a CSV cannot silently produce a row that says nothing.
WHAT = {
    "coverage-three-layers.csv": ("The covenant decomposed", "F1",
        "The consultant's six forecast years separated into operating revenue, designated "
        "revenue and the Coverage Account. Carries the ratio at each layer and the reserve as a "
        "share of debt service."),
    "coverage-table.csv": ("The coverage forecasts", "F1",
        "Both vintages of the consultant's coverage table, 2021 and 2025, kept as separate "
        "series and never summed."),
    "coverage-decomposition.csv": ("Printed against recomputed", "F1",
        "Each printed coverage ratio beside the ratio recomputed from the document's own rows. "
        "This is the check that the table is being read correctly."),
    "other-pledged-revenue.csv": ("What was designated, by year", "F1",
        "Other Pledged Revenues 2019 through 2030, with the 2023 conflict carried as two rows "
        "and neither chosen."),
    "other-pledged-revenue-itemized.csv": ("What the designation was made of", "F1",
        "Exhibit E by component: federal pandemic aid, gas royalty, slot-machine tax. Shows gas "
        "at zero in every year from 2020."),
    "flow-of-funds.csv": ("The indenture's order of payment", "F1",
        "Each fund in priority order, whether the deposit is mandatory or discretionary, and any "
        "cap on it."),
    "flow-of-funds-edges.csv": ("Where the money moves", "F1",
        "The edges between funds, used to draw the flow diagram."),
    "who-pays-opr.csv": ("What withdrawal would cost", "F1",
        "The charge per boarded passenger as forecast, against the charge if the designation "
        "were withdrawn."),
    "term-structure.csv": ("What ends when", "F2",
        "The airline agreements, the designation commitment, the capital deposit waiver and the "
        "bonds, with the year each begins and ends."),
    "rail.csv": ("The dated rail", "F2",
        "Six dates the financing turns on, from board approval to bond maturity."),
    "cpe-audited-acfr.csv": ("The audited charge", "F3",
        "Ten years of cost per enplaned passenger from the audited annual reports, with rate "
        "base costs, enplanements and the debt service component shown separately."),
    "debt-service-arrives.csv": ("When the debt service starts", "F3",
        "Debt service inside the airline rate base through 2024, and the forecast aggregate "
        "after it. Two different measures, drawn adjacent and never joined."),
    "cpe-record.csv": ("Every published charge", "F3",
        "Each figure published as cost per enplaned passenger, with its series, its basis and "
        "its source, so that no two are subtracted across bases."),
    "cpe-series.csv": ("The charge by series", "F3",
        "The same figures grouped by which of the four measures they belong to."),
    "cpe-2026-claims.csv": ("The two 2026 figures", "F3",
        "$19.13 filed with investors against $17.64 given to a newspaper, both the Authority's."),
    "cpe-forecast-accuracy.csv": ("Forecast against actual, cost", "F2",
        "What each vintage forecast for the charge, against what the charge turned out to be."),
    "enplanement-forecast-accuracy.csv": ("Forecast against actual, passengers", "F2",
        "What each vintage forecast for boardings, against the actual. Passengers beat the base "
        "case; the cost forecast is the one that missed."),
    "peer-cpe.csv": ("Peer airports", "F3",
        "Comparable airports' charges. Held rather than published: most rows carry no dollar "
        "value in this case."),
    "peer-cpe-benchmark.csv": ("The peer benchmark", "F3",
        "The sixteen-airport comparison, held for the same reason."),
    "airline-mix.csv": ("Carrier share", "F4",
        "Share of traffic by airline, by year."),
    "plan-of-finance.csv": ("How the terminal was paid for", "S1",
        "The plan of finance by source: bonds, federal and state grants, and the rest."),
    "budget-revisions.csv": ("What the budget became", "S1",
        "Each published cost figure for the program and the revision that followed it."),
    "documents.csv": ("The source registry", "all",
        "Every record the reporting stands on: grade, what it establishes, the pages cited, the "
        "checksum and where to download it. This table drives the records library."),
    "source-grades.csv": ("How sources are graded", "all",
        "The reliability grade for each source and whether it is in the vault."),
    "claims.csv": ("The claims", "all",
        "Each statement the reporting makes, its status, and the document behind it."),
    "statements.csv": ("What people said, and when", "all",
        "Statements from published reporting, with speaker, date and archive link. Graded C: a "
        "source of utterances, never of figures."),
    "conflicts.csv": ("Where the filings disagree", "all",
        "Ten places the Authority's own documents contradict each other, with both figures and "
        "neither chosen."),
    "held-claims.csv": ("What is not published", "all",
        "Claims held, withdrawn, attributed or never written, each with the reason."),
    "factcheck-v16-disposition.csv": ("An earlier fact check", "all",
        "The disposition of each claim in the Aug. 30 draft. Kept for the trail; the draft it "
        "checked has been superseded."),
}


def describe(path):
    with io.open(path, encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f)
        try:
            cols = next(r)
        except StopIteration:
            return [], 0
        return cols, sum(1 for _ in r)


def build():
    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(DATA, "*.csv")))
    groups = [("F1", "The covenant, and what secures it"),
              ("F2", "The forecasts, and what ends when"),
              ("F3", "What it costs to fly here"),
              ("F4", "Passengers"),
              ("S1", "How the terminal was decided"),
              ("all", "The apparatus")]

    total_rows = 0
    rowsets = {}
    for fn in files:
        cols, n = describe(os.path.join(DATA, fn))
        total_rows += n
        key = WHAT.get(fn, (None, "all", None))[1]
        rowsets.setdefault(key, []).append((fn, cols, n))

    b = ['<p class="back"><a href="../index.html">&larr; the record</a></p>',
         '<p class="kicker">The data</p>',
         "<h1>Every table behind the findings</h1>",
         f'<p class="sub">{len(files)} files, {total_rows:,} rows. Every figure published on this '
         f'site is computed from one of these at build time, and each table names the document, '
         f'the page and the checksum its numbers came from. Download any of them.</p>']

    for key, label in groups:
        rs = rowsets.get(key)
        if not rs:
            continue
        b.append(f'<h2 class="grp">{esc(label)}</h2>')
        b.append('<div class="scroll"><table><thead><tr><th>Table</th><th>What it holds</th>'
                 '<th class="n">Rows</th></tr></thead><tbody>')
        for fn, cols, n in rs:
            title, _, desc = WHAT.get(fn, (fn, "all", "Not yet annotated."))
            b.append(f'<tr><td><a href="{esc(fn)}"><b>{esc(title)}</b></a>'
                     f'<span class="fn">{esc(fn)}</span>'
                     f'<span class="cols">{esc(", ".join(cols[:7]))}'
                     f'{"&#8230;" if len(cols) > 7 else ""}</span></td>'
                     f'<td>{esc(desc)}</td><td class="n">{n}</td></tr>')
        b.append("</tbody></table></div>")

    b.append('<div class="note"><b>How to check any of it.</b> Every table names its source in a '
             '<code>source_id</code> and a page. Run <code>python 03-harness/fetch_sources.py</code> '
             'to rebuild the document vault from the public record; any file whose checksum does '
             'not match is rejected rather than kept. Then '
             '<code>python 03-harness/check.py</code> re-renders every page from these tables and '
             'fails if one has drifted.</div>')
    b.append(f'<p class="count">Built {BUILT}. Row counts and column names are read from the '
             f'files themselves.</p>')

    return page("Every table behind the findings", "".join(b), "", CSS)


CSS = """
.back{font-family:system-ui,sans-serif;font-size:.82rem;margin:0 0 1.4rem}
h2.grp{font-family:system-ui,sans-serif;font-size:1.02rem;margin:2.3rem 0 .5rem;
padding-top:1.1rem;border-top:2px solid var(--ink)}
table{width:100%;border-collapse:collapse;font-family:system-ui,sans-serif;font-size:.86rem;
margin:.6rem 0}
th{text-align:left;border-bottom:1px solid var(--ink2);padding:.45rem .55rem;font-size:.72rem;
letter-spacing:.06em;text-transform:uppercase;color:var(--muted);font-weight:600}
td{border-bottom:1px solid var(--ring);padding:.6rem .55rem;vertical-align:top;line-height:1.5}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
td a{text-decoration:none}
td a:hover{text-decoration:underline}
.fn{display:block;font-family:"Cascadia Code",Consolas,monospace;font-size:.72rem;
color:var(--muted);margin-top:.15rem}
.cols{display:block;font-size:.71rem;color:var(--muted);margin-top:.25rem;line-height:1.4}
.note{background:var(--surface2);border-left:3px solid var(--blue);border-radius:0 9px 9px 0;
padding:.85rem 1.05rem;margin:1.6rem 0;font-family:system-ui,sans-serif;font-size:.87rem;
line-height:1.56}
.note b{display:block;margin-bottom:.2rem}
.count{font-family:system-ui,sans-serif;font-size:.8rem;color:var(--muted)}
.scroll{overflow-x:auto}
@media(min-width:60rem){.wrap{max-width:62rem}}
"""


def main():
    html = build()
    path = os.path.join(DATA, "index.html")
    if "--check" in sys.argv:
        if not os.path.exists(path) or io.open(path, encoding="utf-8").read() != html:
            print("data --check DRIFT or missing")
            return 1
        print("data --check OK")
        return 0
    io.open(path, "w", encoding="utf-8", newline="\n").write(html)
    print(f"wrote 02-data/index.html  {len(html):,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
