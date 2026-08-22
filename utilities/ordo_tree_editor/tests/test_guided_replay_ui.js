const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'..');
const app=fs.readFileSync(path.join(root,'web','app.js'),'utf8');
const html=fs.readFileSync(path.join(root,'web','index.html'),'utf8');
for (const needle of ['live-guided-replay','live-guided-replay-file']) if(!html.includes(needle)) throw new Error('missing '+needle);
for (const needle of ['buildGuidedReplay','nextGuidedReplayCall','maybeExitGuidedReplayAtCheckpoint','recorded_model_result']) if(!app.includes(needle)) throw new Error('missing '+needle);
console.log('guided replay UI static checks PASS');
