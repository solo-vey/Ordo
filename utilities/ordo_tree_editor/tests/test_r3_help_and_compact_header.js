const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'web/index.html'),'utf8');
const css=fs.readFileSync(path.join(root,'web/styles.css'),'utf8');
const js=fs.readFileSync(path.join(root,'web/app.js'),'utf8');
function must(text,needle,label){ if(!text.includes(needle)){ throw new Error(`missing ${label}: ${needle}`); } }
function no(text,needle,label){ if(text.includes(needle)){ throw new Error(`unexpected ${label}: ${needle}`); } }
must(html,'class="app-header"','compact app header');
must(html,'data-workspace-tab="help">Help','Help workspace tab');
must(html,'id="help-panel"','Help panel');
must(css,'.app-brand { display:flex; align-items:baseline; gap:12px;','single-line brand');
must(css,'.workspace-tabs { gap: 30px;','workspace spacing');
must(css,'main[data-workspace-mode="help"]','help workspace layout');
must(js,'const HELP_PAGES = [','help page registry');
must(js,'title:"Getting Started"','getting started page');
must(js,'title:"Execute Playbook"','execute docs');
must(js,'title:"Package Files"','file docs');
must(js,'title:"Troubleshooting"','troubleshooting docs');
must(js,'help:"help"','help workspace mapping');
no(html,'Допомога','Ukrainian help label');
console.log('R3 HELP + COMPACT HEADER UI PASS');
