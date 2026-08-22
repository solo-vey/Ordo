
const fs=require("fs");
const fixture=JSON.parse(fs.readFileSync("tests/fixtures/rfp095_data_lineage.json","utf8"));
const nodes=fixture.nodes||[],edges=(fixture.edges||[]).filter(e=>!e.hidden_projection),byId=new Map(nodes.map(n=>[n.id,n]));
const isT=n=>String(n?.kind||"").startsWith("transform_");
const base=n=>{
  if(!n)return null;
  if(n.kind==="analyst_input")return 0;
  if(n.kind==="derived_state")return 2;
  if((n.kind==="document"||n.kind==="artifact")&&n.artifact_role!=="package_source_resource")return 5;
  if(n.kind==="archive")return 8;
  return null;
};
const rank=n=>{
  if(!isT(n))return base(n);
  const incoming=[],outgoing=[];
  for(const e of edges){
    if(e.target===n.id){const r=base(byId.get(e.source));if(r!==null)incoming.push(r);}
    if(e.source===n.id){const r=base(byId.get(e.target));if(r!==null)outgoing.push(r);}
  }
  const i=incoming.length?Math.max(...incoming):null,o=outgoing.length?Math.max(...outgoing):null;
  if(n.kind==="transform_package"||o===8)return 7;
  if(i===5)return 6;
  if(o===5)return 4;
  if(i===2&&o===2)return 3;
  if((i===0||i===null)&&o===2)return 1;
  if(o===0)return 1;
  if(i===2)return 3;
  if(n.kind==="transform_template")return 4;
  if(n.kind==="transform_analyst")return 1;
  return 3;
};

const dataRanks=new Set([0,2,5,8]);
for(const n of nodes){
  const r=rank(n);
  if(isT(n)&&dataRanks.has(r)) throw new Error(`transformation ${n.id} leaked into data lane ${r}`);
}
const expect=(id,want)=>{
  const n=byId.get("transform:"+id);if(!n)throw new Error("missing "+id);
  const got=rank(n);if(got!==want)throw new Error(`${id}: expected ${want}, got ${got}`);
};
expect("N_RISK_FACTOR_IDENTITY_DRAFT",1);
expect("N_IMPL_EVIDENCE_INTAKE",3);
expect("N_GENERATE_PASSPORT_DRAFT",4);
expect("N_FINALIZE_APPROVED_PASSPORT",6);
expect("N_MATERIALIZE_JIRA_TASK",6);
expect("N_FORM_DELIVERY_PACKAGE",7);
expect("N_OFFER_RUN_EVIDENCE_EXPORT",7);

console.log("PASS real RFP095: transformations/materializations never share data rows");
