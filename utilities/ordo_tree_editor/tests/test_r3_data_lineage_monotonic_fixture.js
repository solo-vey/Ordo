
// Mini-fixture mirrors: business_meaning -> transform -> derived -> document,
// plus an illegal derived -> deterministic transform -> sibling-derived branch.
const layers={analyst_input:0,transform_model:1,transform_deterministic:1,derived_state:2,document:3,archive:4};
const nodes={
  business:{kind:"analyst_input"},
  t1:{kind:"transform_model"},
  d1:{kind:"derived_state"},
  doc:{kind:"document"},
  zip:{kind:"archive"},
  tBack:{kind:"transform_deterministic"},
  sibling:{kind:"derived_state"}
};
const edges=[
  ["business","t1"],["t1","d1"],["d1","doc"],["doc","zip"],
  ["d1","tBack"],["tBack","sibling"]
];
const down=(a,b)=>layers[nodes[b].kind]>=layers[nodes[a].kind];
const seen=new Set(["business"]),q=["business"];
while(q.length){
  const cur=q.shift();
  for(const [a,b] of edges) if(a===cur&&down(a,b)&&!seen.has(b)){seen.add(b);q.push(b);}
}
for(const id of ["business","t1","d1","doc","zip"]) if(!seen.has(id)) throw new Error("missing legal causal node "+id);
for(const id of ["tBack","sibling"]) if(seen.has(id)) throw new Error("illegal backward branch leaked into downstream focus: "+id);
console.log("PASS monotonic fixture blocks derived -> transformation -> sibling branch");
