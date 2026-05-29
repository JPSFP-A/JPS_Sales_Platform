const fs=require('fs'),s=fs.readFileSync('D:/Projects/Sales_Platform/JPS_Sales_Platform_v1.html','utf8');
const lines=s.split('\n');
lines.forEach(function(l,i){
  if(/SCORECARD_DATA|renderScorecard|scorecard_table|es_score/.test(l))
    console.log((i+1)+': '+l.trim().slice(0,120));
});
