const fs=require("fs");
const html=fs.readFileSync("web/index.html","utf8");
const js=fs.readFileSync("web/app.js","utf8");
for(const token of [
  'id="source-flow-panel"',
  'id="source-flow-viewport"',
  'id="source-flow-canvas"',
  'id="source-flow-subview-tree"',
  'id="source-flow-subview-passports"'
]) if(!html.includes(token)) throw new Error("missing source-only html "+token);
for(const forbidden of [
  'id="lineage-view-reconstructed"',
  'id="lineage-view-source"',
  'id="lineage-reconstructed-panel"',
  '>Reconstructed Flow<'
]) if(html.includes(forbidden)) throw new Error("retired reconstructed UI still present: "+forbidden);
for(const token of [
  '/api/embedded-data-flow',
  'loadEmbeddedDataFlow',
  'renderSourceDataFlow',
  'source-flow-node',
  'sourceFlowOrthogonalPath',
  'view_mode:"source"'
]) if(!js.includes(token)) throw new Error("missing source-only js "+token);
if(js.includes('setLineageViewMode(')) throw new Error("retired lineage view switch still present");
if(!js.includes('lineage:{viewMode:"source"')) throw new Error("Source Data Flow is not default mode");
console.log("PASS source-only Show Data Flow contract");
