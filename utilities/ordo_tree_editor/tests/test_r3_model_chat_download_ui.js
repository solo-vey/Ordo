
const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");
const py=fs.readFileSync("editor_service.py","utf8");
for(const token of ["file.download_url","/api/model-chat-workspace-file","Content-Disposition","workspace.archive"])if(!js.includes(token)&&!py.includes(token))throw new Error("missing "+token);
console.log("PASS binary workspace download + archive contract");
