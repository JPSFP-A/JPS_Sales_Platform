const fs=require('fs'),s=fs.readFileSync('D:/Projects/Sales_Platform/JPS_Sales_Platform_v1.html','utf8');
const lines=s.split('\n');
// Find _buildPrefixIdx calls + CUSTOMERS build + renderRsPar + mkBracketCharts
lines.forEach(function(l,i){
  if(/_buildPrefixIdx|CUSTOMERS\s*=|let CUSTOMERS|var CUSTOMERS|renderRsPar|mkBracketCharts|renderPfCust|renderPfInd|renderCmPivot|renderKamPerf|renderCmCust|renderCmIndTbl|renderFcKPIs|renderFcEntry|buildReconData|generateCommentary/.test(l) && !/\/\//.test(l.trim().slice(0,2)))
    console.log((i+1)+': '+l.trim().slice(0,120));
});
