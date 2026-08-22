const fs=require('fs');
const js=fs.readFileSync('web/app.js','utf8');
const css=fs.readFileSync('web/styles.css','utf8');
for(const token of [
  'function sourceFlowArtifactPresentation',
  'source-flow-file-kind',
  'artifact-document',
  'artifact-archive'
]) if(!js.includes(token)) throw new Error('missing visual classification token '+token);
for(const token of [
  '.source-flow-node.type-gate_fragment',
  'clip-path:polygon',
  '.source-flow-node.type-artifact::after',
  '.source-flow-node.artifact-archive',
  '.source-flow-file-kind',
  '.source-flow-node.source-flow-upstream',
  '.source-flow-node.source-flow-downstream'
]) if(!css.includes(token)) throw new Error('missing visual styling token '+token);
console.log('PASS Source Data Flow tree visual-language contract');
