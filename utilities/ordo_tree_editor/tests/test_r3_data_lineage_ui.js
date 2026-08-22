const fs=require("fs");
const html=fs.readFileSync("web/index.html","utf8");
const js=fs.readFileSync("web/app.js","utf8");
const css=fs.readFileSync("web/styles.css","utf8");
for(const token of ['data-workspace-tab="lineage"','id="lineage-main-panel"','id="lineage-assistant-panel"','id="source-flow-viewport"','id="lineage-explain"']) if(!html.includes(token)) throw new Error("missing "+token);
for(const token of ['/api/embedded-data-flow','/api/data-lineage-assistant','renderDataLineage','renderSourceDataFlow','sourceFlowConnectedContext','sendLineageAssistant','bindLineageAssistant']) if(!js.includes(token)) throw new Error("missing js "+token);
for(const token of ['main[data-workspace-mode="lineage"]','.source-flow-node','.source-flow-edge','.source-flow-subtabs']) if(!css.includes(token)) throw new Error("missing css "+token);
if(html.includes('id="lineage-reconstructed-panel"')) throw new Error("reconstructed flow must be retired");
console.log("PASS source-only Data Flow UI contract");
