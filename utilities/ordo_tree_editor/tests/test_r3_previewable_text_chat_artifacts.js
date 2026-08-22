const fs=require('fs'), path=require('path');
const app=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
const html=fs.readFileSync(path.join(__dirname,'..','web','index.html'),'utf8');
const css=fs.readFileSync(path.join(__dirname,'..','web','styles.css'),'utf8');
function must(x,msg){ if(!x.includes(msg)){ console.error('missing',msg); process.exit(1); } }
must(app,'function isPreviewableTextArtifact(path)');
for(const ext of ['json','ya?ml','py','csv','xml','html?','css','jsx?','tsx?','sql']) must(app,ext);
must(app,'if (isPreviewableTextArtifact(item.artifact.path))');
must(app,'JSON.stringify(JSON.parse(text), null, 2)');
must(app,'artifact-source-preview');
must(html,'id="artifact-preview-subtitle"');
must(css,'.artifact-source-preview');
console.log('PASS previewable text chat artifacts');
