const fs=require('fs');
const js=fs.readFileSync(require('path').join(__dirname,'../web/app.js'),'utf8');
const html=fs.readFileSync(require('path').join(__dirname,'../web/index.html'),'utf8');
for(const token of ['sourceDataClassFilter','sourceFlowNodeDataClass','activeSourceFlowGraph','updateSourceFlowDataClassFilter']) if(!js.includes(token)) throw new Error('missing '+token);
if(!html.includes('id="source-flow-data-class-filter"')) throw new Error('missing data class selector');
for(const value of ['business','technical','control','metadata','unclassified']) if(!js.includes(value)) throw new Error('missing class '+value);
console.log('PASS source data class filter');
