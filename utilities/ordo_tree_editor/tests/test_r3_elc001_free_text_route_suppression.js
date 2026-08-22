const fs=require('fs'), path=require('path'), vm=require('vm');
const app=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
const start=app.indexOf('function buildLiveChoiceContext');
const end=app.indexOf('async function diagnoseLiveRecovery');
if(start<0||end<0) throw new Error('choice helper not found');
const snippet=app.slice(start,end);
const sandbox={
  state:{
    source:{nodes:[{id:'N_TEXT',question:'Describe the issue',answer_type:'free_text',on_answer:{next:'N_NEXT'}}],gates:[]},
    liveRecoveryDiagnoses:{}
  },
  uiText:(a,b)=>a,
  latestFailedGateEvidence:()=>null,
  humanGateRouteLabel:(k,t)=>k,
  humanDecisionAnswerLabel:(k,t,c)=>k,
  systemNodeLabel:x=>x,
  humanReadableNodeLabel:x=>x,
  formatFailedCheck:x=>String(x||''),
  choiceTargetTooltip:x=>'',
  console
};
vm.createContext(sandbox); vm.runInContext(snippet,sandbox);
const live={await_analyst:true,routes:[{key:'next',target:'N_NEXT'}],llm_call_skipped:true,debug:{runtime:{reason:'declared-human-input'}}};
const ctx=sandbox.buildLiveChoiceContext('N_TEXT',live);
if(ctx!==null) throw new Error('ordinary free-text input must not expose graph transition routes as analyst answer buttons');
console.log('ELC-001 FREE-TEXT ROUTE SUPPRESSION: PASS');
// Explicit choice interaction still exposes declared choices.
sandbox.state.source={nodes:[{id:'N_ENUM',question:'Choose',answer_type:'enum',on_answer:{yes:{next:'END_Y'},no:{next:'END_N'}}}],gates:[]};
const enumLive={await_analyst:true,routes:[{key:'yes',target:'END_Y'},{key:'no',target:'END_N'}],llm_call_skipped:true,debug:{runtime:{reason:'declared-human-input'}}};
const enumCtx=sandbox.buildLiveChoiceContext('N_ENUM',enumLive);
if(!enumCtx || enumCtx.options.length!==2) throw new Error('explicit enum choices must remain visible');
console.log('ELC-001 EXPLICIT CHOICES PRESERVED: PASS');
