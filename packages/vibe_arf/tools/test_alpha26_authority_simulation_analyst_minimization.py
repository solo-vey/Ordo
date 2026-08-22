#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys, tempfile, shutil, zipfile, importlib.util, io, contextlib
from types import SimpleNamespace
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
RESULTS=[]
def check(name,cond,detail=''):
    RESULTS.append({'name':name,'status':'PASS' if cond else 'FAIL','detail':detail})
_MODULE_CACHE={}
def run(script,*args):
    # Trusted alpha.26 regression calls package-local validator main() in-process.
    # This preserves CLI argument behavior while avoiding repeated Python startup cost.
    p=ROOT/'tools'/script
    if not p.is_file():
        return None
    mod=_MODULE_CACHE.get(script)
    if mod is None:
        name='alpha26_reg_'+script.replace('.py','').replace('-','_')
        spec=importlib.util.spec_from_file_location(name,p)
        mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        _MODULE_CACHE[script]=mod
    old_argv=list(sys.argv); out=io.StringIO(); err=io.StringIO(); rc=0
    try:
        sys.argv=[str(p),*map(str,args)]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                result=mod.main()
                rc=int(result or 0)
            except SystemExit as e:
                rc=int(e.code or 0)
    except Exception as e:
        rc=1; err.write(f'{type(e).__name__}: {e}')
    finally:
        sys.argv=old_argv
    return SimpleNamespace(returncode=rc,stdout=out.getvalue(),stderr=err.getvalue())
def jload(rel):
    p=ROOT/rel
    try:return json.loads(p.read_text(encoding='utf-8'))
    except Exception:return None
def yload(rel):
    p=ROOT/rel
    try:return yaml.safe_load(p.read_text(encoding='utf-8'))
    except Exception:return None

# Static architecture/policy layer.
policies=[
 'source/analyst-minimal-authoring-policy.json',
 'source/proposal-canonicalization-policy.json',
 'source/simulation-first-verification-policy.json',
 'source/defect-ownership-policy.json',
 'source/behavioral-coverage-policy.json',
]
check('A26_POLICIES_EXIST',all((ROOT/p).is_file() for p in policies),','.join(p for p in policies if not (ROOT/p).is_file()))

templates=[
 'authoring_templates/information_model/review_bundle_catalog.yaml',
 'authoring_templates/information_model/proposal_canonicalization.yaml',
 'authoring_templates/information_model/approval_ledger.yaml',
 'authoring_templates/information_model/scenario_matrix.yaml',
]
check('A26_AUTHORING_TEMPLATES_EXIST',all((ROOT/p).is_file() for p in templates),','.join(p for p in templates if not (ROOT/p).is_file()))

validators=[
 'validate_review_bundle_design.py','validate_proposal_canonical_separation.py','validate_approval_persistence.py',
 'validate_local_persistence_gates.py','validate_state_phase_ordering.py','validate_recovery_locality.py',
 'validate_runtime_gate_evidence.py','validate_behavioral_scenario_coverage.py','validate_semantic_dependency_inputs.py',
 'validate_simulation_evidence.py','validate_fixture_contract_closure.py','validate_defect_ownership.py'
]
check('A26_PYTHON_GATES_EXIST',all((ROOT/'tools'/p).is_file() for p in validators),','.join(p for p in validators if not (ROOT/'tools'/p).is_file()))

simdep=jload('verification/SIMULATION_KIT_DEPENDENCY.json')
check('A26_SIMULATION_DEPENDENCY_PINNED',bool(simdep and simdep.get('dependency_id')=='ORDO_PLAYBOOK_SIMULATION_KIT' and simdep.get('version') and simdep.get('semantic_authority')=='runtime_adapter_only'))

bar=jload('source/analyst-visibility-barrier-policy.json') or {}
req=set(bar.get('required_before_candidate_handoff') or [])
check('A26_ANALYST_BARRIER_REQUIRES_SIMULATION',{'simulation_contract','simulation_fixture_closure','simulation_pass','defect_ownership'}.issubset(req),str(sorted(req)))

vp=jload('verification_profile.json') or {}
checkids={str(c.get('id')) for c in (vp.get('checks') or []) if isinstance(c,dict)}
required_checks={
 'review_bundle_design','proposal_canonical_separation','approval_persistence','local_persistence_gates',
 'state_phase_ordering','recovery_locality','runtime_gate_evidence','behavioral_scenario_coverage',
 'semantic_dependency_inputs','simulation_evidence','fixture_contract_closure','defect_ownership'
}
check('A26_GATES_IN_SELF_PRE_EDITOR',required_checks.issubset(checkids),str(sorted(required_checks-checkids)))

arch=yload('source/modules/30_vibe_architecture.ordo.module.yaml') or {}
node_ids={str(n.get('id')) for n in (arch.get('nodes') or []) if isinstance(n,dict)}
needed_nodes={'N_U_REVIEW_BUNDLE_COMPILATION','N_U_PROPOSAL_CANONICALIZATION','N_B_APPROVAL_RECOVERY_BINDING','N_SIM_INSPECT','N_SIM_FIXTURE_SYNTHESIS','N_SIM_RUN','N_SIM_CLASSIFY'}
check('A26_EXPLICIT_AUTHORING_AND_SIMULATION_CONTOUR',needed_nodes.issubset(node_ids),str(sorted(needed_nodes-node_ids)))

# Dynamic validators on domain-neutral fixtures.
with tempfile.TemporaryDirectory() as td:
    d=Path(td); (d/'authoring').mkdir(); (d/'source').mkdir(); (d/'verification').mkdir(); (d/'reports').mkdir()
    prog={'ordo':{'package':'T','package_version':'0.1','execution_mode':'chat_internal','control_level':'strict'},'nodes':[
      {'id':'N_H','answer_type':'enum','allowed_answers':['approve','reject'],'on_answer':{'approve':{'update_state':{'proposal_reviews.core':'APPROVED'},'next':'G_LOCAL'},'reject':{'next':'N_H'}}},
      {'id':'N_M','inputs':['state.seed'],'authority_contract':{'derived_targets':[{'target':'state.derived','sources':['state.seed']}]},'on_answer':{'update_state':{'proposal.core':'$answer'}}},
      {'id':'N_COMMIT','on_answer':{'update_state':{'contract_status':'VERIFIED'}}},
    ],'gates':[
      {'id':'G_LOCAL','method':'deterministic','trust_class':'deterministic','condition':'state.proposal_reviews.core == "APPROVED"','on_pass':'N_COMMIT','on_fail':'N_H'},
      {'id':'G_VERIFY','method':'deterministic','trust_class':'deterministic','condition':'state.contract_status == "ASSEMBLED"','on_pass':'N_COMMIT','on_fail':'N_H'},
    ]}
    (d/'source/program.ordo.yaml').write_text(yaml.safe_dump(prog,sort_keys=False),encoding='utf-8')
    # authoring model fragments
    (d/'authoring/information_object_catalog.yaml').write_text(yaml.safe_dump({'schema_version':'1.0','objects':[{'id':'I_A','kind':'scalar','group_id':'G_A','value_contract':{'type':'string','cardinality':'one','required':True,'value_states':['unset','value','unknown','not_applicable']},'lifecycle':{'validation_states':['draft','validated','approved','stale'],'invalidate_on_change':True},'origins':['human_input']}]},sort_keys=False),encoding='utf-8')
    (d/'authoring/information_group_catalog.yaml').write_text(yaml.safe_dump({'schema_version':'1.0','groups':[{'id':'G_A','members':['I_A'],'display':{'language':'en','title':'A','description':'A'},'validation':{'gate_ids':['G_LOCAL']}}]},sort_keys=False),encoding='utf-8')
    (d/'authoring/review_bundle_catalog.yaml').write_text(yaml.safe_dump({'schema_version':'1.0','bundles':[{'id':'RB_A','group_ids':['G_A'],'authority_fields':['I_A'],'uncertain_fields':[],'derived_fields':[],'display_fields':['I_A'],'silent_fields':[],'approval_mode':'explicit','review_trigger':'authority_required'}]},sort_keys=False),encoding='utf-8')
    (d/'authoring/proposal_canonicalization.yaml').write_text(yaml.safe_dump({'schema_version':'1.0','proposal_state_root':'proposal','canonical_state_root':'canonical','approved_projection_root':'approved_projection','rules':{'materializers_must_consume_approved_projection':True,'deep_merge_proposal_into_canonical_forbidden':True}},sort_keys=False),encoding='utf-8')
    (d/'authoring/approval_ledger.yaml').write_text(yaml.safe_dump({'schema_version':'1.0','ledger_mode':'append_only_revisioned','entries':[{'group_id':'G_A','revision':1,'approved_fields':['I_A'],'rejected_fields':[],'authority':'analyst','evidence':['answer:N_H'],'supersedes':None}]},sort_keys=False),encoding='utf-8')
    (d/'authoring/scenario_matrix.yaml').write_text(yaml.safe_dump({'schema_version':'1.0','required_families':['core_identity','trigger','null_no_data','source_failure','lifecycle','output','history_transition'],'scenarios':[{'id':'S1','families':['core_identity','trigger','null_no_data','source_failure','lifecycle','output','history_transition'],'status':'designed'}]},sort_keys=False),encoding='utf-8')
    # positive simulation evidence
    sim={'schema_version':'1.0','exact_candidate_sha256':'abc','kit_version':'0.1.0','status':'PASS','fixture_closure':'PASS','runtime_baseline':'test','scenarios':[{'id':'S1','status':'PASS'}]}
    (d/'reports/SIMULATION_EVIDENCE.json').write_text(json.dumps(sim),encoding='utf-8')
    (d/'reports/DEFECT_OWNERSHIP.json').write_text(json.dumps({'schema_version':'1.0','status':'PASS','findings':[]}),encoding='utf-8')
    # runtime gate evidence fixture
    (d/'reports/RUNTIME_GATE_EVIDENCE.json').write_text(json.dumps({'gates':[{'gate_id':'G_LOCAL','status':'PASS','check_results':[{'id':'c1','status':'PASS'}],'evidence':['state:proposal_reviews.core']}] }),encoding='utf-8')
    # simulation contract + fixture usage
    (d/'reports/SIMULATION_CONTRACT.json').write_text(json.dumps({'analyst_fixture_points':['N_H'],'model_fixture_points':['N_M'],'dynamic_recovery_fixture_points':[]}),encoding='utf-8')
    (d/'reports/FIXTURE_USAGE.json').write_text(json.dumps({'provided_analyst':['N_H'],'provided_model':['N_M'],'unused':[]}),encoding='utf-8')

    for script,testname in [
      ('validate_review_bundle_design.py','A26_REVIEW_BUNDLE_VALIDATOR_WORKS'),
      ('validate_proposal_canonical_separation.py','A26_PROPOSAL_QUARANTINE_VALIDATOR_WORKS'),
      ('validate_approval_persistence.py','A26_APPROVAL_LEDGER_VALIDATOR_WORKS'),
      ('validate_local_persistence_gates.py','A26_LOCAL_PERSISTENCE_VALIDATOR_WORKS'),
      ('validate_state_phase_ordering.py','A26_PHASE_ORDER_VALIDATOR_WORKS'),
      ('validate_recovery_locality.py','A26_RECOVERY_LOCALITY_VALIDATOR_WORKS'),
      ('validate_runtime_gate_evidence.py','A26_RUNTIME_EVIDENCE_VALIDATOR_WORKS'),
      ('validate_behavioral_scenario_coverage.py','A26_COVERAGE_VALIDATOR_WORKS'),
      ('validate_semantic_dependency_inputs.py','A26_SEMANTIC_INPUT_PARITY_VALIDATOR_WORKS'),
      ('validate_simulation_evidence.py','A26_SIMULATION_EVIDENCE_VALIDATOR_WORKS'),
      ('validate_fixture_contract_closure.py','A26_FIXTURE_CLOSURE_VALIDATOR_WORKS'),
      ('validate_defect_ownership.py','A26_DEFECT_OWNERSHIP_VALIDATOR_WORKS')]:
        rr=run(script,d)
        check(testname,rr is not None and rr.returncode==0,'' if rr is None else (rr.stdout+rr.stderr)[-900:])

    # Negative regression fixtures: every historical defect class must be rejected.
    def clone(name):
        b=d/'_mut'/name
        b.parent.mkdir(exist_ok=True)
        shutil.copytree(d,b,ignore=shutil.ignore_patterns('_mut'))
        return b
    # bad review bundle references unknown group
    b=clone('bad_review'); x=yaml.safe_load((b/'authoring/review_bundle_catalog.yaml').read_text()); x['bundles'][0]['group_ids']=['G_UNKNOWN']; (b/'authoring/review_bundle_catalog.yaml').write_text(yaml.safe_dump(x,sort_keys=False)); rr=run('validate_review_bundle_design.py',b); check('A26_NEG_REVIEW_UNKNOWN_GROUP_BLOCKED',rr is not None and rr.returncode!=0)
    # proposal/canonical roots collapse
    b=clone('bad_proposal'); x=yaml.safe_load((b/'authoring/proposal_canonicalization.yaml').read_text()); x['canonical_state_root']=x['proposal_state_root']; (b/'authoring/proposal_canonicalization.yaml').write_text(yaml.safe_dump(x,sort_keys=False)); rr=run('validate_proposal_canonical_separation.py',b); check('A26_NEG_PROPOSAL_LEAK_BLOCKED',rr is not None and rr.returncode!=0)
    # approval overwrite/duplicate revision
    b=clone('bad_approval'); x=yaml.safe_load((b/'authoring/approval_ledger.yaml').read_text()); e=dict(x['entries'][0]); e['approved_fields']=[]; e['rejected_fields']=['I_A']; x['entries'].append(e); (b/'authoring/approval_ledger.yaml').write_text(yaml.safe_dump(x,sort_keys=False)); rr=run('validate_approval_persistence.py',b); check('A26_NEG_APPROVAL_OVERWRITE_BLOCKED',rr is not None and rr.returncode!=0)
    # local authority update without local gate
    b=clone('bad_local_gate'); x=yaml.safe_load((b/'source/program.ordo.yaml').read_text()); x['nodes'][0]['on_answer']['approve']['next']='N_COMMIT'; (b/'source/program.ordo.yaml').write_text(yaml.safe_dump(x,sort_keys=False)); rr=run('validate_local_persistence_gates.py',b); check('A26_NEG_LOCAL_PERSISTENCE_MISSING_BLOCKED',rr is not None and rr.returncode!=0)
    # gate requires own postcondition
    b=clone('bad_phase'); x=yaml.safe_load((b/'source/program.ordo.yaml').read_text()); x['gates'][1]['condition']='state.contract_status == VERIFIED'; (b/'source/program.ordo.yaml').write_text(yaml.safe_dump(x,sort_keys=False)); rr=run('validate_state_phase_ordering.py',b); check('A26_NEG_POSTCONDITION_INVERSION_BLOCKED',rr is not None and rr.returncode!=0)
    # broad recovery to entry
    b=clone('bad_recovery'); x=yaml.safe_load((b/'source/program.ordo.yaml').read_text()); x['graph_contract']={'entry_node':'N_H'}; x['gates'][1]['on_fail']='N_H'; (b/'source/program.ordo.yaml').write_text(yaml.safe_dump(x,sort_keys=False)); rr=run('validate_recovery_locality.py',b); check('A26_NEG_BROAD_RECOVERY_BLOCKED',rr is not None and rr.returncode!=0)
    # vacuous runtime gate evidence
    b=clone('bad_evidence'); (b/'reports/RUNTIME_GATE_EVIDENCE.json').write_text(json.dumps({'gates':[{'gate_id':'G_LOCAL','status':'PASS','check_results':[],'evidence':[]}]})); rr=run('validate_runtime_gate_evidence.py',b); check('A26_NEG_VACUOUS_GATE_PASS_BLOCKED',rr is not None and rr.returncode!=0)
    # incomplete scenario coverage
    b=clone('bad_coverage'); x=yaml.safe_load((b/'authoring/scenario_matrix.yaml').read_text()); x['scenarios'][0]['families']=['core_identity']; (b/'authoring/scenario_matrix.yaml').write_text(yaml.safe_dump(x,sort_keys=False)); rr=run('validate_behavioral_scenario_coverage.py',b); check('A26_NEG_FAKE_COVERAGE_COMPLETE_BLOCKED',rr is not None and rr.returncode!=0)
    # authority source missing input
    b=clone('bad_semantic_input'); x=yaml.safe_load((b/'source/program.ordo.yaml').read_text()); x['nodes'][1]['inputs']=[]; (b/'source/program.ordo.yaml').write_text(yaml.safe_dump(x,sort_keys=False)); rr=run('validate_semantic_dependency_inputs.py',b); check('A26_NEG_AUTHORITY_SOURCE_NOT_INPUT_BLOCKED',rr is not None and rr.returncode!=0)
    # simulation FAIL cannot qualify
    b=clone('bad_sim'); x=json.loads((b/'reports/SIMULATION_EVIDENCE.json').read_text()); x['status']='FAIL'; (b/'reports/SIMULATION_EVIDENCE.json').write_text(json.dumps(x)); rr=run('validate_simulation_evidence.py',b); check('A26_NEG_SIMULATION_FAIL_BLOCKED',rr is not None and rr.returncode!=0)
    # fixture contract missing model response
    b=clone('bad_fixture'); x=json.loads((b/'reports/FIXTURE_USAGE.json').read_text()); x['provided_model']=[]; (b/'reports/FIXTURE_USAGE.json').write_text(json.dumps(x)); rr=run('validate_fixture_contract_closure.py',b); check('A26_NEG_FIXTURE_GAP_BLOCKED',rr is not None and rr.returncode!=0)
    # runtime defect with playbook workaround is forbidden
    b=clone('bad_owner'); (b/'reports/DEFECT_OWNERSHIP.json').write_text(json.dumps({'findings':[{'primary_owner':'RUNTIME_ADAPTER_CONFORMANCE_DEFECT','evidence':['missing_route'],'playbook_workaround_applied':True}]})); rr=run('validate_defect_ownership.py',b); check('A26_NEG_RUNTIME_WORKAROUND_BLOCKED',rr is not None and rr.returncode!=0)

# Materializer must distribute new gates/templates to generated playbooks.
mat=(ROOT/'tools/materialize_generated_playbook_verification.py').read_text(encoding='utf-8') if (ROOT/'tools/materialize_generated_playbook_verification.py').is_file() else ''
check('A26_GENERATED_INHERITANCE_WIRED',all(v in mat for v in validators) and 'review_bundle_catalog.yaml' in mat and 'scenario_matrix.yaml' in mat)

# Portable ZIP builder must preserve runtime freshness after ordinary extraction.
builder=ROOT/'tools/build_portable_candidate_zip.py'
builder_ok=False; builder_detail='missing'
if builder.is_file():
    with tempfile.TemporaryDirectory() as ztd:
        ztd=Path(ztd); pkg=ztd/'pkg'; (pkg/'source').mkdir(parents=True); (pkg/'compiled').mkdir()
        (pkg/'source/program.ordo.yaml').write_text('ordo:\n  package: zip_probe\n',encoding='utf-8')
        (pkg/'compiled/program.ir.json').write_text('{}\n',encoding='utf-8')
        out=ztd/'probe.zip'
        rr=subprocess.run([sys.executable,str(builder),str(pkg),str(out)],capture_output=True,text=True,timeout=15)
        if rr.returncode==0 and out.is_file():
            with zipfile.ZipFile(out) as z:
                names=z.namelist(); order_ok=names.index('source/program.ordo.yaml') < names.index('compiled/program.ir.json')
                ext=ztd/'ext'; z.extractall(ext)
            mtime_ok=(ext/'compiled/program.ir.json').stat().st_mtime >= (ext/'source/program.ordo.yaml').stat().st_mtime
            builder_ok=order_ok and mtime_ok
            builder_detail=f'order_ok={order_ok};mtime_ok={mtime_ok}'
        else: builder_detail='' if rr is None else (rr.stdout+rr.stderr)[-600:]
check('A26_PORTABLE_ZIP_RUNTIME_FRESHNESS_BUILDER',builder_ok,builder_detail)

blob='\n'.join((ROOT/p).read_text(encoding='utf-8',errors='ignore') for p in policies+templates if (ROOT/p).is_file()).lower()
forbidden=['risk_factor_passport','risk factor passport','company terminated','severity_level']
check('A26_DOMAIN_NEUTRAL',not any(x in blob for x in forbidden),str([x for x in forbidden if x in blob]))

passed=sum(x['status']=='PASS' for x in RESULTS); failed=len(RESULTS)-passed
report={'schema_version':'1.0','suite':'alpha26_authority_simulation_analyst_minimization','passed':passed,'failed':failed,'tests':RESULTS}
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(0 if failed==0 else 1)
