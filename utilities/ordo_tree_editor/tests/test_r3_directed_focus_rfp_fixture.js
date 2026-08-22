
const fs=require("fs");
const f=JSON.parse(fs.readFileSync("tests/fixtures/rfp095_data_lineage.json","utf8"));
const edges=(f.edges||[]).filter(e=>!e.hidden_projection),ids=new Set((f.nodes||[]).map(n=>n.id));
const root="state:business_meaning";if(!ids.has(root))throw new Error("missing business_meaning");
function walk(dir){
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
const up=walk("up"),down=walk("down");
if(!down.size)throw new Error("business_meaning has no downstream in fixture");
console.log(`PASS RFP095 business_meaning: ${up.size} upstream / ${down.size} downstream`);
