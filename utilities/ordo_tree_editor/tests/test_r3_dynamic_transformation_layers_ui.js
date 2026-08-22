
const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");
for(const t of [
  'label:"Analyst input / collection"',
  'label:"Transformation · input → state"',
  'label:"Derived state"',
  'label:"Transformation · state → document"',
  'label:"Document / document-phase transformation"',
  'label:"Transformation · document → package"',
  'label:"Archive / package"',
  'function lineageTransformationRank',
  'artifact_role==="package_source_resource"',
  'lineageSemanticLayer(n,data)===layerIndex'
]) if(!js.includes(t)) throw new Error("missing "+t);
console.log("PASS dynamic transformation phase UI");
