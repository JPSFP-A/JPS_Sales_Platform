// JPS May-2026 Revenue Quality — US$ component view. Why volume ≠ energy sales.
const pptxgen=require("pptxgenjs");
const D=require("./usd.json");

const f1=v=>v.toLocaleString("en-US",{maximumFractionDigits:1,minimumFractionDigits:1});
const f0=v=>Math.round(v).toLocaleString("en-US");
const sgn=v=>(v>=0?"+":"")+f1(v);
const pct=(a,b)=>(a-b)/b*100;

const TOT=D.comp['None'];                  // total row
const comps=[['Fuel','E2864B'],['IPP','9B59B6'],['Energy','3B6EA5'],['Customer charge','1F9D8B'],['Other','9AA7B4']];
const C=k=>D.comp[k];
const mwh=D.ratio.mwh, nf=D.ratio.nonfuel, fu=D.ratio.fuel, tt=D.ratio.total, fx=D.fx;
const volMoM=pct(mwh.may,mwh.apr), volVB=pct(mwh.may,mwh.bud);
const totMoM=pct(TOT.may,TOT.apr), totVB=pct(TOT.may,TOT.bud), totYoY=pct(TOT.may,TOT.pyr);
const enExp=C('Energy').apr*(mwh.may/mwh.apr), enShort=C('Energy').may-enExp;
const RC=['Rate 10','Rate 20','Rate 40','Rate 50','Rate 60','Rate 70'];

// theme
const DARK="14202E",DARK2="1E2D40",YEL="FFC60B",LIGHT="F6F8FB",CARD="FFFFFF",
 INK="1B2A3A",MUT="6B7C8F",POS="1F9D8B",NEG="D9534F",BLU="3B6EA5",LINEC="E2E8F0";
const HF="Georgia",BF="Calibri";
const pres=new pptxgen(); pres.layout="LAYOUT_WIDE"; const W=13.3,Ht=7.5;
pres.author="JPS FP&A"; pres.title="JPS May 2026 Revenue Quality (US$)";
const sh=()=>({type:"outer",color:"000000",blur:7,offset:3,angle:135,opacity:0.16});
let PGN=1;
function footer(s){PGN++; s.addShape(pres.shapes.RECTANGLE,{x:0,y:Ht-0.32,w:W,h:0.32,fill:{color:DARK}});
 s.addText("JPS Revenue analysis (US$'000) · Apr vs May 2026 · Billing FX ≈ "+f1(fx.may)+" · components: Fuel/IPP pass-through + Energy/Customer (non-fuel)",
 {x:0.4,y:Ht-0.32,w:11.3,h:0.32,fontFace:BF,fontSize:8,color:"9FB0C2",valign:"middle",margin:0});
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
s.addText("JPS · FP&A · REVENUE QUALITY REVIEW",{x:0.9,y:1.4,w:11,h:0.4,fontFace:BF,fontSize:14,color:YEL,bold:true,charSpacing:3,margin:0});
s.addText("Volume isn't converting to energy sales",{x:0.9,y:2.0,w:11.8,h:1.0,fontFace:HF,fontSize:38,color:"FFFFFF",bold:true,margin:0});
s.addText("May 2026 · US$ component view — fuel tracked volume; the non-fuel energy charge did not",{x:0.9,y:3.05,w:11.8,h:0.5,fontFace:BF,fontSize:16,color:"C7D3E0",margin:0});
const strip=[["Volume (MoM)",sgn(volMoM)+"%","MWh"],["Total revenue (MoM)",sgn(totMoM)+"%","US$"],
 ["Energy revenue (MoM)",sgn(pct(C('Energy').may,C('Energy').apr))+"%","non-fuel"],["Non-fuel ¢/kWh (MoM)",sgn(pct(nf.may,nf.apr))+"%","realization"]];
strip.forEach((c,i)=>{const x=0.9+i*2.95;
 s.addShape(pres.shapes.RECTANGLE,{x,y:4.3,w:2.7,h:1.5,fill:{color:DARK2},line:{color:"2C4258",width:1}});
 s.addShape(pres.shapes.RECTANGLE,{x,y:4.3,w:0.07,h:1.5,fill:{color:YEL}});
 s.addText(c[0].toUpperCase(),{x:x+0.2,y:4.45,w:2.4,h:0.3,fontFace:BF,fontSize:9.5,color:"9FB0C2",bold:true,charSpacing:1,margin:0});
 s.addText(c[1],{x:x+0.2,y:4.77,w:2.45,h:0.55,fontFace:HF,fontSize:23,color:(c[1].startsWith("+")?"6FE0C8":"FF8A80"),bold:true,margin:0});
 s.addText(c[2],{x:x+0.2,y:5.38,w:2.4,h:0.3,fontFace:BF,fontSize:10.5,color:"C7D3E0",margin:0});});
s.addText("Prepared "+new Date().toISOString().slice(0,10)+" · figures in US$'000 unless noted",{x:0.9,y:6.5,w:11.8,h:0.3,fontFace:BF,fontSize:11,color:"7E91A5",margin:0});

// ===== 2 THE DISPROPORTION =====
s=pres.addSlide(); header(s,"01 · The anomaly","Volume up "+f1(volMoM)+"%, energy revenue down "+f1(-pct(C('Energy').may,C('Energy').apr))+"%");
s.addChart(pres.charts.BAR,[{name:"MoM %",labels:["Sales volume\n(MWh)","Energy revenue\n(US$)"],values:[+volMoM.toFixed(1),+pct(C('Energy').may,C('Energy').apr).toFixed(1)]}],
 cbase({x:0.5,y:1.7,w:5.6,h:4.9,barDir:"col",chartColors:[BLU],chartColorsOpacity:[100],
  showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:16,dataLabelColor:INK,dataLabelFormatCode:'0.0"%"',
  valAxisHidden:true,valAxisMinVal:-6,valAxisMaxVal:18,barGapWidthPct:80,catAxisLabelFontSize:12}));
// expected vs actual callout
s.addShape(pres.shapes.RECTANGLE,{x:6.5,y:1.7,w:6.3,h:2.35,fill:{color:CARD},line:{color:LINEC,width:1},shadow:sh()});
s.addText("If energy billed in line with volume",{x:6.75,y:1.88,w:5.9,h:0.35,fontFace:HF,fontSize:15,color:INK,bold:true,margin:0});
s.addText([{text:"Expected energy  ",options:{color:MUT,fontSize:13}},{text:"US$"+f0(enExp)+"k",options:{color:INK,bold:true,fontSize:15,breakLine:true}},
 {text:"Actual energy       ",options:{color:MUT,fontSize:13}},{text:"US$"+f0(C('Energy').may)+"k",options:{color:INK,bold:true,fontSize:15,breakLine:true}},
 {text:"Shortfall               ",options:{color:MUT,fontSize:13}},{text:"−US$"+f0(-enShort)+"k  (~US$"+f1(-enShort/1000)+"M short)",options:{color:NEG,bold:true,fontSize:16}}],
 {x:6.75,y:2.35,w:5.9,h:1.55,fontFace:BF,lineSpacingMultiple:1.35,margin:0});
s.addShape(pres.shapes.RECTANGLE,{x:6.5,y:4.25,w:6.3,h:2.35,fill:{color:"FBEFD0"},line:{color:YEL,width:1.5}});
s.addText("Why it matters",{x:6.75,y:4.4,w:5.9,h:0.35,fontFace:HF,fontSize:15,color:"8A6D1B",bold:true,margin:0});
s.addText([
 {text:"Energy is the controllable, margin-bearing charge — fuel & IPP are pass-throughs.",options:{bullet:{code:"2022",color:"B8860B"},breakLine:true,color:"5A4A1E"}},
 {text:"Volume grew but the energy charge didn't follow — a rating/billing or estimation gap, not demand.",options:{bullet:{code:"2022",color:"B8860B"},breakLine:true,color:"5A4A1E"}},
 {text:"This is the real driver behind the revenue-vs-volume divergence flagged earlier.",options:{bullet:{code:"2022",color:"B8860B"},color:"5A4A1E"}}
],{x:6.75,y:4.8,w:5.9,h:1.7,fontFace:BF,fontSize:11.5,lineSpacingMultiple:1.03,paraSpaceAfter:6,margin:0});
footer(s);

// ===== 3 COMPONENTS MoM =====
s=pres.addSlide(); header(s,"02 · By component","Fuel & IPP tracked volume — energy & customer charge didn't");
s.addChart(pres.charts.BAR,[{name:"MoM %",labels:comps.map(c=>c[0]),values:comps.map(c=>+pct(C(c[0]).may,C(c[0]).apr).toFixed(1))}],
 cbase({x:0.4,y:1.65,w:8.6,h:4.8,barDir:"col",chartColors:comps.map(c=>c[1]),
  showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:11,dataLabelColor:INK,dataLabelFormatCode:'0.0"%"',
  valAxisMinVal:-25,valAxisMaxVal:35,valAxisMajorUnit:10,valAxisLabelFormatCode:'0"%"'}));
// volume reference line via a thin shape + label
s.addText("Volume grew +"+f1(volMoM)+"% — the bar to beat. Fuel (+"+f1(pct(C('Fuel').may,C('Fuel').apr))+"%) and IPP (+"+f1(pct(C('IPP').may,C('IPP').apr))+"%) kept pace; Energy ("+sgn(pct(C('Energy').may,C('Energy').apr))+"%) and Customer charge ("+sgn(pct(C('Customer charge').may,C('Customer charge').apr))+"%) went the other way.",
 {x:0.4,y:6.52,w:8.7,h:0.4,fontFace:BF,fontSize:10,italic:true,color:MUT,margin:0});
s.addShape(pres.shapes.RECTANGLE,{x:9.3,y:1.65,w:3.5,h:5.1,fill:{color:CARD},line:{color:LINEC,width:1},shadow:sh()});
s.addText("US$'000 · May vs Apr",{x:9.5,y:1.8,w:3.15,h:0.3,fontFace:HF,fontSize:13,color:INK,bold:true,margin:0});
let yy=2.25; comps.concat([['Total','14202E']]).forEach(c=>{const k=c[0]=='Total'?'None':c[0]; const d=C(k);
 s.addShape(pres.shapes.RECTANGLE,{x:9.5,y:yy,w:0.16,h:0.16,fill:{color:c[0]=='Total'?DARK:c[1]}});
 s.addText(c[0],{x:9.74,y:yy-0.06,w:1.55,h:0.3,fontFace:BF,fontSize:10.5,color:INK,bold:c[0]=='Total',margin:0});
 s.addText(f0(d.apr)+" → "+f0(d.may),{x:11.0,y:yy-0.06,w:1.7,h:0.3,fontFace:BF,fontSize:10.5,color:INK,bold:c[0]=='Total',align:"right",margin:0});
 yy+=0.72;});
footer(s);

// ===== 4 UNIT ECONOMICS =====
s=pres.addSlide(); header(s,"03 · Unit economics","US¢/kWh: fuel held, non-fuel collapsed");
s.addChart(pres.charts.BAR,[
 {name:"Apr-26",labels:["Non-fuel","Fuel","Total"],values:[+nf.apr.toFixed(1),+fu.apr.toFixed(1),+tt.apr.toFixed(1)]},
 {name:"May-26",labels:["Non-fuel","Fuel","Total"],values:[+nf.may.toFixed(1),+fu.may.toFixed(1),+tt.may.toFixed(1)]},
 {name:"Budget",labels:["Non-fuel","Fuel","Total"],values:[+nf.bud.toFixed(1),+fu.bud.toFixed(1),+tt.bud.toFixed(1)]}
],cbase({x:0.4,y:1.65,w:8.5,h:5.1,barDir:"col",chartColors:["B9C6D6",BLU,"FFD980"],showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:11,
 showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:9.5,dataLabelColor:INK,dataLabelFormatCode:"0.0",valAxisHidden:true,valAxisMaxVal:40}));
s.addShape(pres.shapes.RECTANGLE,{x:9.15,y:1.65,w:3.65,h:5.1,fill:{color:DARK}});
s.addText("US¢/kWh realization",{x:9.35,y:1.8,w:3.3,h:0.35,fontFace:HF,fontSize:14,color:YEL,bold:true,margin:0});
s.addText([
 {text:"Fuel held: "+f1(fu.apr)+" → "+f1(fu.may)+" ("+sgn(pct(fu.may,fu.apr))+"%), and +"+f1(pct(fu.may,fu.bud))+"% vs budget.",options:{color:"DCE6F0",bullet:{code:"2022",color:POS},breakLine:true}},
 {text:"Non-fuel fell: "+f1(nf.apr)+" → "+f1(nf.may)+" ("+sgn(pct(nf.may,nf.apr))+"%), and −"+f1(-pct(nf.may,nf.bud))+"% vs budget.",options:{color:"DCE6F0",bullet:{code:"2022",color:NEG},breakLine:true}},
 {text:"Total "+f1(tt.may)+"¢ ("+sgn(pct(tt.may,tt.apr))+"% MoM) — the whole decline is the non-fuel charge.",options:{color:"DCE6F0",bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:"Billing FX flat ("+f1(fx.apr)+"→"+f1(fx.may)+") — not a currency effect.",options:{color:"FFE9A8",bold:true,bullet:{code:"2022",color:YEL}}}
],{x:9.35,y:2.25,w:3.3,h:4.4,fontFace:BF,fontSize:10.5,lineSpacingMultiple:1.04,paraSpaceAfter:9,margin:0});
footer(s);

// ===== 5 vs BUDGET =====
s=pres.addSlide(); header(s,"04 · Versus budget","Volume beat plan — but non-fuel realization missed by "+f1(-pct(nf.may,nf.bud))+"%");
s.addText("Component revenue vs budget (US$'000)",{x:0.5,y:1.5,w:8,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[
 {name:"Budget",labels:comps.map(c=>c[0]),values:comps.map(c=>+(C(c[0]).bud).toFixed(0))},
 {name:"Actual",labels:comps.map(c=>c[0]),values:comps.map(c=>+(C(c[0]).may).toFixed(0))}
],cbase({x:0.4,y:1.85,w:8.5,h:4.85,barDir:"col",chartColors:["C9D3DE",BLU],showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:11,
 showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:8.5,dataLabelColor:INK,valAxisHidden:true}));
s.addShape(pres.shapes.RECTANGLE,{x:9.15,y:1.85,w:3.65,h:4.85,fill:{color:CARD},line:{color:LINEC,width:1},shadow:sh()});
s.addText("vs budget",{x:9.35,y:2.0,w:3.3,h:0.35,fontFace:HF,fontSize:14,color:INK,bold:true,margin:0});
s.addText([
 {text:"Volume +"+f1(volVB)+"% and total revenue +"+f1(totVB)+"% vs plan — but driven by fuel & volume, not energy.",options:{bullet:{code:"2022",color:MUT},breakLine:true,color:INK}},
 {text:"Fuel +"+f1(pct(C('Fuel').may,C('Fuel').bud))+"% (pass-through), IPP "+sgn(pct(C('IPP').may,C('IPP').bud))+"%.",options:{bullet:{code:"2022",color:POS},breakLine:true,color:INK}},
 {text:"Energy "+sgn(pct(C('Energy').may,C('Energy').bud))+"% and Customer charge "+sgn(pct(C('Customer charge').may,C('Customer charge').bud))+"% — short despite higher volume.",options:{bullet:{code:"2022",color:NEG},breakLine:true,color:INK}},
 {text:"Non-fuel realization −"+f1(-pct(nf.may,nf.bud))+"% vs budget is the headline miss.",options:{bullet:{code:"2022",color:NEG},bold:true,color:INK}}
],{x:9.35,y:2.45,w:3.3,h:4.2,fontFace:BF,fontSize:10.5,lineSpacingMultiple:1.03,paraSpaceAfter:8,margin:0});
footer(s);

// ===== 6 BY RATE CLASS =====
s=pres.addSlide(); header(s,"05 · By rate class","US$ revenue — May vs April, budget & prior year");
s.addChart(pres.charts.BAR,[
 {name:"Apr-26",labels:RC.map(r=>r.replace("Rate","R")),values:RC.map(r=>+(D.rc[r].apr).toFixed(0))},
 {name:"May-26",labels:RC.map(r=>r.replace("Rate","R")),values:RC.map(r=>+(D.rc[r].may).toFixed(0))},
 {name:"Budget",labels:RC.map(r=>r.replace("Rate","R")),values:RC.map(r=>+(D.rc[r].bud).toFixed(0))}
],cbase({x:0.4,y:1.6,w:8.6,h:5.15,barDir:"col",chartColors:["B9C6D6",BLU,"FFD980"],showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:11,
 showValue:false,valAxisHidden:false,valAxisLabelFontSize:8,catAxisLabelFontSize:11}));
s.addShape(pres.shapes.RECTANGLE,{x:9.25,y:1.6,w:3.55,h:5.15,fill:{color:CARD},line:{color:LINEC,width:1},shadow:sh()});
s.addText("Class notes (US$)",{x:9.45,y:1.75,w:3.2,h:0.35,fontFace:HF,fontSize:14,color:INK,bold:true,margin:0});
s.addText([
 {text:"R10 & R20 (mass market) up strongly MoM and ahead of budget — they carry the volume.",options:{bullet:{code:"2022",color:POS},breakLine:true,color:INK}},
 {text:"R40 & R50 below budget ("+sgn(pct(D.rc['Rate 40'].may,D.rc['Rate 40'].bud))+"%, "+sgn(pct(D.rc['Rate 50'].may,D.rc['Rate 50'].bud))+"%) — large-customer softness.",options:{bullet:{code:"2022",color:NEG},breakLine:true,color:INK}},
 {text:"R60 streetlight "+sgn(pct(D.rc['Rate 60'].may,D.rc['Rate 60'].pyr))+"% YoY — the persistent billing gap.",options:{bullet:{code:"2022",color:NEG},breakLine:true,color:INK}},
 {text:"R70 +"+f1(pct(D.rc['Rate 70'].may,D.rc['Rate 70'].pyr))+"% YoY — the lone grower.",options:{bullet:{code:"2022",color:POS},color:INK}}
],{x:9.45,y:2.2,w:3.2,h:4.5,fontFace:BF,fontSize:10.5,lineSpacingMultiple:1.03,paraSpaceAfter:8,margin:0});
footer(s);

// ===== 7 WHAT IT MEANS =====
s=pres.addSlide(); header(s,"06 · What it means","Reconciling the picture");
const cards=[
 ["It's non-fuel energy, not fuel",NEG,"The MoM revenue lag is the non-fuel energy charge (−8.9% ¢/kWh, US$"+f1(-enShort/1000)+"M short vs volume). Fuel ¢/kWh actually rose +"+f1(pct(fu.may,fu.apr))+"%."],
 ["Not FX",BLU,"Billing FX was flat ("+f1(fx.apr)+"→"+f1(fx.may)+", "+f1(pct(fx.may,fx.apr))+"%). Currency is not behind the gap."],
 ["Reconciles the JMD bridge",BLU,"The earlier JMD 'fuel/rate −J$769M' term is really this: a non-fuel energy under-realization. Fuel & FX were red herrings; the energy charge per kWh is the lever."],
 ["Most likely cause",NEG,"Volume billed without the matching energy charge points to estimated/unbilled reads, a rating-engine issue, or a true-up — an operational billing question, not demand or tariff."]];
cards.forEach((c,i)=>{const col=i%2,row=Math.floor(i/2);const x=0.5+col*6.25,y=1.6+row*2.5;
 s.addShape(pres.shapes.RECTANGLE,{x,y,w:5.95,h:2.3,fill:{color:CARD},line:{color:LINEC,width:1},shadow:sh()});
 s.addShape(pres.shapes.RECTANGLE,{x,y,w:0.09,h:2.3,fill:{color:c[1]}});
 s.addText(c[0],{x:x+0.25,y:y+0.18,w:5.5,h:0.5,fontFace:HF,fontSize:15.5,color:INK,bold:true,margin:0});
 s.addText(c[2],{x:x+0.25,y:y+0.72,w:5.55,h:1.45,fontFace:BF,fontSize:11.5,color:INK,lineSpacingMultiple:1.05,margin:0});});
footer(s);

// ===== 8 RECOMMENDATIONS =====
s=pres.addSlide(); s.background={color:DARK};
s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:0.22,h:Ht,fill:{color:YEL}});
s.addText("NEXT STEPS",{x:0.9,y:0.7,w:11,h:0.4,fontFace:BF,fontSize:13,color:YEL,bold:true,charSpacing:3,margin:0});
s.addText("Chase the energy charge",{x:0.9,y:1.1,w:11,h:0.7,fontFace:HF,fontSize:32,color:"FFFFFF",bold:true,margin:0});
const recs=[
 ["1","Find the US$"+f1(-enShort/1000)+"M","Energy revenue is ~US$"+f1(-enShort/1000)+"M below what May volume implies. Pull the energy-charge billing detail and isolate estimated/unbilled reads, rating errors, or a prior-period true-up."],
 ["2","Split non-fuel realization","Non-fuel ¢/kWh fell "+f1(-pct(nf.may,nf.apr))+"% MoM and "+f1(-pct(nf.may,nf.bud))+"% vs budget. Decompose into energy vs customer-charge vs mix to size each."],
 ["3","Retire the fuel/FX hypothesis","Fuel ¢/kWh +"+f1(pct(fu.may,fu.apr))+"% and FX flat — neither explains the gap. Re-point the earlier JMD bridge's 'fuel/rate' term at non-fuel energy."],
 ["4","Reconcile volume basis","This view shows "+f0(mwh.may)+" MWh vs the billing pivot's ~281k. Tie the two volume bases so billed kWh = energy-charged kWh."],
 ["5","Watch R40/R50 vs budget","Large-power classes are "+sgn(pct(D.rc['Rate 40'].may,D.rc['Rate 40'].bud))+"% / "+sgn(pct(D.rc['Rate 50'].may,D.rc['Rate 50'].bud))+"% under plan — confirm it's volume, not unbilled energy."]];
recs.forEach((r,i)=>{const y=2.0+i*0.98;
 s.addShape(pres.shapes.OVAL,{x:0.95,y,w:0.6,h:0.6,fill:{color:YEL}});
 s.addText(r[0],{x:0.95,y,w:0.6,h:0.6,fontFace:HF,fontSize:22,color:DARK,bold:true,align:"center",valign:"middle",margin:0});
 s.addText([{text:r[1]+"   ",options:{bold:true,color:YEL,fontSize:15}},{text:r[2],options:{color:"D7E1EC",fontSize:12}}],
  {x:1.75,y:y-0.05,w:10.6,h:0.92,fontFace:BF,valign:"middle",lineSpacingMultiple:1.0,margin:0});});
s.addText("JPS · revenue analysis (US$'000) · May 2026 · billing FX ≈ "+f1(fx.may),{x:0.9,y:7.0,w:11.5,h:0.3,fontFace:BF,fontSize:10,color:"7E91A5",margin:0});

pres.writeFile({fileName:"D:\\Projects\\Sales_Platform\\analysis\\JPS_May2026_Revenue_Quality_USD.pptx"}).then(f=>console.log("WROTE",f));
