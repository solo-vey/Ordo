const fs=require('fs');const path=require('path');
const app=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
function must(cond,msg){if(!cond){console.error('FAIL:',msg);process.exit(1)}}
must(app.includes('liveRunId: ""'), 'state must carry a run id');
must(app.includes('state.liveRunId = crypto.randomUUID'), 'each fresh run must receive a new run id');
must(app.includes('run_id: state.liveRunId'), 'live-step payload must carry run_id');
must(app.includes('&run_id=${encodeURIComponent(state.liveRunId||"")}'), 'artifact download must address the producing run workspace');
must(app.includes('run_id: state.liveRunId,\n      session_id: liveSessionId'), 'evidence run metadata must carry run/session identity');
console.log('PASS test_r3_run_identity_ui');
