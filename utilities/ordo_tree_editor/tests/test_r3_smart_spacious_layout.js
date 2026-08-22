const fs=require('fs'), vm=require('vm');
const js=fs.readFileSync('web/app.js','utf8');
function must(v,m){if(!v) throw new Error(m);}
for(const token of [
  'function smartSpaciousOrderedGroups',
  'for (let pass = 0; pass < 4; pass += 1)',
  'function relaxSmartSpaciousPositions',
  'function smartSpaciousEdgeGeometry',
  'function deterministicEdgeLane',
  'function spaciousExternalCorridorLanes',
  'assignment.side === "left"',
  'if ((state.treeLayoutDensity || "normal") === "spacious") return smartSpaciousEdgeGeometry'
]) must(js.includes(token), `missing smart Spacious contract: ${token}`);

const start=js.indexOf('function smartSpaciousOrderedGroups');
const end=js.indexOf('function relaxSmartSpaciousPositions', start);
must(start>=0 && end>start, 'smart ordering helper must be extractable');
const helper=js.slice(start,end);
const sandbox={state:{treeLayoutDensity:'spacious'}, result:null};
vm.createContext(sandbox);
vm.runInContext(helper, sandbox);
const groups=new Map([[0,['A','B']],[1,['X','Y']]]);
const levels=new Map([['A',0],['B',0],['X',1],['Y',1]]);
const nodes=['A','B','X','Y'].map(id=>({id}));
const edges=[{source:'A',target:'Y',edge_type:'control_flow'},{source:'B',target:'X',edge_type:'control_flow'}];
const ordered=sandbox.smartSpaciousOrderedGroups(groups,levels,nodes,edges);
const l0=ordered.get(0), l1=ordered.get(1);
const pos0=new Map(l0.map((id,i)=>[id,i])), pos1=new Map(l1.map((id,i)=>[id,i]));
const crossing=(pos0.get('A')-pos0.get('B'))*(pos1.get('Y')-pos1.get('X'))<0;
must(!crossing, `smart ordering should remove simple two-edge crossing, got ${JSON.stringify([l0,l1])}`);
const again=sandbox.smartSpaciousOrderedGroups(groups,levels,nodes,edges);
must(JSON.stringify([...again])===JSON.stringify([...ordered]), 'smart ordering must be deterministic');
console.log('PASS smart Spacious topology ordering regression');
