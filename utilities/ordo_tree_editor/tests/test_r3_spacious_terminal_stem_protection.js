const fs=require('fs'),vm=require('vm');
const js=fs.readFileSync('web/app.js','utf8');
function must(v,m){if(!v)throw new Error(m);}
for(const token of [
  'function spaciousRouteSegmentsWithRoles',
  'function spaciousTerminalStemInvariant',
  'terminalConflicts * 8000000',
  'score.terminalConflicts * 1000',
  '!spaciousTerminalStemInvariant(route.originalPoints, candidate)',
  'terminal:index===0||index===best.segs.length-1'
]) must(js.includes(token),`missing terminal-stem protection contract: ${token}`);
must((js.match(/function spaciousPlannedInternalRoutes\(\)/g)||[]).length===1,'Spacious planner must have exactly one active definition');
const parts=[];
for(const [a,b] of [
  ['function spaciousIntervalsOverlap','function spaciousBuildReservedSegments'],
  ['function spaciousParseOrthogonalPath','function drawEdges']
]){
  const start=js.indexOf(a),end=js.indexOf(b,start);must(start>=0&&end>start,`cannot extract ${a}`);parts.push(js.slice(start,end));
}
const sandbox={state:{treeLayoutDensity:'spacious',positions:{},graph:{nodes:[]}},nodeSize:()=>({width:205,height:88}),treeLayoutMetrics:()=>({margin:54,minCanvasWidth:1000})};
vm.createContext(sandbox);
vm.runInContext(parts.join('\n')+'\nthis.post=spaciousPostProcessGeometries;this.parse=spaciousParseOrthogonalPath;this.segs=spaciousSegmentsFromPoints;this.cross=spaciousSegmentsCross;',sandbox);
const trunk={edge:{source:'A',target:'D'},relation:'control_flow',geometry:{path:'M 20 20 L 20 100 L 420 100 L 420 330',label:{x:220,y:94}}};
const terminal={edge:{source:'B',target:'E'},relation:'control_flow',geometry:{path:'M 120 20 L 120 250',label:{x:126,y:130}}};
const result=sandbox.post([trunk,terminal]);
const routed=sandbox.parse(result[0].geometry.path),original=sandbox.parse(trunk.geometry.path);
must(routed[0].x===original[0].x&&routed[0].y===original[0].y,'source endpoint must not move');
must(routed.at(-1).x===original.at(-1).x&&routed.at(-1).y===original.at(-1).y,'target endpoint / arrow anchor must not move');
const rs=sandbox.segs(routed),os=sandbox.segs(original);
must(rs[0].orientation===os[0].orientation&&rs.at(-1).orientation===os.at(-1).orientation,'terminal stem orientation must be preserved');
let terminalCrossings=0;for(const a of rs)for(const b of sandbox.segs(sandbox.parse(result[1].geometry.path)))if(sandbox.cross(a,b,1))terminalCrossings++;
must(terminalCrossings===0,'post-pass must move the trunk away from another edge terminal stem when a clean lane exists');
console.log('PASS Spacious terminal-stem / arrow-anchor protection regression');
