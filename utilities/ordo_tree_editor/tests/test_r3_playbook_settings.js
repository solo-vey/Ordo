const fs=require('fs'), path=require('path');
const html=fs.readFileSync(path.join(__dirname,'..','web','index.html'),'utf8');
const js=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
for (const token of ['data-workspace-tab="settings"','id="playbook-settings-panel"','id="playbook-settings-list"']) {
  if(!html.includes(token)) throw new Error('missing '+token);
}
for (const token of ['renderPlaybookSettings','/api/playbook-settings','Allowed values','No enumerated alternatives are declared in the language registry.']) {
  if(!js.includes(token)) throw new Error('missing '+token);
}
console.log('PASS Playbook Settings UI contract');
