// JPS Sales — MAY 2026 performance (v3): buckets=RT10+RT20 only, large classes by customer,
// three bridges (YoY / MoM / vs-Budget), realization reframed as fuel+fixed (base rate unchanged).
const pptxgen=require("pptxgenjs");
const D=require("./data_v3.json");

const MN=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const f1=v=>v.toLocaleString("en-US",{maximumFractionDigits:1,minimumFractionDigits:1});
const f0=v=>Math.round(v).toLocaleString("en-US");
const sgn=v=>(v>=0?"+":"")+f1(v);
const sgn0=v=>(v>=0?"+":"")+f0(v);
const pct=(a,b)=>(a-b)/b*100;
const sum=a=>a.reduce((x,y)=>x+y,0);

const mon=D.monthly;                       // [y,mo,cust,rev,kwh]
const C=2,R=3,K=4;
const m=(y,mo)=>mon.find(r=>r[0]==y&&r[1]==mo);
const May25=m(2025,5),Apr26=m(2026,4),May26=m(2026,5);
const yoyR=pct(May26[R],May25[R]),yoyK=pct(May26[K],May25[K]),yoyC=pct(May26[C],May25[C]);
const momR=pct(May26[R],Apr26[R]),momK=pct(May26[K],Apr26[K]);
const real=r=>r[R]/r[K], realY=pct(real(May26),real(May25));

// mass-market (RT10+RT20) buckets
const BO=['<Zero','Zero','<150','150>350','350>550','550>750','750>950','over 950'];
const BL={'<Zero':"Credits (<0)",'Zero':"Zero-use",'<150':"<150",'150>350':"150–350",'350>550':"350–550",'550>750':"550–750",'750>950':"750–950",'over 950':">950"};
const consume=['<150','150>350','350>550','550>750','750>950','over 950'];
const bC=b=>D.massBuckets[b];              // {may25:[c,r,k],apr26,may26}
const BM=D.massBucketsMonthly;
const labBM=BM.map(r=>MN[r.ym[1]-1]+(r.ym[0]==2025?"·25":"·26"));
const massTot=p=>BO.reduce((a,b)=>[a[0]+bC(b)[p][0],a[1]+bC(b)[p][1],a[2]+bC(b)[p][2]],[0,0,0]);
const mt26=massTot('may26');

// rate classes & large
const RTN={RT10:"RT10 Residential",RT20:"RT20 Gen. Service",RT40:"RT40 Power",RT50:"RT50 Large Power","RT60-ST":"RT60 Streetlight",RT70:"RT70 Standby"};
const rks=['RT10','RT20','RT40','RT50','RT60-ST','RT70'];
const rcYoYR=k=>pct(D.rate[k].may26[1],D.rate[k].may25[1]);
const rcYoYK=k=>pct(D.rate[k].may26[2],D.rate[k].may25[2]);
const LRG=['RT40','RT50','RT60-ST','RT70'];

const BR=D.bridges;

// theme
const DARK="14202E",DARK2="1E2D40",YEL="FFC60B",LIGHT="F6F8FB",CARD="FFFFFF",
 INK="1B2A3A",MUT="6B7C8F",POS="1F9D8B",NEG="D9534F",BLU="3B6EA5",LINEC="E2E8F0";
const HF="Georgia",BF="Calibri";
const pres=new pptxgen(); pres.layout="LAYOUT_WIDE"; const W=13.3,Ht=7.5;
pres.author="JPS FP&A"; pres.title="JPS Sales — May 2026 Performance v3";
const sh=()=>({type:"outer",color:"000000",blur:7,offset:3,angle:135,opacity:0.16});
let PGN=1;
function footer(s){PGN++; s.addShape(pres.shapes.RECTANGLE,{x:0,y:Ht-0.32,w:W,h:0.32,fill:{color:DARK}});
 s.addText("JPS Sales · 'sales trend' billing pivot (net) · consumption tiers = RT10+RT20 · Jan-25→May-26 · J$ unless noted",
 {x:0.4,y:Ht-0.32,w:11,h:0.32,fontFace:BF,fontSize:8,color:"9FB0C2",valign:"middle",margin:0});
 s.addText(String(PGN),{x:W-0.8,y:Ht-0.32,w:0.4,h:0.32,fontFace:BF,fontSize:9,color:"9FB0C2",align:"right",valign:"middle",margin:0});}
function header(s,kick,title){s.background={color:LIGHT};
 s.addText(kick.toUpperCase(),{x:0.5,y:0.32,w:11,h:0.3,fontFace:BF,fontSize:11,color:BLU,bold:true,charSpacing:3,margin:0});
 s.addText(title,{x:0.5,y:0.6,w:12.3,h:0.65,fontFace:HF,fontSize:26,color:INK,bold:true,margin:0});
 s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.26,w:0.9,h:0.06,fill:{color:YEL}});}
function cbase(extra){return Object.assign({chartArea:{fill:{color:CARD}},plotArea:{fill:{color:CARD}},
 catAxisLabelColor:MUT,valAxisLabelColor:MUT,catAxisLabelFontFace:BF,valAxisLabelFontFace:BF,
 catAxisLabelFontSize:10,valAxisLabelFontSize:9,valGridLine:{color:LINEC,size:0.5},catGridLine:{style:"none"},showLegend:false},extra);}

// generic waterfall (steps:[label,value,type]; type start/end/up/down)
function waterfall(s,o){
 const {x,y,w,h,steps,vMin,vMax,grid,gridFmt,absFmt,dFmt}=o;
 let run=0; const seg=[];
 steps.forEach(st=>{ if(st[2]=="start"||st[2]=="end"){seg.push([vMin,st[1]]); if(st[2]=="start")run=st[1];}
  else {const lo=Math.min(run,run+st[1]),hi=Math.max(run,run+st[1]); seg.push([lo,hi]); run+=st[1];}});
 const slot=w/steps.length, bw=slot*0.58;
 const mapY=v=>y+h-(v-vMin)/(vMax-vMin)*h;
 s.addShape(pres.shapes.RECTANGLE,{x,y,w,h,fill:{color:CARD},line:{color:LINEC,width:1}});
 grid.forEach(g=>{const gy=mapY(g); s.addShape(pres.shapes.LINE,{x,y:gy,w,h:0,line:{color:LINEC,width:0.5}});
  s.addText(gridFmt(g),{x:x-0.92,y:gy-0.12,w:0.86,h:0.24,fontFace:BF,fontSize:8,color:MUT,align:"right",valign:"middle",margin:0});});
 // connectors
 let r2=0; steps.forEach((st,i)=>{ if(st[2]=="start")r2=st[1]; else if(st[2]!="end")r2+=st[1];
  if(i<steps.length-1){const yc=mapY(r2),cx=x+i*slot+(slot-bw)/2+bw,nx=x+(i+1)*slot+(slot-bw)/2;
   s.addShape(pres.shapes.LINE,{x:cx,y:yc,w:nx-cx,h:0,line:{color:"9AA7B4",width:0.75,dashType:"dash"}});}});
 steps.forEach((st,i)=>{const cx=x+i*slot+(slot-bw)/2,lo=seg[i][0],hi=seg[i][1];
  const yTop=mapY(hi),hgt=Math.max(mapY(lo)-mapY(hi),0.02);
  const col=st[2]=="start"?DARK2:st[2]=="end"?YEL:st[2]=="up"?POS:NEG;
  s.addShape(pres.shapes.RECTANGLE,{x:cx,y:yTop,w:bw,h:hgt,fill:{color:col}});
  const isEnd=(st[2]=="start"||st[2]=="end");
  const lc=isEnd?INK:(st[1]>=0?"15715F":"A6332E");
  const ly=(!isEnd&&st[1]<0)?mapY(lo)+0.02:yTop-0.28;
  s.addText(isEnd?absFmt(st[1]):dFmt(st[1]),{x:cx-0.3,y:ly,w:bw+0.6,h:0.26,fontFace:BF,fontSize:9.5,bold:true,color:lc,align:"center",margin:0});
  s.addText(st[0],{x:cx-0.3,y:y+h+0.06,w:bw+0.6,h:0.5,fontFace:BF,fontSize:9.5,color:INK,align:"center",valign:"top",margin:0});});
}

// ===== 1 TITLE =====
let s=pres.addSlide(); s.background={color:DARK};
s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:W,h:0.18,fill:{color:YEL}});
s.addShape(pres.shapes.RECTANGLE,{x:0,y:Ht-0.18,w:W,h:0.18,fill:{color:YEL}});
s.addText("JPS SALES PLATFORM · FP&A PERFORMANCE REVIEW",{x:0.9,y:1.4,w:11,h:0.4,fontFace:BF,fontSize:14,color:YEL,bold:true,charSpacing:3,margin:0});
s.addText("May 2026 Sales & Revenue Performance",{x:0.9,y:2.0,w:11.6,h:1.0,fontFace:HF,fontSize:40,color:"FFFFFF",bold:true,margin:0});
s.addText("Rebound vs April, soft vs last May — and base rates unchanged, so the YoY gap is fuel & fixed",{x:0.9,y:3.1,w:11.8,h:0.5,fontFace:BF,fontSize:16,color:"C7D3E0",margin:0});
const strip=[["May revenue (MoM)",sgn(momR)+"%","vs Apr-26"],["May revenue (YoY)",sgn(yoyR)+"%","vs May-25"],
 ["Vol vs budget",sgn(pct(sum(BR.budgetVol.act),sum(BR.budgetVol.bud)))+"%","+"+f1((sum(BR.budgetVol.act)-sum(BR.budgetVol.bud))/1e6)+"M kWh"],
 ["Realization (YoY)",sgn(realY)+"%","fuel & fixed"]];
strip.forEach((c,i)=>{const x=0.9+i*2.95;
 s.addShape(pres.shapes.RECTANGLE,{x,y:4.3,w:2.7,h:1.5,fill:{color:DARK2},line:{color:"2C4258",width:1}});
 s.addShape(pres.shapes.RECTANGLE,{x,y:4.3,w:0.07,h:1.5,fill:{color:YEL}});
 s.addText(c[0].toUpperCase(),{x:x+0.2,y:4.45,w:2.4,h:0.3,fontFace:BF,fontSize:9.5,color:"9FB0C2",bold:true,charSpacing:1,margin:0});
 s.addText(c[1],{x:x+0.2,y:4.77,w:2.45,h:0.55,fontFace:HF,fontSize:23,color:(c[1].startsWith("+")?"6FE0C8":"FF8A80"),bold:true,margin:0});
 s.addText(c[2],{x:x+0.2,y:5.38,w:2.4,h:0.3,fontFace:BF,fontSize:10.5,color:"C7D3E0",margin:0});});
s.addText("Prepared "+new Date().toISOString().slice(0,10)+" · consumption tiers shown for RT10+RT20; RT40–70 by customer",{x:0.9,y:6.5,w:11.8,h:0.3,fontFace:BF,fontSize:11,color:"7E91A5",margin:0});

// ===== 2 EXEC =====
s=pres.addSlide(); header(s,"01 · Executive summary","May in one page");
const k=[["May revenue YoY",sgn(yoyR)+"%",NEG,"J$"+f1(May26[R]/1e9)+"B net"],
 ["May revenue MoM",sgn(momR)+"%",POS,"vs April"],
 ["Sales vs budget",sgn(pct(sum(BR.budgetVol.act),sum(BR.budgetVol.bud)))+"%",POS,"kWh, +"+f1((sum(BR.budgetVol.act)-sum(BR.budgetVol.bud))/1e6)+"M"],
 ["Realization YoY",sgn(realY)+"%",NEG,"fuel & fixed"]];
k.forEach((c,i)=>{const x=0.5+i*3.12;
 s.addShape(pres.shapes.RECTANGLE,{x,y:1.5,w:2.92,h:1.5,fill:{color:CARD},line:{color:LINEC,width:1},shadow:sh()});
 s.addText(c[0].toUpperCase(),{x:x+0.18,y:1.64,w:2.6,h:0.45,fontFace:BF,fontSize:10,color:MUT,bold:true,charSpacing:1,margin:0});
 s.addText(c[1],{x:x+0.16,y:2.04,w:2.7,h:0.65,fontFace:HF,fontSize:31,color:c[2],bold:true,margin:0});
 s.addText(c[3],{x:x+0.18,y:2.68,w:2.65,h:0.28,fontFace:BF,fontSize:10.5,color:INK,margin:0});});
s.addText("What happened in May",{x:0.5,y:3.25,w:7,h:0.35,fontFace:HF,fontSize:16,color:INK,bold:true,margin:0});
s.addText([
 {text:"Base tariff is unchanged. ",options:{bold:true,bullet:{code:"2022",color:YEL},breakLine:false,color:INK}},
 {text:"So the −"+f1(-realY)+"% realization is fuel (IPP pass-through) + fixed charges — not a rate cut, and largely margin-neutral.",options:{color:INK,breakLine:true}},
 {text:"Volume helped, fuel/rate hurt. ",options:{bold:true,bullet:{code:"2022",color:YEL},breakLine:false,color:INK}},
 {text:"YoY bridge: +J$"+f0(BR.yoy.vol/1e6)+"M volume, but −J$"+f0(-BR.yoy.rate/1e6)+"M fuel/rate → net −J$"+f0((BR.yoy.r0-BR.yoy.r1)/1e6)+"M.",options:{color:INK,breakLine:true}},
 {text:"Strong April rebound. ",options:{bold:true,bullet:{code:"2022",color:YEL},breakLine:false,color:INK}},
 {text:"MoM +J$"+f0(BR.mom.vol/1e6)+"M volume and +J$"+f0(BR.mom.rate/1e6)+"M fuel/rate recovery = +"+f1(momR)+"%.",options:{color:INK,breakLine:true}},
 {text:"Ahead of plan on volume. ",options:{bold:true,bullet:{code:"2022",color:YEL},breakLine:false,color:INK}},
 {text:"Sales +"+f1(pct(sum(BR.budgetVol.act),sum(BR.budgetVol.bud)))+"% vs budget (kWh); RT70 & residential led.",options:{color:INK,breakLine:true}}
],{x:0.5,y:3.65,w:7.15,h:2.6,fontFace:BF,fontSize:12.5,lineSpacingMultiple:1.05,paraSpaceAfter:5,margin:0});
s.addShape(pres.shapes.RECTANGLE,{x:7.95,y:3.25,w:4.85,h:3.5,fill:{color:"FBEFD0"},line:{color:YEL,width:1.5}});
s.addText([{text:"⚑  ",options:{color:"B8860B"}},{text:"WATCH-LIST",options:{bold:true,color:"8A6D1B"}}],{x:8.15,y:3.4,w:4.5,h:0.35,fontFace:BF,fontSize:12,charSpacing:1,margin:0});
s.addText([
 {text:"Confirm the fuel-rate & FX movement that drove −J$"+f0(-BR.yoy.rate/1e6)+"M; check it nets against fuel cost (margin).",options:{bullet:{code:"25B8",color:NEG},breakLine:true,color:"5A4A1E"}},
 {text:"Zero-use accounts (RT10+RT20) up "+f1(pct(bC('Zero').may26[0],bC('Zero').may25[0]))+"% YoY — mix drifting to low tiers.",options:{bullet:{code:"25B8",color:NEG},breakLine:true,color:"5A4A1E"}},
 {text:"Streetlight (RT60) revenue "+sgn(rcYoYR("RT60-ST"))+"% YoY — billing/metering gap.",options:{bullet:{code:"25B8",color:NEG},breakLine:true,color:"5A4A1E"}},
 {text:"Revenue-vs-budget bridge blocked: budget revenue is corrupted (=kWh). Volume bridge shown instead.",options:{bullet:{code:"25B8",color:NEG},color:"5A4A1E"}}
],{x:8.15,y:3.85,w:4.5,h:2.85,fontFace:BF,fontSize:11,lineSpacingMultiple:1.02,paraSpaceAfter:8,margin:0});
footer(s);

// ===== 3 BASIS =====
s=pres.addSlide(); header(s,"02 · Basis & method","Read before the charts");
const notes=[
 ["Consumption tiers = RT10 + RT20 only","Usage bands (<150 … >950 kWh) are meaningful only for the mass-market residential (RT10) and general-service (RT20) classes. RT40/50/60/70 are a handful of large accounts — analysed by customer, not by tier."],
 ["Base rate unchanged → fuel & fixed","Tariff base rates did not change May-25→May-26. The realization decline is therefore the fuel (IPP) pass-through and fixed/standing charges. The bridge's 'fuel/rate' bar captures this; it is largely cost-offsetting."],
 ["Net revenue basis","'net_revenue' is ~8–9% below GL/billed revenue (net of taxes); kWh ties to the meter data. Reconcile to GL before external use."],
 ["Budget revenue unusable","jps_budget.revenue_budget is corrupted (=kWh) for Mar-Dec; jps_le is empty. kWh & customer budgets are intact, so the vs-budget bridge is on volume (kWh)."]];
notes.forEach((n,i)=>{const col=i%2,row=Math.floor(i/2);const x=0.5+col*6.25,y=1.55+row*2.45;
 s.addShape(pres.shapes.RECTANGLE,{x,y,w:5.95,h:2.25,fill:{color:CARD},line:{color:LINEC,width:1},shadow:sh()});
 s.addShape(pres.shapes.RECTANGLE,{x,y,w:0.09,h:2.25,fill:{color:(i==0||i==1)?BLU:NEG}});
 s.addText(n[0],{x:x+0.25,y:y+0.18,w:5.5,h:0.6,fontFace:HF,fontSize:14.5,color:((i==3)?NEG:INK),bold:true,margin:0});
 s.addText(n[1],{x:x+0.25,y:y+0.74,w:5.55,h:1.4,fontFace:BF,fontSize:11.5,color:INK,lineSpacingMultiple:1.04,margin:0});});
footer(s);

// ===== 4 MAY SPOTLIGHT =====
s=pres.addSlide(); header(s,"03 · May spotlight","Rebound vs April, softer vs last May");
const mc=[["Sales","MoM",sgn(momK)+"%",momK>=0?POS:NEG],["Sales","YoY",sgn(yoyK)+"%",yoyK>=0?POS:NEG],
 ["Revenue","MoM",sgn(momR)+"%",momR>=0?POS:NEG],["Revenue","YoY",sgn(yoyR)+"%",yoyR>=0?POS:NEG]];
mc.forEach((c,i)=>{const x=0.5+i*3.12;
 s.addShape(pres.shapes.RECTANGLE,{x,y:1.5,w:2.92,h:1.55,fill:{color:CARD},line:{color:LINEC,width:1},shadow:sh()});
 s.addText(c[0]+" · "+c[1],{x:x+0.18,y:1.64,w:2.6,h:0.3,fontFace:BF,fontSize:11,color:MUT,bold:true,margin:0});
 s.addText(c[2],{x:x+0.16,y:1.98,w:2.7,h:0.7,fontFace:HF,fontSize:33,color:c[3],bold:true,margin:0});
 s.addText(c[1]=="MoM"?"vs April 2026":"vs May 2025",{x:x+0.18,y:2.68,w:2.65,h:0.3,fontFace:BF,fontSize:10.5,color:INK,margin:0});});
s.addText("Apr-26 → May-26 vs May-25",{x:0.5,y:3.35,w:8,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[
 {name:"Sales (M kWh)",labels:["Apr-26","May-25","May-26"],values:[Apr26,May25,May26].map(r=>+(r[K]/1e6).toFixed(0))},
 {name:"Revenue (J$00M)",labels:["Apr-26","May-25","May-26"],values:[Apr26,May25,May26].map(r=>+(r[R]/1e8).toFixed(0))}
],cbase({x:0.4,y:3.7,w:7.7,h:3.1,barDir:"col",chartColors:[BLU,YEL],showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:10,
 showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:9,dataLabelColor:INK,valAxisHidden:true,valAxisMaxVal:320,valAxisMinVal:0}));
s.addShape(pres.shapes.RECTANGLE,{x:8.35,y:3.35,w:4.45,h:3.45,fill:{color:DARK}});
s.addText("The shape of May",{x:8.55,y:3.5,w:4.1,h:0.35,fontFace:HF,fontSize:14,color:YEL,bold:true,margin:0});
s.addText([
 {text:"Volume recovered "+f1((May26[K]-Apr26[K])/1e6)+"M kWh over April (+"+f1(momK)+"%), led by the high-use tier and RT70.",options:{color:"DCE6F0",bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:"Revenue outpaced volume MoM — fuel/realization repaired after April's dip (+J$"+f0(BR.mom.rate/1e6)+"M).",options:{color:"DCE6F0",bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:"Against May-25: +"+f1(yoyK)+"% kWh & +"+f1(yoyC)+"% customers but "+sgn(yoyR)+"% revenue — the YoY shortfall is fuel/fixed.",options:{color:"DCE6F0",bullet:{code:"2022",color:YEL},breakLine:true}}
],{x:8.55,y:3.95,w:4.1,h:2.7,fontFace:BF,fontSize:11.5,lineSpacingMultiple:1.05,paraSpaceAfter:9,margin:0});
footer(s);

// ===== 5 TOTAL REVENUE TREND =====
s=pres.addSlide(); header(s,"04 · Total revenue","Total net revenue & realization — 17-month trend");
s.addText("Total net revenue (J$ B)",{x:0.5,y:1.45,w:8,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[{name:"Net revenue",labels:labBM,values:mon.map(r=>+(r[R]/1e9).toFixed(2))}],
 cbase({x:0.4,y:1.75,w:12.4,h:2.55,barDir:"col",chartColors:[BLU],showValue:true,dataLabelFormatCode:"0.0",
  dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:8.5,dataLabelColor:INK,valAxisHidden:true,valAxisMaxVal:17,catAxisLabelFontSize:8.5,catAxisLabelRotate:-40}));
s.addText("Realization — net J$/kWh (base rate flat → moves with fuel & fixed)",{x:0.5,y:4.45,w:9,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.LINE,[{name:"J$/kWh",labels:labBM,values:mon.map(r=>+(r[R]/r[K]).toFixed(1))}],
 cbase({x:0.4,y:4.75,w:12.4,h:2.0,lineSize:2.5,lineSmooth:true,chartColors:[YEL],lineDataSymbol:"circle",lineDataSymbolSize:5,
  showValue:true,dataLabelPosition:"t",dataLabelFontFace:BF,dataLabelFontSize:8,dataLabelColor:"8A6D1B",
  valAxisMinVal:40,valAxisMaxVal:64,catAxisLabelFontSize:8.5,catAxisLabelRotate:-40}));
footer(s);

// ===== 6 RATE CLASS DIVERGENCE =====
s=pres.addSlide(); header(s,"05 · By rate class","May YoY: volume holds, revenue falls — across the board");
s.addChart(pres.charts.BAR,[
 {name:"Sales kWh YoY %",labels:rks.map(k=>k.replace("-ST","")),values:rks.map(k=>+rcYoYK(k).toFixed(1))},
 {name:"Revenue YoY %",labels:rks.map(k=>k.replace("-ST","")),values:rks.map(k=>+rcYoYR(k).toFixed(1))}
],cbase({x:0.4,y:1.6,w:8.5,h:5.15,barDir:"col",chartColors:[BLU,YEL],showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:11,
 showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:9,dataLabelColor:INK,valAxisMinVal:-34,valAxisMaxVal:18}));
s.addShape(pres.shapes.RECTANGLE,{x:9.15,y:1.6,w:3.65,h:5.15,fill:{color:"FBEFD0"},line:{color:YEL,width:1.5}});
s.addText("Uniform, not structural",{x:9.35,y:1.75,w:3.3,h:0.35,fontFace:HF,fontSize:14,color:"8A6D1B",bold:true,margin:0});
s.addText([
 {text:"RT10/20/40/50 revenue all ≈ −3.3 to −3.6% YoY on flat/up volume — the same fuel/fixed effect, not class-specific.",options:{color:"5A4A1E",bullet:{code:"2022",color:NEG},breakLine:true}},
 {text:"RT50 Large Power: kWh "+sgn(rcYoYK("RT50"))+"% yet revenue "+sgn(rcYoYR("RT50"))+"%.",options:{color:"5A4A1E",bullet:{code:"2022",color:NEG},breakLine:true}},
 {text:"RT60 Streetlight is the real outlier ("+sgn(rcYoYR("RT60-ST"))+"% rev) — operational, chase metering.",options:{color:"5A4A1E",bullet:{code:"2022",color:NEG},breakLine:true}},
 {text:"RT70 Standby the lone gainer (+"+f1(rcYoYR("RT70"))+"% rev).",options:{color:"5A4A1E",bullet:{code:"2022",color:POS}}}
],{x:9.35,y:2.2,w:3.3,h:4.5,fontFace:BF,fontSize:10.5,lineSpacingMultiple:1.03,paraSpaceAfter:8,margin:0});
footer(s);

// ===== 7 LARGE CLASSES BY CUSTOMER =====
s=pres.addSlide(); header(s,"06 · Large classes — by customer","RT40 / 50 / 60 / 70: a few hundred accounts, ~"+f1((LRG.reduce((a,r)=>a+D.rate[r].may26[1],0))/May26[R]*100)+"% of revenue");
const lr=[["Class","Customers","kWh (M)","Revenue (J$M)","kWh/cust ('000)","Rev YoY","kWh YoY"]];
LRG.forEach(rt=>{const d=D.rate[rt].may26;
 lr.push([RTN[rt],f0(d[0]),f1(d[2]/1e6),f0(d[1]/1e6),f0(d[2]/d[0]/1000),sgn(rcYoYR(rt))+"%",sgn(rcYoYK(rt))+"%"]);});
s.addTable(lr.map((row,ri)=>row.map((c,ci)=>{
 if(ri==0)return{text:c,options:{fill:{color:DARK},color:"FFFFFF",bold:true,fontSize:11,align:ci==0?"left":"center",valign:"middle",fontFace:BF}};
 const isNeg=(ci>=5&&String(c).startsWith("-"));
 return{text:c,options:{fill:{color:ri%2?"FFFFFF":"F1F5F9"},color:(ci>=5?(isNeg?NEG:POS):INK),bold:(ci==0||ci>=5),fontSize:12,align:ci==0?"left":"center",valign:"middle",fontFace:BF}};
})),{x:0.5,y:1.6,w:7.85,colW:[1.9,0.95,0.85,1.2,1.15,0.9,0.9],rowH:0.62,border:{type:"solid",pt:0.5,color:LINEC},margin:[3,5,3,5]});
// mini bar: revenue by large class May25 vs May26
s.addText("Revenue J$M — May-25 vs May-26",{x:0.5,y:5.35,w:8,h:0.3,fontFace:BF,fontSize:11,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[
 {name:"May-25",labels:LRG.map(r=>r.replace("-ST","")),values:LRG.map(r=>+(D.rate[r].may25[1]/1e6).toFixed(0))},
 {name:"May-26",labels:LRG.map(r=>r.replace("-ST","")),values:LRG.map(r=>+(D.rate[r].may26[1]/1e6).toFixed(0))}
],cbase({x:0.4,y:5.65,w:8.3,h:1.15,barDir:"bar",chartColors:["B9C6D6",YEL],showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:9,
 showValue:false,valAxisHidden:true,catAxisLabelFontSize:9}));
s.addShape(pres.shapes.RECTANGLE,{x:8.95,y:1.6,w:3.85,h:5.2,fill:{color:CARD},line:{color:LINEC,width:1},shadow:sh()});
s.addText("By customer, not tier",{x:9.15,y:1.75,w:3.5,h:0.35,fontFace:HF,fontSize:14,color:INK,bold:true,margin:0});
s.addText([
 {text:"These classes are a few hundred large accounts — consumption tiers don't apply; we track them by customer.",options:{bullet:{code:"2022",color:BLU},breakLine:true,color:INK}},
 {text:"RT40 (power) + RT50 (large power) carry most large-class volume; RT70 standby is small but growing (+"+f1(rcYoYK("RT70"))+"% kWh).",options:{bullet:{code:"2022",color:POS},breakLine:true,color:INK}},
 {text:"RT60 streetlight: "+sgn(rcYoYR("RT60-ST"))+"% revenue YoY — a billing/metering completeness issue to fix.",options:{bullet:{code:"2022",color:NEG},breakLine:true,color:INK}},
 {text:"Concentration risk: a single large account moving has visible P&L impact — monitor churn monthly.",options:{bullet:{code:"2022",color:YEL},color:INK}}
],{x:9.15,y:2.2,w:3.5,h:4.5,fontFace:BF,fontSize:10.5,lineSpacingMultiple:1.03,paraSpaceAfter:8,margin:0});
footer(s);

// ===== 8 BUCKET vs REVENUE OVER TIME (RT10+RT20) =====
s=pres.addSlide(); header(s,"07 · Tiers vs revenue","RT10+RT20 net revenue by consumption tier — over time");
const stkKeys=['FIX','<150','150>350','350>550','550>750','750>950','over 950'];
const stkLbl={FIX:"Fixed/credits",'<150':"<150",'150>350':"150–350",'350>550':"350–550",'550>750':"550–750",'750>950':"750–950",'over 950':">950"};
const stkCol={FIX:"B7C4D1",'<150':"CAD8EC",'150>350':"9DBDE0",'350>550':"6E96C4",'550>750':"4E7CB0",'750>950':"345D8C",'over 950':"FFC60B"};
const revStk=key=>BM.map(r=>((key=='FIX'?(r.b['Zero'][1]+r.b['<Zero'][1]):r.b[key][1]))/1e9);
s.addChart(pres.charts.BAR, stkKeys.map(key=>({name:stkLbl[key],labels:labBM,values:revStk(key).map(v=>+v.toFixed(2))})),
 cbase({x:0.4,y:1.55,w:9.0,h:5.2,barDir:"col",barGrouping:"stacked",chartColors:stkKeys.map(key=>stkCol[key]),
  showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:9,valAxisTitle:"J$ B",catAxisLabelFontSize:8,catAxisLabelRotate:-45}));
s.addShape(pres.shapes.RECTANGLE,{x:9.55,y:1.55,w:3.25,h:5.2,fill:{color:CARD},line:{color:LINEC,width:1},shadow:sh()});
s.addText("Read",{x:9.75,y:1.7,w:2.9,h:0.35,fontFace:HF,fontSize:14,color:INK,bold:true,margin:0});
s.addText([
 {text:"RT10+RT20 are ~"+f1(massTot('may26')[1]/May26[R]*100)+"% of total revenue.",options:{bullet:{code:"2022",color:YEL},breakLine:true,color:INK}},
 {text:"The gold >950 tier is the swing band — it drives the Apr-26 dip and May-26 rebound.",options:{bullet:{code:"2022",color:YEL},breakLine:true,color:INK}},
 {text:"Mid tiers (150–550) are stable; volatility lives at the top.",options:{bullet:{code:"2022",color:MUT},breakLine:true,color:INK}},
 {text:"Nov-25 = partial billing cycle (data).",options:{bullet:{code:"2022",color:NEG},color:INK}}
],{x:9.75,y:2.15,w:2.9,h:4.4,fontFace:BF,fontSize:10.5,lineSpacingMultiple:1.03,paraSpaceAfter:8,margin:0});
footer(s);

// ===== 9 CUSTOMER MIX OVER TIME (RT10+RT20) =====
s=pres.addSlide(); header(s,"08 · Tier movement","RT10+RT20 customer mix — share of accounts over time");
s.addChart(pres.charts.BAR, BO.map(b=>({name:BL[b],labels:labBM,values:BM.map(r=>Math.max(r.b[b][0],0))})),
 cbase({x:0.4,y:1.55,w:9.0,h:5.2,barDir:"col",barGrouping:"percentStacked",
  chartColors:['D9534F','9AA7B4','CAD8EC','9DBDE0','6E96C4','4E7CB0','345D8C','FFC60B'],
  showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:9,catAxisLabelFontSize:8,catAxisLabelRotate:-45,valAxisLabelFormatCode:'0%'}));
s.addShape(pres.shapes.RECTANGLE,{x:9.55,y:1.55,w:3.25,h:5.2,fill:{color:"FBEFD0"},line:{color:YEL,width:1.5}});
s.addText("The drift",{x:9.75,y:1.7,w:2.9,h:0.35,fontFace:HF,fontSize:14,color:"8A6D1B",bold:true,margin:0});
const zsh25=bC('Zero').may25[0]/massTot('may25')[0]*100, zsh26=bC('Zero').may26[0]/massTot('may26')[0]*100;
s.addText([
 {text:"Zero-use band (grey) thickened from "+f1(zsh25)+"% to "+f1(zsh26)+"% of RT10+RT20 accounts — step-up after Dec-25.",options:{bullet:{code:"2022",color:NEG},breakLine:true,color:"5A4A1E"}},
 {text:"The <150 band (pale blue) is shrinking as customers fall into Zero-use.",options:{bullet:{code:"2022",color:NEG},breakLine:true,color:"5A4A1E"}},
 {text:"High tiers are a thin, stable sliver of accounts — but most of the revenue (prev slide).",options:{bullet:{code:"2022",color:YEL},breakLine:true,color:"5A4A1E"}},
 {text:"More accounts, lower average use.",options:{bullet:{code:"2022",color:"B8860B"},bold:true,color:"5A4A1E"}}
],{x:9.75,y:2.15,w:2.9,h:4.4,fontFace:BF,fontSize:10.5,lineSpacingMultiple:1.03,paraSpaceAfter:8,margin:0});
footer(s);

// ===== 10 CONSUMPTION SNAPSHOT (RT10+RT20) =====
s=pres.addSlide(); header(s,"09 · Tier snapshot","RT10+RT20 customers by tier — and the YoY shift");
s.addText("Customers by tier (May-26, '000)",{x:0.5,y:1.5,w:7,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[{name:"cust",labels:BO.map(b=>BL[b]),values:BO.map(b=>+(bC(b).may26[0]/1000).toFixed(1))}],
 cbase({x:0.4,y:1.85,w:6.7,h:4.5,barDir:"bar",chartColors:[BLU],showValue:true,dataLabelPosition:"outEnd",
  dataLabelFontFace:BF,dataLabelFontSize:9,dataLabelColor:INK,valAxisHidden:true,valAxisMaxVal:430,catAxisLabelColor:INK,catAxisLabelFontSize:10,barGapWidthPct:40}));
s.addText("YoY change in customers (May-26 vs May-25, '000)",{x:7.4,y:1.5,w:5.4,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[{name:"d",labels:BO.map(b=>BL[b]),values:BO.map(b=>+((bC(b).may26[0]-bC(b).may25[0])/1000).toFixed(1))}],
 cbase({x:7.3,y:1.85,w:5.5,h:4.5,barDir:"bar",chartColors:[POS],showValue:true,dataLabelPosition:"outEnd",
  dataLabelFontFace:BF,dataLabelFontSize:9,dataLabelColor:INK,valAxisHidden:true,valAxisMinVal:-15,valAxisMaxVal:21,catAxisLabelColor:INK,catAxisLabelFontSize:10,barGapWidthPct:40}));
s.addText("Customers shifting out of <150 into Zero-use is the clearest sign of softening residential demand.",{x:0.5,y:6.5,w:12,h:0.25,fontFace:BF,fontSize:10,italic:true,color:MUT,margin:0});
footer(s);

// ===== 11 REALIZATION SQUEEZE (RT10+RT20) =====
s=pres.addSlide(); header(s,"10 · The squeeze","RT10+RT20 realization fell in every tier — fuel & fixed");
const rz25=consume.map(b=>bC(b).may25[1]/bC(b).may25[2]);
const rz26=consume.map(b=>bC(b).may26[1]/bC(b).may26[2]);
s.addChart(pres.charts.BAR,[
 {name:"May-25 J$/kWh",labels:consume.map(b=>BL[b]),values:rz25.map(v=>+v.toFixed(1))},
 {name:"May-26 J$/kWh",labels:consume.map(b=>BL[b]),values:rz26.map(v=>+v.toFixed(1))}
],cbase({x:0.4,y:1.6,w:8.5,h:5.15,barDir:"col",chartColors:["A9B7C7",NEG],showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:11,
 showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:9,dataLabelColor:INK,valAxisHidden:true,valAxisMaxVal:75,valAxisMinVal:0}));
s.addShape(pres.shapes.RECTANGLE,{x:9.15,y:1.6,w:3.65,h:5.15,fill:{color:DARK}});
s.addText("Net realization, J$/kWh",{x:9.35,y:1.75,w:3.3,h:0.35,fontFace:HF,fontSize:14,color:YEL,bold:true,margin:0});
s.addText([
 {text:"Unit revenue fell ~4–6% in every tier — uniform, consistent with a fuel/fixed move rather than a base-rate change.",options:{color:"DCE6F0",bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:">950 tier: J$"+f1(rz25[5])+" → J$"+f1(rz26[5])+" /kWh ("+sgn(pct(rz26[5],rz25[5]))+"%).",options:{color:"DCE6F0",bullet:{code:"2022",color:NEG},breakLine:true}},
 {text:"Lower tiers carry a higher unit rate (fixed-charge effect); the top tier is cheapest per kWh.",options:{color:"DCE6F0",bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:"Sized in the bridge: fuel/rate = −J$"+f0(-BR.yoy.rate/1e6)+"M YoY.",options:{color:"FFE9A8",bold:true,bullet:{code:"2022",color:YEL}}}
],{x:9.35,y:2.2,w:3.3,h:4.5,fontFace:BF,fontSize:10.5,lineSpacingMultiple:1.03,paraSpaceAfter:8,margin:0});
footer(s);

// ===== 12 YoY BRIDGE =====
function revWF(s,br,startLbl,sub){
 const V=x=>x/1e6;                       // everything in J$M
 const r0=V(br.r0),r1=V(br.r1),d=[V(br.vol),V(br.mix),V(br.rate),V(br.fix),V(br.cred)];
 const steps=[[startLbl,r0,"start"],["Volume",d[0],d[0]>=0?"up":"down"],["Mix",d[1],d[1]>=0?"up":"down"],
  ["Fuel / rate",d[2],d[2]>=0?"up":"down"],["Std chg",d[3],d[3]>=0?"up":"down"],["Credits",d[4],d[4]>=0?"up":"down"],
  [sub,r1,"end"]];
 let lo=Math.min(r0,r1),hi=Math.max(r0,r1),run=r0;
 d.forEach(x=>{run+=x; lo=Math.min(lo,run); hi=Math.max(hi,run);});
 const pad=(hi-lo)*0.5, vMin=Math.floor((lo-pad)/100)*100, vMax=Math.ceil((hi+pad)/100)*100;
 const grid=[],gs=Math.max(Math.round((vMax-vMin)/4/100)*100,100); for(let g=vMin; g<=vMax+1; g+=gs) grid.push(g);
 waterfall(s,{x:1.15,y:1.95,w:11.3,h:4.0,steps,vMin,vMax,grid,
  gridFmt:g=>"J$"+f1(g/1000)+"B", absFmt:v=>"J$"+f1(v/1000)+"B", dFmt:v=>(v>=0?"+":"")+f0(v)+"M"});
}
s=pres.addSlide(); header(s,"11 · Revenue bridge — YoY","Why May revenue fell J$"+f0((BR.yoy.r0-BR.yoy.r1)/1e6)+"M vs May-25");
revWF(s,BR.yoy,"May-25","May-26");
s.addText([
 {text:"Volume added J$"+f0(BR.yoy.vol/1e6)+"M, but ",options:{color:INK}},
 {text:"fuel/rate cost J$"+f0(-BR.yoy.rate/1e6)+"M",options:{color:NEG,bold:true}},
 {text:" and mix a further J$"+f0(-BR.yoy.mix/1e6)+"M. Base tariff unchanged → fuel/rate ≈ fuel (IPP) pass-through + fixed; largely margin-neutral. Net −J$"+f0((BR.yoy.r0-BR.yoy.r1)/1e6)+"M ("+f1(yoyR)+"%).",options:{color:INK}}
],{x:1.15,y:6.5,w:11.3,h:0.55,fontFace:BF,fontSize:11.5,lineSpacingMultiple:1.0,align:"center",margin:0});
footer(s);

// ===== 13 MoM BRIDGE =====
s=pres.addSlide(); header(s,"12 · Revenue bridge — MoM","Why May rebounded J$"+f0((BR.mom.r1-BR.mom.r0)/1e6)+"M vs April");
revWF(s,BR.mom,"Apr-26","May-26");
s.addText([
 {text:"The April→May rebound is mostly volume (+J$"+f0(BR.mom.vol/1e6)+"M) as the high-use tier recovered, plus a fuel/rate bounce (+J$"+f0(BR.mom.rate/1e6)+"M) that reversed April's dip. Net +J$"+f0((BR.mom.r1-BR.mom.r0)/1e6)+"M (+"+f1(momR)+"%).",options:{color:INK}}
],{x:1.15,y:6.5,w:11.3,h:0.55,fontFace:BF,fontSize:11.5,lineSpacingMultiple:1.0,align:"center",margin:0});
footer(s);

// ===== 14 vs BUDGET (VOLUME) BRIDGE =====
s=pres.addSlide(); header(s,"13 · Volume bridge — vs Budget","May sales beat plan by "+f1((sum(BR.budgetVol.act)-sum(BR.budgetVol.bud))/1e6)+"M kWh (+"+f1(pct(sum(BR.budgetVol.act),sum(BR.budgetVol.bud)))+"%)");
const bv=BR.budgetVol, totB=sum(bv.bud),totA=sum(bv.act);
const bsteps=[["Budget",totB,"start"]];
bv.cls.forEach((cl,i)=>{const d=bv.act[i]-bv.bud[i]; bsteps.push([cl.replace("-ST",""),d,d>=0?"up":"down"]);});
bsteps.push(["Actual",totA,"end"]);
let lo=Math.min(totA,totB),hi=Math.max(totA,totB),run=totB;
bv.cls.forEach((cl,i)=>{run+=bv.act[i]-bv.bud[i]; lo=Math.min(lo,run);hi=Math.max(hi,run);});
const vMin=Math.floor((lo/1e6-6)/5)*5*1e6, vMax=Math.ceil((hi/1e6+6)/5)*5*1e6;
const grid=[]; for(let g=vMin; g<=vMax; g+=5e6) grid.push(g);
waterfall(s,{x:1.15,y:1.95,w:11.3,h:4.0,steps:bsteps,vMin,vMax,grid,
 gridFmt:g=>f0(g/1e6)+"M", absFmt:v=>f0(v/1e6)+"M", dFmt:v=>(v>=0?"+":"")+f1(v/1e6)});
s.addText([
 {text:"Volume ran ahead of plan in 4 of 6 classes — RT70 (+"+f1((bv.act[5]-bv.bud[5])/1e6)+"M), residential RT10 (+"+f1((bv.act[0]-bv.bud[0])/1e6)+"M) and RT20 (+"+f1((bv.act[1]-bv.bud[1])/1e6)+"M) led; RT50 & RT60 slightly behind. Revenue-vs-budget can't be bridged — budget revenue is corrupted (slide 2).",options:{color:INK}}
],{x:1.15,y:6.5,w:11.3,h:0.55,fontFace:BF,fontSize:11,lineSpacingMultiple:1.0,align:"center",margin:0});
footer(s);

// ===== 15 ANOMALY REGISTER =====
s=pres.addSlide(); header(s,"14 · Watch-list","Consolidated register");
const rows=[
 ["#","Item","Evidence (May-26)","Severity","Action"],
 ["1","Fuel/fixed realization drop","Bridge: fuel/rate −J$"+f0(-BR.yoy.rate/1e6)+"M YoY; base rate flat","High","Confirm fuel-rate & FX; verify it offsets fuel cost (margin-neutral)"],
 ["2","Zero-use tier growing","RT10+RT20 zero-use "+sgn(pct(bC('Zero').may26[0],bC('Zero').may25[0]))+"% YoY","High","Audit estimated/unread reads; report rev per active customer"],
 ["3","Streetlight (RT60) decline","Rev "+sgn(rcYoYR("RT60-ST"))+"% & kWh "+sgn(rcYoYK("RT60-ST"))+"% YoY","Med","Verify streetlight metering/billing completeness"],
 ["4","Revenue basis = net","~8-9% below GL/billed revenue","Med","Reconcile net→gross before board/external use"],
 ["5","Budget revenue corrupted","jps_budget.revenue=kWh; jps_le empty","Med","Reload budget revenue to enable rev-vs-plan bridge"],
 ["6","Large-account concentration","RT40-70 ≈ "+f1((LRG.reduce((a,r)=>a+D.rate[r].may26[1],0))/May26[R]*100)+"% of revenue, few accounts","Med","Monitor large-customer churn & tariff sensitivity monthly"],
 ["7","Source stub months","Jun–Dec-26 = 90/15 placeholders","Low","Exclude; refresh when actuals land"]];
const sev=t=>t=="High"?NEG:(t=="Med"?"E2864B":"7E8C9A");
s.addTable(rows.map((r,ri)=>r.map((c,ci)=>{
 if(ri==0)return{text:c,options:{fill:{color:DARK},color:"FFFFFF",bold:true,fontSize:11,align:ci==0?"center":"left",valign:"middle",fontFace:BF}};
 if(ci==3)return{text:c,options:{fill:{color:ri%2?"FFFFFF":"F1F5F9"},color:sev(c),bold:true,fontSize:10.5,align:"center",valign:"middle",fontFace:BF}};
 if(ci==0)return{text:c,options:{fill:{color:ri%2?"FFFFFF":"F1F5F9"},color:INK,bold:true,fontSize:10.5,align:"center",valign:"middle",fontFace:BF}};
 return{text:c,options:{fill:{color:ri%2?"FFFFFF":"F1F5F9"},color:INK,fontSize:10.5,valign:"middle",fontFace:BF}};
})),{x:0.5,y:1.55,w:12.3,colW:[0.5,2.8,3.5,1.1,4.4],rowH:0.62,border:{type:"solid",pt:0.5,color:LINEC},margin:[3,4,3,4]});
footer(s);

// ===== 16 RECOMMENDATIONS =====
s=pres.addSlide(); s.background={color:DARK};
s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:0.22,h:Ht,fill:{color:YEL}});
s.addText("RECOMMENDATIONS",{x:0.9,y:0.7,w:11,h:0.4,fontFace:BF,fontSize:13,color:YEL,bold:true,charSpacing:3,margin:0});
s.addText("Acting on May",{x:0.9,y:1.1,w:11,h:0.7,fontFace:HF,fontSize:32,color:"FFFFFF",bold:true,margin:0});
const recs=[
 ["1","Confirm the fuel/fixed driver","Base rate is flat, so the −J$"+f0(-BR.yoy.rate/1e6)+"M YoY 'fuel/rate' effect should be the IPP fuel pass-through + fixed/FX. Verify against the fuel-rate schedule and confirm it offsets fuel cost (margin-neutral) before treating it as lost revenue."],
 ["2","Reload the revenue budget","jps_budget.revenue_budget is corrupted (=kWh) and jps_le is empty — so revenue-vs-plan is impossible. Fix the load to unlock the budget revenue bridge."],
 ["3","Own the zero-use drift","RT10+RT20 zero-use accounts are up "+f1(pct(bC('Zero').may26[0],bC('Zero').may25[0]))+"% YoY. Confirm estimated/unread backlog; report kWh & revenue per active customer."],
 ["4","Fix RT60 streetlight","Both volume and revenue down double-digits — a metering/billing completeness gap, not demand. Quantify the catch-up."],
 ["5","Watch the large accounts","RT40-70 are ~"+f1((LRG.reduce((a,r)=>a+D.rate[r].may26[1],0))/May26[R]*100)+"% of revenue across a few hundred accounts — track churn & tariff sensitivity monthly."]];
recs.forEach((r,i)=>{const y=2.0+i*0.98;
 s.addShape(pres.shapes.OVAL,{x:0.95,y,w:0.6,h:0.6,fill:{color:YEL}});
 s.addText(r[0],{x:0.95,y,w:0.6,h:0.6,fontFace:HF,fontSize:22,color:DARK,bold:true,align:"center",valign:"middle",margin:0});
 s.addText([{text:r[1]+"   ",options:{bold:true,color:YEL,fontSize:15}},{text:r[2],options:{color:"D7E1EC",fontSize:12}}],
  {x:1.75,y:y-0.05,w:10.6,h:0.92,fontFace:BF,valign:"middle",lineSpacingMultiple:1.0,margin:0});});
s.addText("JPS Sales · billing pivot (net) · figures end May-2026 · J$ unless noted",{x:0.9,y:7.0,w:11.5,h:0.3,fontFace:BF,fontSize:10,color:"7E91A5",margin:0});

pres.writeFile({fileName:"D:\\Projects\\Sales_Platform\\analysis\\JPS_Sales_May2026_Performance_v3.pptx"}).then(f=>console.log("WROTE",f));
