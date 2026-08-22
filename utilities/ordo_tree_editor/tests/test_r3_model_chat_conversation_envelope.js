
const fs=require("fs"),vm=require("vm");
const js=fs.readFileSync("web/app.js","utf8");
const a=js.indexOf("function modelChatStructuredAnswer"),b=js.indexOf("async function sendModelChat()",a);
if(a<0||b<0)throw new Error("missing frontend normalizer");
const code=js.slice(a,b)+"\nthis.A=modelChatAnswerText;";
const ctx={};vm.createContext(ctx);vm.runInContext(code,ctx);
const raw=JSON.stringify({conversation:[{role:"assistant",content:"Привіт!"}]});
if(ctx.A({answer_markdown:raw})!=="Привіт!")throw new Error("serialized conversation envelope not unwrapped");
if(ctx.A({conversation:[{role:"assistant",content:"Hello"}]})!=="Hello")throw new Error("object conversation envelope not unwrapped");
console.log("PASS frontend conversation envelope extraction");
