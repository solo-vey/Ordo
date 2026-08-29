const fs=require('fs'), vm=require('vm');
const js=fs.readFileSync('web/app.js','utf8');
function must(v,m){if(!v)throw new Error(m);}
for(const token of [
  'function sourceFlowSegments',
  'function sourceFlowSegmentOverlap',
  'function sourceFlowSegmentCross',
  'function sourceFlowSegmentHitsNode',
  'function sourceFlowRouteCandidates',
  'function sourceFlowPlanRoutes',
  'overlap*2000000+cross*4000',
  'function sourceFlowBandLaneAssignments',
  'routes.stats={overlap:totalOverlap,cross:totalCross,blocked:totalBlocked',
  'function sourceFlowAdaptiveLayout(graph)',
  'const direction=state.lineage.sourceDirection||"TB",planned=sourceFlowPlanRoutes(graph,positions,direction);',
  'for(let sweep=0;sweep<6;sweep++)',
  'reorder(ordered[li][1],outgoing)'
]) must(js.includes(token),`missing smart Data Flow routing contract: ${token}`);
const start=js.indexOf('const SOURCE_FLOW_CARD_W=196');
const end=js.indexOf('function updateSourceFlowTransform',start);
must(start>=0&&end>start,'source-flow routing helpers must be extractable');
const section=js.slice(start,end);
const sandbox={state:{lineage:{}},console};
vm.createContext(sandbox);
vm.runInContext(section+'\nthis.plan=sourceFlowPlanRoutes;this.cross=sourceFlowSegmentCross;this.segments=sourceFlowSegments;',sandbox);
const graph={nodes:[{id:'A'},{id:'B'},{id:'C'},{id:'D'}],edges:[
  {from:'A',to:'D',type:'dependency'},
  {from:'B',to:'C',type:'dependency'}
]};
const positions={A:{x:0,y:0},B:{x:300,y:0},C:{x:0,y:220},D:{x:300,y:220}};
const routes=sandbox.plan(graph,positions,'TB');
must(routes.size===2,'planner must produce all visible dependency routes');
for(const path of routes.values()) must(/^M /.test(path)&&path.includes(' L '),'planned routes must stay orthogonal');
console.log('PASS smart Source Data Flow routing regression');
