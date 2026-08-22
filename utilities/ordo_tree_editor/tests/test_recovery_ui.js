const fs=require('fs'), path=require('path'), vm=require('vm');
const here=__dirname;
const fixture=JSON.parse(fs.readFileSync(path.join(here,'fixtures','real_validation_recovery_choice.json'),'utf8'));
const app=fs.readFileSync(path.join(here,'..','web','app.js'),'utf8');
const start=app.indexOf('function humanReadableNodeLabel');
const end=app.indexOf('function renderLiveChoicePanel');
if(start<0||end<0) throw new Error('recovery helper functions not found');
const snippet=app.slice(start,end);
const sandbox={state:{source:fixture.source,liveDebugTrace:fixture.debug_trace},graphNodeView:(id)=>({id,label:id}),console};
vm.createContext(sandbox); vm.runInContext(snippet,sandbox);
const ctx=sandbox.buildLiveChoiceContext('N_VALIDATION_FAILURE_RECOVERY',fixture.live);
if(!ctx||!ctx.recovery) throw new Error('recovery context not detected');
if(ctx.options.length!==fixture.expected.option_count) throw new Error(`option count ${ctx.options.length}`);
if(ctx.options.filter(x=>x.recommended).length!==fixture.expected.recommended_count) throw new Error('editor guessed a recommendation without evidence');
for(const needle of fixture.expected.summary_contains){ if(!ctx.summary.includes(needle)) throw new Error(`summary missing ${needle}`); }
for(const label of fixture.expected.labels){ if(!ctx.options.some(x=>x.label===label)) throw new Error(`missing label ${label}`); }
console.log('RECOVERY UI REGRESSION: PASS');
