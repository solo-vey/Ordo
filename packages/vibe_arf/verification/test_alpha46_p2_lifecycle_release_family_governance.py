from pathlib import Path
import json, sys
R=Path(__file__).resolve().parents[1]
checks=[]
def ok(name, cond): checks.append((name,bool(cond)))
p=json.load(open(R/'source/lifecycle-release-family-governance-policy.json'))
ok('authoring_master_canonical',p['authoring_master']['canonical'] and p['authoring_master']['distribution_profiles_are_derived'])
ok('no_destructive_pruning',p['authoring_master']['destructive_runtime_pruning_forbidden'])
ok('lifecycle_complete',p['lifecycle']==['AUTHORING','CANDIDATE_BUILD','CANDIDATE_VALIDATION','RELEASE_QUALIFICATION','PROFILE_MATERIALIZATION','RELEASE_FAMILY_VALIDATION','RELEASE'])
ok('edit_data_layer',set(p['edit_invariants'])=={'DATA_LAYER_PRESENT','DATA_LAYER_SOURCE_HASH_MATCH','DATA_LAYER_PROJECTION_CURRENT'})
ok('three_profiles',p['release_family']['required_profiles']==['EDIT','CLI_RUN','MODEL_RUN'])
ok('family_manifest',p['release_family']['manifest']=='RELEASE_FAMILY_MANIFEST.json')
ok('identity',set(p['release_family']['canonical_identity_fields'])=={'playbook_id','version','canonical_source_sha256'})
ok('validation_levels',list(p['validation_levels'])==['L0','L1','L2','L3','L4'])
ok('tool_purity',p['tool_purity']['mutating_tools_run_on_qualification_copy'])
ok('coverage',set(p['coverage']['required_signals'])=={'gate_coverage','assertion_coverage','critical_node_coverage','behavioral_scenario_coverage'})
ok('direct_local_parity',all(p['execution_parity'][x] for x in ['direct_local_same_planner','direct_local_same_write_engine','direct_local_same_verification_engine','transport_layer_only_may_differ']))
ok('learning_classes',set(p['learning_classification']['classes'])=={'SESSION_EXECUTION_ERROR','DOMAIN_CONTRACT_DISCOVERY','FRAMEWORK_PROCESS_DEFECT','PLATFORM_LIMITATION'})
reg=json.load(open(R/'authoring_templates/reusable/TEMPLATE_KIT_REGISTRY.json'))
ok('template_registered','LIFECYCLE_RELEASE_FAMILY_GOVERNANCE' in reg['reusable_subprocesses'])
for f in ['PLAYBOOK_LAWS.md','authoring_templates/PLAYBOOK_LAWS.md','canonical_support/guides/PLAYBOOK_LAWS.md','canonical_support/output_templates/PLAYBOOK_LAWS.md']:
    ok('law_'+f.replace('/','_'),'E97_LIFECYCLE_RELEASE_FAMILY_GOVERNANCE' in (R/f).read_text())
print(f"P2 governance: {sum(v for _,v in checks)}/{len(checks)} PASS")
for n,v in checks:
    if not v: print('FAIL',n)
sys.exit(0 if all(v for _,v in checks) else 1)
