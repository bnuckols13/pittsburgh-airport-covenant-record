#!/usr/bin/env python3
"""build_press.py — what the Airport Authority told the press, in order.

Every statement here is Tier C. A quotation is an utterance and a date. It is
never a figure this reporting computes with: where a number appears inside
quotation marks it stays inside them and belongs to the speaker, and the audited
or filed figure is what the findings use.

Generated from 02-data/statements.csv, which is produced by the media archive's
extract_statements.py and checks every quotation back against the archived bytes
of the clip it claims to come from.

    python 03-harness/build_press.py
    python 03-harness/build_press.py --check
"""
import io, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_explainer import page, rows
from build_tools import CSS as TOOLS_CSS, bar, FILTER_JS
from charts import esc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILT = "2026-09-01"

MONTH = ["", "January", "February", "March", "April", "May", "June", "July",
         "August", "September", "October", "November", "December"]

CSS = TOOLS_CSS + """
.stmt{border-top:1px solid var(--ring);padding:1.15rem 0;display:grid;
grid-template-columns:7.5rem 1fr;gap:1rem}
.stmt .when{font-family:system-ui,sans-serif;font-size:.8rem;color:var(--muted);
line-height:1.4;font-variant-numeric:tabular-nums}
.stmt .when b{display:block;color:var(--ink2);font-size:.86rem;font-weight:600}
.stmt blockquote{margin:0 0 .5rem;padding:0 0 0 .9rem;border-left:3px solid var(--blue);
font-family:Georgia,serif;font-size:1.04rem;line-height:1.52;color:var(--ink)}
.stmt .who{font-family:system-ui,sans-serif;font-size:.82rem;color:var(--ink);
font-weight:600;margin:0 0 .2rem}
.stmt .head{font-family:system-ui,sans-serif;font-size:.79rem;color:var(--muted);
margin:0 0 .5rem;line-height:1.45}
.stmt .acts{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center}
.stmt a.src{font-family:system-ui,sans-serif;font-size:.76rem;text-decoration:none;
padding:.16rem .5rem;border-radius:99px;border:1px solid var(--ring);color:var(--blue);
background:var(--surface)}
.stmt a.src:hover{border-color:var(--blue);background:var(--blue);color:#fff}
.stmt .undated{color:var(--yellow)}
h2.yr{font-family:system-ui,sans-serif;font-size:1.3rem;margin:2.4rem 0 .3rem;
padding-top:1.2rem;border-top:2px solid var(--ink);font-variant-numeric:tabular-nums;
display:flex;align-items:baseline;gap:.7rem}
h2.yr .gn{font-size:.72rem;font-weight:400;color:var(--muted);letter-spacing:.06em;
text-transform:uppercase;margin-left:auto}
@media(max-width:34rem){.stmt{grid-template-columns:1fr}}
"""


def when(raw):
    """A readable date, and nothing invented when there is not one."""
    if not raw:
        return None, "undated"
    m = re.search(r"((?:19|20)\d\d)-(\d\d)-(\d\d)", raw)
    if m:
        y, mo, d = m.groups()
        return y, f"{MONTH[int(mo)]} {int(d)}, {y}"
    m = re.search(r"(\d{1,2}) (\w{3}) ((?:19|20)\d\d)", raw)
    if m:
        mo = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7,
              "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}.get(m.group(2))
        if mo:
            return m.group(3), f"{MONTH[mo]} {int(m.group(1))}, {m.group(3)}"
    m = re.search(r"(19|20)\d\d", raw)
    return (m.group(0), m.group(0)) if m else (None, "undated")


def build():
    stmts = rows("statements.csv")
    speakers = sorted({s["speaker"] for s in stmts})

    dated = [s for s in stmts if when(s["published"])[0]]
    undated = [s for s in stmts if not when(s["published"])[0]]
    years = sorted({when(s["published"])[0] for s in dated})

    body = ['<p class="back"><a href="../index.html">&larr; the record</a></p>',
            '<p class="kicker">The press record</p>',
            '<h1>What the Airport Authority told the press</h1>',
            f'<p class="sub">{len(stmts)} statements by people speaking for the Authority, drawn '
            f'from its coverage in the Tribune-Review and read out of archived copies of the '
            f'articles. {len(dated)} carry a date, running from {years[0]} to {years[-1]}.</p>']

    body.append('<div class="note"><b>What these are, and what they are not</b>'
                'A quotation here is an utterance and a date. It is not a figure this reporting '
                'computes with. Where a number appears inside quotation marks it belongs to the '
                'speaker and stays in quotation marks; the audited and filed figures are what the '
                'findings rest on, and those are in the documents. Every quotation was checked '
                'back against the archived copy of the article it came from before it was '
                'published here.</div>')

    body.append(bar("Search the statements",
                    ("speaker", "Who is speaking", [(s, s.split(",")[0]) for s in speakers]),
                    [("era", "When", [("2019+", "2019 and later"),
                                      ("pre2019", "before 2019"),
                                      ("undated", "undated")])]))
    body.append('<p class="empty" id="empty" hidden>Nothing matches that.</p>')

    def card(s):
        y, label = when(s["published"])
        era = "undated" if not y else ("2019+" if int(y) >= 2019 else "pre2019")
        hay = " ".join([s["statement"], s["speaker"], s["title"], label]).lower()
        links = []
        if s.get("url"):
            links.append(f'<a class="src" href="{esc(s["url"])}" rel="noopener">'
                         f'read the article</a>')
        if s.get("wayback"):
            links.append(f'<a class="src" href="{esc(s["wayback"])}" rel="noopener">'
                         f'archived copy</a>')
        return (f'<article class="stmt" data-hay="{esc(hay)}" data-speaker="{esc(s["speaker"])}" '
                f'data-era="{era}">'
                f'<div class="when"><b>{esc(label)}</b>'
                f'{"" if y else "<span class=undated>no date on the page</span>"}</div>'
                f'<div><p class="who">{esc(s["speaker"])}</p>'
                f'<blockquote>{esc(s["statement"])}</blockquote>'
                f'<p class="head">{esc(s["title"])}</p>'
                f'<div class="acts">{"".join(links)}</div></div></article>')

    for y in years:
        group = [s for s in dated if when(s["published"])[0] == y]
        body.append(f'<h2 class="yr">{esc(y)}<span class="gn">'
                    f'{len(group)} statement{"s" if len(group) != 1 else ""}</span></h2>')
        body.extend(card(s) for s in group)

    if undated:
        body.append(f'<h2 class="yr">Undated<span class="gn">{len(undated)} statements</span></h2>')
        body.append('<p class="grpnote">The archived copy of these articles carries no publication '
                    'date in its markup. They are published without one rather than with a guess.</p>')
        body.extend(card(s) for s in undated)

    body.append(f'<p class="count">Built {BUILT}. Generated from '
                f'<code>02-data/statements.csv</code>. Speakers are included only where the '
                f'reporting itself identifies them as speaking for the Authority.</p>')
    return page("What the Airport Authority told the press", "".join(body), FILTER_JS, CSS)


def main():
    html = build()
    path = os.path.join(ROOT, "press", "index.html")
    if "--check" in sys.argv:
        if not os.path.exists(path) or io.open(path, encoding="utf-8").read() != html:
            print("press: DRIFT or missing")
            return 1
        print("press --check OK")
        return 0
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8", newline="\n").write(html)
    print(f"wrote press/index.html  {len(html):,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
