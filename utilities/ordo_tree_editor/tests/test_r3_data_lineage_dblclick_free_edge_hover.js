
const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");
const css=fs.readFileSync("web/styles.css","utf8");
for(const token of [
  'focusRoot:null',
  'function focusLineageEntity',
  'el.addEventListener("dblclick"',
  'selectLineageEntity(n.id)',
  'state.lineage.layoutMode!=="free"||ev.button!==0',
  'state.lineage.focusRoot?lineageFocusedDisplayEdges()',
  'function bindLineageEdgeHover',
  'edge-endpoint','edge-hovered'
]) if(!js.includes(token) && !css.includes(token)) throw new Error("missing "+token);
if(js.includes('state.lineage.layoutMode!=="free"||state.lineage.selected||ev.button!==0')) throw new Error("focused Free layout still blocked");
console.log("PASS inspect/focus split + focused Free + edge hover contract");
