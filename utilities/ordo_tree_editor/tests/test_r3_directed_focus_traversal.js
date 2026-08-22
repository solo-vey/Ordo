
const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");
for(const token of [
  'function lineageDirectedReachable',
  'const visited=new Set([entityId])',
  'direction==="up"?edge.target===current:edge.source===current',
  'direction==="up"?edge.source:edge.target',
  'if(!nextId||visited.has(nextId)) continue',
  'const up=lineageDirectedReachable(data,entityId,"up")',
  'const down=lineageDirectedReachable(data,entityId,"down")',
  'return lineageFocusedSlice(data,state.lineage.focusRoot).edges'
]) if(!js.includes(token)) throw new Error("missing "+token);
if(/function\s+lineageMonotonicReachable\s*\(/.test(js)) throw new Error("old traversal definition remains");
if(js.includes("collapsed_lineage")) throw new Error("synthetic collapsed focused edges remain");
console.log("PASS directed focused traversal contract");
