const fs=require('fs'); const path=require('path');
const src=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
for (const needle of ['evidence_profile: evidenceProfile','function classifyExecutionStep(d)','live_calls:liveCalls.length','replayed_calls:replayedCalls.length','skipped_incomplete_context:skippedIncompleteContext','acceptance_eligible: evidenceProfile === "live"','recorded_model_provenance']) {
  if (!src.includes(needle)) throw new Error('missing '+needle);
}
console.log('PASS evidence provenance/profile UI contract with R2-D05 classifier');
