const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'web','index.html'),'utf8');
const js=fs.readFileSync(path.join(root,'web','app.js'),'utf8');
const css=fs.readFileSync(path.join(root,'web','styles.css'),'utf8');
function must(haystack,needle,label){ if(!haystack.includes(needle)) throw new Error(`Missing ${label}: ${needle}`); }
must(html,'data-workspace-tab="modelchat">Model Chat','global Model Chat tab');
must(html,'data-workspace-tab="help">Help','global Help tab');
must(js,'!loaded && !["upload","modelchat","help"].includes(mode)','source-empty global-workspace enablement');
must(js,'if (!state.source && !["upload","modelchat","help"].includes(mode)) return;','source-empty navigation guard');
must(css,'main.source-empty[data-workspace-mode="help"] #inspector { display:block!important; }','source-empty Help inspector override');
console.log('PASS Help remains visible and openable from free Model Chat/source-empty mode');
