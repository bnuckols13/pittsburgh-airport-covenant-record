"""model_page.py — the markup, styling and behaviour of the interactive model.

Design intent, because the first build got it wrong. That version led with a long
caveat, then four sliders each carrying a paragraph, and put the result underneath
all of it. A reader met about twenty lines of instruction before seeing a single
number, and could never see a control and its consequence at the same time.

This one is result first. The answer and the chart sit at the top in a sticky
band and stay there while you work. The primary interaction is a row of named
scenarios, because most readers will never drag anything. The dials, the per-year
table, the worked arithmetic and the full method are all still here, one
disclosure each, for the reader who wants them.

The discipline that makes it publishable lives in build_explainer.py: with every
dial at the Authority's own value the model must reproduce the Authority's own
printed ratios and its charge per boarded passenger, or the build refuses to
write the page.
"""

CSS = """
.hero{position:sticky;top:0;z-index:5;background:var(--plane);padding:.6rem 0 1rem;
margin:0 0 .2rem;border-bottom:1px solid var(--ring)}
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:.9rem;margin:0 0 .8rem}
@media(max-width:640px){.tiles{grid-template-columns:1fr;gap:.45rem}}
.tile b{display:block;font-family:system-ui,sans-serif;font-size:2.05rem;line-height:1.05;
letter-spacing:-.03em;font-variant-numeric:tabular-nums;color:var(--blue)}
.tile.warn b{color:var(--orange)}
.tile span{display:block;font-family:system-ui,sans-serif;font-size:.75rem;color:var(--muted);
margin-top:.15rem;line-height:1.35}
.reading{font-family:system-ui,sans-serif;font-size:1rem;line-height:1.5;margin:0}
.reading em{font-style:normal;color:var(--blue);font-weight:600}
.reading em.warn{color:var(--orange)}
#chart{margin:.15rem 0 0}
.scen{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:.6rem;
margin:1.5rem 0 .7rem}
.scen button{font:inherit;font-family:system-ui,sans-serif;text-align:left;cursor:pointer;
line-height:1.32;
background:var(--surface);border:1px solid var(--ring);border-radius:11px;padding:.7rem .85rem;
color:var(--ink);transition:border-color .12s,transform .12s}
.scen button:hover{border-color:var(--blue);transform:translateY(-1px)}
.scen button.on{border-color:var(--blue);background:color-mix(in srgb,var(--blue) 9%,transparent);
box-shadow:inset 0 0 0 1px var(--blue)}
.scen button strong{display:block;font-size:.89rem;line-height:1.25;margin-bottom:.2rem}
.scen button span{font-size:.755rem;color:var(--muted);line-height:1.35}
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
.caveat{font-family:system-ui,sans-serif;font-size:.78rem;color:var(--muted);margin:.2rem 0 1.4rem}
/* Sticky is a gift on a tall screen and a thief on a short one: the band is about
420px, and on a laptop it was covering the first row of scenarios. Pin it only where
there is room, and let it scroll normally otherwise. */
@media (max-height:820px){.hero{position:static}}
@media print{.scen,.toggle{display:none}.hero{position:static}}
"""

BODY = """
<p class="kicker">Model</p>
<h1>If the Authority decides differently</h1>
<p class="sub">The covenant clears because the Authority makes two discretionary decisions every
year, and its consultant assumes it goes on making them. Change the decisions and read the whole
forecast.</p>

<div class="hero">
  <div class="tiles">
    <div class="tile" id="t1"><b>&#8211;</b><span>&#8211;</span></div>
    <div class="tile" id="t2"><b>&#8211;</b><span>&#8211;</span></div>
    <div class="tile" id="t3"><b>&#8211;</b><span>&#8211;</span></div>
  </div>
  <p class="reading" id="ifthen"></p>
  <svg id="chart" viewBox="0 0 900 300" role="img" aria-label="Coverage ratio across the six forecast years under the settings chosen, against the Authority's own forecast shown as a dotted line."></svg>
</div>

<div class="scen">
  <button data-p="base" class="on"><strong>As the Authority forecasts it</strong>
    <span>Every dial on the document. The baseline.</span></button>
  <button data-p="after28"><strong>After the vote runs out</strong>
    <span>Nothing designated in 2029 and 2030, which no vote covers.</span></button>
  <button data-p="nodesig"><strong>Nothing designated, ever</strong>
    <span>What the Authority actually did in 2024, carried through.</span></button>
  <button data-p="noacct"><strong>No Coverage Account deposit</strong>
    <span>The second lever left at zero.</span></button>
  <button data-p="short"><strong>Traffic ten percent short</strong>
    <span>Watch what this moves, and what it leaves alone.</span></button>
  <button data-p="stack"><strong>All of it at once</strong>
    <span>Both levers down and traffic short.</span></button>
</div>

<p class="caveat">Arithmetic on the Authority's own rows. Not a forecast, and not a prediction. At
the baseline this model reproduces its printed ratios and its charge to the cent, and the build
refuses to publish the page if it does not.</p>

<details class="more"><summary>Adjust it yourself</summary>
  <div class="lev">
    <label for="s0">Designated into the pledge <b id="v0">as forecast</b></label>
    <input type="range" id="s0" min="0" max="110" value="100" step="5">
    <div class="why">Slot-machine tax and gas royalty, as a share of what the Authority assumes.
      A share rather than a sum because it assumes $8.8m for 2025 and $11.575m after, so no single
      figure could mean &#8220;as forecast&#8221; in every year. Moves Net Revenues one for one.</div>
  </div>
  <div class="lev">
    <label for="s3">Apply that <b id="v3">to every year</b></label>
    <input type="range" id="s3" min="0" max="1" value="0" step="1">
    <div class="why">The airlines voted the designation for 2026 through 2028 only.</div>
  </div>
  <div class="lev">
    <label for="s1">Coverage Account deposit <b id="v1">25% of debt service</b></label>
    <input type="range" id="s1" min="0" max="25" value="25" step="1">
    <div class="why">Discretionary, monthly, capped at 25 percent. Moves the printed ratio only:
      the account is not part of pledged Net Revenues.</div>
  </div>
  <div class="lev">
    <label for="s2">Boardings against forecast <b id="v2">as forecast</b></label>
    <input type="range" id="s2" min="-25" max="10" value="0" step="1">
    <div class="why">Holds the airline requirement constant, which is what a residual agreement
      does with fixed costs and debt service.</div>
  </div>
</details>

<details class="more"><summary>Every year, in numbers</summary>
  <div class="scroll"><table id="tbl"><thead><tr>
    <th>year</th><th class="num">designated $m</th><th class="num">net revenues $m</th>
    <th class="num">pledged alone</th><th class="num">as printed</th>
    <th class="num">charge</th><th class="num">vs forecast</th>
  </tr></thead><tbody></tbody></table></div>
</details>

<details class="more"><summary>Show the arithmetic</summary>
  <div class="work" id="work"></div>
</details>

<details class="more"><summary>Where the numbers come from, and what this cannot tell you</summary>
  <p>Every baseline is the Authority's own figure from the April 2025 Official Statement at
  os-2025ab PDF 202 (printed B-16), carried in <code>02-data/coverage-table.csv</code>.
  Designations come from Exhibit E at PDF 316 by way of
  <code>02-data/other-pledged-revenue.csv</code>. The window the airlines actually voted is at
  PDF 67.</p>
  <p>The relationship between a designation and the airline charge is not asserted here. It is
  checked at build time against <code>02-data/who-pays-opr.csv</code>, and separately the whole
  model is required to reproduce the Authority's printed ratios and its charge at baseline before
  this page can be written at all.</p>
  <p>What it cannot tell you: what the Authority will decide, what Harrisburg will do to the
  gaming appropriation, or what traffic will be. It is arithmetic on published rows, and moving a
  dial states a consequence rather than a probability.</p>
  <p>This page never says default, breach or violation. The indenture lets the Coverage Account
  count toward the 1.25 test, and on that test the Authority's forecasts comply in every year.
  Missing the covenant once would not be an event of default either: the indenture requires the
  Authority to hire a consultant, take its advice and raise its rates, and only a second
  consecutive miss after rates have gone up is an Event of Default. The finding here is narrower
  and is stated in those words: what the ratio is on pledged Net Revenues alone.</p>
</details>

<p style="margin-top:2rem"><a href="../covenant/index.html">&#8592; What the two pots are</a>
&#160;&#183;&#160; <a href="../appendix-dataviz/index.html">The plates</a>
&#160;&#183;&#160; <a href="../index.html">The package</a></p>

<p class="src">Built __BUILT__ from the CSVs in <code>02-data/</code>. Rebuild with
<code>python 03-harness/build_explainer.py</code>, check with <code>--check</code>.</p>
"""

JS = r"""
var el=function(i){return document.getElementById(i)};
var s0=el('s0'),s1=el('s1'),s2=el('s2'),s3=el('s3');
function m(k){return '$'+(k/1000).toFixed(1)+'m'}
var NS='http://www.w3.org/2000/svg';
function mk(n,a,t){var e=document.createElementNS(NS,n);for(var k in a)e.setAttribute(k,a[k]);
  if(t!==undefined)e.textContent=t;return e}

function compute(){
  var share=+s0.value/100, pct=+s1.value/100, dpax=+s2.value/100, lateOnly=(+s3.value===1);
  return B.map(function(b){
    var d=(lateOnly && b.year<=2028)?b.opr:b.opr*share;
    var net=b.net-b.opr+d, acct=pct*b.ads, enpl=b.enpl*(1+dpax);
    var req=(b.cpe+b.opr/b.enpl)*b.enpl;   // the airline requirement before any designation
    return {year:b.year,desig:d,net:net,acct:acct,alone:net/b.ads,printed:(net+acct)/b.ads,
            cpe:(req-d)/enpl,base:b};
  });
}
function baseAlone(b){return b.net/b.ads}
function basePrinted(b){return (b.net+b.cov)/b.ads}

function draw(rows){
  // A dumbbell, not lines. The reading this page exists for is a vertical distance:
  // how far pledged revenue sits below 1.25, and how much of the printed ratio is a
  // discretionary deposit. The connector IS the Coverage Account, and a dot either
  // sits in the shaded band under 1.25 or it does not. Dots carry position, not
  // length, so no zero baseline is owed and the scale can show what matters.
  var svg=el('chart'); while(svg.firstChild)svg.removeChild(svg.firstChild);
  var W=900,H=300,L=56,R=104,T=44,BM=44;
  var v=[1.25];
  rows.forEach(function(r){v.push(r.alone,r.printed,baseAlone(r.base))});
  var lo=Math.min.apply(null,v),hi=Math.max.apply(null,v);
  var pad=(hi-lo)*0.18||0.1; lo-=pad; hi+=pad;
  var X=function(i){return L+i*(W-L-R)/(rows.length-1)};
  var Y=function(t){return H-BM-(t-lo)/(hi-lo)*(H-BM-T)};
  var half=((W-L-R)/(rows.length-1))/2, x0=L-half*0.55, x1=W-R+half*0.55;

  // a scale, so the dots are anchored to something other than each other
  var step=(hi-lo)>0.75?0.2:0.1;
  for(var t=Math.ceil(lo/step)*step;t<hi;t+=step){
    if(Math.abs(t-1.25)<step*0.4) continue;          // never crowd the covenant rule
    svg.appendChild(mk('line',{x1:x0,y1:Y(t),x2:x1,y2:Y(t),stroke:'var(--grid)'}));
    svg.appendChild(mk('text',{x:x0-8,y:Y(t)+4,'text-anchor':'end','class':'ax'},t.toFixed(2)));
  }

  // under 1.25 is a region a dot is inside or outside, not a line to remember
  svg.appendChild(mk('rect',{x:x0,y:Y(1.25),width:x1-x0,height:(H-BM)-Y(1.25),
    fill:'var(--orange)','fill-opacity':0.07}));
  svg.appendChild(mk('line',{x1:x0,y1:Y(1.25),x2:x1,y2:Y(1.25),stroke:'var(--ink2)',
    'stroke-width':1.4,'stroke-dasharray':'5 3'}));
  svg.appendChild(mk('text',{x:x1+9,y:Y(1.25)+4,'class':'lab2'},'1.25'));
  svg.appendChild(mk('text',{x:x1+9,y:Y(1.25)+18,'class':'ax'},'the covenant'));

  var xi=-1; rows.forEach(function(r,i){if(xi<0&&r.year>2028)xi=i});
  if(xi>0){
    svg.appendChild(mk('rect',{x:X(xi)-half,y:T-6,width:x1-(X(xi)-half),height:(H-BM)-(T-6),
      fill:'var(--yellow)','fill-opacity':0.10}));
    svg.appendChild(mk('text',{x:X(xi)-half+8,y:T+9,'class':'ax'},'no vote covers these years'));
  }

  rows.forEach(function(r,i){
    var x=X(i), yA=Y(r.alone), yP=Y(r.printed), yB=Y(baseAlone(r.base));
    if(Math.abs(yB-yA)>2){
      svg.appendChild(mk('line',{x1:x-9,y1:yB,x2:x+9,y2:yB,stroke:'var(--muted)',
        'stroke-width':1.4,'stroke-dasharray':'3 2'}));
    }
    svg.appendChild(mk('line',{x1:x,y1:yA,x2:x,y2:yP,stroke:'var(--blue-lt)',
      'stroke-width':10,'stroke-linecap':'round',opacity:.5}));
    svg.appendChild(mk('circle',{cx:x,cy:yP,r:5,fill:'var(--plane)',
      stroke:'var(--blue-lt)','stroke-width':2.2}));
    svg.appendChild(mk('circle',{cx:x,cy:yA,r:5.8,
      fill:r.alone<1.25?'var(--orange)':'var(--blue)'}));
    // only the filled dot is labelled; the open dot has the scale
    svg.appendChild(mk('text',{x:x,y:yA+21,'text-anchor':'middle','class':'val',
      fill:r.alone<1.25?'var(--orange)':'var(--ink)'},r.alone.toFixed(2)));
    svg.appendChild(mk('text',{x:x,y:H-BM+18,'text-anchor':'middle','class':'ax'},r.year));
  });

  // name the connector once, on the year where it does the most work, and only when it
  // does any: at a deposit of zero the dots coincide and a label pointing at nothing
  // reads as a broken chart rather than as an empty account.
  var wide=rows.reduce(function(a,b){return (b.printed-b.alone)>(a.printed-a.alone)?b:a});
  var wi=rows.indexOf(wide);
  if(Y(wide.alone)-Y(wide.printed)>18){
    svg.appendChild(mk('text',{x:X(wi)+15,y:(Y(wide.alone)+Y(wide.printed))/2+4,'class':'ax'},
      'the Coverage Account'));
  } else {
    svg.appendChild(mk('text',{x:x0,y:T-6,'class':'ax',fill:'var(--orange)'},
      'no Coverage Account deposit: the two readings coincide'));
  }

  // one legend, drawn by the same shapes that draw the data
  svg.appendChild(mk('circle',{cx:x0+6,cy:12,r:5.8,fill:'var(--blue)'}));
  svg.appendChild(mk('text',{x:x0+17,y:16,'class':'ax'},'pledged Net Revenues alone'));
  svg.appendChild(mk('circle',{cx:x0+200,cy:12,r:5,fill:'var(--plane)',
    stroke:'var(--blue-lt)','stroke-width':2.2}));
  svg.appendChild(mk('text',{x:x0+211,y:16,'class':'ax'},'as the statement prints it'));
  svg.appendChild(mk('line',{x1:x0+378,y1:12,x2:x0+394,y2:12,stroke:'var(--muted)',
    'stroke-width':1.4,'stroke-dasharray':'3 2'}));
  svg.appendChild(mk('text',{x:x0+400,y:16,'class':'ax'},
    'where the Authority’s forecast puts it'));
  svg.appendChild(mk('line',{x1:x0,y1:H-BM,x2:x1,y2:H-BM,stroke:'var(--axis)'}));
}

function tiles(rows){
  var under=rows.filter(function(r){return r.alone<1.25});
  var worst=rows.reduce(function(a,b){return b.alone<a.alone?b:a});
  var chg=rows.map(function(r,i){return r.cpe-B[i].cpe});
  var big=chg.reduce(function(a,b){return Math.abs(b)>Math.abs(a)?b:a},0);
  function set(id,val,lab,warn){
    var t=el(id); t.querySelector('b').textContent=val;
    t.querySelector('span').textContent=lab; t.classList.toggle('warn',!!warn);
  }
  set('t1',worst.alone.toFixed(2),'lowest on pledged revenue alone, in '+worst.year,
      worst.alone<1.25);
  set('t2',under.length+' of '+rows.length,'forecast years under 1.25 on pledged revenue alone',
      under.length>0);
  set('t3',(Math.abs(big)<0.005?'no change':(big>0?'+':'−')+'$'+Math.abs(big).toFixed(2)),
      'to the charge per boarded passenger, against the forecast',big>0.005);
}

function sentence(rows){
  var under=rows.filter(function(r){return r.alone<1.25});
  var nB=B.filter(function(b){return baseAlone(b)<1.25}).length;
  var worst=rows.reduce(function(a,b){return b.alone<a.alone?b:a});
  var f=document.createDocumentFragment();
  function t(x){f.appendChild(document.createTextNode(x))}
  function e(x,w){var n=document.createElement('em');n.textContent=x;
    if(w)n.className='warn';f.appendChild(n)}
  if(!under.length){ t('Pledged Net Revenues alone clear 1.25 in every forecast year. '); }
  else{
    t('Pledged Net Revenues alone come in under 1.25 in ');
    e(under.length+' of '+rows.length,true);
    t(' forecast years, lowest at '); e(worst.alone.toFixed(2),true);
    t(' in '+worst.year+'. ');
  }
  t('The Authority’s own forecast has '+nB+' of '+rows.length+'. ');
  if(+s3.value===1) t('This change applies only to 2029 and 2030, the years the January 2025 '+
    'majority-in-interest vote does not cover.');
  return f;
}

function render(){
  var rows=compute();
  el('v0').textContent=(+s0.value===100?'as forecast':(+s0.value===0?'nothing':(+s0.value)+'%'));
  el('v1').textContent=(+s1.value)+'% of debt service';
  var dp=+s2.value; el('v2').textContent=(dp===0?'as forecast':(dp>0?'+':'')+dp+'%');
  el('v3').textContent=(+s3.value===1?'only to 2029 and 2030':'to every year');
  tiles(rows); draw(rows);
  var p=el('ifthen'); p.innerHTML=''; p.appendChild(sentence(rows));
  var tb=el('tbl').querySelector('tbody'); tb.innerHTML='';
  rows.forEach(function(r,i){
    var d=r.cpe-B[i].cpe, tr=document.createElement('tr');
    tr.innerHTML='<td>'+r.year+(r.year>2028?'<span class="nv">no vote</span>':'')+'</td>'+
      '<td class="num">'+(r.desig/1000).toFixed(1)+'</td>'+
      '<td class="num">'+(r.net/1000).toFixed(1)+'</td>'+
      '<td class="num'+(r.alone<1.25?' under':'')+'">'+r.alone.toFixed(2)+'</td>'+
      '<td class="num">'+r.printed.toFixed(2)+'</td>'+
      '<td class="num">$'+r.cpe.toFixed(2)+'</td>'+
      '<td class="num">'+(Math.abs(d)<0.005?'—':(d>0?'+':'−')+'$'+Math.abs(d).toFixed(2))+'</td>';
    tb.appendChild(tr);
  });
  var b=rows[1];
  el('work').textContent=
    'worked for '+b.year+'. The Authority’s own rows: Net Revenues '+m(b.base.net)+
    ' (including '+m(b.base.opr)+' designated), Coverage Account '+m(b.base.cov)+', debt service '+
    m(b.base.ads)+', boardings '+b.base.enpl.toLocaleString()+'k, charge $'+b.base.cpe.toFixed(2)+
    '\n\nours, from the dials:'+
    '\n  net revenues      '+m(b.base.net)+' − '+m(b.base.opr)+' + '+m(b.desig)+' = '+m(b.net)+
    '\n  pledged alone     '+m(b.net)+' ÷ '+m(b.base.ads)+' = '+b.alone.toFixed(3)+
    '\n  coverage account  '+(+s1.value)+'% × '+m(b.base.ads)+' = '+m(b.acct)+
    '\n  as printed        ('+m(b.net)+' + '+m(b.acct)+') ÷ '+m(b.base.ads)+' = '+b.printed.toFixed(3)+
    '\n  charge            requirement less '+m(b.desig)+' designated, over boardings = $'+b.cpe.toFixed(2);
}

var P={base:[100,25,0,0],after28:[0,25,0,1],nodesig:[0,25,0,0],
       noacct:[100,0,0,0],short:[100,25,-10,0],stack:[0,0,-10,0]};
[].forEach.call(document.querySelectorAll('.scen button'),function(btn){
  btn.addEventListener('click',function(){
    var p=P[btn.dataset.p];
    s0.value=p[0];s1.value=p[1];s2.value=p[2];s3.value=p[3];render();
    [].forEach.call(document.querySelectorAll('.scen button'),function(o){
      o.classList.toggle('on',o===btn)});
  });
});
[s0,s1,s2,s3].forEach(function(x){
  x.addEventListener('input',function(){
    [].forEach.call(document.querySelectorAll('.scen button'),function(o){o.classList.remove('on')});
    render();
  });
  // A range input under the cursor swallows the wheel and rewrites itself, so simply
  // scrolling past the dials silently changed the scenario and left the reader looking
  // at numbers that did not match what was on the screen. Take the wheel, scroll by hand.
  x.addEventListener('wheel',function(ev){ev.preventDefault();window.scrollBy(0,ev.deltaY)},
    {passive:false});
});
render();
"""
