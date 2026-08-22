
const fs=require("fs");
const html=fs.readFileSync("web/index.html","utf8");
const js=fs.readFileSync("web/app.js","utf8");
const css=fs.readFileSync("web/styles.css","utf8");
for(const t of ['id="lineage-filter-all"','id="lineage-filter-issues"','id="lineage-export-json"']) if(!html.includes(t)) throw new Error("missing "+t);
for(const t of ['filterMode:"all"','lineageIssueNodes','lineageIssueContextIds','buildLineageExportReport','exportLineageReportJson','schema:"ordo.editor.data_flow_report"','isolated_entities','candidate_usage_resources','semantic_layers']) if(!js.includes(t)) throw new Error("missing "+t);
for(const t of ['.lineage-filter-toggle','#lineage-export-json','.lineage-summary .has-issues']) if(!css.includes(t)) throw new Error("missing css "+t);
console.log("PASS Data Flow report + Issues filter contract");
