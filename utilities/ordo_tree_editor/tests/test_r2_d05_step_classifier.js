const fs=require('fs'), path=require('path');
const src=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
for (const needle of ['function classifyExecutionStep(d)','skipped_incomplete_context','replayed_model_call','live_model_call','step_class_counts','step_class: classifyExecutionStep(d)']) {
  if (!src.includes(needle)) throw new Error('missing '+needle);
}
// Extract classifier only and execute it.
const m=src.match(/function classifyExecutionStep\(d\) \{[\s\S]*?\n\}/);
if(!m) throw new Error('classifier function not found');
eval(m[0]);
const skipped={semantic_model_attempts:[{skipped_model_call:true,reason:'context_incomplete'}],input:{request_payload:null},output:{api_response:null},runtime:{}};
if(classifyExecutionStep(skipped)!=='skipped_incomplete_context') throw new Error('skipped classified live');
const replay={input:{request_payload:{replay:true}},output:{api_response:{replay:true}},runtime:{llm_call_skipped:false}};
if(classifyExecutionStep(replay)!=='replayed_model_call') throw new Error('replay mismatch');
const live={input:{request_payload:{model:'x'}},output:{api_response:{id:'x'}},runtime:{llm_call_skipped:false}};
if(classifyExecutionStep(live)!=='live_model_call') throw new Error('live mismatch');
console.log('PASS R2-D05 canonical step classifier');
