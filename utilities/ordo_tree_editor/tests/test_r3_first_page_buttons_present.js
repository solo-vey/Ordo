const fs=require("fs");
const html=fs.readFileSync("web/index.html","utf8");
for(const token of ['data-workspace-tab="upload"','id="package-file-input"','id="gitlab-playbook-browser"','id="header-model-settings"'])
  if(!html.includes(token)) throw new Error("missing startup control "+token);
for(const obsolete of ['id="empty-model-settings"','id="empty-model-chat"'])
  if(html.includes(obsolete)) throw new Error("obsolete first-page control still present "+obsolete);
console.log("PASS dedicated Upload Playbook startup controls are present");
