"""model_page.py — the markup, styling and behaviour of the interactive model.

Design intent, written down because several earlier attempts were wrong in
instructive ways.

The first three showed the reader a coverage ratio and nothing else: 1.12 against
a covenant of 1.25, as a line, then as a dumbbell. Accurate, and illuminating
nothing, because a ratio of 1.12 means little to a person who does not price
municipal bonds for a living. The fourth answered that by drawing dollars instead
and refusing to print a ratio anywhere. That went too far the other way: the
story this page belongs to is built on two six-year rows of ratios, and a reader
arriving from that passage could not find the numbers they came for.

So the page now carries both, on one switch, over the same six years and the same
controls. Dollars are the unit a reader already owns; ratios are the unit the
document prints and the covenant is written in. Neither is the "real" one.

The second thing those attempts got wrong is subtler. The page explained. It
opened with a hundred words of prose, put four preset cards and a verdict
paragraph above the instrument, wrapped every control in sixty words of caption,
and closed by assuring the reader that the build gate would refuse to publish an
unfaithful page. All true, all the writer talking, and none of it something the
reader could do anything with. A model that only explains is a worse essay.

This one is a test. The Authority promised its lenders 1.25 times annual debt
service. Three things stack up to meet it and only the first is money the airport
earns:

  what the airport earns    Net Revenues less anything designated in. The
                            indenture is explicit that designated money is
                            "not constituting Revenues", so this really is the
                            airport's own operating result.
  money designated in       Other Pledged Revenues: federal relief, then casino
                            money. Chosen each year, or not, as in 2024.
  the Coverage Account      A reserve funded monthly at the Authority's
                            discretion and capped at 25 percent of debt service.

The reader can switch off either of the last two and watch what happens. Turn off
both and six of six years fall below 1.25. That is the finding, and discovering it
by trying beats being told it in a verdict paragraph.

Three rules the layout has to obey, each of them a bug the last version had:

1. The controls and the thing they control must be visible at the same time, at
   every width. The previous version made .chartwrap sticky inside .results while
   every control lived in .panel, a sibling. A sticky element's travel is bounded
   by its containing block, so on a phone the chart unstuck twenty-two pixels
   before the first control appeared. Here the sticky element is .instrument and
   its parent is .layout, which contains the panel too, so the travel covers the
   whole control stack.
2. The instrument is above the fold. Kicker, headline, one sentence, then it.
3. A control states its value as a number and shows where the document's own
   value sits. "as forecast" with no figure and no baseline tick tells a reader
   nothing about what they just did.

Sub-1.25 reads as failure in four places at once: the count, the year chips, the
tinted zone under the covenant line, and the colour of the marks themselves.

The discipline that makes it publishable lives in build_explainer.py: at the
Authority's own values the model must reproduce all three of its printed ratio
series and its charge per boarded passenger, or the build refuses to write the
page.
"""

CSS = """
/* --ok, --warn, --flag and --accent-soft are referenced by this page but defined
   in none of build_explainer.CSS's three token blocks, where they resolved to
   nothing. Defined here rather than there because extra_css is per-page and the
   other eight pages that share build_explainer.CSS each carry their own byte-exact
   --check. The values are the ones build_front.py already ships, so failure reads
   the same colour here as on the front door. */
:root{--flag:#a8321e;--ok:#1d6b3f;--warn:#b8600b;
--accent-soft:rgba(28,92,171,.08)}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
--flag:#ff9b86;--ok:#7fd3a1;--warn:#e8973f;--accent-soft:rgba(85,152,231,.14)}}
:root[data-theme=dark]{--flag:#ff9b86;--ok:#7fd3a1;--warn:#e8973f;
--accent-soft:rgba(85,152,231,.14)}

.wrap{max-width:64rem}
/* The shared sheet fixes the theme button to the top right, which on this page sits
   permanently on top of a sticky scoreboard. Moved to the bottom on the model page
   only, where nothing is pinned. */
.toggle{top:auto;bottom:.9rem;opacity:.85;font-size:.72rem;padding:.25rem .55rem}
.toggle:hover{opacity:1}
.kicker{font-family:system-ui,sans-serif;font-size:.72rem;letter-spacing:.14em;
text-transform:uppercase;color:var(--blue);font-weight:600;margin:0 0 .4rem}
h1{font-size:2.4rem;line-height:1.06;letter-spacing:-.025em;margin:0 0 .5rem}
.sub{font-size:1.05rem;color:var(--ink2);max-width:42rem;margin:0 0 1.1rem}

/* ---- the instrument: sticky, and its parent contains the controls ---- */
.instrument{position:sticky;top:0;z-index:3;background:var(--plane);
padding:.5rem 0 .7rem}

/* ---- scoreboard ---- */
.score{border-top:2px solid var(--ink);padding-top:.7rem}
.counts{display:flex;flex-wrap:wrap;gap:.35rem 1.4rem;font-family:system-ui,sans-serif;
font-size:.95rem;line-height:1.35;margin:0 0 .6rem}
.counts div{display:flex;align-items:baseline;gap:.4rem}
/* nowrap, because "5 of 6" broke across two lines as "5 of" and "6". */
.counts b{font-size:1.25rem;font-weight:600;letter-spacing:-.02em;white-space:nowrap;
font-variant-numeric:tabular-nums;color:var(--ok)}
.counts b.bad{color:var(--flag)}
.counts span{color:var(--ink2);font-size:.83rem;max-width:22rem}
.chips{display:flex;gap:1px;background:var(--ring);border:1px solid var(--ring);
border-radius:9px;overflow:hidden}
.chip{flex:1 1 0;min-width:0;background:var(--surface);padding:.4rem .3rem .45rem;
font-family:system-ui,sans-serif;text-align:center;cursor:pointer;border:0;
color:var(--ink);transition:background .12s}
.chip:hover{background:var(--accent-soft)}
.chip .yr{display:block;font-size:.7rem;color:var(--muted);letter-spacing:.03em}
.chip .vl{display:block;font-size:1rem;font-weight:600;font-variant-numeric:tabular-nums;
letter-spacing:-.01em;line-height:1.2;color:var(--ok)}
.chip .st{display:block;font-size:.6rem;letter-spacing:.09em;text-transform:uppercase;
color:var(--ok);font-weight:600}
.chip.bad .vl,.chip.bad .st{color:var(--flag)}
.chip.on{background:var(--accent-soft);box-shadow:inset 0 -2px 0 var(--blue)}
.chip.on .yr{color:var(--ink);font-weight:600}

/* ---- chart ---- */
.chead{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;
gap:.5rem;margin:.8rem 0 .1rem}
.chead .ct{font-family:system-ui,sans-serif;font-size:.75rem;color:var(--muted);
letter-spacing:.03em}
.seg{display:inline-flex;border:1px solid var(--ring);border-radius:8px;overflow:hidden;
background:var(--surface)}
.seg button{font:inherit;font-family:system-ui,sans-serif;font-size:.78rem;
padding:.3rem .7rem;border:0;background:transparent;color:var(--ink2);cursor:pointer;
transition:background .12s,color .12s}
.seg button+button{border-left:1px solid var(--ring)}
.seg button[aria-pressed=true]{background:var(--blue);color:#fff;font-weight:600}
/* The viewBox is measured, not fixed. A fixed 640-unit box inside a 333px phone
   column scaled every 11.5px label down to about 6px, which the ratio view cannot
   survive: six two-decimal numbers is the whole readout. One user unit is now one
   CSS pixel at every width, so the stated sizes are the delivered sizes. */
.chartwrap{margin:0}
#chart{width:100%;height:auto;display:block;overflow:visible}
#chart text{font-family:system-ui,sans-serif}
#chart .ax{font-size:11.5px;fill:var(--muted)}
#chart .val{font-size:12px;font-weight:600}
#chart .lg{font-size:11.5px;fill:var(--ink2)}
#chart .yrlab{font-size:12px;fill:var(--ink2)}
#chart .yrlab.bad{fill:var(--flag);font-weight:600}
#chart .refl{font-size:10.5px;fill:var(--muted)}
/* Geometry attributes on SVG are animatable in CSS, so marks keep their identity
   across a state change and move to the new value instead of being destroyed and
   rebuilt. Seeing what moved is most of the comprehension. */
#chart rect.seg,#chart line.ref,#chart line.gap,#chart text.val,#chart circle.pt,
#chart line.spine{
transition:x .38s cubic-bezier(.4,0,.2,1),y .38s cubic-bezier(.4,0,.2,1),
height .38s cubic-bezier(.4,0,.2,1),y1 .38s cubic-bezier(.4,0,.2,1),
y2 .38s cubic-bezier(.4,0,.2,1),cy .38s cubic-bezier(.4,0,.2,1),
fill .25s,stroke .25s,opacity .25s}
@media (prefers-reduced-motion:reduce){#chart *{transition:none!important}}
#chart .hit{cursor:pointer;fill:transparent}
#chart g.on .focusbox{opacity:1}
#chart .focusbox{opacity:0;fill:none;stroke:var(--blue);stroke-width:1.4;
stroke-dasharray:3 2;transition:opacity .2s}
.reading{font-family:system-ui,sans-serif;font-size:.88rem;color:var(--ink2);
line-height:1.5;margin:.45rem 0 0;max-width:46rem}
.reading em{font-style:normal;font-weight:600;color:var(--ink);
font-variant-numeric:tabular-nums}
.reading em.bad{color:var(--flag)}

/* ---- layout. .instrument and .panel are siblings under .layout, which is what
   lets the sticky instrument travel the length of the controls.

   Written mobile-first with exactly one query. The previous version paired
   min-width:64rem with max-width:64rem, and because both are inclusive both fired
   at exactly 1024px, giving the page two nested sticky contexts at that width. One
   query cannot overlap itself. ---- */
.layout{display:block}
.instrument{box-shadow:0 6px 14px -12px rgba(0,0,0,.5)}
.counts b{font-size:1.1rem}
.chip .vl{font-size:.92rem}
@media(min-width:64rem){
  .layout{display:grid;grid-template-columns:minmax(0,1fr) 21.5rem;gap:1.8rem;
  align-items:start}
  .instrument{top:1rem;box-shadow:none}
  .panel{margin-top:0}
  .levs{grid-template-columns:1fr;gap:1.05rem}
  .switches{grid-template-columns:1fr;gap:.55rem}
  .scen{grid-template-columns:1fr;gap:.4rem}
  .counts b{font-size:1.25rem}
  .chip .vl{font-size:1rem}
}

/* ---- controls ---- */
.panel{border:1px solid var(--ring);border-radius:13px;background:var(--surface);
padding:1.1rem 1.2rem;margin:1.2rem 0}
.panel h2{font-family:system-ui,sans-serif;font-size:.72rem;letter-spacing:.14em;
text-transform:uppercase;color:var(--muted);margin:1.3rem 0 .7rem;font-weight:600}
.panel h2:first-child{margin-top:0}
.scen{display:grid;grid-template-columns:repeat(auto-fit,minmax(13rem,1fr));gap:.4rem;
margin:0}
.scen button{text-align:left;font:inherit;font-family:system-ui,sans-serif;cursor:pointer;
background:var(--plane);border:1px solid var(--ring);border-radius:9px;
padding:.5rem .65rem;color:var(--ink);transition:border-color .12s,background .12s}
.scen button:hover{border-color:var(--blue)}
.scen button strong{display:block;font-size:.84rem;font-weight:600;line-height:1.3}
.scen button span{display:block;font-size:.73rem;color:var(--muted);line-height:1.35;
margin-top:.1rem}
.scen button.on{border-color:var(--blue);box-shadow:inset 0 0 0 1px var(--blue);
background:var(--accent-soft)}
.scen button.on strong{color:var(--blue)}

.switches{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:.55rem}
.sw{display:flex;gap:.6rem;align-items:flex-start;font-family:system-ui,sans-serif;
font-size:.83rem;line-height:1.45;cursor:pointer;padding:.55rem .7rem;border-radius:9px;
border:1px solid var(--ring);background:var(--plane);transition:opacity .12s,border-color .12s}
.sw input{margin-top:.18rem;accent-color:var(--blue);width:1rem;height:1rem;flex:none}
.sw strong{display:block;font-size:.86rem;margin-bottom:.05rem}
.sw span span{color:var(--muted);font-size:.77rem}
.sw.off{opacity:.55;border-style:dashed}
.why{font-size:.75rem;color:var(--muted);line-height:1.45;margin-top:.5rem}
.why a{color:var(--blue)}

.levs{display:grid;grid-template-columns:repeat(auto-fit,minmax(16rem,1fr));gap:1.1rem 1.5rem}
.lev{font-family:system-ui,sans-serif}
.lev label{display:flex;justify-content:space-between;align-items:baseline;gap:.6rem;
font-size:.85rem;margin-bottom:.25rem}
.lev label b{font-weight:600;color:var(--blue);font-variant-numeric:tabular-nums;
white-space:nowrap}
/* The baseline tick marks where the Authority's own value sits on the track, so a
   reader can see at a glance how far from the document they have moved. */
.track{position:relative;padding-bottom:.55rem}
.track input[type=range]{width:100%;accent-color:var(--blue);cursor:pointer;margin:0;
display:block}
.track .tick{position:absolute;bottom:.1rem;transform:translateX(-50%);font-size:.6rem;
color:var(--muted);letter-spacing:.04em;white-space:nowrap;pointer-events:none}
.track .tick::before{content:"";position:absolute;left:50%;bottom:100%;width:1px;
height:.3rem;background:var(--axis)}
.readout{font-size:.76rem;color:var(--ink2);font-variant-numeric:tabular-nums;
margin-top:.15rem}
.readout b{color:var(--ink);font-weight:600}
.charge{font-family:system-ui,sans-serif;display:flex;flex-wrap:wrap;align-items:baseline;
gap:.15rem .5rem;margin-top:.6rem;padding-top:.55rem;border-top:1px solid var(--ring)}
.charge .cl{font-size:.78rem;color:var(--muted)}
.charge .cl b{color:var(--ink2);font-weight:600}
.charge > b{font-size:1.3rem;font-weight:600;color:var(--blue);letter-spacing:-.02em;
font-variant-numeric:tabular-nums}
.charge .cd{font-size:.76rem;font-variant-numeric:tabular-nums;color:var(--muted)}
.charge .cd.up{color:var(--flag)}
.charge .cd.down{color:var(--ok)}

.breakeven{font-family:system-ui,sans-serif;font-size:.79rem;color:var(--ink2);
line-height:1.5;margin:1rem 0 0}
.breakeven b{color:var(--ink)}
.hint{font-family:system-ui,sans-serif;font-size:.78rem;color:var(--muted);
margin:.2rem 0 1.2rem}

.caveat{font-family:system-ui,sans-serif;font-size:.79rem;color:var(--muted);line-height:1.55;
max-width:46rem}
details.more{border-top:1px solid var(--ring);padding:.75rem 0}
details.more summary{font-family:system-ui,sans-serif;font-size:.87rem;color:var(--ink);
cursor:pointer;list-style:none;font-weight:500}
details.more summary::-webkit-details-marker{display:none}
details.more summary::before{content:"+ ";color:var(--muted)}
details.more[open] summary::before{content:"− "}
details.more > *:not(summary){margin-top:.8rem}
table{width:100%;border-collapse:collapse;font-family:system-ui,sans-serif;font-size:.83rem;
font-variant-numeric:tabular-nums}
th,td{padding:.4rem .5rem;border-bottom:1px solid var(--ring);text-align:left}
th{font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);
font-weight:600}
td.num,th.num{text-align:right}
td.under{color:var(--flag)}
tr.bad td{background:color-mix(in srgb,var(--flag) 7%,transparent)}
.nv{font-size:.68rem;color:var(--warn);margin-left:.35rem}
.scroll{overflow-x:auto}
.work{font-family:"Cascadia Code",Consolas,monospace;font-size:.76rem;white-space:pre-wrap;
color:var(--ink2);line-height:1.6;background:var(--plane);border:1px solid var(--ring);
border-radius:9px;padding:.9rem 1rem;overflow-x:auto}
.src{font-family:system-ui,sans-serif;font-size:.76rem;color:var(--muted);margin-top:1.6rem}
@media(max-width:40rem){h1{font-size:1.85rem}.counts{font-size:.88rem}}
/* The old print block in build_explainer.CSS hides .presets, a selector this page
   does not use, so the whole control panel printed. */
@media print{
  .panel,.hint{display:none}
  .instrument{position:static;box-shadow:none}
  #chart{max-height:none}
  details.more > *:not(summary){display:block!important}
}
"""

BODY = """
<p class="kicker">Model</p>
<h1>Can the airport keep its promise?</h1>
<p class="sub">It owes its lenders 1.25 times its debt payment every year. Switch off the two
things it chooses to add, and see what is left.</p>

<div class="layout">
<section class="instrument" aria-label="The coverage test">
  <div class="score">
    <div class="counts">
      <div><b id="k1">&#8211;</b><span id="k1l">&#8211;</span></div>
      <div><b id="k2">&#8211;</b><span id="k2l">&#8211;</span></div>
    </div>
    <div class="chips" id="chips" role="group" aria-label="Each forecast year against the covenant"></div>
  </div>

  <div class="chead">
    <span class="ct" id="ctitle">&#8211;</span>
    <div class="seg" role="group" aria-label="Show the test in">
      <button type="button" data-u="0" aria-pressed="true">dollars</button>
      <button type="button" data-u="1" aria-pressed="false">ratios</button>
    </div>
  </div>
  <div class="chartwrap"><svg id="chart" viewBox="0 0 640 300" role="img" aria-label=""></svg></div>
  <p class="reading" id="ifthen"></p>
</section>

<aside class="panel">
  <h2>Start somewhere</h2>
  <div class="scen">
    <button type="button" data-p="base" class="on"><strong>As the Authority forecasts it</strong>
      <span>Both decisions made, at the values in the statement.</span></button>
    <button type="button" data-p="alone"><strong>The airport on its own</strong>
      <span>Neither decision. What its operations carry unaided.</span></button>
    <button type="button" data-p="after28"><strong>After the commitment runs out</strong>
      <span>Nothing designated in 2029 and 2030, which nothing covers.</span></button>
    <button type="button" data-p="short"><strong>Boardings ten percent short</strong>
      <span>Watch what this moves, and what it leaves alone.</span></button>
  </div>

  <h2>The two decisions</h2>
  <div class="switches">
    <label class="sw"><input type="checkbox" id="c0" checked>
      <span><strong>Count the designated revenue</strong>
      <span>State gaming money, which the indenture defines as
      &#8220;not constituting Revenues.&#8221;</span></span></label>
    <label class="sw"><input type="checkbox" id="c1" checked>
      <span><strong>Count the Coverage Account</strong>
      <span>Operating money moved to a reserve monthly, at the Authority&#8217;s
      discretion.</span></span></label>
  </div>
  <p class="why">Two pots, funded from different money and governed by different sentences.
  <a href="../covenant/index.html">What each one is, and why they are not the same thing.</a></p>

  <h2>Move the levers</h2>
  <div class="levs">
    <div class="lev">
      <label for="s0">How much is designated <b id="v0">as forecast</b></label>
      <div class="track"><input type="range" id="s0" min="0" max="110" value="100" step="5"
        aria-describedby="r0"><span class="tick" style="left:90.9%">as forecast</span></div>
      <div class="readout" id="r0">&#8211;</div>
    </div>
    <div class="lev">
      <label for="s1">Coverage Account deposit <b id="v1">as forecast</b></label>
      <div class="track"><input type="range" id="s1" min="0" max="120" value="100" step="5"
        aria-describedby="r1"><span class="tick" style="left:83.3%">as forecast</span></div>
      <div class="readout" id="r1">&#8211;</div>
    </div>
    <div class="lev">
      <label for="scope">Apply the designation change</label>
      <div class="seg" id="scope" role="group" aria-label="Apply the designation change to">
        <button type="button" data-l="0" aria-pressed="true">every year</button>
        <button type="button" data-l="1" aria-pressed="false">only 2029 and 2030</button>
      </div>
      <div class="readout">The Authority committed the designation for 2026 through 2028 only.</div>
    </div>
  </div>
  <p class="breakeven" id="be"></p>

  <h2>What the airlines pay</h2>
  <div class="levs">
    <div class="lev">
      <label for="s2">Boardings against forecast <b id="v2">as forecast</b></label>
      <div class="track"><input type="range" id="s2" min="-25" max="10" value="0" step="1"
        aria-describedby="r2"><span class="tick" style="left:71.4%">as forecast</span></div>
      <div class="readout" id="r2">&#8211;</div>
      <div class="charge"><span class="cl">Charge to airlines, <b id="cy">&#8211;</b></span>
        <b id="cv">&#8211;</b><span class="cd" id="cd"></span></div>
      <div class="why">A residual agreement holds the airline requirement constant, so fewer
      boardings divide the same bill among fewer passengers. It moves the charge and leaves the
      covenant test almost exactly where it was, which is why it sits here rather than with the
      levers above.</div>
    </div>
  </div>
</aside>
</div>

<p class="hint">Select a year on the chart or a chip above it to read its arithmetic. The link in
your address bar carries whatever you set, so a scenario can be sent to someone.</p>

<details class="more"><summary>Every year, in numbers</summary>
  <div class="scroll"><table id="tbl"><thead><tr>
    <th>year</th><th class="num">the promise $m</th><th class="num">earned $m</th>
    <th class="num">designated $m</th><th class="num">reserve $m</th>
    <th class="num">operating</th><th class="num">pledged</th><th class="num">tested</th>
    <th class="num">charge</th>
  </tr></thead><tbody></tbody></table></div>
  <p class="caveat">The promise is 1.25 times aggregate annual debt service. Earned is Net Revenues
  less anything designated in: the indenture defines designated money as &#8220;not constituting
  Revenues,&#8221; so it is not part of what the airport earns. The three ratio columns are the
  same three layers the chart draws, each divided by annual debt service.</p>
</details>

<details class="more"><summary>Show the arithmetic</summary>
  <div class="work" id="work"></div>
</details>

<details class="more"><summary>Where the numbers come from, and what this cannot tell you</summary>
  <p>Every baseline is the Authority&#8217;s own figure from the April 2025 Official Statement at
  os-2025ab PDF 202 (printed B-16), carried in <code>02-data/coverage-table.csv</code>.
  Designations come from Exhibit E at PDF 316 by way of
  <code>02-data/other-pledged-revenue.csv</code>. The window the Authority committed to is at
  PDF 67. The flow of funds and the 25 percent cap are at PDF 31, 32 and 34.</p>
  <p>The one figure not printed as such is the first block, what the airport earns. It is Net
  Revenues less the designated money, which is a subtraction of two published rows. The indenture
  makes the distinction itself: Other Pledged Revenues are defined as &#8220;moneys, not
  constituting Revenues, that are designated.&#8221;</p>
  <p>This is arithmetic on the Authority&#8217;s own rows, not a forecast and not a prediction.
  At the baseline the model reproduces all three of its printed ratio series and its charge to the
  cent, and the build refuses to write this page if it does not. Moving a control states a
  consequence, not a probability.</p>
  <p>What this cannot tell you: what the Authority will decide, what Harrisburg will do to the
  gaming appropriation, or what traffic will be.</p>
  <p>This page never says default, breach or violation. The indenture lets the Coverage Account
  count toward the 1.25 test, and on that test the Authority&#8217;s forecasts comply in every
  year. Missing the covenant once would not be an event of default either: the indenture requires
  the Authority to hire a consultant, take its advice and raise its rates, and only a second
  consecutive miss after rates have gone up is an Event of Default.</p>
</details>

<p style="margin-top:2rem"><a href="../covenant/index.html">&#8592; What the two pots are</a>
&#160;&#183;&#160; <a href="../appendix-dataviz/index.html">The plates</a>
&#160;&#183;&#160; <a href="../index.html">The package</a></p>

<p class="src">Built __BUILT__ from the CSVs in <code>02-data/</code>. Rebuild with
<code>python 03-harness/build_explainer.py</code>, check with <code>--check</code>.</p>
"""

JS = r"""
var el=function(i){return document.getElementById(i)};
var s0=el('s0'),s1=el('s1'),s2=el('s2'),c0=el('c0'),c1=el('c1');
var COV=1.25;
function m(k){return '$'+(k/1000).toFixed(1)+'m'}
function r2(v){return v.toFixed(2)}
var NS='http://www.w3.org/2000/svg';
function mk(n,a,t){var e=document.createElementNS(NS,n);for(var k in a)e.setAttribute(k,a[k]);
  if(t!==undefined)e.textContent=t;return e}

/* State lives in one object rather than in the DOM inputs. The previous version read
   the live inputs inside compute(), which meant breakeven() had to write to s0.value a
   hundred times per render and put it back. */
var S={d:100,a:100,p:0,l:0,D:1,C:1,y:1,u:0};

function compute(st){
  var share=st.d/100, cshare=st.a/100, dpax=st.p/100, lateOnly=(st.l===1);
  return B.map(function(b){
    var d=(lateOnly && b.year<=2028)?b.opr:b.opr*share;
    if(!st.D) d=0;
    // A share of the Authority's own deposit, not a flat percentage of debt service:
    // its deposit is 25.00% of debt service in five years and 23.23% in 2027, so a flat
    // rate would not reproduce the document. Raising it stops at the contractual cap.
    var cap=0.25*b.ads;
    var acct=st.C?Math.min(b.cov*cshare, cap):0;
    var earned=b.net-b.opr;               // Net Revenues before anything designated in
    var promise=COV*b.ads;
    var enpl=b.enpl*(1+dpax);
    var req=(b.cpe+b.opr/b.enpl)*b.enpl;  // the airline requirement before any designation
    return {year:b.year, earned:earned, desig:d, acct:acct, promise:promise,
            total:earned+d+acct,
            // The three layers the chart draws, as ratios: what operations carry, what
            // the pledge carries once designated money is counted, and what the covenant
            // is actually tested on given the reader's switches.
            operating:earned/b.ads,
            pledged:(earned+d)/b.ads,
            tested:(earned+d+acct)/b.ads,
            atCap:(st.C && b.cov*cshare>=cap-1e-9),
            gapBefore:promise-earned, cpe:(req-d)/enpl, base:b};
  });
}

var CH=null, UNIT=null;

// A fixed vertical scale in both units. Recomputing per state would make a smaller
// stack redraw at the same height as a larger one, so two scenarios could not be
// compared by eye, which is the whole point of being able to switch between them.
function domain(){
  var hi=0;
  B.forEach(function(b){
    var earned=b.net-b.opr;
    hi=Math.max(hi, earned+1.1*b.opr+0.25*b.ads, COV*b.ads);
  });
  return hi*1.10;
}
// Every reachable ratio across every control position falls between 0.98 and 1.61.
var RLO=0.90, RHI=1.70;

/* Measured rather than fixed. A 640-unit viewBox inside a 333px phone column scaled
   every label to about half its stated size, which the ratio view cannot survive.
   Measuring makes one user unit one CSS pixel at every width. The height is budgeted
   against the viewport as well as the width, because a sticky instrument taller than
   the screen pins its top and hangs its bottom off the bottom edge forever. */
var GEO=null;
function geo(){
  var W=Math.max(300,Math.round(el('chart').parentNode.clientWidth));
  var wide=window.matchMedia('(min-width:64rem)').matches;
  var H=wide?300:Math.round(Math.max(170,Math.min(W*0.62,window.innerHeight*0.32)));
  var narrow=W<420;
  return {W:W,H:H,L:narrow?36:46,R:narrow?12:56,T:narrow?42:44,BM:narrow?26:34,
          narrow:narrow};
}

function xcentre(i){return GEO.L+(i+0.5)*(GEO.W-GEO.L-GEO.R)/B.length}

function frame(svg){
  // The 2028 boundary as a dated event rather than a wash of colour.
  var g=GEO, xi=-1;
  B.forEach(function(b,i){if(xi<0&&b.year>2028)xi=i});
  if(xi>0){
    var bx=g.L+xi*(g.W-g.L-g.R)/B.length-3;
    svg.appendChild(mk('rect',{x:bx,y:g.T,width:(g.W-g.R)-bx,height:(g.H-g.BM)-g.T,
      fill:'var(--yellow)','fill-opacity':.07}));
    svg.appendChild(mk('line',{x1:bx,y1:g.T,x2:bx,y2:g.H-g.BM,stroke:'var(--warn)',
      'stroke-width':1.4,'stroke-dasharray':'4 3'}));
    // The full label runs off the right edge of a phone-width box, so on narrow it
    // shortens and hangs to the left of the rule, where there is room.
    svg.appendChild(g.narrow
      ? mk('text',{x:bx-4,y:g.T-6,'text-anchor':'end','class':'refl',fill:'var(--warn)'},
          'agreements end 2028')
      : mk('text',{x:bx+5,y:g.T-6,'class':'refl',fill:'var(--warn)'},
          'the airline agreement ends Dec. 31, 2028'));
  }
}

/* ---------- the dollar view ---------- */
function buildDollars(rows){
  var svg=el('chart'); while(svg.firstChild)svg.removeChild(svg.firstChild);
  GEO=geo(); var g=GEO, hi=domain();
  svg.setAttribute('viewBox','0 0 '+g.W+' '+g.H);
  var Y=function(v){return g.H-g.BM-(v/hi)*(g.H-g.BM-g.T)};
  var bw=Math.min((g.W-g.L-g.R)/B.length*0.56,58);

  var defs=mk('defs');
  [['hz','var(--blue-lt)','var(--blue)',45,.30,.55],
   ['hz2','var(--aqua)','var(--aqua)',-45,.22,.6]].forEach(function(p){
    var pat=mk('pattern',{id:p[0],width:6,height:6,patternUnits:'userSpaceOnUse',
      patternTransform:'rotate('+p[3]+')'});
    pat.appendChild(mk('rect',{width:6,height:6,fill:p[1],'fill-opacity':p[4]}));
    pat.appendChild(mk('line',{x1:0,y1:0,x2:0,y2:6,stroke:p[2],'stroke-width':2.2,
      opacity:p[5]}));
    defs.appendChild(pat);
  });
  svg.appendChild(defs);

  for(var v=0;v<=hi;v+=50000){
    if(v===0) continue;
    svg.appendChild(mk('line',{x1:g.L,y1:Y(v),x2:g.W-g.R,y2:Y(v),stroke:'var(--grid)'}));
    svg.appendChild(mk('text',{x:g.L-7,y:Y(v)+4,'text-anchor':'end','class':'ax'},
      '$'+(v/1000)+'m'));
  }
  frame(svg);

  CH={kind:'d',svg:svg,Y:Y,groups:[]};
  rows.forEach(function(r,i){
    var grp=mk('g',{'class':'yr'});
    var cx=xcentre(i), x=cx-bw/2, o={};
    o.focusbox=mk('rect',{'class':'focusbox',x:x-9,y:g.T+2,width:bw+18,
      height:(g.H-g.BM)-g.T-2+20,rx:5});
    grp.appendChild(o.focusbox);
    o.earned=mk('rect',{'class':'seg',x:x,width:bw,fill:'var(--blue)'});
    o.desig =mk('rect',{'class':'seg',x:x,width:bw,fill:'url(#hz)',stroke:'var(--ink2)',
      'stroke-opacity':.35});
    o.acct  =mk('rect',{'class':'seg',x:x,width:bw,fill:'url(#hz2)',stroke:'var(--ink2)',
      'stroke-opacity':.35});
    [o.earned,o.desig,o.acct].forEach(function(n){grp.appendChild(n)});
    // debt service itself, under the promise. Without it a reader cannot see that in
    // some years operations do not cover even the payment, let alone the cushion.
    o.debt=mk('line',{'class':'ref',x1:x-7,x2:x+bw+7,stroke:'var(--ink2)','stroke-width':1.3,
      'stroke-dasharray':'2 2'});
    o.promise=mk('line',{'class':'ref',x1:x-7,x2:x+bw+7,stroke:'var(--ink)','stroke-width':2.4});
    o.gap=mk('line',{'class':'gap',x1:cx,x2:cx,stroke:'var(--flag)','stroke-width':1.8,
      'stroke-dasharray':'3 2'});
    o.gaplab=mk('text',{'class':'val',x:cx,'text-anchor':'middle',fill:'var(--flag)'});
    o.yrlab=mk('text',{'class':'yrlab',x:cx,y:g.H-g.BM+17,'text-anchor':'middle'},r.year);
    [o.debt,o.promise,o.gap,o.gaplab,o.yrlab].forEach(function(n){grp.appendChild(n)});
    o.hit=mk('rect',{'class':'hit',x:x-9,y:g.T+2,width:bw+18,height:(g.H-g.BM)-g.T-2+20});
    o.hit.addEventListener('click',function(){S.y=i;render()});
    grp.appendChild(o.hit);
    svg.appendChild(grp);
    CH.groups.push({grp:grp,o:o});
  });

  legend(svg,[['var(--blue)',g.narrow?'earns':'what the airport earns'],
              ['url(#hz)','designated'],
              ['url(#hz2)',g.narrow?'reserve':'Coverage Account']]);
  // The two reference lines are labelled where they sit, at the right edge, which is
  // where the eye already is. On a phone there is no right edge to spare, and the
  // dashed and solid strokes carry it with the legend.
  if(!g.narrow){
    CH.reflab={
      promise:mk('text',{'class':'refl',x:g.W-g.R+5,fill:'var(--ink)'},'promise'),
      debt:mk('text',{'class':'refl',x:g.W-g.R+5,fill:'var(--muted)'},'debt')
    };
    svg.appendChild(CH.reflab.promise); svg.appendChild(CH.reflab.debt);
  }
  svg.appendChild(mk('line',{x1:g.L,y1:g.H-g.BM,x2:g.W-g.R,y2:g.H-g.BM,stroke:'var(--axis)'}));
}

// Laid out by measured advance rather than by hard-coded offsets, because the offsets
// were tuned for a 640-unit box and overflowed the moment the box became 333.
function legend(svg,items){
  var g=GEO, x=g.L, y=16;
  items.forEach(function(c){
    svg.appendChild(mk('rect',{x:x,y:y-9,width:10,height:10,fill:c[0],
      stroke:c[0].indexOf('url')===0?'var(--ink2)':'none','stroke-opacity':.35}));
    svg.appendChild(mk('text',{x:x+14,y:y,'class':'lg'},c[1]));
    x+=14+c[1].length*(g.narrow?5.6:6.0)+16;
  });
}

function drawDollars(rows){
  var g=GEO, Y=CH.Y, base=g.H-g.BM;
  rows.forEach(function(r,i){
    var G=CH.groups[i], o=G.o, y=base;
    [['earned',r.earned],['desig',r.desig],['acct',r.acct]].forEach(function(seg){
      var n=o[seg[0]], v=seg[1];
      if(v<=0){ n.setAttribute('height',0); n.setAttribute('y',base); n.style.opacity=0; return; }
      n.style.opacity=1;
      var h=base-Y(v); y-=h;
      n.setAttribute('y',y); n.setAttribute('height',h);
    });
    o.promise.setAttribute('y1',Y(r.promise)); o.promise.setAttribute('y2',Y(r.promise));
    o.debt.setAttribute('y1',Y(r.base.ads));   o.debt.setAttribute('y2',Y(r.base.ads));
    // The shortfall stem is drawn for every year that does not reach the promise, not
    // only the selected one. A year falling short is the signal; hiding five of them
    // behind a click was the old page telling the reader what to look at instead of
    // showing them.
    var bad=r.total<r.promise-1e-6;
    o.gap.setAttribute('y1',Y(r.total)); o.gap.setAttribute('y2',Y(r.promise));
    o.gap.style.opacity=bad?1:0;
    o.gaplab.setAttribute('y',Math.min(Y(r.total),Y(r.promise))-7);
    o.gaplab.textContent=bad?('−'+((r.promise-r.total)/1000).toFixed(1)+'m'):'';
    o.earned.setAttribute('fill',bad?'var(--flag)':'var(--blue)');
    o.yrlab.setAttribute('class','yrlab'+(bad?' bad':''));
    G.grp.setAttribute('class','yr'+(i===S.y?' on':''));
  });
  if(CH.reflab){
    var last=rows[rows.length-1];
    CH.reflab.promise.setAttribute('y',Y(last.promise)+4);
    CH.reflab.debt.setAttribute('y',Y(last.base.ads)+4);
  }
}

/* ---------- the ratio view ---------- */
function buildRatios(rows){
  var svg=el('chart'); while(svg.firstChild)svg.removeChild(svg.firstChild);
  GEO=geo(); var g=GEO;
  svg.setAttribute('viewBox','0 0 '+g.W+' '+g.H);
  var Y=function(v){var c=Math.max(RLO,Math.min(RHI,v));
    return g.H-g.BM-(c-RLO)/(RHI-RLO)*(g.H-g.BM-g.T)};

  // Everything under the covenant line is failure, and it is drawn as a place on the
  // chart rather than as a colour on a number.
  svg.appendChild(mk('rect',{x:g.L,y:Y(COV),width:(g.W-g.R)-g.L,height:(g.H-g.BM)-Y(COV),
    fill:'var(--flag)','fill-opacity':.07}));
  // Every 0.1 is too many lines in a 170px-tall phone chart; every 0.2 keeps 1.00,
  // 1.20, 1.40 and 1.60 and drops the rest.
  var stepv=g.narrow?0.2:0.1;
  for(var v=1.0;v<=RHI+1e-9;v+=stepv){
    var vv=Math.round(v*100)/100;
    svg.appendChild(mk('line',{x1:g.L,y1:Y(vv),x2:g.W-g.R,y2:Y(vv),stroke:'var(--grid)'}));
    svg.appendChild(mk('text',{x:g.L-7,y:Y(vv)+4,'text-anchor':'end','class':'ax'},
      vv.toFixed(2)));
  }
  frame(svg);
  svg.appendChild(mk('line',{x1:g.L,y1:Y(COV),x2:g.W-g.R,y2:Y(COV),stroke:'var(--ink)',
    'stroke-width':2.4}));
  // On a phone there is no margin to hang these in and no horizontal position that
  // does not sit on a column of data, so the header carries the sentence instead and
  // the rule, the tinted zone and the axis do the rest.
  if(!g.narrow){
    svg.appendChild(mk('text',{x:g.W-g.R+5,y:Y(COV)+4,'class':'refl',fill:'var(--ink)'},
      'covenant ' + COV.toFixed(2)));
    svg.appendChild(mk('text',{x:g.W-g.R+5,y:Y(COV)+16,'class':'refl',fill:'var(--flag)'},
      'below is short'));
  }

  CH={kind:'r',svg:svg,Y:Y,groups:[]};
  rows.forEach(function(r,i){
    var grp=mk('g',{'class':'yr'}), cx=xcentre(i), o={};
    o.focusbox=mk('rect',{'class':'focusbox',x:cx-24,y:g.T+2,width:48,
      height:(g.H-g.BM)-g.T-2+20,rx:5});
    grp.appendChild(o.focusbox);
    o.spine=mk('line',{'class':'spine',x1:cx,x2:cx,stroke:'var(--ring)','stroke-width':2.5,
      'stroke-linecap':'round'});
    grp.appendChild(o.spine);
    // Hollow to solid, bottom to top: what operations carry, what the pledge carries,
    // what the covenant is tested on. The same three layers the dollar stack draws.
    o.op =mk('circle',{'class':'pt',cx:cx,r:4,fill:'var(--plane)','stroke-width':1.8});
    o.pl =mk('circle',{'class':'pt',cx:cx,r:4.6,'fill-opacity':.45,'stroke-width':1.8});
    o.te =mk('circle',{'class':'pt',cx:cx,r:6.2,'stroke-width':1.8,stroke:'var(--plane)'});
    [o.op,o.pl,o.te].forEach(function(n){grp.appendChild(n)});
    o.val=mk('text',{'class':'val',x:cx,'text-anchor':'middle'});
    o.yrlab=mk('text',{'class':'yrlab',x:cx,y:g.H-g.BM+17,'text-anchor':'middle'},r.year);
    [o.val,o.yrlab].forEach(function(n){grp.appendChild(n)});
    o.hit=mk('rect',{'class':'hit',x:cx-24,y:g.T+2,width:48,height:(g.H-g.BM)-g.T-2+20});
    o.hit.addEventListener('click',function(){S.y=i;render()});
    grp.appendChild(o.hit);
    svg.appendChild(grp);
    CH.groups.push({grp:grp,o:o});
  });

  var lx=g.L, ly=16;
  ['operating','pledged','as tested'].forEach(function(lab,k){
    svg.appendChild(mk('circle',{cx:lx+5,cy:ly-4,r:[4,4.6,6.2][k],
      fill:k===0?'var(--plane)':'var(--blue)','fill-opacity':k===1?.45:1,
      stroke:'var(--blue)','stroke-width':1.8}));
    svg.appendChild(mk('text',{x:lx+16,y:ly,'class':'lg'},lab));
    lx+=16+lab.length*(g.narrow?5.6:6.0)+16;
  });
  svg.appendChild(mk('line',{x1:g.L,y1:g.H-g.BM,x2:g.W-g.R,y2:g.H-g.BM,stroke:'var(--axis)'}));
}

function drawRatios(rows){
  var Y=CH.Y;
  rows.forEach(function(r,i){
    var o=CH.groups[i].o;
    function paint(n,v){
      var bad=v<COV-1e-9, col=bad?'var(--flag)':'var(--blue)';
      n.setAttribute('cy',Y(v)); n.setAttribute('stroke',col);
      if(n!==o.op) n.setAttribute('fill',col);
    }
    paint(o.op,r.operating); paint(o.pl,r.pledged); paint(o.te,r.tested);
    o.op.setAttribute('fill','var(--plane)');
    o.te.setAttribute('stroke','var(--plane)');
    o.spine.setAttribute('y1',Y(r.operating)); o.spine.setAttribute('y2',Y(r.tested));
    var bad=r.tested<COV-1e-9;
    // A value sitting just under the covenant put its label straight on the rule, so
    // when the two are within a label's height the label goes below the mark instead.
    var ty=Y(r.tested);
    o.val.setAttribute('y',Math.abs(ty-Y(COV))<14?ty+18:ty-11);
    o.val.setAttribute('fill',bad?'var(--flag)':'var(--ink)');
    o.val.textContent=r2(r.tested);
    o.yrlab.setAttribute('class','yrlab'+(bad?' bad':''));
    CH.groups[i].grp.setAttribute('class','yr'+(i===S.y?' on':''));
  });
}

function chart(rows){
  // Rebuilt when the unit changes, and when the measured width or the breakpoint
  // does, because the viewBox and the label sizes are derived from both.
  var w=Math.round(el('chart').parentNode.clientWidth);
  var wide=window.matchMedia('(min-width:64rem)').matches;
  if(CH===null || UNIT!==S.u || CH.w!==w || CH.wide!==wide){
    (S.u===1?buildRatios:buildDollars)(rows); UNIT=S.u; CH.w=w; CH.wide=wide;
  }
  (S.u===1?drawRatios:drawDollars)(rows);
  var fails=rows.filter(function(r){return r.tested<COV-1e-9});
  el('chart').setAttribute('aria-label',
    (S.u===1
      ? 'Coverage ratio for each forecast year, on three cumulative layers: operating revenue, '
        +'plus designated revenue, and as tested. Against a covenant of 1.25. '
      : 'What meets the promise in each forecast year, in millions of dollars: what the airport '
        +'earns, money designated into the pledge, and the Coverage Account, stacked against a '
        +'line at 1.25 times annual debt service. ')
    + (fails.length
        ? fails.length+' of '+rows.length+' years fall below the covenant, in '
          +fails.map(function(r){return r.year}).join(', ')+'.'
        : 'Every year clears the covenant.'));
}

/* ---------- scoreboard ---------- */
function scoreboard(rows){
  var clear=rows.filter(function(r){return r.tested>=COV-1e-9}).length;
  var short=rows.filter(function(r){return r.pledged<COV-1e-9}).length;
  var n=rows.length;
  var k1=el('k1'), k2=el('k2');
  k1.textContent=clear+' of '+n;
  k1.className=(clear<n?'bad':'');
  el('k1l').textContent='clear the covenant as the test is set here';
  k2.textContent=short+' of '+n;
  k2.className=(short>0?'bad':'');
  el('k2l').textContent='fall below on pledged revenue alone';

  var box=el('chips'); box.innerHTML='';
  rows.forEach(function(r,i){
    var bad=r.tested<COV-1e-9;
    var b=document.createElement('button');
    b.type='button';
    b.className='chip'+(bad?' bad':'')+(i===S.y?' on':'');
    b.setAttribute('aria-pressed',String(i===S.y));
    b.innerHTML='<span class="yr">'+r.year+'</span><span class="vl">'+r2(r.tested)+
      '</span><span class="st">'+(bad?'short':'clears')+'</span>';
    b.addEventListener('click',function(){S.y=i;render()});
    box.appendChild(b);
  });
}

/* How far the designation can fall, holding everything else where the reader has put
   it, before some year stops reaching the promise. Scanned rather than solved because
   the switches can zero a whole term and there is then no root to find. Runs over a
   copy of the state, so it no longer writes to the live input a hundred times. */
function breakeven(){
  for(var v=100;v>=0;v-=1){
    var t={}; for(var k in S) t[k]=S[k]; t.d=v;
    var ok=compute(t).every(function(r){return r.tested>=COV-1e-9});
    if(!ok) return v+1;
  }
  return null;
}

function sentence(rows){
  var f=document.createDocumentFragment();
  function t(x){f.appendChild(document.createTextNode(x))}
  function e(x,w){var n=document.createElement('em');n.textContent=x;if(w)n.className='bad';
    f.appendChild(n)}
  // Verdict first. The old sentence spent forty words getting to the number, which on
  // a phone pushed the sticky instrument past two thirds of the viewport.
  var y=rows[S.y];
  t(y.year+' comes out at '); e(r2(y.tested),y.tested<COV);
  t(y.tested<COV?', under the covenant. ':', which clears. ');
  t('It earns '); e(m(y.earned)); t(' against a promise of '); e(m(y.promise));
  t(', '); e(m(y.gapBefore),true); t(' short before either decision.');
  if(y.earned<y.base.ads){
    t(' Operations do not cover the '); e(m(y.base.ads),true); t(' debt payment.');
  }
  if(S.l===1) t(' The designation change applies only to 2029 and 2030.');
  return f;
}

function render(){
  var rows=compute(S);

  el('v0').textContent=(S.d===100?'as forecast':(S.d===0?'nothing':S.d+'%'));
  el('v1').textContent=(S.a===100?'as forecast':(S.a===0?'nothing':S.a+'%'));
  el('v2').textContent=(S.p===0?'as forecast':(S.p>0?'+':'')+S.p+'%');
  var fy=rows[S.y];
  // At the baseline the readout would otherwise say a figure "against" itself.
  el('r0').innerHTML=!S.D ? 'Not counted. Switch the decision back on to move this.'
    : '<b>'+m(fy.desig)+'</b> designated in '+fy.year
      +(S.d===100?', the figure in the statement':', against '+m(fy.base.opr)+' in the statement');
  el('r1').innerHTML=!S.C ? 'Not counted. Switch the decision back on to move this.'
    : '<b>'+m(fy.acct)+'</b> in '+fy.year+(fy.atCap
        ? ', at the 25 percent cap the contract sets'
        : (S.a===100?', the figure in the statement'
                    :', against '+m(fy.base.cov)+' in the statement'));
  el('r2').innerHTML='<b>'+(fy.base.enpl*(1+S.p/100)/1000).toFixed(2)+'m</b> boardings in '
    +fy.year+', against '+(fy.base.enpl/1000).toFixed(2)+'m forecast';
  el('cy').textContent=fy.year;
  el('cv').textContent='$'+fy.cpe.toFixed(2);
  var dc=fy.cpe-fy.base.cpe, cd=el('cd');
  cd.textContent=(Math.abs(dc)<0.005)?'as the Authority forecasts it'
    :((dc>0?'+':'−')+'$'+Math.abs(dc).toFixed(2)+' against its forecast of $'
      +fy.base.cpe.toFixed(2));
  cd.className='cd'+(Math.abs(dc)<0.005?'':(dc>0?' up':' down'));

  c0.closest('.sw').classList.toggle('off',!S.D);
  c1.closest('.sw').classList.toggle('off',!S.C);
  [].forEach.call(document.querySelectorAll('#scope button'),function(b){
    b.setAttribute('aria-pressed',String(+b.dataset.l===S.l))});
  [].forEach.call(document.querySelectorAll('.chead .seg button'),function(b){
    b.setAttribute('aria-pressed',String(+b.dataset.u===S.u))});
  el('ctitle').textContent=(S.u===1
    ? 'Coverage ratio in three layers. Below the 1.25 line is short.'
    : 'What meets the promise, in millions of dollars');

  scoreboard(rows);
  chart(rows);
  var p=el('ifthen'); p.innerHTML=''; p.appendChild(sentence(rows));

  var be=breakeven(), bx=el('be');
  if(!S.C||!S.D||be===null){
    bx.innerHTML=(rows.every(function(r){return r.tested>=COV-1e-9}))
      ? 'The promise is met at every level of designation on these settings.'
      : 'The promise is already unmet on these settings.';
  } else {
    bx.innerHTML='Designation could fall to <b>'+be+'%</b> of what the Authority assumes '
      +'before a year stops reaching the promise.';
  }

  var tb=el('tbl').querySelector('tbody'); tb.innerHTML='';
  rows.forEach(function(r){
    var bad=r.tested<COV-1e-9;
    var tr=document.createElement('tr');
    if(bad) tr.className='bad';
    tr.innerHTML='<td>'+r.year+(r.year>2028?'<span class="nv">not committed</span>':'')+'</td>'+
      '<td class="num">'+(r.promise/1000).toFixed(1)+'</td>'+
      '<td class="num">'+(r.earned/1000).toFixed(1)+'</td>'+
      '<td class="num">'+(r.desig/1000).toFixed(1)+'</td>'+
      '<td class="num">'+(r.acct/1000).toFixed(1)+'</td>'+
      '<td class="num'+(r.operating<COV?' under':'')+'">'+r2(r.operating)+'</td>'+
      '<td class="num'+(r.pledged<COV?' under':'')+'">'+r2(r.pledged)+'</td>'+
      '<td class="num'+(bad?' under':'')+'">'+r2(r.tested)+'</td>'+
      '<td class="num">$'+r.cpe.toFixed(2)+'</td>';
    tb.appendChild(tr);
  });

  // Follows the selected year. It used to be pinned to rows[1], so clicking 2029 and
  // opening the arithmetic showed 2026.
  var b=fy;
  el('work').textContent=
    'worked for '+b.year+'. The Authority’s own rows: Net Revenues '+m(b.base.net)+
    ' (including '+m(b.base.opr)+' designated), Coverage Account '+m(b.base.cov)+
    ', debt service '+m(b.base.ads)+', boardings '+b.base.enpl.toLocaleString()+
    'k, charge $'+b.base.cpe.toFixed(2)+
    '\n\nours:'+
    '\n  the promise       1.25 × '+m(b.base.ads)+' = '+m(b.promise)+
    '\n  what it earns     '+m(b.base.net)+' − '+m(b.base.opr)+' designated = '+m(b.earned)+
    '\n  short before      '+m(b.promise)+' − '+m(b.earned)+' = '+m(b.gapBefore)+
    '\n  designated        '+m(b.desig)+
    '\n  coverage account  '+m(b.acct)+
    '\n  stack             '+m(b.total)+(b.total>=b.promise?', over the promise':', under the promise')+
    '\n\nthe same three layers as ratios, which is how the statement prints them:'+
    '\n  operating         '+b.operating.toFixed(3)+
    '\n  plus designated   '+b.pledged.toFixed(3)+
    '\n  as tested         '+b.tested.toFixed(3)+'   against a covenant of 1.25';

  writeURL();
}

/* The control state lives in the address bar, so a scenario is a link. replaceState
   rather than pushState: one history entry per slider tick would bury the reader's
   back button under a hundred of them. The cost is that Back does not step through
   scenarios; hashchange still restores a link someone pastes or follows. */
function writeURL(){
  var q='d='+S.d+'&a='+S.a+'&p='+S.p+'&l='+S.l+'&D='+S.D+'&C='+S.C+'&y='+S.y+'&u='+S.u;
  try{history.replaceState(null,'','#'+q)}catch(e){}
}
function clamp(v,lo,hi,dflt){v=parseInt(v,10);
  return (isNaN(v)||v<lo||v>hi)?dflt:v}
function readURL(){
  var h=(location.hash||'').replace(/^#/,''); if(!h) return false;
  var q={}; h.split('&').forEach(function(kv){var p=kv.split('=');q[p[0]]=p[1]});
  if(q.d===undefined) return false;
  S.d=clamp(q.d,0,110,100); S.a=clamp(q.a,0,120,100); S.p=clamp(q.p,-25,10,0);
  S.l=clamp(q.l,0,1,0); S.D=clamp(q.D,0,1,1); S.C=clamp(q.C,0,1,1);
  S.y=clamp(q.y,0,B.length-1,1); S.u=clamp(q.u,0,1,0);
  return true;
}
function toInputs(){
  s0.value=S.d; s1.value=S.a; s2.value=S.p; c0.checked=!!S.D; c1.checked=!!S.C;
}

var P={base:{d:100,a:100,p:0,l:0,D:1,C:1},
       alone:{d:100,a:100,p:0,l:0,D:0,C:0},
       after28:{d:0,a:100,p:0,l:1,D:1,C:1},
       short:{d:100,a:100,p:-10,l:0,D:1,C:1}};
[].forEach.call(document.querySelectorAll('.scen button'),function(btn){
  btn.addEventListener('click',function(){
    var p=P[btn.dataset.p]; for(var k in p) S[k]=p[k];
    toInputs(); render();
    [].forEach.call(document.querySelectorAll('.scen button'),function(o){
      o.classList.toggle('on',o===btn)});
  });
});
function manual(){
  [].forEach.call(document.querySelectorAll('.scen button'),function(o){o.classList.remove('on')});
  render();
}
c0.addEventListener('change',function(){S.D=c0.checked?1:0;manual()});
c1.addEventListener('change',function(){S.C=c1.checked?1:0;manual()});
[].forEach.call(document.querySelectorAll('#scope button'),function(b){
  b.addEventListener('click',function(){S.l=+b.dataset.l;manual()});
});
[].forEach.call(document.querySelectorAll('.chead .seg button'),function(b){
  // The unit switch is not a scenario change, so it does not clear the preset.
  b.addEventListener('click',function(){S.u=+b.dataset.u;render()});
});
[[s0,'d'],[s1,'a'],[s2,'p']].forEach(function(pair){
  var x=pair[0], k=pair[1];
  x.addEventListener('input',function(){S[k]=+x.value;manual()});
  // A range input under the cursor swallows the wheel and rewrites itself, so simply
  // scrolling past the dials silently changed the scenario and left the reader looking
  // at numbers that did not match what was on the screen. Take the wheel, scroll by hand.
  x.addEventListener('wheel',function(ev){ev.preventDefault();window.scrollBy(0,ev.deltaY)},
    {passive:false});
});
el('chart').addEventListener('keydown',function(ev){
  if(ev.key==='ArrowRight'&&S.y<B.length-1){S.y++;render();ev.preventDefault()}
  if(ev.key==='ArrowLeft'&&S.y>0){S.y--;render();ev.preventDefault()}
});
el('chart').setAttribute('tabindex','0');
// The viewBox is measured, so a width change has to redraw. Debounced, and chart()
// no-ops unless the rounded width or the breakpoint actually moved.
var rt=null;
window.addEventListener('resize',function(){
  clearTimeout(rt); rt=setTimeout(render,120);
});
window.addEventListener('hashchange',function(){
  if(readURL()){
    toInputs();
    [].forEach.call(document.querySelectorAll('.scen button'),function(o){
      o.classList.remove('on')});
    render();
  }
});

if(readURL()){
  toInputs();
  [].forEach.call(document.querySelectorAll('.scen button'),function(o){o.classList.remove('on')});
}
render();
"""
