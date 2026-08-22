
const fs=require("fs");
const f=JSON.parse(fs.readFileSync("tests/fixtures/rfp095_data_lineage.json","utf8"));
const edges=(f.edges||[]).filter(e=>!e.hidden_projection),root="state:business_meaning";
function walk(dir){
  const visited=new Set([root]),dist=new Map([[root,0]]),used=[],q=[root];
  while(q.length){
    const cur=q.shift(),d=dist.get(cur);
    for(const e of edges){
      const ok=dir==="up"?e.target===cur:e.source===cur;if(!ok)continue;
      const next=dir==="up"?e.source:e.target;if(!next||visited.has(next))continue;
      visited.add(next);dist.set(next,d+1);used.push(e);q.push(next);
    }
  }
  return {dist,used};
}
const up=walk("up"),down=walk("down");
const maxUp=Math.max(...up.dist.values()),maxDown=Math.max(...down.dist.values());
if(maxUp<1||maxDown<1)throw new Error("real RFP fixture does not produce both sides");
console.log(`PASS RFP095 signed-distance focus: upstream depth ${maxUp}, downstream depth ${maxDown}`);
