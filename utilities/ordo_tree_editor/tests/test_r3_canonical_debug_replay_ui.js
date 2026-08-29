const fs=require('fs');
const html=fs.readFileSync('web/index.html','utf8');
const js=fs.readFileSync('web/app.js','utf8');
const css=fs.readFileSync('web/styles.css','utf8');
function must(v,m){if(!v)throw new Error(m);}
must(html.includes('canonical debug handoff ZIP'),'Replay upload text must name canonical debug handoff');
must(html.includes('accept=".zip,application/zip"'),'Replay upload must be ZIP-only');
for(const token of ['Assistant · verbatim','Analyst · verbatim','Model action','Runtime-observable token equivalent','Exact host tokens','Files / tools','Receipt / integrity details','Artifact quality'])must(js.includes(token),`missing canonical replay UI token: ${token}`);
must(!js.includes('Route and accepted decisions come from run_trace.json'),'legacy run_trace replay wording must be removed');
must(css.includes('.replay-event.model-action'),'structured model actions need dedicated UI styling');
console.log('PASS canonical debug replay UI regression');
