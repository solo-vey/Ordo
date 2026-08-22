const fs=require('fs'); const path=require('path');
const app=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
function assert(cond,msg){ if(!cond){ console.error('FAIL',msg); process.exit(1); } }
assert(app.includes('<div class="replay-print-shell">'),'print shell is neutral div');
assert(!app.includes('<main class="replay-print-shell">'),'legacy main print shell removed');
assert(app.includes('display:block!important;box-sizing:border-box;width:100%!important'),'print block width override');
console.log('PASS replay print grid isolation');
