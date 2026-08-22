const fs=require('fs');
const s=fs.readFileSync(require('path').join(__dirname,'..','web','app.js'),'utf8');
for (const needle of ['function isConversationalRecoveryNode','/api/recovery-chat','isConversationalRecoveryNode(id)) { state.livePaused = true','action === "retry_gate"','action === "go_to_target"']) {
  if (!s.includes(needle)) throw new Error('missing '+needle);
}
console.log('CONVERSATIONAL RECOVERY UI: PASS');
