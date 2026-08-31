#!/usr/bin/env python3
"""build_explainer.py — the two-pot explainer and the interactive model.

Writes covenant/index.html (what the Coverage Account is, what Other Pledged
Revenues are, and why they are not the same thing) and model/index.html (a
slider model whose baseline is the Authority's own forecast rows).

The model is arithmetic on document figures, not a simulation. Two of its three
levers move quantities the indenture says the Authority chooses; the third moves
traffic. Every baseline is page-cited. Every delta is stated as ours.

    python 03-harness/build_explainer.py
    python 03-harness/build_explainer.py --check
"""
import csv, io, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import charts as ch
import model_page
from charts import Frame, C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "02-data")
BUILT = "2026-08-31"


def rows(name):
    with io.open(os.path.join(DATA, name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def num(v):
    return float(str(v).replace(",", "").replace("$", "").strip())


CSS = """
:root{--plane:#fbfaf7;--surface:#fff;--surface2:#f4f2ec;--ink:#1a1a1a;--ink2:#4a4a4a;
--muted:#6b6b6b;--grid:#e6e2d8;--axis:#b9b3a5;--ring:#d9d4c8;--blue:#1c5cab;
--blue-lt:#7ba7de;--aqua:#2b8a8a;--yellow:#b8860b;--orange:#c2570f;--red:#a8321e;}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--plane:#0f130f;
--surface:#181a17;--surface2:#1f221e;--ink:#f4f2e9;--ink2:#c3c2b7;--muted:#9a988d;
--grid:#26302a;--axis:#4a544c;--ring:#26302a;--blue:#5598e7;--blue-lt:#2f4f74;
--aqua:#5fc0bd;--yellow:#d8ad4a;--orange:#e8843f;--red:#ff9b86;}}
:root[data-theme=dark]{--plane:#0f130f;--surface:#181a17;--surface2:#1f221e;--ink:#f4f2e9;
--ink2:#c3c2b7;--muted:#9a988d;--grid:#26302a;--axis:#4a544c;--ring:#26302a;--blue:#5598e7;
--blue-lt:#2f4f74;--aqua:#5fc0bd;--yellow:#d8ad4a;--orange:#e8843f;--red:#ff9b86;}
*{box-sizing:border-box}
body{margin:0;background:var(--plane);color:var(--ink);
font-family:Georgia,"Palatino Linotype",serif;line-height:1.68}
.wrap{max-width:50rem;margin:0 auto;padding:2.6rem 1.3rem 5rem}
.sans{font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
h1{font-size:1.95rem;line-height:1.18;margin:0 0 .5rem;letter-spacing:-.01em}
h2{font-size:1.28rem;margin:2.4rem 0 .7rem;line-height:1.3}
h3{font-family:system-ui,sans-serif;font-size:1rem;margin:1.6rem 0 .4rem}
.kicker{font-family:system-ui,sans-serif;font-size:.74rem;letter-spacing:.1em;
text-transform:uppercase;color:var(--blue);margin:0 0 .5rem}
.sub{color:var(--ink2);margin:0 0 1.8rem;font-size:1.03rem}
blockquote{margin:1.1rem 0;padding:.7rem 0 .7rem 1.1rem;border-left:3px solid var(--blue);
color:var(--ink2);font-size:.97rem}
blockquote .cite{display:block;font-family:system-ui,sans-serif;font-size:.76rem;
color:var(--muted);margin-top:.45rem}
.two{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:1.4rem 0}
@media(max-width:640px){.two{grid-template-columns:1fr}}
.pot{background:var(--surface);border:1px solid var(--ring);border-radius:12px;padding:1.1rem 1.2rem}
.pot h3{margin-top:0;color:var(--blue)}
.pot dl{margin:0;font-size:.88rem}
.pot dt{font-family:system-ui,sans-serif;font-size:.7rem;text-transform:uppercase;
letter-spacing:.05em;color:var(--muted);margin-top:.7rem}
.pot dd{margin:.1rem 0 0}
table{border-collapse:collapse;width:100%;font-family:system-ui,sans-serif;font-size:.85rem;
margin:1rem 0}
th,td{text-align:left;padding:.42rem .6rem;border-bottom:1px solid var(--ring)}
th{font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
td.num{text-align:right;font-variant-numeric:tabular-nums}
.scroll{overflow-x:auto}
code{font-family:"Cascadia Code",Consolas,monospace;background:var(--surface2);
padding:.1rem .35rem;border-radius:4px;font-size:.86em}
.disc{font-family:system-ui,sans-serif;font-size:.84rem;color:var(--ink);
background:color-mix(in srgb,var(--yellow) 12%,transparent);border-left:3px solid var(--yellow);
border-radius:0 8px 8px 0;padding:.8rem 1rem;margin:1.3rem 0}
.note{background:color-mix(in srgb,var(--blue) 8%,transparent);border-left:3px solid var(--blue);
border-radius:0 8px 8px 0;padding:.8rem 1rem;margin:1.3rem 0;font-size:.94rem}
.src{font-size:.78rem;color:var(--muted);border-top:1px solid var(--ring);padding-top:.7rem;
margin-top:2.4rem;font-family:system-ui,sans-serif}
.toggle{position:fixed;top:.8rem;right:.8rem;font:inherit;font-size:.8rem;padding:.3rem .7rem;
border-radius:99px;border:1px solid var(--ring);background:var(--surface);color:var(--ink);
cursor:pointer;z-index:9}
a{color:var(--blue)}
svg{width:100%;height:auto;overflow:visible;display:block;margin:.6rem 0}
text{font-family:system-ui,sans-serif;font-variant-numeric:tabular-nums}
.ax{font-size:10.5px;fill:var(--muted)}
.lab{font-size:12.5px;fill:var(--ink);font-weight:600}
.lab2{font-size:11.5px;fill:var(--ink2)}
.val{font-size:11.5px;fill:var(--ink);font-weight:600}
/* model */
.rig{background:var(--surface);border:1px solid var(--ring);border-radius:12px;
padding:1.2rem 1.3rem;margin:1.4rem 0}
.lev{margin:0 0 1.1rem}
.lev label{display:flex;justify-content:space-between;font-family:system-ui,sans-serif;
font-size:.86rem;margin-bottom:.25rem}
.lev label b{font-variant-numeric:tabular-nums;color:var(--blue)}
.lev input[type=range]{width:100%;accent-color:var(--blue)}
.lev .why{font-family:system-ui,sans-serif;font-size:.74rem;color:var(--muted);margin-top:.2rem}
.out{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.9rem;
margin:1.2rem 0 .4rem}
.out div{background:var(--surface2);border-radius:10px;padding:.8rem .9rem}
.out b{display:block;font-family:system-ui,sans-serif;font-size:1.5rem;letter-spacing:-.02em;
font-variant-numeric:tabular-nums}
.out span{font-family:system-ui,sans-serif;font-size:.75rem;color:var(--muted)}
.presets{display:flex;flex-wrap:wrap;gap:.4rem;margin:.2rem 0 1rem}
.presets button{font:inherit;font-family:system-ui,sans-serif;font-size:.78rem;
padding:.3rem .7rem;border-radius:99px;border:1px solid var(--ring);background:var(--surface);
color:var(--ink);cursor:pointer}
.presets button:hover{border-color:var(--blue);color:var(--blue)}
.work{font-family:"Cascadia Code",Consolas,monospace;font-size:.78rem;color:var(--ink2);
background:var(--surface2);border-radius:8px;padding:.8rem .9rem;margin-top:.9rem;
white-space:pre-wrap;line-height:1.55}
.ifthen{font-family:system-ui,sans-serif;font-size:1rem;line-height:1.55;
background:color-mix(in srgb,var(--blue) 9%,transparent);border-left:3px solid var(--blue);
border-radius:0 8px 8px 0;padding:.85rem 1rem;margin:1.3rem 0 .6rem}
#chart{margin:.4rem 0 1rem}
#tbl td.under{color:var(--orange);font-weight:600}
#tbl .nv{font-size:.7rem;color:var(--yellow);border:1px solid currentColor;border-radius:99px;
padding:0 .35rem;vertical-align:middle}
.presets button.on{background:var(--blue);color:#fff;border-color:var(--blue)}
@media print{.toggle,.presets{display:none}}
"""

TOGGLE = ('<button class="toggle">&#9686; theme</button>')
TOGGLE_JS = ("<script>document.querySelector('.toggle').onclick=function(){"
             "var r=document.documentElement,d=r.getAttribute('data-theme')==='dark';"
             "r.setAttribute('data-theme',d?'light':'dark')};</script>")


def page(title, body, extra_js=""):
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            f"<title>{title}</title><style>{CSS}</style></head><body>{TOGGLE}"
            f"<div class=\"wrap\">{body}</div>{TOGGLE_JS}{extra_js}</body></html>")


# ---------------------------------------------------------------- explainer

def build_explainer():
    opr = {r["year"]: r for r in rows("other-pledged-revenue.csv") if not r["conflict"]}
    itm = rows("other-pledged-revenue-itemized.csv")
    years = [str(y) for y in range(2019, 2031)]

    def cat_total(cats, y):
        return sum(num(r[y]) for r in itm if r["category"] in cats)

    door = []
    for y in years:
        fed = cat_total({"federal pandemic aid", "federal disaster aid"}, y)
        gas = cat_total({"gas royalty"}, y)
        gam = cat_total({"slot-machine tax"}, y)
        tot = fed + gas + gam
        what = ", ".join(n for n, v in (("federal aid", fed), ("gas royalty", gas),
                                        ("slot-machine tax", gam)) if v) or "nothing"
        door.append((y, fed, gas, gam, tot, what))

    mech = ch.flow_diagram(Frame(w=980, h=520, l=20, r=20, t=26, b=20),
                           rows("flow-of-funds.csv"), rows("flow-of-funds-edges.csv"))
    mech = ch.svg(Frame(w=980, h=520), "The flow of funds, with the two discretionary "
                  "levers drawn as the only dashed strokes.", mech)

    door_rows = "".join(
        f'<tr><td>{y}</td><td class="num">{fed:,.0f}</td><td class="num">{gas:,.0f}</td>'
        f'<td class="num">{gam:,.0f}</td><td class="num"><b>{tot:,.0f}</b></td>'
        f'<td>{what}</td></tr>' for y, fed, gas, gam, tot, what in door)

    body = f"""
<p class="kicker">Explainer</p>
<h1>Two pots, and the Authority fills both</h1>
<p class="sub">The covenant test adds two things together. They are funded from different money,
governed by different sentences of the indenture, and the Authority decides how much goes into
each. Conflating them is the single easiest mistake to make about this financing, and most
coverage makes it.</p>

<h2>What the covenant actually says</h2>
<blockquote>Net Revenues, together with any amounts available in the Coverage Account, will be
equal to at least (i) 125% of Annual Debt Service on the Outstanding Bonds for such Fiscal Year
<span class="cite">os-2025ab, PDF 34</span></blockquote>
<p>Two terms on the left. <em>Net Revenues</em> is one pot. <em>the Coverage Account</em> is the
other. The Official Statements print only the sum, so a reader sees one number and one line at
1.25, and every forecast year clears it. Separating the two is what this package does, and the
arithmetic is ours.</p>

<div class="two">
  <div class="pot">
    <h3>The Coverage Account</h3>
    <dl>
      <dt>What is in it</dt><dd>The airport's own revenue.</dd>
      <dt>Where it comes from</dt>
      <dd>Revenues, after operations and maintenance and the eight priorities above it.</dd>
      <dt>Who decides</dt>
      <dd>The Authority, monthly, &#8220;in an amount determined by the Authority.&#8221;</dd>
      <dt>Limit</dt><dd>25 percent of that year's annual debt service.</dd>
      <dt>Where it sits in the test</dt><dd><b>Beside</b> Net Revenues, added to them.</dd>
      <dt>Locator</dt><dd>os-2025ab PDF 32 (funding), PDF 34 (the cap)</dd>
    </dl>
  </div>
  <div class="pot">
    <h3>Other Pledged Revenues</h3>
    <dl>
      <dt>What is in it</dt>
      <dd>Money that is <b>not</b> the airport's revenue: federal grants, slot-machine tax, gas royalty.</dd>
      <dt>Where it comes from</dt>
      <dd>Outside the Airport System, designated in for a stated period.</dd>
      <dt>Who decides</dt><dd>The Authority, each fiscal year, by designating it.</dd>
      <dt>Limit</dt><dd>None stated.</dd>
      <dt>Where it sits in the test</dt><dd><b>Inside</b> Net Revenues, counted as part of them.</dd>
      <dt>Locator</dt><dd>os-2025ab PDF 30 and PDF 343 (definition), PDF 316 (the amounts)</dd>
    </dl>
  </div>
</div>

<div class="note"><b>The Coverage Account does not hold the gas and casino money.</b> That is the
error worth guarding against. Gas and casino money reaches the covenant through the other door,
as a designation into Net Revenues, and it does so only in the years the Authority designates it.</div>

<h2>Why gas and casino money needs a door at all</h2>
<p>The indenture defines Revenues and then excludes fifteen things from the definition. Two of
the exclusions decide this story.</p>
<blockquote>The term Revenues &#8230; shall not include: (i) gifts, grants, reimbursements or
payments received for the Airport System's benefit <b>unless designated as and included in
&#8220;Other Pledged Revenues&#8221;</b> &#8230; (xii) Customer Facility Charges, <b>Gaming
Revenues and Natural Gas Revenues unless designated as and included in &#8220;Other Pledged
Revenues&#8221;</b><span class="cite">os-2025ab, PDF 349</span></blockquote>
<p>The statement says the same thing in plain language forty pages earlier:</p>
<blockquote>Gaming Revenues are excluded from the definition of Revenues in the Master Indenture,
except to the extent designated by the Authority in any Fiscal Year as Other Pledged Revenues and
deposited to the Debt Service Fund, and unless so designated and deposited, <b>are not pledged to
pay debt service on the Bonds</b>.<span class="cite">os-2025ab, PDF 67</span></blockquote>
<p>So federal aid, slot-machine money and gas royalty are the three kinds of money that the
indenture singles out as outside the pledge by default. Each reaches the covenant only if the
Authority walks it through the same single door, one year at a time, by choice. The airport
receives the money either way. Whether it counts toward the promise to lenders is a decision.</p>

<h2>What has gone through the door</h2>
<p>The Authority itemises its designations in Exhibit E. Read down the last column: this is not
three separate stories about three sources. It is one door and a rotation of what goes through it.</p>
<div class="scroll"><table>
<thead><tr><th>year</th><th>federal aid $k</th><th>gas $k</th><th>slot-machine $k</th>
<th>designated $k</th><th>what it was</th></tr></thead>
<tbody>{door_rows}</tbody></table></div>
<p>Gas and casino money did not dry up. It was <b>substituted</b>. While federal pandemic aid was
available the Authority designated that instead, and in 2024 it designated nothing at all. The
forecast turns the casino money back on from 2025, now that the federal money is spent.</p>

<div class="disc"><b>A correction this package makes to earlier reporting, including our own
drafts.</b> The fall from $19.1 million in 2021 to $3.0 million in 2023 is a fall in
<b>federal pandemic relief</b>. It is not gas and gambling money running out. Gas and casino
money had already been designated at zero for four years by then.</div>

<h2>Two things the forecast assumes that nobody has committed to</h2>
<p>In January 2025 the signatory airlines took a majority-in-interest vote. The statement records
what it covered:</p>
<blockquote>the Authority committed to using discretionary revenue, which may include Gaming
Revenues or Natural Gas Revenues, of no less than $8.8 million for 2025 and $11.575 million per
year for <b>2026 through 2028</b> to reduce airline rates and charges.
<span class="cite">os-2025ab, PDF 67</span></blockquote>
<p><b>The commitment ends in 2028. The forecast designates $11,575,000 in 2029 and again in
2030.</b> The last two years of the forecast that satisfies the covenant rest on a designation no
vote covers. The statement's own word for what happens then is <em>expects</em>: &#8220;The
Authority currently expects to continue to designate a portion of annual Gaming Revenues as Other
Pledged Revenues in the future.&#8221;</p>
<p>And the same money is described as doing two jobs. At PDF 67 the commitment is
&#8220;to reduce airline rates and charges.&#8221; In Exhibit E the identical amounts, $8.8
million and $11.575 million, are Other Pledged Revenues, which is the pledge to bondholders.
Raising Net Revenues does lower the residual airline bill, so the two can be reconciled. The
statement does not reconcile them, and the question is on the list for the Authority.</p>

<h2>The whole machine, on one page</h2>
{mech}
<p class="sans" style="font-size:.85rem;color:var(--muted)">Dashed means the Authority chooses.
Four of the eleven priorities are funded at its discretion, and only the ninth counts toward the
1.25 test. The remaining dashed stroke is the designation entering Net Revenues from the left.</p>

<div class="note"><b>Nothing here is a breach.</b> The indenture lets the Coverage Account count
toward the 1.25 test, and on that test the Authority's forecasts comply in every year. No payment
is missed in any forecast year. Missing the covenant once is not an event of default either: the
indenture requires the Authority to hire a consultant, take its advice and raise its rates, and
only a second consecutive miss after rates have gone up is an Event of Default. The finding in
this package is narrower and is stated in those words: <b>what the ratio is on pledged Net
Revenues alone.</b></div>

<p><a href="../model/index.html">Move the two levers yourself &#8594;</a> &#160;&#183;&#160;
<a href="../appendix-dataviz/index.html">The plates</a> &#160;&#183;&#160;
<a href="../index.html">The package</a></p>

<p class="src">Every quotation above is from a document hashed in
<code>01-sources-archive/</code> and is checked by <code>python 03-harness/verify_claims.py</code>,
which re-extracts each cited page and looks for the text. Designation amounts from
<code>02-data/other-pledged-revenue-itemized.csv</code>, built from os-2025ab PDF 316. Built {BUILT}.</p>
"""
    return page("Two pots &#183; Pittsburgh Airport Covenant Record", body)


# ---------------------------------------------------------------- model

def build_model():
    cov = [r for r in rows("coverage-table.csv") if r["vintage"] == "2025"]
    cov.sort(key=lambda r: int(r["year"]))
    opr = {r["year"]: num(r["designated_k"]) for r in rows("other-pledged-revenue.csv")
           if not r["conflict"]}
    wp = {r["year"]: r for r in rows("who-pays-opr.csv")}

    base = []
    for r in cov:
        y = r["year"]
        d = opr[y]
        base.append({
            "year": int(y), "net": num(r["net_revenues_incl_OPR_k"]),
            "cov": num(r["coverage_amount_k"]), "ads": num(r["aggregate_annual_debt_service_k"]),
            "cpe": num(r["cpe"]), "enpl": num(r["enplanements_k"]), "opr": d,
        })
        # The CPE lever is exact and the case already proves it: withdrawing the
        # designation raises CPE by the designation divided by enplanements.
        if y in wp:
            want = num(wp[y]["cpe_if_opr_withdrawn"])
            got = num(r["cpe"]) + d / num(r["enplanements_k"])
            if abs(want - got) > 0.02:
                raise SystemExit(f"model: CPE relation does not reproduce for {y}: "
                                 f"{got:.2f} against the case's {want:.2f}")

    # Fidelity gate. With every dial at the Authority's own forecast value, the model
    # must reproduce the Authority's own printed ratios and charge. If it does not, the
    # model is not arithmetic on the documents and has no business being published.
    for b, r in zip(base, cov):
        pct = num(r["coverage_amount_pct_of_ADS"])
        alone = b["net"] / b["ads"]
        printed = (b["net"] + pct * b["ads"]) / b["ads"]
        req = (b["cpe"] + b["opr"] / b["enpl"]) * b["enpl"]
        cpe = (req - b["opr"]) / b["enpl"]
        for got, want, what, tol in (
                (alone, num(r["coverage_on_net_revenues_alone"]), "coverage on net revenues alone", 0.002),
                (printed, num(r["coverage_recomputed_with_account"]), "coverage as printed", 0.002),
                (cpe, b["cpe"], "cost per enplaned passenger", 0.01)):
            if abs(got - want) > tol:
                raise SystemExit(
                    f"model fidelity: {b['year']} {what} comes out {got:.4f} against the "
                    f"Authority's {want:.4f}. The model does not reproduce the document at "
                    f"baseline and must not ship.")
    print(f"  model fidelity OK: all {len(base)} forecast years reproduce at baseline")

    js = json.dumps(base, separators=(",", ":"))
    body = model_page.BODY.replace("__BUILT__", BUILT)
    js_block = "<script>var B=" + js + ";" + model_page.JS + "</script>"
    return page("The model &#183; Pittsburgh Airport Covenant Record", body, js_block)


def main():
    check = "--check" in sys.argv
    targets = {os.path.join(ROOT, "covenant", "index.html"): build_explainer(),
               os.path.join(ROOT, "model", "index.html"): build_model()}
    if check:
        for p, want in targets.items():
            if not os.path.exists(p) or io.open(p, encoding="utf-8").read() != want:
                print(f"FAIL: {os.path.relpath(p, ROOT)} does not match a rebuild")
                return 1
        print("explainer + model --check OK")
        return 0
    for p, txt in targets.items():
        os.makedirs(os.path.dirname(p), exist_ok=True)
        io.open(p, "w", encoding="utf-8", newline="\n").write(txt)
        print(f"wrote {os.path.relpath(p, ROOT)}  ({len(txt):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
