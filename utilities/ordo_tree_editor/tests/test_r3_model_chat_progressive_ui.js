
const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");
const html=fs.readFileSync("web/index.html","utf8");
for(const token of ["/api/model-chat-start","/api/model-chat-status","/api/model-chat-cancel","waitForModelChatRun","activityBuffer"])if(!js.includes(token))throw new Error("missing "+token);
if(html.includes('>Upload YAML<'))throw new Error("standalone Upload YAML must be removed from first page");
if(!html.includes(">Upload Playbook<"))throw new Error("Upload Playbook must remain");
console.log("PASS progressive Model Chat UI and first-page upload contract");
