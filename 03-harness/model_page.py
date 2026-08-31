"""model_page.py — the markup, styling and behaviour of the interactive model.

Design intent, written down because the first three attempts were wrong in the
same way. Each of them showed the reader a coverage ratio: 1.12 against a
covenant of 1.25, as a line, then as a dumbbell. Both were accurate. Neither
illuminated anything, because a ratio of 1.12 means nothing to a person who does
not price municipal bonds for a living. There is no intuition to hang on it, so
the reader cannot tell whether they should be alarmed, and the chart does the
reader's feeling for them or not at all.

What a reader can hold is money, and a decision with a name on it.

So this page is built on the dollar decomposition instead. The Authority
promised its lenders 1.25 times annual debt service. That promise is a number of
dollars. It is met by three things stacked on top of each other, and only the
first is the airport's own money:

  what the airport earns    Net Revenues less anything designated in. The
                            indenture is explicit that designated money is
                            "not constituting Revenues", so this really is the
                            airport's own operating result.
  money designated in       Other Pledged Revenues: federal relief, then casino
                            money. Chosen each year, or not, as in 2024.
  the Coverage Account      A reserve funded monthly at the Authority's
                            discretion and capped at 25 percent of debt service.

Drawn that way, the reading is immediate and needs no training: the solid block
does not reach the line, and two blocks the Authority chooses to add sit on top
of it to get there. About three dollars in every ten of the promise is carried
by those two decisions, in every forecast year.

Bars from zero, in dollars, because a length encoding is owed a zero baseline
and dollars are the unit the reader already owns.

The discipline that makes it publishable lives in build_explainer.py: at the
Authority's own values the model must reproduce the Authority's own printed
ratios and its charge per boarded passenger, or the build refuses to write the
page.
"""

CSS = """
.hero{padding:.2rem 0 .4rem;margin:0 0 .2rem}
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:0 0 .9rem}
@media(max-width:640px){.tiles{grid-template-columns:1fr;gap:.5rem}}
.tile b{display:block;font-family:system-ui,sans-serif;font-size:2.15rem;line-height:1.05;
letter-spacing:-.03em;font-variant-numeric:tabular-nums;color:var(--blue)}
.tile.warn b{color:var(--orange)}
.tile span{display:block;font-family:system-ui,sans-serif;font-size:.76rem;color:var(--muted);
margin-top:.2rem;line-height:1.35}
.reading{font-family:system-ui,sans-serif;font-size:1.03rem;line-height:1.55;margin:0 0 .3rem}
.reading em{font-style:normal;font-weight:600;color:var(--blue)}
.reading em.warn{color:var(--orange)}
.switches{display:flex;flex-wrap:wrap;gap:.6rem;margin:1.1rem 0 .3rem}
.sw{flex:1 1 300px;display:flex;gap:.7rem;align-items:flex-start;cursor:pointer;
background:var(--surface);border:1px solid var(--ring);border-radius:11px;padding:.75rem .9rem;
font-family:system-ui,sans-serif;transition:border-color .12s}
.sw:hover{border-color:var(--blue)}
.sw input{margin:.15rem 0 0;width:1.05rem;height:1.05rem;accent-color:var(--blue);flex:none}
.sw strong{display:block;font-size:.89rem;line-height:1.3}
.sw span{display:block;font-size:.76rem;color:var(--muted);line-height:1.35;margin-top:.1rem}
.sw.off{background:var(--surface2);border-style:dashed}
.sw.off strong{color:var(--muted)}
.scen{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:.6rem;
margin:.9rem 0 .7rem}
.scen button{font:inherit;font-family:system-ui,sans-serif;line-height:1.32;text-align:left;
cursor:pointer;background:var(--surface);border:1px solid var(--ring);border-radius:11px;
padding:.7rem .85rem;color:var(--ink);transition:border-color .12s,transform .12s}
.scen button:hover{border-color:var(--blue);transform:translateY(-1px)}
.scen button.on{border-color:var(--blue);background:color-mix(in srgb,var(--blue) 9%,transparent);
box-shadow:inset 0 0 0 1px var(--blue)}
.scen button strong{display:block;font-size:.88rem;line-height:1.25;margin-bottom:.15rem}
.scen button span{font-size:.75rem;color:var(--muted);line-height:1.35}
details.more{border-top:1px solid var(--ring);margin-top:.2rem}
details.more>summary{cursor:pointer;font-family:system-ui,sans-serif;font-size:.87rem;
color:var(--blue);padding:.75rem 0;list-style:none}
details.more>summary::-webkit-details-marker{display:none}
details.more>summary::before{content:"+";display:inline-block;width:1rem;font-weight:600}
details.more[open]>summary::before{content:"\\2013"}
details.more>*:not(summary){margin-bottom:1rem}
.lev{margin:0 0 1rem}
.lev label{display:flex;justify-content:space-between;align-items:baseline;gap:1rem;
font-family:system-ui,sans-serif;font-size:.88rem;margin-bottom:.2rem}
.lev label b{font-variant-numeric:tabular-nums;color:var(--blue);white-space:nowrap}
.lev input[type=range]{width:100%;accent-color:var(--blue)}
.lev .why{font-family:system-ui,sans-serif;font-size:.75rem;color:var(--muted);margin-top:.15rem}
#tbl td.under{color:var(--orange);font-weight:600}
#tbl .nv{font-size:.66rem;color:var(--yellow);border:1px solid currentColor;border-radius:99px;
padding:0 .32rem;margin-left:.3rem;white-space:nowrap}
.caveat{font-family:system-ui,sans-serif;font-size:.78rem;color:var(--muted);margin:.2rem 0 1.3rem}
@media print{.scen,.switches,.toggle{display:none}}
"""

BODY = """
<p class="kicker">Model</p>
<h1>What holds the promise up</h1>
<p class="sub">The Authority told its lenders that every year it would have a quarter more than it
owes them. That promise is a number of dollars, and three things stack up to meet it. Only the
first is the airport's own money.</p>

<div class="hero">
  <div class="tiles">
    <div class="tile" id="t1"><b>&#8211;</b><span>&#8211;</span></div>
    <div class="tile" id="t2"><b>&#8211;</b><span>&#8211;</span></div>
    <div class="tile" id="t3"><b>&#8211;</b><span>&#8211;</span></div>
  </div>
  <p class="reading" id="ifthen"></p>
  <svg id="chart" viewBox="0 0 900 330" role="img" aria-label="What meets the promise in each forecast year, in millions of dollars: what the airport earns, money designated into the pledge, and the Coverage Account, stacked against a line at 1.25 times annual debt service."></svg>
</div>

<div class="switches">
  <label class="sw"><input type="checkbox" id="c0" checked>
    <span><strong>Count the money it designates</strong>
    <span>Casino and gas revenue the Authority adds to the pledge each year, or does not. It
    designated none in 2024.</span></span></label>
  <label class="sw"><input type="checkbox" id="c1" checked>
    <span><strong>Count the Coverage Account</strong>
    <span>A reserve it tops up monthly at its own discretion, capped at a quarter of the debt
    payment.</span></span></label>
</div>

<div class="scen">
  <button data-p="base" class="on"><strong>As the Authority forecasts it</strong>
    <span>Both decisions made, at the values in the statement.</span></button>
  <button data-p="after28"><strong>After the vote runs out</strong>
    <span>Nothing designated in 2029 and 2030, which no vote covers.</span></button>
  <button data-p="short"><strong>Traffic ten percent short</strong>
    <span>Watch what this moves, and what it leaves alone.</span></button>
  <button data-p="stack"><strong>Neither decision, traffic short</strong>
    <span>The airport on its own earnings.</span></button>
</div>

<p class="caveat">Arithmetic on the Authority's own rows. Not a forecast and not a prediction. At
the baseline this model reproduces its printed ratios and its charge to the cent, and the build
refuses to publish the page if it does not.</p>

<details class="more"><summary>Adjust it yourself</summary>
  <div class="lev">
    <label for="s0">How much is designated <b id="v0">as forecast</b></label>
    <input type="range" id="s0" min="0" max="110" value="100" step="5">
    <div class="why">As a share of what the Authority assumes, because it assumes $8.8m for 2025
      and $11.575m after, so no single sum could mean &#8220;as forecast&#8221; in every year.</div>
  </div>
  <div class="lev">
    <label for="s3">Apply that <b id="v3">to every year</b></label>
    <input type="range" id="s3" min="0" max="1" value="0" step="1">
    <div class="why">The airlines voted the designation for 2026 through 2028 only.</div>
  </div>
  <div class="lev">
    <label for="s1">Coverage Account deposit <b id="v1">25% of the debt payment</b></label>
    <input type="range" id="s1" min="0" max="25" value="25" step="1">
    <div class="why">Discretionary, monthly, capped at 25 percent.</div>
  </div>
  <div class="lev">
    <label for="s2">Boardings against forecast <b id="v2">as forecast</b></label>
    <input type="range" id="s2" min="-25" max="10" value="0" step="1">
    <div class="why">Holds the airline requirement constant, which is what a residual agreement
      does with fixed costs and debt service. It moves the charge to airlines and leaves the
      promise almost exactly where it was.</div>
  </div>
</details>

<details class="more"><summary>Every year, in numbers</summary>
  <div class="scroll"><table id="tbl"><thead><tr>
    <th>year</th><th class="num">the promise $m</th><th class="num">earned $m</th>
    <th class="num">designated $m</th><th class="num">reserve $m</th>
    <th class="num">short before the decisions $m</th><th class="num">charge</th>
  </tr></thead><tbody></tbody></table></div>
  <p class="caveat">The promise is 1.25 times aggregate annual debt service. Earned is Net
  Revenues less anything designated in: the indenture defines designated money as
  &#8220;not constituting Revenues,&#8221; so it is not part of what the airport earns.</p>
</details>

<details class="more"><summary>Show the arithmetic</summary>
  <div class="work" id="work"></div>
</details>

<details class="more"><summary>Where the numbers come from, and what this cannot tell you</summary>
  <p>Every baseline is the Authority's own figure from the April 2025 Official Statement at
  os-2025ab PDF 202 (printed B-16), carried in <code>02-data/coverage-table.csv</code>.
  Designations come from Exhibit E at PDF 316 by way of
  <code>02-data/other-pledged-revenue.csv</code>. The window the airlines actually voted is at
  PDF 67. The flow of funds and the 25 percent cap are at PDF 31, 32 and 34.</p>
  <p>The one figure not printed as such is the first block, what the airport earns. It is Net
  Revenues less the designated money, which is a subtraction of two published rows. The indenture
  makes the distinction itself: Other Pledged Revenues are defined as &#8220;moneys, not
  constituting Revenues, that are designated.&#8221;</p>
  <p>What this cannot tell you: what the Authority will decide, what Harrisburg will do to the
  gaming appropriation, or what traffic will be. It is arithmetic on published rows, and moving a
  control states a consequence rather than a probability.</p>
  <p>This page never says default, breach or violation. The indenture lets the Coverage Account
  count toward the 1.25 test, and on that test the Authority's forecasts comply in every year.
  Missing the covenant once would not be an event of default either: the indenture requires the
  Authority to hire a consultant, take its advice and raise its rates, and only a second
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
var s0=el('s0'),s1=el('s1'),s2=el('s2'),s3=el('s3'),c0=el('c0'),c1=el('c1');
function m(k){return '$'+(k/1000).toFixed(1)+'m'}
var NS='http://www.w3.org/2000/svg';
function mk(n,a,t){var e=document.createElementNS(NS,n);for(var k in a)e.setAttribute(k,a[k]);
  if(t!==undefined)e.textContent=t;return e}

function compute(){
  var share=+s0.value/100, pct=+s1.value/100, dpax=+s2.value/100, lateOnly=(+s3.value===1);
  var useD=c0.checked, useA=c1.checked;
  return B.map(function(b){
    var d=(lateOnly && b.year<=2028)?b.opr:b.opr*share;
    if(!useD) d=0;
    var acct=useA?pct*b.ads:0;
    var earned=b.net-b.opr;               // Net Revenues before anything designated in
    var promise=1.25*b.ads;
    var enpl=b.enpl*(1+dpax);
    var req=(b.cpe+b.opr/b.enpl)*b.enpl;  // the airline requirement before any designation
    return {year:b.year, earned:earned, desig:d, acct:acct, promise:promise,
            total:earned+d+acct, net:earned+d,
            alone:(earned+d)/b.ads, printed:(earned+d+acct)/b.ads,
            gapBefore:promise-earned, cpe:(req-d)/enpl, base:b};
  });
}

function draw(rows){
  var svg=el('chart'); while(svg.firstChild)svg.removeChild(svg.firstChild);
  var W=900,H=330,L=54,R=118,T=34,BM=46;
  var hi=Math.max.apply(null,rows.map(function(r){return Math.max(r.total,r.promise)}))*1.10;
  var X=function(i){return L+i*(W-L-R)/rows.length};
  var bw=Math.min((W-L-R)/rows.length*0.56,58);
  var Y=function(v){return H-BM-(v/hi)*(H-BM-T)};   // bars are lengths, so zero baseline

  // hatch marks the two blocks the Authority chooses to add
  var defs=mk('defs');
  var pat=mk('pattern',{id:'hz',width:6,height:6,patternUnits:'userSpaceOnUse',
    patternTransform:'rotate(45)'});
  pat.appendChild(mk('rect',{width:6,height:6,fill:'var(--blue-lt)','fill-opacity':.30}));
  pat.appendChild(mk('line',{x1:0,y1:0,x2:0,y2:6,stroke:'var(--blue)','stroke-width':2.2,
    opacity:.55}));
  defs.appendChild(pat);
  var pat2=mk('pattern',{id:'hz2',width:6,height:6,patternUnits:'userSpaceOnUse',
    patternTransform:'rotate(-45)'});
  pat2.appendChild(mk('rect',{width:6,height:6,fill:'var(--aqua)','fill-opacity':.22}));
  pat2.appendChild(mk('line',{x1:0,y1:0,x2:0,y2:6,stroke:'var(--aqua)','stroke-width':2.2,
    opacity:.6}));
  defs.appendChild(pat2);
  svg.appendChild(defs);

  for(var g=0;g<=hi;g+=40000){
    svg.appendChild(mk('line',{x1:L,y1:Y(g),x2:W-R,y2:Y(g),stroke:'var(--grid)'}));
    svg.appendChild(mk('text',{x:L-8,y:Y(g)+4,'text-anchor':'end','class':'ax'},
      '$'+(g/1000)+'m'));
  }

  var xi=-1; rows.forEach(function(r,i){if(xi<0&&r.year>2028)xi=i});
  if(xi>0){
    svg.appendChild(mk('rect',{x:X(xi)-4,y:T-12,width:(W-R)-(X(xi)-4),height:(H-BM)-(T-12),
      fill:'var(--yellow)','fill-opacity':.10}));
    svg.appendChild(mk('text',{x:X(xi)+2,y:T-2,'class':'ax'},'no vote covers these years'));
  }

  rows.forEach(function(r,i){
    var cx=X(i)+((W-L-R)/rows.length)/2, x=cx-bw/2, y=H-BM;
    [[r.earned,'var(--blue)',null],[r.desig,null,'url(#hz)'],[r.acct,null,'url(#hz2)']]
      .forEach(function(seg){
        if(seg[0]<=0) return;
        var h=(H-BM)-Y(seg[0]);
        y-=h;
        svg.appendChild(mk('rect',{x:x,y:y,width:bw,height:h,
          fill:seg[2]||seg[1],stroke:seg[2]?'var(--ink2)':'none','stroke-opacity':.35}));
      });
    // the promise, drawn across each bar so the comparison is local
    svg.appendChild(mk('line',{x1:x-7,y1:Y(r.promise),x2:x+bw+7,y2:Y(r.promise),
      stroke:'var(--ink)','stroke-width':2.4}));
    // how far the airport's own earnings fall short of it
    var eTop=Y(r.earned);
    svg.appendChild(mk('line',{x1:cx,y1:eTop,x2:cx,y2:Y(r.promise),stroke:'var(--orange)',
      'stroke-width':1.6,'stroke-dasharray':'3 2'}));
    // the shortfall reads beside the bar, never inside a gap a few pixels tall
    svg.appendChild(mk('text',{x:x+bw+7,y:(eTop+Y(r.promise))/2+4,'class':'val',
      fill:'var(--orange)'},'\u2212'+(r.gapBefore/1000).toFixed(1)));
    svg.appendChild(mk('text',{x:cx,y:H-BM+18,'text-anchor':'middle','class':'ax'},r.year));
  });

  // legend, drawn with the same fills that draw the data
  var lx=L, ly=14;
  [['var(--blue)','what the airport earns',0],
   ['url(#hz)','money it designates in',180],
   ['url(#hz2)','the Coverage Account',350]].forEach(function(c){
    svg.appendChild(mk('rect',{x:lx+c[2],y:ly-9,width:12,height:12,fill:c[0],
      stroke:c[0].indexOf('url')===0?'var(--ink2)':'none','stroke-opacity':.35}));
    svg.appendChild(mk('text',{x:lx+c[2]+18,y:ly+1,'class':'ax'},c[1]));
  });
  svg.appendChild(mk('line',{x1:lx+512,y1:ly-3,x2:lx+530,y2:ly-3,stroke:'var(--ink)',
    'stroke-width':2.4}));
  svg.appendChild(mk('text',{x:lx+536,y:ly+1,'class':'ax'},'the promise'));
  svg.appendChild(mk('line',{x1:L,y1:H-BM,x2:W-R,y2:H-BM,stroke:'var(--axis)'}));
}

function tiles(rows){
  var shortY=rows.filter(function(r){return r.earned<r.promise});
  var worst=rows.reduce(function(a,b){return b.gapBefore>a.gapBefore?b:a});
  var discShare=rows.map(function(r){return (r.desig+r.acct)/r.promise});
  var avg=discShare.reduce(function(a,b){return a+b},0)/discShare.length;
  var missing=rows.filter(function(r){return r.total<r.promise});
  function set(id,val,lab,warn){var t=el(id);t.querySelector('b').textContent=val;
    t.querySelector('span').textContent=lab;t.classList.toggle('warn',!!warn)}
  set('t1',Math.round(avg*100)+'%',
      'of the promise carried by decisions the Authority makes itself',avg>0.15);
  set('t2',shortY.length+' of '+rows.length,
      'years the airport\u2019s own earnings fall short of the promise',shortY.length>0);
  if(missing.length){
    set('t3',missing.length+' of '+rows.length,
        'years the stack no longer reaches the promise',true);
  } else {
    set('t3','\u2212'+m(worst.gapBefore),
        'the largest gap the two decisions have to close, in '+worst.year,true);
  }
}

function sentence(rows){
  var f=document.createDocumentFragment();
  function t(x){f.appendChild(document.createTextNode(x))}
  function e(x,w){var n=document.createElement('em');n.textContent=x;if(w)n.className='warn';
    f.appendChild(n)}
  var y=rows[1];
  t('In '+y.year+' the promise is '); e(m(y.promise));
  t(' and the airport earns '); e(m(y.earned));
  t('. It is '); e(m(y.gapBefore).replace('$','$'),true); t(' short before either decision. ');
  var missing=rows.filter(function(r){return r.total<r.promise});
  if(missing.length){
    t('On these settings the stack no longer reaches the promise in ');
    e(missing.length+' of '+rows.length,true); t(' years.');
  } else {
    t('Both decisions together more than close it.');
  }
  if(+s3.value===1) t(' The change applies only to 2029 and 2030, which the January 2025 vote does not cover.');
  return f;
}

function render(){
  var rows=compute();
  el('v0').textContent=(+s0.value===100?'as forecast':(+s0.value===0?'nothing':(+s0.value)+'%'));
  el('v1').textContent=(+s1.value)+'% of the debt payment';
  var dp=+s2.value; el('v2').textContent=(dp===0?'as forecast':(dp>0?'+':'')+dp+'%');
  el('v3').textContent=(+s3.value===1?'only to 2029 and 2030':'to every year');
  c0.closest('.sw').classList.toggle('off',!c0.checked);
  c1.closest('.sw').classList.toggle('off',!c1.checked);
  tiles(rows); draw(rows);
  var p=el('ifthen'); p.innerHTML=''; p.appendChild(sentence(rows));
  var tb=el('tbl').querySelector('tbody'); tb.innerHTML='';
  rows.forEach(function(r){
    var tr=document.createElement('tr');
    tr.innerHTML='<td>'+r.year+(r.year>2028?'<span class="nv">no vote</span>':'')+'</td>'+
      '<td class="num">'+(r.promise/1000).toFixed(1)+'</td>'+
      '<td class="num">'+(r.earned/1000).toFixed(1)+'</td>'+
      '<td class="num">'+(r.desig/1000).toFixed(1)+'</td>'+
      '<td class="num">'+(r.acct/1000).toFixed(1)+'</td>'+
      '<td class="num under">'+(r.gapBefore/1000).toFixed(1)+'</td>'+
      '<td class="num">$'+r.cpe.toFixed(2)+'</td>';
    tb.appendChild(tr);
  });
  var b=rows[1];
  el('work').textContent=
    'worked for '+b.year+'. The Authority\u2019s own rows: Net Revenues '+m(b.base.net)+
    ' (including '+m(b.base.opr)+' designated), Coverage Account '+m(b.base.cov)+
    ', debt service '+m(b.base.ads)+', boardings '+b.base.enpl.toLocaleString()+
    'k, charge $'+b.base.cpe.toFixed(2)+
    '\n\nours:'+
    '\n  the promise       1.25 \u00d7 '+m(b.base.ads)+' = '+m(b.promise)+
    '\n  what it earns     '+m(b.base.net)+' \u2212 '+m(b.base.opr)+' designated = '+m(b.earned)+
    '\n  short before      '+m(b.promise)+' \u2212 '+m(b.earned)+' = '+m(b.gapBefore)+
    '\n  designated        '+m(b.desig)+
    '\n  coverage account  '+m(b.acct)+
    '\n  stack             '+m(b.total)+(b.total>=b.promise?', over the promise':' , under the promise')+
    '\n\nthe same thing as a ratio, which is how the statement prints it:'+
    '\n  on pledged alone  '+b.alone.toFixed(3)+'      with the account  '+b.printed.toFixed(3);
}

var P={base:[100,25,0,0,1,1],after28:[0,25,0,1,1,1],short:[100,25,-10,0,1,1],
       stack:[0,0,-10,0,0,0]};
[].forEach.call(document.querySelectorAll('.scen button'),function(btn){
  btn.addEventListener('click',function(){
    var p=P[btn.dataset.p];
    s0.value=p[0];s1.value=p[1];s2.value=p[2];s3.value=p[3];
    c0.checked=!!p[4];c1.checked=!!p[5];render();
    [].forEach.call(document.querySelectorAll('.scen button'),function(o){
      o.classList.toggle('on',o===btn)});
  });
});
function manual(){
  [].forEach.call(document.querySelectorAll('.scen button'),function(o){o.classList.remove('on')});
  render();
}
[c0,c1].forEach(function(x){x.addEventListener('change',manual)});
[s0,s1,s2,s3].forEach(function(x){
  x.addEventListener('input',manual);
  // A range input under the cursor swallows the wheel and rewrites itself, so simply
  // scrolling past the dials silently changed the scenario and left the reader looking
  // at numbers that did not match what was on the screen. Take the wheel, scroll by hand.
  x.addEventListener('wheel',function(ev){ev.preventDefault();window.scrollBy(0,ev.deltaY)},
    {passive:false});
});
render();
"""
