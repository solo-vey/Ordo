
const fs=require('fs');
const html=fs.readFileSync('web/index.html','utf8');
const js=fs.readFileSync('web/app.js','utf8');
const css=fs.readFileSync('web/styles.css','utf8');

for(const token of [
  'id="playbook-settings-main-panel"',
  'id="playbook-settings-assistant-panel"',
  'id="playbook-settings-summary"',
  'id="settings-assistant-analyze"',
  'id="settings-assistant-form"',
  'id="settings-assistant-messages"'
]) if(!html.includes(token)) throw new Error('missing '+token);

for(const token of [
  '/api/playbook-settings-assistant',
  'runSettingsAssistant',
  'Not specified',
  'Proposed YAML settings block'
]) if(!js.includes(token)) throw new Error('missing '+token);

for(const token of [
  'main[data-workspace-mode="settings"] #workspace',
  '#playbook-settings-main-panel',
  '.playbook-settings-assistant-panel',
  '.playbook-settings-assistant'
]) if(!css.includes(token)) throw new Error('missing '+token);

console.log('PASS split Playbook Settings + assistant UI contract');
