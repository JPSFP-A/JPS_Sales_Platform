// JPS Sales Platform — Sales vs Revenue analytics deck (YTD + May 2026)
// All figures sourced from Supabase bhrswnbenkvflpdjhfpa: jps_actuals + jps_budget.
const pptxgen = require("pptxgenjs");

// ---------- RAW DB DATA (do not alter — pulled live) ----------
// Monthly totals, all rate classes
const tot2025 = [
  [1,270794157.34,15092898050.57,719825],[2,263336983.97,14749358542.60,720627],
  [3,272435352.87,15595412259.90,721271],[4,265841291.46,14692045759.07,721490],
  [5,274069298.33,15739050635.65,722036],[6,289924663.98,16464616050.91,722882],
  [7,304836032.01,16390483404.37,724546],[8,307004889.62,16271631699.01,724341],
  [9,301714914.12,16671795156.30,725108],[10,289134382.35,16500205426.91,725686],
  [11,184757961.71,10723643104.60,723330],[12,227105142.09,13229716008.87,726070]];
const tot2026 = [
  [1,234149599.22,13531197187.01,726442],[2,221297131.36,13239907988.64,727246],
  [3,258718423.74,16361223821.90,728648],[4,250638549.58,13201617317.93,729884],
  [5,281134173.65,15260933832.90,730899]];
// Total kWh budget 2026 (m1-2 = actual copy; m3-5 genuine targets)
const budKwh2026 = [234149599.22,221297131.36,246508809.59,248952059.78,262492770.44];

// Rate class: [kwh, rev, cust] per month
const RC = {
  RT10:{n:"RT10 Residential",c:"FFC60B",
    y25:[[96433594,5791982674,644380],[90413823,5354768037,645024],[94150936,5768562471,645636],[93926781,5465087951,645808],[98392862,5894818472,646298],[104458032,6189449650,647142],[108175568,6152216946,648616],[113466911,6338213535,648371],[110279240,6330912948,649030],[105757381,6182599926,649432],[68847948,3892216349,647240],[73015878,4290836776,649785]],
    y26:[[84427346,5096896034,650168],[76489141,4615746701,650809],[88277732,5784519657,652071],[87175653,4729794343,653180],[99081407,5630756521,654088]],
    bud:[84427346,76489141,85621230,87181780,94113450]},
  RT20:{n:"RT20 Gen. Service",c:"3B6EA5",
    y25:[[49693721,3205117527,72839],[50244273,3239961138,72997],[52473379,3472900016,73026],[51767162,3255581926,73063],[53628536,3484011586,73121],[56957304,3724726599,73119],[58772343,3684537045,73292],[58706663,3570454479,73337],[58277527,3658151216,73449],[57703541,3700394856,73621],[34601369,2162827201,73456],[44470624,3024215269,73651]],
    y26:[[44388714,2957058516,73634],[41872696,2948462921,73797],[49678165,3721622449,73942],[47362312,2769333670,74073],[55463130,3411515036,74175]],
    bud:[44388714,41872696,47281150,47796140,51079600]},
  RT40:{n:"RT40 Power",c:"1F9D8B",
    y25:[[64622923,3375531107,1932],[63259832,3363954824,1930],[66641554,3558450298,1933],[64341208,3330662788,1943],[66557252,3609371946,1942],[68336945,3683421550,1946],[71186413,3627502483,1952],[71436651,3589743153,1947],[68941056,3687997809,1944],[68350099,3730851630,1949],[43348151,2667830502,1949],[59715678,3364996784,1949]],
    y26:[[56013972,3113218323,1955],[52824358,3115434733,1955],[61689769,3747347919,1952],[59597986,3162053643,1948],[65913617,3510264763,1952]],
    bud:[56013972,52824358,61748830,65177070,62480020]},
  RT50:{n:"RT50 Large Power",c:"9B59B6",
    y25:[[31427624,1409980651,158],[32136255,1456002251,160],[32062506,1502814519,161],[27946000,1329974470,159],[27361092,1365699631,158],[33517694,1557721511,158],[36711985,1589431158,159],[32479884,1412795090,158],[33527198,1473660257,159],[26980582,1386957881,158],[20973821,1077912391,159],[27705701,1319611977,159]],
    y26:[[26723902,1269696632,159],[26712470,1339462148,159],[29779866,1495187790,158],[28362022,1246575924,159],[30151229,1320599527,160]],
    bud:[26723902,26712470,28569070,25969880,30892270]},
  "RT60-ST":{n:"RT60 Streetlight",c:"E2864B",
    y25:[[3346882,239715921,493],[3354315,240822945,493],[3358623,244596384,492],[3355602,235368088,494],[3355442,246896535,494],[3393687,250273876,494],[3409167,248282310,504],[3399579,240553421,503],[3408536,247806505,503],[3414800,252823095,503],[1438578,101280920,503],[3412233,311032248,503]],
    y26:[[2224344,132586582,503],[2309944,211413199,503],[3098901,275034584,503],[3413243,218176034,503],[2798276,176768489,503]],
    bud:[2224344,2309944,3014540,3079200,3180130]},
  RT70:{n:"RT70 Standby/Spec.",c:"5D6D7E",
    y25:[[25269414,1070570172,23],[23928486,1093849347,23],[23748354,1048088572,23],[24504538,1075370537,23],[24774114,1138252466,23],[23261002,1059022865,23],[26580556,1088513461,23],[27515201,1119872021,25],[27281358,1273266420,23],[26927979,1246578040,23],[15548095,821575741,23],[18785028,919022955,23]],
    y26:[[20371320,961741098,23],[21088524,1009388288,23],[26193991,1337511423,22],[24727333,1075683703,21],[27726514,1211029497,21]],
    bud:[20371320,21088524,20273990,19747990,20747300]}
};

// Residential (RT10) buckets — customer counts
const zeroCustY25=[50800,52034,50801,50302,50445,50672,50816,50569,50935,51144,66782,176916];
const zeroCustY26=[109188,81291,68676,66699,65472];
const postCustY25=[578611,578180,580394,581417,582120,582724,583886,583985,584721,585168,569128,459510];
const postCustY26=[527710,555981,569958,572981,575095];
const prepCustY26=[11995,11900,12408,12444,12439];
// <Zero adjustment revenue (negative credits), JMD
const adjY25=[-18906339,-26190785,-14997855,-11697322,-21178327,-12255607,-10082904,-9360319,-6288293,-5698973,-2117404,-4580712];
const adjY26=[-8039331,-7939758,-11227760,-8999611,-8293167];

// ---------- HELPERS ----------
const MN=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const sum=a=>a.reduce((x,y)=>x+y,0);
const M=v=>v/1e6, B=v=>v/1e9;
const pct=(a,b)=>(a-b)/b*100;
const f1=v=>v.toLocaleString("en-US",{maximumFractionDigits:1,minimumFractionDigits:1});
const f0=v=>Math.round(v).toLocaleString("en-US");
const sgn=v=>(v>=0?"+":"")+f1(v);
// rate-class aggregate helpers
const rcRev=(k,yr,mi)=> (yr==25?RC[k].y25:RC[k].y26)[mi][1];
const rcKwh=(k,yr,mi)=> (yr==25?RC[k].y25:RC[k].y26)[mi][0];
const rcCust=(k,yr,mi)=> (yr==25?RC[k].y25:RC[k].y26)[mi][2];
const classes=Object.keys(RC);

// ---------- DERIVED KPIs ----------
const ytdK26=sum(tot2026.map(r=>r[1])), ytdK25=sum(tot2025.slice(0,5).map(r=>r[1]));
const ytdR26=sum(tot2026.map(r=>r[2])), ytdR25=sum(tot2025.slice(0,5).map(r=>r[2]));
const custMay26=tot2026[4][3], custMay25=tot2025[4][3];
const realK26=ytdR26/ytdK26, realK25=ytdR25/ytdK25;          // J$/kWh effective realization
const yoyK=pct(ytdK26,ytdK25), yoyR=pct(ytdR26,ytdR25), yoyC=pct(custMay26,custMay25);
// May
const mayK26=tot2026[4][1], mayK25=tot2025[4][1], aprK26=tot2026[3][1];
const mayR26=tot2026[4][2], mayR25=tot2025[4][2], aprR26=tot2026[3][2];
const momK=pct(mayK26,aprK26), momR=pct(mayR26,aprR26);
const yoyMayK=pct(mayK26,mayK25), yoyMayR=pct(mayR26,mayR25);
// budget (volume) Mar-May
const budVarPct=[2,3,4].map(i=>pct(tot2026[i][1],budKwh2026[i]));
const budYTDact=sum([2,3,4].map(i=>tot2026[i][1])), budYTDbud=sum([2,3,4].map(i=>budKwh2026[i]));

// print verification
console.log("YTD kWh YoY %",f1(yoyK)," Rev YoY %",f1(yoyR)," Cust YoY %",f1(yoyC));
console.log("Realization 25/26",f1(realK25),f1(realK26));
console.log("May MoM kWh/Rev",f1(momK),f1(momR)," May YoY kWh/Rev",f1(yoyMayK),f1(yoyMayR));
console.log("Budget var Mar-May %",budVarPct.map(f1),"YTD vol vs bud %",f1(pct(budYTDact,budYTDbud)));

// ---------- THEME ----------
const DARK="14202E",DARK2="1E2D40",YEL="FFC60B",LIGHT="F6F8FB",CARD="FFFFFF",
      INK="1B2A3A",MUT="6B7C8F",POS="1F9D8B",NEG="D9534F",BLU="3B6EA5",LINE="E2E8F0";
const HF="Georgia", BF="Calibri";
const pres=new pptxgen();
pres.layout="LAYOUT_WIDE"; // 13.3 x 7.5
const W=13.3,H=7.5;
pres.author="JPS FP&A"; pres.title="JPS Sales Analytics — YTD & May 2026";
const sh=()=>({type:"outer",color:"000000",blur:7,offset:3,angle:135,opacity:0.16});

function footer(s,n){
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:H-0.32,w:W,h:0.32,fill:{color:DARK}});
  s.addText("JPS Sales Platform · jps_actuals / jps_budget (Supabase) · Jan 2025–May 2026 · J$ unless noted",
    {x:0.4,y:H-0.32,w:10,h:0.32,fontFace:BF,fontSize:8,color:"9FB0C2",valign:"middle",margin:0});
  s.addText(String(n),{x:W-0.8,y:H-0.32,w:0.4,h:0.32,fontFace:BF,fontSize:9,color:"9FB0C2",align:"right",valign:"middle",margin:0});
}
function header(s,kicker,title){
  s.background={color:LIGHT};
  s.addText(kicker.toUpperCase(),{x:0.5,y:0.32,w:11,h:0.3,fontFace:BF,fontSize:11,color:BLU,bold:true,charSpacing:3,margin:0});
  s.addText(title,{x:0.5,y:0.6,w:12.3,h:0.65,fontFace:HF,fontSize:27,color:INK,bold:true,margin:0});
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.28,w:0.9,h:0.06,fill:{color:YEL}});
}
function chartBase(extra){
  return Object.assign({
    chartArea:{fill:{color:CARD}}, plotArea:{fill:{color:CARD}},
    catAxisLabelColor:MUT,valAxisLabelColor:MUT,catAxisLabelFontFace:BF,valAxisLabelFontFace:BF,
    catAxisLabelFontSize:10,valAxisLabelFontSize:9,
    valGridLine:{color:LINE,size:0.5},catGridLine:{style:"none"},
    showLegend:false
  },extra);
}

// ============ SLIDE 1 — TITLE ============
let s=pres.addSlide(); s.background={color:DARK};
s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:W,h:0.18,fill:{color:YEL}});
s.addShape(pres.shapes.RECTANGLE,{x:0,y:H-0.18,w:W,h:0.18,fill:{color:YEL}});
s.addText("JPS SALES PLATFORM  ·  FP&A REVENUE ANALYTICS",
  {x:0.9,y:1.5,w:11,h:0.4,fontFace:BF,fontSize:14,color:YEL,bold:true,charSpacing:3,margin:0});
s.addText("Sales, Revenue & Customer Movement",
  {x:0.9,y:2.15,w:11.6,h:1.0,fontFace:HF,fontSize:42,color:"FFFFFF",bold:true,margin:0});
s.addText("Trend, budget & anomaly review by rate class — YTD 2026 and May spotlight",
  {x:0.9,y:3.25,w:11.6,h:0.5,fontFace:BF,fontSize:18,color:"C7D3E0",margin:0});
// mini stat strip
const strip=[["YTD-26 Revenue","J$ "+f1(B(ytdR26))+"B",sgn(yoyR)+"% YoY"],
 ["YTD-26 Sales",f1(M(ytdK26)/1000)+" TWh",sgn(yoyK)+"% YoY"],
 ["Customers (May)",f0(custMay26),sgn(yoyC)+"% YoY"],
 ["Realization",f1(realK26)+" $/kWh",sgn(pct(realK26,realK25))+"% YoY"]];
strip.forEach((c,i)=>{const x=0.9+i*2.95;
  s.addShape(pres.shapes.RECTANGLE,{x,y:4.35,w:2.7,h:1.45,fill:{color:DARK2},line:{color:"2C4258",width:1}});
  s.addShape(pres.shapes.RECTANGLE,{x,y:4.35,w:0.07,h:1.45,fill:{color:YEL}});
  s.addText(c[0].toUpperCase(),{x:x+0.2,y:4.5,w:2.4,h:0.3,fontFace:BF,fontSize:9.5,color:"9FB0C2",bold:true,charSpacing:1,margin:0});
  s.addText(c[1],{x:x+0.2,y:4.82,w:2.45,h:0.55,fontFace:HF,fontSize:21,color:"FFFFFF",bold:true,margin:0});
  s.addText(c[2],{x:x+0.2,y:5.4,w:2.4,h:0.3,fontFace:BF,fontSize:11,color:(c[2].startsWith("+")?POS:NEG==NEG&&c[2].startsWith("-")?"FF8A80":POS),bold:true,margin:0});
});
s.addText("Prepared "+new Date().toISOString().slice(0,10)+"  ·  Source: live Supabase pull",
  {x:0.9,y:6.5,w:11,h:0.3,fontFace:BF,fontSize:11,color:"7E91A5",margin:0});

// ============ SLIDE 2 — EXECUTIVE SUMMARY ============
s=pres.addSlide(); header(s,"01 · Executive summary","What the numbers are saying");
// KPI cards
const kpi=[
 ["Sales volume (YTD)",sgn(yoyK)+"%",NEG,"vs 2025 · "+f1(M(ytdK26)/1000)+" TWh"],
 ["Revenue (YTD)",sgn(yoyR)+"%",NEG,"vs 2025 · J$"+f1(B(ytdR26))+"B"],
 ["Customers",sgn(yoyC)+"%",POS,"+"+f0(custMay26-custMay25)+" accounts YoY"],
 ["Vol. vs budget (Mar–May)",sgn(pct(budYTDact,budYTDbud))+"%",POS,"ahead of plan on kWh"]];
kpi.forEach((c,i)=>{const x=0.5+i*3.12;
  s.addShape(pres.shapes.RECTANGLE,{x,y:1.55,w:2.92,h:1.5,fill:{color:CARD},line:{color:LINE,width:1},shadow:sh()});
  s.addText(c[0].toUpperCase(),{x:x+0.18,y:1.7,w:2.6,h:0.5,fontFace:BF,fontSize:10,color:MUT,bold:true,charSpacing:1,margin:0});
  s.addText(c[1],{x:x+0.16,y:2.12,w:2.7,h:0.65,fontFace:HF,fontSize:32,color:c[2],bold:true,margin:0});
  s.addText(c[3],{x:x+0.18,y:2.74,w:2.65,h:0.28,fontFace:BF,fontSize:10.5,color:INK,margin:0});
});
// findings
s.addText("Key findings",{x:0.5,y:3.3,w:6,h:0.35,fontFace:HF,fontSize:16,color:INK,bold:true,margin:0});
s.addText([
 {text:"Volume is falling faster than revenue. ",options:{bold:true,color:INK,bullet:{code:"2022",color:YEL},breakLine:false}},
 {text:"YTD sales −"+f1(-yoyK)+"% but revenue only −"+f1(-yoyR)+"% — effective realization rose to "+f1(realK26)+" $/kWh.",options:{color:INK,breakLine:true}},
 {text:"Customers up, usage per customer down. ",options:{bold:true,color:INK,bullet:{code:"2022",color:YEL},breakLine:false}},
 {text:"+"+f0(custMay26-custMay25)+" accounts YoY, yet kWh/customer is lower — growth in low/zero-use accounts.",options:{color:INK,breakLine:true}},
 {text:"March–April revenue whipsaw. ",options:{bold:true,color:INK,bullet:{code:"2022",color:YEL},breakLine:false}},
 {text:"Mar realization J$"+f1(tot2026[2][2]/tot2026[2][1])+"/kWh spiked, Apr collapsed to J$"+f1(aprR26/aprK26)+" — likely fuel/true-up timing.",options:{color:INK,breakLine:true}},
 {text:"May rebound. ",options:{bold:true,color:INK,bullet:{code:"2022",color:YEL},breakLine:false}},
 {text:"MoM kWh "+sgn(momK)+"% and revenue "+sgn(momR)+"%, but still −"+f1(-yoyMayR)+"% revenue vs May-25.",options:{color:INK,breakLine:true}}
],{x:0.5,y:3.7,w:7.1,h:2.5,fontFace:BF,fontSize:12.5,lineSpacingMultiple:1.05,paraSpaceAfter:6,margin:0});
// anomaly flags panel
s.addShape(pres.shapes.RECTANGLE,{x:7.95,y:3.3,w:4.85,h:3.55,fill:{color:"FBEFD0"},line:{color:YEL,width:1.5}});
s.addText([{text:"⚑  ",options:{color:"B8860B"}},{text:"ANOMALIES FLAGGED",options:{bold:true,color:"8A6D1B"}}],
  {x:8.15,y:3.45,w:4.5,h:0.35,fontFace:BF,fontSize:12,charSpacing:1,margin:0});
s.addText([
 {text:"Budget revenue corrupted Mar–Dec 2026 (= kWh value); only kWh budget is usable.",options:{bullet:{code:"25B8",color:NEG},breakLine:true,color:"5A4A1E"}},
 {text:"Zero-consumption residential accounts spiked to 27% in Dec-25 (vs ~8% norm); ~10% now.",options:{bullet:{code:"25B8",color:NEG},breakLine:true,color:"5A4A1E"}},
 {text:"Streetlight (RT60) revenue −"+f1(-pct(rcRev("RT60-ST",26,4),rcRev("RT60-ST",25,4)))+"% YoY in May — billing irregular.",options:{bullet:{code:"25B8",color:NEG},breakLine:true,color:"5A4A1E"}},
 {text:"Negative billing-adjustment credits J$"+f1(-M(sum(adjY26)))+"M YTD; large one-off reversals May & Dec-25.",options:{bullet:{code:"25B8",color:NEG},breakLine:true,color:"5A4A1E"}},
 {text:"May upload relabelled buckets (dropped Post/Prepaid suffix) — schema drift.",options:{bullet:{code:"25B8",color:NEG},color:"5A4A1E"}}
],{x:8.15,y:3.85,w:4.5,h:2.9,fontFace:BF,fontSize:11,lineSpacingMultiple:1.02,paraSpaceAfter:7,margin:0});
footer(s,2);

// ============ SLIDE 3 — DATA & INTEGRITY ============
s=pres.addSlide(); header(s,"02 · Scope & data integrity","Read this before the charts");
const notes=[
 ["Coverage","Actuals Jan-2025 → May-2026 (17 months). Budget loaded for FY2026. 6 rate classes, ~9,300 account-rows/month."],
 ["Revenue budget — DO NOT USE","For Mar–Dec 2026 jps_budget.revenue_budget equals kwh_budget (data-load error). Jan/Feb budget = a copy of actuals. Revenue-vs-budget is therefore not shown; volume-vs-budget uses the intact kwh_budget."],
 ["Customer budget is static","Budgeted customer count frozen at the Feb actual — treat customer variance as directional only."],
 ["Prepaid revenue is NULL","Residential prepaid kWh is recorded but revenue is not booked in this table (recognised at point of sale). Prepaid excluded from revenue, kept in volume & counts."],
 ["Nov-2025 partial","Nov-2025 kWh is ~36% below trend across every class — an incomplete billing cycle, not a demand collapse. Flagged, not over-weighted."],
 ["May bucket relabel","May-2026 zero/credit buckets dropped the -Postpaid/-Prepaid suffix; totals reconcile but the sub-split breaks in May."]];
notes.forEach((nrow,i)=>{const col=i%2,row=Math.floor(i/2);const x=0.5+col*6.25,y=1.6+row*1.72;
  s.addShape(pres.shapes.RECTANGLE,{x,y,w:5.95,h:1.55,fill:{color:CARD},line:{color:LINE,width:1},shadow:sh()});
  s.addShape(pres.shapes.RECTANGLE,{x,y,w:0.09,h:1.55,fill:{color:i==1?NEG:BLU}});
  s.addText(nrow[0],{x:x+0.25,y:y+0.13,w:5.5,h:0.35,fontFace:HF,fontSize:14,color:(i==1?NEG:INK),bold:true,margin:0});
  s.addText(nrow[1],{x:x+0.25,y:y+0.52,w:5.55,h:0.95,fontFace:BF,fontSize:11,color:INK,lineSpacingMultiple:1.0,margin:0});
});
footer(s,3);

// ============ SLIDE 4 — SALES vs REVENUE TREND (indexed) ============
s=pres.addSlide(); header(s,"03 · The core trend","Sales vs revenue vs customers — indexed to Jan-2025 = 100");
const allMonths=tot2025.concat(tot2026);
const labels17=allMonths.map((r,i)=>MN[(r[0]-1)]+(i<12?"·25":"·26"));
const base=allMonths[0];
const idxK=allMonths.map(r=>r[1]/base[1]*100);
const idxR=allMonths.map(r=>r[2]/base[2]*100);
const idxC=allMonths.map(r=>r[3]/base[3]*100);
s.addChart(pres.charts.LINE,[
  {name:"Sales (kWh)",labels:labels17,values:idxK},
  {name:"Revenue (J$)",labels:labels17,values:idxR},
  {name:"Customers",labels:labels17,values:idxC}
],chartBase({x:0.5,y:1.55,w:8.55,h:5.25,lineSize:2.5,lineSmooth:true,
  chartColors:[BLU,YEL,POS],showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:11,
  valAxisMinVal:60,valAxisMaxVal:120,catAxisLabelRotate:-45}));
// side commentary
s.addShape(pres.shapes.RECTANGLE,{x:9.3,y:1.55,w:3.5,h:5.25,fill:{color:CARD},line:{color:LINE,width:1},shadow:sh()});
s.addText("Reading the divergence",{x:9.5,y:1.72,w:3.15,h:0.35,fontFace:HF,fontSize:14,color:INK,bold:true,margin:0});
s.addText([
 {text:"Customer line drifts up (+1% YoY) while sales & revenue sit well below the 2025 band.",options:{bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:"Revenue (yellow) holds above sales (blue) — price/realization is cushioning lower volume.",options:{bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:"Aug-25 was the volume peak; 2026 is tracking a structurally lower demand curve.",options:{bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:"Nov-25 trough = partial billing cycle (data), not real demand.",options:{bullet:{code:"2022",color:NEG},breakLine:true}}
],{x:9.5,y:2.15,w:3.15,h:3.0,fontFace:BF,fontSize:11,color:INK,lineSpacingMultiple:1.02,paraSpaceAfter:8,margin:0});
s.addShape(pres.shapes.RECTANGLE,{x:9.5,y:5.6,w:3.1,h:1.05,fill:{color:DARK}});
s.addText([{text:"Effective realization\n",options:{fontSize:10,color:"9FB0C2",bold:true}},
  {text:"J$"+f1(realK25)+" → "+f1(realK26)+" /kWh",options:{fontSize:16,color:YEL,bold:true}}],
  {x:9.65,y:5.72,w:2.85,h:0.85,fontFace:BF,valign:"middle",margin:0});
footer(s,4);

// ============ SLIDE 5 — YTD YoY SCORECARD ============
s=pres.addSlide(); header(s,"04 · Year-on-year","YTD Jan–May: 2026 vs 2025");
// grouped bars per month: revenue
s.addText("Revenue by month (J$ B)",{x:0.5,y:1.5,w:6,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[
 {name:"2025",labels:MN.slice(0,5),values:tot2025.slice(0,5).map(r=>+B(r[2]).toFixed(2))},
 {name:"2026",labels:MN.slice(0,5),values:tot2026.map(r=>+B(r[2]).toFixed(2))}
],chartBase({x:0.4,y:1.85,w:6.4,h:4.9,barDir:"col",chartColors:["B9C6D6",YEL],
 showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:11,
 showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:9,dataLabelColor:INK,
 dataLabelFormatCode:"0.0",valAxisMaxVal:19,valAxisHidden:true}));
// kWh by month
s.addText("Sales by month (GWh)",{x:6.95,y:1.5,w:6,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[
 {name:"2025",labels:MN.slice(0,5),values:tot2025.slice(0,5).map(r=>+(r[1]/1e6).toFixed(0))},
 {name:"2026",labels:MN.slice(0,5),values:tot2026.map(r=>+(r[1]/1e6).toFixed(0))}
],chartBase({x:6.85,y:1.85,w:6.0,h:4.9,barDir:"col",chartColors:["B9C6D6",BLU],
 showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:11,
 showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:9,dataLabelColor:INK,
 valAxisMaxVal:330,valAxisHidden:true}));
footer(s,5);

// ============ SLIDE 6 — MAY SPOTLIGHT ============
s=pres.addSlide(); header(s,"05 · May 2026 spotlight","Strong sequential rebound, still soft vs last year");
const mcards=[
 ["May sales","MoM",sgn(momK)+"%",momK>=0?POS:NEG,f1(M(mayK26)/1)+" M kWh"],
 ["May sales","YoY",sgn(yoyMayK)+"%",yoyMayK>=0?POS:NEG,"vs "+f1(M(mayK25))+"M"],
 ["May revenue","MoM",sgn(momR)+"%",momR>=0?POS:NEG,"J$"+f1(B(mayR26))+"B"],
 ["May revenue","YoY",sgn(yoyMayR)+"%",yoyMayR>=0?POS:NEG,"vs J$"+f1(B(mayR25))+"B"]];
mcards.forEach((c,i)=>{const x=0.5+i*3.12;
  s.addShape(pres.shapes.RECTANGLE,{x,y:1.55,w:2.92,h:1.7,fill:{color:CARD},line:{color:LINE,width:1},shadow:sh()});
  s.addText(c[0]+"  ·  "+c[1],{x:x+0.18,y:1.7,w:2.6,h:0.3,fontFace:BF,fontSize:10.5,color:MUT,bold:true,margin:0});
  s.addText(c[2],{x:x+0.16,y:2.05,w:2.7,h:0.7,fontFace:HF,fontSize:34,color:c[3],bold:true,margin:0});
  s.addText(c[4],{x:x+0.18,y:2.82,w:2.65,h:0.3,fontFace:BF,fontSize:11,color:INK,margin:0});
});
// Apr/May25/May26 grouped bars (rev & kwh)
s.addText("Apr-26  →  May-26  vs  May-25",{x:0.5,y:3.55,w:8,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[
 {name:"Sales (M kWh)",labels:["Apr-26","May-25","May-26"],values:[+M(aprK26).toFixed(0),+M(mayK25).toFixed(0),+M(mayK26).toFixed(0)]},
 {name:"Revenue (J$00M)",labels:["Apr-26","May-25","May-26"],values:[+(aprR26/1e8).toFixed(0),+(mayR25/1e8).toFixed(0),+(mayR26/1e8).toFixed(0)]}
],chartBase({x:0.4,y:3.9,w:7.6,h:2.9,barDir:"col",chartColors:[BLU,YEL],
 showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:10,
 showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:9,dataLabelColor:INK,valAxisHidden:true}));
// narrative
s.addShape(pres.shapes.RECTANGLE,{x:8.25,y:3.55,w:4.55,h:3.25,fill:{color:DARK}});
s.addText("Why May matters",{x:8.45,y:3.7,w:4.2,h:0.35,fontFace:HF,fontSize:14,color:YEL,bold:true,margin:0});
s.addText([
 {text:"Sequential snap-back from the soft April: kWh "+sgn(momK)+"%, revenue "+sgn(momR)+"%.",options:{color:"DCE6F0",bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:"Revenue grew faster than volume MoM — realization recovered after the April dip.",options:{color:"DCE6F0",bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:"Still −"+f1(-yoyMayR)+"% revenue YoY on +"+f1(yoyMayK)+"% volume: the YoY gap is price, not demand.",options:{color:"DCE6F0",bullet:{code:"2022",color:YEL},breakLine:true}}
],{x:8.45,y:4.15,w:4.2,h:2.5,fontFace:BF,fontSize:11.5,lineSpacingMultiple:1.05,paraSpaceAfter:9,margin:0});
footer(s,6);

// ============ SLIDE 7 — MOVEMENT TO BUDGET (volume) ============
s=pres.addSlide(); header(s,"06 · Movement to budget","Volume vs plan — kWh (revenue budget unusable, see slide 3)");
s.addChart(pres.charts.BAR,[
 {name:"Actual",labels:["Mar","Apr","May"],values:[2,3,4].map(i=>+M(tot2026[i][1]).toFixed(0))},
 {name:"Budget",labels:["Mar","Apr","May"],values:[2,3,4].map(i=>+M(budKwh2026[i]).toFixed(0))}
],chartBase({x:0.4,y:1.7,w:7.2,h:5.05,barDir:"col",chartColors:[POS,"C9D3DE"],
 showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:11,
 showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:10,dataLabelColor:INK,
 valAxisHidden:true,barGapWidthPct:60}));
// variance cards
s.addText("kWh variance to budget",{x:8.0,y:1.65,w:4.8,h:0.35,fontFace:HF,fontSize:15,color:INK,bold:true,margin:0});
["Mar","Apr","May"].forEach((m,i)=>{const y=2.15+i*1.15;const v=budVarPct[i];
  s.addShape(pres.shapes.RECTANGLE,{x:8.0,y,w:4.8,h:1.0,fill:{color:CARD},line:{color:LINE,width:1},shadow:sh()});
  s.addShape(pres.shapes.RECTANGLE,{x:8.0,y,w:0.08,h:1.0,fill:{color:v>=0?POS:NEG}});
  s.addText(m+" 2026",{x:8.25,y:y+0.12,w:2.2,h:0.35,fontFace:HF,fontSize:15,color:INK,bold:true,margin:0});
  s.addText(f1(M(tot2026[i+2][1]))+"M vs "+f1(M(budKwh2026[i+2]))+"M plan",{x:8.25,y:y+0.52,w:3.0,h:0.35,fontFace:BF,fontSize:10.5,color:MUT,margin:0});
  s.addText(sgn(v)+"%",{x:10.7,y:y+0.18,w:2.0,h:0.65,fontFace:HF,fontSize:26,color:v>=0?POS:NEG,bold:true,align:"right",margin:0});
});
s.addShape(pres.shapes.RECTANGLE,{x:8.0,y:5.7,w:4.8,h:1.05,fill:{color:"E6F4F1"},line:{color:POS,width:1.2}});
s.addText([{text:"YTD Mar–May volume vs plan\n",options:{fontSize:11,color:"15715F",bold:true}},
 {text:sgn(pct(budYTDact,budYTDbud))+"%  ("+f1(M(budYTDact-budYTDbud))+"M kWh ahead)",options:{fontSize:18,color:"15715F",bold:true}}],
 {x:8.25,y:5.82,w:4.4,h:0.85,fontFace:BF,valign:"middle",margin:0});
footer(s,7);

// ============ SLIDE 8 — REVENUE BY RATE CLASS ============
s=pres.addSlide(); header(s,"07 · Rate class","Revenue by rate class — May YoY & YTD mix");
// grouped bar May25 vs May26 per class
s.addText("May revenue by class (J$ B) — 2025 vs 2026",{x:0.5,y:1.5,w:7,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[
 {name:"May-25",labels:classes.map(k=>RC[k].n.split(" ")[0]),values:classes.map(k=>+B(rcRev(k,25,4)).toFixed(2))},
 {name:"May-26",labels:classes.map(k=>RC[k].n.split(" ")[0]),values:classes.map(k=>+B(rcRev(k,26,4)).toFixed(2))}
],chartBase({x:0.4,y:1.85,w:7.7,h:4.9,barDir:"col",chartColors:["B9C6D6",YEL],
 showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:11,
 showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:8.5,dataLabelColor:INK,
 dataLabelFormatCode:"0.0",valAxisHidden:true}));
// YTD mix — horizontal % share bar (avoids donut label collision)
const ytdRevByClass=classes.map(k=>sum(RC[k].y26.map(r=>r[1])));
const ytdRevTot=sum(ytdRevByClass);
s.addText("YTD-26 revenue mix (% of total)",{x:8.5,y:1.5,w:4.3,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[{name:"share",labels:classes.map(k=>RC[k].n.split(" ")[0]),values:classes.map((k,i)=>+(ytdRevByClass[i]/ytdRevTot*100).toFixed(1))}],
 {x:8.3,y:1.85,w:4.55,h:3.05,barDir:"bar",chartColors:[BLU],
  chartArea:{fill:{color:CARD}},plotArea:{fill:{color:CARD}},
  showLegend:false,barGapWidthPct:45,
  showValue:true,dataLabelFormatCode:'0.0"%"',dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:9,dataLabelColor:INK,
  catAxisLabelColor:INK,catAxisLabelFontFace:BF,catAxisLabelFontSize:9.5,
  valAxisHidden:true,valAxisMaxVal:42,catGridLine:{style:"none"},valGridLine:{style:"none"}});
s.addShape(pres.shapes.RECTANGLE,{x:8.5,y:5.05,w:4.3,h:1.75,fill:{color:CARD},line:{color:LINE,width:1},shadow:sh()});
s.addText([
 {text:"RT10 + RT20 ≈ "+f1((ytdRevByClass[0]+ytdRevByClass[1])/sum(ytdRevByClass)*100)+"% of revenue.",options:{bullet:{code:"2022",color:YEL},breakLine:true,color:INK}},
 {text:"Every class is below May-25 revenue.",options:{bullet:{code:"2022",color:NEG},breakLine:true,color:INK}},
 {text:"RT60 streetlight worst hit (−"+f1(-pct(rcRev("RT60-ST",26,4),rcRev("RT60-ST",25,4)))+"%).",options:{bullet:{code:"2022",color:NEG},color:INK}}
],{x:8.7,y:5.18,w:4.0,h:1.55,fontFace:BF,fontSize:11,lineSpacingMultiple:1.02,paraSpaceAfter:6,margin:0});
footer(s,8);

// ============ SLIDE 9 — kWh BY RATE CLASS (stacked trend) ============
s=pres.addSlide(); header(s,"08 · Rate class","Sales volume composition — 2026 monthly (GWh)");
s.addChart(pres.charts.BAR,classes.map(k=>({
  name:RC[k].n.split(" ")[0],labels:MN.slice(0,5),
  values:RC[k].y26.map(r=>+(r[0]/1e6).toFixed(1))
})),chartBase({x:0.4,y:1.6,w:8.7,h:5.15,barDir:"col",barGrouping:"stacked",
  chartColors:classes.map(k=>RC[k].c),showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:10,
  valAxisTitle:"GWh",showValue:false}));
s.addShape(pres.shapes.RECTANGLE,{x:9.35,y:1.6,w:3.45,h:5.15,fill:{color:CARD},line:{color:LINE,width:1},shadow:sh()});
s.addText("Volume notes",{x:9.55,y:1.75,w:3.1,h:0.35,fontFace:HF,fontSize:14,color:INK,bold:true,margin:0});
s.addText([
 {text:"Residential (RT10) is ~38% of kWh and drives the seasonal shape.",options:{bullet:{code:"2022",color:RC.RT10.c},breakLine:true}},
 {text:"Feb is the low point; volume builds through May into the summer peak.",options:{bullet:{code:"2022",color:YEL},breakLine:true}},
 {text:"RT50 Large Power +"+f1(pct(rcKwh("RT50",26,4),rcKwh("RT50",25,4)))+"% kWh YoY (May) — an industrial bright spot.",options:{bullet:{code:"2022",color:POS},breakLine:true}},
 {text:"RT70 Standby +"+f1(pct(rcKwh("RT70",26,4),rcKwh("RT70",25,4)))+"% kWh YoY (May).",options:{bullet:{code:"2022",color:POS},breakLine:true}}
],{x:9.55,y:2.2,w:3.1,h:4.3,fontFace:BF,fontSize:11,color:INK,lineSpacingMultiple:1.03,paraSpaceAfter:9,margin:0});
footer(s,9);

// ============ SLIDE 10 — VOLUME vs REVENUE DIVERGENCE BY CLASS ============
s=pres.addSlide(); header(s,"09 · The anomaly","Volume up, revenue down — the price gap by class (May YoY)");
const divK=classes.map(k=>pct(rcKwh(k,26,4),rcKwh(k,25,4)));
const divR=classes.map(k=>pct(rcRev(k,26,4),rcRev(k,25,4)));
s.addChart(pres.charts.BAR,[
 {name:"Sales kWh YoY %",labels:classes.map(k=>RC[k].n.split(" ")[0]),values:divK.map(v=>+v.toFixed(1))},
 {name:"Revenue YoY %",labels:classes.map(k=>RC[k].n.split(" ")[0]),values:divR.map(v=>+v.toFixed(1))}
],chartBase({x:0.4,y:1.6,w:8.5,h:5.15,barDir:"col",chartColors:[BLU,YEL],
 showLegend:true,legendPos:"b",legendFontFace:BF,legendFontSize:11,
 showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:9,dataLabelColor:INK}));
s.addShape(pres.shapes.RECTANGLE,{x:9.15,y:1.6,w:3.65,h:5.15,fill:{color:"FBEFD0"},line:{color:YEL,width:1.5}});
s.addText("The realization squeeze",{x:9.35,y:1.75,w:3.3,h:0.35,fontFace:HF,fontSize:14,color:"8A6D1B",bold:true,margin:0});
s.addText([
 {text:"In 4 of 6 classes volume rose but revenue fell — a clear price/fuel effect, not a demand problem.",options:{color:"5A4A1E",bullet:{code:"2022",color:NEG},breakLine:true}},
 {text:"RT50: kWh "+sgn(divK[3])+"% yet revenue "+sgn(divR[3])+"% — widest gap.",options:{color:"5A4A1E",bullet:{code:"2022",color:NEG},breakLine:true}},
 {text:"RT60 streetlight is the exception: both volume and revenue down sharply — a billing/metering issue to chase.",options:{color:"5A4A1E",bullet:{code:"2022",color:NEG},breakLine:true}},
 {text:"Action: confirm fuel-rate pass-through and any tariff change between May-25 and May-26.",options:{color:"5A4A1E",bold:true,bullet:{code:"2022",color:"B8860B"}}}
],{x:9.35,y:2.2,w:3.3,h:4.4,fontFace:BF,fontSize:11,lineSpacingMultiple:1.04,paraSpaceAfter:9,margin:0});
footer(s,10);

// ============ SLIDE 11 — CONSUMPTION BUCKETS vs CUSTOMER COUNT ============
s=pres.addSlide(); header(s,"10 · Customers & buckets","Customer count is rising — but into zero-use buckets");
const zeroAll=zeroCustY25.concat(zeroCustY26);
const rt10CustAll=RC.RT10.y25.map(r=>r[2]).concat(RC.RT10.y26.map(r=>r[2]));
const zeroShare=zeroAll.map((z,i)=>z/rt10CustAll[i]*100);
const labelsZ=labels17;
s.addText("Zero-consumption residential accounts as % of RT10 customers",{x:0.5,y:1.5,w:9,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.LINE,[{name:"Zero-use share %",labels:labelsZ,values:zeroShare.map(v=>+v.toFixed(1))}],
 chartBase({x:0.4,y:1.85,w:8.6,h:4.9,lineSize:3,lineSmooth:true,chartColors:[NEG],
  lineDataSymbol:"circle",lineDataSymbolSize:5,showValue:false,
  catAxisLabelRotate:-45,valAxisMaxVal:30,valAxisMinVal:0,valAxisLabelFormatCode:'0"%"'}));
// key-point callouts
s.addText("~8% baseline (2025 H1)",{x:1.0,y:5.55,w:2.4,h:0.3,fontFace:BF,fontSize:10,color:MUT,bold:true,align:"center",margin:0});
s.addText([{text:"27%",options:{fontSize:14,color:NEG,bold:true,breakLine:true}},{text:"Dec-25 spike",options:{fontSize:9,color:NEG}}],{x:6.4,y:1.95,w:1.4,h:0.6,fontFace:BF,align:"center",margin:0});
s.addText([{text:"~10%",options:{fontSize:13,color:"B85C00",bold:true,breakLine:true}},{text:"May-26",options:{fontSize:9,color:"B85C00"}}],{x:8.0,y:4.75,w:1.0,h:0.55,fontFace:BF,align:"center",margin:0});
s.addShape(pres.shapes.RECTANGLE,{x:9.25,y:1.85,w:3.55,h:4.9,fill:{color:CARD},line:{color:LINE,width:1},shadow:sh()});
s.addText("What's happening",{x:9.45,y:2.0,w:3.2,h:0.35,fontFace:HF,fontSize:14,color:INK,bold:true,margin:0});
s.addText([
 {text:"Baseline zero-use ≈ 8% of residential accounts through 2025-H1.",options:{bullet:{code:"2022",color:MUT},breakLine:true,color:INK}},
 {text:"Spiked to 27% in Dec-25 (≈177k accounts) — holiday estimated/unread bills.",options:{bullet:{code:"2022",color:NEG},breakLine:true,color:INK}},
 {text:"Normalising through 2026 but settling near 10% — a structurally higher zero-use base.",options:{bullet:{code:"2022",color:NEG},breakLine:true,color:INK}},
 {text:"Implication: account growth (+1% YoY) is not converting to kWh or revenue — usage per active customer is the metric to watch.",options:{bullet:{code:"2022",color:YEL},color:INK,bold:true}}
],{x:9.45,y:2.45,w:3.2,h:4.2,fontFace:BF,fontSize:10.5,lineSpacingMultiple:1.03,paraSpaceAfter:8,margin:0});
footer(s,11);

// ============ SLIDE 12 — ADJUSTMENTS / CREDITS ============
s=pres.addSlide(); header(s,"11 · Adjustments","Billing credits & reversals (the '<Zero' bucket)");
const adjAll=adjY25.concat(adjY26).map(v=>+(v/1e6).toFixed(1));
s.addText("Monthly billing-adjustment credits (J$ M, negative = credit to customers)",{x:0.5,y:1.5,w:10,h:0.3,fontFace:BF,fontSize:12,color:MUT,bold:true,margin:0});
s.addChart(pres.charts.BAR,[{name:"Adjustment J$M",labels:labels17.slice(0,adjAll.length),values:adjAll}],
 chartBase({x:0.4,y:1.85,w:8.7,h:4.9,barDir:"col",chartColors:[NEG],
  showValue:true,dataLabelPosition:"outEnd",dataLabelFontFace:BF,dataLabelFontSize:8.5,dataLabelColor:NEG,
  catAxisLabelRotate:-45}));
s.addShape(pres.shapes.RECTANGLE,{x:9.35,y:1.85,w:3.45,h:4.9,fill:{color:CARD},line:{color:LINE,width:1},shadow:sh()});
s.addText("Adjustment read",{x:9.55,y:2.0,w:3.1,h:0.35,fontFace:HF,fontSize:14,color:INK,bold:true,margin:0});
s.addText([
 {text:"YTD-26 credits total J$"+f1(-M(sum(adjY26)))+"M — modest vs J$"+f1(B(ytdR26))+"B revenue.",options:{bullet:{code:"2022",color:MUT},breakLine:true,color:INK}},
 {text:"Mar-26 is the heaviest credit month (J$"+f1(-adjY26[2]/1e6)+"M).",options:{bullet:{code:"2022",color:NEG},breakLine:true,color:INK}},
 {text:"Separately, the normally-positive 'Zero' fixed-charge bucket flipped negative in May-25 (−J$22M) and Dec-25 (−J$15M) — large one-off reversals worth auditing.",options:{bullet:{code:"2022",color:NEG},breakLine:true,color:INK}},
 {text:"These reversals partly explain the lumpy Mar/Apr realization swing.",options:{bullet:{code:"2022",color:YEL},color:INK}}
],{x:9.55,y:2.45,w:3.1,h:4.2,fontFace:BF,fontSize:10.5,lineSpacingMultiple:1.03,paraSpaceAfter:8,margin:0});
footer(s,12);

// ============ SLIDE 13 — ANOMALY REGISTER ============
s=pres.addSlide(); header(s,"12 · Anomaly register","Consolidated watch-list");
const rows=[
 ["#","Anomaly","Evidence","Severity","Action"],
 ["1","Budget revenue corrupted (Mar–Dec 26)","revenue_budget = kwh_budget in jps_budget","High","Reload budget revenue before any rev-vs-plan reporting"],
 ["2","Zero-use account surge","27% of RT10 in Dec-25 vs ~8% norm; ~10% now","High","Confirm estimated-read backlog; track usage/active cust"],
 ["3","Mar↑/Apr↓ realization swing","J$"+f1(tot2026[2][2]/tot2026[2][1])+" → J$"+f1(aprR26/aprK26)+" /kWh","Med","Reconcile fuel pass-through & prior-period true-ups"],
 ["4","Streetlight (RT60) decline","Rev −"+f1(-pct(rcRev("RT60-ST",26,4),rcRev("RT60-ST",25,4)))+"% & kWh −"+f1(-pct(rcKwh("RT60-ST",26,4),rcKwh("RT60-ST",25,4)))+"% YoY (May)","Med","Audit streetlight metering/billing completeness"],
 ["5","Large one-off credit reversals","Zero bucket −J$22M (May-25), −J$15M (Dec-25)","Med","Trace journal source; assess recurrence"],
 ["6","May bucket relabel","Suffix dropped on zero/credit buckets","Low","Standardise upload mapping"],
 ["7","Nov-25 partial cycle","kWh ~36% below trend, all classes","Low","Exclude from trend; confirm cut-off"]];
const sev=t=>t=="High"?NEG:(t=="Med"?"E2864B":"7E8C9A");
s.addTable(rows.map((r,ri)=>r.map((c,ci)=>{
  if(ri==0)return{text:c,options:{fill:{color:DARK},color:"FFFFFF",bold:true,fontSize:11,align:ci==0?"center":"left",valign:"middle",fontFace:BF}};
  if(ci==3)return{text:c,options:{fill:{color:ri%2?"FFFFFF":"F1F5F9"},color:sev(c),bold:true,fontSize:10.5,align:"center",valign:"middle",fontFace:BF}};
  if(ci==0)return{text:c,options:{fill:{color:ri%2?"FFFFFF":"F1F5F9"},color:INK,bold:true,fontSize:10.5,align:"center",valign:"middle",fontFace:BF}};
  return{text:c,options:{fill:{color:ri%2?"FFFFFF":"F1F5F9"},color:INK,fontSize:10.5,valign:"middle",fontFace:BF}};
})),{x:0.5,y:1.55,w:12.3,colW:[0.5,3.0,3.4,1.1,4.3],rowH:0.62,border:{type:"solid",pt:0.5,color:LINE},margin:[3,4,3,4]});
footer(s,13);

// ============ SLIDE 14 — RECOMMENDATIONS / CLOSE ============
s=pres.addSlide(); s.background={color:DARK};
s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:0.22,h:H,fill:{color:YEL}});
s.addText("RECOMMENDATIONS",{x:0.9,y:0.7,w:11,h:0.4,fontFace:BF,fontSize:13,color:YEL,bold:true,charSpacing:3,margin:0});
s.addText("Where to focus next",{x:0.9,y:1.1,w:11,h:0.7,fontFace:HF,fontSize:32,color:"FFFFFF",bold:true,margin:0});
const recs=[
 ["1","Fix the budget","Reload FY26 revenue_budget; rebuild mv_budget_agg. Revenue-vs-plan is currently impossible — the single biggest data gap."],
 ["2","Decompose the YoY revenue gap","Volume is +ve in most classes; the −5.6% YTD revenue is price. Split fuel pass-through vs base tariff vs adjustments and quantify each."],
 ["3","Own the zero-use base","Investigate the post-Dec-25 step-up in zero-consumption accounts. Report kWh & revenue per active customer, not just account count."],
 ["4","Chase RT60 streetlight","Both volume and revenue down double-digits — most likely a metering/billing completeness issue, not demand."],
 ["5","Audit one-off reversals","Trace the −J$22M (May-25) and −J$15M (Dec-25) credit reversals; confirm they are non-recurring before forecasting."]];
recs.forEach((r,i)=>{const y=2.0+i*0.98;
  s.addShape(pres.shapes.OVAL,{x:0.95,y,w:0.6,h:0.6,fill:{color:YEL}});
  s.addText(r[0],{x:0.95,y,w:0.6,h:0.6,fontFace:HF,fontSize:22,color:DARK,bold:true,align:"center",valign:"middle",margin:0});
  s.addText([{text:r[1]+"   ",options:{bold:true,color:YEL,fontSize:15}},{text:r[2],options:{color:"D7E1EC",fontSize:12}}],
    {x:1.75,y:y-0.05,w:10.6,h:0.92,fontFace:BF,valign:"middle",lineSpacingMultiple:1.0,margin:0});
});
s.addText("JPS Sales Platform · FP&A · figures from live Supabase pull · J$ unless noted",
  {x:0.9,y:7.0,w:11.5,h:0.3,fontFace:BF,fontSize:10,color:"7E91A5",margin:0});

pres.writeFile({fileName:"D:\\Projects\\Sales_Platform\\analysis\\JPS_Sales_Analysis_YTD_May2026.pptx"})
 .then(f=>console.log("WROTE",f));
