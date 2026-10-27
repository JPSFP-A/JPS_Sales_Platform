# -*- coding: utf-8 -*-
# Make operational adjustments roll forward in the Driver Forecast engine.
#   - Structural reasons (confirmed/possible defection, expansion, renewal, win-back) stay in force from the month entered
#     until the next entry for the account; an entry of 0% and 0 kWh ends it.
#   - Other reasons (operational disruption, other, unstated) apply to the months entered only.
#   - The adjustment is applied on top of an unadjusted rolling base, so it no longer feeds back into the base and cannot compound.
import sys
p = r'C:\Projects\Sales_Platform\JPS_Sales_Platform_v1.html'
s = open(p, encoding='utf-8').read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (old[:80], n)
    s = s.replace(old, new)

# 1. lookup helpers (after the old lookup, which stays for reference by nothing else)
rep("""  return row?{pct:Number(row.operational_pct)||0,kwh:Number(row.manual_kwh)||0}:{pct:0,kwh:0};
}
function _dfcDriverPcts(""", """  return row?{pct:Number(row.operational_pct)||0,kwh:Number(row.manual_kwh)||0}:{pct:0,kwh:0};
}
// Adjustments roll forward. An entry with a structural reason stays in force from the month it is
// entered until the next entry for the account; an entry of 0% and 0 kWh ends it. Every other reason
// (operational disruption, other, unstated) applies to the months entered only.
const _DFC_OP_ROLLS=new Set(['Confirmed defection','Possible defection','Expansion','Renewal','Win-back']);
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
function _dfcDriverPcts(""")

# 2. chain: unadjusted base, adjustment overlaid
rep("""  const totals={};
  for(let m=1;m<=asof;m++){
    const act=actMap?actMap[`${year}_${m}`]:undefined;
    totals[m]={total:act||0,isActual:true};
  }""", """  const totals={};
  const opEntries=opAc?_dfcOpEntries(opAc):[];
  for(let m=1;m<=asof;m++){
    const act=actMap?actMap[`${year}_${m}`]:undefined;
    totals[m]={total:act||0,baseTotal:act||0,isActual:true};
  }""")
rep("if(mm>=1&&totals[mm])terms.push(totals[mm].total);", "if(mm>=1&&totals[mm])terms.push(totals[mm].baseTotal);")
rep("const op=opAc?_dfcOpAdjLookup(opAc,year,m):{pct:0,kwh:0};", "const op=opAc?_dfcOpEffective(opEntries,year,m):{pct:0,kwh:0};")
rep("""    const total=base*(1+_drvSum/100)+op.kwh;
    totals[m]={total,isActual:false,base,""", """    const total=base*(1+_drvSum/100)+op.kwh;
    // The base is built from UNADJUSTED totals, so an adjustment never feeds back into it and cannot compound.
    const baseTotal=base*(1+Math.max(-100, macro+weather+seasInd+solar+(norm||0)+(migration||0))/100);
    totals[m]={total,baseTotal,isActual:false,base,""")

# 3. cross-year carry uses the unadjusted tail; the adjustment itself carries the level shift
rep("    const pv=m=>prior[m]?(prior[m].total||0):0;", "    const pv=m=>prior[m]?((prior[m].baseTotal!=null?prior[m].baseTotal:prior[m].total)||0):0;")
rep("const annualAvg=Object.values(prior).reduce((s,v)=>s+(v.total||0),0)/12;", "const annualAvg=Object.values(prior).reduce((s,v)=>s+((v.baseTotal!=null?v.baseTotal:v.total)||0),0)/12;")
rep("    // Carry the prior year's Oct/Nov/Dec tail forward -- that tail is what preserves a\n    // PERMANENT LEVEL SHIFT (a confirmed mid-year defection like Alcoa RT70 going 100%\n    // self-generating from Aug-2026 must stay gone in FY2027, not be averaged back in).",
    "    // Carry the prior year's Oct/Nov/Dec UNADJUSTED tail forward. A permanent level shift (a\n    // confirmed defection like Alcoa RT70 self-generating from Aug-2026) is no longer carried by\n    // this tail: the defection entry rolls forward and is applied on top of the base each month.")

# 4. cache signature must see the reason code
rep("b+=r.jps_ac+'|'+r.year+'|'+r.month+'|'+r.operational_pct+'|'+r.manual_kwh+';';}", "b+=r.jps_ac+'|'+r.year+'|'+r.month+'|'+r.operational_pct+'|'+r.manual_kwh+'|'+r.reason_code+';';}")

# 5. edit modal and header notes
_marker = "is changing to <strong>${pct>0?'+':''}${pct}%</strong>. Every non-zero change needs a reason before it saves.\n    </div>\n    <label style=\"font-size:10px;color:var(--text3);text-transform:uppercase\">Reason code</label>\n    <select id=\"dfc_reason_code\""
rep(_marker, _marker.replace("\n    <label", "\n    <div style=\"font-size:11px;color:var(--text3);margin-bottom:10px\">Confirmed or possible defection, expansion, renewal and win-back stay in force from this month until the next entry for the account. Enter 0% to end one. Operational disruption and Other apply to this month only.</div>\n    <label", 1))
rep("""   Base(month) = avg of the prior 3 months' Total (actual where closed,
   adjusted forecast where open) — a chain, not a lookup.""", """   Base(month) = avg of the prior 3 months' UNADJUSTED total (actual where closed,
   unadjusted forecast where open) — a chain, not a lookup. Operational adjustments
   are applied on top of that base and, for structural reasons, roll forward.""")
open(p, 'w', encoding='utf-8').write(s)
print('patched platform')
