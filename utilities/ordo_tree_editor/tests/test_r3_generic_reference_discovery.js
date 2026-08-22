const fs=require('fs'), path=require('path');
const app=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
for(const token of ['pathPattern','Object.values(value).some(walk)','templateCapableRecord']) {
  if(!app.includes(token)){ console.error('missing',token); process.exit(1); }
}
console.log('PASS generic reference discovery UI contract');
