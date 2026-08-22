
const fs=require("fs");
const html=fs.readFileSync("web/index.html","utf8");
const js=fs.readFileSync("web/app.js","utf8");
const css=fs.readFileSync("web/styles.css","utf8");

const mainIndex=html.indexOf('id="playbook-settings-main-panel"');
const workspaceIndex=html.indexOf('id="workspace"');
const inspectorIndex=html.indexOf('id="inspector"');
const assistantIndex=html.indexOf('id="playbook-settings-assistant-panel"');

if(mainIndex<0 || assistantIndex<0) throw new Error("settings panels missing");
if(!(workspaceIndex < mainIndex && mainIndex < inspectorIndex && inspectorIndex < assistantIndex)) {
  throw new Error("settings main panel must be outside inspector; assistant must be inside inspector");
}
if(html.includes('id="playbook-settings-panel"')) throw new Error("legacy combined settings panel still present");
for(const token of ['#playbook-settings-main-panel").hidden=tab !== "settings"','#playbook-settings-assistant-panel").hidden=tab !== "settings"']) {
  if(!js.includes(token)) throw new Error("missing JS toggle "+token);
}
for(const token of [
  'grid-template-areas:"tabs tabs tabs" "primary resize side"',
  '#playbook-settings-main-panel',
  'main[data-workspace-mode="settings"] #workspace',
  '.playbook-settings-assistant-panel'
]) {
  if(!css.includes(token)) throw new Error("missing CSS contract "+token);
}
console.log("PASS settings main/assistant two-pane DOM contract");
