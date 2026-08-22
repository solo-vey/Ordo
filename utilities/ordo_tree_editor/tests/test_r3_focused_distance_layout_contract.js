
const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");
for(const t of [
  'distance=new Map([[entityId,0]])',
  'distance.set(nextId,currentDistance+1)',
  'signedDistance=new Map([[entityId,0]])',
  'signedDistance.set(id,-d)',
  'function lineageFocusedDistanceLayout',
  'Upstream · ${Math.abs(distance)} step',
  'Downstream · ${distance} step',
  'const focusedLayout=lineageFocusedDistanceLayout'
]) if(!js.includes(t)) throw new Error("missing "+t);
const a=js.indexOf("function lineageDirectedReachable"),b=js.indexOf("function lineageFocusedSlice",a),body=js.slice(a,b);
if(body.indexOf("if(!nextId||visited.has(nextId)) continue") > body.indexOf("traversedEdges.push(edge)"))
  throw new Error("non-traversed cycle/duplicate edge can leak into focused edge set");
console.log("PASS focused signed-distance layout contract");
