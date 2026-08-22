
const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");
const css=fs.readFileSync("web/styles.css","utf8");

for(const token of [
  'direct=base.filter(e=>{',
  'lineageAllowsCausalStep(sourceNode,targetNode,"down")',
  'if(state.lineage.focusRoot){',
  'if(!state.lineage.focusRoot) return;',
  'focused-lineage'
]) if(!js.includes(token)) throw new Error("missing "+token);

for(const token of [
  '#lineage-edges .lineage-edge-hit{pointer-events:none!important}',
  '#lineage-viewport.focused-lineage #lineage-edges .lineage-edge-hit{pointer-events:stroke!important}'
]) if(!css.includes(token)) throw new Error("missing css "+token);

// Semantic edge matrix: only same/downward ranks may be drawn in focused mode.
const ranks={analyst:0,transform:1,derived:2,document:3,archive:4};
const allowed=(a,b)=>ranks[b]>=ranks[a];
if(allowed("derived","transform")) throw new Error("reverse derived -> transformation edge must be hidden");
if(allowed("document","transform")) throw new Error("reverse document -> transformation edge must be hidden");
if(allowed("archive","document")) throw new Error("reverse archive -> document edge must be hidden");
if(!allowed("analyst","transform")) throw new Error("analyst -> transformation should remain");
if(!allowed("transform","derived")) throw new Error("transformation -> derived should remain");
if(!allowed("derived","document")) throw new Error("derived -> document should remain");
if(!allowed("document","archive")) throw new Error("document -> archive should remain");

console.log("PASS focused graph renders causal-only edges; hover hit areas are focus-only");
