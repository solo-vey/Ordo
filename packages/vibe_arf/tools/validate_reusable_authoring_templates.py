from pathlib import Path
import json, sys, yaml
root=Path(__file__).resolve().parents[1]
kit=root/'authoring_templates'/'reusable'
reg=json.loads((kit/'TEMPLATE_KIT_REGISTRY.json').read_text())
errors=[]
required=['information_model','bindings','document','semantic_execution_invariants','interactive_analyst_workflow','adaptive_artifact_quality','materialization','validator','editor_projection']
if reg.get('source_of_truth')!='data_layer': errors.append('source_of_truth')
templates=reg.get('templates',{})
if set(templates)!=set(required): errors.append('registry_categories')
order=reg.get('instantiation_order',[])
if set(order)!=set(required) or len(order)!=len(required): errors.append('instantiation_order')
for k in required:
 if k not in templates: continue
 p=root/templates[k]['path']
 if not p.exists() or p.stat().st_size==0: errors.append('missing:'+k); continue
 if p.suffix in {'.yaml','.yml'}:
  try: y=yaml.safe_load(p.read_text())
  except Exception: errors.append('yaml:'+k); continue
  if y.get('template_kind')!=k: errors.append('kind:'+k)
prog=(root/'source'/'program.ordo.yaml').read_text()
for token in ['TEMPLATE_KIT_REGISTRY.json','reusable authoring template kit']:
 if token not in prog: errors.append('program_binding:'+token)
print(json.dumps({'status':'PASS' if not errors else 'FAIL','errors':errors},indent=2))
sys.exit(0 if not errors else 1)
