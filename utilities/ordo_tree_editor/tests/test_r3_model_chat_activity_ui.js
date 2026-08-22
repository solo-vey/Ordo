
const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");
const css=fs.readFileSync("web/styles.css","utf8");
for(const token of ["activity_events","msg.activities","model-chat-activity"])if(!js.includes(token)&&!css.includes(token))throw new Error("missing "+token);
console.log("PASS Model Chat quiet tool activity UI");
