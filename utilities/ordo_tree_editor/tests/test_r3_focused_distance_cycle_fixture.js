
const edges=[
  {source:"A",target:"B"},{source:"B",target:"R"},
  {source:"R",target:"C"},{source:"C",target:"D"},{source:"D",target:"C"},
  {source:"X",target:"B"},{source:"R",target:"E"},{source:"E",target:"F"}
];
function walk(root,dir){
  const visited=new Set([root]),dist=new Map([[root,0]]),used=[],q=[root];
  while(q.length){
    const cur=q.shift(),d=dist.get(cur);
    for(const e of edges){
      const ok=dir==="up"?e.target===cur:e.source===cur;if(!ok)continue;
      const next=dir==="up"?e.source:e.target;
      if(!next||visited.has(next))continue;
      visited.add(next);dist.set(next,d+1);used.push(e);q.push(next);
    }
  }
  return {dist,used};
}
const up=walk("R","up"),down=walk("R","down");
if(up.dist.get("B")!==1||up.dist.get("A")!==2||up.dist.get("X")!==2)throw new Error("bad upstream distances");
if(down.dist.get("C")!==1||down.dist.get("D")!==2||down.dist.get("E")!==1||down.dist.get("F")!==2)throw new Error("bad downstream distances");
if(down.used.some(e=>e.source==="D"&&e.target==="C"))throw new Error("cycle-closing edge was included");
console.log("PASS focused BFS distance + cycle protection");
