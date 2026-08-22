#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys, tempfile, textwrap
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
RESULTS=[]
def check(name, cond, detail=""):
    RESULTS.append({"name":name,"status":"PASS" if cond else "FAIL","detail":detail})

def load_json(rel):
    p=ROOT/rel
    if not p.exists(): return None
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return None

def run(*args):
    return subprocess.run([sys.executable,*map(str,args)],capture_output=True,text=True,timeout=20)

# 1 policy/law exists and graph is a projection, not source model.
policy=load_json('source/information-first-authoring-policy.json')
check('A24_POLICY_INFORMATION_FIRST', bool(policy and policy.get('process_graph_role')=='projection_of_information_model'))
laws=(ROOT/'PLAYBOOK_LAWS.md').read_text(encoding='utf-8') if (ROOT/'PLAYBOOK_LAWS.md').exists() else ''
check('A24_LAW_INFORMATION_FIRST', 'E12_INFORMATION_FIRST_AUTHORING' in laws and 'E13_INFORMATION_PROJECTION_TRACEABILITY' in laws)

# 2 canonical neutral scaffold templates exist.
needed=[
 'authoring_templates/information_model/information_object_catalog.yaml',
 'authoring_templates/information_model/information_group_catalog.yaml',
 'authoring_templates/information_model/artifact_catalog.yaml',
 'authoring_templates/information_model/information_flow_graph.yaml',
 'authoring_templates/information_model/interaction_projection.yaml',
 'authoring_templates/information_model/ordo_projection.yaml',
]
check('A24_NEUTRAL_AIM_TEMPLATES', all((ROOT/x).is_file() for x in needed), ','.join(x for x in needed if not (ROOT/x).is_file()))

# 3 tools exist.
validator=ROOT/'tools/validate_authoring_information_model.py'
proj=ROOT/'tools/validate_information_projection.py'
init=ROOT/'tools/init_information_first_authoring.py'
check('A24_INFORMATION_VALIDATOR_EXISTS', validator.is_file())
check('A24_PROJECTION_VALIDATOR_EXISTS', proj.is_file())
check('A24_INFORMATION_INIT_TOOL_EXISTS', init.is_file())

# Build domain-neutral fixtures.
with tempfile.TemporaryDirectory() as td:
    d=Path(td); (d/'authoring').mkdir(); (d/'source').mkdir();
    objects={
      'schema_version':'1.0','objects':[
       {'id':'I_A','kind':'scalar','value_contract':{'type':'string','cardinality':'one','required':True,'value_states':['unset','value','unknown','not_applicable']},'lifecycle':{'validation_states':['draft','validated','approved','stale'],'invalidate_on_change':True},'group_id':'G_CORE','origins':['human_input']},
       {'id':'I_B','kind':'derived','value_contract':{'type':'string','cardinality':'one','required':True,'value_states':['unset','value','unknown','not_applicable']},'lifecycle':{'validation_states':['draft','validated','approved','stale'],'invalidate_on_change':True},'group_id':'G_CORE','origins':['model_derivation']}
      ]}
    groups={'schema_version':'1.0','groups':[{'id':'G_CORE','members':['I_A','I_B'],'display':{'language':'en','title':'Core','description':'Core information'},'validation':{'gate_ids':['G_CHECK']}}]}
    arts={'schema_version':'1.0','artifacts':[{'id':'A_DOC','kind':'document','inputs':['I_B'],'materialization':{'required':True},'verification':{'required':True}}]}
    graph={'schema_version':'1.0','nodes':[{'id':'I_A','kind':'information'},{'id':'I_B','kind':'information'},{'id':'G_CHECK','kind':'validation_gate','covers':['I_A','I_B']},{'id':'A_DOC','kind':'artifact'}], 'edges':[{'from':'I_A','to':'I_B','type':'derived_from'},{'from':'I_B','to':'G_CHECK','type':'validated_by'},{'from':'G_CHECK','to':'A_DOC','type':'materializes'}], 'entry_nodes':['I_A'],'terminal_nodes':['A_DOC']}
    projection={'schema_version':'1.0','status':'design','information_bindings':[{'information_id':'I_A','status':'unbound','node_ids':[]},{'information_id':'I_B','status':'unbound','node_ids':[]}], 'group_bindings':[{'group_id':'G_CORE','status':'unbound','node_ids':[]}], 'gate_bindings':[{'gate_id':'G_CHECK','status':'unbound','node_ids':[]}], 'artifact_bindings':[{'artifact_id':'A_DOC','status':'unbound','node_ids':[]}], 'rules':{'authoring_ids_must_not_be_ordo_extensions':True}}
    interaction={'schema_version':'1.0','policy':{'progressive_intake':True,'proposal_first_when_derivable':True},'interactions':[{'id':'X_CAPTURE','strategy':'free_text_seed','produces':['I_A'],'group_ids':['G_CORE']},{'id':'X_CONFIRM','strategy':'proposal_confirm','consumes':['I_A'],'produces':['I_B'],'group_ids':['G_CORE']}]}
    for name,obj in [('information_object_catalog.yaml',objects),('information_group_catalog.yaml',groups),('artifact_catalog.yaml',arts),('information_flow_graph.yaml',graph),('interaction_projection.yaml',interaction),('ordo_projection.yaml',projection)]:
        (d/'authoring'/name).write_text(yaml.safe_dump(obj,sort_keys=False),encoding='utf-8')
    (d/'source/program.ordo.yaml').write_text(yaml.safe_dump({'ordo':{'package':'fixture','package_version':'0.0.1','execution_mode':'chat_internal','control_level':'guided'},'nodes':[{'id':'N_CAPTURE'},{'id':'N_DERIVE'},{'id':'N_GATE'},{'id':'N_DOC'}]}),encoding='utf-8')

    if validator.is_file():
        r=run(validator,d)
        check('A24_VALID_AIM_PASSES', r.returncode==0, r.stdout[-500:]+r.stderr[-300:])
        # dangling dependency must fail
        bad=yaml.safe_load((d/'authoring/information_flow_graph.yaml').read_text()); bad['edges'].append({'from':'NOPE','to':'I_B','type':'derived_from'})
        (d/'authoring/information_flow_graph.yaml').write_text(yaml.safe_dump(bad,sort_keys=False))
        r2=run(validator,d)
        check('A24_DANGLING_FLOW_FAILS', r2.returncode!=0 and 'NOPE' in (r2.stdout+r2.stderr), r2.stdout[-500:])
        (d/'authoring/information_flow_graph.yaml').write_text(yaml.safe_dump(graph,sort_keys=False))
        badx=yaml.safe_load((d/'authoring/interaction_projection.yaml').read_text()); badx['interactions'][0]['produces']=['NO_INFO']
        (d/'authoring/interaction_projection.yaml').write_text(yaml.safe_dump(badx,sort_keys=False))
        rx=run(validator,d)
        check('A24_INTERACTION_PROJECTION_REFERENCES_ENFORCED', rx.returncode!=0 and 'NO_INFO' in (rx.stdout+rx.stderr), rx.stdout[-500:])
        (d/'authoring/interaction_projection.yaml').write_text(yaml.safe_dump(interaction,sort_keys=False))
        # artifact must be first-class in topology
        bad2=yaml.safe_load((d/'authoring/information_flow_graph.yaml').read_text()); bad2['nodes']=[n for n in bad2['nodes'] if n['id']!='A_DOC']; bad2['edges']=[e for e in bad2['edges'] if e['from']!='A_DOC' and e['to']!='A_DOC']
        (d/'authoring/information_flow_graph.yaml').write_text(yaml.safe_dump(bad2,sort_keys=False))
        r3=run(validator,d)
        check('A24_ARTIFACT_FIRST_CLASS_ENFORCED', r3.returncode!=0 and 'A_DOC' in (r3.stdout+r3.stderr),r3.stdout[-500:])
        (d/'authoring/information_flow_graph.yaml').write_text(yaml.safe_dump(graph,sort_keys=False))
    else:
        for n in ['A24_VALID_AIM_PASSES','A24_DANGLING_FLOW_FAILS','A24_INTERACTION_PROJECTION_REFERENCES_ENFORCED','A24_ARTIFACT_FIRST_CLASS_ENFORCED']: check(n,False,'validator missing')

    # 4 projection requires bindings once graph synthesis begins and checks both directions.
    if proj.is_file():
        r=run(proj,d,'--playbook',d/'source/program.ordo.yaml','--require-bound')
        check('A24_UNBOUND_PROJECTION_BLOCKS_RELEASE',r.returncode!=0 and 'unbound' in (r.stdout+r.stderr).lower(),r.stdout[-500:])
        p=yaml.safe_load((d/'authoring/ordo_projection.yaml').read_text())
        mapping={'I_A':'N_CAPTURE','I_B':'N_DERIVE','G_CORE':'N_CAPTURE','G_CHECK':'N_GATE','A_DOC':'N_DOC'}
        for key,idkey in [('information_bindings','information_id'),('group_bindings','group_id'),('gate_bindings','gate_id'),('artifact_bindings','artifact_id')]:
            for b in p[key]: b['status']='bound'; b['node_ids']=[mapping[b[idkey]]]
        p['playbook']={'managed_node_scope':['N_CAPTURE','N_DERIVE','N_GATE','N_DOC']}
        (d/'authoring/ordo_projection.yaml').write_text(yaml.safe_dump(p,sort_keys=False))
        r2=run(proj,d,'--playbook',d/'source/program.ordo.yaml','--require-bound')
        check('A24_BIDIRECTIONAL_PROJECTION_PASSES',r2.returncode==0,r2.stdout[-500:])
        p['playbook']['managed_node_scope'].append('N_ORPHAN')
        (d/'source/program.ordo.yaml').write_text(yaml.safe_dump({'ordo':{'package':'fixture','package_version':'0.0.1','execution_mode':'chat_internal','control_level':'guided'},'nodes':[{'id':'N_CAPTURE'},{'id':'N_DERIVE'},{'id':'N_GATE'},{'id':'N_DOC'},{'id':'N_ORPHAN'}]}))
        (d/'authoring/ordo_projection.yaml').write_text(yaml.safe_dump(p,sort_keys=False))
        r3=run(proj,d,'--playbook',d/'source/program.ordo.yaml','--require-bound')
        check('A24_REVERSE_TRACEABILITY_ENFORCED',r3.returncode!=0 and 'N_ORPHAN' in (r3.stdout+r3.stderr),r3.stdout[-500:])
    else:
        for n in ['A24_UNBOUND_PROJECTION_BLOCKS_RELEASE','A24_BIDIRECTIONAL_PROJECTION_PASSES','A24_REVERSE_TRACEABILITY_ENFORCED']: check(n,False,'projection validator missing')

# 5 generated verification profile inherits AIM gates.
gen=(ROOT/'tools/generate_verification_profile.py').read_text(encoding='utf-8') if (ROOT/'tools/generate_verification_profile.py').exists() else ''
check('A24_PROFILE_INHERITS_AIM_GATES', 'authoring_information_model' in gen and 'information_projection' in gen)
mat=(ROOT/'tools/materialize_generated_playbook_verification.py').read_text(encoding='utf-8') if (ROOT/'tools/materialize_generated_playbook_verification.py').exists() else ''
check('A24_GENERATED_PACKAGE_INHERITS_AIM_TOOLING', 'validate_authoring_information_model.py' in mat and 'validate_information_projection.py' in mat)

# 6 interaction and lifecycle semantics are explicit, not graph-first.
if policy:
    principles=' '.join(policy.get('principles',[])).lower()
    check('A24_PROGRESSIVE_INTAKE_POLICY', 'progressive' in principles and 'proposal' in principles)
    check('A24_LIFECYCLE_INVALIDATION_POLICY', 'stale' in principles and 'mutation' in principles)
    check('A24_VALUE_VALIDATION_STATE_INDEPENDENCE', 'unknown' in principles and 'not_applicable' in principles and 'independent' in principles)
else:
    check('A24_PROGRESSIVE_INTAKE_POLICY',False,'policy missing')
    check('A24_LIFECYCLE_INVALIDATION_POLICY',False,'policy missing')
    check('A24_VALUE_VALIDATION_STATE_INDEPENDENCE',False,'policy missing')


# 7 factory execution contour uses AIM before process/Ordo graph synthesis.
try:
    program=yaml.safe_load((ROOT/'source/program.ordo.yaml').read_text(encoding='utf-8')) or {}
    nby={n.get('id'):n for n in program.get('nodes',[]) if isinstance(n,dict) and n.get('id')}
    gby={g.get('id'):g for g in program.get('gates',[]) if isinstance(g,dict) and g.get('id')}
    def nxt(nid): return ((nby[nid].get('on_answer') or {}).get('next'))
    chain_ok=(
      nxt('N_U_RULE_AUTHORITY_MODEL')=='N_U_INFORMATION_OBJECT_CATALOG' and
      nxt('N_U_INFORMATION_OBJECT_CATALOG')=='N_U_INFORMATION_GROUP_CATALOG' and
      nxt('N_U_INFORMATION_GROUP_CATALOG')=='N_U_INFORMATION_FLOW_TOPOLOGY' and
      nxt('N_U_INFORMATION_FLOW_TOPOLOGY')=='N_U_INFORMATION_LIFECYCLE_AUTHORITY' and
      nxt('N_U_INFORMATION_LIFECYCLE_AUTHORITY')=='N_U_INTERACTION_PROJECTION' and
      nxt('N_U_INTERACTION_PROJECTION') in {'N_VERIFY_INFORMATION_MODEL','N_U_REVIEW_BUNDLE_COMPILATION'} and
      (nxt('N_U_INTERACTION_PROJECTION')!='N_U_REVIEW_BUNDLE_COMPILATION' or (nxt('N_U_REVIEW_BUNDLE_COMPILATION')=='N_U_PROPOSAL_CANONICALIZATION' and nxt('N_U_PROPOSAL_CANONICALIZATION') in {'N_VERIFY_INFORMATION_MODEL','N_VERIFY_DATA_LAYER_CANONICAL'})) and
      (nxt('N_U_PROPOSAL_CANONICALIZATION')!='N_VERIFY_DATA_LAYER_CANONICAL' or (nxt('N_VERIFY_DATA_LAYER_CANONICAL')=='G_DATA_LAYER_CANONICAL_READY' and gby['G_DATA_LAYER_CANONICAL_READY'].get('on_pass')=='N_VERIFY_INFORMATION_MODEL')) and
      nxt('N_VERIFY_INFORMATION_MODEL')=='G_INFORMATION_MODEL_READY' and
      gby['G_INFORMATION_MODEL_READY'].get('on_pass')=='N_U_LEGACY_MIGRATION')
    check('A24_FACTORY_AIM_PRECEDES_PROCESS_SYNTHESIS',chain_ok)
    check('A24_FACTORY_INFORMATION_GATES_DETERMINISTIC', all(gby[x].get('method')=='mechanical' and gby[x].get('trust_class')=='deterministic' for x in ['G_INFORMATION_MODEL_READY','G_INFORMATION_PROJECTION_PASS']))
    check('A24_BUILD_BINDS_PROJECTION_BEFORE_SOURCE', nxt('N_B_REUSE_PROVENANCE_ASSEMBLY')=='N_B_INFORMATION_TO_ORDO_PROJECTION_BIND' and nxt('N_B_INFORMATION_TO_ORDO_PROJECTION_BIND')=='N_B_SOURCE_MATERIALIZE')
    check('A24_PROJECTION_GATE_PRECEDES_STRUCTURE', gby['G_SOURCE_VERIFICATION_PASS'].get('on_pass')=='N_VERIFY_INFORMATION_PROJECTION' and nxt('N_VERIFY_INFORMATION_PROJECTION')=='G_INFORMATION_PROJECTION_PASS' and gby['G_INFORMATION_PROJECTION_PASS'].get('on_pass')=='N_VERIFY_STRUCTURE')
except Exception as e:
    for n in ['A24_FACTORY_AIM_PRECEDES_PROCESS_SYNTHESIS','A24_FACTORY_INFORMATION_GATES_DETERMINISTIC','A24_BUILD_BINDS_PROJECTION_BEFORE_SOURCE','A24_PROJECTION_GATE_PRECEDES_STRUCTURE']:
        check(n,False,str(e))

passed=sum(r['status']=='PASS' for r in RESULTS); failed=len(RESULTS)-passed
out={'schema_version':'1.0','suite':'alpha24_information_first_authoring','passed':passed,'failed':failed,'tests':RESULTS}
print(json.dumps(out,ensure_ascii=False,indent=2))
raise SystemExit(0 if failed==0 else 1)
