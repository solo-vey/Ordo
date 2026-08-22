const fs=require('fs'),assert=require('assert');
const app=fs.readFileSync(require('path').join(__dirname,'../web/app.js'),'utf8');
for (const token of ['form.hidden=!(inspectable || outputInspectable)','renderDerivedOutputParameters(data)','state.templateInspectorData?.entity_type === "output"','loadTemplateInspector(null,view)']) assert(app.includes(token),token);
console.log('PASS output resource inspector visible-parent contract');
