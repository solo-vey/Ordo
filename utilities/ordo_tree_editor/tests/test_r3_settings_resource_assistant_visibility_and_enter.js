const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'..');
const app=fs.readFileSync(path.join(root,'web/app.js'),'utf8');
const css=fs.readFileSync(path.join(root,'web/styles.css'),'utf8');

for(const token of [
  'const submitSettingsAssistant=()=>{',
  'form?.addEventListener("submit",event=>{',
  'submitSettingsAssistant();',
  'if(event.key!=="Enter"||event.shiftKey||event.isComposing) return;'
]) if(!app.includes(token)) throw new Error('missing shared settings submit contract: '+token);

const settingsBinding=app.slice(app.indexOf('function bindSettingsAssistant(){'),app.indexOf('const LINEAGE_CARD_W'));
if(settingsBinding.includes('requestSubmit')) throw new Error('settings Enter still depends on requestSubmit');
if(css.includes('main.settings-resource-mode[data-workspace-mode="settings"] #inspector-resizer,main.settings-resource-mode[data-workspace-mode="settings"] #inspector{display:none!important}')) throw new Error('resource mode still hides assistant inspector');
for(const token of [
  'main.settings-resource-mode[data-workspace-mode="settings"] #inspector{grid-area:inspector;display:block!important}',
  'grid-template-areas:"tabs tabs tabs" "primary resize inspector"'
]) if(!css.includes(token)) throw new Error('missing resource assistant layout contract: '+token);

console.log('PASS settings resource assistant visibility + Enter shared submit contract');
