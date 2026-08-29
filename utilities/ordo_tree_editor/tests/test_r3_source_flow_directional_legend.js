const fs=require('fs');
const js=fs.readFileSync('web/app.js','utf8');
const html=fs.readFileSync('web/index.html','utf8');
const css=fs.readFileSync('web/styles.css','utf8');
function must(v,m){if(!v)throw new Error(m);}
for(const token of [
  'data-legend-kind="trace" data-legend-value="upstream"',
  'data-legend-kind="trace" data-legend-value="downstream"'
]) must(html.includes(token),`directional legend must use trace semantics: ${token}`);
for(const token of [
  'sourceTraceDirection:null',
  'function sourceFlowTraceRoot()',
  'function sourceFlowActiveTrace',
  'if(kind==="trace")',
  'available=hasSemanticEdges',
  'Choose ${value}, then click a graph node to set the trace root',
  'if(state.lineage.sourceTraceDirection)state.lineage.sourceFocusRoot=node.id'
]) must(js.includes(token),`missing directional trace interaction contract: ${token}`);
must(css.includes('.source-flow-edge.downstream{stroke:#258064;stroke-width:2.2;stroke-dasharray:7 4}'),'Downstream must differ by color and dash pattern');
must(css.includes('.source-flow-edge.upstream{stroke:#2d6fb7;stroke-width:2.2}'),'Upstream must remain solid blue');
console.log('PASS Source Data Flow directional legend regression');
