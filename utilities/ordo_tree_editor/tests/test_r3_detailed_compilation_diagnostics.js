const fs=require('fs');
const html=fs.readFileSync('web/index.html','utf8');
const js=fs.readFileSync('web/app.js','utf8');
const css=fs.readFileSync('web/styles.css','utf8');
for(const token of ['Download diagnostics JSON','playbook-preparation-diagnostics','Raw diagnostics']) if(!html.includes(token)) throw new Error('missing html '+token);
for(const token of ['diagnostics','source_location','Expected rule','How to fix','downloadPlaybookPreparationDiagnostics','compilation_diagnostics.json','GRAPH_NOT_FULLY_REACHABLE','NONTERMINAL_WITHOUT_ROUTE']) if(!js.includes(token)) throw new Error('missing js '+token);
for(const token of ['.playbook-preparation-diagnostic','.diagnostic-meta','.playbook-preparation-download']) if(!css.includes(token)) throw new Error('missing css '+token);
console.log('PASS detailed compilation diagnostics UI contract');
