
const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");
const css=fs.readFileSync("web/styles.css","utf8");

for(const token of [
  'model-explanation-markdown">${renderBasicMarkdown(cached.explanation||"")}',
  'resource-model-explanation-markdown">${renderBasicMarkdown(rex.explanation||"")}',
  'verification-explanation-markdown"; body.innerHTML=renderBasicMarkdown(cached.explanation||"")',
  'role==="assistant"?renderBasicMarkdown(msg.content||"")'
]) if(!js.includes(token)) throw new Error("missing markdown renderer: "+token);

for(const forbidden of [
  'escapeHtml(cached.explanation).replace(/\\n/g,"<br>")',
  'esc(rex.explanation).replace(/\\n/g,"<br>")',
  'escapeHtml(rex.explanation).replace(/\\n/g,"<br>")'
]) if(js.includes(forbidden)) throw new Error("raw explanation renderer remains: "+forbidden);

for(const token of ['.model-explanation-markdown','.resource-model-explanation-markdown','.verification-explanation-markdown'])
  if(!css.includes(token)) throw new Error("missing explanation markdown css "+token);

console.log("PASS unified model explanation Markdown rendering");
