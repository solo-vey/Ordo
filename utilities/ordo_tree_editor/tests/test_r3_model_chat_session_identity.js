const fs=require('fs');
const js=fs.readFileSync('web/app.js','utf8');
if(!js.includes('modelChat:{messages:[],attachments:[],busy:false,sessionId:liveSessionId,')) throw new Error('Model Chat session must share configured live session identity');
const sends=(js.match(/session_id:state\.modelChat\.sessionId/g)||[]).length;
if(sends<2) throw new Error('Model Chat send and debug export must use the same session id');
console.log('PASS Model Chat send/export workspace session identity');
