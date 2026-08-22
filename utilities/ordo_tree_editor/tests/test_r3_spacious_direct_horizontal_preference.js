const fs=require('fs'), vm=require('vm');
const js=fs.readFileSync('web/app.js','utf8');
function must(v,m){ if(!v) throw new Error(m); }
const match=js.match(/function spaciousDirectHorizontalGeometry\(sourceId, targetId\) \{[\s\S]*?\n\}/);
must(match,'direct horizontal helper must exist');
must(js.includes('if (spaciousDirectHorizontalGeometry(edge.source, edge.target)) continue;'),'direct horizontal edges must be excluded from corridor lane allocation');
must(js.includes('const directHorizontal = spaciousDirectHorizontalGeometry(sourceId, targetId);\n  if (directHorizontal) return directHorizontal;'),'Spacious geometry must prefer direct horizontal route before corridor routing');
const sandbox={
  state:{positions:{A:{x:0,y:100},B:{x:400,y:100}},graph:{nodes:[{id:'A'},{id:'B'}]}},
  nodeSize:(id)=>({width:100,height:80})
};
vm.createContext(sandbox);
vm.runInContext(match[0]+'\nthis.route=spaciousDirectHorizontalGeometry;',sandbox);
let route=sandbox.route('A','B');
must(route && route.path==='M 100 140 L 400 140','aligned unobstructed nodes should use a straight horizontal segment');
sandbox.state.positions.C={x:220,y:100};
sandbox.state.graph.nodes.push({id:'C'});
route=sandbox.route('A','B');
must(route===null,'a node intersecting the horizontal segment must force fallback routing');
sandbox.state.positions.C={x:220,y:260};
route=sandbox.route('A','B');
must(route && route.path==='M 100 140 L 400 140','a non-intersecting node must not block the direct horizontal route');
console.log('PASS Spacious direct-horizontal preference regression');
