const fs=require('fs'), path=require('path'), vm=require('vm');
const app=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
const start=app.indexOf('function stableLiveJson');
const end=app.indexOf('function accumulateLiveUsage');
if(start<0||end<0) throw new Error('no-progress helpers not found');
const snippet=app.slice(start,end);
const sandbox={state:{liveNoProgressGateFailures:{}},console};
vm.createContext(sandbox); vm.runInContext(snippet,sandbox);

const failure={
  failed_checks:[{check_id:'G_CONTRACT',summary:'invalid contract'}],
  missing_coverage:[], invalid_state:['bad'], missing_information:[], affected_state:['contract']
};
const base={state_after:{contract:{status:'invalid'},runtime_timestamp:'t1'}};

if(sandbox.detectNoProgressGateFailure('G_CONTRACT',failure,base,'analyst:fix A')!==false)
  throw new Error('first failure must not halt');

// A genuinely new correction event is progress even if business state is unchanged.
if(sandbox.detectNoProgressGateFailure('G_CONTRACT',failure,base,'analyst:fix B')!==false)
  throw new Error('new analyst correction must reset no-progress guard without fake business-state mutation');

// Repeating the same correction with the same relevant state is a real stall.
if(sandbox.detectNoProgressGateFailure('G_CONTRACT',failure,base,'analyst:fix B')!==true)
  throw new Error('identical correction + identical relevant state must halt');

// Unrelated timestamp mutation must NOT manufacture progress.
const timestampNoise={state_after:{contract:{status:'invalid'},runtime_timestamp:'t2'}};
if(sandbox.detectNoProgressGateFailure('G_OTHER',failure,base,'analyst:same')!==false)
  throw new Error('first failure on second gate must not halt');
if(sandbox.detectNoProgressGateFailure('G_OTHER',failure,timestampNoise,'analyst:same')!==true)
  throw new Error('unrelated runtime timestamp mutation must not count as progress');

console.log('LANGUAGE CONFORMANCE NO-PROGRESS: PASS');
