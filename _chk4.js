const fs=require('fs'),src=fs.readFileSync('D:/Projects/Sales_Platform/JPS_Sales_Platform_v1.html','utf8');
// Extract JS between the two large script blocks more carefully
// Find all inline script blocks (no src=) and join them
var results=[];
var pos=0;
while(pos<src.length){
  var start=src.indexOf('<script',pos);
  if(start===-1)break;
  var tagEnd=src.indexOf('>',start);
  if(tagEnd===-1)break;
  var tag=src.slice(start,tagEnd+1);
  if(!tag.includes('src=')){
    // Find the matching </script> — careful not to stop at embedded </script> in strings
    var contentStart=tagEnd+1;
    var closeTag=src.indexOf('</script>',contentStart);
    if(closeTag!==-1){
      results.push(src.slice(contentStart,closeTag));
      pos=closeTag+9;
    } else break;
  } else {
    pos=tagEnd+1;
  }
}
console.log('Script blocks:',results.length,'total chars:',results.join('').length);
// Try parsing
try{
  new(require('vm').Script)(results.join('\n'));
  console.log('SYNTAX OK');
}catch(e){
  console.log('ERR:',e.message);
}
