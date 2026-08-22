const fs=require('fs'); const path=require('path');
const app=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
for (const t of ['print-color-adjust:exact','replay-bubble.analyst{background:#f1f1f1!important;border:1px solid #d6d6d6!important','replay-bubble.analyst .replay-values']) { if(!app.includes(t)){console.error('missing',t);process.exit(1);} }
console.log('PASS replay print analyst parity');
