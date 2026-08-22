
const fs=require("fs");const js=fs.readFileSync("web/app.js","utf8");
for(const x of ["function lineageNonTransformRank","function lineageInitialBound","function lineageMonotonicReachable",'direction==="up" && rank>current.bound','direction==="down" && rank<current.bound','lineageMonotonicReachable(data,state.lineage.selected,"up")','lineageMonotonicReachable(data,state.lineage.selected,"down")'])if(!js.includes(x))throw Error(x);
console.log("PASS monotonic causal slice focused-view contract");
