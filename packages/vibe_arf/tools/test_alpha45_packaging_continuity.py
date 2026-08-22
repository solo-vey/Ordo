#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, subprocess, tempfile, zipfile
from pathlib import Path
import yaml
R=Path(__file__).resolve().parents[1]
checks=[]
def ck(name,cond,detail=''):
    checks.append((name,bool(cond),detail))
def j(rel):
    p=R/rel
    return json.loads(p.read_text()) if p.exists() else {}
def y(rel):
    p=R/rel
    return yaml.safe_load(p.read_text()) if p.exists() else {}

policy=j('source/packaging-continuity-policy.json')
app=j('source/validator-applicability-policy.json')
contract=j('DISTRIBUTION_PACKAGE_CONTRACT.json')
prod=j('source/generated-playbook-production-package-policy.json')
profile=j('verification_profile.json')
exts=j('verification/PROFILE_EXTENSIONS.json')
prog=y('source/program.ordo.yaml')
info=y('authoring/information_object_catalog.yaml')
proj=y('authoring/ordo_projection.yaml')

ck('policy_exists', bool(policy))
ck('policy_active', policy.get('status')=='ACTIVE_CANDIDATE_POLICY')
ck('canonical_source_only', policy.get('source_of_truth')=='canonical_source_only')
ck('historical_non_authoritative', policy.get('historical_candidates')=='evidence_only_never_source_of_truth')
ck('profiles_three', set(policy.get('release_profiles',[]))=={'EDIT','CLI_RUN','MODEL_RUN'})
ck('candidate_subset', policy.get('candidate_materialization')=='requested_subset_or_all')
ck('release_all_three', policy.get('release_materialization')=='all_three_required')
ck('sibling_projections', policy.get('projection_model')=='sibling_projections_from_one_canonical_source')
ck('consumer_closure', policy.get('dependency_projection',{}).get('mode')=='consumer_aware_transitive_closure')
ck('startup_projected', policy.get('dependency_projection',{}).get('startup')=='profile_specific_clean_projection')
ck('tests_projected', policy.get('dependency_projection',{}).get('tests')=='project_with_retained_contract')
ck('fixtures_projected', policy.get('dependency_projection',{}).get('fixtures')=='project_with_retained_contract')
ck('no_orphans', policy.get('dependency_projection',{}).get('orphan_reference_policy')=='fail_closed')
ck('reproducible', policy.get('reproducible_build',{}).get('required') is True)
ck('fixed_zip_time', policy.get('reproducible_build',{}).get('zip_timestamp')=='1980-01-01T00:00:00')
ck('normalized_permissions', policy.get('reproducible_build',{}).get('permissions')=='normalized')
ck('sorted_members', policy.get('reproducible_build',{}).get('member_order')=='lexicographic')
ck('no_cache', '__pycache__' in policy.get('reproducible_build',{}).get('forbidden_tokens',[]))
ck('continuity_manifest', policy.get('continuity_manifest')=='PACKAGE_CONTINUITY_MANIFEST.json')
ck('exact_zip_before_handoff', policy.get('handoff_rule')=='exact_zip_validated_before_delivery')

ck('app_policy_exists', bool(app))
ck('app_default_deny', app.get('default')=='NOT_APPLICABLE_UNLESS_DECLARED')
for p in ['EDIT','CLI_RUN','MODEL_RUN']:
    ck('app_profile_'+p, p in app.get('profiles',{}))
ck('app_candidate_release_split', set(app.get('stages',{}))>={'CANDIDATE','RELEASE'})
ck('app_model_no_cli', 'cli_runtime' in app.get('profiles',{}).get('MODEL_RUN',{}).get('forbidden_validator_classes',[]))
ck('app_cli_no_editor', 'editor_authoring' in app.get('profiles',{}).get('CLI_RUN',{}).get('forbidden_validator_classes',[]))
ck('app_candidate_no_release_only', 'release_only' in app.get('stages',{}).get('CANDIDATE',{}).get('forbidden_validator_classes',[]))

ck('distribution_policy_ref', contract.get('packaging_continuity_policy')=='source/packaging-continuity-policy.json')
ck('distribution_applicability_ref', contract.get('validator_applicability_policy')=='source/validator-applicability-policy.json')
ck('manifest_schema_v3', contract.get('schema_version')=='3.0')
for p in ['EDIT','CLI_RUN','MODEL_RUN']:
    pc=contract.get('profiles',{}).get(p,{})
    ck('asset_selection_'+p, pc.get('asset_selection')=='consumer_aware_transitive_dependency_closure')
    ck('clean_start_'+p, pc.get('startup_projection')=='profile_specific_clean')
ck('release_continuity_check', 'continuity_manifest_parity' in contract.get('release_parity_checks',[]))
ck('release_semantic_parity', 'semantic_contract_parity' in contract.get('release_parity_checks',[]))

principles=prod.get('principles',[])
ck('prod_reproducible', 'reproducible_zip_bytes_required' in principles)
ck('prod_tests_projected', 'profile_tests_and_fixtures_project_with_retained_contract' in principles)
ck('prod_applicability', 'validator_applicability_is_profile_and_stage_aware' in principles)
ck('prod_continuity', 'continuity_manifest_makes_each_profile_rebuildable_from_canonical_source' in principles)

laws=(R/'PLAYBOOK_LAWS.md').read_text()
for lid in ['E89_PROFILE_AWARE_PACKAGING_CONTINUITY','E90_VALIDATOR_APPLICABILITY_BY_PROFILE_STAGE','E91_REPRODUCIBLE_PROFILE_BUILD_AND_HANDOFF']:
    ck('law_'+lid,lid in laws)

objs={x.get('id'):x for x in info.get('objects',[]) if isinstance(x,dict)}
ck('info_contract','I_PACKAGING_CONTINUITY_CONTRACT' in objs)
if 'I_PACKAGING_CONTINUITY_CONTRACT' in objs:
    cons=set(objs['I_PACKAGING_CONTINUITY_CONTRACT'].get('consumers',[]))
    ck('info_consumers',{'N_PI_GENERATED_PLAYBOOK_PACKAGE_DEPENDENCY_CLOSURE','N_PI_GENERATED_PLAYBOOK_PACKAGE_ASSEMBLE_PACKAGE','N_PI_GENERATED_PLAYBOOK_PACKAGE_VALIDATE_PACKAGE','N_PK_PACKAGE_CONTINUITY_AUDIT'}<=cons)
binds={x.get('information_id'):set(x.get('node_ids',[])) for x in proj.get('information_bindings',[]) if isinstance(x,dict)}
ck('projection_binding','N_PK_PACKAGE_CONTINUITY_AUDIT' in binds.get('I_PACKAGING_CONTINUITY_CONTRACT',set()))

nodes={x.get('id'):x for x in prog.get('nodes',[]) if isinstance(x,dict)}
gates={x.get('id'):x for x in prog.get('gates',[]) if isinstance(x,dict)}
ck('audit_node','N_PK_PACKAGE_CONTINUITY_AUDIT' in nodes)
ck('audit_deterministic','N_PK_PACKAGE_CONTINUITY_AUDIT' in nodes and nodes['N_PK_PACKAGE_CONTINUITY_AUDIT'].get('answer_type')=='structured_record')
ck('audit_tool','N_PK_PACKAGE_CONTINUITY_AUDIT' in nodes and 'tools/audit_packaging_continuity.py' in nodes['N_PK_PACKAGE_CONTINUITY_AUDIT'].get('node_context',{}).get('knowledge_refs',[]))
ck('continuity_gate','G_PK_PACKAGE_CONTINUITY_VALID' in gates)
if 'G_PK_PACKAGE_CONTINUITY_VALID' in gates:
    ck('gate_on_fail', bool(gates['G_PK_PACKAGE_CONTINUITY_VALID'].get('on_fail')))
    ck('gate_on_pass', bool(gates['G_PK_PACKAGE_CONTINUITY_VALID'].get('on_pass')))
ck('delivery_routes_audit','N_PI_GENERATED_PLAYBOOK_PACKAGE_RECORD_DELIVERY_EVIDENCE' in nodes and nodes['N_PI_GENERATED_PLAYBOOK_PACKAGE_RECORD_DELIVERY_EVIDENCE'].get('on_answer',{}).get('next')=='N_PK_PACKAGE_CONTINUITY_AUDIT')

ck('audit_tool_exists',(R/'tools/audit_packaging_continuity.py').is_file())
ck('profile_projector_exists',(R/'tools/project_profile_test_inventory.py').is_file())
ck('continuity_schema_exists',(R/'source/package-continuity-manifest.schema.json').is_file())

# canonical verification registration
ids={x.get('id') for x in profile.get('checks',[]) if isinstance(x,dict)}
ck('verification_registered','alpha45_packaging_continuity' in ids)
# profile extension source must retain it
exttxt=(R/'verification/PROFILE_EXTENSIONS.json').read_text() if (R/'verification/PROFILE_EXTENSIONS.json').exists() else ''
ck('extension_registered','alpha45_packaging_continuity' in exttxt)

# executable audit should pass current root and emit state_updates_v1
if (R/'tools/audit_packaging_continuity.py').exists():
    cp=subprocess.run(['python',str(R/'tools/audit_packaging_continuity.py'),str(R)],capture_output=True,text=True)
    try: out=json.loads(cp.stdout)
    except Exception: out={}
    ck('audit_exec_pass',cp.returncode==0 and out.get('report',{}).get('status')=='PASS',cp.stderr[-500:])
    ck('audit_envelope',out.get('schema_version')=='state_updates_v1' and isinstance(out.get('state_updates'),dict))
else:
    ck('audit_exec_pass',False); ck('audit_envelope',False)

# deterministic build: same root, same requested profile, identical bytes across two builds
builder=R/'tools/build_three_profile_playbook_distribution.py'
if builder.exists():
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        c1=subprocess.run(['python',str(builder),str(R),a,'--stem','T','--profiles','CLI_RUN'],capture_output=True,text=True)
        c2=subprocess.run(['python',str(builder),str(R),b,'--stem','T','--profiles','CLI_RUN'],capture_output=True,text=True)
        z1=Path(a)/'T_CLI_RUN.zip'; z2=Path(b)/'T_CLI_RUN.zip'
        same=c1.returncode==0 and c2.returncode==0 and z1.exists() and z2.exists() and z1.read_bytes()==z2.read_bytes()
        ck('reproducible_cli_zip',same,(c1.stderr+c2.stderr)[-500:])
        if z1.exists():
            with zipfile.ZipFile(z1) as z:
                names=z.namelist()
                ck('zip_member_order',names==sorted(names))
                ck('zip_fixed_time',all(i.date_time==(1980,1,1,0,0,0) for i in z.infolist()))
                ck('zip_continuity_manifest','PACKAGE_CONTINUITY_MANIFEST.json' in names)
                if 'PACKAGE_CONTINUITY_MANIFEST.json' in names:
                    cm=json.loads(z.read('PACKAGE_CONTINUITY_MANIFEST.json'))
                    ck('cm_profile',cm.get('profile')=='CLI_RUN')
                    ck('cm_source_identity',cm.get('canonical_source_identity')==json.loads(z.read('DISTRIBUTION_MANIFEST.json')).get('source_identity_sha256'))
                    ck('cm_rebuild_recipe',bool(cm.get('rebuild_recipe')))
                    ck('cm_closure_hash',bool(cm.get('dependency_closure_sha256')))
else:
    ck('reproducible_cli_zip',False); ck('zip_member_order',False); ck('zip_fixed_time',False); ck('zip_continuity_manifest',False); ck('cm_profile',False); ck('cm_source_identity',False); ck('cm_rebuild_recipe',False); ck('cm_closure_hash',False)

passed=sum(v for _,v,_ in checks); total=len(checks)
for n,v,d in checks:
    print(('PASS' if v else 'FAIL'),n,(':: '+d if d and not v else ''))
print(f'RESULT {passed}/{total}')
raise SystemExit(0 if passed==total else 1)
