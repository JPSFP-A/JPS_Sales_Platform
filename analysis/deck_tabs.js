let caseSel=null, wowMet='rev', movCls='RT50', movMode='topbot', movMet='kwh';
let tmMet='rev', tmView='customer';
function renderTopMovers(){
  const MV=D.movers; if(!MV){document.getElementById('app').innerHTML='<div class="card">Top movers not available — rebuild data.</div>';return;}
  if(tmView==='bucket'&&tmMet==='dem')tmMet='vol';
  const div=tmMet==='vol'?1000:1e6, un=tmMet==='vol'?'GWh':'J$M';
  const data=(tmView==='customer'?MV.byCustomer[tmMet]:MV.byBucketRT10[tmMet])||[];
  const lab=r=>r.name||r.bucket;
  let h='<div class="ctrl"><span class="lbl">Metric</span><div class="seg">'+
    [['vol','Volume'],['dem','Demand'],['rev','Revenue']].map(o=>'<button data-tmm="'+o[0]+'" class="'+(tmMet===o[0]?'on':'')+'"'+(o[0]==='dem'&&tmView==='bucket'?' disabled style="opacity:.4"':'')+'>'+o[1]+'</button>').join('')+'</div>'+
    '<div class="seg"><button data-tmv="customer" class="'+(tmView==='customer'?'on':'')+'">By customer · RT40/50/70</button><button data-tmv="bucket" class="'+(tmView==='bucket'?'on':'')+'">RT10 buckets</button></div></div>';
  h+='<div style="margin:0 2px 8px;color:var(--mut);font-size:12px">'+MV.window+' · Actual − estimated budget ('+un+') · est. budget = Jan/Feb share × seasonally-shaped class budget</div>';
  h+='<div class="grid"><div class="card"><div class="chartttl">Top variance movers · '+(tmMet==='vol'?'Volume':tmMet==='dem'?'Demand':'Revenue')+' ('+un+')</div><div class="chartwrap" style="height:'+(Math.min(data.length,20)*26+90)+'px"><canvas id="c"></canvas></div></div>'+
     '<div class="card" style="padding:10px"><div class="tbl"><table><thead><tr><th class="l">'+(tmView==='customer'?'Customer':'Bucket')+'</th><th>Actual</th><th>Est. Bud</th><th>Var</th></tr></thead><tbody id="tb"></tbody></table></div></div></div>';
  document.getElementById('app').innerHTML=h;
  const top=data.slice(0,20);
  barChart('c',top.map(r=>lab(r).slice(0,26)),top.map(r=>+(r.var/div).toFixed(2)),top.map(r=>r.var>=0?'#1D9E75':'#E24B4A'),v=>(v>=0?'+':'')+(+v).toFixed(1),{x:{grid:{color:'#223247'}},y:{grid:{display:false},ticks:{font:{size:10.5}}}},true);
  document.getElementById('tb').innerHTML=data.slice(0,80).map(r=>'<tr><td class="l">'+esc(lab(r)).slice(0,26)+(r.cls?' <span class="badge">'+r.cls+'</span>':'')+'</td><td>'+(r.act/div).toFixed(1)+'</td><td>'+(r.bud/div).toFixed(1)+'</td><td class="'+(r.var>=0?'up':'dn')+'">'+(r.var>=0?'+':'')+(r.var/div).toFixed(1)+'</td></tr>').join('');
  document.querySelectorAll('[data-tmm]').forEach(b=>b.onclick=()=>{tmMet=b.dataset.tmm;renderTopMovers();});
  document.querySelectorAll('[data-tmv]').forEach(b=>b.onclick=()=>{tmView=b.dataset.tmv;renderTopMovers();});
}
let aBase=null, aCur=null;
function aIdx(){if(aBase==null)aBase=D.months[0];if(aCur==null)aCur=D.months[D.months.length-1];return [D.months.indexOf(aBase),D.months.indexOf(aCur)];}
function periodSel(){return '<span class="lbl">Compare</span><select id="aB">'+D.months.map((m,i)=>'<option value="'+m+'"'+(aBase===m?' selected':'')+'>'+D.mlabels[i]+'</option>').join('')+'</select><span class="lbl">→</span><select id="aC">'+D.months.map((m,i)=>'<option value="'+m+'"'+(aCur===m?' selected':'')+'>'+D.mlabels[i]+'</option>').join('')+'</select>';}
function bindPeriod(fn){document.getElementById('aB').onchange=e=>{aBase=e.target.value;fn();};document.getElementById('aC').onchange=e=>{aCur=e.target.value;fn();};}
function dlbl(fmt){return {display:true,anchor:'end',align:'end',clip:false,formatter:fmt,color:'#c7d3e0',font:{size:11,weight:500}};}
function barChart(id,labels,data,colors,fmt,scales,horiz,onClickBar){
  if(chart)chart.destroy();
  chart=new Chart(document.getElementById(id),{type:'bar',data:{labels,datasets:[{data,backgroundColor:colors,borderRadius:3}]},
    options:{indexAxis:horiz?'y':'x',responsive:true,maintainAspectRatio:false,onClick:onClickBar?(evt,els)=>{if(els.length)onClickBar(els[0].index);}:undefined,plugins:{legend:{display:false},datalabels:dlbl(fmt),tooltip:{callbacks:{label:c=>fmt(c.raw)}}},scales:scales}});
  if(onClickBar&&document.getElementById(id))document.getElementById(id).style.cursor='pointer';
}
const ANSWER_FIELDS=['kwh','energy','fuel','ipp','dem','cust'];
const ANSWER_UNITS={kwh:['kWh (M)',1e6,''],energy:['Energy (J$M)',1e6,'J$'],fuel:['Fuel (J$M)',1e6,'J$'],ipp:['IPP (J$M)',1e6,'J$'],dem:['Demand charge (J$M)',1e6,'J$'],cust:['Customer charge (J$M)',1e6,'J$']};
let _contribCtx=null;
const _safeId=s=>String(s).replace(/[^\w]/g,'_');
function renderAnswerContributors(idx,iA,iB){
  const field=ANSWER_FIELDS[idx],[label,div,pfx]=ANSWER_UNITS[field];
  const dv=a=>((a[field]?a[field][iB]:0)-(a[field]?a[field][iA]:0));
  const rows=D.accts.map(a=>({id:a.id,n:a.n,c:a.c,d:dv(a)})).sort((x,y)=>y.d-x.d);
  const top=rows.slice(0,10),bot=rows.slice(-10).reverse();
  _contribCtx={top,bot,label,div,pfx,iA,iB};
  const row=r=>{
    const sid=_safeId(r.id);
    return '<tr style="cursor:pointer" onclick="toggleContribRow(\''+r.id+'\')"><td class="l"><span id="carrow-'+sid+'" style="color:var(--mut);display:inline-block;width:12px">&#9656;</span>'+esc(r.n).slice(0,26)+'</td><td><span class="badge">'+r.c+'</span></td><td class="'+(r.d>=0?'up':'dn')+'">'+(r.d>=0?'+':'')+pfx+(Math.abs(r.d)/div).toFixed(1)+'</td></tr>'+
      '<tr id="cdet-'+sid+'" style="display:none"><td colspan="3" style="padding:0"><div id="cbody-'+sid+'" style="padding:8px 6px 10px 22px;background:#F8FAFC;border-left:2px solid var(--yel)"></div></td></tr>';
  };
  const el=document.getElementById('answer-contrib');
  if(!el)return;
  el.innerHTML='<div style="display:flex;justify-content:space-between;align-items:center;margin:8px 0 4px;border-top:1px solid var(--line);padding-top:8px"><div style="font-size:10px;font-weight:700;color:var(--mut);letter-spacing:1px">TOP 10 / BOTTOM 10 · '+label+' — '+D.mlabels[iA]+' → '+D.mlabels[iB]+' <span style="font-weight:400;text-transform:none;letter-spacing:0">(click a row to expand accounts)</span></div><button class="chip" id="contrib-export-btn" onclick="exportContributors()" style="border-color:var(--yel);color:var(--yel);font-weight:700">⬇ Excel</button></div>'+
    '<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:11px"><thead><tr style="color:var(--mut);text-align:left"><th class="l" style="padding:2px 4px">Customer</th><th style="padding:2px 4px">Cls</th><th style="padding:2px 4px;text-align:right">Δ '+label+'</th></tr></thead><tbody>'+
    top.map(row).join('')+'<tr><td colspan="3" style="padding:2px 4px;color:var(--mut);font-size:10px">— bottom 10 —</td></tr>'+bot.map(row).join('')+
    '</tbody></table></div>';
}
function toggleContribRow(id){
  const sid=_safeId(id);
  const tr=document.getElementById('cdet-'+sid), arrow=document.getElementById('carrow-'+sid);
  if(!tr)return;
  const opening=tr.style.display==='none';
  tr.style.display=opening?'table-row':'none';
  if(arrow)arrow.innerHTML=opening?'&#9662;':'&#9656;';
  if(!opening)return;
  const body=document.getElementById('cbody-'+sid);
  if(!body||body.dataset.loaded)return;
  body.dataset.loaded='1';
  const a=D.accts.find(x=>x.id===id);if(!a){body.innerHTML='';return;}
  const {iA,iB}=_contribCtx;
  body.innerHTML=buildTrend6mo(a,iB)+'<div style="margin-top:4px"><a href="javascript:void(0)" onclick="event.stopPropagation();pickAt(\''+id+'\','+iA+','+iB+')" style="font-size:11px;color:var(--blu);font-weight:700">&#8599; Full detail</a></div>'+
    '<div id="cacc-'+sid+'" style="margin-top:6px;color:var(--mut);font-size:11px">Loading accounts…</div>';
  _fetchAccts(a.n,D.months[iA],D.months[iB]).then(({rows,err})=>{
    const accEl=document.getElementById('cacc-'+sid);if(!accEl)return;
    accEl.innerHTML=_renderAcctTable(rows,D.mlabels[iA],D.mlabels[iB],err);
    body._acctRows=rows;
  });
}
window.toggleContribRow=toggleContribRow;
async function exportContributors(){
  if(!_contribCtx)return;
  const {top,bot,label,div,pfx,iA,iB}=_contribCtx;
  const lb=D.mlabels[iA],lc=D.mlabels[iB];
  const btn=document.getElementById('contrib-export-btn');
  const origTxt=btn?btn.textContent:'';
  if(btn){btn.textContent='Building…';btn.disabled=true;}
  const all=top.map((r,i)=>({...r,rank:i+1,grp:'TOP 10'})).concat(bot.map((r,i)=>({...r,rank:i+1,grp:'BOTTOM 10'})));
  const fetched=await Promise.all(all.map(r=>{
    const a=D.accts.find(x=>x.id===r.id);
    if(!a)return Promise.resolve({rows:[]});
    return _fetchAccts(a.n,D.months[iA],D.months[iB]);
  }));
  const hdr=['Rank','Customer','Class','Δ '+label,'A/C No.','Parish','kWh '+lb,'kWh '+lc,'Rev '+lb+' (J$M)','Rev '+lc+' (J$M)'];
  const aoa=[hdr]; const rowMeta=[null];
  let curGrp=null;
  all.forEach((r,i)=>{
    if(r.grp!==curGrp){curGrp=r.grp;aoa.push([curGrp,'','','','','','','','','']);rowMeta.push(null);}
    aoa.push([r.rank,r.n,r.c,+(r.d/div).toFixed(2),'','','','','','']);rowMeta.push({level:0});
    (fetched[i].rows||[]).forEach(ar=>{
      aoa.push(['','','','',ar.ac,ar.parish||'',
        ar.base?.kwh!=null?+(ar.base.kwh/1000).toFixed(1):'',ar.cur?.kwh!=null?+(ar.cur.kwh/1000).toFixed(1):'',
        ar.base?.rev!=null?+(ar.base.rev/1e6).toFixed(2):'',ar.cur?.rev!=null?+(ar.cur.rev/1e6).toFixed(2):'']);
      rowMeta.push({level:1});
    });
  });
  const fname='JPS_'+label.replace(/[^\w]+/g,'_')+'_Movers_'+lb+'_to_'+lc;
  if(window.XLSX){
    const ws=XLSX.utils.aoa_to_sheet(aoa);
    ws['!rows']=rowMeta.map(m=>m?{level:m.level}:undefined);
    ws['!outline']={summaryBelow:false};
    const wb=XLSX.utils.book_new(); XLSX.utils.book_append_sheet(wb,ws,'Movers'); XLSX.writeFile(wb,fname+'.xlsx');
  } else {
    const csv=aoa.map(r=>r.map(c=>typeof c==='string'&&/[",\n]/.test(c)?'"'+c.replace(/"/g,'""')+'"':c).join(',')).join('\n');
    const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'})); a.download=fname+'.csv'; a.click();
  }
  if(btn){btn.textContent=origTxt;btn.disabled=false;}
}
window.exportContributors=exportContributors;
function renderAnswer(){
  const [iA,iB]=aIdx(), T=D.total;
  const comp=[['Volume (kWh)',pctV(T.kwh[iA],T.kwh[iB])],['Energy',pctV(T.energy[iA],T.energy[iB])],['Fuel',pctV(T.fuel[iA],T.fuel[iB])],['IPP',pctV(T.ipp[iA],T.ipp[iB])],['Demand (kVA)',pctV(T.demand[iA],T.demand[iB])],['Customer',pctV(T.cust_chg[iA],T.cust_chg[iB])]];
  const revPc=pctV(T.rev[iA],T.rev[iB]), kPc=pctV(T.kwh[iA],T.kwh[iB]), dPc=pctV(T.demand[iA],T.demand[iB]);
  document.getElementById('app').innerHTML='<div class="ctrl">'+periodSel()+'</div><div class="grid"><div class="card"><div class="chartttl">'+D.mlabels[iA]+' → '+D.mlabels[iB]+' · % change by component <span style="font-weight:400;color:var(--mut);font-size:11px">(click a bar for top/bottom 5 contributors)</span></div><div class="chartwrap"><canvas id="c"></canvas></div></div><div class="kpis" id="kp"></div></div>';
  barChart('c',comp.map(c=>c[0]),comp.map(c=>+c[1].toFixed(1)),comp.map(c=>c[0][0]==='D'?'#E24B4A':c[0][0]==='V'?'#9AA7B4':'#3b6ea5'),v=>(v>=0?'+':'')+v.toFixed(1)+'%',{x:{grid:{display:false}},y:{grid:{color:'#223247'},ticks:{callback:v=>v+'%'}}},false,idx=>renderAnswerContributors(idx,iA,iB));
  document.getElementById('kp').innerHTML=kpi('Volume',(kPc>=0?'+':'')+kPc.toFixed(1)+'%','kWh',kPc>=0?'up':'dn')+kpi('Revenue',(revPc>=0?'+':'')+revPc.toFixed(1)+'%',(revPc>kPc?'outpaced':'lagged')+' volume',revPc>=0?'up':'dn')+kpi('Demand charge',(dPc>=0?'+':'')+dPc.toFixed(1)+'%','fixed kVA',dPc<kPc?'dn':'up')+'<div class="kpi"><div class="l">Read</div><div style="font-size:12px;line-height:1.5;margin-top:4px;color:#c7d3e0">Energy &amp; fuel track kWh; demand is fixed. When volume outruns demand, blended realization dilutes.</div></div><div id="answer-contrib" class="kpi" style="border-left-color:var(--blu)"><div class="l">Contributors</div><div style="font-size:11px;color:var(--mut);margin-top:4px">Click a bar in the chart to see the top 5 / bottom 5 accounts driving that component.</div></div>';
  bindPeriod(renderAnswer);
}
function renderBridge(){
  const [iA,iB]=aIdx(), T=D.total;
  const d={Fuel:T.fuel[iB]-T.fuel[iA],Energy:T.energy[iB]-T.energy[iA],IPP:T.ipp[iB]-T.ipp[iA],Demand:T.demand[iB]-T.demand[iA],Customer:T.cust_chg[iB]-T.cust_chg[iA]};
  const net=T.rev[iB]-T.rev[iA], other=net-(d.Fuel+d.Energy+d.IPP+d.Demand+d.Customer);
  const rows=[['Fuel',d.Fuel],['Energy',d.Energy],['Customer',d.Customer],['Other/adj',other],['Demand',d.Demand],['IPP',d.IPP]].sort((a,b)=>b[1]-a[1]);
  document.getElementById('app').innerHTML='<div class="ctrl">'+periodSel()+'</div><div class="grid"><div class="card"><div class="chartttl">'+D.mlabels[iA]+' → '+D.mlabels[iB]+' · revenue change by charge component (J$M)</div><div class="chartwrap"><canvas id="c"></canvas></div></div><div class="kpis" id="kp"></div></div>';
  barChart('c',rows.map(r=>r[0]),rows.map(r=>Math.round(r[1]/1e6)),rows.map(r=>r[1]>=0?'#1D9E75':'#E24B4A'),v=>(v>=0?'+':'')+v+'M',{x:{grid:{color:'#223247'},ticks:{callback:v=>v+'M'}},y:{grid:{display:false}}},true);
  const margin=Math.round((d.Energy+d.Demand+d.Customer)/1e6);
  document.getElementById('kp').innerHTML=kpi('Net revenue',(net>=0?'+':'-')+'J$'+Math.abs(Math.round(net/1e6))+'M',pctV(T.rev[iA],T.rev[iB]).toFixed(1)+'% on vol '+(pctV(T.kwh[iA],T.kwh[iB])>=0?'+':'')+pctV(T.kwh[iA],T.kwh[iB]).toFixed(1)+'%',net>=0?'up':'dn')+kpi('IPP (pass-through)',(d.IPP>=0?'+':'-')+'J$'+Math.abs(Math.round(d.IPP/1e6))+'M','margin-neutral',d.IPP>=0?'up':'dn')+kpi('Demand',(d.Demand>=0?'+':'-')+'J$'+Math.abs(Math.round(d.Demand/1e6))+'M','structural',d.Demand>=0?'up':'dn')+'<div class="kpi"><div class="l">Read</div><div style="font-size:12px;line-height:1.5;margin-top:4px;color:#c7d3e0">Margin-bearing (energy+demand+customer) net '+(margin>=0?'+':'')+margin+'M. Fuel &amp; IPP are pass-through.</div></div>';
  bindPeriod(renderBridge);
}
function renderCases(){
  const [iA,iB]=aIdx();
  const big=D.accts.slice().sort((a,b)=>b.rev[iB]-a.rev[iB]).slice(0,40);
  if(!caseSel||!D.accts.find(a=>a.n===caseSel)){const al=D.accts.find(a=>a.n.toLowerCase().includes('alcoa'));caseSel=al?al.n:(big[0]&&big[0].n);}
  const a=D.accts.find(x=>x.n===caseSel)||big[0];
  const anchors=['Alcoa','Caribbean Cement','Windalco','Jamaica Broilers','National Water'];
  let h='<div class="ctrl">'+periodSel()+'<select id="caseSel">'+big.map((x,i)=>'<option value="'+i+'"'+(x.n===caseSel?' selected':'')+'>'+esc(x.n).slice(0,30)+'</option>').join('')+'</select></div>';
  h+='<div style="margin:0 2px 10px;display:flex;gap:6px;flex-wrap:wrap">'+anchors.map(n=>'<span class="chip" data-anc="'+n+'">'+n+'</span>').join('')+'</div>';
  h+='<div class="grid"><div class="card"><div class="chartttl">'+esc(a.n).slice(0,32)+' ['+a.c+'] · indexed to '+D.mlabels[iA]+' = 100</div><div class="chartwrap"><canvas id="c"></canvas></div></div><div class="card" style="padding:10px"><div class="tbl"><table><thead><tr><th class="l"></th><th>'+D.mlabels[iA]+'</th><th>'+D.mlabels[iB]+'</th><th>Δ</th></tr></thead><tbody id="tb"></tbody></table></div></div></div>';
  document.getElementById('app').innerHTML=h;
  const pc=(x,y)=>Math.round((x?y/x-1:0)*100);
  const dpkA=a.kwh[iA]?a.dem[iA]/a.kwh[iA]:0, dpkB=a.kwh[iB]?a.dem[iB]/a.kwh[iB]:0;
  const tr=[['kWh',(a.kwh[iA]/1e6).toFixed(1)+'M',(a.kwh[iB]/1e6).toFixed(1)+'M',pc(a.kwh[iA],a.kwh[iB])],['Revenue','J$'+(a.rev[iA]/1e6).toFixed(1)+'M','J$'+(a.rev[iB]/1e6).toFixed(1)+'M',pc(a.rev[iA],a.rev[iB])],['Demand','J$'+(a.dem[iA]/1e6).toFixed(1)+'M','J$'+(a.dem[iB]/1e6).toFixed(1)+'M',pc(a.dem[iA],a.dem[iB])],['Demand/kWh','J$'+dpkA.toFixed(2),'J$'+dpkB.toFixed(2),pc(dpkA,dpkB)]];
  document.getElementById('tb').innerHTML=tr.map(r=>'<tr><td class="l">'+r[0]+'</td><td>'+r[1]+'</td><td>'+r[2]+'</td><td class="'+(r[3]>=0?'up':'dn')+'">'+(r[3]>=0?'+':'')+r[3]+'%</td></tr>').join('');
  const idx=[pc(a.kwh[iA],a.kwh[iB])+100,pc(a.rev[iA],a.rev[iB])+100,pc(a.dem[iA],a.dem[iB])+100];
  if(chart)chart.destroy();
  chart=new Chart(document.getElementById('c'),{type:'bar',data:{labels:['kWh','Revenue','Demand'],datasets:[{label:D.mlabels[iA],data:[100,100,100],backgroundColor:'#7d93ab',borderRadius:3},{label:D.mlabels[iB],data:idx,backgroundColor:'#3b6ea5',borderRadius:3}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom'},datalabels:dlbl(v=>Math.round(v))},scales:{x:{grid:{display:false}},y:{grid:{color:'#223247'}}}}});
  document.getElementById('caseSel').onchange=e=>{caseSel=big[+e.target.value].n;renderCases();};
  document.querySelectorAll('[data-anc]').forEach(c=>c.onclick=()=>{const m=D.accts.filter(x=>x.n.toLowerCase().includes(c.dataset.anc.toLowerCase()));if(m.length){caseSel=m.sort((x,y)=>y.rev[iB]-x.rev[iB])[0].n;renderCases();}});
  bindPeriod(renderCases);
}
function renderGiants(){
  const [iA,iB]=aIdx(), cls=['RT40','RT50','RT70'];
  const giants=['alcoa','windalco','caribbean cement'], isG=n=>giants.some(p=>n.toLowerCase().includes(p));
  const cl=c=>wowMet==='rev'?D.cls[c].rev:D.cls[c].demand, ac=a=>wowMet==='rev'?a.rev:a.dem;
  let h='<div class="ctrl">'+periodSel()+'<div class="seg"><button data-wm="rev" class="'+(wowMet==='rev'?'on':'')+'">Revenue</button><button data-wm="dem" class="'+(wowMet==='dem'?'on':'')+'">Demand</button></div></div>';
  h+='<div class="grid"><div class="card"><div class="chartttl">'+D.mlabels[iA]+' → '+D.mlabels[iB]+' · '+(wowMet==='rev'?'revenue':'demand')+' % — all vs ex-giants (Carib/Alcoa/Windalco)</div><div class="chartwrap"><canvas id="c"></canvas></div></div><div class="kpis" id="kp"></div></div>';
  document.getElementById('app').innerHTML=h;
  const R={};
  cls.forEach(c=>{const aA=cl(c)[iA],aB=cl(c)[iB];let gA=0,gB=0;D.accts.forEach(x=>{if(x.c===c&&isG(x.n)){gA+=ac(x)[iA];gB+=ac(x)[iB];}});R[c]={all:pctV(aA,aB),ex:pctV(aA-gA,aB-gB)};});
  if(chart)chart.destroy();
  chart=new Chart(document.getElementById('c'),{type:'bar',data:{labels:cls,datasets:[{label:'All accounts',data:cls.map(c=>+R[c].all.toFixed(1)),backgroundColor:'#3b6ea5',borderRadius:3},{label:'Ex-giants',data:cls.map(c=>+R[c].ex.toFixed(1)),backgroundColor:'#c8772f',borderRadius:3}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom'},datalabels:dlbl(v=>(v>=0?'+':'')+v.toFixed(1)+'%')},scales:{x:{grid:{display:false}},y:{grid:{color:'#223247'},ticks:{callback:v=>v+'%'}}}}});
  document.getElementById('kp').innerHTML=kpi('RT50 '+(wowMet==='rev'?'revenue':'demand'),(R.RT50.all>=0?'+':'')+R.RT50.all.toFixed(1)+'%','ex-Carib: '+(R.RT50.ex>=0?'+':'')+R.RT50.ex.toFixed(1)+'%',R.RT50.all>=0?'up':'dn')+kpi('RT70 '+(wowMet==='rev'?'revenue':'demand'),(R.RT70.all>=0?'+':'')+R.RT70.all.toFixed(1)+'%','ex-Alcoa/Windalco: '+(R.RT70.ex>=0?'+':'')+R.RT70.ex.toFixed(1)+'%',R.RT70.all>=0?'up':'dn')+'<div class="kpi"><div class="l">Read</div><div style="font-size:12px;line-height:1.5;margin-top:4px;color:#c7d3e0">A few giants mask each class trend. Strip them out to see the underlying book.</div></div>';
  document.querySelectorAll('[data-wm]').forEach(b=>b.onclick=()=>{wowMet=b.dataset.wm;renderGiants();});
  bindPeriod(renderGiants);
}
const MOVMET={kwh:['Volume (kWh)','kwh','M kWh'],rev:['Revenue','rev','M J$'],fuel:['Fuel','fuel','M J$'],ipp:['IPP','ipp','M J$'],energy:['Energy (non-fuel)','energy','M J$'],demand:['Demand','dem','M J$'],cust:['Customer charge','cust','M J$']};
function renderMovers(){
  const [iA,iB]=aIdx();
  const mm=MOVMET[movMet]||MOVMET.kwh, fld=mm[1], un=mm[2];
  const dv=a=>((a[fld]?a[fld][iB]:0)-(a[fld]?a[fld][iA]:0))/1e6;
  let h='<div class="ctrl">'+periodSel()+
    '<span class="lbl">Line</span><select id="mvmet">'+Object.keys(MOVMET).map(k=>'<option value="'+k+'"'+(movMet===k?' selected':'')+'>'+MOVMET[k][0]+'</option>').join('')+'</select>'+
    '<div class="seg"><button data-mvm="topbot" class="'+(movMode==='topbot'?'on':'')+'">Top/bottom 5</button><button data-mvm="cluster" class="'+(movMode==='cluster'?'on':'')+'">Clustered</button></div>';
  if(movMode==='topbot') h+='<div class="seg">'+['RT40','RT50','RT70'].map(c=>'<button data-mvc="'+c+'" class="'+(movCls===c?'on':'')+'">'+c+'</button>').join('')+'</div>';
  h+='</div>';
  if(movMode==='topbot'){
    const m=D.accts.filter(a=>a.c===movCls).map(a=>({n:a.n,d:dv(a)})).sort((x,y)=>y.d-x.d);
    const rows=m.slice(0,5).concat(m.slice(-5));
    h+='<div class="card"><div class="chartttl">'+movCls+' · top &amp; bottom 5 movers · '+mm[0]+' — '+D.mlabels[iA]+' → '+D.mlabels[iB]+' ('+un+')</div><div class="chartwrap" style="height:480px"><canvas id="c"></canvas></div></div>';
    document.getElementById('app').innerHTML=h;
    barChart('c',rows.map(r=>r.n.slice(0,26)),rows.map(r=>+r.d.toFixed(1)),rows.map(r=>r.d>=0?'#1D9E75':'#E24B4A'),v=>(v>=0?'+':'')+v.toFixed(1),{x:{grid:{color:'#223247'}},y:{grid:{display:false},ticks:{font:{size:11}}}},true);
  } else {
    const named=['alcoa','windalco','wigton','jamaica private power','west kingston power','seawind','kingston free port','playa hall','bay roc','x fund','musson international dairies','caribbean cement','jamaica broilers','national water'];
    const isN=n=>named.some(p=>n.toLowerCase().includes(p));
    const co=[],rest=[];
    D.accts.forEach(a=>{const dR=dv(a)*1e6;(isN(a.n)?co:rest).push({n:a.n,dR});});
    const TH=2e6, inc=rest.filter(a=>a.dR>TH), dec=rest.filter(a=>a.dR<-TH), flat=rest.filter(a=>Math.abs(a.dR)<=TH);
    const sum=b=>b.reduce((s,a)=>s+a.dR,0);
    const cl=co.filter(a=>Math.abs(a.dR)>1e6).sort((a,b)=>b.dR-a.dR);
    const labels=cl.map(a=>a.n.slice(0,24)).concat(['▸ Other increase ('+inc.length+')','▸ No change ('+flat.length+')','▸ Other decrease ('+dec.length+')']);
    const data=cl.map(a=>Math.round(a.dR/1e6)).concat([Math.round(sum(inc)/1e6),Math.round(sum(flat)/1e6),Math.round(sum(dec)/1e6)]);
    h+='<div class="card"><div class="chartttl">Clustered movers · '+mm[0]+' — call-outs + buckets · '+D.mlabels[iA]+' → '+D.mlabels[iB]+' ('+un+')</div><div class="chartwrap" style="height:'+(labels.length*30+90)+'px"><canvas id="c"></canvas></div></div>';
    document.getElementById('app').innerHTML=h;
    barChart('c',labels,data,data.map((v,i)=>i>=cl.length?'#BA7517':(v>=0?'#1D9E75':'#E24B4A')),v=>(v>=0?'+':'')+v,{x:{grid:{color:'#223247'}},y:{grid:{display:false},ticks:{font:{size:10.5}}}},true);
  }
  const me=document.getElementById('mvmet'); if(me)me.onchange=e=>{movMet=e.target.value;renderMovers();};
  document.querySelectorAll('[data-mvm]').forEach(b=>b.onclick=()=>{movMode=b.dataset.mvm;renderMovers();});
  document.querySelectorAll('[data-mvc]').forEach(b=>b.onclick=()=>{movCls=b.dataset.mvc;renderMovers();});
  bindPeriod(renderMovers);
}
