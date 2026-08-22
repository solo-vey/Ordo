
const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");
const html=fs.readFileSync("web/index.html","utf8");
for(const token of ["model-chat-export","model-chat-export-debug","Export Chat","Export Chat Debug"]){
  if(!html.includes(token))throw new Error("missing UI "+token);
}
for(const token of ["async function exportModelChat","usageHistory","agentTrace","generatedFiles","/api/model-chat-export"]){
  if(!js.includes(token))throw new Error("missing JS "+token);
}
console.log("PASS Model Chat export UI contract");
