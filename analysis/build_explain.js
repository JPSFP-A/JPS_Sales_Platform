// JPS May-2026 — meter-level explanation of volume vs revenue. Source: Billing Details Report (Apr & May).
const pptxgen=require("pptxgenjs");
const D=require("./tariff_app_data.json");
const f1=v=>v.toLocaleString("en-US",{maximumFractionDigits:1,minimumFractionDigits:1});
const f2=v=>v.toLocaleString("en-US",{maximumFractionDigits:2,minimumFractionDigits:2});
const f0=v=>Math.round(v).toLocaleString("en-US");
const sgn=v=>(v>=0?"+":"")+f1(v);
const pc=(a,b)=>(a/b-1)*100;
const T=D.total, RC=['RT10','RT20','RT40','RT50','RT60','RT70'];
const RN={RT10:"RT10 Residential",RT20:"RT20 Gen Svc",RT40:"RT40 Power",RT50:"RT50 Lg Power",RT60:"RT60 Streetlt",RT70:"RT70 Standby"};
// component MoM (total $)
const comp=[['Volume (kWh)',pc(T.may.kwh,T.apr.kwh)],['Energy chg',pc(T.may.energy_m,T.apr.energy_m)],
 ['Fuel',pc(T.may.fuel_m,T.apr.fuel_m)],['IPP',pc(T.may.ipp_m,T.apr.ipp_m)],
 ['Demand (kVA)',pc(T.may.demand_m,T.apr.demand_m)],['Cust chg',pc(T.may.cc_m,T.apr.cc_m)]];
const cA=D.carib.apr,cM=D.carib.may;

const DARK="14202E",DARK2="1E2D40",YEL="FFC60B",LIGHT="F6F8FB",CARD="FFFFFF",
 INK="1B2A3A",MUT="6B7C8F",POS="1F9D8B",NEG="D9534F",BLU="3B6EA5",LINEC="E2E8F0";
const HF="Georgia",BF="Calibri";
const MV=require("./movers_deck.json");
const AD=require("./anchors_deck.json");
const Y=require("./yoy_verify.json"); const yI={}; Y.leg.forEach((n,i)=>yI[n]=i);
const yd=k=>(Y.T26[yI[k]]-Y.T25[yI[k]])/1e6;            // J$M delta YoY
const yyo=k=>(Y.T26[yI[k]]/Y.T25[yI[k]]-1)*100;
const ykwh=yyo('net_kwh'), yrev=yyo('net_rev');
const yDemTot=yyo('demand'), yDemPerKwh=((Y.T26[yI['demand']]/Y.T26[yI['net_kwh']])/(Y.T25[yI['demand']]/Y.T25[yI['net_kwh']])-1)*100;
const yClsDem=r=>(Y.G26[r][yI['demand']]/Y.G25[r][yI['demand']]-1)*100;
const yClsKwh=r=>(Y.G26[r][yI['net_kwh']]/Y.G25[r][yI['net_kwh']]-1)*100;
const netD=(Y.T26[yI['net_rev']]-Y.T25[yI['net_rev']])/1e6;
const otherD=netD-(yd('fuel')+yd('energy')+yd('demand')+yd('ipp')+yd('cust_chg'));
const marginD=yd('energy')+yd('demand')+yd('cust_chg');
const pres=new pptxgen(); pres.layout="LAYOUT_WIDE"; const W=13.3,Ht=7.5;
pres.title="JPS May 2026 Revenue Explained";
const sh=()=>({type:"outer",color:"000000",blur:7,offset:3,angle:135,opacity:0.16});
let PGN=1;
function footer(s){PGN++; s.addShape(pres.shapes.RECTANGLE,{x:0,y:Ht-0.32,w:W,h:0.32,fill:{color:DARK}});
 s.addText("JPS · Billing Details Report (meter-level), April & May 2026 · 723k meters · J$ unless noted",
 {x:0.4,y:Ht-0.32,w:11,h:0.32,fontFace:BF,fontSize:8,color:"9FB0C2",valign:"middle",margin:0});
 s.addText(String(PGN),{x:W-0.8,y:Ht-0.32,w:0.4,h:0.32,fontFace:BF,fontSize:9,color:"9FB0C2",align:"right",valign:"middle",margin:0});}
function header(s,kick,title){s.background={color:LIGHT};
 s.addText(kick.toUpperCase(),{x:0.5,y:0.32,w:11,h:0.3,fontFace:BF,fontSize:11,color:BLU,bold:true,charSpacing:3,margin:0});
 s.addText(title,{x:0.5,y:0.6,w:12.3,h:0.65,fontFace:HF,fontSize:25,color:INK,bold:true,margin:0});
 s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.26,w:0.9,h:0.06,fill:{color:YEL}});}
function cbase(e){return Object.assign({chartArea:{fill:{color:CARD}},plotArea:{fill:{color:CARD}},
 catAxisLabelColor:MUT,valAxisLabelColor:MUT,catAxisLabelFontFace:BF,valAxisLabelFontFace:BF,
 catAxisLabelFontSize:10,valAxisLabelFontSize:9,valGridLine:{color:LINEC,size:0.5},catGridLine:{style:"none"},showLegend:false},e);}

// 1 TITLE
let s=pres.addSlide(); s.background={color:DARK};
s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:W,h:0.18,fill:{color:YEL}});
s.addShape(pres.shapes.RECTANGLE,{x:0,y:Ht-0.18,w:W,h:0.18,fill:{color:YEL}});
s.addText("JPS · FP&A · REVENUE DIAGNOSIS",{x:0.9,y:1.4,w:11,h:0.4,fontFace:BF,fontSize:14,color:YEL,bold:true,charSpacing:3,margin:0});
s.addText("Volume vs revenue — the meter-level answer",{x:0.9,y:2.0,w:11.8,h:1.0,fontFace:HF,fontSize:37,color:"FFFFFF",bold:true,margin:0});
s.addText("723,000 meters, April vs May 2026 — billed revenue actually kept pace with volume; only the fixed demand charge lagged",{x:0.9,y:3.05,w:12,h:0.7,fontFace:BF,fontSize:15,color:"C7D3E0",margin:0});
const strip=[["Volume (MoM)",sgn(D.momKwh)+"%","kWh"],["Revenue (MoM)",sgn(D.momRev)+"%","billed"],
 ["Demand chg (MoM)",sgn(comp[4][1])+"%","fixed → lagged"],["Unit tariff (MoM)",sgn(pc(T.may.total,T.apr.total))+"%","J$/kWh"]];
strip.forEach((c,i)=>{const x=0.9+i*2.95;
 s.addShape(pres.shapes.RECTANGLE,{x,y:4.35,w:2.7,h:1.5,fill:{color:DARK2},line:{color:"2C4258",width:1}});
 s.addShape(pres.shapes.RECTANGLE,{x,y:4.35,w:0.07,h:1.5,fill:{color:YEL}});
 s.addText(c[0].toUpperCase(),{x:x+0.2,y:4.5,w:2.4,h:0.3,fontFace:BF,fontSize:9.5,color:"9FB0C2",bold:true,charSpacing:1,margin:0});
 s.addText(c[1],{x:x+0.2,y:4.82,w:2.45,h:0.55,fontFace:HF,fontSize:22,color:(c[1].startsWith("+")?"6FE0C8":"FF8A80"),bold:true,margin:0});
 s.addText(c[2],{x:x+0.2,y:5.42,w:2.4,h:0.3,fontFace:BF,fontSize:10.5,color:"C7D3E0",margin:0});});
s.addText("Prepared "+new Date().toISOString().slice(0,10),{x:0.9,y:6.55,w:11,h:0.3,fontFace:BF,fontSize:11,color:"7E91A5",margin:0});

// 2 THE ANSWER
s=pres.addSlide(); header(s,"01 · The answer","At the meter level, revenue did keep pace with volume");
s.addChart(pres.charts.BAR,[{name:"MoM %",labels:["Volume\n(kWh)","Billed\nrevenue"],values:[+D.momKwh.toFixed(1),+D.momRev.toFixed(1)]}],
 cbase({x:0.5,y:1.7,w:5.3,h:4.9,barDir:"col",chartColors:[BLU],showValue:true,dataLabelPosition:"outEnd",
  dataLabelFontFace:BF,dataLabelFontSize:18,dataLabelColor:INK,dataLabelFormatCode:'0.0"%"',valAxisHidden:true,valAxisMaxVal:20,barGapWidthPct:90,catAxisLabelFontSize:12}));
s.addShape(pres.shapes.RECTANGLE,{x:6.2,y:1.7,w:6.6,h:2.3,fill:{color:"E6F4F1"},line:{color:POS,width:1.4}});
s.addText("Revenue grew faster than volume",{x:6.45,y:1.88,w:6.1,h:0.4,fontFace:HF,fontSize:16,color:"15715F",bold:true,margin:0});
s.addText([
 {text:"May billed revenue +"+f1(D.momRev)+"% on volume +"+f1(D.momKwh)+"% — there is no revenue-lagging-volume problem in the billing.",options:{color:"1B5A4C",bullet:{code:"2022",color:POS},breakLine:true}},
 {text:"Unit tariff rose +"+f1(pc(T.may.total,T.apr.total))+"% (J$"+f2(T.apr.total)+"→"+f2(T.may.total)+"/kWh): both fuel and non-fuel up ~3%.",options:{color:"1B5A4C",bullet:{code:"2022",color:POS}}}
],{x:6.45,y:2.35,w:6.1,h:1.55,fontFace:BF,fontSize:12.5,lineSpacingMultiple:1.05,paraSpaceAfter:7,margin:0});
s.addShape(pres.shapes.RECTANGLE,{x:6.2,y:4.2,w:6.6,h:2.4,fill:{color:"FBEFD0"},line:{color:YEL,width:1.4}});
s.addText("So where did “revenue down” come from?",{x:6.45,y:4.36,w:6.1,h:0.4,fontFace:HF,fontSize:15,color:"8A6D1B",bold:true,margin:0});
s.addText([
 {text:"The decline is year-on-year (May-26 vs May-25): kWh +2.5% but net revenue −3.1% — a realization (¢/kWh) effect, not lost sales.",options:{color:"5A4A1E",bullet:{code:"2022",color:NEG},breakLine:true}},
 {text:"And the USD management pivot's “energy −2.9%” is a reporting artifact (next slides) — it bundles the fixed demand charge into “Energy.”",options:{color:"5A4A1E",bullet:{code:"2022",color:NEG}}}
],{x:6.45,y:4.78,w:6.1,h:1.7,fontFace:BF,fontSize:11.5,lineSpacingMultiple:1.04,paraSpaceAfter:7,margin:0});
footer(s);

// 3 COMPONENTS
s=pres.addSlide(); header(s,"02 · By charge component","Energy & fuel tracked volume — only demand stayed flat");
s.addChart(pres.charts.BAR,[{name:"MoM %",labels:comp.map(c=>c[0]),values:comp.map(c=>+c[1].toFixed(1))}],
 cbase({x:0.4,y:1.65,w:8.6,h:5.1,barDir:"col",chartColors:comp.map(c=>c[0].startsWith('Demand')?NEG:(c[0].startsWith('Volume')?"9AA7B4":BLU)),
  showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:11,dataLabelColor:INK,dataLabelFormatCode:'0.0"%"',
  valAxisMinVal:-2,valAxisMaxVal:38,valAxisLabelFormatCode:'0"%"'}));
s.addShape(pres.shapes.RECTANGLE,{x:9.3,y:1.65,w:3.5,h:5.1,fill:{color:CARD},line:{color:LINEC,width:1},shadow:sh()});
s.addText("Read",{x:9.5,y:1.8,w:3.15,h:0.35,fontFace:HF,fontSize:14,color:INK,bold:true,margin:0});
s.addText([
 {text:"Energy charge +"+f1(comp[1][1])+"% and fuel +"+f1(comp[2][1])+"% — both moved with volume (+"+f1(D.momKwh)+"%).",options:{bullet:{code:"2022",color:POS},breakLine:true,color:INK}},
 {text:"IPP +"+f1(comp[3][1])+"% (pass-through, ran ahead).",options:{bullet:{code:"2022",color:MUT},breakLine:true,color:INK}},
 {text:"Demand (kVA) only +"+f1(comp[4][1])+"% — it is a fixed capacity charge that does NOT scale with kWh.",options:{bullet:{code:"2022",color:NEG},breakLine:true,color:INK,bold:true}},
 {text:"That single flat component is the whole “volume up, realization down” story.",options:{bullet:{code:"2022",color:YEL},color:INK}}
],{x:9.5,y:2.25,w:3.15,h:4.4,fontFace:BF,fontSize:11,lineSpacingMultiple:1.03,paraSpaceAfter:9,margin:0});
footer(s);

// 4 DEMAND DILUTION
s=pres.addSlide(); header(s,"03 · The mechanism","Demand is a big, fixed slice of industrial bills");
s.addText("Demand charge as % of class revenue (May)",{x:0.5,y:1.5,w:8,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[{name:"demand % of rev",labels:RC.map(r=>r),values:RC.map(r=>+D.byClass[r].may.dem_share.toFixed(1))}],
 cbase({x:0.4,y:1.85,w:8.5,h:4.85,barDir:"col",chartColors:RC.map(r=>['RT40','RT50','RT70'].includes(r)?NEG:"C9D3DE"),
  showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:11,dataLabelColor:INK,dataLabelFormatCode:'0.0"%"',
  valAxisMaxVal:26,valAxisLabelFormatCode:'0"%"'}));
s.addShape(pres.shapes.RECTANGLE,{x:9.15,y:1.85,w:3.65,h:4.85,fill:{color:DARK}});
s.addText("Why it dilutes ¢/kWh",{x:9.35,y:2.0,w:3.3,h:0.35,fontFace:HF,fontSize:14,color:YEL,bold:true,margin:0});
s.addText([
 {text:"Demand is ~18–22% of RT40/50/70 bills — and it's billed on peak kVA, not kWh.",options:{color:"DCE6F0",bullet:{code:"2022",color:NEG},breakLine:true}},
 {text:"When an industrial plant runs more kWh at the same peak, demand revenue is unchanged → blended J$/kWh falls.",options:{color:"DCE6F0",bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:"Total demand share fell "+f1(T.apr.dem_share)+"% → "+f1(T.may.dem_share)+"% as volume grew — exactly this effect.",options:{color:"DCE6F0",bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:"Residential (RT10/20) has no demand charge — so the dilution is an industrial-load story.",options:{color:"DCE6F0",bullet:{code:"2022",color:MUT}}}
],{x:9.35,y:2.45,w:3.3,h:4.2,fontFace:BF,fontSize:10.5,lineSpacingMultiple:1.03,paraSpaceAfter:8,margin:0});
footer(s);

// 4b YoY PROOF
s=pres.addSlide(); header(s,"04 · Year-on-year proof","Volume +"+f1(ykwh)+"%, revenue "+sgn(yrev)+"% — demand actually fell");
const dd=[['Fuel',yd('fuel')],['Energy',yd('energy')],['Other/adj',otherD],['Cust chg',yd('cust_chg')],['Demand',yd('demand')],['IPP',yd('ipp')]];
s.addText("YoY revenue change by charge component (May-25 → May-26, J$M)",{x:0.5,y:1.5,w:8.5,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[{name:"ΔJ$M",labels:dd.map(d=>d[0]),values:dd.map(d=>Math.round(d[1]))}],
 cbase({x:0.4,y:1.85,w:8.5,h:4.85,barDir:"bar",chartColors:[BLU],
  showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:11,dataLabelColor:INK,dataLabelFormatCode:'+#,##0;\\-#,##0',
  valAxisHidden:true,valAxisMinVal:-850,valAxisMaxVal:420,catAxisLabelColor:INK,catAxisLabelFontSize:11,barGapWidthPct:45}));
s.addShape(pres.shapes.RECTANGLE,{x:9.15,y:1.85,w:3.65,h:4.85,fill:{color:DARK}});
s.addText("Demand assumption: confirmed",{x:9.35,y:2.0,w:3.3,h:0.4,fontFace:HF,fontSize:14,color:YEL,bold:true,margin:0});
s.addText([
 {text:"Demand "+sgn(yDemTot)+"% YoY while volume +"+f1(ykwh)+"% — it fell as kWh rose. Demand/kWh "+sgn(yDemPerKwh)+"%.",options:{color:"DCE6F0",bullet:{code:"2022",color:NEG},breakLine:true}},
 {text:"Every industrial class: RT40 dem "+sgn(yClsDem('RT40'))+"%, RT50 "+sgn(yClsDem('RT50'))+"% (kWh +"+f1(yClsKwh('RT50'))+"%), RT70 "+sgn(yClsDem('RT70'))+"% (kWh +"+f1(yClsKwh('RT70'))+"%).",options:{color:"DCE6F0",bullet:{code:"2022",color:NEG},breakLine:true}},
 {text:"Biggest mover is IPP −J$"+f0(-yd('ipp'))+"M — a pass-through (margin-neutral).",options:{color:"DCE6F0",bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:"Strip pass-throughs: margin-bearing revenue (energy+demand+cust) only "+sgn(marginD)+"M. The “−3.1%” is mostly pass-through, not lost margin.",options:{color:"FFE9A8",bold:true,bullet:{code:"2022",color:YEL}}}
],{x:9.35,y:2.5,w:3.3,h:4.1,fontFace:BF,fontSize:10,lineSpacingMultiple:1.03,paraSpaceAfter:7,margin:0});
footer(s);

// 5 CARIB CEMENT
s=pres.addSlide(); header(s,"05 · Case study","Caribbean Cement: the dilution in one account");
const ccRows=[["",  "April","May","Δ"],
 ["kWh", f1(cA.kwh/1e6)+"M", f1(cM.kwh/1e6)+"M", sgn(pc(cM.kwh,cA.kwh))+"%"],
 ["Revenue","J$"+f1(cA.rev/1e6)+"M","J$"+f1(cM.rev/1e6)+"M",sgn(pc(cM.rev,cA.rev))+"%"],
 ["Energy chg","J$"+f1(cA.energy/1e6)+"M","J$"+f1(cM.energy/1e6)+"M",sgn(pc(cM.energy,cA.energy))+"%"],
 ["Demand (kVA)","J$"+f1(cA.demand/1e6)+"M","J$"+f1(cM.demand/1e6)+"M",sgn(pc(cM.demand,cA.demand))+"%"],
 ["Fuel","J$"+f1(cA.fuel/1e6)+"M","J$"+f1(cM.fuel/1e6)+"M",sgn(pc(cM.fuel,cA.fuel))+"%"]];
s.addTable(ccRows.map((r,ri)=>r.map((c,ci)=>{
  const head=ri==0, lab=ci==0;
  const hl=(!head&&ci==3&&(r[0]==='kWh'||r[0]==='Revenue'));      // highlight the key contrast rows
  let col=head?"FFFFFF":(hl?(r[0]==='kWh'?BLU:"B5651D"):INK);
  return {text:c,options:{fill:{color:head?DARK:(ri%2?"FFFFFF":"F1F5F9")},color:col,
    bold:head||lab||ci==3,fontSize:13,align:lab?"left":"center",valign:"middle",fontFace:BF}};
})),{x:0.5,y:1.7,w:6.6,colW:[1.9,1.55,1.55,1.6],rowH:0.62,border:{type:"solid",pt:0.5,color:LINEC},margin:[3,5,3,5]});
s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:5.7,w:6.6,h:1.0,fill:{color:"FBEFD0"},line:{color:YEL,width:1.2}});
s.addText([{text:"Bill mix: ",options:{bold:true,color:"8A6D1B"}},{text:"~"+f0(cM.fuel/cM.rev*100)+"% fuel · ~"+f0(cM.demand/cM.rev*100)+"% demand (flat) · ~"+f0(cM.energy/cM.rev*100)+"% energy. Production up, but the demand charge didn't move and the fuel rate fell — so revenue barely grew.",options:{color:"5A4A1E"}}],
 {x:0.7,y:5.82,w:6.25,h:0.8,fontFace:BF,fontSize:11,lineSpacingMultiple:1.0,valign:"middle",margin:0});
// bar: kwh vs rev index
s.addText("kWh vs revenue (April = 100)",{x:7.45,y:1.6,w:5,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[
 {name:"kWh",labels:["Apr","May"],values:[100,+(cM.kwh/cA.kwh*100).toFixed(1)]},
 {name:"Revenue",labels:["Apr","May"],values:[100,+(cM.rev/cA.rev*100).toFixed(1)]}
],cbase({x:7.35,y:1.95,w:5.45,h:4.75,barDir:"col",chartColors:[BLU,YEL],showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:11,
 showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:11,dataLabelColor:INK,dataLabelFormatCode:"0.0",valAxisHidden:true,valAxisMinVal:95,valAxisMaxVal:110}));
footer(s);

// 5b ANCHOR CASE STUDIES
const pcr=(x,y)=>Math.round((y/x-1)*100), sgp=v=>(v>=0?"+":"")+v+"%";
const A=AD.alcoa, Wd=AD.windalco, WO=AD.wow;
function caseSlide(kick,title,rows,callBold,callRest,idx){
  s=pres.addSlide(); header(s,kick,title);
  s.addTable(rows.map((r,ri)=>r.map((c,ci)=>{const head=ri==0,lab=ci==0;
    let col=head?"FFFFFF":(ci==3?(String(c).startsWith('-')?NEG:POS):INK);
    return {text:c,options:{fill:{color:head?DARK:(ri%2?"FFFFFF":"F1F5F9")},color:col,bold:head||lab||ci==3,fontSize:12.5,align:lab?"left":"center",valign:"middle",fontFace:BF}};
  })),{x:0.5,y:1.7,w:6.8,colW:[2.05,1.75,1.75,1.25],rowH:0.6,border:{type:"solid",pt:0.5,color:LINEC},margin:[3,5,3,5]});
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:5.5,w:6.8,h:1.2,fill:{color:"FBEFD0"},line:{color:YEL,width:1.2}});
  s.addText([{text:callBold,options:{bold:true,color:"8A6D1B"}},{text:callRest,options:{color:"5A4A1E"}}],
    {x:0.7,y:5.6,w:6.45,h:1.02,fontFace:BF,fontSize:10.5,lineSpacingMultiple:1.0,valign:"middle",margin:0});
  s.addText("Indexed to May-25 = 100",{x:7.6,y:1.6,w:5,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
  s.addChart(pres.charts.BAR,[
    {name:"May-25",labels:["kWh","Revenue","Demand"],values:[100,100,100]},
    {name:"May-26",labels:["kWh","Revenue","Demand"],values:idx}
  ],cbase({x:7.45,y:1.95,w:5.35,h:4.65,barDir:"col",chartColors:["B9C6D6",BLU],showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:10,
    showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:10.5,dataLabelColor:INK,dataLabelFormatCode:"0",valAxisHidden:true,valAxisMaxVal:165}));
  footer(s);
}
caseSlide("06 · Case study","Alcoa — demand cut, not lost volume (YoY)",
 [["Alcoa [RT70]","May-25","May-26","Δ"],
  ["kWh",A.k25+"M",A.k26+"M",sgp(pcr(A.k25,A.k26))],
  ["Revenue","J$"+A.r25+"M","J$"+A.r26+"M",sgp(pcr(A.r25,A.r26))],
  ["Billed demand",A.kva25.toLocaleString()+" kVA",A.kva26.toLocaleString()+" kVA",sgp(pcr(A.kva25,A.kva26))],
  ["Demand charge","J$"+A.d25+"M","J$"+A.d26+"M",sgp(pcr(A.d25,A.d26))],
  ["Demand / kWh","J$"+f2(A.dpk25),"J$"+f2(A.dpk26),sgp(pcr(A.dpk25,A.dpk26))]],
 "Demand cut, not a billing error: ",
 "Alcoa ran +"+pcr(A.k25,A.k26)+"% more energy but cut peak demand "+pcr(A.kva25,A.kva26)+"% (50,531→18,641 kVA) — so its demand charge halved and revenue grew only +"+pcr(A.r25,A.r26)+"%. This one account is −J$46M of the −J$102M industrial demand decline.",
 [pcr(A.k25,A.k26)+100,pcr(A.r25,A.r26)+100,pcr(A.d25,A.d26)+100]);
caseSlide("07 · Case study","Windalco — growth that kept its value (YoY)",
 [["Windalco [RT70]","May-25","May-26","Δ"],
  ["kWh",Wd.k25+"M",Wd.k26+"M",sgp(pcr(Wd.k25,Wd.k26))],
  ["Revenue","J$"+Wd.r25+"M","J$"+Wd.r26+"M",sgp(pcr(Wd.r25,Wd.r26))],
  ["Energy chg","J$"+Wd.en25+"M","J$"+Wd.en26+"M",sgp(pcr(Wd.en25,Wd.en26))],
  ["Demand chg","J$"+Wd.d25+"M","J$"+Wd.d26+"M",sgp(pcr(Wd.d25,Wd.d26))],
  ["Fuel","J$"+Wd.fu25+"M","J$"+Wd.fu26+"M",sgp(pcr(Wd.fu25,Wd.fu26))]],
 "The contrast: ",
 "Windalco grew volume +"+pcr(Wd.k25,Wd.k26)+"% AND held its demand up (+"+pcr(Wd.d25,Wd.d26)+"%) — so revenue tracked volume (+"+pcr(Wd.r25,Wd.r26)+"%). When demand keeps pace with kWh, there is no dilution.",
 [pcr(Wd.k25,Wd.k26)+100,pcr(Wd.r25,Wd.r26)+100,pcr(Wd.d25,Wd.d26)+100]);

// 5c WITH vs WITHOUT
s=pres.addSlide(); header(s,"08 · With vs without","The giants mask the real class trends (YoY revenue)");
s.addChart(pres.charts.BAR,[
 {name:"All accounts",labels:["RT40","RT50","RT70"],values:[WO.RT40.revW,WO.RT50.revW,WO.RT70.revW]},
 {name:"Excluding Carib / Alcoa / Windalco",labels:["RT40","RT50","RT70"],values:[WO.RT40.revX,WO.RT50.revX,WO.RT70.revX]}
],cbase({x:0.4,y:1.65,w:8.4,h:5.1,barDir:"col",chartColors:[BLU,"E2864B"],showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:11,
 showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:11,dataLabelColor:INK,dataLabelFormatCode:'0.0"%"',
 valAxisMinVal:-20,valAxisMaxVal:8,valAxisLabelFormatCode:'0"%"'}));
s.addShape(pres.shapes.RECTANGLE,{x:9.15,y:1.65,w:3.65,h:5.1,fill:{color:"FBEFD0"},line:{color:YEL,width:1.5}});
s.addText("Three accounts distort it",{x:9.35,y:1.8,w:3.3,h:0.35,fontFace:HF,fontSize:14,color:"8A6D1B",bold:true,margin:0});
s.addText([
 {text:"RT50 reads "+sgn(WO.RT50.revW)+"% — but ex-Carib Cement it's "+sgn(WO.RT50.revX)+"%. The cement restart masks broad weakness.",options:{color:"5A4A1E",bullet:{code:"2022",color:NEG},breakLine:true}},
 {text:"RT70 reads "+sgn(WO.RT70.revW)+"% — but ex-Alcoa/Windalco it's "+sgn(WO.RT70.revX)+"%.",options:{color:"5A4A1E",bullet:{code:"2022",color:NEG},breakLine:true}},
 {text:"Demand tells the same story: RT70 "+sgn(WO.RT70.demW)+"% vs "+sgn(WO.RT70.demX)+"% ex-Alcoa — the −J$46M is one meter.",options:{color:"5A4A1E",bullet:{code:"2022",color:NEG},breakLine:true}},
 {text:"256 of 1,013 industrial accounts diluted; total industrial demand −J$102M YoY.",options:{color:"5A4A1E",bold:true,bullet:{code:"2022",color:"B8860B"}}}
],{x:9.35,y:2.3,w:3.3,h:4.4,fontFace:BF,fontSize:11,lineSpacingMultiple:1.04,paraSpaceAfter:9,margin:0});
footer(s);

// 5c TOP/BOTTOM MOVERS
s=pres.addSlide(); header(s,"09 · Movers by class","Top & bottom 5 — by YoY revenue (May-25 → May-26)");
['RT40','RT50','RT70'].forEach((cls,ci)=>{const x=0.5+ci*4.27;const m=MV[cls];
  s.addShape(pres.shapes.RECTANGLE,{x,y:1.55,w:4.05,h:5.15,fill:{color:CARD},line:{color:LINEC,width:1},shadow:sh()});
  s.addText([{text:cls+"  ",options:{bold:true,fontSize:15,color:INK}},{text:"rev "+(m.dRev>=0?"+":"")+"J$"+m.dRev+"M",options:{fontSize:11,color:(m.dRev<0?NEG:POS)}}],
    {x:x+0.2,y:1.66,w:3.7,h:0.35,fontFace:HF,valign:"middle",margin:0});
  const mk=(arr,clr,hdr)=>{const runs=[{text:hdr+"\n",options:{bold:true,fontSize:10,color:MUT,charSpacing:1}}];
    arr.forEach(r=>{runs.push({text:r.name+"  ",options:{fontSize:10,color:INK,breakLine:false}});
      runs.push({text:(r.dRev>=0?"+":"")+r.dRev+"M\n",options:{fontSize:10,bold:true,color:clr}});});
    return runs;};
  s.addText(mk(m.top,POS,"TOP 5 GAINERS"),{x:x+0.2,y:2.12,w:3.7,h:2.2,fontFace:BF,lineSpacingMultiple:1.12,margin:0,valign:"top"});
  s.addText(mk(m.bot.slice().reverse(),NEG,"BOTTOM 5 LOSERS"),{x:x+0.2,y:4.45,w:3.7,h:2.2,fontFace:BF,lineSpacingMultiple:1.12,margin:0,valign:"top"});
});
s.addText("Reclassified accounts excluded. Δ = May-26 − May-25 net revenue (J$M). Full sortable list in the live app.",{x:0.5,y:6.78,w:12,h:0.25,fontFace:BF,fontSize:9,italic:true,color:MUT,margin:0});
footer(s);

// 6 TARIFF (non-fuel vs fuel by class)
s=pres.addSlide(); header(s,"10 · Average tariff","Non-fuel vs fuel J$/kWh — by rate class (May)");
s.addChart(pres.charts.BAR,[
 {name:"Non-fuel",labels:RC,values:RC.map(r=>+D.byClass[r].may.nonfuel.toFixed(1))},
 {name:"Fuel",labels:RC,values:RC.map(r=>+D.byClass[r].may.fuel.toFixed(1))}
],cbase({x:0.4,y:1.6,w:8.6,h:5.15,barDir:"col",barGrouping:"stacked",chartColors:[BLU,"9A4E1A"],
 showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:11,showValue:true,dataLabelFontFace:BF,dataLabelFontSize:10,dataLabelColor:"FFFFFF",dataLabelBold:true,dataLabelFormatCode:"0.0",
 valAxisTitle:"J$/kWh"}));
s.addShape(pres.shapes.RECTANGLE,{x:9.25,y:1.6,w:3.55,h:5.15,fill:{color:CARD},line:{color:LINEC,width:1},shadow:sh()});
s.addText("Tariff read",{x:9.45,y:1.75,w:3.2,h:0.35,fontFace:HF,fontSize:14,color:INK,bold:true,margin:0});
s.addText([
 {text:"Blended tariff J$"+f2(T.may.total)+"/kWh (non-fuel J$"+f2(T.may.nonfuel)+" + fuel J$"+f2(T.may.fuel)+").",options:{bullet:{code:"2022",color:YEL},breakLine:true,color:INK}},
 {text:"Both rose ~3% vs April — no tariff cut.",options:{bullet:{code:"2022",color:POS},breakLine:true,color:INK}},
 {text:"Industrial classes (RT40/50/70) carry a LOWER non-fuel tariff — their demand charge sits outside per-kWh, so heavy use bills cheap per kWh.",options:{bullet:{code:"2022",color:NEG},breakLine:true,color:INK}},
 {text:"Toggle the live app to flip non-fuel / fuel / trend.",options:{bullet:{code:"2022",color:MUT},italic:true,color:MUT}}
],{x:9.45,y:2.2,w:3.2,h:4.5,fontFace:BF,fontSize:10.5,lineSpacingMultiple:1.03,paraSpaceAfter:8,margin:0});
footer(s);

// 7 RECONCILE USD PIVOT
s=pres.addSlide(); header(s,"11 · Reconciling the USD pivot","Why the management report looked worse");
const cards=[
 ["“Energy” bundles demand",NEG,"In the USD pivot, the “Energy” line = energy charge + the fixed demand charge. Adding flat demand to growing energy makes the line grow slower than kWh — so it looks like energy isn't tracking volume. Unbundled, the true energy charge rose +"+f1(comp[1][1])+"%."],
 ["Different volume base",BLU,"The pivot shows ~291 GWh vs ~278 GWh actually billed (~5% higher). A bigger denominator pushes the reported ¢/kWh down. Reconcile system volume → billed kWh."],
 ["The real signal is YoY",BLU,"Month-on-month is healthy. The genuine softness is May-26 vs May-25: kWh +2.5%, revenue −3.1% — realization, driven by the same flat-demand + fuel/FX mix over a year."],
 ["Not lost revenue",POS,"Energy is on/ahead of budget YTD. Nothing is leaking — it's a mix/measurement effect concentrated in demand-billed industrial load."]];
cards.forEach((c,i)=>{const col=i%2,row=Math.floor(i/2);const x=0.5+col*6.25,y=1.6+row*2.5;
 s.addShape(pres.shapes.RECTANGLE,{x,y,w:5.95,h:2.3,fill:{color:CARD},line:{color:LINEC,width:1},shadow:sh()});
 s.addShape(pres.shapes.RECTANGLE,{x,y,w:0.09,h:2.3,fill:{color:c[1]}});
 s.addText(c[0],{x:x+0.25,y:y+0.16,w:5.5,h:0.45,fontFace:HF,fontSize:15,color:INK,bold:true,margin:0});
 s.addText(c[2],{x:x+0.25,y:y+0.66,w:5.55,h:1.5,fontFace:BF,fontSize:11,color:INK,lineSpacingMultiple:1.04,margin:0});});
footer(s);

// 8 RECOMMENDATIONS
s=pres.addSlide(); s.background={color:DARK};
s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:0.22,h:Ht,fill:{color:YEL}});
s.addText("TAKEAWAYS",{x:0.9,y:0.7,w:11,h:0.4,fontFace:BF,fontSize:13,color:YEL,bold:true,charSpacing:3,margin:0});
s.addText("What to do with this",{x:0.9,y:1.1,w:11,h:0.7,fontFace:HF,fontSize:32,color:"FFFFFF",bold:true,margin:0});
const recs=[
 ["1","Stop diagnosing off the USD pivot","Its “Energy” line bundles the fixed demand charge and its volume base is ~5% above billed kWh. Use the meter billing for revenue-quality analysis."],
 ["2","Report realization split by charge","Track non-fuel (energy + demand + customer) vs fuel J$/kWh, and demand's share, monthly. Demand dilution is the metric that explains “volume up, ¢/kWh down.”"],
 ["3","Watch the demand-heavy accounts","RT40/50/70 carry 18–22% demand. A handful — Carib Cement et al. — move blended realization. Monitor their kVA vs kWh."],
 ["4","Reconcile the volume bases","Close the ~291 GWh (report) vs ~278 GWh (billed) gap so the ¢/kWh denominator is consistent."],
 ["5","Frame YoY correctly","The −3.1% YoY is realization (mix + fuel/FX), not lost volume or customers — say so to avoid a false alarm."]];
recs.forEach((r,i)=>{const y=2.0+i*0.98;
 s.addShape(pres.shapes.OVAL,{x:0.95,y,w:0.6,h:0.6,fill:{color:YEL}});
 s.addText(r[0],{x:0.95,y,w:0.6,h:0.6,fontFace:HF,fontSize:22,color:DARK,bold:true,align:"center",valign:"middle",margin:0});
 s.addText([{text:r[1]+"   ",options:{bold:true,color:YEL,fontSize:15}},{text:r[2],options:{color:"D7E1EC",fontSize:12}}],
  {x:1.75,y:y-0.05,w:10.6,h:0.92,fontFace:BF,valign:"middle",lineSpacingMultiple:1.0,margin:0});});
s.addText("JPS · meter-level billing detail · April & May 2026 · J$ unless noted",{x:0.9,y:7.0,w:11.5,h:0.3,fontFace:BF,fontSize:10,color:"7E91A5",margin:0});

pres.writeFile({fileName:"D:\\Projects\\Sales_Platform\\analysis\\JPS_May2026_Revenue_Explained_v2.pptx"}).then(f=>console.log("WROTE",f));
