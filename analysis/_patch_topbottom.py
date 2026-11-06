# -*- coding: utf-8 -*-
# Adds the Top & Bottom companies view to the Commercial section of the sales app.
f = r'C:\Projects\Sales_Platform\JPS_Sales_Platform_v1.html'
t = open(f, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in t else '\n'
cv = lambda s: s.replace('\n', nl)

# 1. tab button
a = '<button class="stab" id="cm_tab_pivot" onclick="swCm(\'pivot\',this)">📊 Pivot &amp; Movers</button>'
assert t.count(a) == 1
t = t.replace(a, a + nl + '        <button class="stab" id="cm_tab_topbot" onclick="swCm(\'topbot\',this)">🏆 Top &amp; Bottom</button>')

# 2. panel markup, placed before the defection panel
a = '      <!-- Defection inline panel (within Commercial section) -->'
assert t.count(a) == 1
panel = cv('''      <div id="cm_topbot_wrap" style="display:none">
        <div class="card">
          <div class="ch">Top &amp; Bottom Companies by Rate Class
            <div style="display:flex;gap:6px;align-items:center">
              <select class="sel" id="tb_cmp" onchange="renderCmTopBottom()" aria-label="Compare against">
                <option value="mom">Month vs previous month</option><option value="yoy">Month vs same month last year</option><option value="ytd">YTD vs last year</option>
              </select>
              <select class="sel" id="tb_n" onchange="renderCmTopBottom()" aria-label="Companies per list">
                <option value="5">Top and bottom 5</option><option value="10">Top and bottom 10</option>
              </select>
              <button class="btn btn-o" onclick="exportTopBottomCSV()">⬇ CSV</button>
              <span class="row-count" id="tb_count"></span>
            </div>
          </div>
          <div id="tb_note" style="font-size:10px;color:var(--text3);padding:4px 2px 8px"></div>
          <div id="tb_out"></div>
        </div>
      </div>

''')
t = t.replace(a, panel + a)

# 3. swCm wiring
a = "  const dfw=document.getElementById('cm_defection_wrap');"
assert t.count(a) == 1
t = t.replace(a, a + nl + "  const tbw=document.getElementById('cm_topbot_wrap');")
a = "  [cw,kw,pw,dfw,row].forEach(el=>{if(el)el.style.display='none';});"
assert t.count(a) == 1
t = t.replace(a, "  [cw,kw,pw,dfw,row,tbw].forEach(el=>{if(el)el.style.display='none';});")
a = "  } else if(panel==='pivot'){" + nl + "    if(pw)pw.style.display='';" + nl + "    renderCmPivot();"
assert t.count(a) == 1
t = t.replace(a, a + nl + "  } else if(panel==='topbot'){" + nl + "    if(tbw)tbw.style.display='';" + nl + "    renderCmTopBottom();")

# 4. renderer, placed before the AI commentary block
a = '// ── AI Commentary ──────────────────────────────────────────────'
assert t.count(a) == 1
js = cv('''// ── Top & Bottom companies by rate class ───────────────────────
// Company = customer number (the part of jps_ac before the dash), so a company with many premises counts once.
// RT20 is held by parish and bucket in the database, not by account, so it is not in this view.
let _tbRows=[];
function _tbMonths(cmp){
  const cy=curYear,py=cy-1,m=curMonth;
  if(cmp==='ytd'){const ms=Array.from({length:m},(_,i)=>i+1);return{cur:ms.map(x=>[cy,x]),prev:ms.map(x=>[py,x]),lbl:`YTD ${MONTHS_SHORT[m-1]} ${cy}`,plbl:`YTD ${MONTHS_SHORT[m-1]} ${py}`};}
  if(cmp==='yoy')return{cur:[[cy,m]],prev:[[py,m]],lbl:`${MONTHS_SHORT[m-1]} ${cy}`,plbl:`${MONTHS_SHORT[m-1]} ${py}`};
  const pm=m===1?12:m-1,pyr=m===1?cy-1:cy;
  return{cur:[[cy,m]],prev:[[pyr,pm]],lbl:`${MONTHS_SHORT[m-1]} ${cy}`,plbl:`${MONTHS_SHORT[pm-1]} ${pyr}`};
}
function renderCmTopBottom(){
  const out=document.getElementById('tb_out');if(!out)return;
  const cmp=document.getElementById('tb_cmp')?.value||'mom';
  const N=Number(document.getElementById('tb_n')?.value)||5;
  const rows=sbActualsComm.length?sbActualsComm:sbActuals.filter(_isComm);
  const per=_tbMonths(cmp);
  const key=(y,m)=>y+'-'+m;
  const curSet=new Set(per.cur.map(p=>key(p[0],p[1]))),prevSet=new Set(per.prev.map(p=>key(p[0],p[1])));
  const CLS=['RT40','RT50','RT60-ST','RT70'];
  const co={};   // class|customer -> totals
  const seen={cur:0,prev:0};
  rows.forEach(r=>{
    const rc=String(r.rate_class||'').trim();if(!CLS.includes(rc))return;
    const k=key(Number(r.year),Number(r.month));
    const isCur=curSet.has(k),isPrev=prevSet.has(k);if(!isCur&&!isPrev)return;
    const ac=String(r.jps_ac||'').trim();if(!ac)return;
    const cust=ac.split('-')[0];
    const id=rc+'|'+cust;
    const c=co[id]||(co[id]={rc,cust,name:'',prem:new Set(),cur:0,prev:0,hasCur:false,hasPrev:false});
    const kwh=Number(r.kwh);if(!isFinite(kwh))return;
    if(!c.name&&r.name)c.name=String(r.name).trim();
    c.prem.add(ac);
    if(isCur){c.cur+=kwh;c.hasCur=true;seen.cur++;}
    if(isPrev){c.prev+=kwh;c.hasPrev=true;seen.prev++;}
  });
  const note=document.getElementById('tb_note');
  if(!seen.cur){
    out.innerHTML='<div style="padding:20px;text-align:center;font-size:11px;color:var(--text3)">No commercial rows for '+esc(per.lbl)+' yet. Load the month and sync.</div>';
    if(note)note.textContent='';document.getElementById('tb_count').textContent='';_tbRows=[];return;
  }
  if(note)note.textContent=`${per.lbl} against ${per.plbl}. Company = customer number, all premises together. Companies under ${(20*per.cur.length).toLocaleString()} MWh in both periods are left out. RT20 is held by parish and bucket, not by company, so it is not shown.`;
  const minK=20000*per.cur.length;
  const mwh=v=>(v/1000).toLocaleString(undefined,{maximumFractionDigits:0});
  const sg=v=>(v>0?'+':v<0?'\\u2212':'')+Math.abs(v/1000).toLocaleString(undefined,{maximumFractionDigits:0});
  const hdr='<thead><tr><th>Company</th><th>Premises</th><th>'+esc(per.lbl)+' MWh</th><th>'+esc(per.plbl)+' MWh</th><th>Change MWh</th><th>Change %</th></tr></thead>';
  const rowHtml=c=>{
    const d=c.cur-c.prev,cls=d>=0?'up':'dn';
    const pcT=!c.hasPrev?'new':(c.prev?((d/c.prev*100>=0?'+':'')+(d/c.prev*100).toFixed(1)+'%'):'n/a');
    return `<tr><td>${esc(c.name||c.cust)}</td><td>${c.prem.size}</td><td>${mwh(c.cur)}</td><td>${c.hasPrev?mwh(c.prev):'\\u2014'}</td><td class="${cls}">${sg(d)}</td><td class="${cls}">${esc(pcT)}</td></tr>`;
  };
  const tbl=l=>l.length?`<table class="dt">${hdr}<tbody>${l.map(rowHtml).join('')}</tbody></table>`:'<div style="padding:10px;font-size:11px;color:var(--text3)">None</div>';
  _tbRows=[];let html='';let nCo=0;
  CLS.forEach(rc=>{
    const L=Object.values(co).filter(c=>c.rc===rc&&Math.max(Math.abs(c.cur),Math.abs(c.prev))>=minK);
    nCo+=L.length;
    const totC=L.reduce((s,c)=>s+c.cur,0),totP=L.reduce((s,c)=>s+(c.hasPrev?c.prev:0),0);
    const head=`<div class="ch" style="font-size:12px;margin-top:14px">${esc(rc)} <span style="font-weight:400;color:var(--text3)">${L.length} companies, ${mwh(totC)} MWh, ${sg(totC-totP)} MWh on ${esc(per.plbl)}</span></div>`;
    if(!L.length){html+=head+'<div style="padding:10px;font-size:11px;color:var(--text3)">No companies above the size cut-off.</div>';return;}
    const flat=L.every(c=>Math.abs(c.cur-c.prev)<1);
    if(flat){html+=head+'<div style="padding:10px;font-size:11px;color:var(--text3)">No movement: these accounts bill the same kWh in both periods.</div>';return;}
    const s=[...L].sort((a,b)=>(b.cur-b.prev)-(a.cur-a.prev));
    const up=s.filter(c=>c.cur-c.prev>0).slice(0,N),dn=s.filter(c=>c.cur-c.prev<0).reverse().slice(0,N);
    up.forEach(c=>_tbRows.push({rc,list:'Top',c}));dn.forEach(c=>_tbRows.push({rc,list:'Bottom',c}));
    html+=head+`<div class="g2"><div><div class="ch" style="font-size:11px">Top ${N} increases</div><div class="tbl-wrap">${tbl(up)}</div></div><div><div class="ch" style="font-size:11px">Bottom ${N} decreases</div><div class="tbl-wrap">${tbl(dn)}</div></div></div>`;
  });
  _tbRows.meta={lbl:per.lbl,plbl:per.plbl};
  out.innerHTML=html;
  document.getElementById('tb_count').textContent=`${nCo} companies`;
}
function exportTopBottomCSV(){
  if(!_tbRows.length){toast('Nothing to export','w');return;}
  const q=v=>'"'+String(v==null?'':v).replace(/"/g,'""')+'"';
  const m=_tbRows.meta||{};
  const lines=[['Rate class','List','Company','Customer no','Premises',(m.lbl||'Current')+' kWh',(m.plbl||'Prior')+' kWh','Change kWh'].map(q).join(',')];
  _tbRows.forEach(x=>{const c=x.c;lines.push([x.rc,x.list,c.name||c.cust,c.cust,c.prem.size,Math.round(c.cur),c.hasPrev?Math.round(c.prev):'',Math.round(c.cur-c.prev)].map(q).join(','));});
  const blob=new Blob([lines.join('\\n')],{type:'text/csv'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='top_bottom_companies.csv';a.click();
  toast('top_bottom_companies.csv downloaded','ok');
}

''')
t = t.replace(a, js + a)
open(f, 'w', encoding='utf-8', newline='').write(t)
print('patched')
