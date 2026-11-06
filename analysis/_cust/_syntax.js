function _dfcOpEntries(ac){
  const seen=new Set(),out=[];
  sbOpAdj.forEach(r=>{
    const rac=String(r.jps_ac||'');
    if(!(rac===ac||rac===String(ac).split('-')[0]||String(ac)===rac.split('-')[0]))return;
    const pct=Number(r.operational_pct)||0,kwh=Number(r.manual_kwh)||0;
    const t=Number(r.year)*12+Number(r.month);
    const roll=_DFC_OP_ROLLS.has(r.reason_code)||(pct===0&&kwh===0);
    const k=(roll?'R':'M')+t;
    if(seen.has(k))return;seen.add(k);
    out.push({t,pct,kwh,roll});
  });
  return out.sort((a,b)=>a.t-b.t);
}
function _dfcOpEffective(entries,year,month){
  const t=year*12+month;let pct=0,kwh=0,last=null;
  for(const e of entries){
    if(e.t>t)break;
    if(e.roll)last=e;                       // latest rolling entry at or before this month
    else if(e.t===t){pct+=e.pct;kwh+=e.kwh;} // month-only entries
  }
  if(last){pct+=last.pct;kwh+=last.kwh;}
  return{pct,kwh};
}
function _dfcComputeChain(idx,key,isAccount,driverCtx,opAc,year,asof,newCustCtx,carryIn){
  const actMap=(isAccount?idx.actByAc:idx.actByCohort)[key];
  const budMap=(isAccount?idx.budByAc:idx.budByCohort)[key];
  const totals={};
  const opEntries=opAc?_dfcOpEntries(opAc):[];
  for(let m=1;m<=asof;m++){
    const act=actMap?actMap[`${year}_${m}`]:undefined;
    totals[m]={total:act||0,baseTotal:act||0,isActual:true};
  }
  for(let m=asof+1;m<=12;m++){
    let base;
    if(newCustCtx&&(year<newCustCtx.startYear||(year===newCustCtx.startYear&&m<newCustCtx.startMonth))){
      base=0;
    }else if(newCustCtx){
      base=newCustCtx.expectedKwh;
    }else{
      const terms=[];
      for(let k=1;k<=3;k++){
        const mm=m-k;
        if(mm>=1&&totals[mm])terms.push(totals[mm].baseTotal);
        else if(mm<=0&&carryIn&&carryIn[mm]!=null)terms.push(carryIn[mm]);
      }
      const budFallback=budMap?budMap[`${year}_${m}`]:undefined;
      base=terms.length?terms.reduce((s,v)=>s+v,0)/terms.length:(budFallback||0);
    }
    // Bucket for seasonality lookup: cohort keys are rate_class|parish|bucket so
    // cohorts self-derive from their own key; accounts pass a bucket snapshot in
    // driverCtx (may be absent — falls back to the class-wide index row).
    const bucket=driverCtx.bucket!==undefined?driverCtx.bucket:(!isAccount?(String(key).split('|')[2]||null):null);
    let{macro,weather,seasInd,norm,migration}=_dfcDriverPcts(driverCtx.rate_class,driverCtx.industry,year,m,bucket);
    // Storm-recovery normalisation is keyed by rate class, so without this it lands on
    // every account in the class. Caribbean Cement is ~a third of RT50 and was never a
    // storm-affected load -- its 2026 volume ROSE while the rest of RT50 fell -- so the
    // recovery uplift does not belong on it. Excluded accounts keep every other driver.
    if(norm&&opAc&&_DFC_NORM_EXCLUDE.has(String(opAc)))norm=0;
    const solar=_dfcSolarPct(driverCtx.rate_class,year,m);
    const op=opAc?_dfcOpEffective(opEntries,year,m):{pct:0,kwh:0};
    // Percentage drivers stack without a bound, so a combination of macro, weather,
    // seasonality, solar, normalisation and an operational cut can exceed -100% and
    // drive an otherwise-positive base below zero -- a modelling artefact, not a real
    // customer position. Clamp the SUM at -100% (a total wipeout, never a reversal).
    // Accounts that are genuinely negative are negative because their BASE is negative
    // (net billers exporting more than they import); the clamp leaves those untouched.
    const _drvSum=Math.max(-100, macro+weather+seasInd+solar+(norm||0)+(migration||0)+op.pct);
    const total=base*(1+_drvSum/100)+op.kwh;
    // The base is built from UNADJUSTED totals, so an adjustment never feeds back into it and cannot compound.
    const baseTotal=base*(1+Math.max(-100, macro+weather+seasInd+solar+(norm||0)+(migration||0))/100);
    totals[m]={total,baseTotal,isActual:false,base,macro,weather,seasInd,solar,norm:norm||0,migration:migration||0,oper:op.pct,manual:op.kwh,drvClamped:_drvSum<=-100};
  }
  return totals;
}
function _dfcGetChain(idx,key,isAccount,driverCtx,opAc,year,newCustCtx){
  const cacheKey=`${year}|${key}|${isAccount}|${opAc||''}`;
  if(_dfcYearChainCache[cacheKey])return _dfcYearChainCache[cacheKey];
  let lockedThru=0,carryIn=null;
  if(year===FC_BUD_YEAR){
    lockedThru=_dfcClosedThru(year);
  }else if(year>FC_BUD_YEAR){
    // Carry the prior year's Oct/Nov/Dec UNADJUSTED tail forward. A permanent level shift (a
    // confirmed defection like Alcoa RT70 self-generating from Aug-2026) is no longer carried by
    // this tail: the defection entry rolls forward and is applied on top of the base each month.
    // For residential (RT10/RT20) only, deseasonalise that tail first: Oct-Dec is the
    // winter consumption peak, so carrying it forward flat inflated every month of the new
    // year by that margin. Dividing by the tail's own uplift vs the year's average converts
    // it to annual-average-equivalent terms. Commercial classes are left on the raw tail --
    // they are weakly seasonal, and a self-computed factor there would divide a
    // defection-collapsed tail by its own collapse and resurrect the lost load.
    const prior=_dfcGetChain(idx,key,isAccount,driverCtx,opAc,year-1,newCustCtx);
    const pv=m=>prior[m]?((prior[m].baseTotal!=null?prior[m].baseTotal:prior[m].total)||0):0;
    const rcSeg=String(driverCtx.rate_class||'');
    let f=1;
    if(rcSeg==='RT10'||rcSeg==='RT20'){
      const annualAvg=Object.values(prior).reduce((s,v)=>s+((v.baseTotal!=null?v.baseTotal:v.total)||0),0)/12;
      const tailAvg=(pv(10)+pv(11)+pv(12))/3;
      if(annualAvg>0&&tailAvg>0)f=tailAvg/annualAvg;
    }
    carryIn={0:pv(12)/f,'-1':pv(11)/f,'-2':pv(10)/f};
  }
  const chain=_dfcComputeChain(idx,key,isAccount,driverCtx,opAc,year,lockedThru,newCustCtx,carryIn);
  _dfcYearChainCache[cacheKey]=chain;
  return chain;
}
console.log("syntax ok");