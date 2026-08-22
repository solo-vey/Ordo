const fs=require("fs");
const html=fs.readFileSync("web/index.html","utf8");
const js=fs.readFileSync("web/app.js","utf8");
const css=fs.readFileSync("web/styles.css","utf8");
for(const token of [
  'id="source-flow-subview-tree"',
  'id="source-flow-subview-passports"',
  'id="source-flow-direction-tb"',
  'id="source-flow-direction-lr"',
  'id="source-flow-passport-groups"'
]) if(!html.includes(token)) throw new Error("missing html "+token);
for(const token of [
  'function sourceFlowDependencyRanks',
  'function sourceFlowLayout(graph)',
  'function renderSourceVariablePassports',
  'addEventListener("dblclick"',
  'setSourceFlowDirection("TB")',
  'setSourceFlowDirection("LR")'
]) if(!js.includes(token)) throw new Error("missing js "+token);
if(js.includes('source-flow-section-band')) throw new Error('section bands must not drive dependency tree layout');
if(!js.includes('e.type!=="invisible"')) throw new Error('dependency rank must ignore invisible layout-only edges');
for(const token of ['.source-flow-subtabs','.source-passport-group','.source-passport-card']) if(!css.includes(token)) throw new Error("missing css "+token);
console.log("PASS dependency-first source data flow UI contract");
