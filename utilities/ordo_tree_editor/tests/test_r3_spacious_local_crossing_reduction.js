const fs=require('fs'), vm=require('vm');
const js=fs.readFileSync('web/app.js','utf8');
function must(v,m){ if(!v) throw new Error(m); }
for(const token of [
  'function spaciousBuildReservedSegments',
  'function spaciousInternalRouteCandidates',
  'function spaciousScoreRouteCandidate',
  'function spaciousPlannedInternalRoutes',
  'const planned = spaciousPlannedInternalRoutes().get(`${sourceId}->${targetId}`);'
]) must(js.includes(token), `missing local crossing-reduction contract: ${token}`);
const start=js.indexOf('function deterministicEdgeLane');
const end=js.indexOf('function edgeGeometry', start);
must(start>=0 && end>start, 'routing planner section must be extractable');
const section=js.slice(start,end);
const sandbox={
  NODE_MIN_HEIGHT:88,
  state:{
    treeLayoutDensity:'spacious',
    positions:{
      A:{x:40,y:20},
      B:{x:360,y:120},
      C:{x:360,y:350}
    },
    graph:{
      nodes:[{id:'A'},{id:'B'},{id:'C'}],
      edges:[
        {source:'A',target:'B',edge_type:'control_flow'},
        {source:'B',target:'C',edge_type:'control_flow'}
      ]
    }
  },
  nodeSize:()=>({width:205,height:88}),
  treeLayoutMetrics:()=>({verticalGap:112,margin:150,minCanvasWidth:1240})
};
vm.createContext(sandbox);
vm.runInContext(section+'\nthis.route=smartSpaciousEdgeGeometry; this.reset=resetSpaciousInternalMiniLaneCache;',sandbox);
sandbox.reset();
const route=sandbox.route(sandbox.state.positions.A, sandbox.state.positions.B, 'A', 'B');
must(route && typeof route.path==='string' && route.path.startsWith('M '), `planned local route must be produced: ${JSON.stringify(route)}`);
must(route.path.includes(' L ') && route.path.split(' L ').length >= 3, `route should remain orthogonal and multi-segment: ${route.path}`);
must(route.mode==='vertical' || route.mode==='horizontal' || route.mode===undefined, `route mode should be exposed when planned, got: ${JSON.stringify(route)}`);
console.log('PASS Spacious local crossing-reduction regression');
