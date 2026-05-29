const fs=require('fs'),s=fs.readFileSync('D:/Projects/Sales_Platform/JPS_Sales_Platform_v1.html','utf8');
const lines=s.split('\n');
// Find all uses of sbActuals with context
lines.forEach(function(l,i){
  if(/sbActuals/.test(l) && !/\/\//.test(l.trim().slice(0,2))){
    // Get surrounding function name (look back up to 30 lines)
    var fn='?';
    for(var j=i-1;j>Math.max(0,i-30);j--){
      var m=lines[j].match(/^(?:async )?function (\w+)/);
      if(m){fn=m[1];break;}
    }
    console.log('L'+(i+1)+' ['+fn+']: '+l.trim().slice(0,100));
  }
});
