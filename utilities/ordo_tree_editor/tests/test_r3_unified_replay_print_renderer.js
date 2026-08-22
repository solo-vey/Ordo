const fs=require('fs');
const path=require('path');
const app=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
function assert(v,m){if(!v){console.error('FAIL',m);process.exit(1)}}
assert(app.includes("document.querySelector('link[rel=\"stylesheet\"]')?.href"),'print uses active stylesheet');
assert(app.includes('class="replay-print-document"'),'print document class');
assert(app.includes('class="replay-print-shell"'),'print shell');
assert(app.includes('<div id="replay-header">${replayHeader.innerHTML}</div>'),'same replay header DOM');
assert(app.includes('<div class="replay-note">${replayNote.innerHTML}</div>'),'same replay note DOM');
assert(app.includes('<div id="replay-transcript">${transcript.innerHTML}</div>'),'same replay transcript DOM');
assert(app.includes('.replay-step,.replay-bubble,.replay-values{break-inside:auto!important'),'continuous page flow');
assert(!app.includes('body{font:14px/1.5 Arial,sans-serif;color:#172033;max-width:900px'),'legacy standalone print visual CSS removed');
console.log('PASS unified replay/print renderer');
