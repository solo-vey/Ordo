
const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");

for(const token of [
  'Explain this verification result immediately.',
  '{hiddenUser:true}',
  'filter(msg=>!msg.hidden)',
  'event.key!=="Enter"',
  'if(event.ctrlKey) return',
  'form?.requestSubmit()',
  'The model returned an empty verification-assistant response.'
]) if(!js.includes(token)) throw new Error("missing "+token);

console.log("PASS verification assistant auto-explain + Enter/Ctrl+Enter contract");
