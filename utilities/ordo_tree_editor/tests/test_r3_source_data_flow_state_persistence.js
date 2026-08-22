const fs=require('fs'),path=require('path');
const app=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
function must(x,m){if(!x)throw new Error(m);}
must(app.includes('assistantThreads:{}'),'source assistant thread store missing');
must(app.includes('function sourceFlowAssistantThread(entityId'),'per-entity assistant thread resolver missing');
must(app.includes('const entityId=entity.id,thread=sourceFlowAssistantThread(entityId)'),'assistant request is not bound to selected entity thread');
must(app.includes('messages:thread.messages.map'),'assistant request does not use entity-local history');
must(!app.includes('if(click&&state.lineage.sourceFocusRoot){state.lineage.sourceSelected=null;state.lineage.sourceFocusRoot=null;renderSourceDataFlow();}'),'background/scroll pointer-up still clears source focus');
must(!app.includes('state.lineage.sourceSelected=node.id;state.lineage.sourceFocusRoot=node.id;state.lineage.messages=[];state.lineage.busy=false;renderSourceDataFlow();'),'tree selection still destroys assistant history');
must(!app.includes('state.lineage.sourceSelected=n.id;state.lineage.sourceFocusRoot=n.id;state.lineage.messages=[];state.lineage.busy=false;renderSourceFlowInspector();'),'passport selection still destroys assistant history');
must(app.includes('#source-flow-clear-focus') && app.includes('state.lineage.sourceSelected=null;state.lineage.sourceFocusRoot=null;renderSourceDataFlow();'),'explicit clear-focus control missing');
console.log('PASS source data flow viewport/assistant state persistence');
