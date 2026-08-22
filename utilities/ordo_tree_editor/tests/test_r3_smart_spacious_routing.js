const fs=require('fs'), vm=require('vm');
const js=fs.readFileSync('web/app.js','utf8');
function must(v,m){if(!v) throw new Error(m);}
for(const token of [
  'function spaciousRoutingParticipantIds',
  'function spaciousRoutingEnvelope',
  'function spaciousExternalCorridorLanes',
  'const intervals = { left: [], right: [] }',
  'const leftLane = firstFreeLane("left", edge, baseLane), rightLane = firstFreeLane("right", edge, baseLane);',
  'side = leftScore < rightScore ? "left" : "right"',
  'assignment.side === "left"',
  'const corridorBaseGap = 34, corridorStep = 34;',
  'rightLaneCount: intervals.right.length',
  'leftLaneCount: intervals.left.length'
]) must(js.includes(token), `missing bidirectional Spacious routing contract: ${token}`);

const detStart=js.indexOf('function deterministicEdgeLane');
const start=js.indexOf('function spaciousRoutingParticipantIds');
const end=js.indexOf('function smartSpaciousEdgeGeometry', start);
must(detStart>=0 && start>detStart && end>start, 'routing helpers must be extractable');
const det=js.slice(detStart,start);
const helper=js.slice(start,end);
const sandbox={
  NODE_MIN_HEIGHT:88,
  state:{
    positions:{
      A:{x:300,y:0}, B:{x:300,y:800},
      C:{x:360,y:20}, D:{x:360,y:820},
      E:{x:420,y:40}, F:{x:420,y:840},
      G:{x:480,y:60}, H:{x:480,y:860},
      YELLOW:{x:1800,y:300}
    },
    graph:{edges:[
      {source:'A',target:'B',edge_type:'control_flow'},
      {source:'C',target:'D',edge_type:'control_flow'},
      {source:'E',target:'F',edge_type:'control_flow'},
      {source:'G',target:'H',edge_type:'control_flow'}
    ]}
  },
  nodeSize:()=>({width:205,height:88}),
  treeLayoutMetrics:()=>({verticalGap:112,margin:150,minCanvasWidth:1240})
};
vm.createContext(sandbox);
vm.runInContext(det+helper+'\nthis.route=spaciousExternalCorridorLanes;this.envelope=spaciousRoutingEnvelope;',sandbox);
const envelope=sandbox.envelope();
must(envelope.maxRight < 1000, `unconnected overlay node must not widen routing envelope: ${JSON.stringify(envelope)}`);
const routing=sandbox.route();
const sides=[...routing.lanes.values()].map(v=>v.side);
must(sides.includes('left') && sides.includes('right'), `overlapping long edges should use both outer sides: ${JSON.stringify([...routing.lanes])}`);
for(const value of routing.lanes.values()) must(Number.isInteger(value.lane)&&value.lane>=0,'every routed edge must have deterministic lane index');
const repeated=sandbox.route();
must(JSON.stringify([...routing.lanes])===JSON.stringify([...repeated.lanes]),'bidirectional corridor assignment must be deterministic');
console.log('PASS smart Spacious bidirectional corridor routing regression');
