
const fs=require("fs");
const html=fs.readFileSync("web/index.html","utf8");
const js=fs.readFileSync("web/app.js","utf8");
const css=fs.readFileSync("web/styles.css","utf8");

for(const token of [
  'id="settings-assistant-context"',
  'Specified settings',
  'Not specified settings',
  'data-setting-discuss=',
  'Discuss in chat',
  'discussPlaybookSetting',
  'settingBootstrapPrompt',
  '{hiddenUser:true}',
  'all documented allowed values',
  'interact with other settings'
]) if(!(html.includes(token)||js.includes(token))) throw new Error("missing "+token);

const specifiedIndex=js.indexOf('renderBucket("Specified settings",true)');
const missingIndex=js.indexOf('renderBucket("Not specified settings",false)');
if(specifiedIndex<0 || missingIndex<0 || specifiedIndex>missingIndex) throw new Error("specified settings must render first");

for(const token of [
  '.playbook-settings-status-section',
  '.setting-discuss-button',
  '.settings-assistant-context'
]) if(!css.includes(token)) throw new Error("missing css "+token);

console.log("PASS per-setting discussion + specified-first settings contract");
