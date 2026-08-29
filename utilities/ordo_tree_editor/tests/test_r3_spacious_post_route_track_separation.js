const fs=require('fs'),vm=require('vm');
const js=fs.readFileSync('web/app.js','utf8');
function must(v,m){if(!v)throw new Error(m);}
for(const token of [
  'function spaciousPostProcessGeometries(items)',
  'function spaciousRouteConflictScore',
  'function spaciousShiftInternalSegment',
  'function spaciousRouteWithinCanvas',
  '84, -84, 108, -108, 140, -140, 180, -180',
  'const routed = spaciousPostProcessGeometries(planned);'
]) must(js.includes(token),`missing main-tree post-route separation contract: ${token}`);
const parts=[];
for(const [a,b] of [
  ['function spaciousIntervalsOverlap','function spaciousBuildReservedSegments'],
  ['function spaciousParseOrthogonalPath','function drawEdges']
]){
  const start=js.indexOf(a),end=js.indexOf(b,start);
  must(start>=0&&end>start,`cannot extract ${a}`);parts.push(js.slice(start,end));
}
const sandbox={
  state:{treeLayoutDensity:'spacious',positions:{},graph:{nodes:[]}},
  nodeSize:()=>({width:205,height:88}),
  treeLayoutMetrics:()=>({margin:54,minCanvasWidth:1000})
};
vm.createContext(sandbox);
vm.runInContext(parts.join('\n')+'\nthis.post=spaciousPostProcessGeometries;this.parse=spaciousParseOrthogonalPath;this.segs=spaciousSegmentsFromPoints;this.cross=spaciousSegmentsCross;',sandbox);
const items=[
  {edge:{source:'A',target:'D'},relation:'control_flow',geometry:{path:'M 20 20 L 20 100 L 420 100 L 420 330',label:{x:220,y:94}}},
  {edge:{source:'B',target:'E'},relation:'control_flow',geometry:{path:'M 120 20 L 120 250',label:{x:126,y:130}}},
  {edge:{source:'C',target:'F'},relation:'control_flow',geometry:{path:'M 320 20 L 320 250',label:{x:326,y:130}}}
];
function crossings(result){
  const routes=result.map(x=>sandbox.segs(sandbox.parse(x.geometry.path)||[]));let count=0;
  for(let i=0;i<routes.length;i++)for(let j=i+1;j<routes.length;j++)for(const a of routes[i])for(const b of routes[j])if(sandbox.cross(a,b,1))count++;
  return count;
}
const before=crossings(items),afterItems=sandbox.post(items),after=crossings(afterItems);
must(before>=2,`fixture must begin with multiple crossings, got ${before}`);
must(after<before,`post-route separation must reduce long-track crossings (${before} -> ${after})`);
must(afterItems[0].geometry.path!==items[0].geometry.path,'conflicted horizontal trunk should move to a cleaner mini-lane');
console.log('PASS Spacious post-route track separation regression');
