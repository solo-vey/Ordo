#!/usr/bin/env python3
from pathlib import Path
import json, yaml, subprocess, sys, tempfile
R=Path(__file__).resolve().parents[1]
fail=[]; passed=0

def ck(c,m):
    global passed
    if c: passed+=1
    else: fail.append(m)

instp=R/'authoring/pattern_instance_catalog.yaml'
projp=R/'authoring/pattern_execution_projection.yaml'
inst=yaml.safe_load(instp.read_text()) or {}
instances=inst.get('instances',[])
ck(bool(instances),'pattern instance catalog empty')
for x in instances:
    ck('execution_projection' not in x,f"{x.get('instance_id')}: canonical Data Layer leaks execution_projection")
    import re
    txt=json.dumps(x,ensure_ascii=False)
    ck(not re.search(r'\b[NG]_[A-Z0-9_]+\b',txt),f"{x.get('instance_id')}: canonical Data Layer leaks concrete node/gate ids")
    ck('data_layer_bindings' in x,f"{x.get('instance_id')}: missing semantic data-layer bindings")
    ck('pattern_id' in x and 'pattern_version' in x and 'instance_digest' in x,f"{x.get('instance_id')}: missing pattern provenance")

proj=yaml.safe_load(projp.read_text()) or {}
ck(proj.get('source_of_truth')=='authoring/pattern_instance_catalog.yaml','projection source of truth wrong')
ck(proj.get('projection_policy')=='derive_only_no_tree_reselection','projection policy wrong')
ck(bool(proj.get('canonical_data_layer_digest')),'projection missing canonical Data Layer synchronization digest')
ck(bool(proj.get('canonical_data_layer_inputs')),'projection missing canonical Data Layer input list')
frags=proj.get('fragments',[])
ck(len(frags)==len(instances),'every pattern instance must have one derived execution fragment')
for f in frags:
    ck(bool(f.get('components')),f"{f.get('pattern_instance_id')}: derived fragment has no components")
    ck(bool(f.get('edges')),f"{f.get('pattern_instance_id')}: derived fragment has no edges")
    ck(f.get('projection_source')=='pattern_execution_template',f"{f.get('pattern_instance_id')}: projection source not template")
    ck(f.get('selection_performed_at_tree_stage') is False,f"{f.get('pattern_instance_id')}: tree stage re-selection allowed")

# Instantiation CLI must not require or accept concrete execution bindings.
cp=subprocess.run([sys.executable,str(R/'tools/instantiate_data_layer_pattern.py'),str(R),'--help'],capture_output=True,text=True)
ck('--execution-bindings-json' not in cp.stdout,'instantiator still asks Data Layer author for execution/node bindings')

# Projection derivation must be reproducible from instances + execution templates.
with tempfile.TemporaryDirectory() as td:
    cp=subprocess.run([sys.executable,str(R/'tools/derive_pattern_execution_projection.py'),str(R),'--out',str(Path(td)/'projection.yaml')],capture_output=True,text=True)
    ck(cp.returncode==0,'projection derivation failed: '+cp.stderr)
    if cp.returncode==0:
        a=yaml.safe_load((Path(td)/'projection.yaml').read_text()) or {}
        ck(a.get('fragments')==frags,'projection is not reproducible from canonical Data Layer + library templates')

# Capability requirements are first-class Data Layer input to pattern discovery.
objs=yaml.safe_load((R/'authoring/information_object_catalog.yaml').read_text()) or {}
ids={x.get('id') for x in objs.get('objects',[])}
ck('I_CAPABILITY_REQUIREMENT_CATALOG' in ids,'missing first-class capability requirement catalog')
flow=yaml.safe_load((R/'authoring/information_flow_graph.yaml').read_text()) or {}
edges={(e.get('from'),e.get('to'),e.get('type')) for e in flow.get('edges',[])}
ck(('I_CAPABILITY_REQUIREMENT_CATALOG','I_PATTERN_SELECTION_INPUT_SNAPSHOT','derived_from') in edges,'capability catalog must feed frozen pre-library selection snapshot')
ck(('I_PATTERN_SELECTION_INPUT_SNAPSHOT','I_PATTERN_APPLICABILITY_RESULT','derived_from') in edges,'frozen selection snapshot must feed pattern applicability')
ck(('I_REUSABLE_DATA_EXECUTION_PATTERN_LIBRARY','I_PATTERN_APPLICABILITY_RESULT','derived_from') in edges,'static library must feed applicability result without becoming project-derived truth')


# Execution projection must occur only after the complete canonical Data Layer gate.
program=yaml.safe_load((R/'source/program.ordo.yaml').read_text()) or {}
nodes={x.get('id'):x for x in program.get('nodes',[])}
gates={x.get('id'):x for x in program.get('gates',[])}
ck(((nodes.get('N_U_INFORMATION_FLOW_TOPOLOGY') or {}).get('on_answer') or {}).get('next')=='N_U_INFORMATION_LIFECYCLE_AUTHORITY',
   'information-flow topology must continue Data Layer completion, not derive execution projection')
ck((gates.get('G_DATA_LAYER_CANONICAL_READY') or {}).get('on_pass')=='N_VERIFY_INFORMATION_MODEL',
   'canonical Data Layer gate must still run final information-model validation')
ck((gates.get('G_INFORMATION_MODEL_READY') or {}).get('on_pass')=='N_VERIFY_PATTERN_DATA_LAYER_MERGE',
   'pattern merge/execution projection must start only after final information-model PASS')
ck(((nodes.get('N_VERIFY_PATTERN_DATA_LAYER_MERGE') or {}).get('allowed_from') or [])==['G_INFORMATION_MODEL_READY'],
   'pattern merge validator must only be reachable from final information-model gate')
ck((gates.get('G_PATTERN_DATA_LAYER_MERGE_VALID') or {}).get('on_pass')=='N_U_LEGACY_MIGRATION',
   'after derived pattern execution projection, flow must enter process/tree semantic derivation')

print(json.dumps({'status':'PASS' if not fail else 'FAIL','passed':passed,'failed':len(fail),'failures':fail},indent=2))
sys.exit(1 if fail else 0)
