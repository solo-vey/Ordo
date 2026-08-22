const fs=require('fs'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'..');
const app=fs.readFileSync(path.join(root,'web/app.js'),'utf8');
for (const token of ['["output","declared_output"].includes(view?.entity_type)','outputInspectable','Producer nodes','loadTemplateInspector(null,view)']) assert(app.includes(token), token);
console.log('R3 OUTPUT RESOURCE INSPECTOR UI CONTRACT PASS');
