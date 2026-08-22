const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");
const css=fs.readFileSync("web/styles.css","utf8");
for(const token of [
  "GRAPH_RESOURCE_PATH_RE",
  "classifyGraphReferenceType",
  "graphReferenceBadgesForNode",
  "node-ref-badges",
  "node-ref-badge-file",
  "node-ref-badge-text",
]) if(!js.includes(token) && !css.includes(token)) throw new Error(`missing ${token}`);
for(const token of [
  ".node-ref-badges",
  ".node-ref-badge",
  ".node-ref-py",
  ".node-ref-yaml",
  ".node-ref-md",
  ".node-ref-json",
  ".node-ref-other",
]) if(!css.includes(token)) throw new Error(`missing css ${token}`);
if(!css.includes('.live-scroll-to-bottom[data-state="working"]')) throw new Error('missing working pill shape');
console.log('PASS graph reference badges + working pill shape contract');
