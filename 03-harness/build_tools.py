#!/usr/bin/env python3
"""build_tools.py — the two aggregation tools.

    documents/   every source the reporting stands on, readable, filterable, and
                 carrying the hash that proves the copy read is the copy published.
    factcheck/   the draft-independent half of the fact check: the two machine
                 gates, the conflicts register, and the claims held or withdrawn.

Both are generated from CSVs in 02-data/. Nothing here is hand-maintained, and
--check re-renders in memory and byte-diffs against the committed file, so a page
that has drifted from its data fails the build rather than shipping.

    python 03-harness/build_tools.py
    python 03-harness/build_tools.py --check
"""
import csv, io, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_explainer import page, rows
from charts import esc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILT = "2026-09-01"

# The two gates are run by verify_claims.py and their results recorded here. Both
# are properties of the vault and the documents, not of any draft, so they stay
# true while the prose is rewritten.
HASH_GATE = (12, 12)
ANCHOR_GATE = (66, 66)

TIER_WHAT = {
    "A": "Issuer or regulator document, read directly.",
    "B": "Official, named, and not captured into the vault.",
    "C": "Secondary reporting or a clip. An utterance, never a figure.",
    "D": "An interested party, or a compiler that grades itself.",
}

KIND_WHAT = {
    "issuer": "published by the Authority",
    "regulator": "published by the FAA",
    "rating": "a rating agency",
    "media": "a news organisation",
    "academic": "peer-reviewed research",
    "interested": "a party with a position",
    "compiler": "a finding aid that aggregates other people's filings",
}

CSS = """
.tool{font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
.bar{position:sticky;top:0;z-index:5;background:var(--plane);border-bottom:1px solid var(--ring);
padding:.8rem 0 .7rem;margin-bottom:1.2rem}
.bar input[type=search]{width:100%;padding:.6rem .8rem;font:inherit;font-family:system-ui,sans-serif;
font-size:.94rem;border:1px solid var(--ring);border-radius:9px;background:var(--surface);
color:var(--ink)}
.chips{display:flex;flex-wrap:wrap;gap:.4rem;margin-top:.6rem;align-items:center}
.prow{display:flex;flex-wrap:wrap;gap:.4rem;margin-top:.7rem;align-items:center}
.plab{font-family:system-ui,sans-serif;font-size:.72rem;letter-spacing:.1em;
text-transform:uppercase;color:var(--muted);margin-right:.3rem}
.flab{font-family:system-ui,sans-serif;font-size:.72rem;color:var(--muted);
margin:0 .1rem 0 .5rem}
.chip.big{font-size:.84rem;padding:.36rem .8rem;font-weight:500;color:var(--ink)}
.chip.big[aria-pressed=true]{background:var(--blue);border-color:var(--blue);color:#fff}
details.more{margin-top:.55rem}
details.more summary{font-family:system-ui,sans-serif;font-size:.76rem;color:var(--ink2);
cursor:pointer;list-style:none}
details.more summary::-webkit-details-marker{display:none}
details.more summary::before{content:"+ ";color:var(--muted)}
details.more[open] summary::before{content:"\2212 "}
.countrow{display:flex;align-items:center;gap:.7rem;margin-top:.55rem}
button.clear{font-family:system-ui,sans-serif;font-size:.74rem;padding:.16rem .55rem;
border-radius:99px;border:1px solid var(--ring);background:var(--surface);color:var(--ink2);
cursor:pointer}
button.clear:hover{border-color:var(--blue);color:var(--blue)}
.chip{font-family:system-ui,sans-serif;font-size:.76rem;padding:.24rem .62rem;border-radius:99px;
border:1px solid var(--ring);background:var(--surface);color:var(--ink2);cursor:pointer;
user-select:none}
.chip[aria-pressed=true]{background:var(--blue);border-color:var(--blue);color:#fff}
.count{font-family:system-ui,sans-serif;font-size:.8rem;color:var(--muted);margin-top:.55rem}
.doc{border-top:1px solid var(--ring);padding:1.05rem 0}
.doc:last-child{border-bottom:1px solid var(--ring)}
.doc h3{font-family:system-ui,sans-serif;font-size:1.01rem;margin:0 0 .3rem;line-height:1.34}
.doc .meta{font-family:system-ui,sans-serif;font-size:.76rem;color:var(--muted);
margin:0 0 .5rem;display:flex;flex-wrap:wrap;gap:.5rem;align-items:center}
.tier{display:inline-block;font-weight:600;border-radius:4px;padding:.05rem .38rem;
border:1px solid currentColor;font-size:.72rem}
.tA{color:var(--blue)}.tB{color:var(--aqua)}.tC{color:var(--yellow)}.tD{color:var(--orange)}
.doc p{margin:0 0 .5rem;font-size:.96rem;line-height:1.6}
.doc .cites{font-family:system-ui,sans-serif;font-size:.79rem;color:var(--ink2)}
.hash{font-family:"Cascadia Code",Consolas,monospace;font-size:.72rem;color:var(--muted);
word-break:break-all;margin-top:.4rem}
.hash button{font:inherit;font-size:.7rem;font-family:system-ui,sans-serif;margin-left:.4rem;
border:1px solid var(--ring);background:var(--surface);color:var(--ink2);border-radius:5px;
padding:.06rem .38rem;cursor:pointer}
.nohash{font-family:system-ui,sans-serif;font-size:.78rem;color:var(--orange)}
.gate{display:flex;gap:1rem;flex-wrap:wrap;margin:1.3rem 0 0}
.gate div{flex:1 1 13rem;border:1px solid var(--ring);border-radius:11px;padding:.9rem 1rem;
background:var(--surface)}
.gate b{display:block;font-family:system-ui,sans-serif;font-size:.74rem;letter-spacing:.08em;
text-transform:uppercase;color:var(--muted);margin-bottom:.25rem}
.gate .v{font-family:system-ui,sans-serif;font-size:1.5rem;font-weight:600;color:var(--blue)}
.gate p{font-family:system-ui,sans-serif;font-size:.82rem;color:var(--ink2);margin:.35rem 0 0;
line-height:1.5}
table.reg{width:100%;border-collapse:collapse;font-family:system-ui,sans-serif;font-size:.84rem;
margin:1rem 0;table-layout:fixed}
table.reg th{text-align:left;border-bottom:1px solid var(--ink2);padding:.45rem .5rem;
font-size:.74rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);font-weight:600}
table.reg td{border-bottom:1px solid var(--ring);padding:.55rem .5rem;vertical-align:top;
line-height:1.5;overflow-wrap:break-word}
/* Only the figure resists breaking. The locator beneath it must wrap, or a long
   page reference forces the whole row wider than the page. */
table.reg td.fig{font-variant-numeric:tabular-nums}
table.reg td.fig .n{white-space:nowrap;font-weight:600}
table.reg .loc{display:block;color:var(--muted);font-size:.75rem;line-height:1.4;margin-top:.15rem}
table.conflicts col.c-subj{width:26%}
table.conflicts col.c-year{width:8%}
table.conflicts col.c-fig{width:24%}
table.conflicts col.c-disp{width:12%}
table.held col.h-claim{width:34%}
table.held col.h-stat{width:12%}
.scroll{overflow-x:auto}
@media(min-width:60rem){.wrap{max-width:64rem}}
.st{display:inline-block;font-size:.7rem;font-family:system-ui,sans-serif;border-radius:4px;
padding:.05rem .4rem;border:1px solid currentColor;font-weight:600}
.s-held{color:var(--yellow)}.s-withdrawn{color:var(--orange)}.s-never{color:var(--red)}
.s-attributed{color:var(--aqua)}.s-disclosed{color:var(--blue)}
.s-unresolved{color:var(--orange)}.s-not{color:var(--red)}
.note{background:var(--surface2);border-left:3px solid var(--blue);border-radius:0 9px 9px 0;
padding:.85rem 1.05rem;margin:1.4rem 0;font-family:system-ui,sans-serif;font-size:.87rem;
line-height:1.56}
.note b{display:block;margin-bottom:.2rem}
.back{font-family:system-ui,sans-serif;font-size:.82rem;margin:0 0 1.4rem}
.empty{font-family:system-ui,sans-serif;color:var(--muted);padding:1.6rem 0;font-size:.9rem}
/* ---- the records library ---- */
section.topic{margin:0 0 2.2rem}
h2.grp{font-family:system-ui,sans-serif;font-size:1.16rem;letter-spacing:-.01em;
margin:2.6rem 0 .25rem;padding-top:1.2rem;border-top:2px solid var(--ink);
display:flex;flex-wrap:wrap;align-items:baseline;gap:.7rem}
h2.grp .gn{font-size:.72rem;font-weight:400;color:var(--muted);letter-spacing:.06em;
text-transform:uppercase;margin-left:auto}
.grpnote{font-family:system-ui,sans-serif;font-size:.85rem;color:var(--ink2);
margin:0 0 1.1rem;line-height:1.55;max-width:44rem}
.rec{display:grid;grid-template-columns:4.4rem 1fr;gap:1rem;padding:1.15rem 0;
border-top:1px solid var(--ring)}
.rec .yr{font-family:system-ui,sans-serif;font-size:1.1rem;font-weight:600;color:var(--ink2);
font-variant-numeric:tabular-nums;line-height:1.2}
.rec .yr .tier{display:block;margin-top:.3rem;font-size:.68rem;width:1.35rem;text-align:center}
.rec h3{font-family:system-ui,sans-serif;font-size:1.04rem;margin:0 0 .15rem;line-height:1.32}
.rec .pub{font-family:system-ui,sans-serif;font-size:.73rem;letter-spacing:.06em;
text-transform:uppercase;color:var(--muted);margin:0 0 .5rem}
.rec .what{font-size:.94rem;line-height:1.6;margin:0 0 .8rem;color:var(--ink2);max-width:46rem}
.keys{border-left:2px solid var(--ring);padding:.1rem 0 .1rem .85rem;margin:0 0 .9rem;
max-width:44rem}
.keys .kh{font-family:system-ui,sans-serif;font-size:.72rem;letter-spacing:.07em;
text-transform:uppercase;color:var(--muted);margin:0 0 .45rem}
.keys ul{list-style:none;margin:0;padding:0}
.keys li{display:flex;gap:.6rem;align-items:baseline;padding:.2rem 0;
font-family:system-ui,sans-serif;font-size:.83rem;line-height:1.45;color:var(--ink2)}
a.pg,span.pg{font-family:system-ui,sans-serif;font-size:.74rem;text-decoration:none;
padding:.12rem .48rem;border-radius:99px;border:1px solid var(--ring);color:var(--blue);
background:var(--surface);font-variant-numeric:tabular-nums;white-space:nowrap;flex:none}
a.pg:hover{border-color:var(--blue);background:var(--blue);color:#fff}
span.pg.off{color:var(--muted)}
.act{display:flex;flex-wrap:wrap;gap:.6rem 1rem;align-items:baseline}
a.open{font-family:system-ui,sans-serif;font-size:.85rem;font-weight:600;text-decoration:none;
color:#fff;background:var(--blue);padding:.42rem .85rem;border-radius:8px;white-space:nowrap}
a.open:hover{filter:brightness(1.12)}
details.ver{font-family:system-ui,sans-serif;font-size:.78rem;color:var(--muted)}
details.ver summary{cursor:pointer;color:var(--ink2);list-style:none}
details.ver summary::-webkit-details-marker{display:none}
details.ver summary::before{content:"✓ ";color:var(--aqua)}
details.ver.cite summary::before{content:"◦ ";color:var(--yellow)}
details.ver.snap summary::before{content:"◷ ";color:var(--aqua)}
details.ver p{margin:.5rem 0 .4rem;max-width:34rem;line-height:1.5}
details.ver code{font-family:"Cascadia Code",Consolas,monospace;font-size:.7rem;
word-break:break-all;color:var(--muted)}
details.ver button{font:inherit;font-size:.7rem;font-family:system-ui,sans-serif;
margin-left:.4rem;border:1px solid var(--ring);background:var(--surface);color:var(--ink2);
border-radius:5px;padding:.06rem .38rem;cursor:pointer}
.rec:target{background:var(--surface2);box-shadow:0 0 0 .7rem var(--surface2);
border-radius:4px;scroll-margin-top:8.5rem}
.rec:target h3::after{content:" ← cited here";font-family:system-ui,sans-serif;
font-size:.72rem;font-weight:400;color:var(--blue);letter-spacing:.04em}
@media(max-width:34rem){.rec{grid-template-columns:1fr}
.rec .yr{display:flex;gap:.5rem;align-items:center}
.rec .yr .tier{display:inline-block;margin:0}
h2.grp .gn{margin-left:0}}
"""

FILTER_JS = """<script>
(function(){
  var q=document.getElementById('q'),
      items=[].slice.call(document.querySelectorAll('[data-hay]')),
      chips=[].slice.call(document.querySelectorAll('.chip[data-group]')),
      secs=[].slice.call(document.querySelectorAll('section.topic')),
      out=document.getElementById('count'),
      empty=document.getElementById('empty'),
      clear=document.getElementById('clear');
  var on={};

  function apply(){
    var t=(q?q.value:'').toLowerCase().trim(), n=0, active=!!t;
    for(var k in on){ if(on[k]&&on[k].length){active=true;} }

    items.forEach(function(el){
      var ok=!t||el.dataset.hay.indexOf(t)>-1;
      if(ok){
        for(var g in on){
          if(on[g]&&on[g].length&&on[g].indexOf(el.dataset[g])<0){ok=false;break;}
        }
      }
      el.hidden=!ok; if(ok)n++;
    });

    // A section whose records are all filtered out must go too. Leaving five
    // headings on screen, each still announcing its original count, is why the
    // filter looked broken: the records changed and the page did not.
    secs.forEach(function(sec){
      var recs=[].slice.call(sec.querySelectorAll('[data-hay]')),
          vis=recs.filter(function(r){return !r.hidden;}).length,
          badge=sec.querySelector('.gn');
      sec.hidden = vis===0;
      if(badge){
        badge.textContent = (active && vis!==recs.length)
          ? vis+' of '+recs.length+' records'
          : recs.length+' records';
      }
    });

    if(out){
      out.textContent = active
        ? 'Showing '+n+' of '+items.length+' records'
        : items.length+' records, grouped by question';
    }
    if(clear) clear.hidden = !active;
    if(empty) empty.hidden = n>0;
  }

  chips.forEach(function(c){
    c.onclick=function(){
      var g=c.dataset.group, v=c.dataset.value, p=c.getAttribute('aria-pressed')==='true';
      c.setAttribute('aria-pressed',p?'false':'true');
      on[g]=on[g]||[];
      if(p){on[g]=on[g].filter(function(x){return x!==v});}else{on[g].push(v);}
      apply();
      // Land the reader on the first surviving section rather than leaving them
      // looking at a filter bar with the result somewhere below the fold.
      var first=secs.filter(function(x){return !x.hidden;})[0];
      if(first && !p){ first.scrollIntoView({block:'start', behavior:'smooth'}); }
    };
  });

  if(clear){
    clear.onclick=function(){
      chips.forEach(function(c){c.setAttribute('aria-pressed','false');});
      on={}; if(q)q.value='';
      apply();
      window.scrollTo({top:0, behavior:'smooth'});
    };
  }
  if(q)q.addEventListener('input',apply);
  apply();
})();
</script>"""

COPY_JS = """<script>
document.addEventListener('click',function(e){
  var b=e.target.closest('button[data-copy]'); if(!b)return;
  navigator.clipboard.writeText(b.dataset.copy).then(function(){
    var t=b.textContent; b.textContent='copied'; setTimeout(function(){b.textContent=t},1200);
  });
});
</script>"""


def bar(placeholder, primary, secondary):
    """A search box, the questions as primary navigation, then narrower filters.

    The questions are the organising idea of this page, so they get their own row
    and their own weight. Putting them in a fourth chip row among four made them
    read as one facet of many.
    """
    pname, plabel, pvalues = primary
    prim = [f'<div class="prow"><span class="plab">{esc(plabel)}</span>']
    for v, txt in pvalues:
        prim.append(f'<button class="chip big" aria-pressed="false" '
                    f'data-group="{esc(pname)}" data-value="{esc(v)}">{esc(txt)}</button>')
    prim.append("</div>")

    sec = []
    for gname, label, values in secondary:
        sec.append(f'<span class="flab">{esc(label)}</span>')
        for v, txt in values:
            sec.append(f'<button class="chip" aria-pressed="false" data-group="{esc(gname)}" '
                       f'data-value="{esc(v)}">{esc(txt)}</button>')

    return (f'<div class="bar tool">'
            f'<input id="q" type="search" placeholder="{esc(placeholder)}" '
            f'aria-label="{esc(placeholder)}">'
            f'{"".join(prim)}'
            f'<details class="more"><summary>More filters</summary>'
            f'<div class="chips">{"".join(sec)}</div></details>'
            f'<div class="countrow"><span class="count" id="count"></span>'
            f'<button class="clear" id="clear" hidden>Clear filters</button></div>'
            f'</div>')


# ------------------------------------------------------------------ documents

TOPICS = [
    ("F1", "The covenant, and what secures it",
     "The promise made to bondholders, the two mechanisms that meet it, and the money behind "
     "each. Start with the 2025 Official Statement."),
    ("F3", "What it costs airlines to fly here",
     "The audited charge per boarded passenger, one report for each year from 2015, plus the "
     "schedule the carriers are billed against. Table IV is the same table in all eleven."),
    ("F2", "The forecasts, and how they have performed",
     "Two consultant forecasts made four years apart, and the record of what happened between "
     "them."),
    ("F4", "Passengers, and whether the cost reaches them",
     "Enplanement counts, and the contested question of whether an airline charge arrives as a "
     "fare or as reduced service."),
    ("S1", "How the terminal was decided",
     "Board proceedings, the economic impact study, the federal rule requiring an alternatives "
     "analysis, and the contemporaneous reporting."),
]

KIND_LABEL = {
    "issuer": "Airport Authority", "regulator": "FAA", "rating": "Rating agency",
    "media": "News reporting", "academic": "Research", "compiler": "Compiler",
    "interested": "Interested party",
}


def key_pages(r):
    """Say which page to open and what is on it, then link straight to it.

    Page links are emitted only where the URL is a PDF: a viewer cannot honour
    #page= on a landing page, and a link that silently does nothing is worse than
    plain text.
    """
    if not r.get("key_pages"):
        return ""
    direct = r["url"].lower().split("?")[0].endswith(".pdf")
    out = []
    for item in r["key_pages"].split(";"):
        if "|" not in item:
            continue
        n, label = item.split("|", 1)
        n, label = n.strip(), label.strip()
        tag = (f'<a class="pg" href="{esc(r["url"])}#page={n}" rel="noopener">p.&thinsp;{n}</a>'
               if direct else f'<span class="pg off">p.&thinsp;{n}</span>')
        out.append(f'<li>{tag}<span>{esc(label)}</span></li>')
    if not out:
        return ""
    head = ("Open the document at a page" if direct
            else "Pages worth reading, once the file is open")
    return f'<div class="keys"><p class="kh">{esc(head)}</p><ul>{"".join(out)}</ul></div>'


def build_documents():
    docs = rows("documents.csv")
    short = [r["id"] for r in docs
             if r["vault"] in ("yes", "snapshot", "citation")
             and len(r["sha256"]) != 64]
    if short:
        raise SystemExit(f"documents.csv: {short} are in the vault but carry no "
                         "full 64-character SHA-256. Restore from sources.json.")
    known = {t for t, _, _ in TOPICS}
    stray = sorted({r["serves"] for r in docs} - known)
    if stray:
        raise SystemExit(f"documents.csv: {stray} is not a topic in TOPICS, so those records "
                         "would render in no section and vanish from the library.")

    n_read = sum(1 for r in docs if r["url"].lower().split("?")[0].endswith(".pdf"))
    n_cap = sum(1 for r in docs if r["vault"] in ("yes", "snapshot"))
    n_file = sum(1 for r in docs if r["vault"] == "yes")
    n_key = sum(len([x for x in (r.get("key_pages") or "").split(";") if "|" in x])
                for r in docs)

    body = ['<p class="back"><a href="../index.html">&larr; the record</a></p>',
            '<p class="kicker">The records</p>',
            '<h1>Read the documents</h1>',
            f'<p class="sub">Every record behind the reporting, grouped by the question it '
            f'answers. {n_cap} of the {len(docs)} are captured and hashed, {n_read} open directly as a '
            f'file, and {n_key} carry a link to the exact page a finding rests on with a note '
            f'on what is there. {n_file} are immutable documents whose checksum any reader can '
            f'reproduce; the rest are dated snapshots of pages that change.</p>']

    body.append(bar(
        "Search titles, findings and page notes",
        ("topic", "Jump to a question", [(t, lbl) for t, lbl, _ in TOPICS]),
        [("vault", "Evidence", [("yes", "immutable document"),
                                ("snapshot", "page snapshot"),
                                ("citation", "citation only"),
                                ("no", "not captured")]),
         ("kind", "Published by",
          [(k, v) for k, v in KIND_LABEL.items() if k != "interested"]),
         ("read", "Access", [("open", "opens directly"),
                             ("page", "landing page only")])]))
    body.append('<p class="empty" id="empty" hidden>Nothing matches that.</p>')

    for topic, label, blurb in TOPICS:
        group = [r for r in docs if r["serves"] == topic]
        if not group:
            continue
        group.sort(key=lambda r: (0 if r.get("key_pages") else 1,
                                  {"A": 0, "B": 1, "C": 2, "D": 3}.get(r["tier"], 4),
                                  -int(r["year"] or 0)))
        body.append(f'<section class="topic"><h2 class="grp">{esc(label)}'
                    f'<span class="gn">{len(group)} records</span></h2>')
        body.append(f'<p class="grpnote">{esc(blurb)}</p>')
        for r in group:
            direct = r["url"].lower().split("?")[0].endswith(".pdf")
            hay = " ".join([r["id"], r["title"], r["proves"], r["cites"],
                            r.get("key_pages", ""), r["kind"], r["year"]]).lower()
            action = (f'<a class="open" href="{esc(r["url"])}" rel="noopener">'
                      f'{"Open the document" if direct else "Open on the publisher&#8217;s site"}'
                      f' &rarr;</a>') if r["url"] else ""
            # Three states, and they are not the same claim. A checksum on a citation
            # record must not read as a checksum on the article.
            if r["vault"] == "snapshot":
                verify = (f'<details class="ver snap"><summary>Snapshot taken 1 September 2026'
                          f'</summary><p>A live web page, captured on the date shown. The digest '
                          f'below is the page this reporting read. It will not match a fresh '
                          f'download, because the page changes: that is what the capture is '
                          f'for.</p><code>{esc(r["sha256"])}</code>'
                          f'<button data-copy="{esc(r["sha256"])}">copy</button></details>')
            elif r["vault"] == "yes":
                verify = (f'<details class="ver"><summary>Confirm this copy</summary>'
                          f'<p>Download the file and hash it. If the digest matches, the copy is '
                          f'the one this reporting read.</p><code>{esc(r["sha256"])}</code>'
                          f'<button data-copy="{esc(r["sha256"])}">copy</button></details>')
            elif r["vault"] == "citation":
                verify = (f'<details class="ver cite"><summary>Citation record captured</summary>'
                          f'<p>The article is behind the publisher&#8217;s paywall and is not '
                          f'republished here. What is held and hashed is the CrossRef record, '
                          f'which fixes the DOI, the authors and the journal.</p>'
                          f'<code>{esc(r["sha256"])}</code>'
                          f'<button data-copy="{esc(r["sha256"])}">copy</button></details>')
            else:
                verify = ('<p class="nohash">No file to capture: this is a query system rather '
                          'than a document. The figure it supplies is the one number in the '
                          'reporting without a hashed source, and it is labelled that way '
                          'wherever it appears.</p>')
            body.append(
                f'<article class="rec" id="{esc(r["id"])}" data-hay="{esc(hay)}" '
                f'data-topic="{esc(topic)}" data-kind="{esc(r["kind"])}" '
                f'data-vault="{esc(r["vault"])}" '
                f'data-read="{"open" if direct else "page"}">'
                f'<div class="yr">{esc(r["year"])}<span class="tier t{r["tier"]}">'
                f'{esc(r["tier"])}</span></div>'
                f'<div class="bod"><h3>{esc(r["title"])}</h3>'
                f'<p class="pub">{esc(KIND_LABEL.get(r["kind"], r["kind"]))}</p>'
                f'<p class="what">{esc(r["proves"])}</p>'
                f'{key_pages(r)}'
                f'<div class="act">{action}{verify}</div></div></article>')
        body.append('</section>')

    body.append('<div class="note"><b>How the grades work</b>'
                + " ".join(f"<b style='display:inline;font-weight:600'>{k}.</b> {esc(v)}"
                           for k, v in TIER_WHAT.items())
                + '</div>')
    body.append(f'<p class="count">Built {BUILT}. Generated from '
                f'<code>02-data/documents.csv</code>. The eleven Authority financial reports and '
                f'the economic impact study were captured Aug. 31, 2026; their source links were '
                f'recovered and hash-verified Sept. 1, and each returns a file matching the '
                f'digest recorded here.</p>')

    return page("Read the documents", "".join(body), FILTER_JS + COPY_JS, CSS)


# ------------------------------------------------------------------ fact check

def build_factcheck():
    con = rows("conflicts.csv")
    held = rows("held-claims.csv")

    hg, ht = HASH_GATE
    ag, at = ANCHOR_GATE

    body = ['<p class="back"><a href="../index.html">&larr; the record</a></p>',
            '<p class="kicker">Fact check</p>',
            '<h1>The fact check</h1>',
            '<p class="sub">Two machine gates over the documents, a register of the places the '
            "Authority's own filings disagree with each other, and the claims this reporting "
            'does not make. Each is a property of the documents rather than of a draft.</p>']

    body.append(
        f'<div class="gate">'
        f'<div><b>Hash gate</b><span class="v">{hg}/{ht}</span>'
        f'<p>Every captured document still hashes to the SHA-256 recorded for it. A document '
        f'that was re-downloaded and changed would fail here rather than quietly reshaping a '
        f'claim.</p></div>'
        f'<div><b>Anchor gate</b><span class="v">{ag}/{at}</span>'
        f'<p>Every anchor, the literal run of text a claim rests on, is present on the page '
        f'cited. Each page is extracted twice, in layout and raw modes, because financial tables '
        f'survive one mode or the other. Checking a single mode produced fourteen false '
        f'misses.</p></div>'
        f'</div>')

    body.append('<div class="note"><b>Claim-level checking of the published piece is not here yet</b>'
                'The last claim ledger checked a draft the audited record has since superseded. '
                'The ledger is rebuilt against the piece as published, by a checker who did not '
                'write it. The two gates above and the two registers below do not depend on which '
                'draft is current.</div>')

    body.append('<h2>Where the Authority\'s documents disagree with themselves</h2>')
    body.append('<p>Where a document contradicts itself, the contradiction is published and no '
                'figure is selected. Several of these weaken the reporting rather than support '
                'it. On the 2020 pair, either page gives a pandemic-year charge higher than the '
                'fiscal 2025 charge, which rules out any claim that the current figure is the '
                'highest the airport has billed.</p>')

    # One disposition filter spans both registers below, so every row in both must
    # carry a value in this group. A row with an empty data-res would vanish the
    # moment any chip was pressed, which is how a filter quietly loses evidence.
    body.append(bar("Search the conflicts and the held claims",
                    ("res", "Filter by disposition",
                     [("disclosed", "disclosed"), ("attributed", "attributed"),
                      ("unresolved", "unresolved"), ("not reproduced", "locator failed"),
                      ("held", "held"), ("withdrawn", "withdrawn"),
                      ("never", "never written")]),
                    []))

    body.append('<div class="scroll"><table class="reg conflicts">'
                '<colgroup><col class="c-subj"><col class="c-year"><col class="c-fig">'
                '<col class="c-fig"><col class="c-disp"></colgroup><thead><tr>'
                '<th>Subject</th><th>Year</th><th>One page says</th><th>Another says</th>'
                '<th>Disposition</th></tr></thead><tbody>')
    for r in con:
        hay = " ".join([r["subject"], r["year"], r["figure_a"], r["figure_b"],
                        r["locator_a"], r["locator_b"], r["note"], r["document"]]).lower()
        cls = "s-" + ("not" if r["resolution"] == "not reproduced" else r["resolution"])
        body.append(
            f'<tr data-hay="{esc(hay)}" data-res="{esc(r["resolution"])}">'
            f'<td><b>{esc(r["subject"])}</b><span class="loc">{esc(r["note"])}</span></td>'
            f'<td class="fig"><span class="n">{esc(r["year"])}</span></td>'
            f'<td class="fig"><span class="n">{esc(r["figure_a"])}</span>'
            f'<span class="loc">{esc(r["locator_a"])}</span></td>'
            f'<td class="fig"><span class="n">{esc(r["figure_b"])}</span>'
            f'<span class="loc">{esc(r["locator_b"])}</span></td>'
            f'<td><span class="st {cls}">{esc(r["resolution"])}</span></td></tr>')
    body.append('</tbody></table></div>')

    body.append('<h2>Claims this reporting does not make</h2>')
    body.append('<p>Several appeared in earlier drafts and were removed. <b>Withdrawn</b> means '
                'the documents stopped supporting the claim. <b>Held</b> means no primary source '
                'establishes it yet. <b>Attributed</b> means the figure belongs to a named party '
                'and is identified as theirs at every appearance. <b>Never</b> means the record '
                'does not support it and the reporting does not state it.</p>')

    body.append('<div class="scroll"><table class="reg held">'
                '<colgroup><col class="h-claim"><col class="h-stat"><col></colgroup><thead><tr>'
                '<th>The claim</th><th>Status</th><th>Why</th></tr></thead><tbody>')
    for r in held:
        hay = " ".join([r["claim"], r["why"], r["status"], r["source_id"]]).lower()
        body.append(
            f'<tr data-hay="{esc(hay)}" data-res="{esc(r["status"])}">'
            f'<td><b>{esc(r["claim"])}</b></td>'
            f'<td><span class="st s-{esc(r["status"])}">{esc(r["status"])}</span></td>'
            f'<td>{esc(r["why"])}</td></tr>')
    body.append('</tbody></table></div>')

    body.append('<p class="empty" id="empty" hidden>Nothing matches that.</p>')
    body.append('<div class="note"><b>What the reporting has not done</b>'
                'Nobody has been interviewed. Right of reply has not been sought from the '
                'Authority or from any named individual. No records request has been answered. '
                'Every person quoted is quoted from published reporting by others and is '
                'labelled as such.</div>')
    body.append(f'<p class="count">Built {BUILT}. Generated from '
                f'<code>02-data/conflicts.csv</code> and <code>02-data/held-claims.csv</code>. '
                f'Gate results from <code>03-harness/verify_claims.py</code>.</p>')

    return page("What was checked, what conflicts, and what is not printed",
                "".join(body), FILTER_JS, CSS)


# ------------------------------------------------------------------ main

TARGETS = [("documents", build_documents), ("factcheck", build_factcheck)]


def main():
    check = "--check" in sys.argv
    bad = 0
    for name, fn in TARGETS:
        html = fn()
        path = os.path.join(ROOT, name, "index.html")
        if check:
            if not os.path.exists(path):
                print(f"{name}: MISSING {path}")
                bad += 1
                continue
            cur = io.open(path, encoding="utf-8").read()
            if cur != html:
                print(f"{name}: DRIFT, the committed page is not what the data renders")
                bad += 1
            else:
                print(f"{name} --check OK")
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            io.open(path, "w", encoding="utf-8", newline="\n").write(html)
            print(f"wrote {name}/index.html  {len(html):,} bytes")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
