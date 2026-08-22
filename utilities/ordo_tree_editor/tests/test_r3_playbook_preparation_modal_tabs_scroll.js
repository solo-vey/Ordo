const fs=require('fs');
const html=fs.readFileSync('web/index.html','utf8');
const js=fs.readFileSync('web/app.js','utf8');
const css=fs.readFileSync('web/styles.css','utf8');
for(const token of [
  'id="playbook-preparation-tabs"',
  'data-playbook-preparation-tab="human"',
  'data-playbook-preparation-tab="technical"',
  'data-playbook-preparation-panel="human"',
  'data-playbook-preparation-panel="technical"'
]) if(!html.includes(token)) throw new Error('missing html '+token);
for(const token of [
  'function showPlaybookPreparationTab',
  'closest?.("#playbook-preparation-close")',
  'closest?.("#playbook-preparation-download-diagnostics")',
  'closest?.("[data-playbook-preparation-tab]")',
  'showPlaybookPreparationTab("human")'
]) if(!js.includes(token)) throw new Error('missing js '+token);
for(const token of [
  'max-height:calc(100vh - 48px)',
  '.playbook-preparation-body',
  'overflow-y:auto',
  'scrollbar-color:rgba(115,115,115,.42) transparent',
  '::-webkit-scrollbar-track{background:transparent}',
  '.playbook-preparation-tabs'
]) if(!css.includes(token)) throw new Error('missing css '+token);
console.log('PASS preparation modal tabs + scroll + delegated close contract');
