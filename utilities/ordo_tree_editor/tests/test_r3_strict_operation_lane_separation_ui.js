
const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");
for(const t of [
  'label:"Analyst input / collection"',
  'label:"Transformation · input → state"',
  'label:"Derived state"',
  'label:"Transformation · state processing"',
  'label:"Transformation · state → document / materialization"',
  'label:"Document"',
  'label:"Transformation · document processing / rematerialization"',
  'label:"Transformation · document → package"',
  'label:"Archive / package"',
  'category:"operation"',
  'category:"data"'
]) if(!js.includes(t)) throw new Error("missing "+t);
console.log("PASS strict operation/data lane UI contract");
