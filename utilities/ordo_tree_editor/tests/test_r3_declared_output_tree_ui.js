const fs=require('fs');
const js=fs.readFileSync('web/app.js','utf8');
const css=fs.readFileSync('web/styles.css','utf8');
for(const token of ['declared_output','declares_output','outputProducerGroups','Declared output']){
  if(!js.includes(token)) throw new Error('missing UI contract token '+token);
}
for(const token of ['.node.output','.edge-line.edge-declares_output','.edge-label-declares_output']){
  if(!css.includes(token)) throw new Error('missing output semantic styling '+token);
}
if(!js.includes('node.producers') || !js.includes('producerId')) throw new Error('output layout is not producer-aware');
console.log('PASS');
