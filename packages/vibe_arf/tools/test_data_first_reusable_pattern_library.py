#!/usr/bin/env python3
from pathlib import Path
import json, yaml, sys
ROOT=Path(__file__).resolve().parents[1]
fail=[]; passed=0

def check(cond,msg):
    global passed
    if cond: passed+=1
    else: fail.append(msg)

regp=ROOT/'patterns'/'PATTERN_REGISTRY.json'
check(regp.exists(),'missing patterns/PATTERN_REGISTRY.json')
if regp.exists():
    reg=json.loads(regp.read_text())
    pats=reg.get('patterns',[])
    check(len(pats)>=8,f'expected at least 8 canonical patterns, got {len(pats)}')
    ids={p.get('id') for p in pats}
    expected={'DOCUMENT_MATERIALIZATION','PRODUCTION_PACKAGE_MATERIALIZATION','VALIDATE_REPAIR_CONVERGENCE','IMPLEMENTATION_CHANGE','DOCUMENT_RECONCILIATION_VERIFICATION','VERIFIED_DOCUMENT_JIRA_TASK_MATERIALIZATION','VERIFIED_DOCUMENT_CODE_IMPLEMENTATION','EXECUTION_DEBUG_EVIDENCE_EXPORT'}
    check(expected.issubset(ids),f'pattern ids missing: {expected-ids}')
    for p in pats:
        base=ROOT/'patterns'/p['path']
        check((base/'PATTERN.yaml').exists(),f"{p['id']}: missing PATTERN.yaml")
        check((base/'DATA_LAYER.template.yaml').exists(),f"{p['id']}: missing DATA_LAYER.template.yaml")
        check((base/'EXECUTION.template.yaml').exists(),f"{p['id']}: missing EXECUTION.template.yaml")

inst=ROOT/'authoring'/'pattern_instance_catalog.yaml'
check(inst.exists(),'missing authoring/pattern_instance_catalog.yaml')
if inst.exists():
    d=yaml.safe_load(inst.read_text()) or {}
    instances=d.get('instances',[])
    check(all('pattern_id' in x and 'pattern_version' in x and 'data_layer_bindings' in x and 'execution_projection' not in x and 'instance_digest' in x for x in instances),
          'pattern instances must persist semantic pattern/version/data-layer bindings/digest without concrete execution projection')

obj=yaml.safe_load((ROOT/'authoring'/'information_object_catalog.yaml').read_text())
ids={x['id'] for x in obj.get('objects',[])}
check('I_REUSABLE_DATA_EXECUTION_PATTERN_LIBRARY' in ids,'missing Data Layer pattern-library information object')
check('I_PATTERN_INSTANCE_CATALOG' in ids,'missing pattern-instance catalog information object')
check('I_PATTERN_GRAPH_REALIZATION_CONTRACT' in ids,'missing pattern graph realization contract information object')
check('I_PATTERN_GRAPH_REALIZATION_EVIDENCE' in ids,'missing pattern graph realization evidence information object')

groups=yaml.safe_load((ROOT/'authoring'/'information_group_catalog.yaml').read_text())
gm={g['id']:g.get('members',[]) for g in groups.get('groups',[])}
check('I_REUSABLE_DATA_EXECUTION_PATTERN_LIBRARY' in gm.get('G_INFORMATION_MODEL',[]),'pattern library must be first-class in G_INFORMATION_MODEL')
check('I_PATTERN_INSTANCE_CATALOG' in gm.get('G_INFORMATION_MODEL',[]),'pattern instances must be first-class in G_INFORMATION_MODEL')

flow=yaml.safe_load((ROOT/'authoring'/'information_flow_graph.yaml').read_text())
edges={(e.get('from'),e.get('to'),e.get('type')) for e in flow.get('edges',[])}
check(('I_ARTIFACT_SURFACE','I_PATTERN_SELECTION_INPUT_SNAPSHOT','derived_from') in edges,'artifact surface must be frozen before pattern lookup')
check(('I_CAPABILITY_REQUIREMENT_CATALOG','I_PATTERN_SELECTION_INPUT_SNAPSHOT','derived_from') in edges,'capability requirements must be frozen before pattern lookup')
check(('I_REUSABLE_DATA_EXECUTION_PATTERN_LIBRARY','I_PATTERN_APPLICABILITY_RESULT','derived_from') in edges,'library must contribute to applicability result')
check(('I_PATTERN_FIT_RESOLUTION','I_PATTERN_INSTANCE_CATALOG','derived_from') in edges,'fit resolution must produce pattern instances')
check(('I_PATTERN_INSTANCE_CATALOG','I_INFORMATION_OBJECT_CATALOG','depends_on') in edges,'pattern instances must constrain Information Object Catalog')
check(('I_PATTERN_INSTANCE_CATALOG','I_INFORMATION_FLOW_GRAPH','depends_on') in edges,'pattern instances must constrain information flow')
check(('I_PATTERN_INSTANCE_CATALOG','I_ORDO_BUILD_IR','derived_from') not in edges,'pattern instances must not bypass derived execution projection into Ordo build')
check(('I_PATTERN_EXECUTION_PROJECTION','I_ORDO_BUILD_IR','derived_from') in edges,'tree/build must derive from validated pattern execution projection')
check(('I_PATTERN_EXECUTION_PROJECTION','I_PATTERN_GRAPH_REALIZATION_EVIDENCE','derived_from') in edges,'pattern graph realization evidence must trace to execution projection')
check(('I_ORDO_BUILD_IR','I_PATTERN_GRAPH_REALIZATION_EVIDENCE','derived_from') in edges,'pattern graph realization evidence must validate actual build IR/source')
check(('I_PATTERN_GRAPH_REALIZATION_EVIDENCE','I_PATTERN_REUSE_EVALUATION','derived_from') in edges,'reuse scoring must consume graph realization evidence')
check(('I_INFORMATION_OBJECT_CATALOG','I_PATTERN_EXECUTION_PROJECTION','depends_on') in edges,'execution projection must depend on merged information-object catalog')
check(('I_INFORMATION_FLOW_GRAPH','I_PATTERN_EXECUTION_PROJECTION','depends_on') in edges,'execution projection must depend on merged information-flow graph')

art=yaml.safe_load((ROOT/'authoring'/'artifact_catalog.yaml').read_text())
am={a['id']:a for a in art.get('artifacts',[])}
check(am.get('A_BUSINESS_VIEW',{}).get('pattern_binding',{}).get('pattern_id')=='DOCUMENT_MATERIALIZATION','business-view document should bind document pattern in Data Layer')
check(am.get('A_GENERATED_PLAYBOOK_PACKAGE',{}).get('pattern_binding',{}).get('pattern_id')=='PRODUCTION_PACKAGE_MATERIALIZATION','generated package should bind package pattern in Data Layer')

mod=yaml.safe_load((ROOT/'source'/'modules'/'30_vibe_architecture.ordo.module.yaml').read_text())
gmod=yaml.safe_load((ROOT/'source'/'modules'/'60_validation_outputs.ordo.module.yaml').read_text())
nodes={n['id']:n for n in mod.get('nodes',[])}
gates={g['id']:g for g in gmod.get('gates',[])}
for nid in ['N_U_PATTERN_APPLICABILITY_DISCOVERY','N_U_PATTERN_FIT_RESOLUTION','N_U_PATTERN_DATA_LAYER_INSTANTIATION','N_VERIFY_PATTERN_DATA_LAYER_INSTANCE']:
    check(nid in nodes,f'missing Data-Layer-first pattern node {nid}')
check('G_PATTERN_DATA_LAYER_INSTANCE_VALID' in gates,'missing Data-Layer-first pattern validation gate')
if 'N_U_RULE_AUTHORITY_MODEL' in nodes:
    check(nodes['N_U_RULE_AUTHORITY_MODEL'].get('on_answer',{}).get('next')=='N_U_CAPABILITY_REQUIREMENT_CATALOG','capability requirements must be classified before library lookup')
    check(nodes.get('N_U_CAPABILITY_REQUIREMENT_CATALOG',{}).get('on_answer',{}).get('next')=='N_U_PATTERN_SELECTION_INPUT_FREEZE','capability requirements must freeze before library lookup')
    check(nodes.get('N_U_PATTERN_SELECTION_INPUT_FREEZE',{}).get('on_answer',{}).get('next')=='N_U_PATTERN_APPLICABILITY_DISCOVERY','pattern discovery must consume frozen pre-library inputs')
if 'G_PATTERN_DATA_LAYER_INSTANCE_VALID' in gates:
    check(gates['G_PATTERN_DATA_LAYER_INSTANCE_VALID'].get('on_pass')=='N_U_INFORMATION_OBJECT_CATALOG','validated pattern Data Layer must feed Information Object Catalog')
if 'N_D_REUSE_PATTERN_SELECTION' in nodes:
    q=str(nodes['N_D_REUSE_PATTERN_SELECTION'].get('question',''))
    check('do not select' in q.lower() or 'do not select' in q.lower(),'tree-design reuse node must not independently re-select pattern')
if 'N_B_INFORMATION_TO_ORDO_PROJECTION_BIND' in nodes:
    q=str(nodes['N_B_INFORMATION_TO_ORDO_PROJECTION_BIND'].get('question',''))
    check('pattern_instance_catalog' in q,'Ordo projection must consume pattern_instance_catalog')

for tool in ['discover_data_layer_patterns.py','instantiate_data_layer_pattern.py','validate_data_layer_pattern_instances.py','derive_pattern_execution_projection.py','validate_pattern_graph_realization.py']:
    check((ROOT/'tools'/tool).exists(),f'missing deterministic pattern tool {tool}')

prod=json.loads((ROOT/'source/generated-playbook-production-package-policy.json').read_text())
profiles=prod.get('package_profiles',{})
production=profiles.get('production',{})
resolved=profiles.get(production.get('alias_of'),production) if production.get('alias_of') else production
check('reusable_patterns' in set(resolved.get('required_surfaces',[])),'reusable pattern library must be a required production/edit surface')
pc=json.loads((ROOT/'PRODUCTION_PACKAGE_CONTRACT.json').read_text())
classes={x.get('class'):x for x in pc.get('artifact_classes',[])}
check(classes.get('reusable_patterns',{}).get('default_inclusion')=='required' and 'patterns/**' in classes.get('reusable_patterns',{}).get('patterns',[]),'production package contract must include patterns/** as required')

print(json.dumps({'status':'PASS' if not fail else 'FAIL','passed':passed,'failed':len(fail),'failures':fail},indent=2))
sys.exit(1 if fail else 0)
