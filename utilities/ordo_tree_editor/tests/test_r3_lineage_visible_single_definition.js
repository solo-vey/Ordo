
const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");
const defs=[...js.matchAll(/function lineageVisibleNodeIds\s*\(/g)];
if(defs.length!==1) throw new Error(`expected exactly one lineageVisibleNodeIds definition, got ${defs.length}`);
const start=js.indexOf("function lineageVisibleNodeIds");
const body=js.slice(start,start+700);
if(!body.includes("lineageFocusedSlice(data,state.lineage.selected).visible"))
  throw new Error("focused selection must use lineageFocusedSlice(...).visible");
if(body.includes("...upstream")||body.includes("...downstream"))
  throw new Error("obsolete spread of structured traversal result remains");
console.log("PASS single lineageVisibleNodeIds definition + focused Set contract");
