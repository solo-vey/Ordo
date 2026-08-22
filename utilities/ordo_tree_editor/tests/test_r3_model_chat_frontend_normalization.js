
const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");
for(const t of [
  "function modelChatAnswerText",
  '["answer_markdown","message","answer","content","text","response","output_text","final_response"]',
  'throw new Error("The Model Chat API returned no displayable answer.")'
]) if(!js.includes(t))throw new Error("missing "+t);
console.log("PASS Model Chat frontend normalization contract");
