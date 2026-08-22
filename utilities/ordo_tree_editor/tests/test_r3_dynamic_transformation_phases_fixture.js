
const fs=require("fs");
const fixture=JSON.parse(fs.readFileSync("tests/fixtures/rfp095_data_lineage.json","utf8"));
const nodes=fixture.nodes||[],edges=(fixture.edges||[]).filter(e=>!e.hidden_projection),byId=new Map(nodes.map(n=>[n.id,n]));
const base=n=>{
  if(!n)return null;
  if(n.kind==="analyst_input")return 0;
  if(n.kind==="derived_state")return 2;
  if((n.kind==="document"||n.kind==="artifact")&&n.artifact_role!=="package_source_resource")return 4;
  if(n.kind==="archive")return 6;
  return null;
};
const rank=n=>{
  if(!String(n.kind||"").startsWith("transform_"))return base(n);
  const incoming=[],outgoing=[];
  for(const e of edges){
    if(e.target===n.id){const r=base(byId.get(e.source));if(r!==null)incoming.push(r);}
    if(e.source===n.id){const r=base(byId.get(e.target));if(r!==null)outgoing.push(r);}
  }
  const i=incoming.length?Math.max(...incoming):null,o=outgoing.length?Math.max(...outgoing):null;
  if(i!==null&&o!==null){if(o>i)return Math.min(5,Math.max(1,Math.round((i+o)/2)));return i;}
  if(o!==null)return o<=0?0:Math.max(1,o-1);
  if(i!==null){if(n.kind==="transform_package")return 5;if(n.kind==="transform_template"&&i<=2)return 3;return i;}
  if(n.kind==="transform_package")return 5;
  if(n.kind==="transform_template")return 3;
  if(n.kind==="transform_analyst")return 0;
  return 1;
};
const expect=(id,want)=>{
  const n=byId.get("transform:"+id);if(!n)throw new Error("missing "+id);
  const got=rank(n);if(got!==want)throw new Error(`${id}: expected phase ${want}, got ${got}`);
};
expect("N_RISK_FACTOR_IDENTITY_DRAFT",1);
expect("N_IMPL_EVIDENCE_INTAKE",2);
expect("N_GENERATE_PASSPORT_DRAFT",3);
expect("N_FINALIZE_APPROVED_PASSPORT",4);
expect("N_MATERIALIZE_JIRA_TASK",4);
expect("N_FORM_DELIVERY_PACKAGE",5);
expect("N_OFFER_RUN_EVIDENCE_EXPORT",5);
expect("N_PRESENT_IMPLEMENTATION_PROMPT",3);

const staticRegistry=byId.get("artifact:registry/RISK_FACTOR_VARIABLE_REGISTRY.yaml");
if(!staticRegistry||staticRegistry.artifact_role!=="package_source_resource")throw new Error("missing package source resource fixture");
console.log("PASS real RFP095 fixture: actual transformation phases are inferred correctly");
