const fs=require('fs');
const vm=require('vm');
const html=fs.readFileSync('web/index.html','utf8');
const js=fs.readFileSync('web/app.js','utf8');
const css=fs.readFileSync('web/styles.css','utf8');
function must(cond,msg){ if(!cond) throw new Error(msg); }
must(html.includes('id="workspace-maximize-toggle"'),'workspace maximize toggle missing');
for(const token of ['workspacePrimarySelector','toggleWorkspaceMaximized','workspace-maximized-target']) must(js.includes(token),`missing js ${token}`);
for(const token of ['body.workspace-maximized','.workspace-maximized-target','#workspace-maximize-toggle']) must(css.includes(token),`missing css ${token}`);
const start=js.indexOf('function workspacePrimarySelector(');
must(start>=0,'workspacePrimarySelector missing');
const brace=js.indexOf('{',start); let depth=0,end=-1;
for(let i=brace;i<js.length;i++){ if(js[i]==='{')depth++; else if(js[i]==='}'&&--depth===0){end=i+1;break;} }
const sandbox={}; vm.createContext(sandbox); vm.runInContext(js.slice(start,end),sandbox);
const expected={upload:'#upload-home-panel',tree:'#workspace',paths:'#workspace',replay:'#inspector',chat:'#inspector',modelchat:'#model-chat-main-panel',lineage:'#lineage-main-panel',settings:'#playbook-settings-main-panel',verification:'#verification-main-panel',help:'#inspector'};
for(const [mode,selector] of Object.entries(expected)) if(sandbox.workspacePrimarySelector(mode)!==selector) throw new Error(`${mode}: ${sandbox.workspacePrimarySelector(mode)} != ${selector}`);
console.log('PASS generic workspace focus-mode contract');
