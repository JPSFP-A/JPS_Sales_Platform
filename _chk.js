const fs=require('fs'),src=fs.readFileSync('D:/Projects/Sales_Platform/JPS_Sales_Platform_v1.html','utf8');
const scripts=[],re=/<script[^>]*>([\s\S]*?)<\/script>/gi;let m;
while((m=re.exec(src))!==null){if(!m[0].includes('src='))scripts.push(m[1]);}
try{new(require('vm').Script)(scripts.join('\n'));console.log('SYNTAX OK',scripts.join('').length);}
catch(e){console.log('ERR:',e.message);}
