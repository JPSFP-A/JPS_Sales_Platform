const fs=require('fs'),s=fs.readFileSync('D:/Projects/Sales_Platform/JPS_Sales_Platform_v1.html','utf8');
const lines=s.split('\n');
// Find syncSupabase function
let inSync=false,start=0;
lines.forEach(function(l,i){
  if(!inSync && /async function syncSupabase/.test(l)){inSync=true;start=i+1;console.log('syncSupabase starts at line '+(i+1));}
  if(inSync && i>start+5 && /^async function|^function /.test(l.trim())){inSync=false;console.log('syncSupabase ends at line '+(i+1));}
});
// Also find where sbActuals is assigned
lines.forEach(function(l,i){
  if(/sbActuals\s*=|let sbActuals|var sbActuals|const sbActuals/.test(l))
    console.log('sbActuals assign line '+(i+1)+': '+l.trim().slice(0,120));
});
