const fs=require('fs'),path=require('path');
const app=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
function must(x,m){if(!x)throw new Error(m);}
must(app.includes('function activeLineageAssistantEntity()'),'missing shared active entity resolver');
must(app.includes('function activeLineageAssistantContext(entity)'),'missing shared context resolver');
must(app.includes('state.lineage.sourceSelected'),'source selection not wired to assistant');
must(!app.includes('if(toolbar)toolbar.hidden=true;if(form)form.hidden=true;if(messages){messages.hidden=true;messages.innerHTML="";}'),'source inspector still hides assistant');
must(app.includes('sendLineageAssistant("Explain this selected data-flow entity.'),'explain binding missing');
console.log('PASS source data flow assistant wiring');
