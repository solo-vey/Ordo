const fs=require('fs'), path=require('path');
const app=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
const css=fs.readFileSync(path.join(__dirname,'..','web','styles.css'),'utf8');
function has(hay,x){if(!hay.includes(x)){console.error('missing',x);process.exit(1)}}
for(const x of ['dialog-step replay-step','dialog-step-head replay-step-head','replay-bubble assistant','replay-bubble analyst','replay-bubble gate']) has(app,x);
for(const x of ['R3 .81-dev — Show Path uses the same transcript visual language','#dialog-transcript .replay-bubble.analyst','#dialog-transcript .dialog-transition','#dialog-transcript .dialog-branch-choices']) has(css,x);
console.log('PASS Show Path transcript parity');
