const fs=require('fs');
const path=require('path');
const src=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
function must(token){ if(!src.includes(token)){ console.error('missing',token); process.exit(1);} }
must('canonicalEnumKeys');
must('humanDecisionAnswerLabel');
must('choiceTargetTooltip');
must('button.title=option.tooltip');
must('canonicalRoutes=routes.filter');
console.log('choice semantics + tooltip regression: PASS');
