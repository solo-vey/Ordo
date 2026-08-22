const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'..');
const app=fs.readFileSync(path.join(root,'web/app.js'),'utf8');
const html=fs.readFileSync(path.join(root,'web/index.html'),'utf8');
for(const token of [
  'id="settings-assistant-title"',
  'id="settings-assistant-subtitle"'
]) if(!html.includes(token)) throw new Error('missing '+token);
for(const token of [
  'settingsResourceAssistantThreads',
  'resource_chat',
  'resource_path:resourceMode?resourcePath:""',
  'AI File Assistant',
  'Ask about the selected file…',
  'event.key!=="Enter"||event.shiftKey||event.isComposing',
  'const submitSettingsAssistant=()=>{'
]) if(!app.includes(token)) throw new Error('missing '+token);
if(app.includes('assistant.hidden=!isCatalog || state.panelTab!=="settings"')) throw new Error('assistant still hidden on file subtabs');
const settingsBinding=app.slice(app.indexOf('function bindSettingsAssistant(){'),app.indexOf('const LINEAGE_CARD_W'));
if(settingsBinding.includes('requestSubmit')) throw new Error('settings Enter still relies on requestSubmit');
console.log('PASS settings file assistant and Enter contract');
