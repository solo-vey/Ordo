
const fs=require('fs'),vm=require('vm');
const js=fs.readFileSync('web/app.js','utf8'),data=JSON.parse(fs.readFileSync('tests/fixtures/rfp095_data_lineage.json','utf8'));
const start=js.indexOf('const LINEAGE_CARD_W='),end=js.indexOf('function lineageIssueNodes()',start),ctx={console};
vm.createContext(ctx);vm.runInContext(js.slice(start,end)+'\nthis.__api={lineageSemanticLayer,lineageFocusedSlice};',ctx);
const by=new Map(data.nodes.map(n=>[n.id,n]));
function check(id){
 const slice=ctx.__api.lineageFocusedSlice(data,id),v=[...slice.visible],layer=ctx.__api.lineageSemanticLayer(by.get(id));
 const same=v.filter(x=>ctx.__api.lineageSemanticLayer(by.get(x))===layer);
 if(same.length!==1||same[0]!==id)throw Error(`${id}: selected layer siblings visible: ${same.join(', ')}`);
 return v;
}
const collect=check('transform:N_COLLECT_IMPLEMENTATION_PROMPT_DETAILS');
const otherTransforms=collect.filter(x=>x!== 'transform:N_COLLECT_IMPLEMENTATION_PROMPT_DETAILS' && String(by.get(x)?.kind||'').startsWith('transform_'));
if(otherTransforms.length)throw Error(`selected transformation shows sibling transformations: ${otherTransforms.join(', ')}`);
// The eight captured analyst-answer fields are actual outputs of this analyst-interaction node.
for(const x of ['state:implementation_target_module','state:implementation_handler_strategy'])if(!collect.includes(x))throw Error(`missing actual selected-node output ${x}`);
const docStatus=check('state:risk_factor_identity.document_status');
if(!docStatus.includes('transform:N_RISK_FACTOR_IDENTITY_DRAFT'))throw Error('document_status lost its real producer');
const derivedSiblings=docStatus.filter(x=>x!=='state:risk_factor_identity.document_status'&&by.get(x)?.kind==='derived_state');
if(derivedSiblings.length)throw Error(`document_status shows derived-state siblings: ${derivedSiblings.join(', ')}`);
const registry=check('artifact:registry/RISK_FACTOR_VARIABLE_REGISTRY.yaml');
const docSiblings=registry.filter(x=>x!=='artifact:registry/RISK_FACTOR_VARIABLE_REGISTRY.yaml'&&['document','artifact'].includes(by.get(x)?.kind));
if(docSiblings.length)throw Error(`registry shows document siblings: ${docSiblings.join(', ')}`);
console.log('PASS real RFP focused selection', {collect:collect.length,document_status:docStatus.length,registry:registry.length});
