const pptxgen=require('pptxgenjs');
const fs=require('fs');
const V=JSON.parse(fs.readFileSync('varset.json'));
const CL=V.classes, A=V.actual, B=V.budget, WIN=V.win;
const MLAB={'2026-01':'Jan-26','2026-02':'Feb-26','2026-03':'Mar-26','2026-04':'Apr-26','2026-05':'May-26','2026-06':'Jun-26','2026-07':'Jul-26','2026-08':'Aug-26','2026-09':'Sep-26','2026-10':'Oct-26','2026-11':'Nov-26','2026-12':'Dec-26'};
const BMON=V.budget_months, AMON=V.actual_months;
const winlab=MLAB[WIN[WIN.length-1]]||'n/a';
const aY=(c,k)=>WIN.reduce((s,m)=>s+(A[c][k][m]||0),0);
const bY=(c,k)=>WIN.reduce((s,m)=>s+(B[c][k][m]||0),0);
const NAVY='1F3864',RED='C00000',LBLUE='9DC3E6',LORG='F4B183',GREEN='70AD47',GREY='7F7F7F',INK='222222';
const p=new pptxgen(); p.defineLayout({name:'W',width:13.33,height:7.5}); p.layout='W';
const HEAD='Georgia', BODY='Calibri';

// ---- Slide 1: title ----
let s=p.addSlide(); s.background={color:NAVY};
s.addText('JPS · FP&A',{x:0.6,y:0.7,w:6,h:0.4,fontFace:BODY,color:LBLUE,fontSize:14,bold:true,charSpacing:3});
s.addText('Demand, Energy & Revenue',{x:0.6,y:2.2,w:12,h:1.0,fontFace:HEAD,color:'FFFFFF',fontSize:44,bold:true});
s.addText('Actual vs Budget — February 2026 LE',{x:0.6,y:3.3,w:12,h:0.7,fontFace:HEAD,color:LORG,fontSize:26,italic:true});
s.addText([{text:'YTD through '+winlab+'  ·  J$ millions  ·  meter-level actuals vs Feb 2026 LE',options:{fontSize:14,color:'CADCFC'}}],
  {x:0.6,y:4.3,w:12,h:0.5,fontFace:BODY});
s.addText('Note: Feb LE embeds actual volumes for closed months (Jan/Feb) — genuine plan-vs-actual variance emerges in the forecast months (Mar onward).',
  {x:0.6,y:6.4,w:12,h:0.6,fontFace:BODY,color:'9FB0C2',fontSize:11,italic:true});

// ---- Slide 2: Monthly Trend (line graph) ----
s=p.addSlide(); s.background={color:'FFFFFF'};
s.addText('Monthly Trend — Demand vs Energy',{x:0.5,y:0.35,w:12,h:0.6,fontFace:HEAD,color:NAVY,fontSize:30,bold:true});
s.addText('Total company · J$M · Actual (dark) vs Budget (light) · demand red, energy navy · actuals through '+winlab,
  {x:0.5,y:1.0,w:12.3,h:0.35,fontFace:BODY,color:GREY,fontSize:13,italic:true});
const labs=BMON.map(m=>MLAB[m]);
const totA=(k)=>BMON.map(m=>AMON.includes(m)?+CL.reduce((s2,c)=>s2+(A[c][k][m]||0),0).toFixed(0):null);
const totB=(k)=>BMON.map(m=>+CL.reduce((s2,c)=>s2+(B[c][k][m]||0),0).toFixed(0));
const trend=[{name:'Actual Demand',labels:labs,values:totA('demand')},
             {name:'Budget Demand',labels:labs,values:totB('demand')},
             {name:'Actual Energy',labels:labs,values:totA('energy')},
             {name:'Budget Energy',labels:labs,values:totB('energy')}];
s.addChart(p.ChartType.line,trend,{x:0.5,y:1.55,w:12.3,h:5.0,chartColors:[RED,LORG,NAVY,LBLUE],
  lineSize:2.75,lineSmooth:false,showLegend:true,legendPos:'b',legendFontSize:11,
  catAxisLabelFontSize:10,valAxisLabelFontSize:9,valAxisTitle:'J$ millions',showValAxisTitle:true,valGridLine:{style:'none'}});
s.addText('Budget energy rises with seasonal load while budget demand stays flat — the structural gap behind realization dilution. Actual lines extend as months close.',
  {x:0.5,y:6.95,w:12.3,h:0.4,fontFace:BODY,color:GREY,fontSize:12,italic:true});

// ---- Slide 3: By Rate Class ----
s=p.addSlide(); s.background={color:'FFFFFF'};
s.addText('By Rate Class — Demand vs Energy',{x:0.5,y:0.35,w:12,h:0.6,fontFace:HEAD,color:NAVY,fontSize:30,bold:true});
s.addText('Actual vs Budget (Feb LE), YTD through '+winlab+' · J$M · demand applies to RT40/RT50/RT70 only',
  {x:0.5,y:1.0,w:12,h:0.35,fontFace:BODY,color:GREY,fontSize:13,italic:true});
const demCats=['RT40','RT50','RT70'];
const demChart=[{name:'Actual',labels:demCats,values:demCats.map(c=>+aY(c,'demand').toFixed(0))},
                {name:'Budget',labels:demCats,values:demCats.map(c=>+bY(c,'demand').toFixed(0))}];
s.addText('Demand charge (J$M)',{x:0.5,y:1.5,w:6,h:0.3,fontFace:BODY,bold:true,color:INK,fontSize:13});
s.addChart(p.ChartType.bar,demChart,{x:0.5,y:1.85,w:6.1,h:4.9,barDir:'col',chartColors:[RED,LORG],
  showLegend:true,legendPos:'b',showValue:true,dataLabelFontSize:9,dataLabelColor:INK,
  catAxisLabelFontSize:11,valAxisLabelFontSize:9,valGridLine:{style:'none'}});
const enCats=CL;
const enChart=[{name:'Actual',labels:enCats,values:enCats.map(c=>+aY(c,'energy').toFixed(0))},
               {name:'Budget',labels:enCats,values:enCats.map(c=>+bY(c,'energy').toFixed(0))}];
s.addText('Energy (non-fuel) charge (J$M)',{x:6.9,y:1.5,w:6,h:0.3,fontFace:BODY,bold:true,color:INK,fontSize:13});
s.addChart(p.ChartType.bar,enChart,{x:6.9,y:1.85,w:6.0,h:4.9,barDir:'col',chartColors:[NAVY,LBLUE],
  showLegend:true,legendPos:'b',showValue:true,dataLabelFontSize:9,dataLabelColor:INK,
  catAxisLabelFontSize:11,valAxisLabelFontSize:9,valGridLine:{style:'none'}});
s.addText('Demand revenue is concentrated in RT40 (power). Energy revenue is led by RT10 residential and RT20 commercial.',
  {x:0.5,y:6.95,w:12.3,h:0.4,fontFace:BODY,color:GREY,fontSize:12,italic:true});

// ---- Slide 3: Variance ----
s=p.addSlide(); s.background={color:'FFFFFF'};
s.addText('Variance — Actual vs Budget',{x:0.5,y:0.35,w:9,h:0.6,fontFace:HEAD,color:NAVY,fontSize:30,bold:true});
s.addText('Actual minus Budget (Feb LE), YTD through '+winlab+' · J$M ex-IPP · red = unfavourable',
  {x:0.5,y:1.0,w:12,h:0.35,fontFace:BODY,color:GREY,fontSize:13,italic:true});
const vlabs=AMON.map(m=>MLAB[m]);
const mvar=(k)=>AMON.map(m=>+CL.reduce((s2,c)=>s2+((A[c][k][m]||0)-(B[c][k][m]||0)),0).toFixed(0));
const vChart=[
  {name:'Demand',labels:vlabs,values:mvar('demand')},
  {name:'Energy',labels:vlabs,values:mvar('energy')},
  {name:'Revenue (ex-IPP)',labels:vlabs,values:mvar('rev')}];
s.addChart(p.ChartType.line,vChart,{x:0.5,y:1.6,w:8.0,h:5.2,chartColors:[RED,NAVY,GREEN],
  lineSize:2.75,lineSmooth:false,showLegend:true,legendPos:'b',
  catAxisLabelFontSize:12,valAxisLabelFontSize:9,valAxisTitle:'J$M (Actual − Budget)',showValAxisTitle:true,valGridLine:{style:'none'}});
// key reads
const fmt=n=>Math.abs(Math.round(n)).toLocaleString('en-US');
const totRev=CL.reduce((s2,c)=>s2+aY(c,'rev')-bY(c,'rev'),0);
const totDem=['RT40','RT50','RT70'].reduce((s2,c)=>s2+aY(c,'demand')-bY(c,'demand'),0);
const totVol=CL.reduce((s2,c)=>s2+aY(c,'vol')-bY(c,'vol'),0)/1000; // MWh->GWh
function card(y,lab,val,col){
  s.addShape(p.ShapeType.rect,{x:8.8,y:y,w:4.1,h:1.0,fill:{color:'F2F4F8'},line:{color:'D9DEE8',width:1}});
  s.addText(lab,{x:9.0,y:y+0.1,w:3.8,h:0.3,fontFace:BODY,color:GREY,fontSize:11,bold:true});
  s.addText(val,{x:9.0,y:y+0.38,w:3.8,h:0.5,fontFace:HEAD,color:col,fontSize:18,bold:true});
}
card(1.6,'Total revenue (ex-IPP) vs LE',(totRev>=0?'+':'−')+'J$'+fmt(totRev)+'M · ahead',totRev>=0?GREEN:RED);
card(2.8,'Demand charge vs LE',(totDem>=0?'+':'−')+'J$'+fmt(totDem)+'M · below (dilution)',totDem<0?RED:GREEN);
card(4.0,'Volume vs LE',(totVol>=0?'+':'−')+fmt(totVol)+' GWh',totVol>=0?GREEN:RED);
s.addText([{text:'Read: ',options:{bold:true}},
  {text:'revenue runs ahead of the Feb LE (+J$'+fmt(totRev)+'M) on stronger volume/energy, but the '},
  {text:'demand charge is below budget (−J$'+fmt(Math.abs(totDem))+'M)',options:{bold:true,color:RED}},
  {text:' — demand is fixed/capacity-based and does not scale with energy, so blended realization dilutes as volume grows. RT70 is the one revenue line behind plan.'}],
  {x:8.8,y:5.2,w:4.1,h:1.6,fontFace:BODY,color:INK,fontSize:11,valign:'top'});

p.writeFile({fileName:'JPS_Variance_Demand_Energy_Revenue.pptx'}).then(f=>console.log('wrote',f,'| window',WIN.join(',')));
