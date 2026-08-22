
const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");
const css=fs.readFileSync("web/styles.css","utf8");
for(const token of ["evidence_summary:item.evidence_summary","evidence:Array.isArray(item.evidence)","verification-evidence-summary","Evidence ${item.evidence.length}"]) if(!js.includes(token)) throw new Error("missing "+token);
for(const token of [".verification-evidence-summary",".verification-evidence-item"]) if(!css.includes(token)) throw new Error("missing css "+token);
console.log("PASS verification evidence UI/export contract");
