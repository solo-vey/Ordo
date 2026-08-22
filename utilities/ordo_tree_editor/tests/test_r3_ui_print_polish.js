const fs=require('fs'), path=require('path');
const app=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
const css=fs.readFileSync(path.join(__dirname,'..','web','styles.css'),'utf8');
function must(v,x){if(!v.includes(x)){console.error('missing',x);process.exit(1)}}
for(const x of ['templateResourcePreviewMode','data-resource-preview-mode="rendered"','Preview</button>','Source</button>','cached?"Explained"','rex?"Explained"','break-inside:auto','break-after:avoid-page']) must(app,x);
for(const x of ['height:48px','template-resource-preview-tabs','margin-left:auto','template-resource-preview-rendered']) must(css,x);
console.log('PASS R3 UI/print polish');
