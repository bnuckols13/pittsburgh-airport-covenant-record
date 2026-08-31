"""model_page.py — the markup and behaviour of the interactive model.

Kept apart from build_explainer.py because it is mostly a long template, and
because the model is a reading instrument rather than a published plate. The
plates are generated at build time and never move; this page recomputes in the
reader's browser as they move the dials.

The discipline that makes it publishable lives in build_explainer.py: with every
dial at the Authority's own forecast value the model must reproduce the
Authority's own printed ratios and its charge per boarded passenger, or the
build refuses to write the page.
"""

BODY = """
<p class="kicker">Model</p>
<h1>If the Authority decides differently</h1>
<p class="sub">The covenant clears because the Authority makes two decisions every year, and its
consultant assumes it goes on making them. Change the decisions and read the whole forecast,
rather than one year of it.</p>

<div class="disc"><b>Arithmetic on documents. Not a forecast, and not a prediction.</b> Every
baseline here is the Authority's own figure from the April 2025 Official Statement, page-cited in
<code>02-data/coverage-table.csv</code>. With every dial left at the Authority's own value this
model reproduces its printed ratios and its charge to the cent, and the build refuses to ship the
page if it does not. Everything away from that baseline is our arithmetic, and it is written out
in full at the bottom. The model knows nothing the documents do not say, and it cannot tell you
what the Authority will choose.</div>

<div class="rig">
  <div class="presets">
    <button data-p="base" class="on">As the Authority forecasts it</button>
    <button data-p="after28">Nothing designated once the vote runs out</button>
    <button data-p="nodesig">Nothing designated, ever</button>
    <button data-p="halve">Gaming halved</button>
    <button data-p="noacct">No Coverage Account deposit</button>
    <button data-p="short">Traffic 10 percent short</button>
    <button data-p="stack">All of it at once</button>
  </div>

  <div class="lev">
    <label for="s0">Designated into the pledge <b id="v0">as forecast</b></label>
    <input type="range" id="s0" min="0" max="110" value="100" step="5">
    <div class="why">Other Pledged Revenues: slot-machine tax and gas royalty. Shown as a share of
      what the Authority itself assumes, because it assumes $8.8m for 2025 and $11.575m after, so
      one dollar figure could not mean "as forecast" in every year. It takes in about $12.4m a
      year in gaming money and designates as much as it chooses, or none, as it did in 2024. Moves
      Net Revenues one for one and the airline charge by the same amount over boardings.</div>
  </div>
  <div class="lev">
    <label for="s3">Apply that change <b id="v3">to every forecast year</b></label>
    <input type="range" id="s3" min="0" max="1" value="0" step="1">
    <div class="why">The airlines voted the designation for 2026 through 2028. 2029 and 2030 sit
      past it. Slide right to change only the years no vote covers.</div>
  </div>
  <div class="lev">
    <label for="s1">Coverage Account deposit <b id="v1">25% of debt service</b></label>
    <input type="range" id="s1" min="0" max="25" value="25" step="1">
    <div class="why">Funded monthly at the Authority's discretion and capped at 25 percent. The
      forecast assumes the ceiling in five of its six years. This moves the printed ratio only:
      the account is not part of pledged Net Revenues.</div>
  </div>
  <div class="lev">
    <label for="s2">Boardings against forecast <b id="v2">as forecast</b></label>
    <input type="range" id="s2" min="-25" max="10" value="0" step="1">
    <div class="why">Holds the airline requirement constant, which is what a residual agreement
      does with fixed costs and debt service. Watch which line this moves and which it leaves
      alone.</div>
  </div>

  <p class="ifthen" id="ifthen"></p>
  <svg id="chart" viewBox="0 0 900 300" role="img" aria-label="Coverage ratio across the six forecast years under the settings chosen. A dotted line shows the Authority's own forecast for comparison."></svg>

  <div class="scroll"><table id="tbl"><thead><tr>
    <th>year</th><th class="num">designated $m</th><th class="num">net revenues $m</th>
    <th class="num">pledged alone</th><th class="num">as printed</th>
    <th class="num">charge</th><th class="num">vs forecast</th>
  </tr></thead><tbody></tbody></table></div>
  <div class="work" id="work"></div>
</div>

<div class="note"><b>What the boardings lever teaches.</b> Drag it a long way down. The coverage
lines barely stir while the charge climbs. That is the residual agreement working exactly as
written: when traffic disappoints, the carriers are billed the difference and the covenant is
insulated from it. It is also why the passengers arriving on forecast, which they did in 2024,
settles less than it appears to.</div>

<p><a href="../covenant/index.html">&#8592; What the two pots are</a> &#160;&#183;&#160;
<a href="../appendix-dataviz/index.html">The plates</a> &#160;&#183;&#160;
<a href="../index.html">The package</a></p>

<p class="src">Baselines: <code>02-data/coverage-table.csv</code>, from os-2025ab PDF 202 (printed
B-16). Designations: <code>other-pledged-revenue.csv</code>, from PDF 316. The commitment window
is from PDF 67. The charge relationship is checked at build time against
<code>who-pays-opr.csv</code>. This page never says default, breach or violation, because on the
covenant as written the Authority's forecasts comply. Built __BUILT__.</p>
"""

JS = r"""
var el=function(i){return document.getElementById(i)};
var s0=el('s0'),s1=el('s1'),s2=el('s2'),s3=el('s3');
function m(k){return '$'+(k/1000).toFixed(1)+'m'}
var NS='http://www.w3.org/2000/svg';
function mk(n,a,txt){var e=document.createElementNS(NS,n);for(var k in a)e.setAttribute(k,a[k]);
  if(txt!==undefined)e.textContent=txt;return e}

function compute(){
  var share=+s0.value/100, pct=+s1.value/100, dpax=+s2.value/100, lateOnly=(+s3.value===1);
  return B.map(function(b){
    var d=(lateOnly && b.year<=2028)?b.opr:b.opr*share;
    var net=b.net-b.opr+d;
    var acct=pct*b.ads;
    var enpl=b.enpl*(1+dpax);
    var req=(b.cpe+b.opr/b.enpl)*b.enpl;   // the airline requirement before any designation
    return {year:b.year,desig:d,net:net,acct:acct,
            alone:net/b.ads, printed:(net+acct)/b.ads,
            cpe:(req-d)/enpl, base:b, voted:(b.year>=2026 && b.year<=2028)};
  });
}

function draw(rows){
  var svg=el('chart'); while(svg.firstChild)svg.removeChild(svg.firstChild);
  var W=900,H=300,L=54,R=168,T=16,BM=46;
  var v=[1.25];
  rows.forEach(function(r){v.push(r.alone,r.printed,
    r.base.net/r.base.ads,(r.base.net+r.base.cov)/r.base.ads)});
  var lo=Math.min.apply(null,v),hi=Math.max.apply(null,v);
  var pad=(hi-lo)*0.14||0.1; lo-=pad; hi+=pad;
  var X=function(i){return L+i*(W-L-R)/(rows.length-1)};
  var Y=function(t){return H-BM-(t-lo)/(hi-lo)*(H-BM-T)};

  var step=(hi-lo)>0.9?0.2:0.1;
  for(var t=Math.ceil(lo/step)*step;t<=hi;t+=step){
    svg.appendChild(mk('line',{x1:L,y1:Y(t),x2:W-R,y2:Y(t),stroke:'var(--grid)'}));
    svg.appendChild(mk('text',{x:L-8,y:Y(t)+4,'text-anchor':'end','class':'ax'},t.toFixed(2)));
  }
  // the years no majority-in-interest vote covers
  var firstUn=rows.filter(function(r){return !r.voted && r.year>2028})[0];
  if(firstUn){
    var xi=rows.indexOf(firstUn);
    svg.appendChild(mk('rect',{x:X(xi)-((W-L-R)/(rows.length-1))/2,y:T,
      width:(W-R)-(X(xi)-((W-L-R)/(rows.length-1))/2),height:H-BM-T,
      fill:'var(--yellow)','fill-opacity':0.10}));
    svg.appendChild(mk('text',{x:X(xi)+4,y:T+13,'class':'ax'},'no vote covers these years'));
  }
  svg.appendChild(mk('line',{x1:L,y1:Y(1.25),x2:W-R,y2:Y(1.25),stroke:'var(--ink2)',
    'stroke-width':1.4,'stroke-dasharray':'5 3'}));
  svg.appendChild(mk('text',{x:W-R+8,y:Y(1.25)+4,'class':'lab2'},'1.25, the covenant'));

  // the Authority's own forecast, faint, so the deviation is seen rather than remembered
  [['alone',function(r){return r.base.net/r.base.ads}],
   ['printed',function(r){return (r.base.net+r.base.cov)/r.base.ads}]].forEach(function(c){
    var d=rows.map(function(r,i){return (i?'L':'M')+X(i)+','+Y(c[1](r))}).join(' ');
    svg.appendChild(mk('path',{d:d,fill:'none',stroke:'var(--muted)','stroke-width':1,
      'stroke-dasharray':'2 3',opacity:0.75}));
  });

  [['printed','var(--blue-lt)','as the statement prints it'],
   ['alone','var(--blue)','on pledged revenue alone']].forEach(function(c){
    var k=c[0],col=c[1];
    var d=rows.map(function(r,i){return (i?'L':'M')+X(i)+','+Y(r[k])}).join(' ');
    svg.appendChild(mk('path',{d:d,fill:'none',stroke:col,'stroke-width':2.4,
      'stroke-linejoin':'round'}));
    rows.forEach(function(r,i){svg.appendChild(mk('circle',{cx:X(i),cy:Y(r[k]),r:4,fill:col}))});
    var last=rows[rows.length-1];
    svg.appendChild(mk('text',{x:W-R+8,y:Y(last[k])+4,'class':'lab2',fill:col},c[2]));
  });
  rows.forEach(function(r,i){
    svg.appendChild(mk('text',{x:X(i),y:H-BM+18,'text-anchor':'middle','class':'ax'},r.year));
    svg.appendChild(mk('text',{x:X(i),y:H-BM+31,'text-anchor':'middle','class':'ax',
      fill:r.alone<1.25?'var(--orange)':'var(--muted)'},r.alone.toFixed(2)));
  });
  svg.appendChild(mk('line',{x1:L,y1:H-BM,x2:W-R,y2:H-BM,stroke:'var(--axis)'}));
  svg.appendChild(mk('text',{x:W-R+8,y:H-BM-2,'class':'ax',fill:'var(--muted)'},
    'dotted: the Authority’s forecast'));
}

function sentence(rows){
  var under=rows.filter(function(r){return r.alone<1.25});
  var nBase=B.filter(function(b){return b.net/b.ads<1.25}).length;
  var chg=rows.map(function(r,i){return r.cpe-B[i].cpe});
  var up=Math.max.apply(null,chg), dn=Math.min.apply(null,chg);
  var s;
  if(!under.length){
    s='On these settings pledged Net Revenues alone clear 1.25 in every forecast year. ';
  }else{
    var worst=under.reduce(function(a,b){return b.alone<a.alone?b:a});
    s='On these settings, pledged Net Revenues alone come in under 1.25 in '+under.length+' of '+
      rows.length+' forecast years ('+under.map(function(r){return r.year}).join(', ')+
      '), lowest at '+worst.alone.toFixed(2)+' in '+worst.year+'. ';
  }
  s+='The Authority’s own forecast has '+nBase+' of '+rows.length+'. ';
  if(up>0.005) s+='The charge to airlines rises as much as $'+up.toFixed(2)+
    ' a boarded passenger above the forecast. ';
  else if(dn<-0.005) s+='The charge to airlines falls as much as $'+Math.abs(dn).toFixed(2)+
    ' a boarded passenger below the forecast. ';
  if(+s3.value===1) s+='The change applies only to 2029 and 2030, the years the January 2025 '+
    'majority-in-interest vote does not cover.';
  return s;
}

function render(){
  var rows=compute();
  var sh=+s0.value;
  el('v0').textContent=(sh===100?'as forecast':(sh===0?'nothing at all':sh+'% of the forecast'))
    +(sh===100?'':' ('+m(B[1].opr*sh/100)+' in 2026)');
  el('v1').textContent=(+s1.value)+'% of debt service';
  var dp=+s2.value;
  el('v2').textContent=(dp===0?'as forecast':(dp>0?'+':'')+dp+'%');
  el('v3').textContent=(+s3.value===1?'only to 2029 and 2030':'to every forecast year');
  el('ifthen').textContent=sentence(rows);
  draw(rows);
  var tb=el('tbl').querySelector('tbody'); tb.innerHTML='';
  rows.forEach(function(r,i){
    var d=r.cpe-B[i].cpe;
    var tr=document.createElement('tr');
    tr.innerHTML='<td>'+r.year+(r.year>2028?' <span class="nv">no vote</span>':'')+'</td>'+
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

var P={base:[100,25,0,0], after28:[0,25,0,1], nodesig:[0,25,0,0], halve:[50,25,0,0],
       noacct:[100,0,0,0], short:[100,25,-10,0], stack:[0,0,-10,0]};
[].forEach.call(document.querySelectorAll('.presets button'),function(btn){
  btn.addEventListener('click',function(){
    var p=P[btn.dataset.p];
    s0.value=p[0];s1.value=p[1];s2.value=p[2];s3.value=p[3];render();
    [].forEach.call(document.querySelectorAll('.presets button'),function(o){
      o.classList.toggle('on',o===btn)});
  });
});
[s0,s1,s2,s3].forEach(function(x){
  x.addEventListener('input',function(){
    [].forEach.call(document.querySelectorAll('.presets button'),function(o){
      o.classList.remove('on')});
    render();
  });
  // A range input under the cursor swallows the wheel and rewrites itself, so simply
  // scrolling past this rig silently changed the scenario and the reader was left
  // looking at numbers that did not match the dials. Take the wheel and scroll the
  // page by hand instead. Keyboard arrows still adjust the slider when it is focused.
  x.addEventListener('wheel',function(e){
    e.preventDefault();
    window.scrollBy(0,e.deltaY);
  },{passive:false});
});
render();
"""
