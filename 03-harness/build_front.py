#!/usr/bin/env python3
"""build_front.py — the front door.

Organised around the findings rather than around the site's file structure,
because a reader arriving cold needs the findings before the navigation.

Every figure on the page is read from a CSV at build time. None is typed. A number
that changed in the data changes here, and --check re-renders in memory and
byte-diffs against the committed file so a stale front door fails the build.

Register is technical: declarative sentences, no intensifiers, no second person,
no figure without its basis and its document.

    python 03-harness/build_front.py
    python 03-harness/build_front.py --check
"""
import csv, io, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from charts import esc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "02-data")
BUILT = "2026-09-01"


def rows(name):
    with io.open(os.path.join(DATA, name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def num(v):
    return float(str(v).replace(",", "").replace("$", "").strip() or 0)


CSS = """
:root{--plane:#fbfaf7;--surface:#fff;--surface2:#f4f2ec;--ink:#161616;--ink2:#4a4a4a;
--muted:#6b6b6b;--rule:#ded9cd;--accent:#1c5cab;--accent-soft:#eaf1fb;--warn:#b8600b;
--flag:#a8321e;--ok:#1d6b3f;}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--plane:#0f130f;
--surface:#181a17;--surface2:#1f221e;--ink:#f4f2e9;--ink2:#c3c2b7;--muted:#9a988d;
--rule:#2b332c;--accent:#5598e7;--accent-soft:#152232;--warn:#e8973f;--flag:#ff9b86;
--ok:#7fd3a1;}}
:root[data-theme=dark]{--plane:#0f130f;--surface:#181a17;--surface2:#1f221e;--ink:#f4f2e9;
--ink2:#c3c2b7;--muted:#9a988d;--rule:#2b332c;--accent:#5598e7;--accent-soft:#152232;
--warn:#e8973f;--flag:#ff9b86;--ok:#7fd3a1;}
*{box-sizing:border-box}
body{margin:0;background:var(--plane);color:var(--ink);line-height:1.62;
font-family:Georgia,"Palatino Linotype",serif;-webkit-text-size-adjust:100%}
.sans{font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
.wrap{max-width:58rem;margin:0 auto;padding:2.6rem 1.3rem 5rem}
h1{font-size:2.1rem;line-height:1.12;margin:.2rem 0 .6rem;letter-spacing:-.015em}
.deck{color:var(--ink2);font-size:1.06rem;margin:0 0 1.5rem;max-width:44rem}
.kicker{font-family:system-ui,sans-serif;font-size:.72rem;letter-spacing:.13em;
text-transform:uppercase;color:var(--accent);margin:0 0 .35rem;font-weight:600}
.method{border:1px solid var(--rule);background:var(--surface);border-radius:12px;
padding:1.1rem 1.25rem;margin:0 0 2.6rem;font-family:system-ui,sans-serif;font-size:.9rem;
line-height:1.6;color:var(--ink2)}
.method h2{font-size:.72rem;letter-spacing:.13em;text-transform:uppercase;color:var(--muted);
margin:0 0 .5rem;font-weight:600;font-family:system-ui,sans-serif}
.method p{margin:0 0 .6rem}
.method p:last-child{margin:0}
.method b{color:var(--ink)}
.tally{display:flex;flex-wrap:wrap;gap:1.6rem;margin-top:.9rem;padding-top:.8rem;
border-top:1px solid var(--rule)}
.tally div{font-family:system-ui,sans-serif}
.tally b{display:block;font-size:1.15rem;color:var(--ink);font-variant-numeric:tabular-nums}
.tally span{font-size:.76rem;color:var(--muted)}

.finding{margin:0 0 2.8rem;border-top:2px solid var(--ink);padding-top:1.1rem}
.finding .n{font-family:system-ui,sans-serif;font-size:.72rem;letter-spacing:.13em;
text-transform:uppercase;color:var(--accent);font-weight:600;margin:0 0 .4rem}
.finding h2{font-size:1.5rem;line-height:1.22;margin:0 0 .5rem;letter-spacing:-.01em}
.finding .sub{color:var(--ink2);margin:0 0 1.2rem;font-size:1rem;max-width:46rem}
.finding p{margin:0 0 .9rem;max-width:46rem}

/* Flex, not grid. The grid left an empty cell whenever the card count did not
   divide by the column count, and because the hairlines are the container's
   background showing through a 1px gap, that empty cell rendered as a solid slab of
   rule colour. Flex items grow to fill the last row, so there is no hole to show. */
.stats{display:flex;flex-wrap:wrap;gap:1px;
background:var(--rule);border:1px solid var(--rule);border-radius:11px;overflow:hidden;
margin:1.3rem 0}
/* Child combinator, not descendant: .stats div also matched .v/.k/.src and gave
   every child the card's own padding and background. */
.stats > div{flex:1 1 13.5rem;background:var(--surface);padding:.95rem 1.05rem;
font-family:system-ui,sans-serif}
.stats .v{font-size:1.62rem;font-weight:600;letter-spacing:-.02em;line-height:1.1;
font-variant-numeric:tabular-nums;color:var(--accent)}
.stats .v.flag{color:var(--flag)}
.stats .k{font-size:.83rem;color:var(--ink);margin-top:.3rem;line-height:1.45}
.stats .src{font-size:.72rem;color:var(--muted);margin-top:.4rem;line-height:1.4}
.stats .src a,table.layers caption a,.defs a,.guard a{color:var(--accent);
text-decoration:underline;text-underline-offset:2px;text-decoration-thickness:.5px}

table.layers{width:100%;border-collapse:collapse;font-family:system-ui,sans-serif;
font-size:.85rem;margin:1.3rem 0;font-variant-numeric:tabular-nums}
table.layers th{text-align:right;padding:.45rem .55rem;border-bottom:1px solid var(--ink2);
font-size:.74rem;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);font-weight:600}
table.layers th:first-child{text-align:left}
table.layers td{text-align:right;padding:.5rem .55rem;border-bottom:1px solid var(--rule)}
table.layers td:first-child{text-align:left;color:var(--ink2)}
table.layers tr.short td{color:var(--flag);font-weight:600}
table.layers tr.printed td{border-bottom:1px solid var(--ink2)}
table.layers tr.promise td{color:var(--muted)}
table.layers caption{caption-side:bottom;text-align:left;font-family:system-ui,sans-serif;
font-size:.76rem;color:var(--muted);padding-top:.6rem;line-height:1.5}
.scroll{overflow-x:auto}
blockquote{margin:1.2rem 0;padding:1rem 1.25rem;background:var(--surface);
border-left:3px solid var(--accent);border-radius:0 9px 9px 0;font-size:1rem;
line-height:1.6;color:var(--ink)}
blockquote p{margin:0}
blockquote .loc{display:block;font-family:system-ui,sans-serif;font-size:.76rem;
color:var(--muted);margin-top:.65rem}
blockquote .loc a{color:var(--accent)}
.rail{margin:1.6rem 0 .4rem}
.rail svg{width:100%;height:auto;display:block;overflow:visible}
.rail .ry{font-family:system-ui,sans-serif;font-size:13px;font-weight:600;
font-variant-numeric:tabular-nums}
.rail .re{font-family:system-ui,sans-serif;font-size:10.5px;fill:var(--muted)}
.rail figcaption{font-family:system-ui,sans-serif;font-size:.78rem;color:var(--muted);
line-height:1.5;margin-top:.5rem}
.open{border:1px solid var(--rule);border-radius:12px;background:var(--surface);
padding:1.1rem 1.25rem;margin:1.4rem 0}
.open h3{font-family:system-ui,sans-serif;font-size:.72rem;letter-spacing:.13em;
text-transform:uppercase;color:var(--muted);margin:0 0 .7rem;font-weight:600}
.open ol{font-family:system-ui,sans-serif;font-size:.88rem;line-height:1.6;
margin:0;padding-left:1.35rem;color:var(--ink2)}
.open li{margin:.45rem 0}
.open b{color:var(--ink)}


.defs{border:1px solid var(--rule);border-radius:11px;background:var(--surface);
padding:.95rem 1.1rem;margin:1.2rem 0;font-family:system-ui,sans-serif;font-size:.86rem;
line-height:1.58;color:var(--ink2)}
.defs p{margin:0 0 .65rem;max-width:none}
.defs p:last-child{margin:0}
.defs b{color:var(--ink)}
.guard{border-left:3px solid var(--warn);background:var(--surface2);border-radius:0 9px 9px 0;
padding:.8rem 1rem;margin:1.2rem 0;font-family:system-ui,sans-serif;font-size:.83rem;
line-height:1.55;color:var(--ink2)}
.guard b{color:var(--ink)}

.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:.9rem;
margin:1.2rem 0 0}
a.card{display:block;text-decoration:none;color:inherit;background:var(--surface);
border:1px solid var(--rule);border-radius:11px;padding:1rem 1.1rem;
transition:border-color .12s,transform .12s}
a.card:hover{border-color:var(--accent);transform:translateY(-1px)}
a.card h3{font-family:system-ui,sans-serif;font-size:.98rem;margin:0 0 .25rem}
a.card p{font-family:system-ui,sans-serif;font-size:.82rem;color:var(--ink2);margin:0;
line-height:1.5}
h2.sec{font-size:1.2rem;margin:2.6rem 0 .5rem;border-top:1px solid var(--rule);
padding-top:1.3rem}
h3.srcgrp{font-family:system-ui,sans-serif;font-size:.74rem;letter-spacing:.11em;
text-transform:uppercase;color:var(--muted);margin:1.5rem 0 .4rem}
ul.srclist{list-style:none;margin:0;padding:0;font-family:system-ui,sans-serif;font-size:.86rem}
ul.srclist li{padding:.34rem 0;border-bottom:1px solid var(--rule);display:flex;
flex-wrap:wrap;gap:.5rem;align-items:baseline;line-height:1.45}
ul.srclist .sy{color:var(--muted);font-variant-numeric:tabular-nums;min-width:2.6rem}
ul.srclist a{text-decoration:none}
ul.srclist a:hover{text-decoration:underline}
ul.srclist .sid{font-family:"Cascadia Code",Consolas,monospace;font-size:.72rem;
color:var(--muted);margin-left:auto}
ul.srclist .sn{font-size:.7rem;color:var(--muted)}
pre{background:var(--surface);border:1px solid var(--rule);border-radius:9px;
padding:.85rem 1rem;overflow-x:auto;font-size:.8rem;
font-family:"Cascadia Code",Consolas,monospace;line-height:1.6}
.foot{color:var(--muted);font-size:.8rem;margin-top:2.6rem;border-top:1px solid var(--rule);
padding-top:1rem;font-family:system-ui,sans-serif;line-height:1.6}
a{color:var(--accent)}
.toggle{position:fixed;top:.8rem;right:.8rem;font-family:system-ui,sans-serif;font-size:.74rem;
padding:.3rem .7rem;border-radius:99px;border:1px solid var(--rule);background:var(--surface);
color:var(--ink);cursor:pointer;z-index:9}
@media print{.toggle{display:none}}
"""

TOGGLE = '<button class="toggle">&#9686; theme</button>'
TOGGLE_JS = ("<script>document.querySelector('.toggle').onclick=function(){"
             "var r=document.documentElement,d=r.getAttribute('data-theme')==='dark';"
             "r.setAttribute('data-theme',d?'light':'dark')};</script>")


# Populated in build() from documents.csv, so a citation can only ever point at a
# document the package actually holds. An id that is not in the registry stays plain
# text rather than becoming a link to nothing.
_CITE = None


def cite(text):
    """Turn every document id in an authored string into a link to its entry.

    One regex pass with alternation rather than repeated replacement, so an id that
    is a substring of another cannot be rewritten inside a link already inserted.
    """
    if _CITE is None:
        return text
    return _CITE.sub(
        lambda m: f'<a href="documents/index.html#{m.group(1)}">{m.group(1)}</a>', text)


def _self_test(body):
    """A citation that points at no entry is worse than no citation."""
    linked = set(re.findall(r'href="documents/index\.html#([^"]+)"', body))
    unknown = {i for i in linked if not _CITE.fullmatch(i)}
    if unknown:
        raise SystemExit(f"front: citations point at unknown documents: {sorted(unknown)}")
    return len(linked)



DOCS = {r["id"]: r for r in rows("documents.csv")}


def src(doc_id, page, label):
    """A citation that opens the document at the page the finding rests on.

    Only a direct PDF can honour #page=. Anything else falls back to the entry in
    the records library, because a link that silently lands on page one is worse
    than one that lands somewhere honest.
    """
    d = DOCS.get(doc_id, {})
    url = d.get("url", "")
    if page and url.lower().split("?")[0].endswith(".pdf"):
        return f'<a href="{esc(url)}#page={int(page)}">{esc(label)}</a>'
    return f'<a href="documents/index.html#{esc(doc_id)}">{esc(label)}</a>'


def says(text, cite):
    """The document in its own words, before any gloss."""
    return f'<blockquote><p>{text}</p><span class="loc">{cite}</span></blockquote>'


def stat(value, key, cite, flag=False):
    return (f'<div><div class="v{" flag" if flag else ""}">{esc(value)}</div>'
            f'<div class="k">{esc(key)}</div>'
            f'<div class="src">{esc(cite)}</div></div>')



def plate_rail():
    """A dated rail. Years place every mark, so nothing sits where it looks best.

    The scale is linear in time and stays that way: half the rail being empty is
    the point, because the bonds run twenty-six years past the last forecast year.
    Labels alternate above and below the line, which is what stops the four events
    between 2017 and 2030 from colliding.
    """
    ev = sorted(rows("rail.csv"), key=lambda r: int(r["year"]))
    W, H, L, R = 900, 150, 30, 30
    y0, y1 = int(ev[0]["year"]) - 3, int(ev[-1]["year"]) + 2
    X = lambda v: L + (v - y0) / (y1 - y0) * (W - L - R)
    base = 84
    out = [f'<line x1="{L}" y1="{base}" x2="{W-R}" y2="{base}" stroke="var(--rule)" '
           f'stroke-width="2"/>']
    for i, r in enumerate(ev):
        yr, x = int(r["year"]), X(int(r["year"]))
        cliff = r["weight"] == "cliff"
        col = ("var(--flag)" if cliff else
               "var(--muted)" if r["weight"] == "end" else "var(--accent)")
        up = (i % 2 == 0)
        tip = base - 30 if up else base + 30
        out.append(f'<line x1="{x:.1f}" y1="{base}" x2="{x:.1f}" y2="{tip}" stroke="{col}" '
                   f'stroke-width="{2.4 if cliff else 1.3}"'
                   f'{"" if cliff else " stroke-dasharray=\"2 2\""}/>')
        out.append(f'<circle cx="{x:.1f}" cy="{base}" r="{5 if cliff else 3.4}" fill="{col}"/>')
        anchor = "start" if i == 0 else ("end" if i == len(ev) - 1 else "middle")
        ylab = tip - 6 if up else tip + 12
        yevt = tip - 18 if up else tip + 24
        out.append(f'<text class="ry" x="{x:.1f}" y="{ylab}" text-anchor="{anchor}" '
                   f'fill="{col}">{r["year"]}</text>')
        out.append(f'<text class="re" x="{x:.1f}" y="{yevt}" text-anchor="{anchor}">'
                   f'{esc(r["event"])}</text>')
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="A dated rail. The board approves '
            f'the terminal program in 2017, the first bonds are issued in 2021, the first terminal '
            f'debt service is billed to airlines in 2025, the airline agreements and the '
            f"designation commitment both end in 2028, the consultant's forecast ends in 2030, "
            f'and the bonds mature in 2056.">{"".join(out)}</svg>')


def build():
    lay = sorted(rows("coverage-three-layers.csv"), key=lambda r: int(r["year"]))
    aud = {r["year"]: r for r in rows("cpe-audited-acfr.csv")}
    itm = rows("other-pledged-revenue-itemized.csv")
    docs = rows("documents.csv")
    con = rows("conflicts.csv")
    held = rows("held-claims.csv")
    fc = {r["year"]: r for r in rows("coverage-table.csv") if r["vintage"] == "2025"}

    years = [r["year"] for r in lay]
    global _CITE
    ids = sorted((r["id"] for r in docs), key=len, reverse=True)
    _CITE = re.compile(r"\b(" + "|".join(re.escape(i) for i in ids) + r")\b")

    n_doc = len(docs)
    n_hash = sum(1 for r in docs if r["vault"] == "yes")
    n_acfr = sum(1 for r in docs
                 if r["id"].startswith(("acfr-", "cafr-")) and r["vault"] == "yes")

    # Finding 1 figures, all read from the decomposition.
    short = [r for r in lay if num(r["ratio_operating"]) < 1.0]
    under = [r for r in lay if num(r["ratio_pledged"]) < 1.25]
    worst = min(lay, key=lambda r: num(r["ratio_operating"]))
    at_cap = sum(1 for r in lay if abs(num(r["cov_acct_pct_of_ads"]) - 25.0) < 0.05)
    desig = {r["line_item"]: r for r in itm}["TOTAL Other Pledged Revenues"]
    slot_2026 = num(desig["2026"])

    # Finding 2 figures.
    zero_years = [r["year"] for r in rows("cpe-audited-acfr.csv")
                  if r["debt_service_in_rate_base"] == "0"]
    zero_years.sort()
    cpe_first, cpe_last = fc[years[0]]["cpe"], fc[years[-1]]["cpe"]

    b = []
    b.append('<p class="kicker">Evidence package</p>')
    b.append("<h1>The PIT Terminal Financing Record</h1>")
    b.append('<p class="deck">Three findings from the Allegheny County Airport Authority\'s own '
             'bond documents and audited annual reports, on how Pittsburgh International\'s '
             '$1.7 billion landside terminal was financed and who carries the risk if the '
             'revenue assumptions behind it do not hold.</p>')

    # ---------------------------------------------------------------- method
    b.append(
        '<div class="method">'
        '<h2>How this was reported</h2>'
        '<p>The findings are built from the documents the decisions were written into: bond '
        'official statements filed with investors, eleven years of audited annual financial '
        'reports, board records, and federal filings. Each was retrieved from a public source, '
        'hashed, and cited to a numbered page. Document identifiers below link to the '
        'source entry, which carries the hash and where to download the file. No official '
        'at the Authority has been interviewed and no records request has been answered.</p>'
        '<p>Two consequences follow. Every figure below can be checked against a named page in a '
        "document a reader can download and hash independently. And where the Authority's own "
        'filings disagree with each other, the disagreement is published rather than resolved by '
        'selecting a figure.</p>'
        f'<div class="tally">'
        f'<div><b>{n_doc}</b><span>documents, each graded</span></div>'
        f'<div><b>{n_hash}</b><span>captured and hashed</span></div>'
        f'<div><b>{n_acfr}</b><span>years of audited financial reports</span></div>'
        f'<div><b>{len(con)}</b><span>contradictions found in the Authority&#8217;s own '
        f'filings</span></div>'
        '</div></div>')
    # ------------------------------------------------------------- finding 1
    b.append('<section class="finding">')
    b.append('<p class="n">Finding one</p>')
    b.append("<h2>The airport's operations do not produce the margin its bond covenant "
             "requires. Slot-machine tax revenue and a discretionary deposit make up the "
             "difference.</h2>")
    b.append('<p class="sub">The margin above the debt payment is not produced by running an '
             'airport. Eleven percent of it is a state gaming appropriation, committed only '
             'through 2028. The rest is a reserve the forecast already tops up to the ceiling '
             'the contract allows, in five of the six years.</p>')

    b.append(
        '<div class="defs">'
        '<p><b>The covenant.</b> A promise in the Master Trust Indenture that the Authority will '
        'set its rates and charges so that each year it holds at least 1.25 times its annual debt '
        'service. It is a margin requirement rather than a payment requirement: the test asks '
        'whether the airport holds a quarter more than the bonds require, not whether it pays '
        'them.</p>'
        '<p><b>The Coverage Account.</b> A fund the Authority may top up from its own revenue on '
        'or before the tenth business day of each month, at its own discretion, capped at 25 '
        'percent of that year&#8217;s debt service. The indenture permits the balance to count '
        'toward the 1.25 test. Nothing obliges the Authority to make the deposit, and it is a '
        'separate mechanism from the designated revenues, which are counted inside Net Revenues '
        'rather than beside them. Cited at os-2025ab PDF 32, with the same cap at '
        'os-2021ab PDF 37 (printed 27).</p>'
        '</div>')
    b.append('<p>The Official Statement prints one combined ratio against that requirement, and '
             'every forecast year clears it. A footnote on that table is what lets the printed '
             'figure be taken apart.</p>')
    b.append(says("Includes Other Pledged Revenues.",
                  "Footnote 1 to the Net Revenues row, "
                  + src("os-2025ab", 202, "os-2025ab PDF 202 (printed B-16)")
                  + ", the consultant&#8217;s forecast of April 8, 2025"))
    b.append('<p>Other Pledged Revenues are money the indenture puts outside the airport&#8217;s '
             'revenue altogether, and Exhibit E states the amount for every year, so the '
             'separation is subtraction rather than inference.</p>')
    b.append(says("&#8220;Other Pledged Revenues&#8221; shall mean moneys, <b>not constituting "
                  "Revenues</b>, that are designated, for any period.",
                  "The Master Trust Indenture&#8217;s own definition, "
                  + src("os-2025ab", 343, "os-2025ab PDF 343")))

    hdr = "".join(f"<th>{y}</th>" for y in years)
    def row(cls, label, key, fmt="{:.2f}"):
        cells = "".join(f"<td>{fmt.format(num(r[key]))}</td>" for r in lay)
        return f'<tr class="{cls}"><td>{esc(label)}</td>{cells}</tr>'
    b.append('<div class="scroll"><table class="layers">'
             f'<thead><tr><th>Coverage ratio</th>{hdr}</tr></thead><tbody>'
             + row("short", "Operating revenue, after expenses", "ratio_operating")
             + row("", "Plus designated slot-machine tax", "ratio_pledged")
             + row("printed", "Plus the Coverage Account (as printed)", "ratio_printed")
             + '<tr class="promise"><td>Required by the covenant</td>'
             + "".join("<td>1.25</td>" for _ in years) + "</tr>"
             + '</tbody><caption>Source: os-2025ab PDF 202 (printed B-16), the consultant\'s '
               'forecast of April 8, 2025, and Exhibit E at PDF 316. The separation is this '
               'publication\'s arithmetic; the document prints only the combined row. All six '
               'printed ratios and all six printed cost-per-enplanement figures reproduce from '
               'the table\'s own rows.</caption></table></div>')

    b.append('<div class="stats">')
    b.append(stat(f'{len(under)} of {len(lay)}',
                  'Forecast years in which pledged revenue alone falls below the 1.25 the '
                  'covenant requires, before the Coverage Account deposit is counted.',
                  'os-2025ab PDF 202 (printed B-16). Ratios of '
                  f'{min(num(r["ratio_pledged"]) for r in under):.2f} to '
                  f'{max(num(r["ratio_pledged"]) for r in under):.2f} against a requirement '
                  'of 1.25.',
                  flag=True))
    b.append(stat(f'{num(worst["ratio_operating"]):.2f}',
                  f'What the airport\'s operations cover of its {worst["year"]} debt service. '
                  f'The covenant requires 1.25.',
                  f'${num(worst["operating_net_k"])/1000:,.1f}m of net revenue against '
                  f'${num(worst["aggregate_annual_debt_service_k"])/1000:,.1f}m of debt service.',
                  flag=True))
    b.append(stat(f'{len(short)} of {len(lay)}',
                  'Forecast years in which operations alone do not cover debt service at all, '
                  'before any designated or discretionary money.',
                  'os-2025ab PDF 202 (printed B-16), less the Exhibit E designations at PDF 316.',
                  flag=True))
    b.append(stat('25.00%',
                  f'The Coverage Account deposit as a share of debt service, assumed in '
                  f'{at_cap} of {len(lay)} forecast years. That is the maximum the contract allows.',
                  'Cap at os-2025ab PDF 32; the deposit is made at the Authority\'s monthly '
                  'discretion.'))
    b.append(stat(f'${slot_2026/1000:,.2f}m',
                  'Designated into the pledge each year from 2026. From 2025 the whole of it is '
                  'slot-machine tax, a state appropriation. Gas royalty is designated at zero in '
                  'every year from 2020 through 2030.',
                  'Exhibit E, os-2025ab PDF 316, corroborated at PDF 295.'))
    b.append('</div>')

    b.append('<p>Where that designated money comes from, and for how long anyone has '
             'committed it, is the second finding.</p>')


    b.append('<div class="grid">'
             '<a class="card" href="model/index.html"><h3>Move the levers</h3>'
             '<p>A model on the Authority\'s own forecast rows. It reproduces every printed ratio '
             'and charge to the cent before any control moves.</p></a>'
             '<a class="card" href="covenant/index.html"><h3>Two pots, explained</h3>'
             '<p>What the Coverage Account holds, what Other Pledged Revenues are, and the '
             'indenture text that separates them.</p></a></div>')
    b.append("</section>")

    # ------------------------------------------------------------- finding two
    b.append('<section class="finding">')
    b.append('<p class="n">Finding two</p>')
    b.append("<h2>The forecast spends designated money for two years longer than anyone has "
             "committed it, and the Authority says it cannot assure the source.</h2>")
    b.append('<p class="sub">The airlines voted the designation for 2026 through 2028. The '
             'forecast carries the same figure into 2029 and 2030. The airline agreements expire '
             'Dec. 31, 2028. The bonds run to 2056.</p>')

    b.append('<p>What the carriers actually voted, and the years it covers, is stated in the '
             'bond document.</p>')
    b.append(says("In connection with a January 2025 Majority In Interest (&#8220;MII&#8221;) "
                  "vote, the Authority committed to using discretionary revenue, which may "
                  "include Gaming Revenues or Natural Gas Revenues, of no less than $8.8 million "
                  "for 2025 and $11.575 million per year <b>for 2026 through 2028</b> to reduce "
                  "airline rates and charges.",
                  src("os-2025ab", 67, "os-2025ab PDF 67")))
    b.append('<p>Exhibit E forecasts $11,575,000 in 2029 and again in 2030, which is the '
             'committed figure carried two years past the commitment. From 2025 the whole of the '
             'designated block is slot-machine tax, a state appropriation. The sentence directly '
             'above the commitment, in the Authority&#8217;s own risk disclosure to its '
             'investors, is this.</p>')
    b.append(says("The Authority expects to continue to receive payments of $12.4 million "
                  "annually for so long as it continues to be a recipient under the Gaming Act. "
                  "However, <b>there can be no assurance that the Gaming Act will not be amended "
                  "in the future to reduce or eliminate payments of such revenues to the "
                  "Authority.</b>",
                  src("os-2025ab", 67, "os-2025ab PDF 67") + ", the sentence above the one "
                  "quoted here"))

    b.append('<div class="rail"><figure>' + plate_rail() +
             '<figcaption>The dates the financing turns on. Two things end together on '
             'Dec. 31, 2028: the agreements that make the carriers responsible for the residual, '
             'and the designation the airlines voted. The forecast runs two years past both, and '
             'the bonds run twenty-six years past the forecast. Source: '
             + src("os-2025ab", 67, "os-2025ab PDF 67") + ' and '
             + src("os-2025ab", 202, "PDF 202 (printed B-16)") +
             '.</figcaption></figure></div>')

    b.append('<div class="stats">')
    b.append(stat("2026–28",
                  "The years the airlines actually voted the designation for.",
                  "os-2025ab PDF 67, the January 2025 majority-in-interest vote."))
    b.append(stat("2029 and 2030",
                  "The two further years the forecast fills with the same figure, which no vote "
                  "covers.",
                  "Exhibit E, os-2025ab PDF 316, corroborated at PDF 295.", flag=True))
    b.append(stat("$12.4m",
                  "Received in gaming revenue in each year from 2020 through 2024, and the sum "
                  "the Authority says it cannot assure will continue.",
                  "os-2025ab PDF 67."))
    b.append("</div>")

    b.append('<p>Gas royalty is designated at zero in every year from 2020 through 2030 and does '
             'not return in the forecast. What was designated from 2020 through 2023 was federal '
             'pandemic relief, and in 2024 nothing was designated at all.</p>')

    b.append('<div class="grid">'
             '<a class="card" href="covenant/index.html"><h3>What was designated, year by year</h3>'
             '<p>Exhibit E itemised: federal relief, then nothing, then slot-machine tax.</p></a>'
             '<a class="card" href="claims/index.html"><h3>The claims, one by one</h3>'
             '<p>Each statement with the document and page behind it.</p></a></div>')
    b.append("</section>")


    # ----------------------------------------------------------- finding three
    a24 = aud["2024"]
    b.append('<section class="finding">')
    b.append('<p class="n">Finding three</p>')
    b.append("<h2>No terminal debt entered the airline charge until 2025. The Authority's "
             "consultant forecasts that charge rising every year to 2030.</h2>")
    b.append('<p class="sub">The charge is set by a residual formula, so revenue the Authority '
             'does not designate is billed to the carriers instead. What that does to passengers '
             'is contested and is not settled here.</p>')

    b.append('<p>The Authority\'s audited annual reports carry a ten-year series of cost per '
             'enplaned passenger, computed as rate base costs divided by enplanements. The debt '
             f'service line inside that calculation reads zero for {zero_years[0]} through '
             f'{zero_years[-1]}. Interest on the 2021 bonds was capitalized through Feb. 1, 2025 '
             'and on the 2023 bonds through April 1, 2025. For four years the carriers were billed '
             'nothing toward the new terminal, and the audited charge fell to its lowest figure in '
             'the series.</p>')

    b.append('<div class="stats">')
    b.append(stat('$0',
                  f'Debt service inside the airline rate base, {zero_years[0]} through '
                  f'{zero_years[-1]}, because interest was capitalized.',
                  'Table IV of acfr-2024, the audited annual report. Capitalization disclosed at '
                  'os-2025ab PDF 39.'))
    b.append(stat(f'${num(a24["cpe_audited"]):.2f}',
                  'Audited cost per enplaned passenger in 2024, the lowest in the ten-year '
                  'audited series.',
                  'Table IV of acfr-2024. Reproduces from '
                  f'${num(a24["rate_base_costs"]):,.0f} of rate base costs over '
                  f'{num(a24["enplanements"]):,.0f} enplanements.'))
    b.append(stat(f'${num(cpe_first):.2f} to ${num(cpe_last):.2f}',
                  f'The consultant\'s forecast charge, {years[0]} to {years[-1]}, on a single '
                  'basis. The first terminal debt service is billed in 2025.',
                  'os-2025ab PDF 202 (printed B-16). Reproduces as airline payments over '
                  'enplanements in all six years.',
                  flag=True))
    b.append('</div>')

    b.append('<div class="guard"><b>Four measures share one name.</b> The Authority\'s audited '
             'annual report, its bond statement\'s management discussion, its consultant\'s '
             'forecast, and FAA Form 5100-127 each publish a figure called cost per enplaned '
             'passenger, computed on different bases. For 2024 acfr-2024 gives $7.34 where '
             'os-2025ab gives $11.56. Each figure on this site names its basis, '
             'and no figure is subtracted from a figure on another basis.</div>')

    b.append('<p>Whether a rising airline charge reaches a passenger as fare or as reduced service '
             'is disputed. The carriers\' position is that it does not. The published research '
             'measures related but distinct questions, and no study in the record tests '
             'Pittsburgh. Five claims and five studies are adjudicated in the record, and the '
             'question is open.</p>')

    b.append('<div class="grid">'
             '<a class="card" href="report/index.html"><h3>The record</h3>'
             '<p>Six modules, each with the figure that carries it and the arithmetic beneath '
             'it.</p></a>'
             '<a class="card" href="appendix-dataviz/index.html"><h3>The figures</h3>'
             '<p>Eight plates and two held cards. Every coordinate recomputes from a CSV naming '
             'its document, page and hash.</p></a></div>')
    b.append("</section>")

    # ---------------------------------------------------------------- tools
    # Open questions rather than a count of what is missing. The tally version of
    # this reads as a scoreboard against the work; the questions read as the work.
    b.append('<h2 class="sec">What this reporting has not established</h2>')
    b.append('<div class="open"><h3>Open questions</h3><ol>'
             '<li><b>Whether the designation continues past 2028.</b> A further '
             'majority-in-interest vote could extend it, and the money has arrived in every year '
             'from 2020 through 2024. Nothing in the record says either way.</li>'
             '<li><b>What happened to the $12.4 million during Pennsylvania&#8217;s 2025 budget '
             'impasse.</b> The gaming money is a state appropriation, so its history is a matter '
             'of record, and that record is not yet in this file.</li>'
             '<li><b>Whether a rising airline charge reaches a passenger.</b> The carriers say it '
             'does not. The published research measures adjacent questions and none of it tests '
             'Pittsburgh.</li>'
             '<li><b>What the Authority says about any of it.</b> Right of reply has not been '
             'sought, and no figure here reflects its answer.</li>'
             '<li><b>What the master plan&#8217;s alternatives analysis contains.</b> Federal '
             'rules require one. It has never been published, and it is what the claim that '
             'renovation would have cost more was measured against.</li>'
             '</ol></div>')

    b.append('<h2 class="sec">The evidence, and how to read it</h2>')
    b.append('<p>The two aggregation tools hold the material the findings are drawn from. Neither '
             'requires taking this publication\'s word for anything.</p>')
    b.append('<div class="grid">'
             f'<a class="card" href="claims/index.html"><h3>What the reporting says</h3>'
             f'<p>Every claim, with the document behind it and a link that opens the source at '
             f'the page cited.</p></a>'
             f'<a class="card" href="press/index.html"><h3>What the airport said</h3>'
             f'<p>Statements by people speaking for the Authority, in order, drawn from archived '
             f'copies of its Tribune-Review coverage.</p></a>'
             f'<a class="card" href="documents/index.html"><h3>Read the documents</h3>'
             f'<p>All {n_doc} records, open to read and searchable. Where a finding cites a page, '
             f'a link opens the document at that page.</p></a>'
             f'<a class="card" href="factcheck/index.html"><h3>The fact check</h3>'
             f'<p>Two machine gates over the documents, {len(con)} places the Authority\'s filings '
             f'disagree with themselves, and the claims this reporting does not make, with the '
             f'reason for each.</p></a>'
             '<a class="card" href="01-sources-archive/MANIFEST.md"><h3>Source manifest</h3>'
             '<p>Every document with its SHA-256, and a script that rebuilds the vault from the '
             'public record and rejects any file whose hash does not match.</p></a>'
             '<a class="card" href="02-data/"><h3>The data</h3>'
             '<p>The coverage decomposition, the revenue itemisation, the audited cost series and '
             'the forecast tables, as CSVs.</p></a>'
             '</div>')

    # Every source, listed and linked. A reader should not have to hunt through a
    # tool to find out what the reporting rests on.
    # Grouped by the question each record answers, matching the library. A reader
    # looking for the covenant evidence should not have to know it was published by
    # a bond underwriter.
    GROUPS = [("F1", "The covenant, and what secures it"),
              ("F3", "What it costs airlines to fly here"),
              ("F2", "The forecasts, and how they have performed"),
              ("F4", "Passengers, and whether the cost reaches them"),
              ("S1", "How the terminal was decided")]
    b.append('<!--SRCINDEX-->')
    idx = ['<h2 class="sec">Every source, listed</h2>']
    idx.append(f'<p>All {n_doc} records behind the three findings, grouped by the question each answers. '
               f'Each title opens the '
               f'document itself; the identifier opens its entry, with what it establishes, the '
               f'pages cited and a checksum for the copy that was read.</p>')
    seen_lbl = set()
    covered = set()
    for topic, label in GROUPS:
        grp = sorted((r for r in docs if r["serves"] == topic),
                     key=lambda r: (-int(r["year"] or 0), r["id"]))
        covered.update(r["id"] for r in grp)
        if not grp:
            continue
        if label and label not in seen_lbl:
            idx.append(f'<h3 class="srcgrp">{esc(label)}</h3>')
            seen_lbl.add(label)
        idx.append('<ul class="srclist">')
        for r in grp:
            direct = r["url"].lower().split("?")[0].endswith(".pdf")
            title = (f'<a href="{esc(r["url"])}" rel="noopener">{esc(r["title"])}</a>'
                     if r["url"] else esc(r["title"]))
            idx.append(f'<li><span class="sy">{esc(r["year"])}</span>{title}'
                     f'<a class="sid" href="documents/index.html#{esc(r["id"])}">'
                     f'{esc(r["id"])}</a>'
                     f'{"" if direct else " <span class=\"sn\">landing page</span>"}</li>')
        idx.append('</ul>')
    missing = [r["id"] for r in docs if r["id"] not in covered]
    if missing:
        raise SystemExit(f"front: {missing} carry a topic not listed in the source index "
                         "and would be dropped from it silently.")

    b.append('<h2 class="sec">Checking the work</h2>')
    b.append('<pre><code>python 03-harness/fetch_sources.py   # rebuild the vault, hash-checked\n'
             'python 03-harness/verify_claims.py    # hash gate and anchor gate\n'
             'python 03-harness/check.py            # all of it, in order</code></pre>')
    b.append('<p>Each generated page carries a <code>--check</code> mode that re-renders it from '
             'the data and compares it byte for byte with the committed file. A page that has '
             'drifted from its source fails the build.</p>')

    b.append(f'<p class="foot">Data CC BY 4.0, code MIT. Figures attributed to the Allegheny '
             f'County Airport Authority are its own, archived and hashed, not independently '
             f'audited here. Media reports are graded C: a source of statements and dates, not of '
             f'figures. No official has been interviewed and right of reply has not been sought. '
             f'Built {BUILT}.</p>')

    body = cite("".join(b)).replace("<!--SRCINDEX-->", "".join(idx))
    _self_test(body)

    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>The PIT Terminal Financing Record</title>'
            f'<style>{CSS}</style></head><body>{TOGGLE}'
            f'<div class="wrap">{body}</div>{TOGGLE_JS}</body></html>')


def main():
    html = build()
    path = os.path.join(ROOT, "index.html")
    if "--check" in sys.argv:
        if not os.path.exists(path):
            print("front: MISSING index.html")
            return 1
        if io.open(path, encoding="utf-8").read() != html:
            print("front: DRIFT, the committed page is not what the data renders")
            return 1
        print("front --check OK")
        return 0
    io.open(path, "w", encoding="utf-8", newline="\n").write(html)
    print(f"wrote index.html  {len(html):,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
