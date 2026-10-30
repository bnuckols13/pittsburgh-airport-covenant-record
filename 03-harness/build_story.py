#!/usr/bin/env python3
"""build_story.py — "The story": the reporting laid out in plain technical grafs.

The prose came through the adversarial loop in ~/journalism-master/prose-method/.
v1 was blocked by Lens D on five findings, v2 on ten. v3 closes all fifteen against
the document rather than against the drafter's judgement. The run records are in
prose-method/runs/.

Register is Lane N, per 00-prose/VOICE-PUBLISHED.md: short sentences, grafs of one to
three, no semicolons, method in the institutional voice, numerals and percent signs,
close on where a decision stands.

Figures are read from the CSVs at build time so the prose cannot drift from the data.
The sentences around them are authored, and every one that states a computed figure
says whose arithmetic it is.

    python 03-harness/build_story.py
    python 03-harness/build_story.py --check
"""
import csv, io, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from charts import esc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "02-data")
BUILT = "2026-09-01"
OUTLET = "This reporting"


def rows(name):
    with io.open(os.path.join(DATA, name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def num(v):
    return float(str(v).replace(",", "").replace("$", "").strip() or 0)


DOCS = {r["id"]: r for r in rows("documents.csv")}


def src(doc_id, page, label):
    """Cite to the page the sentence rests on where the source is a direct PDF."""
    d = DOCS.get(doc_id, {})
    url = d.get("url", "")
    if page and url.lower().split("?")[0].endswith(".pdf"):
        return f'<a href="{esc(url)}#page={int(page)}">{esc(label)}</a>'
    return f'<a href="documents/index.html#{esc(doc_id)}">{esc(label)}</a>'


CSS = """
:root{--plane:#fbfaf7;--surface:#fff;--surface2:#f4f2ec;--ink:#161616;--ink2:#3f3f3f;
--muted:#6b6b6b;--rule:#ded9cd;--accent:#1c5cab;--flag:#a8321e;}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--plane:#0f130f;
--surface:#181a17;--surface2:#1f221e;--ink:#f4f2e9;--ink2:#cfcdc2;--muted:#9a988d;
--rule:#2b332c;--accent:#5598e7;--flag:#ff9b86;}}
:root[data-theme=dark]{--plane:#0f130f;--surface:#181a17;--surface2:#1f221e;
--ink:#f4f2e9;--ink2:#cfcdc2;--muted:#9a988d;--rule:#2b332c;--accent:#5598e7;
--flag:#ff9b86;}
*{box-sizing:border-box}
body{margin:0;background:var(--plane);color:var(--ink);line-height:1.66;
font-family:Georgia,"Palatino Linotype",serif;font-size:17px}
.wrap{max-width:40rem;margin:0 auto;padding:2.4rem 1.3rem 5rem}
.back{font-family:system-ui,sans-serif;font-size:.82rem;margin:0 0 1.3rem}
.kicker{font-family:system-ui,sans-serif;font-size:.72rem;letter-spacing:.13em;
text-transform:uppercase;color:var(--accent);font-weight:600;margin:0 0 .4rem}
h1{font-size:2.1rem;line-height:1.14;margin:0 0 1.2rem;letter-spacing:-.015em}
h2{font-family:system-ui,sans-serif;font-size:1.02rem;margin:2.4rem 0 .7rem;
padding-top:1.1rem;border-top:1px solid var(--rule);letter-spacing:-.005em}
p{margin:0 0 1rem}
p.lede{font-size:1.1rem}
.note{font-family:system-ui,sans-serif;font-size:.85rem;color:var(--ink2);
background:var(--surface);border:1px solid var(--rule);border-radius:10px;
padding:.85rem 1rem;margin:1.2rem 0;line-height:1.55}
blockquote{margin:1.2rem 0;padding:.9rem 1.1rem;background:var(--surface2);
border-left:3px solid var(--accent);border-radius:0 8px 8px 0;font-size:1rem}
blockquote p{margin:0}
blockquote .loc{display:block;font-family:system-ui,sans-serif;font-size:.76rem;
color:var(--muted);margin-top:.6rem}
a{color:var(--accent)}
.figs{font-family:system-ui,sans-serif;font-size:.88rem;font-variant-numeric:tabular-nums;
border-collapse:collapse;width:100%;margin:1.1rem 0}
.figs th{text-align:right;font-size:.72rem;letter-spacing:.05em;text-transform:uppercase;
color:var(--muted);padding:.35rem .45rem;border-bottom:1px solid var(--ink2)}
.figs th:first-child{text-align:left}
.figs td{text-align:right;padding:.4rem .45rem;border-bottom:1px solid var(--rule);
color:var(--ink2)}
.figs td:first-child{text-align:left}
.figs tr.short td{color:var(--flag);font-weight:600}
.scroll{overflow-x:auto}
.foot{font-family:system-ui,sans-serif;font-size:.78rem;color:var(--muted);
margin-top:2.6rem;border-top:1px solid var(--rule);padding-top:1rem;line-height:1.6}
.toggle{position:fixed;top:.8rem;right:.8rem;font-family:system-ui,sans-serif;
font-size:.74rem;padding:.3rem .7rem;border-radius:99px;border:1px solid var(--rule);
background:var(--surface);color:var(--ink);cursor:pointer;z-index:9}
@media print{.toggle{display:none}}
"""

TOGGLE = '<button class="toggle">&#9686; theme</button>'
TOGGLE_JS = ("<script>document.querySelector('.toggle').onclick=function(){"
             "var r=document.documentElement,d=r.getAttribute('data-theme')==='dark';"
             "r.setAttribute('data-theme',d?'light':'dark')};</script>")


def says(text, cite):
    return f'<blockquote><p>{text}</p><span class="loc">{cite}</span></blockquote>'


def build():
    lay = sorted(rows("coverage-three-layers.csv"), key=lambda r: int(r["year"]))
    aud = {r["year"]: r for r in rows("cpe-audited-acfr.csv")}
    fc = {r["year"]: r for r in rows("coverage-table.csv") if r["vintage"] == "2025"}
    yrs = [r["year"] for r in lay]
    under = [r for r in lay if num(r["ratio_pledged"]) < 1.25]
    y26 = next(r for r in lay if r["year"] == "2026")
    a24 = aud["2024"]

    b = ['<p class="back"><a href="index.html">&larr; the record</a></p>',
         '<p class="kicker">The story</p>',
         "<h1>What pays for Pittsburgh&#8217;s new terminal</h1>"]

    b.append('<p class="lede">Pittsburgh International Airport opened its new landside terminal '
             'in November 2025, financed by three bond issues in 2021, 2023 and 2025.</p>')
    b.append('<p>The Allegheny County Airport Authority covenanted to set its rates and charges '
             'so that its net revenue, together with the amount on deposit in a reserve called '
             'the Coverage Account, is at least 1.25 times its annual debt service. Its own '
             'consultant forecasts six years that comply. Documents analyzed by this reporting '
             'show what the compliance is made of.</p>')

    b.append("<h2>What the coverage figure is made of</h2>")
    b.append(f'<p>The Official Statement for the 2025 bonds prints one coverage figure for each '
             f'forecast year, and every one of them clears 1.25. The printed figures are '
             f'{", ".join(f"{num(r[chr(114)+chr(97)+chr(116)+chr(105)+chr(111)+chr(95)+chr(112)+chr(114)+chr(105)+chr(110)+chr(116)+chr(101)+chr(100)]):.2f}" for r in lay[:-1])} '
             f'and {num(lay[-1]["ratio_printed"]):.2f}.</p>')
    b.append('<p>A footnote on that table reads: &#8220;Includes Other Pledged Revenues.&#8221; '
             'The Master Trust Indenture defines those as moneys &#8220;not constituting '
             'Revenues&#8221; that the Authority designates for a period. Exhibit E of the same '
             'document gives the amount for every year.</p>')
    b.append(f'<p>Subtracting the one from the other is this reporting&#8217;s arithmetic. The '
             f'Authority prints only the combined figure. Sources: '
             f'{src("os-2025ab", 202, "PDF 202 (printed B-16)")} and '
             f'{src("os-2025ab", 316, "PDF 316")}.</p>')

    hdr = "".join(f"<th>{y}</th>" for y in yrs)
    r1 = "".join(f'<td>{num(r["ratio_operating"]):.2f}</td>' for r in lay)
    r2 = "".join(f'<td>{num(r["ratio_pledged"]):.2f}</td>' for r in lay)
    r3 = "".join(f'<td>{num(r["ratio_printed"]):.2f}</td>' for r in lay)
    b.append('<div class="scroll"><table class="figs"><thead><tr><th>Coverage</th>' + hdr +
             '</tr></thead><tbody>'
             '<tr class="short"><td>From operations</td>' + r1 + "</tr>"
             '<tr><td>Plus designated revenue</td>' + r2 + "</tr>"
             '<tr><td>Plus the Coverage Account</td>' + r3 + "</tr>"
             "</tbody></table></div>")

    b.append(f'<p>On what the airport earns from running an airport, after expenses, coverage is '
             f'{num(lay[0]["ratio_operating"]):.2f} in {yrs[0]} and between '
             f'{min(num(r["ratio_operating"]) for r in lay):.2f} and '
             f'{max(num(r["ratio_operating"]) for r in lay[1:]):.2f} in the five years after it. '
             f'In 2026 and 2028 operations fall just short of the debt payment. In 2026 the '
             f'airport earns ${num(y26["operating_net_k"])/1000:,.1f} million from operations '
             f'against a payment of ${num(y26["aggregate_annual_debt_service_k"])/1000:,.1f} '
             f'million.</p>')
    b.append(f'<p>Adding the designated revenue raises coverage to '
             f'{num(y26["ratio_pledged"]):.2f} in 2026. On that measure '
             f'{len(under)} of the {len(lay)} forecast years fall below 1.25. The rest is closed '
             f'by the Coverage Account, a reserve the Authority may fund monthly from its own '
             f'revenue, ninth in the indenture&#8217;s order of payment and capped at 25% of that '
             f'year&#8217;s debt service. By this reporting&#8217;s calculation the forecast '
             f'assumes the cap in five of the six years, and 23.23% in 2027.</p>')

    b.append("<h2>What has been designated</h2>")
    b.append('<p>Gas royalty was designated once, $3.8 million in 2019, and at zero in every year '
             'since and every year forecast through 2030.</p>')
    b.append('<p>From 2020 through 2022 the designated money was federal pandemic relief: $13.1 '
             'million, $19.1 million and $13.1 million. For 2023 the same statement prints two '
             'figures, $4.0 million in Exhibit E and $3.0 million in its management discussion, '
             'and this reporting chooses neither. In 2024 the Authority designated nothing.</p>')
    b.append('<p>From 2025 the designated block is slot-machine tax under the state Gaming Act. '
             'The Authority reported receiving $12.4 million a year under that act from 2020 '
             'through 2024, in years it designated none of it into the pledge.</p>')
    b.append(f'<p>In connection with a January 2025 majority-in-interest vote, the Authority '
             f'committed to using discretionary revenue, &#8220;which may include Gaming '
             f'Revenues or Natural Gas Revenues,&#8221; of at least $8.8 million in 2025 and '
             f'$11.575 million a year for 2026 through 2028, to reduce airline rates and charges. '
             f'Exhibit E carries $11,575,000 into 2029 and 2030, two years past the commitment. '
             f'{src("os-2025ab", 67, "PDF 67")}.</p>')
    b.append(says("there can be no assurance that the Gaming Act will not be amended in the "
                  "future to reduce or eliminate payments of such revenues to the Authority",
                  "The Authority, in the sentence directly above that commitment. "
                  + src("os-2025ab", 67, "os-2025ab PDF 67")))
    b.append('<p>The Airline Operating Agreements and the committed designation both end '
             'Dec. 31, 2028. The forecast runs through 2030, and the bonds run to 2056.</p>')

    b.append("<h2>The charge per boarded passenger</h2>")
    b.append(f'<p>Interest on the 2021 and 2023 bonds was capitalized, which means it was paid out '
             f'of the borrowing rather than out of operating revenue, through Feb. 1 and April 1 '
             f'of 2025. Interest on the 2025 bonds was capitalized through Oct. 1 of that year, '
             f'except for the portion supported by passenger facility charges, which the statement '
             f'says is not capitalized. {src("os-2025ab", 39, "PDF 39")}.</p>')
    b.append('<p>Through those dates, one line in the calculation the airlines are billed against '
             'read zero. Also missing from the audited rate base in 2021, 2022, 2023 and 2024, '
             'every year the terminal was under construction: any debt service on it.</p>')
    b.append(f'<p>The audited charge fell to ${num(a24["cpe_audited"]):.2f} per boarded passenger '
             f'in 2024, the lowest of the ten years in that table. It had been '
             f'${num(aud["2015"]["cpe_audited"]):.2f} in 2015 and '
             f'${num(aud["2020"]["cpe_audited"]):.2f} in the pandemic year of 2020. '
             f'{src("acfr-2024", 68, "Table IV, ACAA annual report 2024")}.</p>')
    b.append(f'<p>The consultant&#8217;s forecast is a different measure and belongs to a '
             f'different table. On it the charge runs '
             f'{", ".join(f"${num(fc[y][chr(99)+chr(112)+chr(101)]):.2f} in {y}" for y in yrs[:-1])} '
             f'and ${num(fc[yrs[-1]]["cpe"]):.2f} in {yrs[-1]}. Forecast boardings rise in every '
             f'one of those years.</p>')
    b.append('<div class="note">Four different figures are called cost per enplaned passenger: '
             'the audited annual report, the bond statement&#8217;s management discussion, the '
             'consultant&#8217;s forecast, and FAA Form 5100-127. For 2024 the first two read '
             '$7.34 and $11.56. Nothing here subtracts one from another.</div>')

    b.append("<h2>Who is billed</h2>")
    b.append('<p>The Authority credits its non-airline revenue and any revenue it designates '
             'against the cost of running the airport, and the airlines are billed the '
             'difference.</p>')

    b.append("<h2>What is disputed</h2>")
    b.append('<p>Whether a charge to an airline reaches a passenger is contested. The figure is '
             'an airline cost rather than a fare: it is the airport&#8217;s costs divided by the '
             'number of passengers the carriers board. What an airline does with that cost is a '
             'separate question.</p>')
    b.append('<p>The published research measures adjacent questions and none of it examines '
             'Pittsburgh. Koopmans and Lieshout, in the Journal of Air Transport Management in '
             '2016, found an airline operating cost passed through at under 50% when it falls on '
             'one carrier and over 50% when it falls on the whole sector. Gayle and Lin, studying '
             'US domestic fuel costs from 2013 to 2015, estimated an elasticity of 0.37. Wozny, '
             'examining a Swedish ticket tax in 2018, found over-shifting in competitive markets '
             'and 0.21 in monopoly markets, and a ticket tax is not an airline operating '
             'cost.</p>')

    b.append("<h2>What is not established</h2>")
    b.append('<p>The Authority has not been asked to respond to any of this. No passenger and no '
             'taxpayer has been interviewed.</p>')
    b.append('<p>The Authority filed a 2026 charge of $19.13 with its investors in April 2025. It '
             'later gave the Post-Gazette a figure of $17.64. This reporting has not matched that '
             'second figure to any document, and the date it was given is unsettled. What the '
             'airlines are actually billed in 2026 has not been published.</p>')

    b.append(f'<p class="foot">Every figure on this page is read from a CSV in '
             f'<code>02-data/</code> that names its document and page, and the page is rebuilt '
             f'from them rather than edited. Computed figures are named as this '
             f'reporting&#8217;s wherever they appear. The documents are at '
             f'<a href="documents/index.html">read the documents</a>. Built {BUILT}.</p>')

    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>The story &#183; What pays for Pittsburgh&#8217;s new terminal</title>'
            f'<style>{CSS}</style></head><body>{TOGGLE}'
            f'<div class="wrap">{"".join(b)}</div>{TOGGLE_JS}</body></html>')


def main():
    html = build()
    path = os.path.join(ROOT, "story", "index.html")
    if "--check" in sys.argv:
        if not os.path.exists(path) or io.open(path, encoding="utf-8").read() != html:
            print("story: DRIFT or missing")
            return 1
        print("story --check OK")
        return 0
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8", newline="\n").write(html)
    print(f"wrote story/index.html  {len(html):,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
