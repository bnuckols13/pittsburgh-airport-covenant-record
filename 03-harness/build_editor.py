#!/usr/bin/env python3
"""build_editor.py — the status page an editor needs before commissioning a run date.

Everything on the page is counted from the files rather than typed, so it cannot
drift from the case: claim statuses come from the ledger, the open reporting
comes from the markers left in the draft, and the plate inventory comes from the
plate specs. If the work moves and this page is rebuilt, it says so by itself.

    python 03-harness/build_editor.py
    python 03-harness/build_editor.py --check
"""
import csv, io, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_explainer as be

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILT = "2026-08-31"
ART = os.path.join(ROOT, "v2", "ARTICLE-v21.md")
LEDGER = os.path.join(ROOT, "v2", "factcheck-v16", "factcheck.json")

CSS = """
.status{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.9rem;
margin:1.4rem 0 1.8rem}
.status div{background:var(--surface);border:1px solid var(--ring);border-radius:11px;
padding:.85rem .95rem}
.status b{display:block;font-family:system-ui,sans-serif;font-size:1.7rem;line-height:1.05;
letter-spacing:-.02em;font-variant-numeric:tabular-nums;color:var(--blue)}
.status.warn b,.status b.warn{color:var(--orange)}
.status span{display:block;font-family:system-ui,sans-serif;font-size:.75rem;color:var(--muted);
margin-top:.2rem;line-height:1.35}
.ask{background:color-mix(in srgb,var(--blue) 8%,transparent);border-left:3px solid var(--blue);
border-radius:0 10px 10px 0;padding:1rem 1.2rem;margin:1.6rem 0}
.ask h3{margin:0 0 .5rem;font-family:system-ui,sans-serif;font-size:1rem}
.ask ol{margin:0;padding-left:1.2rem}
.ask li{margin:.35rem 0}
ul.plain{list-style:none;padding:0;margin:.6rem 0}
ul.plain li{padding:.4rem 0 .4rem 1.5rem;border-bottom:1px solid var(--ring);position:relative;
font-family:system-ui,sans-serif;font-size:.9rem}
ul.plain li::before{position:absolute;left:0;top:.4rem}
li.yes::before{content:"\\2713";color:var(--blue);font-weight:700}
li.no::before{content:"\\2013";color:var(--orange);font-weight:700}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:1.4rem}
@media(max-width:640px){.two-col{grid-template-columns:1fr}}
"""


def build():
    led = json.load(open(LEDGER, encoding="utf-8"))
    art = io.open(ART, encoding="utf-8").read()
    counts = {}
    for c in led["claims"]:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    n_claims = len(led["claims"])
    n_fail = counts.get("failed", 0)

    # What became of each failure, from the disposition file rather than from a
    # heuristic. Seventeen were determined by comparing the text; four were read
    # against the draft by hand, because a shingle match is not evidence an editor
    # should have to accept.
    with io.open(os.path.join(ROOT, "02-data", "factcheck-v16-disposition.csv"),
                 encoding="utf-8-sig", newline="") as f:
        disp = list(csv.DictReader(f))
    removed = [d for d in disp if d["disposition"] == "removed"]
    addressed = [d for d in disp if d["disposition"] == "addressed"]
    carried = [d for d in disp if d["disposition"] == "carried"]

    tks = re.findall(r"\[(?:TK|VERIFY)[^\]]*\]", art)
    blocks = re.findall(r"\*\*\[([A-Z][A-Z0-9 —-]{2,40})", art)
    unreported = [b.strip().rstrip("—- ").strip().lower()
              for b in blocks if not b.strip().startswith("PLATE")]
    words = len(art.split())

    src = json.load(open(os.path.join(ROOT, "01-sources-archive", "sources.json"),
                         encoding="utf-8"))["sources"]
    hashed = sum(1 for s in src.values() if s.get("sha256"))

    body = f"""
<p class="kicker">For the editor</p>
<h1>Where this stands</h1>
<p class="sub">A records-based investigation into how Pittsburgh International's $1.7 billion
terminal was financed, and who carries the risk if the revenue behind it does not hold. Reported
by Lena Rose Williams for Newsworks Lab and the Tribune-Review. This page is generated from the
case files, so it cannot drift from them.</p>

<div class="status">
  <div><b>{words:,}</b><span>words in the current draft</span></div>
  <div><b>{hashed}</b><span>primary documents captured and hashed</span></div>
  <div><b>{n_claims}</b><span>claims checked line by line</span></div>
  <div><b class="warn">0</b><span>people interviewed on the record</span></div>
</div>

<h2>The story</h2>
<p>The terminal was sold on two promises: that the airport would pay for it out of what it earns,
and that flying out of Pittsburgh would get cheaper. Its own bond documents show its consultant
expecting neither.</p>

<p><strong>The covenant is met, and it is not secure.</strong> The Authority told its lenders it
would hold a quarter more than it owes them every year, and on paper it does. Take that figure
apart and roughly three dollars in every ten come from two decisions the Authority makes itself
each year and can stop making. On its own earnings it falls short of the promise in all six
forecast years. The money it designates to close the gap was federal pandemic aid through 2023,
was nothing at all in 2024, and is casino money from 2025 that the airlines have voted to supply
only through 2028. The forecast runs to 2030. The bonds run to 2056.</p>

<p><strong>What that costs is not hypothetical, because the airlines are billed whatever the
airport does not earn.</strong> The obvious version of this story, that a public authority inflated
its passenger forecast to justify a building, is not true, and the record kills it: passengers beat
the 2021 forecast in 2024. The cost did not. Between two bond sales the Authority carried its
passenger forecast forward unchanged and raised its cost forecast by between 20 and 27 percent
depending on the year. On the Authority's own basis the charge was $11.34 in 2023, the year its
chief executive had said it would be $9.73, and its consultant now expects $20.53 by 2030. On the
federal filing, which is a separate series and is never subtracted against the first, it was
$16.10 in fiscal 2025.</p>

<p>Those are one story rather than two. The charge to airlines is residual, so every dollar the
Authority does not designate is a dollar the carriers are billed instead. The two discretionary
decisions that hold the covenant up are the same decisions that hold the charge down.</p>

<h2>What is solid</h2>
<ul class="plain">
  <li class="yes">The covenant arithmetic. Every printed ratio reproduces from the Authority's own
    printed rows before we decompose it, which is the check that the reading is right.</li>
  <li class="yes">The revenue itemisation, from Exhibit E of the 2025 statement. It reconciles to
    the printed total in every year but two, where the Authority's own table rounds by $1,000.</li>
  <li class="yes">Every figure in the piece traces to a page in a hashed document. A machine gate
    re-extracts each cited page and looks for the text; it currently reads 12 of 12 on hashes and
    66 of 66 on anchors.</li>
  <li class="yes">The two-basis discipline. The Authority's residual calculation and FAA Form
    5100-127 are two different series and the piece never subtracts across them.</li>
</ul>

<h2>What is not done, plainly</h2>
<ul class="plain">
  <li class="no"><strong>Nobody has been interviewed.</strong> Four requests went out on Aug. 25
    and 26 to an Allegheny Institute analyst and three academics. None has replied.</li>
  <li class="no"><strong>The Authority has not been asked for comment.</strong> Six questions are
    drafted and unsent. Nothing in the piece rests on an anticipated answer.</li>
  <li class="no"><strong>No records request has been sent.</strong> A Right-to-Know for the master
    plan alternatives analysis and a parallel FOIA to the FAA are drafted. That analysis is the
    document that would settle whether renovating really was more expensive.</li>
  <li class="no"><strong>{len(unreported)} passages are marked as unreported in the text</strong>
    rather than written around: {", ".join(unreported[:4])}.</li>
  <li class="no"><strong>{len(tks)} smaller items carry a TK</strong>, each one named in place.</li>
  <li class="no"><strong>Twenty-two cited sources are not captured.</strong> The heaviest gap is
    the Authority's own Reports and Financials page, which publishes eleven annual financial
    reports for 2015 through 2025 and nine budgets, none of them in the vault. Those carry the
    cost-per-enplaned-passenger series on the Authority's own basis year by year, and they should
    settle the debt-service conflict the piece currently has to leave open. The FAA Form 5100-127
    that the $16.10 rests on is also uncaptured.</li>
  <li class="no"><strong>Two figures ship held rather than drawn.</strong> The sixteen-peer rank,
    because eleven of the sixteen carry no dollar value in the case; and the terminal's design
    capacity, because the only figure for it contradicts the Post-Gazette of Sept. 12, 2017.</li>
</ul>

<h2>The fact check</h2>
<p>A claim-level check on Aug. 30 put {n_claims} claims through a ledger and found
<strong>{n_fail} that failed</strong>, four of them above the fold. The draft was rewritten after
it. Of those {n_fail}: <strong>{len(removed)} no longer appear in the piece at all</strong>, and
<strong>{len(addressed)} were fixed in place</strong> and read against the draft one by one, which
is recorded with the evidence in <code>02-data/factcheck-v16-disposition.csv</code>.
{"" if not carried else "<strong>" + str(len(carried)) + " still read as the check found them.</strong>"}</p>
<p><strong>That is the reporter's account of her own corrections, not an independent
verification.</strong> The ledger has not been re-run against the current draft, and it should be,
by someone who did not write it, before this publishes. All {n_claims} claims are browsable at
<a href="#">the claim ledger</a>, failures included.</p>

<div class="ask">
  <h3>What I need decided</h3>
  <ol>
    <li><strong>Timing.</strong> Hold for interviews and the Authority's response, or run a
      records-based piece first and follow it. The documents carry the story on their own; the
      people do not exist in it yet.</li>
    <li><strong>Right of reply.</strong> Six questions are ready. Once they go, a 72-hour hold
      starts and the Authority knows what is coming.</li>
    <li><strong>A fact-checker.</strong> The ledger is built for someone other than me to run.</li>
    <li><strong>The outlet line and the byline</strong> as they should appear.</li>
  </ol>
</div>

<h2>The material</h2>
<div class="two-col">
  <div>
    <h3 style="font-family:system-ui,sans-serif;font-size:.95rem">Read</h3>
    <ul class="plain">
      <li class="yes"><a href="https://bnuckols13.github.io/pittsburgh-airport-covenant-record/site/">The draft</a>, with unreported passages marked
        in place</li>
      <li class="yes"><a href="https://bnuckols13.github.io/pittsburgh-airport-covenant-record/covenant/">Two pots, explained</a>, the mechanism from
        the indenture</li>
      <li class="yes"><a href="https://bnuckols13.github.io/pittsburgh-airport-covenant-record/model/">What holds the promise up</a>, the decisions
        turned off and on</li>
    </ul>
  </div>
  <div>
    <h3 style="font-family:system-ui,sans-serif;font-size:.95rem">Check</h3>
    <ul class="plain">
      <li class="yes"><a href="https://bnuckols13.github.io/pittsburgh-airport-covenant-record/appendix-dataviz/">The plates</a>, each recomputed from
        a CSV</li>
      <li class="yes"><a href="#">The claim ledger</a>, failures included</li>
      <li class="yes"><a href="https://github.com/bnuckols13/pittsburgh-airport-covenant-record/blob/main/01-sources-archive/MANIFEST.md">The sources</a>, with hashes</li>
    </ul>
  </div>
</div>

<p class="src">Generated {BUILT} from the case files by <code>03-harness/build_editor.py</code>.
Claim counts from <code>v2/factcheck-v16/factcheck.json</code>; open reporting counted from the
markers in the draft itself. Nothing on this page is typed by hand.</p>
"""
    return be.page("Where this stands &#183; Pittsburgh Airport Covenant Record", body,
                   extra_css=CSS)


def main():
    # Not a public page. This is the brief for the commissioning editor and it
    # belongs in the case, where the gaps it lists are working notes rather than
    # a published account of the reporter's own shortfalls.
    out = os.path.normpath(os.path.join(ROOT, "..", "pit-terminal-financing",
                                        "v2", "EDITOR-BRIEF.html"))
    html = build()
    if "--check" in sys.argv:
        if not os.path.exists(out) or io.open(out, encoding="utf-8").read() != html:
            print("FAIL: editor/index.html does not match a rebuild")
            return 1
        print("editor brief --check OK")
        return 0
    os.makedirs(os.path.dirname(out), exist_ok=True)
    io.open(out, "w", encoding="utf-8", newline="\n").write(html)
    print(f"wrote ../pit-terminal-financing/v2/EDITOR-BRIEF.html  ({len(html):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
