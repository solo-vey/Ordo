const fs=require('fs'),assert=require('assert');
const html=fs.readFileSync(require('path').join(__dirname,'../web/index.html'),'utf8');
const app=fs.readFileSync(require('path').join(__dirname,'../web/app.js'),'utf8');
for (const token of ['Parameters','YAML','References','template-inspector-view']) assert(html.includes(token),token);
for (const removed of ['data-template-tab="overview"','data-template-tab="template"','data-template-tab="parameters"','data-template-tab="raw"']) assert(!html.includes(removed),removed);
for (const token of ['/api/template-inspector','templateCapableRecord','loadTemplateInspector','renderTemplateInspectorTab']) assert(app.includes(token),token);
assert(app.includes('tab !== "references"'));
console.log('PASS unified Parameters/YAML/References inspector contract');
