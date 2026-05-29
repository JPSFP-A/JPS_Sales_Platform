const fs=require('fs'),s=fs.readFileSync('D:/Projects/Sales_Platform/JPS_Sales_Platform_v1.html','utf8');
const lines=s.split('\n');
const hits=[];
lines.forEach(function(l,i){
  if(/syncSupabase|jps_actuals|rate_class|RT10|RT20|\.from\(|\.select\(|segment/.test(l))
    hits.push((i+1)+': '+l.trim().slice(0,140));
});
console.log(hits.slice(0,100).join('\n'));
