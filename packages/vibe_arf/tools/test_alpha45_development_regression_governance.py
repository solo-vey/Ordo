#!/usr/bin/env python3
from pathlib import Path
import json,yaml,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[1]
checks={}
def ck(k,v): checks[k]=bool(v)
def j(rel):
 p=R/rel; return json.loads(p.read_text()) if p.is_file() else {}
def y(rel):
 p=R/rel; return yaml.safe_load(p.read_text()) if p.is_file() else {}
policy=j('source/development-regression-governance-policy.json')
ck('policy_exists',bool(policy)); ck('policy_id',policy.get('policy_id')=='DEVELOPMENT_REGRESSION_GOVERNANCE'); ck('scope',policy.get('scope')=='cross_domain')
for k in ['regression_first','invariant_not_implementation_detail','candidate_targeted_release_full','positive_negative_fixtures','real_failure_retention','regression_vs_live_evidence','packaging_only_semantic_proof','explainable_coverage']:
 ck('principle_'+k,k in policy.get('principles',[]))
cc=policy.get('candidate_change_contract',{})
for f in ['change_id','change_class','protected_invariant','baseline_identity','regression_asset','prechange_evidence','postchange_evidence','impacted_checks','regression_proof','live_proof']:
 ck('candidate_field_'+f,f in cc.get('required_fields',[]))
ck('prechange_fail_required',cc.get('prechange_rule')=='material change requires reproducible pre-change non-PASS for the new invariant, or explicit NOT_APPLICABLE with machine-checkable reason')
ck('green_required',cc.get('postchange_rule')=='exact regression PASS plus impacted checks PASS before candidate handoff')
ck('full_release_only',policy.get('verification_modes',{}).get('release',{}).get('full_accumulated_suite') is True)
ck('candidate_not_full',policy.get('verification_modes',{}).get('candidate',{}).get('full_accumulated_suite') is False)
ck('candidate_impacted',policy.get('verification_modes',{}).get('candidate',{}).get('impacted_checks_required') is True)
ck('proof_namespaces',set(policy.get('evidence_namespaces',[]))>={'REGRESSION_PROOF','LIVE_PROOF'})
ck('live_not_substitute',policy.get('live_evidence_rule')=='LIVE_PROOF never substitutes for REGRESSION_PROOF; path-not-exercised is a valid live status')
ck('packaging_only_hashes',set(policy.get('packaging_only_semantic_proof',{}).get('required_equal_hashes',[]))>={'source/program.ordo.yaml','canonical_data_layer'})
ck('coverage_formula',policy.get('explainable_coverage',{}).get('required') is True)
for rel in ['tools/build_development_regression_plan.py','tools/validate_development_regression_governance.py','authoring_templates/reusable/DEVELOPMENT_REGRESSION_GOVERNANCE.template.yaml']:
 ck('asset_'+Path(rel).name,(R/rel).is_file())
prog=y('source/program.ordo.yaml') or {}; mod=y('source/modules/40_policies.ordo.module.yaml') or {}
laws={x.get('id'):x for x in prog.get('playbook_laws',{}).get('laws',[]) if isinstance(x,dict)}
mlaws={x.get('id'):x for x in mod.get('playbook_laws',{}).get('laws',[]) if isinstance(x,dict)}
ck('law_program','E94_DEVELOPMENT_REGRESSION_GOVERNANCE' in laws); ck('law_module','E94_DEVELOPMENT_REGRESSION_GOVERNANCE' in mlaws); ck('law_md','E94_DEVELOPMENT_REGRESSION_GOVERNANCE' in (R/'PLAYBOOK_LAWS.md').read_text())
nodes={x.get('id'):x for x in prog.get('nodes',[]) if isinstance(x,dict)}; gates={x.get('id'):x for x in prog.get('gates',[]) if isinstance(x,dict)}
for nid in ['N_DV_REGRESSION_DEFINE','N_DV_PRECHANGE_REGRESSION_RUN','N_DV_POSTCHANGE_REGRESSION_AUDIT']:
 ck('node_'+nid,nid in nodes)
for gid in ['G_DV_PRECHANGE_EVIDENCE_VALID','G_DV_CANDIDATE_REGRESSION_READY']:
 ck('gate_'+gid,gid in gates)
ck('semantic_change_enters_dev_regression',nodes.get('N_C_ROOT_CAUSE',{}).get('on_answer',{}).get('next')=='N_DV_REGRESSION_DEFINE')
ck('prechange_gate_to_dependency',gates.get('G_DV_PRECHANGE_EVIDENCE_VALID',{}).get('on_pass')=='N_C_DEPENDENCY_CLOSURE')
ck('accept_routes_postchange',nodes.get('N_FEEDBACK_CLASSIFY',{}).get('on_answer',{}).get('accept',{}).get('next')=='N_DV_POSTCHANGE_REGRESSION_AUDIT')
ck('postchange_pass_acceptance',gates.get('G_DV_CANDIDATE_REGRESSION_READY',{}).get('on_pass')=='N_ACCEPTANCE_READINESS')
ck('postchange_fail_hardening',gates.get('G_DV_CANDIDATE_REGRESSION_READY',{}).get('on_fail')=='N_QH_BASELINE_CAPTURE')
# impact-map semantics
imap=j('verification_impact_map.json').get('modes',{})
ck('candidate_targeted_mode',imap.get('CANDIDATE',{}).get('full_pre_editor') is False and imap.get('CANDIDATE',{}).get('validation_class')=='TARGETED')
ck('release_full_mode',imap.get('RELEASE',{}).get('full_pre_editor') is True and imap.get('RELEASE',{}).get('validation_class')=='FULL')
# old incremental policy must align
inc=j('source/incremental-development-verification-policy.json')
ck('incremental_policy_candidate_targeted',any('CANDIDATE runs targeted' in x for x in inc.get('rules',[])))
ck('incremental_policy_release_full',any('RELEASE runs the full accumulated' in x for x in inc.get('rules',[])))
# inheritance/template registry
reg=j('authoring_templates/reusable/TEMPLATE_KIT_REGISTRY.json')
ck('template_registry',reg.get('reusable_subprocesses',{}).get('DEVELOPMENT_REGRESSION_GOVERNANCE')=='authoring_templates/reusable/DEVELOPMENT_REGRESSION_GOVERNANCE.template.yaml')
inh=j('source/generated-playbook-execution-inheritance-policy.json')
ck('inherit_policy','source/development-regression-governance-policy.json' in inh.get('required_generated_artifacts',[]))
# profile registered
pe=j('verification/PROFILE_EXTENSIONS.json')
ck('profile_registration',any(x.get('id')=='alpha45_development_regression_governance' for x in pe.get('checks',[]) if isinstance(x,dict)))
# behavior: plan tool preserves evidence namespaces and derives impacted check list from explicit inputs
try:
 with tempfile.TemporaryDirectory() as td:
  req=Path(td)/'req.json'; out=Path(td)/'out.json'
  req.write_text(json.dumps({'change_id':'C1','change_class':'DEFECT_FIX','protected_invariant':'INV','baseline_identity':'a'*64,'regression_asset':'tools/test_x.py','prechange_status':'FAIL','prechange_reason':'expected invariant absent','changed_files':['source/x.json'],'impacted_checks':['lint','x_regression']}))
  p=subprocess.run([sys.executable,str(R/'tools/build_development_regression_plan.py'),str(req),'--output',str(out)],capture_output=True,text=True)
  data=json.loads(out.read_text()) if out.is_file() else {}
  ck('behavior_plan_tool',p.returncode==0 and data.get('status')=='PASS')
  ck('behavior_regression_namespace',data.get('regression_proof',{}).get('namespace')=='REGRESSION_PROOF')
  ck('behavior_live_namespace',data.get('live_proof',{}).get('namespace')=='LIVE_PROOF')
  ck('behavior_impacted_dedup',data.get('impacted_checks')==['lint','x_regression'])
except Exception:
 for k in ['behavior_plan_tool','behavior_regression_namespace','behavior_live_namespace','behavior_impacted_dedup']: ck(k,False)
failed=[k for k,v in checks.items() if not v]
print(json.dumps({'status':'PASS' if not failed else 'FAIL','passed':sum(checks.values()),'total':len(checks),'failed':failed},indent=2))
raise SystemExit(1 if failed else 0)
