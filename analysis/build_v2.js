// JPS Sales — MAY 2026 performance review (rebuilt on 'sales trend.xlsx' billing pivot)
// Source: net_revenue / net_kwh_billed_consump / cust_billed by month x rate x consumption bucket.
const pptxgen=require("pptxgenjs");
const D=require("./data_v2.json");

// ---- helpers ----
const MN=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const f1=v=>v.toLocaleString("en-US",{maximumFractionDigits:1,minimumFractionDigits:1});
const f0=v=>Math.round(v).toLocaleString("en-US");
const sgn=v=>(v>=0?"+":"")+f1(v);
const pct=(a,b)=>(a-b)/b*100;
const sum=a=>a.reduce((x,y)=>x+y,0);

// monthly: [y,mo,cust,rev,kwh]
const mon=D.monthly;
const idxMay25=mon.findIndex(r=>r[0]==2025&&r[1]==5);
const idxApr26=mon.findIndex(r=>r[0]==2026&&r[1]==4);
const idxMay26=mon.findIndex(r=>r[0]==2026&&r[1]==5);
const May25=mon[idxMay25], Apr26=mon[idxApr26], May26=mon[idxMay26];
// totals
const C=2,R=3,K=4;
const yoyR=pct(May26[R],May25[R]), yoyK=pct(May26[K],May25[K]), yoyC=pct(May26[C],May25[C]);
const momR=pct(May26[R],Apr26[R]), momK=pct(May26[K],Apr26[K]), momC=pct(May26[C],Apr26[C]);
const real=(r)=>r[R]/r[K]; // net J$/kWh
const realY=pct(real(May26),real(May25));
// YTD Jan-May
const ytd=(y)=>{const ms=mon.filter(r=>r[0]==y&&r[1]<=5);return[Math.max(...ms.map(r=>r[2])),sum(ms.map(r=>r[3])),sum(ms.map(r=>r[4]))];};
const Y25=ytd(2025),Y26=ytd(2026);
const ytdR=pct(Y26[1],Y25[1]), ytdK=pct(Y26[2],Y25[2]);

// rate classes
const RTN={RT10:"RT10 Residential",RT20:"RT20 Gen. Service",RT40:"RT40 Power",RT50:"RT50 Large Power","RT60-ST":"RT60 Streetlight",RT70:"RT70 Standby"};
const RTC={RT10:"FFC60B",RT20:"3B6EA5",RT40:"1F9D8B",RT50:"9B59B6","RT60-ST":"E2864B",RT70:"5D6D7E"};
const rks=Object.keys(D.rate);
const rcYoYR=k=>pct(D.rate[k].may26[1],D.rate[k].may25[1]);
const rcYoYK=k=>pct(D.rate[k].may26[2],D.rate[k].may25[2]);

// buckets (low->high)
const BO=['<Zero','Zero','<150','150>350','350>550','550>750','750>950','over 950'];
const BL={'<Zero':"Credits (<0)",'Zero':"Zero-use",'<150':"<150",'150>350':"150–350",'350>550':"350–550",'550>750':"550–750",'750>950':"750–950",'over 950':">950"};
const bC=b=>D.buckets[b]; // {may25:[c,r,k],apr26,may26}
const consume=['<150','150>350','350>550','550>750','750>950','over 950']; // kwh>0 buckets

// ---- monthly bucket movement (17 months) ----
const BM=D.bucketsMonthly;                       // [{ym:[y,mo], b:{bucket:[c,rev,kwh]}}]
const labBM=BM.map(r=>MN[r.ym[1]-1]+(r.ym[0]==2025?"·25":"·26"));
const totRevB=mon.map(r=>r[3]/1e9);              // total net revenue J$B
const realM=mon.map(r=>r[3]/r[4]);               // realization J$/kWh
// revenue stack series: Fixed(=Zero+<Zero net) + 6 consuming buckets -> sums to total
const stkKeys=['FIX','<150','150>350','350>550','550>750','750>950','over 950'];
const stkLbl={FIX:"Fixed/credits",'<150':"<150",'150>350':"150–350",'350>550':"350–550",'550>750':"550–750",'750>950':"750–950",'over 950':">950"};
const stkCol={FIX:"B7C4D1",'<150':"CAD8EC",'150>350':"9DBDE0",'350>550':"6E96C4",'550>750':"4E7CB0",'750>950':"345D8C",'over 950':"FFC60B"};
const revStk=k=>BM.map(r=> (k=='FIX'? (r.b['Zero'][1]+r.b['<Zero'][1]) : r.b[k][1])/1e9 );
// customer mix (100% stacked) over 8 buckets
const custCol={'<Zero':"D9534F",'Zero':"9AA7B4",'<150':"CAD8EC",'150>350':"9DBDE0",'350>550':"6E96C4",'550>750':"4E7CB0",'750>950':"345D8C",'over 950':"FFC60B"};
const custStk=b=>BM.map(r=> Math.max(r.b[b][0],0) );

// ---- revenue bridge May-25 -> May-26 (all rates) ----
const bk0=k=>D.buckets[k].may25, bk1=k=>D.buckets[k].may26;   // [c,rev,kwh]
let Q0=0,Q1=0,Rc0=0,Rc1=0;
consume.forEach(k=>{Q0+=bk0(k)[2];Q1+=bk1(k)[2];Rc0+=bk0(k)[1];Rc1+=bk1(k)[1];});
const R0a=Rc0/Q0,R1a=Rc1/Q1;
let Rmix=0; consume.forEach(k=>{Rmix+=(bk1(k)[2]/Q1)*(bk0(k)[1]/bk0(k)[2]);});
const eVol=(Q1-Q0)*R0a, eMix=Q1*(Rmix-R0a), eRate=Q1*(R1a-Rmix);
const eFixed=bk1('Zero')[1]-bk0('Zero')[1], eCred=bk1('<Zero')[1]-bk0('<Zero')[1];
const R0tot=Rc0+bk0('Zero')[1]+bk0('<Zero')[1], R1tot=Rc1+bk1('Zero')[1]+bk1('<Zero')[1];
console.log('BRIDGE M:',[eVol,eMix,eRate,eFixed,eCred].map(v=>Math.round(v/1e6)),
 'sum',Math.round((eVol+eMix+eRate+eFixed+eCred)/1e6),'actual',Math.round((R1tot-R0tot)/1e6));

console.log("May YoY rev/kwh/cust",f1(yoyR),f1(yoyK),f1(yoyC),"real",f1(realY));
console.log("May MoM rev/kwh",f1(momR),f1(momK));
console.log("YTD rev/kwh",f1(ytdR),f1(ytdK));
console.log("Zero-use cust May25->26",bC('Zero').may25[0],"->",bC('Zero').may26[0],f1(pct(bC('Zero').may26[0],bC('Zero').may25[0])));

// ---- theme ----
const DARK="14202E",DARK2="1E2D40",YEL="FFC60B",LIGHT="F6F8FB",CARD="FFFFFF",
 INK="1B2A3A",MUT="6B7C8F",POS="1F9D8B",NEG="D9534F",BLU="3B6EA5",LINEC="E2E8F0";
const HF="Georgia",BF="Calibri";
const pres=new pptxgen(); pres.layout="LAYOUT_WIDE"; const W=13.3,Ht=7.5;
pres.author="JPS FP&A"; pres.title="JPS Sales — May 2026 Performance";
const sh=()=>({type:"outer",color:"000000",blur:7,offset:3,angle:135,opacity:0.16});
let PGN=1;
function footer(s){PGN++; s.addShape(pres.shapes.RECTANGLE,{x:0,y:Ht-0.32,w:W,h:0.32,fill:{color:DARK}});
 s.addText("JPS Sales · source: 'sales trend' billing pivot (net revenue / net kWh / cust billed) · Jan-25→May-26 · J$ unless noted",
 {x:0.4,y:Ht-0.32,w:11,h:0.32,fontFace:BF,fontSize:8,color:"9FB0C2",valign:"middle",margin:0});
 s.addText(String(PGN),{x:W-0.8,y:Ht-0.32,w:0.4,h:0.32,fontFace:BF,fontSize:9,color:"9FB0C2",align:"right",valign:"middle",margin:0});}
function header(s,kick,title){s.background={color:LIGHT};
 s.addText(kick.toUpperCase(),{x:0.5,y:0.32,w:11,h:0.3,fontFace:BF,fontSize:11,color:BLU,bold:true,charSpacing:3,margin:0});
 s.addText(title,{x:0.5,y:0.6,w:12.3,h:0.65,fontFace:HF,fontSize:26,color:INK,bold:true,margin:0});
 s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.26,w:0.9,h:0.06,fill:{color:YEL}});}
function cbase(extra){return Object.assign({chartArea:{fill:{color:CARD}},plotArea:{fill:{color:CARD}},
 catAxisLabelColor:MUT,valAxisLabelColor:MUT,catAxisLabelFontFace:BF,valAxisLabelFontFace:BF,
 catAxisLabelFontSize:10,valAxisLabelFontSize:9,valGridLine:{color:LINEC,size:0.5},catGridLine:{style:"none"},showLegend:false},extra);}

// ===== 1 TITLE =====
let s=pres.addSlide(); s.background={color:DARK};
s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:W,h:0.18,fill:{color:YEL}});
s.addShape(pres.shapes.RECTANGLE,{x:0,y:Ht-0.18,w:W,h:0.18,fill:{color:YEL}});
s.addText("JPS SALES PLATFORM · FP&A PERFORMANCE REVIEW",{x:0.9,y:1.45,w:11,h:0.4,fontFace:BF,fontSize:14,color:YEL,bold:true,charSpacing:3,margin:0});
s.addText("May 2026 Sales & Revenue Performance",{x:0.9,y:2.05,w:11.6,h:1.0,fontFace:HF,fontSize:40,color:"FFFFFF",bold:true,margin:0});
s.addText("Strong sequential rebound, soft year-on-year — a price & consumption-mix story",{x:0.9,y:3.15,w:11.6,h:0.5,fontFace:BF,fontSize:17,color:"C7D3E0",margin:0});
const strip=[["May sales (MoM)",sgn(momK)+"%","vs Apr-26"],["May revenue (MoM)",sgn(momR)+"%","vs Apr-26"],
 ["May revenue (YoY)",sgn(yoyR)+"%","vs May-25"],["Realization (YoY)",sgn(realY)+"%","J$"+f1(real(May26))+"/kWh net"]];
strip.forEach((c,i)=>{const x=0.9+i*2.95;
 s.addShape(pres.shapes.RECTANGLE,{x,y:4.3,w:2.7,h:1.5,fill:{color:DARK2},line:{color:"2C4258",width:1}});
 s.addShape(pres.shapes.RECTANGLE,{x,y:4.3,w:0.07,h:1.5,fill:{color:YEL}});
 s.addText(c[0].toUpperCase(),{x:x+0.2,y:4.45,w:2.4,h:0.3,fontFace:BF,fontSize:9.5,color:"9FB0C2",bold:true,charSpacing:1,margin:0});
 s.addText(c[1],{x:x+0.2,y:4.77,w:2.45,h:0.55,fontFace:HF,fontSize:23,color:(c[1].startsWith("+")?"6FE0C8":"FF8A80"),bold:true,margin:0});
 s.addText(c[2],{x:x+0.2,y:5.38,w:2.4,h:0.3,fontFace:BF,fontSize:10.5,color:"C7D3E0",margin:0});});
s.addText("Prepared "+new Date().toISOString().slice(0,10)+" · basis: billing pivot (net of taxes); see slide 3",{x:0.9,y:6.5,w:11.5,h:0.3,fontFace:BF,fontSize:11,color:"7E91A5",margin:0});

// ===== 2 EXEC SUMMARY =====
s=pres.addSlide(); header(s,"01 · Executive summary","May in one page");
const k=[["May sales YoY",sgn(yoyK)+"%",POS,f1(May26[K]/1e6)+"M kWh"],
 ["May revenue YoY",sgn(yoyR)+"%",NEG,"J$"+f1(May26[R]/1e9)+"B net"],
 ["Customers YoY",sgn(yoyC)+"%",POS,"+"+f0(May26[C]-May25[C])+" accts"],
 ["Realization YoY",sgn(realY)+"%",NEG,"J$"+f1(real(May26))+"/kWh"]];
k.forEach((c,i)=>{const x=0.5+i*3.12;
 s.addShape(pres.shapes.RECTANGLE,{x,y:1.5,w:2.92,h:1.5,fill:{color:CARD},line:{color:LINEC,width:1},shadow:sh()});
 s.addText(c[0].toUpperCase(),{x:x+0.18,y:1.64,w:2.6,h:0.45,fontFace:BF,fontSize:10,color:MUT,bold:true,charSpacing:1,margin:0});
 s.addText(c[1],{x:x+0.16,y:2.04,w:2.7,h:0.65,fontFace:HF,fontSize:31,color:c[2],bold:true,margin:0});
 s.addText(c[3],{x:x+0.18,y:2.68,w:2.65,h:0.28,fontFace:BF,fontSize:10.5,color:INK,margin:0});});
s.addText("What happened in May",{x:0.5,y:3.25,w:7,h:0.35,fontFace:HF,fontSize:16,color:INK,bold:true,margin:0});
s.addText([
 {text:"Sharp sequential rebound. ",options:{bold:true,bullet:{code:"2022",color:YEL},breakLine:false,color:INK}},
 {text:"kWh "+sgn(momK)+"% and revenue "+sgn(momR)+"% vs a soft April — demand snapped back.",options:{color:INK,breakLine:true}},
 {text:"Still below last May. ",options:{bold:true,bullet:{code:"2022",color:YEL},breakLine:false,color:INK}},
 {text:"Volume "+sgn(yoyK)+"% and customers "+sgn(yoyC)+"%, yet revenue "+sgn(yoyR)+"% — realization fell "+f1(-realY)+"%.",options:{color:INK,breakLine:true}},
 {text:"The gap is price, not demand. ",options:{bold:true,bullet:{code:"2022",color:YEL},breakLine:false,color:INK}},
 {text:"Revenue YoY is ≈ −3.4% in every consuming class (RT10/20/40/50) — a uniform tariff/fuel effect.",options:{color:INK,breakLine:true}},
 {text:"Mix is shifting down. ",options:{bold:true,bullet:{code:"2022",color:YEL},breakLine:false,color:INK}},
 {text:"Zero-use accounts +"+f1(pct(bC('Zero').may26[0],bC('Zero').may25[0]))+"% YoY; growth is landing in zero/low-use tiers.",options:{color:INK,breakLine:true}}
],{x:0.5,y:3.65,w:7.15,h:2.6,fontFace:BF,fontSize:12.5,lineSpacingMultiple:1.05,paraSpaceAfter:6,margin:0});
s.addShape(pres.shapes.RECTANGLE,{x:7.95,y:3.25,w:4.85,h:3.5,fill:{color:"FBEFD0"},line:{color:YEL,width:1.5}});
s.addText([{text:"⚑  ",options:{color:"B8860B"}},{text:"WATCH-LIST",options:{bold:true,color:"8A6D1B"}}],{x:8.15,y:3.4,w:4.5,h:0.35,fontFace:BF,fontSize:12,charSpacing:1,margin:0});
s.addText([
 {text:"Streetlight (RT60) revenue "+sgn(rcYoYR("RT60-ST"))+"% YoY (kWh "+sgn(rcYoYK("RT60-ST"))+"%) — billing/metering gap.",options:{bullet:{code:"25B8",color:NEG},breakLine:true,color:"5A4A1E"}},
 {text:">950 kWh bucket = "+f1(bC('over 950').may26[1]/May26[R]/10)+"0% of revenue; its kWh +"+f1(pct(bC('over 950').may26[2],bC('over 950').may25[2]))+"% but revenue "+sgn(pct(bC('over 950').may26[1],bC('over 950').may25[1]))+"%.",options:{bullet:{code:"25B8",color:NEG},breakLine:true,color:"5A4A1E"}},
 {text:"Billing credits (<0 bucket) widened to J$"+f1(-bC('<Zero').may26[1]/1e6)+"M (from J$"+f1(-bC('<Zero').may25[1]/1e6)+"M).",options:{bullet:{code:"25B8",color:NEG},breakLine:true,color:"5A4A1E"}},
 {text:"Revenue here is net of taxes — ~8–9% below billed/GL revenue. Reconcile before board use.",options:{bullet:{code:"25B8",color:NEG},color:"5A4A1E"}}
],{x:8.15,y:3.8,w:4.5,h:2.9,fontFace:BF,fontSize:11,lineSpacingMultiple:1.02,paraSpaceAfter:8,margin:0});
footer(s,2);

// ===== 3 BASIS =====
s=pres.addSlide(); header(s,"02 · Basis & data notes","Read before the charts");
const notes=[
 ["New source","Rebuilt on the 'sales trend' billing pivot: net revenue, net kWh billed, and customers billed by month × rate class × consumption bucket — finer than the prior platform extract."],
 ["Net revenue basis","'net_revenue' runs ~8–9% below the platform/GL revenue used previously (e.g. May J$"+f1(May26[R]/1e9)+"B vs ~J$15.3B). kWh ties out almost exactly. Treat revenue here as net-of-tax; reconcile to GL before external use."],
 ["Consumption buckets now available","Customers are tiered by monthly kWh: <150, 150–350, 350–550, 550–750, 750–950, >950, plus Zero (no use) and <0 (credits). This is the mix view the platform data could not give."],
 ["Future months are placeholders","Jun-26→Dec-26 carry stub values (90 / 15) in the source — excluded. Analysis ends at May-26."]];
notes.forEach((n,i)=>{const col=i%2,row=Math.floor(i/2);const x=0.5+col*6.25,y=1.55+row*2.45;
 s.addShape(pres.shapes.RECTANGLE,{x,y,w:5.95,h:2.25,fill:{color:CARD},line:{color:LINEC,width:1},shadow:sh()});
 s.addShape(pres.shapes.RECTANGLE,{x,y,w:0.09,h:2.25,fill:{color:i==1?NEG:BLU}});
 s.addText(n[0],{x:x+0.25,y:y+0.18,w:5.5,h:0.4,fontFace:HF,fontSize:15,color:(i==1?NEG:INK),bold:true,margin:0});
 s.addText(n[1],{x:x+0.25,y:y+0.66,w:5.55,h:1.45,fontFace:BF,fontSize:11.5,color:INK,lineSpacingMultiple:1.05,margin:0});});
footer(s,3);

// ===== 4 MAY HEADLINE =====
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
 {text:"Volume recovered "+f1((May26[K]-Apr26[K])/1e6)+"M kWh over April (+"+f1(momK)+"%), led by the high-use tier.",options:{color:"DCE6F0",bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:"Revenue outpaced volume MoM (+"+f1(momR)+"% vs +"+f1(momK)+"%) — realization repaired after April's dip.",options:{color:"DCE6F0",bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:"Against May-25, +"+f1(yoyK)+"% kWh & +"+f1(yoyC)+"% customers but "+sgn(yoyR)+"% revenue — the YoY shortfall is entirely price.",options:{color:"DCE6F0",bullet:{code:"2022",color:YEL},breakLine:true}}
],{x:8.55,y:3.95,w:4.1,h:2.7,fontFace:BF,fontSize:11.5,lineSpacingMultiple:1.05,paraSpaceAfter:9,margin:0});
footer(s,4);

// ===== 5 TREND =====
s=pres.addSlide(); header(s,"04 · Context","Sales, revenue & customers — indexed to Jan-25 = 100");
const labels17=mon.map(r=>MN[r[1]-1]+(r[0]==2025?"·25":"·26"));
const b0=mon[0];
const iK=mon.map(r=>r[4]/b0[4]*100),iR=mon.map(r=>r[3]/b0[3]*100),iC=mon.map(r=>r[2]/b0[2]*100);
s.addChart(pres.charts.LINE,[
 {name:"Sales (kWh)",labels:labels17,values:iK.map(v=>+v.toFixed(1))},
 {name:"Revenue (net J$)",labels:labels17,values:iR.map(v=>+v.toFixed(1))},
 {name:"Customers",labels:labels17,values:iC.map(v=>+v.toFixed(1))}
],cbase({x:0.5,y:1.5,w:8.55,h:5.3,lineSize:2.5,lineSmooth:true,chartColors:[BLU,YEL,POS],
 showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:11,valAxisMinVal:60,valAxisMaxVal:120,catAxisLabelRotate:-45}));
s.addShape(pres.shapes.RECTANGLE,{x:9.3,y:1.5,w:3.5,h:5.3,fill:{color:CARD},line:{color:LINEC,width:1},shadow:sh()});
s.addText("Context",{x:9.5,y:1.66,w:3.15,h:0.35,fontFace:HF,fontSize:14,color:INK,bold:true,margin:0});
s.addText([
 {text:"Customers (green) drift up all year; sales & revenue sit below the 2025 band.",options:{bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:"May-26 is the year's high point so far — the rebound is real, not just seasonal noise.",options:{bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:"Revenue (yellow) tracks below sales (blue) in 2026 — the realization gap that opened YoY.",options:{bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:"Nov-25 dip = partial billing cycle (data), not demand.",options:{bullet:{code:"2022",color:NEG},breakLine:true}}
],{x:9.5,y:2.1,w:3.15,h:4.5,fontFace:BF,fontSize:11,color:INK,lineSpacingMultiple:1.03,paraSpaceAfter:9,margin:0});
footer(s,5);

// ===== TOTAL REVENUE TREND =====
s=pres.addSlide(); header(s,"05 · Total revenue","Total net revenue & realization — 17-month trend");
s.addText("Total net revenue (J$ B)",{x:0.5,y:1.45,w:8,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[{name:"Net revenue",labels:labBM,values:totRevB.map(v=>+v.toFixed(2))}],
 cbase({x:0.4,y:1.75,w:12.4,h:2.55,barDir:"col",chartColors:[BLU],showValue:true,dataLabelFormatCode:"0.0",
  dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:8.5,dataLabelColor:INK,valAxisHidden:true,valAxisMaxVal:17,catAxisLabelFontSize:8.5,catAxisLabelRotate:-40}));
s.addText("Realization — net J$/kWh",{x:0.5,y:4.45,w:8,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.LINE,[{name:"J$/kWh",labels:labBM,values:realM.map(v=>+v.toFixed(1))}],
 cbase({x:0.4,y:4.75,w:12.4,h:2.0,lineSize:2.5,lineSmooth:true,chartColors:[YEL],lineDataSymbol:"circle",lineDataSymbolSize:5,
  showValue:true,dataLabelPosition:"t",dataLabelFontFace:BF,dataLabelFontSize:8,dataLabelColor:"8A6D1B",
  valAxisMinVal:40,valAxisMaxVal:60,catAxisLabelFontSize:8.5,catAxisLabelRotate:-40}));
footer(s);

// ===== REVENUE BY BUCKET OVER TIME =====
s=pres.addSlide(); header(s,"06 · Bucket vs revenue","Net revenue by consumption tier — stack height = total revenue");
s.addChart(pres.charts.BAR, stkKeys.map(k=>({name:stkLbl[k],labels:labBM,values:revStk(k).map(v=>+v.toFixed(2))})),
 cbase({x:0.4,y:1.55,w:9.0,h:5.2,barDir:"col",barGrouping:"stacked",chartColors:stkKeys.map(k=>stkCol[k]),
  showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:9,valAxisTitle:"J$ B",showTitle:false,
  catAxisLabelFontSize:8,catAxisLabelRotate:-45}));
s.addShape(pres.shapes.RECTANGLE,{x:9.55,y:1.55,w:3.25,h:5.2,fill:{color:CARD},line:{color:LINEC,width:1},shadow:sh()});
s.addText("Read",{x:9.75,y:1.7,w:2.9,h:0.35,fontFace:HF,fontSize:14,color:INK,bold:true,margin:0});
s.addText([
 {text:"Stack height tracks total revenue; the gold band (>950) is the swing factor month to month.",options:{bullet:{code:"2022",color:YEL},breakLine:true,color:INK}},
 {text:"The >950 tier drives both the seasonal peaks and the Apr-26 dip / May-26 rebound.",options:{bullet:{code:"2022",color:YEL},breakLine:true,color:INK}},
 {text:"Lower tiers (<150–550) are stable — the volatility lives at the top.",options:{bullet:{code:"2022",color:MUT},breakLine:true,color:INK}},
 {text:"Nov-25 = partial billing cycle (data).",options:{bullet:{code:"2022",color:NEG},color:INK}}
],{x:9.75,y:2.15,w:2.9,h:4.4,fontFace:BF,fontSize:10.5,lineSpacingMultiple:1.03,paraSpaceAfter:8,margin:0});
footer(s);

// ===== CUSTOMER MIX OVER TIME =====
s=pres.addSlide(); header(s,"07 · Bucket movement","Customer mix by tier — share of accounts over time");
s.addChart(pres.charts.BAR, BO.map(b=>({name:BL[b],labels:labBM,values:custStk(b)})),
 cbase({x:0.4,y:1.55,w:9.0,h:5.2,barDir:"col",barGrouping:"percentStacked",chartColors:BO.map(b=>custCol[b]),
  showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:9,catAxisLabelFontSize:8,catAxisLabelRotate:-45,
  valAxisLabelFormatCode:'0%'}));
s.addShape(pres.shapes.RECTANGLE,{x:9.55,y:1.55,w:3.25,h:5.2,fill:{color:"FBEFD0"},line:{color:YEL,width:1.5}});
s.addText("The drift",{x:9.75,y:1.7,w:2.9,h:0.35,fontFace:HF,fontSize:14,color:"8A6D1B",bold:true,margin:0});
const zsh25=bk0('Zero')[0]/May25[C]*100, zsh26=bk1('Zero')[0]/May26[C]*100;
s.addText([
 {text:"Zero-use band (grey) thickened from "+f1(zsh25)+"% to "+f1(zsh26)+"% of accounts — visible step-up after Dec-25.",options:{bullet:{code:"2022",color:NEG},breakLine:true,color:"5A4A1E"}},
 {text:"The <150 band (pale blue) is shrinking as customers fall into Zero-use.",options:{bullet:{code:"2022",color:NEG},breakLine:true,color:"5A4A1E"}},
 {text:"Mid/high tiers are a thin, stable sliver of accounts — but (prev slide) most of the revenue.",options:{bullet:{code:"2022",color:YEL},breakLine:true,color:"5A4A1E"}},
 {text:"Mix is migrating down: more accounts, lower average consumption.",options:{bullet:{code:"2022",color:"B8860B"},bold:true,color:"5A4A1E"}}
],{x:9.75,y:2.15,w:2.9,h:4.4,fontFace:BF,fontSize:10.5,lineSpacingMultiple:1.03,paraSpaceAfter:8,margin:0});
footer(s);

// ===== 6 RATE CLASS DIVERGENCE =====
s=pres.addSlide(); header(s,"08 · By rate class","May YoY: volume holds, revenue falls — across the board");
s.addChart(pres.charts.BAR,[
 {name:"Sales kWh YoY %",labels:rks.map(k=>k.replace("-ST","")),values:rks.map(k=>+rcYoYK(k).toFixed(1))},
 {name:"Revenue YoY %",labels:rks.map(k=>k.replace("-ST","")),values:rks.map(k=>+rcYoYR(k).toFixed(1))}
],cbase({x:0.4,y:1.6,w:8.5,h:5.15,barDir:"col",chartColors:[BLU,YEL],showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:11,
 showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:9,dataLabelColor:INK,valAxisMinVal:-34,valAxisMaxVal:18}));
s.addShape(pres.shapes.RECTANGLE,{x:9.15,y:1.6,w:3.65,h:5.15,fill:{color:"FBEFD0"},line:{color:YEL,width:1.5}});
s.addText("Uniform price effect",{x:9.35,y:1.75,w:3.3,h:0.35,fontFace:HF,fontSize:14,color:"8A6D1B",bold:true,margin:0});
s.addText([
 {text:"RT10/20/40/50 all show revenue ≈ −3.3 to −3.6% YoY despite flat-to-up volume — a tariff/fuel reduction, not lost demand.",options:{color:"5A4A1E",bullet:{code:"2022",color:NEG},breakLine:true}},
 {text:"RT50 Large Power: kWh "+sgn(rcYoYK("RT50"))+"% yet revenue "+sgn(rcYoYR("RT50"))+"% — widest squeeze.",options:{color:"5A4A1E",bullet:{code:"2022",color:NEG},breakLine:true}},
 {text:"RT60 Streetlight is the outlier: both down sharply ("+sgn(rcYoYR("RT60-ST"))+"% rev) — chase metering/billing.",options:{color:"5A4A1E",bullet:{code:"2022",color:NEG},breakLine:true}},
 {text:"RT70 Standby the lone gainer (+"+f1(rcYoYR("RT70"))+"% rev).",options:{color:"5A4A1E",bullet:{code:"2022",color:POS},breakLine:true}},
 {text:"Action: confirm the fuel pass-through / tariff change applied May-25 → May-26.",options:{color:"5A4A1E",bold:true,bullet:{code:"2022",color:"B8860B"}}}
],{x:9.35,y:2.2,w:3.3,h:4.5,fontFace:BF,fontSize:10.5,lineSpacingMultiple:1.03,paraSpaceAfter:7,margin:0});
footer(s,6);

// ===== 7 CONSUMPTION BUCKETS — customer distribution =====
s=pres.addSlide(); header(s,"09 · Consumption mix","Where the customers sit — and how it shifted");
// customer count by bucket May-26 (horizontal) + YoY delta labels
s.addText("Customers by consumption tier (May-26, '000)",{x:0.5,y:1.5,w:7,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[{name:"cust",labels:BO.map(b=>BL[b]),values:BO.map(b=>+(bC(b).may26[0]/1000).toFixed(1))}],
 cbase({x:0.4,y:1.85,w:6.7,h:4.5,barDir:"bar",chartColors:[BLU],showValue:true,dataLabelPosition:"outEnd",
  dataLabelFontFace:BF,dataLabelFontSize:9,dataLabelColor:INK,valAxisHidden:true,valAxisMaxVal:430,catAxisLabelColor:INK,catAxisLabelFontSize:10,barGapWidthPct:40}));
// YoY change in customers per bucket
s.addText("YoY change in customers (May-26 vs May-25)",{x:7.4,y:1.5,w:5.4,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
const dCust=BO.map(b=>bC(b).may26[0]-bC(b).may25[0]);
s.addChart(pres.charts.BAR,[{name:"Δcust",labels:BO.map(b=>BL[b]),values:dCust.map(v=>+(v/1000).toFixed(1))}],
 cbase({x:7.3,y:1.85,w:5.5,h:4.5,barDir:"bar",chartColors:[POS],
  showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:9,dataLabelColor:INK,
  valAxisHidden:true,valAxisMinVal:-15,valAxisMaxVal:21,catAxisLabelColor:INK,catAxisLabelFontSize:10,barGapWidthPct:40}));
s.addText("'000 accounts. Positive = more customers in that tier vs last May.",{x:0.5,y:6.5,w:8,h:0.25,fontFace:BF,fontSize:9,italic:true,color:MUT,margin:0});
footer(s,7);

// ===== 8 BUCKET MIGRATION / where volume & revenue are =====
s=pres.addSlide(); header(s,"10 · Mix vs value","Most customers are low-use; the value sits at the top");
// revenue share by bucket (May26) horizontal + kwh share
const totR=May26[R], totK=May26[K];
s.addText("Share of customers vs share of revenue (May-26)",{x:0.5,y:1.5,w:8,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[
 {name:"% customers",labels:BO.map(b=>BL[b]),values:BO.map(b=>+(bC(b).may26[0]/May26[C]*100).toFixed(1))},
 {name:"% revenue",labels:BO.map(b=>BL[b]),values:BO.map(b=>+(Math.max(bC(b).may26[1],0)/totR*100).toFixed(1))}
],cbase({x:0.4,y:1.85,w:8.4,h:4.9,barDir:"bar",chartColors:["A9B7C7",YEL],showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:10,
 showValue:true,dataLabelFormatCode:'0.0"%"',dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:8.5,dataLabelColor:INK,
 valAxisHidden:true,valAxisMaxVal:66,catAxisLabelColor:INK,catAxisLabelFontSize:9.5}));
s.addShape(pres.shapes.RECTANGLE,{x:9.05,y:1.85,w:3.75,h:4.9,fill:{color:CARD},line:{color:LINEC,width:1},shadow:sh()});
s.addText("Concentration",{x:9.25,y:2.0,w:3.4,h:0.35,fontFace:HF,fontSize:14,color:INK,bold:true,margin:0});
const c950=bC('over 950').may26, share950R=c950[1]/totR*100, share950C=c950[0]/May26[C]*100;
const lowC=(bC('<150').may26[0]+bC('Zero').may26[0])/May26[C]*100;
s.addText([
 {text:"The >950 kWh tier is just "+f1(share950C)+"% of accounts but "+f1(share950R)+"% of revenue — the book is top-heavy.",options:{bullet:{code:"2022",color:YEL},breakLine:true,color:INK}},
 {text:"Zero-use + <150 kWh = "+f1(lowC)+"% of all accounts yet a small slice of revenue.",options:{bullet:{code:"2022",color:MUT},breakLine:true,color:INK}},
 {text:"Revenue risk is concentrated: a small move in the top tier's tariff swings the whole result (see slide 6).",options:{bullet:{code:"2022",color:NEG},breakLine:true,color:INK}},
 {text:"Growth strategy should protect & grow the mid tiers (350–950 kWh), which are rising in count.",options:{bullet:{code:"2022",color:POS},color:INK}}
],{x:9.25,y:2.45,w:3.4,h:4.2,fontFace:BF,fontSize:10.5,lineSpacingMultiple:1.03,paraSpaceAfter:8,margin:0});
footer(s,8);

// ===== 9 REALIZATION SQUEEZE BY BUCKET =====
s=pres.addSlide(); header(s,"11 · The squeeze","Realization fell in every tier — May-25 vs May-26");
const rz25=consume.map(b=>bC(b).may25[1]/bC(b).may25[2]);
const rz26=consume.map(b=>bC(b).may26[1]/bC(b).may26[2]);
s.addChart(pres.charts.BAR,[
 {name:"May-25 J$/kWh",labels:consume.map(b=>BL[b]),values:rz25.map(v=>+v.toFixed(1))},
 {name:"May-26 J$/kWh",labels:consume.map(b=>BL[b]),values:rz26.map(v=>+v.toFixed(1))}
],cbase({x:0.4,y:1.6,w:8.5,h:5.15,barDir:"col",chartColors:["A9B7C7",NEG],showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:11,
 showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:9,dataLabelColor:INK,valAxisHidden:true,valAxisMaxVal:70,valAxisMinVal:0}));
s.addShape(pres.shapes.RECTANGLE,{x:9.15,y:1.6,w:3.65,h:5.15,fill:{color:DARK}});
s.addText("Net realization, J$/kWh",{x:9.35,y:1.75,w:3.3,h:0.35,fontFace:HF,fontSize:14,color:YEL,bold:true,margin:0});
const sq950=pct(rz26[5],rz25[5]);
s.addText([
 {text:"Unit revenue fell ~4–6% in every consuming tier — the clearest evidence of a price/fuel cut, not a volume problem.",options:{color:"DCE6F0",bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:">950 kWh tier: J$"+f1(rz25[5])+" → J$"+f1(rz26[5])+" /kWh ("+sgn(sq950)+"%) — and it carries most of the revenue.",options:{color:"DCE6F0",bullet:{code:"2022",color:NEG},breakLine:true}},
 {text:"Lower tiers run a higher unit rate (fixed-charge effect); the top tier is the cheapest per kWh.",options:{color:"DCE6F0",bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:"Quantified on the next slide: rate alone cost −J$"+f0(-eRate/1e6)+"M of revenue YoY.",options:{color:"FFE9A8",bold:true,bullet:{code:"2022",color:YEL}}}
],{x:9.35,y:2.2,w:3.3,h:4.5,fontFace:BF,fontSize:10.5,lineSpacingMultiple:1.03,paraSpaceAfter:8,margin:0});
footer(s,9);

// ===== REVENUE BRIDGE =====
s=pres.addSlide(); header(s,"12 · Revenue bridge","Why May revenue fell J$"+f1((R0tot-R1tot)/1e6)+"M YoY — volume, mix & rate");
// waterfall steps: [label, delta, type]  type: start/end/up/down
const steps=[
 ["May-25",R0tot,"start"],
 ["Volume",eVol,eVol>=0?"up":"down"],
 ["Mix",eMix,eMix>=0?"up":"down"],
 ["Rate",eRate,eRate>=0?"up":"down"],
 ["Fixed chg",eFixed,eFixed>=0?"up":"down"],
 ["Credits",eCred,eCred>=0?"up":"down"],
 ["May-26",R1tot,"end"]];
// running cumulative (value at top of each floating bar)
const vMin=13000, FLOOR=vMin*1e6; // J$M zoomed floor; start/end bars sit on the floor
let run=0; const seg=[];
steps.forEach((st,i)=>{
 if(st[2]=="start"){seg.push([FLOOR,st[1]]); run=st[1];}
 else if(st[2]=="end"){seg.push([FLOOR,st[1]]);}
 else { const lo=Math.min(run,run+st[1]), hi=Math.max(run,run+st[1]); seg.push([lo,hi]); run=run+st[1]; }
});
const allV=seg.flat(); const vMax=Math.max(...allV)/1e6;
const px=0.95, pw=11.5, py=2.05, ph=4.0, slot=pw/steps.length, bw=slot*0.62;
const mapY=v=>py+ph-(v-vMin)/(vMax-vMin)*ph;   // v in J$M
// baseline + axis frame
s.addShape(pres.shapes.RECTANGLE,{x:px,y:py,w:pw,h:ph,fill:{color:CARD},line:{color:LINEC,width:1}});
[13000,13500,14000,14500].forEach(g=>{const y=mapY(g); s.addShape(pres.shapes.LINE,{x:px,y,w:pw,h:0,line:{color:LINEC,width:0.5}});
 s.addText("J$"+f1(g/1000)+"B",{x:px-0.85,y:y-0.12,w:0.8,h:0.24,fontFace:BF,fontSize:8,color:MUT,align:"right",valign:"middle",margin:0});});
steps.forEach((st,i)=>{const cx=px+i*slot+(slot-bw)/2; const lo=seg[i][0]/1e6,hi=seg[i][1]/1e6;
 const yTop=mapY(hi), hgt=Math.max(mapY(lo)-mapY(hi),0.02);
 const col=st[2]=="start"?DARK2:st[2]=="end"?YEL:st[2]=="up"?POS:NEG;
 s.addShape(pres.shapes.RECTANGLE,{x:cx,y:yTop,w:bw,h:hgt,fill:{color:col}});
 // value label
 const lab=(st[2]=="start"||st[2]=="end")? "J$"+f1(st[1]/1e9)+"B" : sgn(st[1]/1e6).replace("+","+")+"M";
 const lc=(st[2]=="up")?"15715F":(st[2]=="down")?"A6332E":INK;
 s.addText((st[2]=="start"||st[2]=="end")?lab:(st[1]>=0?"+":"")+f0(st[1]/1e6)+"M",
  {x:cx-0.25,y:(st[1]<0&&st[2]!="end"&&st[2]!="start")?mapY(lo)+0.03:yTop-0.3,w:bw+0.5,h:0.28,fontFace:BF,fontSize:9.5,bold:true,color:lc,align:"center",margin:0});
 // category label
 s.addText(st[0],{x:cx-0.25,y:py+ph+0.08,w:bw+0.5,h:0.3,fontFace:BF,fontSize:10,color:INK,align:"center",margin:0});
 // connector
 if(i<steps.length-1 && st[2]!="start"){const yC=mapY(run/1e6); }
});
// connectors between bars at running level
let r2=0; steps.forEach((st,i)=>{ if(st[2]=="start"){r2=st[1];} else if(st[2]=="end"){} else {r2=r2+st[1];}
 if(i<steps.length-1){const yc=mapY(r2/1e6); const cx=px+i*slot+(slot-bw)/2+bw; const nx=px+(i+1)*slot+(slot-bw)/2;
  s.addShape(pres.shapes.LINE,{x:cx,y:yc,w:nx-cx,h:0,line:{color:"9AA7B4",width:0.75,dashType:"dash"}});}});
// commentary
s.addText([
 {text:"Volume added J$"+f0(eVol/1e6)+"M (more kWh), but ",options:{color:INK}},
 {text:"rate cut J$"+f0(-eRate/1e6)+"M",options:{color:NEG,bold:true}},
 {text:" — the price/fuel effect — and mix cost a further J$"+f0(-eMix/1e6)+"M as customers shifted to lower-rate tiers. Net: revenue −J$"+f1((R0tot-R1tot)/1e6)+"M (−"+f1((R0tot-R1tot)/R0tot*100)+"%) despite +"+f1(yoyK)+"% volume.",options:{color:INK}}
],{x:0.95,y:6.55,w:11.5,h:0.55,fontFace:BF,fontSize:11.5,lineSpacingMultiple:1.0,align:"center",margin:0});
footer(s);

// ===== 10 ZERO-USE & ADJUSTMENTS =====
s=pres.addSlide(); header(s,"13 · Zero-use & credits","The non-consuming tail is growing");
// zero-use customers May25/Apr26/May26 + credits
s.addText("Zero-use accounts ('000)",{x:0.5,y:1.5,w:6,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[{name:"Zero-use",labels:["May-25","Apr-26","May-26"],values:[bC('Zero').may25[0],bC('Zero').apr26[0],bC('Zero').may26[0]].map(v=>+(v/1000).toFixed(1))}],
 cbase({x:0.4,y:1.85,w:5.9,h:4.55,barDir:"col",chartColors:[BLU],showValue:true,dataLabelPosition:"outEnd",
  dataLabelFontFace:BF,dataLabelFontSize:11,dataLabelColor:INK,valAxisHidden:true,valAxisMaxVal:95,valAxisMinVal:0,barGapWidthPct:70}));
s.addText("Billing credits — '<0' bucket (J$ M)",{x:6.7,y:1.5,w:6,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[{name:"Credits",labels:["May-25","Apr-26","May-26"],values:[bC('<Zero').may25[1],bC('<Zero').apr26[1],bC('<Zero').may26[1]].map(v=>+(v/1e6).toFixed(1))}],
 cbase({x:6.6,y:1.85,w:6.1,h:4.55,barDir:"col",chartColors:[NEG],showValue:true,dataLabelPosition:"outEnd",
  dataLabelFontFace:BF,dataLabelFontSize:11,dataLabelColor:NEG,valAxisHidden:true,valAxisMaxVal:4,valAxisMinVal:-26,barGapWidthPct:70}));
s.addText([
 {text:"Zero-use accounts are up "+f1(pct(bC('Zero').may26[0],bC('Zero').may25[0]))+"% YoY ("+f0(bC('Zero').may25[0])+" → "+f0(bC('Zero').may26[0])+"). These pay a fixed charge only — they dilute revenue-per-customer and signal estimated/unread or vacant accounts to investigate.    ",options:{color:INK,breakLine:true}},
 {text:"Credits in the '<0' tier widened to J$"+f1(-bC('<Zero').may26[1]/1e6)+"M (from J$"+f1(-bC('<Zero').may25[1]/1e6)+"M) — confirm these are routine corrections, not a systemic billing issue.",options:{color:INK}}
],{x:0.5,y:6.45,w:12.3,h:0.55,fontFace:BF,fontSize:10.5,lineSpacingMultiple:1.0,margin:0});
footer(s,10);

// ===== 11 ANOMALY REGISTER =====
s=pres.addSlide(); header(s,"14 · Watch-list","Consolidated register");
const rows=[
 ["#","Item","Evidence (May-26)","Severity","Action"],
 ["1","Realization squeeze","Bridge: rate −J$"+f0(-eRate/1e6)+"M vs volume +J$"+f0(eVol/1e6)+"M YoY","High","Confirm tariff & fuel pass-through behind the rate effect"],
 ["2","Zero-use tail growing","Zero-use accounts "+sgn(pct(bC('Zero').may26[0],bC('Zero').may25[0]))+"% YoY","High","Audit estimated/unread reads; track revenue per active customer"],
 ["3","Streetlight (RT60) decline","Rev "+sgn(rcYoYR("RT60-ST"))+"% & kWh "+sgn(rcYoYK("RT60-ST"))+"% YoY","Med","Verify streetlight metering/billing completeness"],
 ["4","Revenue basis = net","~8-9% below GL/billed revenue","Med","Reconcile net→gross before board/external use"],
 ["5","Top-tier concentration",">950 tier ≈ "+f1(share950R)+"% of revenue, "+f1(share950C)+"% of accounts","Med","Stress-test revenue to large-customer tariff moves"],
 ["6","Credits widening","'<0' bucket J$"+f1(-bC('<Zero').may26[1]/1e6)+"M","Low","Trace adjustment source; confirm non-systemic"],
 ["7","Source stub months","Jun–Dec-26 = 90/15 placeholders","Low","Exclude; refresh when actuals land"]];
const sev=t=>t=="High"?NEG:(t=="Med"?"E2864B":"7E8C9A");
s.addTable(rows.map((r,ri)=>r.map((c,ci)=>{
 if(ri==0)return{text:c,options:{fill:{color:DARK},color:"FFFFFF",bold:true,fontSize:11,align:ci==0?"center":"left",valign:"middle",fontFace:BF}};
 if(ci==3)return{text:c,options:{fill:{color:ri%2?"FFFFFF":"F1F5F9"},color:sev(c),bold:true,fontSize:10.5,align:"center",valign:"middle",fontFace:BF}};
 if(ci==0)return{text:c,options:{fill:{color:ri%2?"FFFFFF":"F1F5F9"},color:INK,bold:true,fontSize:10.5,align:"center",valign:"middle",fontFace:BF}};
 return{text:c,options:{fill:{color:ri%2?"FFFFFF":"F1F5F9"},color:INK,fontSize:10.5,valign:"middle",fontFace:BF}};
})),{x:0.5,y:1.55,w:12.3,colW:[0.5,2.7,3.5,1.1,4.5],rowH:0.6,border:{type:"solid",pt:0.5,color:LINEC},margin:[3,4,3,4]});
footer(s,11);

// ===== 12 RECOMMENDATIONS =====
s=pres.addSlide(); s.background={color:DARK};
s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:0.22,h:Ht,fill:{color:YEL}});
s.addText("RECOMMENDATIONS",{x:0.9,y:0.7,w:11,h:0.4,fontFace:BF,fontSize:13,color:YEL,bold:true,charSpacing:3,margin:0});
s.addText("Acting on May",{x:0.9,y:1.1,w:11,h:0.7,fontFace:HF,fontSize:32,color:"FFFFFF",bold:true,margin:0});
const recs=[
 ["1","Lock the rate/fuel assumption","The YoY gap is now decomposed (slide 13): +J$"+f0(eVol/1e6)+"M volume, −J$"+f0(-eRate/1e6)+"M rate, −J$"+f0(-eMix/1e6)+"M mix. Confirm the tariff/fuel change behind the −J$"+f0(-eRate/1e6)+"M and whether it recurs through H2."],
 ["2","Reconcile net vs GL revenue","This pivot is net of taxes (~8-9% below GL). Tie it to the ledger before the number goes to the board; standardise one revenue definition."],
 ["3","Investigate the zero-use tail","Zero-use accounts are up "+f1(pct(bC('Zero').may26[0],bC('Zero').may25[0]))+"% YoY. Confirm estimated/unread backlog and report kWh & revenue per active customer, not just account count."],
 ["4","Fix RT60 streetlight","Both volume and revenue down double-digits — almost certainly a metering/billing completeness gap, not demand. Quantify the catch-up."],
 ["5","Protect top-tier revenue",">950 kWh customers are ~"+f1(share950R)+"% of revenue. Track large-account churn and tariff sensitivity monthly."]];
recs.forEach((r,i)=>{const y=2.0+i*0.98;
 s.addShape(pres.shapes.OVAL,{x:0.95,y,w:0.6,h:0.6,fill:{color:YEL}});
 s.addText(r[0],{x:0.95,y,w:0.6,h:0.6,fontFace:HF,fontSize:22,color:DARK,bold:true,align:"center",valign:"middle",margin:0});
 s.addText([{text:r[1]+"   ",options:{bold:true,color:YEL,fontSize:15}},{text:r[2],options:{color:"D7E1EC",fontSize:12}}],
  {x:1.75,y:y-0.05,w:10.6,h:0.92,fontFace:BF,valign:"middle",lineSpacingMultiple:1.0,margin:0});});
s.addText("JPS Sales · billing pivot (net) · figures end May-2026 · J$ unless noted",{x:0.9,y:7.0,w:11.5,h:0.3,fontFace:BF,fontSize:10,color:"7E91A5",margin:0});

pres.writeFile({fileName:"D:\\Projects\\Sales_Platform\\analysis\\JPS_Sales_May2026_Performance_v2.pptx"}).then(f=>console.log("WROTE",f));
