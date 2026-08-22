const fs=require('fs');
const src=fs.readFileSync(require('path').join(__dirname,'..','web','app.js'),'utf8');
if(!src.includes('title: ["Title", "title"]')) throw new Error('title is not a known inspector field');
if(!src.includes('const knownSectionOrder=["title", "id", "kind", "purpose", "question"')) throw new Error('title is not first in known field ordering');
console.log('PASS inspector title known-first');
