const fs=require('fs'), path=require('path');
const app=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
const html=fs.readFileSync(path.join(__dirname,'..','web','index.html'),'utf8');
for(const token of [
  'id="verification-export-json"',
  'Export results JSON'
]) if(!html.includes(token)){ console.error('missing html',token); process.exit(1); }
for(const token of [
  'function exportVerificationResultsJson()',
  'ordo.editor.verification_results.v2',
  'checks:(v.checks || []).map',
  'descriptor_file:item.descriptor_file',
  'duration_ms:item.duration_ms',
  'exit_code:item.exit_code',
  'output:item.output || ""',
  'model_explanation:',
  'classification:cached.classification',
  'verification-export-json'
]) if(!app.includes(token)){ console.error('missing app',token); process.exit(1); }
console.log('PASS verification JSON export');
