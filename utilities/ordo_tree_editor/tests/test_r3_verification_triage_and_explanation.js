const fs=require('fs'), path=require('path');
const app=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
for(const token of ['verificationDisplayRows','FAIL:1','SKIPPED:2','PASS:5','verification_check','Explain with model','verification-explanation-markdown','renderBasicMarkdown(cached.explanation||"")']){
  if(!app.includes(token)){ console.error('missing',token); process.exit(1); }
}
console.log('PASS verification triage + explanation UI contract');
