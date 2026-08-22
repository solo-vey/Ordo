const fs=require('fs');
const html=fs.readFileSync('web/index.html','utf8');
const js=fs.readFileSync('web/app.js','utf8');
const css=fs.readFileSync('web/styles.css','utf8');
for(const token of [
  'data-playbook-settings-subtab="settings"',
  'data-playbook-settings-subtab="runtime"',
  'data-playbook-settings-subtab="package"',
  'data-playbook-settings-subtab="verification"',
  'id="playbook-settings-resources-view"',
  'id="playbook-settings-resource-preview"'
]) if(!html.includes(token)) throw new Error('missing '+token);
for(const token of [
  'renderPlaybookSettingsSubtab',
  'renderPlaybookSettingsResourcePreview',
  'unbound_resource_groups',
  'settings-resource-mode'
]) if(!js.includes(token)) throw new Error('missing JS '+token);
for(const token of ['.playbook-settings-subtabs','.playbook-settings-resource-layout','main.settings-resource-mode']) if(!css.includes(token)) throw new Error('missing CSS '+token);
console.log('PASS Playbook Settings unbound resource subtabs UI contract');
