const pptxgen=require('pptxgenjs'); const fs=require('fs');
const E=JSON.parse(fs.readFileSync('exec_data.json'));

// ── Palette — light, premium ──────────────────────────────────────────────────
const TEAL='0C3547';   // JPS deep teal — authority
const TEAL2='1A5F7A';  // mid teal for accents
const AMBER='D4920A';  // warm amber — accent
const AMLT='FEF3DC';   // amber tint (card bg)
const INK='0D1B2A';    // near-black
const BODY='374151';   // body text
const MUTED='6B7A99';  // muted labels
const BG='FFFFFF';     // white
const CARD='F6F8FB';   // off-white card
const BORDER='E4EAF2'; // very light border
const POS='027A48';    // deep green
const NEG='B91C1C';    // deep crimson

const p=new pptxgen();
p.defineLayout({name:'W',width:13.33,height:7.5}); p.layout='W';
const HEAD='Georgia', BODY_F='Calibri', MONO='Courier New';
const fmt=n=>(n>=0?'+':'−')+'J$'+Math.abs(n).toFixed(1)+'M';

const CATS=[
 ['IPP','IPP self-generation',"Independent power producers; Wigton's demand break (equipment failure) took effect in May.",'2E7D32'],
 ['Adjustment','Billing adjustments',"April-overstated corrections reversing — Musson (multiplier), Bay Juices (set-up), Hodges (demand write-off).",AMBER],
 ['Ratchet','Hurricane ratchet step-down',"Accounts billed on ratcheted demand; steps down each month toward ~80% of actual usage.",NEG],
 ['Operational','Operational changes',"Convenient Brands inactive, Playa RT50 idle, Gleaner site sold.",MUTED],
 ['Normal','Normal billing',"Usage in keeping with account pattern; included as top reviewed accounts.",TEAL2],
];

// ── Helpers ───────────────────────────────────────────────────────────────────
const rule=(s,x,y,w,col=AMBER,h=0.018)=>
  s.addShape(p.ShapeType.rect,{x,y,w,h,fill:{color:col},line:{color:col,width:0}});

// 4-corner bracket (all four corners) — elegant accent
function bracket(s,x,y,w,h,col,arm=0.3){
  const t=0.018;
  s.addShape(p.ShapeType.rect,{x,y,w:arm,h:t,fill:{color:col},line:{color:col,width:0}});
  s.addShape(p.ShapeType.rect,{x,y,w:t,h:arm,fill:{color:col},line:{color:col,width:0}});
  s.addShape(p.ShapeType.rect,{x:x+w-arm,y,w:arm,h:t,fill:{color:col},line:{color:col,width:0}});
  s.addShape(p.ShapeType.rect,{x:x+w-t,y,w:t,h:arm,fill:{color:col},line:{color:col,width:0}});
  s.addShape(p.ShapeType.rect,{x,y:y+h-t,w:arm,h:t,fill:{color:col},line:{color:col,width:0}});
  s.addShape(p.ShapeType.rect,{x,y:y+h-arm,w:t,h:arm,fill:{color:col},line:{color:col,width:0}});
  s.addShape(p.ShapeType.rect,{x:x+w-arm,y:y+h-t,w:arm,h:t,fill:{color:col},line:{color:col,width:0}});
  s.addShape(p.ShapeType.rect,{x:x+w-t,y:y+h-arm,w:t,h:arm,fill:{color:col},line:{color:col,width:0}});
}

function sHdr(s,pg,ttl,sub){
  s.background={color:BG};
  rule(s,0,0,13.33,AMBER,0.02);
  // Page indicator — monospace, small, top right
  s.addText((pg<10?'0'+pg:pg)+' / 06',
    {x:11.9,y:0.06,w:1.35,h:0.26,fontFace:MONO,color:AMBER,fontSize:9,align:'right',bold:true});
  // Title in JPS teal
  s.addText(ttl,{x:0.45,y:0.16,w:11.3,h:0.72,fontFace:HEAD,color:TEAL,fontSize:27,bold:true});
  // Subtitle
  if(sub) s.addText(sub,
    {x:0.45,y:0.93,w:12.5,h:0.3,fontFace:BODY_F,color:MUTED,fontSize:11.5,italic:true});
  // Thin teal bottom rule
  rule(s,0,7.46,13.33,TEAL,0.01);
}

// ── SLIDE 1 ─ Cover ───────────────────────────────────────────────────────────
let s=p.addSlide(); s.background={color:BG};

// Full-width amber stripe — very top (signature mark)
rule(s,0,0,13.33,AMBER,0.055);

// Diagonal geometric accent lines (subtle, thin)
s.addShape(p.ShapeType.rect,{x:-1,y:5.8,w:7.5,h:0.014,fill:{color:BORDER},line:{color:BORDER,width:0},rotate:-9});
s.addShape(p.ShapeType.rect,{x:4.5,y:1.1,w:12,h:0.011,fill:{color:BORDER},line:{color:BORDER,width:0},rotate:5});

// JPS identity block — top left
s.addText('JPS',{x:0.52,y:0.12,w:1.8,h:0.48,fontFace:HEAD,color:TEAL,bold:true,fontSize:22,charSpacing:3});
s.addText('FP&A  ·  SALES ANALYSIS',{x:0.52,y:0.62,w:6,h:0.28,fontFace:BODY_F,color:MUTED,fontSize:9.5,charSpacing:2.5});

// Huge two-tone title — teal + near-black for contrast
s.addText('SALES',{x:0.52,y:1.35,w:12.5,h:1.55,fontFace:HEAD,color:TEAL,fontSize:100,bold:true,charSpacing:10});
s.addText('VARIANCE.',{x:0.52,y:2.85,w:12.5,h:1.4,fontFace:HEAD,color:INK,fontSize:100,bold:true,charSpacing:5});

// Amber rule under title
rule(s,0.52,4.4,6.5,AMBER,0.022);

// "EXPLAINED" in spaced amber
s.addText('E X P L A I N E D',{x:0.52,y:4.54,w:8,h:0.58,fontFace:HEAD,color:AMBER,fontSize:22,charSpacing:10});

// Period badge with corner brackets
s.addText('APR → MAY  2026',{x:0.52,y:5.3,w:4.3,h:0.52,fontFace:MONO,color:TEAL,fontSize:14,bold:true,valign:'middle'});
bracket(s,0.44,5.2,4.45,0.7,AMBER,0.3);

// Thin rule + key finding
rule(s,0.52,6.18,9.8,BORDER,0.012);
s.addText([
  {text:'KEY FINDING   ',options:{color:TEAL,bold:true,fontSize:9.5,charSpacing:2,fontFace:MONO}},
  {text:'Demand fell on one-off factors (Wigton equipment break, ratchet step-down, April adjustment reversals) — offset by Alcoa IPP uplift. All drivers well-understood; no structural trend break.',
   options:{color:BODY,fontSize:11.5,fontFace:BODY_F}},
],{x:0.52,y:6.3,w:9.8,h:1.0,valign:'top'});

// Thin teal bottom rule
rule(s,0,7.46,13.33,TEAL,0.01);

// ── SLIDE 2 ─ Chart RIGHT, numbered callouts LEFT ─────────────────────────────
s=p.addSlide();
sHdr(s,2,'April → May movement by driver','Month-on-month change by cause — demand & revenue (J$M)');

// Corner-bracket numbered callouts — LEFT
const CALLS=[
  ['01',NEG,'Demand fell','Wigton demand break −J$8.8M (equipment failure) + ratchet step-down + April adjustment reversals (Hodges, Musson, Bay Juices).'],
  ['02',TEAL2,'Revenue mixed','Alcoa IPP up +J$32M and normal accounts higher, offset by April-overstated adjustments reversing (Musson −J$12M).'],
  ['03',POS,'Net read','Almost all MoM movement is one-off — adjustments, demand break, ratchet unwind, IPP self-gen. No structural trend break.'],
];
let cy=1.42;
CALLS.forEach((c,i)=>{
  bracket(s,0.45,cy,0.72,0.62,c[1],0.22);
  s.addText(c[0],{x:0.45,y:cy+0.04,w:0.72,h:0.54,fontFace:MONO,color:c[1],bold:true,fontSize:17,align:'center',valign:'middle'});
  s.addText(c[2].toUpperCase(),{x:1.3,y:cy+0.06,w:3.55,h:0.42,fontFace:BODY_F,bold:true,color:c[1],fontSize:13,charSpacing:1});
  s.addText(c[3],{x:0.45,y:cy+0.76,w:4.3,h:1.06,fontFace:BODY_F,color:BODY,fontSize:11,valign:'top'});
  cy+=1.9;
  if(i<2) rule(s,0.45,cy-0.12,4.35,BORDER,0.01);
});

// Chart RIGHT — clean white background
s.addChart(p.ChartType.bar,[
  {name:'Δ Demand',labels:CATS.map(c=>c[1].split(' ').slice(0,2).join(' ')),
   values:CATS.map(c=>+(E.cats[c[0]]?E.cats[c[0]].dem:0).toFixed(1))},
  {name:'Δ Revenue',labels:CATS.map(c=>c[1].split(' ').slice(0,2).join(' ')),
   values:CATS.map(c=>+(E.cats[c[0]]?E.cats[c[0]].rev:0).toFixed(1))},
],{
  x:4.92,y:1.38,w:8.2,h:5.8,
  barDir:'col',chartColors:[NEG,TEAL2],
  chartArea:{fill:{color:BG}},
  plotArea:{fill:{color:BG}},
  catAxisLabelColor:MUTED,valAxisLabelColor:MUTED,
  showLegend:true,legendPos:'b',legendColor:MUTED,
  showValue:true,dataLabelColor:INK,dataLabelFontSize:9,
  catAxisLabelFontSize:10,valAxisLabelFontSize:9,
  valAxisTitle:'J$M (May − April)',showValAxisTitle:true,
  valGridLine:{color:BORDER,style:'dash',width:0.5},
});

// ── SLIDE 3 ─ By driver — horizontal bands, light theme ───────────────────────
s=p.addSlide();
sHdr(s,3,'By driver — accounts behind each','Apr → May change per account (J$M) · demand & revenue');

const byCat={}; E.rows.forEach(r=>{(byCat[r.cat]=byCat[r.cat]||[]).push(r);});

const BAND_H=1.14, Y0=1.32;
CATS.forEach((c,i)=>{
  const y=Y0+i*BAND_H;
  const bg=i%2===0?BG:CARD;
  s.addShape(p.ShapeType.rect,{x:0,y,w:13.33,h:BAND_H,fill:{color:bg},line:{color:bg,width:0}});
  // Left accent bar
  s.addShape(p.ShapeType.rect,{x:0,y,w:0.07,h:BAND_H,fill:{color:c[3]},line:{color:c[3],width:0}});
  // Category label — monospace small-caps feel
  s.addText(c[1].toUpperCase(),{x:0.2,y:y+0.09,w:2.2,h:0.3,fontFace:MONO,color:c[3],bold:true,fontSize:9,charSpacing:1.5});
  // Totals
  const cat=E.cats[c[0]]||{dem:0,rev:0};
  s.addText('Dem '+fmt(cat.dem),{x:0.2,y:y+0.49,w:1.15,h:0.26,fontFace:MONO,color:cat.dem>=0?POS:NEG,fontSize:8.5,bold:true});
  s.addText('Rev '+fmt(cat.rev),{x:1.38,y:y+0.49,w:1.1,h:0.26,fontFace:MONO,color:cat.rev>=0?POS:NEG,fontSize:8.5,bold:true});
  // Thin vertical rule between label and accounts
  s.addShape(p.ShapeType.rect,{x:2.55,y:y+0.14,w:0.01,h:BAND_H-0.28,fill:{color:BORDER},line:{color:BORDER,width:0}});
  // Up to 4 accounts
  const accs=(byCat[c[0]]||[]).sort((a,b)=>Math.abs(b.dem)-Math.abs(a.dem)).slice(0,4);
  accs.forEach((a,ai)=>{
    const ax=2.7+ai*2.65;
    s.addText(a.name.split(' ').slice(0,3).join(' ').slice(0,20),
      {x:ax,y:y+0.09,w:2.5,h:0.3,fontFace:BODY_F,color:INK,fontSize:10.5,bold:true,valign:'top'});
    s.addText(fmt(a.dem),
      {x:ax,y:y+0.48,w:2.5,h:0.28,fontFace:MONO,color:a.dem>=0?POS:NEG,fontSize:11,bold:true});
    const rv=E.rows.find(r2=>r2.name===a.name)||{rev:0};
    s.addText('Rev '+fmt(rv.rev),
      {x:ax,y:y+0.82,w:2.5,h:0.22,fontFace:BODY_F,color:MUTED,fontSize:9});
  });
  if(i<CATS.length-1) rule(s,0,y+BAND_H-0.01,13.33,BORDER,0.01);
});

// ── SLIDE 4 ─ Revenue quality table ──────────────────────────────────────────
s=p.addSlide();
sHdr(s,4,'Revenue quality — demand vs energy divergence',
  'Inside "Normal billing": revenue (ex-fuel) rose while billed demand fell or was flat.');

const dil=(E.divergence||[]).filter(r=>r.rev>0&&r.dem<=0.2&&!r.name.toLowerCase().includes('alcoa'));
const dt=(t,o)=>({text:t,options:Object.assign({fontFace:BODY_F,fontSize:11.5,valign:'middle'},o||{})});
const hFill={bold:true,color:'FFFFFF',fill:TEAL,charSpacing:0.8,fontFace:BODY_F,fontSize:10.5};
const t2=[[dt('Account',hFill),dt('Class',Object.assign({},hFill,{align:'center'})),
  dt('Δ Rev x-fuel',Object.assign({},hFill,{align:'center'})),
  dt('Δ Demand',Object.assign({},hFill,{align:'center'})),
  dt('Δ Energy',Object.assign({},hFill,{align:'center'})),
  dt('Δ IPP',Object.assign({},hFill,{align:'center'}))]];
dil.forEach((r,i)=>{
  const bg=i%2?CARD:BG;
  t2.push([dt(r.name.slice(0,30),{fill:bg,bold:true,color:INK}),
    dt(r.cls,{fill:bg,align:'center',color:MUTED,fontSize:10}),
    dt(fmt(r.rev),{fill:bg,align:'center',color:POS,bold:true,fontFace:MONO}),
    dt(fmt(r.dem),{fill:bg,align:'center',color:r.dem<0?NEG:INK,bold:true,fontFace:MONO}),
    dt(fmt(r.energy),{fill:bg,align:'center',color:BODY,fontFace:MONO}),
    dt(fmt(r.ipp),{fill:bg,align:'center',color:BODY,fontFace:MONO})]);
});
s.addTable(t2,{x:0.28,y:1.42,w:12.5,colW:[3.6,1.9,2.1,1.7,1.6,1.6],
  border:{type:'solid',color:BORDER,pt:0.5},rowH:0.5});

const ny=1.42+(dil.length+1)*0.5+0.28;
// Why it matters — white card, amber left bar
s.addShape(p.ShapeType.rect,{x:0.28,y:ny,w:7.6,h:1.62,fill:{color:AMLT},line:{color:BORDER,width:0.5}});
s.addShape(p.ShapeType.rect,{x:0.28,y:ny,w:0.07,h:1.62,fill:{color:AMBER},line:{color:AMBER,width:0}});
s.addText([{text:'WHY IT MATTERS   ',options:{bold:true,color:AMBER,charSpacing:1.5,fontFace:MONO,fontSize:9}},
  {text:'Demand is the capacity charge — the margin. Revenue rising while demand falls means accounts are consuming more energy but billing is not capturing it in capacity charges. Investigate load-factor shift, ratchet application, or multiplier settings.',
   options:{fontFace:BODY_F,color:BODY}}],
  {x:0.48,y:ny+0.12,w:7.25,h:1.38,fontSize:11.5,valign:'top'});
// Alcoa callout
const aa=E.alcoa_adj||{rev:0,adj:0,comp:0};
s.addShape(p.ShapeType.rect,{x:8.1,y:ny,w:4.7,h:1.62,fill:{color:CARD},line:{color:AMBER,width:0.75}});
s.addShape(p.ShapeType.rect,{x:8.1,y:ny,w:0.07,h:1.62,fill:{color:AMBER},line:{color:AMBER,width:0}});
s.addText([{text:'ALCOA FLAG   ',options:{bold:true,color:AMBER,charSpacing:1.5,fontFace:MONO,fontSize:9}},
  {text:"Of the "+fmt(aa.rev)+" revenue (ex-fuel) jump, ~"+fmt(aa.adj)+" appears to be a billing adjustment (only "+fmt(aa.comp)+" from energy/demand/IPP). Confirm the true-up nature before treating as a trend.",
   options:{fontFace:BODY_F,color:BODY}}],
  {x:8.3,y:ny+0.12,w:4.35,h:1.38,fontSize:11.5,valign:'top'});

// ── SLIDE 5 ─ Two-column: movers | revenue quality flags ─────────────────────
s=p.addSlide();
sHdr(s,5,'Areas flagged for investigation','Left: large MoM movers (unreviewed).  Right: revenue quality alerts.');

s.addText('// LARGE MOVERS',{x:0.45,y:1.35,w:5.7,h:0.3,fontFace:MONO,bold:true,color:TEAL,fontSize:9,charSpacing:2});
rule(s,0.45,1.67,5.7,TEAL,0.015);

// Amber vertical divider
s.addShape(p.ShapeType.rect,{x:6.28,y:1.3,w:0.03,h:5.98,fill:{color:AMBER},line:{color:AMBER,width:0}});

s.addText('// REVENUE FLAGS',{x:6.58,y:1.35,w:6.5,h:0.3,fontFace:MONO,bold:true,color:NEG,fontSize:9,charSpacing:2});
rule(s,6.58,1.67,6.5,NEG,0.015);

// Left movers — clean rows, thin separator only
(E.investigate||[]).forEach((r,i)=>{
  const y=1.78+i*0.89;
  const demC=r.dem>=0?POS:NEG, revC=r.rev>=0?POS:NEG;
  s.addText(r.name.slice(0,26),{x:0.45,y:y+0.04,w:3.85,h:0.28,fontFace:BODY_F,bold:true,color:INK,fontSize:10.5});
  s.addText(r.cls,{x:4.3,y:y+0.04,w:1.85,h:0.28,fontFace:BODY_F,color:MUTED,fontSize:9.5,align:'right'});
  s.addText(fmt(r.dem),{x:0.45,y:y+0.4,w:2.8,h:0.27,fontFace:MONO,fontSize:10.5,bold:true,color:demC});
  s.addText(fmt(r.rev),{x:3.35,y:y+0.4,w:2.8,h:0.27,fontFace:MONO,fontSize:10.5,bold:true,color:revC,align:'right'});
  if(i<(E.investigate||[]).length-1) rule(s,0.45,y+0.8,5.7,BORDER,0.01);
});

// Right revenue flags — minimal card, left accent
const dilNamed=(E.divergence||[]).filter(r=>r.rev>0&&r.dem<=0.2&&!r.name.toLowerCase().includes('alcoa'));
dilNamed.forEach((r,i)=>{
  const y=1.78+i*1.37;
  s.addShape(p.ShapeType.rect,{x:6.58,y,w:6.5,h:1.28,fill:{color:CARD},line:{color:BORDER,width:0.5}});
  s.addShape(p.ShapeType.rect,{x:6.58,y,w:0.06,h:1.28,fill:{color:NEG},line:{color:NEG,width:0}});
  s.addText(r.name.slice(0,28),{x:6.76,y:y+0.08,w:4.55,h:0.3,fontFace:BODY_F,bold:true,color:INK,fontSize:11.5});
  s.addText(r.cls,{x:11.28,y:y+0.08,w:1.7,h:0.3,fontFace:BODY_F,color:MUTED,fontSize:9.5,align:'right'});
  s.addText('Rev '+fmt(r.rev)+'   ·   Dem '+fmt(r.dem)+'   ·   Energy '+fmt(r.energy),
    {x:6.76,y:y+0.45,w:6.15,h:0.28,fontFace:MONO,color:INK,fontSize:10,bold:true});
  s.addText('Revenue up, demand flat/down — capacity charge not keeping pace (see slide 4)',
    {x:6.76,y:y+0.8,w:6.15,h:0.38,fontFace:BODY_F,color:NEG,fontSize:9.5,italic:true});
});

// ── SLIDE 6 ─ Outlook: 2×2 light quadrants with corner brackets ──────────────
s=p.addSlide(); s.background={color:BG};
rule(s,0,0,13.33,AMBER,0.022);
s.addText('06 / 06',{x:11.9,y:0.06,w:1.35,h:0.26,fontFace:MONO,color:AMBER,fontSize:9,align:'right',bold:true});
s.addText('What it means / outlook',{x:0.45,y:0.16,w:12.0,h:0.75,fontFace:HEAD,color:TEAL,fontSize:30,bold:true});
rule(s,0.45,1.0,12.4,BORDER,0.01);

[['ONE-OFF',AMBER,"Wigton's demand break and April-overstated adjustments (Musson, Bay Juices, Hodges) are corrections. They reverse naturally — not run-rate."],
 ['TEMPORARY',NEG,"Hurricane-ratchet accounts (Bay Roc, X Fund, Seawind, the bakeries) step down each month until demand settles at ~80% of actual."],
 ['STRUCTURAL-BY-DESIGN','2E7D32',"IPP accounts (Alcoa, Wigton, JPPC, West Kingston, JEP, Content Solar) swing with self-generation; Alcoa lifted May revenue as self-gen fell."],
 ['TO INVESTIGATE',TEAL2,"A set of large accounts moved materially MoM outside the reviewed list. Assign for explanation before next reporting cycle (see slide 5)."]
].forEach((pt,i)=>{
  const col=i%2, row=Math.floor(i/2);
  const x=0.45+col*6.55, y=1.12+row*3.1;
  const qw=6.2, qh=2.88;
  // White card with very light border
  s.addShape(p.ShapeType.rect,{x,y,w:qw,h:qh,fill:{color:CARD},line:{color:BORDER,width:0.75}});
  // Thin coloured top strip
  s.addShape(p.ShapeType.rect,{x,y,w:qw,h:0.06,fill:{color:pt[1]},line:{color:pt[1],width:0}});
  // Corner brackets in the accent colour
  bracket(s,x,y,qw,qh,pt[1],0.35);
  // Category label — monospace, small, colour
  s.addText(pt[0],{x:x+0.22,y:y+0.2,w:qw-0.44,h:0.36,fontFace:MONO,bold:true,color:pt[1],fontSize:11,charSpacing:2.5});
  // Body text — readable dark grey
  s.addText(pt[2],{x:x+0.22,y:y+0.72,w:qw-0.44,h:2.0,fontFace:BODY_F,color:BODY,fontSize:12.5,valign:'top'});
});

rule(s,0,7.46,13.33,TEAL,0.01);

p.writeFile({fileName:'JPS_Sales_Variance_Explained_Exec.pptx'}).then(f=>console.log('wrote',f));
