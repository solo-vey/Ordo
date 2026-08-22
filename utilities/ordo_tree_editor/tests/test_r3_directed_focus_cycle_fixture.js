
const edges=[
  {source:"A",target:"B"},{source:"B",target:"C"},{source:"C",target:"D"},
  {source:"D",target:"C"},{source:"X",target:"B"},{source:"Y",target:"X"},{source:"Y",target:"Z"}
];
function walk(root,dir){
  const visited=new Set([root]),nodes=new Set(),q=[root];
  while(q.length){
    const cur=q.shift();
    for(const e of edges){
      const ok=dir==="up"?e.target===cur:e.source===cur;if(!ok)continue;
      const next=dir==="up"?e.source:e.target;if(visited.has(next))continue;
      visited.add(next);nodes.add(next);q.push(next);
    }
  }
  return nodes;
}
const up=walk("B","up"),down=walk("B","down");
for(const x of ["A","X","Y"])if(!up.has(x))throw new Error("missing upstream "+x);
if(up.has("Z"))throw new Error("upstream switched direction into sibling branch");
for(const x of ["C","D"])if(!down.has(x))throw new Error("missing downstream "+x);
for(const x of ["A","X","Y","Z"])if(down.has(x))throw new Error("downstream leaked "+x);
console.log("PASS directed cycles and direction isolation");
