const fs=require('fs'), path=require('path');
const app=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
const html=fs.readFileSync(path.join(__dirname,'..','web','index.html'),'utf8');
const css=fs.readFileSync(path.join(__dirname,'..','web','styles.css'),'utf8');
for (const token of ['parsePlaybookPreparationFailure','renderPlaybookPreparationFailure','closePlaybookPreparation','What was found','What to do','event.key==="Escape"']) if(!app.includes(token)) throw new Error('missing '+token);
for (const token of ['playbook-preparation-summary','playbook-preparation-technical','Technical details']) if(!html.includes(token)) throw new Error('missing '+token);
if(!css.includes('playbook-preparation-human-lead')) throw new Error('missing human error css');
console.log('PASS human compilation error UI');
