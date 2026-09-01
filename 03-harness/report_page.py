"""report_page.py — the six modules and their prose.

Kept apart from build_report.py, which owns the plates, so that the writing and
the drawing can be edited without stepping on each other. The spine is Brian's,
from his session note of 2026-08-29: the room where everyone agreed, how secure
the covenant is, the consequences and rising costs, the enplanement debate, the
forecast and how it has gone, and the options.

Each module carries its own plate and paragraphs under the plate that read it.
Each stands alone. Cutting one does not break the others, which is what modular
has to mean if it is to mean anything.
"""
import io, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_report as R
import build_explainer as be
from charts import esc

BUILT = R.BUILT

CSS = """
.mod{border-top:1px solid var(--ring);padding-top:1.7rem;margin-top:2.4rem}
.mod .n{font-family:system-ui,sans-serif;font-size:.72rem;letter-spacing:.12em;
text-transform:uppercase;color:var(--blue);margin:0 0 .3rem}
.mod h2{margin:0 0 .35rem;font-size:1.44rem;line-height:1.24}
.mod .standfirst{color:var(--ink2);font-size:1.02rem;margin:0 0 1.1rem}
.hyp{display:inline-block;font-family:system-ui,sans-serif;font-size:.66rem;letter-spacing:.06em;
text-transform:uppercase;color:var(--muted);border:1px solid var(--ring);border-radius:99px;
padding:.12rem .5rem;margin-left:.5rem;vertical-align:middle;font-weight:400}
figure{margin:1.6rem 0 1.3rem;padding:0}
figure svg{width:100%;height:auto;overflow:visible;display:block}
figcaption{font-family:system-ui,sans-serif;font-size:.84rem;color:var(--ink2);line-height:1.56;
margin-top:.6rem;border-left:2px solid var(--ring);padding-left:.9rem}
figcaption b{color:var(--ink)}
figcaption .prov{display:block;color:var(--muted);font-size:.76rem;margin-top:.5rem}
text{font-family:system-ui,sans-serif;font-variant-numeric:tabular-nums}
.ax{font-size:10.5px;fill:var(--muted)}
.lab{font-size:12.5px;fill:var(--ink);font-weight:600}
.lab2{font-size:11.5px;fill:var(--ink2)}
.val{font-size:11.5px;fill:var(--ink);font-weight:600}
.open{background:color-mix(in srgb,var(--yellow) 10%,transparent);
border-left:3px solid var(--yellow);border-radius:0 8px 8px 0;padding:.8rem 1rem;margin:1.3rem 0;
font-family:system-ui,sans-serif;font-size:.85rem;line-height:1.5}
.open b{display:block;margin-bottom:.15rem}
.toc{background:var(--surface);border:1px solid var(--ring);border-radius:12px;
padding:1rem 1.2rem;margin:1.7rem 0 0}
.toc ol{margin:.45rem 0 0;padding-left:1.3rem;font-family:system-ui,sans-serif;font-size:.9rem}
.toc li{margin:.32rem 0}
.toc a{text-decoration:none}
.toc a:hover{text-decoration:underline}
"""


def fig(svg, caption, prov):
    return f'<figure>{svg}<figcaption>{caption}<span class="prov">{prov}</span></figcaption></figure>'


def module(anchor, kicker, head, hyp, standfirst, body):
    h = f'<span class="hyp">{esc(hyp)}</span>' if hyp else ""
    return (f'<section class="mod" id="{anchor}"><p class="n">{esc(kicker)}</p>'
            f'<h2>{esc(head)}{h}</h2><p class="standfirst">{esc(standfirst)}</p>{body}</section>')


def build():
    promise_svg, precs, share = R.plate_promise()
    debt_svg, _ = R.plate_debt_arrives()
    bases_svg, aud, _ = R.plate_three_bases()
    desig_svg, fed, gas, gam = R.plate_designated()
    budget_svg, _ = R.plate_budget()
    spans_svg, _ = R.plate_spans()

    a24 = next(r for r in aud if r["year"] == "2024")
    worst = max(precs, key=lambda x: x["promise"] - x["earned"])
    gapw = (worst["promise"] - worst["earned"]) / 1000

    M = {}

    M['m1'] = (module("m1", "Module one", "The room where everyone agreed", "",
        "In October the whole political spectrum turned out for the terminal. The only elected "
        "body that touches the Authority had been told, seven years earlier, that it had no "
        "standing to ask about the money.",
        "<p>On a Saturday morning in October, with the federal government shut down and the "
        "state budget months overdue, the county executive stood beside the chief executive of "
        "the airport authority under 811,000 square feet of new glass and steel. Members of "
        "Congress from both parties were there. Nobody on the dais said what it would cost to "
        "carry the building.</p>"
        "<p>In February 2018, four months after the board approved the project, a resident named "
        "David Allinder asked Allegheny County Council to hold a public hearing on it. Council "
        "did not hold one. Its president said the county had no jurisdiction over the Authority. "
        "No elected body in Allegheny County has taken the question up since. Council does "
        "confirm every member of the airport board, and in July it seated a state senator who "
        "sits on the committees handling the state money the airport receives, 12 to 3.</p>"
        + fig(spans_svg,
            "<b>A nine-year contract holding up a thirty-five-year debt.</b> The bonds run to "
            "2056. The agreement that makes the airlines responsible for whatever the airport "
            "does not earn, and the money committed under it, both end on Dec. 31, 2028. "
            "Twenty-eight years of the debt fall after every arrangement now holding the "
            "arithmetic together has expired.",
            "Data <code>02-data/term-structure.csv</code>, from os-2025ab PDF 39, 67 and 70.")
        + '<div class="open"><b>Not yet reported</b>This scene is assembled from the record '
          'rather than from the room. Nobody who stood on that dais has been interviewed.</div>'))

    M['m2'] = (module("m2", "Module three", "How secure the covenant is", "Hypothesis 1",
        "The Authority promised its lenders a quarter more than it owes them, every year. Its "
        "own forecast meets that promise. Its own operations do not: the margin is made up with "
        "a state gaming appropriation and a reserve already topped up to the contractual "
        "ceiling.",
        "<p>The terminal is meant to pay for itself out of what the airport earns, with a margin "
        "on top. The bond documents call it the rate covenant and print it as 1.25. The Official "
        "Statements print one combined figure for each forecast year, and every one clears.</p>"
        "<p>That figure is made of three things, and they are not the same kind of money. The "
        "first is what the airport earns by running an airport. The second the indenture calls "
        "Other Pledged Revenues, defined as moneys &#8220;not constituting Revenues, that are "
        "designated&#8221; into the pledge for a period: from 2025 the whole of that block is "
        "slot-machine tax, a state appropriation, and it is not operating revenue at all. The "
        "third is the Coverage Account, which is operating money: Revenues may be deposited to "
        "it monthly &#8220;at the discretion of the Authority,&#8221; ninth in the flow of funds "
        "and capped at a quarter of the debt payment. What is notable about it is not that the "
        "Authority might decline to fund it, which it has no reason to do, but that the forecast "
        "already assumes the maximum the contract allows in five of the six years. There is no "
        "headroom left in it.</p>"
        + fig(promise_svg,
            f"<b>What holds the promise up.</b> The solid block is what the airport earns. The "
            f"first hatched block is the designated gaming money, which is not operating revenue; "
            f"the second is the Coverage Account deposit. The rule across each bar is the "
            f"promise, 1.25 times that year's debt payment. On its own earnings the airport "
            f"falls short in all six forecast years, by ${gapw:.1f} million at the widest, in "
            f"{worst['year']}. Across the six, <b>{share*100:.0f} percent of the promise is met "
            f"by the two blocks above what the airport earns.</b>",
            "Data <code>02-data/coverage-table.csv</code> and "
            "<code>other-pledged-revenue.csv</code>, from os-2025ab PDF 202 and PDF 316. The "
            "decomposition is ours; the statement prints only the combined figure, and "
            "recomputing that figure from the same rows reproduces every printed ratio.")
        + "<p>What has actually been designated is not what the public record has assumed.</p>"
        + fig(desig_svg,
            f"<b>Federal aid, then nothing, then casino money.</b> From 2020 through 2023 the "
            f"designation was federal pandemic relief in full, peaking at "
            f"${fed['2021']/1000:.1f} million in 2021. In 2024 the Authority designated "
            f"<b>nothing at all</b>. Gas royalty appears once, in 2019, at "
            f"${gas['2019']/1000:.1f} million, and is zero in every year after it. Slot-machine "
            f"money returns only in the forecast, from 2025.",
            "Data <code>02-data/other-pledged-revenue-itemized.csv</code>, from os-2025ab PDF "
            "316. The 2023 total conflicts inside the same statement, $3,029k at PDF 61 against "
            "$4,040k at PDF 316. Both are recorded and neither is chosen.")
        + "<p>The airlines voted that money for 2026 through 2028. The forecast designates it in "
        "2029 and 2030 as well, two years past the vote. The statement's own word for what "
        "happens then is that the Authority &#8220;expects to continue to designate.&#8221;</p>"
        + '<div class="open"><b>What this is not</b>None of it is a breach. The indenture lets '
          'the Coverage Account count toward the test and on that test the forecasts comply in '
          'every year. Missing once would not be an event of default either: the indenture '
          'requires a consultant and a rate increase, and only a second consecutive miss after '
          'rates have risen qualifies. The finding is what the ratio is on pledged revenue '
          'alone.</div>'))

    M['m3'] = (module("m3", "Module five", "What it costs to fly out of Pittsburgh", "Hypothesis 2",
        "Airlines are billed whatever the airport does not earn, which makes the covenant and "
        "the charge to carriers the same fact seen from two sides.",
        "<p>Carriers are not charged by the head. They pay rent and landing fees, $298.36 per "
        "square foot of terminal space and $4.06 per 1,000 pounds of landing weight as of "
        "January. The industry figure is that total divided by boardings, and Pittsburgh sets it "
        "on a residual basis: every other source of money is counted first and the carriers are "
        "billed the remainder.</p>"
        "<p>Three series go by that name in this story and they are never subtracted across each "
        "other.</p>"
        + fig(bases_svg,
            f"<b>Three measures, one name.</b> The Authority's audited annual report, its bond "
            f"statement's management discussion, and its consultant's forecast. They track each "
            f"other closely from 2020 to 2023 and then part: for 2024 the audited report says "
            f"<b>${a24['cpe_audited']}</b> where the bond statement says <b>$11.56</b>. The "
            f"federal Form 5100-127 filing is a fourth measure again, marked separately.",
            "Data <code>02-data/cpe-audited-acfr.csv</code> from the 2024 annual comprehensive "
            "financial report, Table IV, and os-2025ab PDF 62 and PDF 202. Every audited row "
            "reproduces from rate base costs divided by enplanements.")
        + "<p>Passengers pay directly as well. A $4.50 charge sits on every eligible ticket and "
        "did not come down when the terminal opened, because federal law caps it there. Rental "
        "customers have paid $8 a day since Jan. 1, 2025. Pennsylvania taxpayers pay through a "
        "$12.4 million appropriation of gambling money that goes to the airport instead of "
        "somewhere else.</p>"
        + '<div class="open"><b>Not yet reported</b>No passenger, parker, rental customer or '
          'terminal tenant has been asked what any of this has cost them. Every source in this '
          'module is a document.</div>'))

    M['m4'] = (module("m4", "Module six", "The enplanement debate", "Hypothesis 1 and 2",
        "The obvious version of this story is that a public authority inflated its passenger "
        "forecast to justify a building. The record does not support it, and what the record "
        "shows instead is harder to answer.",
        "<p>The 2021 forecast projected 4,924,000 boardings for 2024 if traffic recovered "
        "strongly. The year came in at 4,964,361. The passengers arrived.</p>"
        "<p>The cost did not hold, and the reason sits in the audited report rather than in the "
        "bond documents: for four years no debt service entered the airline bill at all.</p>"
        + fig(debt_svg,
            f"<b>The bill that had not started.</b> Debt service inside the airline rate base "
            f"reads zero for 2021, 2022, 2023 and 2024. Interest on the 2021 bonds was "
            f"capitalized through Feb. 1, 2025 and on the 2023 bonds through April 1, 2025, so "
            f"the carriers were billed nothing toward the new terminal across those four years. "
            f"The charge fell with it, to <b>${a24['cpe_audited']} in 2024 on the audited basis, "
            f"its lowest in a decade</b>. The forecast bars to the right are aggregate annual "
            f"debt service, a different measure, drawn adjacent and never joined to the audited "
            f"ones.",
            "Data <code>02-data/debt-service-arrives.csv</code>, from the 2024 annual "
            "comprehensive financial report Table IV and os-2025ab PDF 202. The capitalized "
            "interest note is at os-2025ab PDF 39.")
        + "<p>So the argument is not that the charge has been rising. On the Authority's own "
        "audited series it fell, to its lowest in ten years, in the last full year before the "
        "payments began. The argument is that it was low because the building was not yet being "
        "paid for, and that the Authority's own consultant expects it to climb every year now "
        "that it is.</p>"
        "<p>One further thing the record carries: between its 2021 and 2023 bond statements the "
        "Authority moved the passenger forecast forward unchanged and raised the forecast cost "
        "by between 20 and 27 percent depending on the year. The forecast that was revised is "
        "not the forecast that was wrong.</p>"))

    M['m5'] = (module("m5", "Module four", "The forecast, and how it has gone", "Hypothesis 1",
        "Between 2017 and 2021 three officials told the public what airlines would pay once the "
        "terminal opened. Each figure sat below what the bond documents already assumed.",
        "<p>The chief executive said in 2017 that the charge would fall to $9.73 by 2023. The "
        "2023 figure the Authority's management discussion reports is $11.34, and Table IV of "
        "the same statement reports $11.50, a conflict the document does not resolve. At the "
        "2021 groundbreaking the chief financial officer said it should settle between $10 and "
        "$11. The statement filed with investors nine weeks before he spoke had already put the "
        "opening year higher.</p>"
        "<p>The consultant now expects $20.53 by 2030, and the charge rises in every year of the "
        "forecast.</p>"
        + '<div class="open"><b>Held</b>The 2025 enplanement actual is not in the case. The only '
          'figure the file holds is an estimate, so nothing about 2025 traffic runs until the '
          'audited number is in hand.</div>'))

    M['m6'] = (module("m6", "Coda", "The options", "Hypothesis 1",
        "The board voted to build rather than renovate. Federal guidance required the "
        "comparison. It has never been published.",
        "<p>In September 2017 the board voted to build a new landside terminal rather than "
        "renovate the one it had. The chief executive said that day that renovating "
        "&#8220;is actually not cheaper and we looked at it.&#8221; Federal guidance for airport "
        "master plans requires that comparison, weighing each option against &#8220;a wide range "
        "of evaluation criteria, including its operational, environmental, and financial "
        "impacts.&#8221; The Authority's 2017 annual report says the plan is on file with the "
        "Federal Aviation Administration. Neither the Authority nor the FAA has released it, and "
        "no estimate for renovating has appeared in the nine years since.</p>"
        + fig(budget_svg,
            "<b>The budget, four revisions.</b> Each step carries its escalation on the figure "
            "before it. The 2017 board figure is annotated rather than drawn, because it appears "
            "in no hashed document in this record.",
            "Data <code>02-data/budget-revisions.csv</code>, from os-2021ab PDF 479, os-2023abc "
            "PDF 18 and os-2025ab PDF 16.")
        + "<p>The old building is closed and still standing. The line for demolishing it read $33 "
        "million in the statement the Authority sold in 2023 and $0 in the one it sold in April "
        "2025, which says the demolition was postponed &#8220;to reduce project costs and "
        "associated debt&#8221; and puts the cost of that postponement at $2,047,000 a year in "
        "additional operating expense.</p>"
        + '<div class="open"><b>Requested, not answered</b>A Right-to-Know for the alternatives '
          'analysis and a parallel FOIA to the FAA are drafted. That analysis is the document '
          'that would settle whether renovating really was more expensive.</div>'))


    # Module two exists because the reporting is an aggregation rather than an access
    # story, and a reader who does not know that cannot weigh anything below it.
    M['m0'] = (module("m0", "Module two", "How this was reported", "",
        "No official at the Authority has been interviewed and no records request has been "
        "answered. Everything below is drawn from the documents the decisions were written into.",
        '<p>Bond official statements filed with investors, eleven years of audited annual '
        'financial reports, board records, the fee schedule the carriers are billed against, and '
        'federal filings. Each was retrieved from a public source, hashed, and cited to a '
        'numbered page. Thirty-six records in all, of which twenty-seven are immutable documents '
        'whose checksum any reader can reproduce.</p>'
        '<p>Two things follow from working this way, and they cut in opposite directions. Every '
        'figure in the modules below can be checked against a named page in a document that can '
        'be downloaded and hashed independently, which is a stronger guarantee than a quotation '
        'from an official. And where the Authority\'s own filings disagree with each other, ten '
        'places in all, the disagreement is published rather than resolved by choosing the more '
        'convenient number.</p>'
        '<p>What it does not buy is comment. The Authority has not been asked to explain any of '
        'this, no records request has been answered, and every person quoted in these modules is '
        'quoted from published reporting by somebody else and labelled that way. The claims and '
        'the documents behind them are listed at '
        '<a href="../claims/index.html">what the reporting says</a>; the documents themselves at '
        '<a href="../documents/index.html">read the documents</a>; the contradictions and the '
        'claims held back at <a href="../factcheck/index.html">the fact check</a>.</p>'))

    # Brian's spine of 2026-09-01. "The options" is not part of it and follows as a coda.
    ORDER = ['m1', 'm0', 'm2', 'm5', 'm3', 'm4']
    m = [M[k] for k in ORDER] + [M['m6']]

    toc = ('<div class="toc"><b style="font-family:system-ui,sans-serif;font-size:.85rem">'
           'Six modules, and a coda</b><ol>'
           '<li><a href="#m1">The room where everyone agreed</a></li>'
           '<li><a href="#m0">How this was reported</a></li>'
           '<li><a href="#m2">How secure the covenant is</a></li>'
           '<li><a href="#m5">The forecast, and how it has gone</a></li>'
           '<li><a href="#m3">What it costs to fly out of Pittsburgh</a></li>'
           '<li><a href="#m4">The enplanement debate</a></li></ol>'
           '<p style="font-family:system-ui,sans-serif;font-size:.85rem;margin:.5rem 0 0">'
           'Then a coda: <a href="#m6">the options</a>.</p></div>')

    body = ('<p class="back" style="font-family:system-ui,sans-serif;font-size:.82rem;'
            'margin:0 0 1.2rem"><a href="../index.html">&#8592; the package</a></p>'
            '<p class="kicker">The record</p>'
            '<h1>Pittsburgh promised its lenders a quarter more than it owes them. Its own '
            'operations do not produce it.</h1>'
            '<p class="sub">The new terminal was financed on two propositions: that the airport '
            'would pay for it out of what it earns, and that flying out of Pittsburgh would get '
            'cheaper. Documents filed with its lenders show its own consultant expecting neither. '
            'The margin above the debt payment is made up with a state gaming appropriation and a '
            'reserve already topped up to the ceiling the contract allows. This is the record, in '
            'six modules, each standing on its own.</p>'
            + toc + "".join(m) +
            '<p class="src">Every figure on this page is drawn from a CSV in '
            '<code>02-data/</code> that names its document, page and SHA-256. No coordinate is '
            'typed by hand. Rebuild with <code>python 03-harness/report_page.py</code> and check '
            f'with <code>--check</code>. Reported by Lena Rose Williams. Built {BUILT}.</p>')
    return be.page("The record &#183; Pittsburgh Airport Covenant Record", body, "", CSS)


def main():
    out = os.path.join(R.ROOT, "report", "index.html")
    html = build()
    if "--check" in sys.argv:
        if not os.path.exists(out) or io.open(out, encoding="utf-8").read() != html:
            print("FAIL: report/index.html does not match a rebuild")
            return 1
        print("report --check OK")
        return 0
    os.makedirs(os.path.dirname(out), exist_ok=True)
    io.open(out, "w", encoding="utf-8", newline="\n").write(html)
    print(f"wrote report/index.html  ({len(html):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
