
const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");
const css=fs.readFileSync("web/styles.css","utf8");
for(const token of [
  'LINEAGE_SEMANTIC_LAYERS',
  '{id:"analyst",label:"Analyst input"',
  '{id:"transformation",label:"Transformation"',
  '{id:"derived",label:"Derived state"',
  '{id:"document",label:"Document"',
  '{id:"archive",label:"Archive / package"',
  'lineageVisibleNodeIds',
  'visibleIds=lineageVisibleNodeIds()',
  'lineage-layer-heading',
  'wasClick&&state.lineage.focusRoot',
  'state.lineage.layoutMode==="free"&&existing[n.id]'
]) if(!js.includes(token)) throw new Error("missing "+token);
for(const token of ['.lineage-layer-heading','.layer-analyst','.layer-transformation','.layer-derived','.layer-document','.layer-archive'])
  if(!css.includes(token)) throw new Error("missing css "+token);
console.log("PASS canonical five-layer + focused-subgraph Data Flow contract");
