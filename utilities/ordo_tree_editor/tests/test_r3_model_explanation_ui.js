const fs=require('fs'), path=require('path');
const app=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
const html=fs.readFileSync(path.join(__dirname,'..','web','index.html'),'utf8');
const css=fs.readFileSync(path.join(__dirname,'..','web','styles.css'),'utf8');
function must(x,msg){if(!x){console.error(msg);process.exit(1)}}
for(const token of ['data-inspector-tab="explanation"','id="node-explanation-view"','id="header-model-settings"','data-workspace-tab="upload"']) must(html.includes(token),token);
for(const token of ['/api/explain','Explain with model','renderNodeExplanationTab','python_resource','resourceExplanations']) must(app.includes(token),token);
for(const token of ['.model-explanation-toolbar','.template-resource-explain','.resource-model-explanation']) must(css.includes(token),token);
console.log('PASS model explanation UI contract');
