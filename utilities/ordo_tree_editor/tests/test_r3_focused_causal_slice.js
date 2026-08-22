
const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");
for(const t of [
  'lineageFocusedSlice',
  'lineageSupportingPrerequisites',
  'lineageFocusedDisplayEdges',
  'sameSelectedLayer',
  'allowSelectedLayerTransit',
  'sourceLayer>=selectedLayer',
  'collapsed_lineage'
]) if(!js.includes(t)) throw new Error("missing "+t);
console.log("PASS selected-layer uniqueness + supporting transformation prerequisites contract");
