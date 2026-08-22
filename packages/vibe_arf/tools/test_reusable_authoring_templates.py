from pathlib import Path
import json, sys
root=Path(__file__).resolve().parents[1]
kit=root/'authoring_templates'/'reusable'
required={
 'information_model':'INFORMATION_MODEL.template.yaml',
 'bindings':'BINDINGS.template.yaml',
 'document':'DOCUMENT.template.md',
 'interactive_analyst_workflow':'INTERACTIVE_ANALYST_WORKFLOW.template.yaml',
 'adaptive_artifact_quality':'ADAPTIVE_ARTIFACT_QUALITY.template.yaml',
 'semantic_execution_invariants':'SEMANTIC_EXECUTION_INVARIANTS.template.yaml',
 'materialization':'MATERIALIZATION.template.yaml',
 'validator':'VALIDATOR.template.yaml',
 'editor_projection':'EDITOR_PROJECTION.template.yaml',
}
errs=[]
reg=kit/'TEMPLATE_KIT_REGISTRY.json'
if not reg.exists(): errs.append('missing registry')
else:
 d=json.loads(reg.read_text())
 if set(d.get('templates',{})) != set(required): errs.append('registry categories mismatch')
 if set(d.get('instantiation_order',[])) != set(required): errs.append('instantiation order mismatch')
 if d.get('source_of_truth')!='data_layer': errs.append('registry source_of_truth != data_layer')
 if not d.get('reuse_required_for_generated_playbooks'): errs.append('reuse not required')
for k,f in required.items():
 p=kit/f
 if not p.exists(): errs.append(f'missing {f}')
policy=root/'source'/'reusable-authoring-template-policy.json'
if not policy.exists(): errs.append('missing policy')
validator=root/'tools'/'validate_reusable_authoring_templates.py'
if not validator.exists(): errs.append('missing validator')
prog=(root/'source'/'program.ordo.yaml').read_text()
for token in ['TEMPLATE_KIT_REGISTRY.json','reusable authoring template kit','N_A_IDENTITY_TEMPLATE','N_B_NODE_ACTION_SYNTHESIS','ADAPTIVE_ARTIFACT_QUALITY.template.yaml']:
 if token not in prog: errs.append(f'program missing {token}')
if errs:
 print('FAIL')
 for e in errs: print('-',e)
 sys.exit(1)
print('PASS reusable authoring templates')
