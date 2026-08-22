const fs=require('fs'), path=require('path');
const app=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
if(!app.includes('(?:[A-Z][A-Z0-9]*_){1,}[A-Z0-9_]+')) throw new Error('technical ID underscore protection missing');
if(!app.includes('const shouldCollapse = item.role === "analyst"')) throw new Error('analyst-only default collapse missing');
if(!app.includes('Other / clarification')) throw new Error('human gate Other/clarification UI missing');
if(!app.includes('Submit clarification and repair')) throw new Error('human gate clarification submit missing');
console.log('A2012 UI STATIC REGRESSION: PASS');
