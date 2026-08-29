const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'..');
const js=fs.readFileSync(path.join(root,'web/app.js'),'utf8');
const css=fs.readFileSync(path.join(root,'web/styles.css'),'utf8');
function must(v,m){if(!v) throw new Error(m);}
for(const token of [
  'function sourceFlowNodeTypeIcon(type)',
  'class="source-flow-type-icon"',
  'sourceFlowNodeTypeIcon(node.type)',
  'transformation:"ƒ"',
  'variable:"{}"',
  'gate:"◇"'
]) must(js.includes(token),`missing Hybrid Scheme B renderer contract: ${token}`);
for(const token of [
  'alpha.20.0.197-dev — Hybrid Scheme B typed source-flow nodes',
  '--sf-type-accent:#5f7fa8',
  '--sf-type-accent:#756b9a',
  '--sf-type-accent:#4f837a',
  '--sf-type-accent:#9a7132',
  '.source-flow-type-icon{',
  '.source-flow-node::before{',
  'clip-path:none',
  '.source-flow-node.type-artifact::after{display:none}'
]) must(css.includes(token),`missing Hybrid Scheme B style contract: ${token}`);
const gateBlock=css.slice(css.lastIndexOf('.source-flow-node.type-gate,'),css.lastIndexOf('.source-flow-node.type-artifact{'));
must(gateBlock.includes('border-radius:9px')&&gateBlock.includes('clip-path:none'),'gate must stay in the rectangular visual family');
console.log('PASS source-flow Hybrid Scheme B regression');
