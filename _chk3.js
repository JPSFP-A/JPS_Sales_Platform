const fs=require('fs'),src=fs.readFileSync('D:/Projects/Sales_Platform/JPS_Sales_Platform_v1.html','utf8');
// Find all <script> occurrences
var idx=src.indexOf('<script');
var count=0;
while(idx!==-1){
  count++;
  var end=src.indexOf('>',idx);
  console.log('script tag at',idx,':',src.slice(idx,end+1).slice(0,80));
  idx=src.indexOf('<script',idx+1);
  if(count>10)break;
}
