const fs=require('fs'); const path=require('path');
const css=fs.readFileSync(path.join(__dirname,'..','web','styles.css'),'utf8');
for(const t of ['R3 .75-dev — single-scroll resource preview','max-height:none','overflow:visible']){if(!css.includes(t)){console.error('missing',t);process.exit(1)}}
console.log('PASS single-scroll resource preview');
