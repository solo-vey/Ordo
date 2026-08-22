
const fs=require("fs");
const html=fs.readFileSync("web/index.html","utf8");
const js=fs.readFileSync("web/app.js","utf8");
const css=fs.readFileSync("web/styles.css","utf8");

for(const token of [
  'id="verification-main-panel"',
  'id="verification-assistant-panel"',
  'id="verification-assistant-messages"',
  'id="verification-assistant-form"',
  'id="verification-assistant-input"'
]) if(!html.includes(token)) throw new Error("missing "+token);

if(html.includes('id="verification-panel"')) throw new Error("legacy verification panel remains");
for(const token of [
  'openVerificationDiscussion',
  'sendVerificationDiscussion',
  'Discuss in chat',
  '["FAIL","ERROR","SKIPPED"].includes(status)',
  '/api/verification-assistant'
]) if(!js.includes(token)) throw new Error("missing "+token);

for(const token of [
  'grid-template-areas:"tabs tabs tabs" "primary resize side"',
  '.verification-assistant-panel',
  '.verification-discuss-button'
]) if(!css.includes(token)) throw new Error("missing css "+token);

console.log("PASS verification two-pane assistant UI contract");
