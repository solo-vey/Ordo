const fs=require('fs'), vm=require('vm');
const js=fs.readFileSync('web/app.js','utf8');
function must(v,m){if(!v)throw new Error(m);}
for(const token of [
  'function sourceFlowLayoutScaled(graph,spacingScale=1)',
  'scales=[1,1.16,1.34,1.56,1.82,2.12,2.46,2.84]',
  'if(stats.blocked===0&&stats.overlap===0)break;',
  'overlap*2000000',
  'for(const d of [0,10,-10,20,-20,32,-32,46,-46,64,-64,84,-84,108,-108,136,-136])'
]) must(js.includes(token),`missing adaptive zero-overlap contract: ${token}`);
const start=js.indexOf('const SOURCE_FLOW_CARD_W=196');
const end=js.indexOf('function redrawSourceFlowEdges',start);
must(start>=0&&end>start,'source-flow layout/routing section must be extractable');
const section=js.slice(start,end);
const sandbox={state:{lineage:{sourceDirection:'TB'}},console};
vm.createContext(sandbox);
vm.runInContext(section+'\nthis.adaptive=sourceFlowAdaptiveLayout;this.plan=sourceFlowPlanRoutes;',sandbox);
const graph={nodes:[
  {id:'A',label:'A'},{id:'B',label:'B'},{id:'C',label:'C'},
  {id:'D',label:'D'},{id:'E',label:'E'},{id:'F',label:'F'}
],edges:[
  {from:'A',to:'D',type:'dependency'},
  {from:'A',to:'E',type:'dependency'},
  {from:'B',to:'D',type:'dependency'},
  {from:'B',to:'F',type:'dependency'},
  {from:'C',to:'E',type:'dependency'},
  {from:'C',to:'F',type:'dependency'}
]};
const layout=sandbox.adaptive(graph);
must(layout&&layout.positions&&layout.spacingScale>=1,'adaptive layout must return positions and scale');
const routes=sandbox.plan(graph,layout.positions,'TB');
must(routes.size===6,'all edges must be routed');
must(routes.stats.blocked===0,'adaptive routing must not pass through node boxes');
must(routes.stats.overlap===0,`distinct Data Flow edges must not share collinear segments in fixture, got ${JSON.stringify(routes.stats)}`);
console.log('PASS Source Data Flow zero-overlap adaptive layout regression');
