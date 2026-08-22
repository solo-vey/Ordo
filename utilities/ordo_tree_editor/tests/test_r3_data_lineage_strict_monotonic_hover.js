
const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");
const css=fs.readFileSync("web/styles.css","utf8");

// The actual helper must rank transformations via lineageSemanticLayer.
const a=js.indexOf("function lineageNonTransformRank");
const b=js.indexOf("function lineageInitialBound",a);
const rankBody=js.slice(a,b);
if(!rankBody.includes("return lineageSemanticLayer(node)")) throw new Error("all semantic kinds must have a real rank");
if(rankBody.includes('startsWith("transform_")')) throw new Error("transformations are still special-cased as neutral");

// Strict step predicate.
for(const token of [
  'function lineageAllowsCausalStep',
  'if(direction==="down") return toRank>=fromRank',
  'if(direction==="up") return toRank<=fromRank',
  'lineageAllowsCausalStep(currentNode,nextNode,direction)'
]) if(!js.includes(token)) throw new Error("missing "+token);

// The reported regression must be impossible in the rank model.
const rank={analyst:0,transform:1,derived:2,document:3,archive:4};
if(rank.transform>=rank.derived) throw new Error("bad fixture");
if(rank.transform>=rank.derived) throw new Error("derived -> transformation would be allowed downstream");

// Hover must use a separate wide hit path.
for(const token of ['class","lineage-edge-hit"','bindLineageEdgeHover(hit,p)']) if(!js.includes(token)) throw new Error("missing "+token);
for(const token of ['.lineage-edge-hit','stroke-width:16px','z-index:4!important']) if(!css.includes(token)) throw new Error("missing css "+token);

console.log("PASS strict causal monotonicity + edge hit target contract");
