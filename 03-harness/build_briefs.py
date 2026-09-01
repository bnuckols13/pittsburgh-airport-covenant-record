#!/usr/bin/env python3
"""build_briefs.py — one working sheet per finding, on the count-sheet pattern.

Modelled on the Emmerling land-use appeal sheets. The skeleton is theirs:

    running head that repeats, so a page found alone identifies itself
    the instrument verbatim, before any gloss
    the argument in plain terms, under the questions a reader actually has
    every authority earning its place with "why it matters here"
    the adverse reading printed rather than hidden
    the record linked, not described

These are working documents, not publication. They build into the case folder,
not the package, for the same reason the editor brief does: they carry what the
reporting cannot yet say in public, including what would defeat each finding.

    python 03-harness/build_briefs.py
    python 03-harness/build_briefs.py --check
"""
import csv, io, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from charts import esc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASE = os.path.normpath(os.path.join(ROOT, "..", "pit-terminal-financing"))
OUT = os.path.join(CASE, "v2", "findings-brief")
DATA = os.path.join(ROOT, "02-data")
CHECKED = "September 1, 2026"
PKG = "https://bnuckols13.github.io/pittsburgh-airport-covenant-record"


def rows(name):
    with io.open(os.path.join(DATA, name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


CSS = """
:root{--ink:#1a1a1a;--soft:#4a4a4a;--muted:#6d6d6d;--paper:#fdfcfa;--rule:#ddd8cc;
--accent:#1c4f8f;--quote:#f4f1ea;--flag:#9c3218;}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);line-height:1.58;
font-family:Georgia,"Palatino Linotype",serif;font-size:16px}
.sheet{max-width:48rem;margin:0 auto;padding:2.4rem 1.4rem 5rem}
.rh{font-family:system-ui,sans-serif;font-size:.74rem;color:var(--muted);
border-bottom:1px solid var(--rule);padding-bottom:.5rem;margin-bottom:1.5rem;
letter-spacing:.01em}
h1{font-size:1.75rem;line-height:1.2;margin:0 0 .5rem;letter-spacing:-.015em}
.claim{font-size:1.08rem;color:var(--ink);margin:0 0 .5rem;
border-left:3px solid var(--accent);padding-left:1rem}
.stand{color:var(--soft);margin:0 0 .4rem}
.checked{font-family:system-ui,sans-serif;font-size:.78rem;color:var(--muted);
margin:0 0 2rem}
h2{font-family:system-ui,sans-serif;font-size:.8rem;letter-spacing:.12em;
text-transform:uppercase;color:var(--accent);font-weight:600;
margin:2.4rem 0 .8rem;padding-top:.9rem;border-top:1px solid var(--rule)}
h3{font-family:system-ui,sans-serif;font-size:.95rem;margin:1.5rem 0 .35rem}
p{margin:0 0 .8rem}
blockquote{margin:1rem 0;padding:1rem 1.2rem;background:var(--quote);
border-left:3px solid var(--accent);border-radius:0 6px 6px 0;font-size:.95rem}
blockquote p{margin:0 0 .7rem}
blockquote p:last-child{margin:0}
blockquote .loc{display:block;font-family:system-ui,sans-serif;font-size:.76rem;
color:var(--muted);margin-top:.7rem}
.asfiled{font-family:system-ui,sans-serif;font-size:.8rem;color:var(--muted);
margin:0 0 .7rem}
ul,ol{margin:.3rem 0 .9rem;padding-left:1.35rem}
li{margin:.3rem 0}
.auth{margin:1.6rem 0 0;padding-bottom:.3rem}
.auth .cite{font-weight:600}
.auth .what{color:var(--soft);font-size:.95rem;margin:.25rem 0 .5rem}
.auth .lnk{font-family:system-ui,sans-serif;font-size:.79rem;word-break:break-all}
.auth .lnk a{color:var(--accent)}
.why{font-family:system-ui,sans-serif;font-size:.78rem;letter-spacing:.11em;
text-transform:uppercase;color:var(--muted);font-weight:600;margin:.9rem 0 .3rem}
.why + ul{font-size:.93rem}
.defeat{background:#fbf6f2;border:1px solid #e6d3c6;border-radius:8px;
padding:1rem 1.2rem;margin:1rem 0}
.defeat h3{margin-top:0}
.defeat li{color:var(--soft)}
.note{font-family:system-ui,sans-serif;font-size:.85rem;color:var(--soft);
background:#f2f4f7;border-left:3px solid #93a4bb;border-radius:0 6px 6px 0;
padding:.8rem 1rem;margin:1rem 0}
.hash{font-family:"Cascadia Code",Consolas,monospace;font-size:.72rem;
color:var(--muted);word-break:break-all}
.foot{margin-top:3rem;border-top:1px solid var(--rule);padding-top:1rem;
font-family:system-ui,sans-serif;font-size:.78rem;color:var(--muted)}
a{color:var(--accent)}
.idx{list-style:none;padding:0}
.idx li{border-bottom:1px solid var(--rule);padding:.8rem 0}
.idx a{font-weight:600;text-decoration:none;font-size:1.05rem}
.idx a:hover{text-decoration:underline}
.idx .d{display:block;color:var(--soft);font-size:.92rem;margin-top:.2rem}
@media print{body{background:#fff}.sheet{max-width:none}}
"""


def page(title, body):
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            f"<title>{esc(title)}</title><style>{CSS}</style></head><body>"
            f"<div class=\"sheet\">{body}</div></body></html>")


def head(n, short):
    return (f'<p class="rh">PIT terminal financing &#183; Allegheny County Airport Authority '
            f'&#183; Finding {n}</p>')


def quote(text, loc):
    return f'<blockquote><p>{text}</p><span class="loc">{esc(loc)}</span></blockquote>'


def authority(cite, what, links, why):
    ls = "".join(f'<div class="lnk"><a href="{esc(u)}" rel="noopener">{esc(u)}</a></div>'
                 for u in links)
    ws = "".join(f"<li>{w}</li>" for w in why)
    return (f'<div class="auth"><div class="cite">{cite}</div>'
            f'<p class="what">{what}</p>{ls}'
            f'<p class="why">Why it matters here</p><ul>{ws}</ul></div>')


def defeat(items):
    return ('<div class="defeat"><h3>What would defeat this finding</h3><ul>'
            + "".join(f"<li>{i}</li>" for i in items) + "</ul></div>")


DOCS = {r["id"]: r for r in rows("documents.csv")}


def rec(doc_id, note):
    d = DOCS.get(doc_id, {})
    return (f'<li><a href="{PKG}/documents/index.html#{doc_id}">{esc(doc_id)}</a> '
            f'&#183; {esc(d.get("title", ""))}. {note}</li>')


# --------------------------------------------------------------------- sheets

def sheet(n, title, claim, matters, quotes, establishes, unknown, kills, records,
          notes=()):
    """One sheet. The order is the order the questions get asked."""
    b = [f'<p class="rh">PIT terminal financing &#183; ACAA &#183; Finding {n}</p>',
         f"<h1>Finding {n}: {title}</h1>",
         f'<p class="claim">{claim}</p>',
         f'<p class="checked">Every page cite checked {CHECKED}. Working sheet.</p>']

    b.append("<h2>Why it matters</h2>")
    b.append(f"<p>{matters}</p>")

    b.append("<h2>What the documents say</h2>")
    for text, loc in quotes:
        b.append(quote(text, loc))

    b.append("<h2>What this establishes</h2><ol>")
    b += [f"<li>{x}</li>" for x in establishes]
    b.append("</ol>")

    for note in notes:
        b.append(f'<div class="note">{note}</div>')

    b.append("<h2>What I don&#8217;t know</h2><ol>")
    b += [f"<li>{x}</li>" for x in unknown]
    b.append("</ol>")

    b.append('<div class="defeat"><h3>What would kill this</h3><ol>')
    b += [f"<li>{x}</li>" for x in kills]
    b.append("</ol></div>")

    b.append("<h2>Documents</h2><ul>")
    b += records
    b.append("</ul>")
    return page(f"Finding {n}: {title}", "".join(b))


def finding_one():
    lay = sorted(rows("coverage-three-layers.csv"), key=lambda r: int(r["year"]))
    worst = min(lay, key=lambda r: float(r["ratio_operating"]))
    under = [r for r in lay if float(r["ratio_pledged"]) < 1.25]
    lo = min(float(r["ratio_operating"]) for r in lay)
    hi = max(float(r["ratio_operating"]) for r in lay)

    return sheet(
        "I",
        "the airport's operations don't produce the margin it promised its lenders",
        "The Authority promised 1.25 times its debt payment every year. Its own forecast meets "
        "that. Its operations don&#8217;t. The gap is filled with a state gaming appropriation "
        "and a reserve that is already at its contractual ceiling.",
        "This is Hypothesis 1. The Authority financed the terminal on revenue it called secure. "
        "The forecast shows what that revenue actually is.",
        [("Includes Other Pledged Revenues.",
          "os-2025ab, PDF 202 (printed B-16). Footnote 1, attached to the Net Revenues row of "
          "the consultant's forecast of April 8, 2025."),
         ("&#8220;Other Pledged Revenues&#8221; shall mean moneys, <b>not constituting "
          "Revenues</b>, that are designated, for any period.",
          "os-2025ab, PDF 343. The indenture's own definition."),
         ("Ninth: to the Coverage Account. On or prior to the tenth (10th) Business Day of each "
          "month, at the discretion of the Authority, <b>Revenues</b> may be deposited to the "
          "Coverage Account.",
          "os-2025ab, PDF 32. The flow of funds.")],
        [f"Footnote 1 says the Net Revenues row already includes the designated money. That means "
         f"I can subtract it out. Exhibit E gives the amount for every year, so this is "
         f"arithmetic, not inference.",
         f"On operating revenue alone the ratio runs {lo:.2f} to {hi:.2f} against a required 1.25. "
         f"In {worst['year']} it is {float(worst['ratio_operating']):.2f}, which is below the debt "
         f"payment itself.",
         f"On pledged revenue alone, before the reserve, {len(under)} of {len(lay)} years fall "
         f"below 1.25.",
         "The two things filling the gap are different kinds of money. The designated block is "
         "outside Revenues by the indenture's own definition. The Coverage Account is fed from "
         "Revenues, so it is the airport's own money set aside.",
         "The reserve is at exactly 25.00 percent of debt service, its contractual maximum, in "
         "five of the six years. There is no headroom left in it."],
        ["Whether the consultant's workpapers show the same subtraction. Footnote 1 is one line "
         "and the whole separation rests on it.",
         "Why 2027 sits at 23.23 percent when every other year is at the 25 percent ceiling.",
         "What the Authority would say about any of this. Right of reply has not been sought."],
        ["The Coverage Account is operating money. Any sentence calling the whole 31 percent "
         "revenue the airport does not earn is wrong, and the Authority can correct it in a line. "
         "Only the designated block, about 11 percent, is outside Revenues.",
         "On the test the indenture actually sets, the forecast complies in all six years. This "
         "finding is about what the number is made of, not whether it is met.",
         "&#8220;Always at the ceiling&#8221; overstates it. 2027 is below.",
         "Nothing here shows the Authority would decline to fund the reserve. It is their own "
         "money moving to satisfy a test. Framing that as a risk invites the obvious answer."],
        [rec("os-2025ab", "Forecast, definitions, flow of funds."),
         rec("acfr-2024", "Audited series; shows Net Revenues is Total Revenues less O&amp;M."),
         rec("os-2021ab", "The earlier forecast. Separate vintage, never summed with 2025.")])


def finding_two():
    aud = {r["year"]: r for r in rows("cpe-audited-acfr.csv")}
    zeros = sorted(r["year"] for r in rows("cpe-audited-acfr.csv")
                   if r["debt_service_in_rate_base"] == "0")
    a24 = aud["2024"]

    return sheet(
        "II",
        "nobody paid for the building until 2025",
        "Interest on the terminal bonds was capitalized through early 2025. For four years no "
        "debt service entered the bill the airlines pay, and the audited charge fell to its "
        "lowest in a decade. The first payment lands in 2025.",
        "This reverses what I had. The earlier drafts said costs rose during construction. On the "
        "Authority&#8217;s own audited numbers they fell, and the Authority could show that from "
        "its own report in an afternoon.",
        [("Note: Interest on the 2021 Bonds was capitalized through February 1, 2025. Interest on "
          "the 2023 Bonds was capitalized through April 1, 2025. Interest on the 2025 Bonds is "
          "capitalized through October 1, 2025.",
          "os-2025ab, PDF 39.")],
        [f"Table IV of the audited report carries debt service in the rate base at zero for "
         f"{zeros[0]} through {zeros[-1]}.",
         f"The audited charge for 2024 is ${float(a24['cpe_audited']):.2f}, the lowest in the "
         f"ten-year series. It reproduces: ${float(a24['rate_base_costs']):,.0f} of rate base "
         f"costs over {float(a24['enplanements']):,.0f} enplanements.",
         "The capitalization note explains the zeros. Without it the audited series is a fact "
         "with no reason attached.",
         "The consultant forecasts the charge rising in every year from 2025 to 2030."],
        ["What the 2025 audited report says. It is captured and hashed and I have not read its "
         "Table IV yet. That is the year the debt service arrives.",
         "Whether the $16.10 holds. It comes from an FAA CATS query rather than a document, and "
         "it is the only load-bearing number here without a hashed source."],
        ["Capitalized interest is ordinary practice for construction financing and is disclosed "
         "in the bond documents. Any implication of concealment is wrong.",
         "Four measures share the name cost per enplaned passenger. For 2024 the audited report "
         "says $7.34 and the bond statement says $11.56. Printing one next to the other without "
         "naming the basis is the most attackable sentence available.",
         "The audited series shows the charge falling. Any framing built on costs rising during "
         "construction dies here."],
        [rec("acfr-2024", "Table IV, the ten-year audited series."),
         rec("acfr-2025", "The first year debt service arrives. Captured, not yet read."),
         rec("os-2025ab", "The capitalization note and the forecast."),
         rec("faa-cats-127", "The federal basis. Not captured.")])


def finding_three():
    return sheet(
        "III",
        "the forecast spends money nobody has committed",
        "The airlines voted the designation for 2026 through 2028. The forecast carries the same "
        "figure into 2029 and 2030. The airline agreement expires Dec. 31, 2028. The bonds run "
        "to 2056.",
        "This is the sharpest version of Hypothesis 1. The Authority says the revenue is secure. "
        "Its own bond document says it cannot assure that.",
        [("In connection with a January 2025 Majority In Interest (&#8220;MII&#8221;) vote, the "
          "Authority committed to using discretionary revenue, which may include Gaming Revenues "
          "or Natural Gas Revenues, of no less than $8.8 million for 2025 and $11.575 million per "
          "year <b>for 2026 through 2028</b> to reduce airline rates and charges.",
          "os-2025ab, PDF 67."),
         ("The Authority expects to continue to receive payments of $12.4 million annually for so "
          "long as it continues to be a recipient under the Gaming Act. However, <b>there can be "
          "no assurance that the Gaming Act will not be amended in the future to reduce or "
          "eliminate payments of such revenues to the Authority.</b>",
          "os-2025ab, PDF 67, the sentence directly above the MII passage.")],
        ["The commitment covers 2026, 2027 and 2028. It stops there.",
         "Exhibit E forecasts $11,575,000 in 2029 and again in 2030, which is the committed "
         "figure carried two years past the commitment.",
         "From 2025 the designated block is entirely slot-machine tax, a state appropriation. Gas "
         "royalty is zero in every year from 2020 through 2030 and does not come back.",
         "<b>The Authority itself says it cannot assure the gaming money continues.</b> That is "
         "the issuer telling investors the revenue behind the designation is not secure. I do not "
         "have to characterise it; they wrote it down."],
        ["What happened to the $12.4 million during Pennsylvania&#8217;s 2025 budget impasse, and "
         "what happens in the next one. Nobody on this case has called Harrisburg. No records "
         "request needed, no permission needed.",
         "Whether a further MII vote is planned or discussed. That would extend the commitment "
         "and take the edge off this.",
         "Whether 2028 is a real cliff or a routine renegotiation. That needs the carriers or a "
         "signed extension and I have neither."],
        ["A further vote could extend it. Nothing says it will not.",
         "The money has arrived every year, $12.4 million in each of 2020 through 2024. "
         "Continuation is the base case, not a leap.",
         "Airline agreements get renegotiated routinely, so 2028 may turn out to be "
         "unremarkable.",
         "A forecast row is not a promise. Treating it as one would be the same error in the "
         "other direction."],
        [rec("os-2025ab", "The MII passage, the risk language, Exhibit E.")],
        notes=["<b>This is the Harrisburg call.</b> The gaming money is a state appropriation, so "
               "its volatility is a matter of record rather than something I have to argue. One "
               "phone call turns &#8220;variable and risky&#8221; from an adjective into a "
               "finding."])


def finding_four():
    return sheet(
        "IV",
        "whether any of this reaches a passenger is contested, and I have not settled it",
        "The charge is residual, so revenue the Authority does not designate is billed to the "
        "carriers. What happens after that is disputed. The airlines say it does not reach the "
        "ticket. No study in the file tests Pittsburgh, and nobody who would bear it has been "
        "interviewed.",
        "This is Hypothesis 2 and it is the weakest part of the reporting. The mechanism is "
        "documented. The harm is not.",
        [("The Authority committed to using discretionary revenue &#8230; <b>to reduce airline "
          "rates and charges.</b>",
          "os-2025ab, PDF 67. States the direction: money designated reduces what the carriers "
          "are billed, money not designated does not.")],
        ["The charge is set residually. That much is on the face of the documents.",
         "The consultant forecasts it rising in every year of the forecast.",
         "The carriers' position is that it does not reach the ticket. That position is reported "
         "elsewhere; no airline has been asked directly by me.",
         "The published research measures adjacent questions. None of it tests Pittsburgh."],
        ["Whether fares or service at PIT moved with the charge. DOT DB1B and T-100 for "
         "Pittsburgh and comparable origin-and-destination airports would test it. Neither has "
         "been pulled, and it needs no permission.",
         "What a carrier would say on the record.",
         "What the three academics I emailed on Aug. 26 think. None has replied."],
        ["The carriers may be right. If the charge does not reach the ticket, the harm channel I "
         "have been circling does not exist in the form assumed.",
         "No study in the record tests this airport, so the literature cannot close it either way.",
         "The standing rule is that a harm channel is not reported until somebody who bears it "
         "has been spoken to. Nobody has. Until then this is a documented mechanism and an open "
         "question, and writing it as anything more would break the rule.",
         "The Allegheny Institute is an interested party. Its 2017 prediction is a lead, not "
         "evidence, until the DOT data is pulled."],
        [rec("os-2025ab", "The residual mechanism, the forecast charge."),
         rec("koopmans-lieshout-2016", "Citation record. Article is paywalled, not republished."),
         rec("ai-20171004", "The 2017 prediction. Untested.")])


def index_sheet():
    items = [
        ("finding-1.html", "Finding I: the airport's operations don't produce the margin it "
                           "promised its lenders",
         "0.98 to 1.20 against a required 1.25. The gap is a state gaming appropriation plus a "
         "reserve already at its ceiling."),
        ("finding-2.html", "Finding II: nobody paid for the building until 2025",
         "Interest capitalized, debt service zero in the rate base for four years, the audited "
         "charge down to $7.34. This reversed what I had."),
        ("finding-3.html", "Finding III: the forecast spends money nobody has committed",
         "The vote covers 2026 through 2028. The forecast fills 2029 and 2030. The Authority says "
         "it cannot assure the gaming money continues."),
        ("finding-4.html", "Finding IV: whether any of this reaches a passenger is contested",
         "The mechanism is documented. The harm is not, and nobody who would bear it has been "
         "interviewed."),
    ]
    b = ['<p class="rh">PIT terminal financing &#183; ACAA &#183; working sheets</p>',
         "<h1>Four findings, and what would kill each one</h1>",
         '<p class="claim">Central inquiry: what happens if the airport can&#8217;t pay its debt '
         'via the projected revenue sources?</p>',
         f'<p class="checked">Every page cite checked {CHECKED}. Working sheets, not '
         f'publication.</p>',
         '<h2>The sheets</h2><ul class="idx">']
    for href, title, desc in items:
        b.append(f'<li><a href="{href}">{esc(title)}</a>'
                 f'<span class="d">{esc(desc)}</span></li>')
    b.append("</ul>")
    b.append('<div class="note"><b>Why every sheet ends with what would kill it.</b> Taken from '
             'the count sheets in the Jackson Township appeal, which print the authority that '
             'cuts against the count rather than leaving it out. A sheet that only collects '
             'supporting material tells you nothing about how strong the claim is.</div>')
    b.append('<h2>Where each one stands</h2><ol>'
             '<li>Findings I and II are documented and reproduce from the Authority&#8217;s own '
             'rows.</li>'
             '<li>Finding III is documented and has one call attached to it that would make it '
             'much stronger.</li>'
             '<li>Finding IV is a mechanism and an open question. It cannot carry weight until '
             'somebody who bears the cost has been interviewed.</li></ol>')
    b.append(f'<p class="foot">Generated from the package data. Public evidence: '
             f'<a href="{PKG}/">{PKG}</a>.</p>')
    return page("Four findings, and what would kill each one", "".join(b))


TARGETS = [("index.html", index_sheet), ("finding-1.html", finding_one),
           ("finding-2.html", finding_two), ("finding-3.html", finding_three),
           ("finding-4.html", finding_four)]


def main():
    check = "--check" in sys.argv
    bad = 0
    for name, fn in TARGETS:
        html = fn()
        path = os.path.join(OUT, name)
        if check:
            if not os.path.exists(path) or io.open(path, encoding="utf-8").read() != html:
                print(f"briefs {name}: DRIFT or missing")
                bad += 1
            else:
                print(f"briefs {name} --check OK")
        else:
            os.makedirs(OUT, exist_ok=True)
            io.open(path, "w", encoding="utf-8", newline="\n").write(html)
            print(f"wrote v2/findings-brief/{name}  {len(html):,} bytes")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
