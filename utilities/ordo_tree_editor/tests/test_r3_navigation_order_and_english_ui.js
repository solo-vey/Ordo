const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'web/index.html'),'utf8');
const js=fs.readFileSync(path.join(root,'web/app.js'),'utf8');
const apiGuide=fs.readFileSync(path.join(root,'web/api-docs/execute-playbook.html'),'utf8');
function must(v,m){if(!v)throw new Error(m);}
const tabs=[...html.matchAll(/data-workspace-tab="([^"]+)"/g)].map(m=>m[1]);
const expected=['upload','tree','lineage','settings','verification','packagefiles','paths','chat','replay','modelchat','help'];
must(JSON.stringify(tabs)===JSON.stringify(expected),`workspace order mismatch: ${JSON.stringify(tabs)}`);
must((html.match(/class="workspace-tab-separator"/g)||[]).length===3,'main navigation must contain three visual group separators');
for(const token of [
  'const HELP_NAV_GROUPS = [',
  '["getting-started"]',
  '["show-tree","show-data-flow","playbook-settings","verify-playbook","files"]',
  '["show-path","execute-playbook","replay-real-chat","auto-answers","current-state","pause-resume","recovery","evidence"]',
  '["model-chat","settings","troubleshooting","rest-api"]',
  'title:"Package Files"',
  'id:"model-chat", title:"Model Chat"',
  'help-nav-separator'
]) must(js.includes(token)||html.includes(token),`missing help navigation contract: ${token}`);
const cyr=/[\u0400-\u04FF]/;
must(!cyr.test(html),'main Editor HTML must not contain Cyrillic UI text');
must(!cyr.test(js),'main Editor JavaScript must not contain Cyrillic UI text');
must(!cyr.test(apiGuide),'Execute Playbook API guide must be English-only');
console.log('PASS navigation order + English UI regression');
