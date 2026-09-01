#!/usr/bin/env python3
"""build_claims.py — every claim, and the document that establishes it.

Organised by claim rather than by document, because a reader arrives asking what
the reporting asserts and what says so. Each claim links to its evidence at the
page cited.

    python 03-harness/build_claims.py
    python 03-harness/build_claims.py --check
"""
import io, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_explainer import page, rows
from build_tools import TOPICS, CSS as TOOLS_CSS, FILTER_JS, bar
from charts import esc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILT = "2026-09-01"

STATUS = {
    "established": ("Established", "A document says so, and the page is linked."),
    "computed": ("Our arithmetic", "Derived from figures in the documents. The source prints "
                 "the inputs, not this result, and it is labelled as ours wherever it appears."),
    "attributed": ("Attributed", "Somebody else's statement or figure, named as theirs."),
    "contested": ("Contested", "The record does not settle it, and this reporting does not "
                  "pretend otherwise."),
}

CSS = TOOLS_CSS + """
.claim{border-top:1px solid var(--ring);padding:1.25rem 0}
.claim .st{margin-bottom:.5rem}
.claim blockquote{margin:0 0 .6rem;padding:0;border:0;font-family:Georgia,serif;
font-size:1.06rem;line-height:1.5;color:var(--ink)}
.claim .who{font-family:system-ui,sans-serif;font-size:.74rem;letter-spacing:.05em;
text-transform:uppercase;color:var(--muted);margin:0 0 .55rem}
.claim .note{background:none;border:0;border-left:2px solid var(--ring);border-radius:0;
padding:.1rem 0 .1rem .85rem;margin:.55rem 0 .7rem;font-size:.85rem;color:var(--ink2);
line-height:1.55}
.ev{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center}
.ev .el{font-family:system-ui,sans-serif;font-size:.73rem;letter-spacing:.05em;
text-transform:uppercase;color:var(--muted);margin-right:.15rem}
a.evd{font-family:system-ui,sans-serif;font-size:.78rem;text-decoration:none;
padding:.2rem .55rem;border-radius:7px;border:1px solid var(--ring);color:var(--blue);
background:var(--surface);white-space:nowrap}
a.evd:hover{border-color:var(--blue);background:var(--blue);color:#fff}
a.evd .pp{opacity:.75;font-variant-numeric:tabular-nums}
span.evd{font-family:system-ui,sans-serif;font-size:.78rem;padding:.2rem .55rem;
border-radius:7px;border:1px dashed var(--ring);color:var(--muted)}
.s-established{color:var(--good,#1d6b3f)}
.s-computed{color:var(--blue)}
.s-contested{color:var(--yellow)}
.legend{font-family:system-ui,sans-serif;font-size:.84rem;color:var(--ink2);
border:1px solid var(--ring);border-radius:11px;padding:.9rem 1.1rem;margin:1.2rem 0 1.8rem;
line-height:1.55}
.legend div{margin:.3rem 0}
"""


def build():
    docs = {r["id"]: r for r in rows("documents.csv")}
    claims = rows("claims.csv")

    # A claim pointing at a document the package does not hold is a broken promise,
    # not a formatting problem. Fail the build rather than render a dead chip.
    missing = sorted({e.split("#")[0] for c in claims for e in c["evidence"].split(";") if e}
                     - set(docs))
    if missing:
        raise SystemExit(f"claims.csv cites documents not in documents.csv: {missing}")
    bad_status = sorted({c["status"] for c in claims} - set(STATUS))
    if bad_status:
        raise SystemExit(f"claims.csv uses unknown status values: {bad_status}")

    tlabel = {t: lbl for t, lbl, _ in TOPICS}
    body = ['<p class="back"><a href="../index.html">&larr; the record</a></p>',
            '<p class="kicker">The claims</p>',
            '<h1>What the reporting says, and what says so</h1>',
            f'<p class="sub">Every substantive claim in the reporting, with the document behind '
            f'it. Where a document is a file and the claim rests on a particular page, the link '
            f'opens it at that page.</p>']

    body.append('<div class="legend">'
                + "".join(f'<div><span class="st s-{k}">{esc(lbl)}</span> &nbsp;{esc(desc)}</div>'
                          for k, (lbl, desc) in STATUS.items())
                + '</div>')

    body.append(bar(
        "Search the claims and their evidence",
        ("topic", "Jump to a question", [(t, lbl) for t, lbl, _ in TOPICS]),
        [("status", "Basis", [(k, v[0]) for k, v in STATUS.items()])]))
    body.append('<p class="empty" id="empty" hidden>Nothing matches that.</p>')

    for topic, label, _ in TOPICS:
        group = [c for c in claims if c["topic"] == topic]
        if not group:
            continue
        body.append(f'<h2 class="grp">{esc(label)}'
                    f'<span class="gn">{len(group)} claims</span></h2>')
        for c in group:
            chips = []
            for e in [x for x in c["evidence"].split(";") if x]:
                did, _, pg = e.partition("#")
                d = docs[did]
                direct = d["url"].lower().split("?")[0].endswith(".pdf")
                lbl = d["title"].split(",")[0][:42]
                if pg and direct:
                    chips.append(f'<a class="evd" href="{esc(d["url"])}#page={pg}" '
                                 f'rel="noopener">{esc(lbl)} <span class="pp">p.&thinsp;{esc(pg)}'
                                 f'</span></a>')
                elif d["url"]:
                    chips.append(f'<a class="evd" href="{esc(d["url"])}" rel="noopener">'
                                 f'{esc(lbl)}</a>')
                else:
                    chips.append(f'<span class="evd">{esc(lbl)}</span>')
                chips.append(f'<a class="evd" href="../documents/index.html#{esc(did)}">'
                             f'about this source</a>')
            hay = " ".join([c["claim"], c["note"], c["whose"], c["evidence"],
                            STATUS[c["status"]][0]]).lower()
            body.append(
                f'<article class="claim" id="{esc(c["id"])}" data-hay="{esc(hay)}" '
                f'data-topic="{esc(topic)}" data-status="{esc(c["status"])}">'
                f'<span class="st s-{esc(c["status"])}">{esc(STATUS[c["status"]][0])}</span>'
                f'<blockquote>{esc(c["claim"])}</blockquote>'
                f'<p class="who">{esc(c["whose"])}</p>'
                + (f'<p class="note">{esc(c["note"])}</p>' if c["note"] else "")
                + f'<div class="ev"><span class="el">Read it</span>{"".join(chips)}</div>'
                f'</article>')

    body.append(f'<p class="count">Built {BUILT}. Generated from '
                f'<code>02-data/claims.csv</code> and <code>02-data/documents.csv</code>. '
                f'{len(claims)} claims.</p>')
    return page("What the reporting says, and what says so",
                "".join(body), FILTER_JS, CSS)


def main():
    html = build()
    path = os.path.join(ROOT, "claims", "index.html")
    if "--check" in sys.argv:
        if not os.path.exists(path) or io.open(path, encoding="utf-8").read() != html:
            print("claims: DRIFT or missing")
            return 1
        print("claims --check OK")
        return 0
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8", newline="\n").write(html)
    print(f"wrote claims/index.html  {len(html):,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
