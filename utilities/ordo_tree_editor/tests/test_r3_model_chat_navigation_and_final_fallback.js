
const fs=require("fs");
const html=fs.readFileSync("web/index.html","utf8");
const js=fs.readFileSync("web/app.js","utf8");
const css=fs.readFileSync("web/styles.css","utf8");
const tabs=[...html.matchAll(/data-workspace-tab="([^"]+)"/g)].map(m=>m[1]);
const expected=["upload","chat","replay","tree","paths","lineage","settings","verification","modelchat","help"];
for(const x of expected) if(!tabs.includes(x)) throw new Error("missing tab "+x);
if(!(tabs.indexOf("modelchat")===tabs.indexOf("help")-1)) throw new Error("Model Chat must be immediately before Help");
if(!css.includes('grid-template-areas: "tabs" "primary"')) throw new Error("source-empty must reserve tabs row");
if(!js.includes('button.hidden=false')) throw new Error("workspace tabs must be explicitly kept visible");
console.log("PASS persistent full navigation + Model Chat placement");
