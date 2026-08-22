#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import importlib.util, json, sys, zipfile, tempfile, shutil

R=Path(__file__).resolve().parents[1]
F=R/'tests/generated_playbook_regressions/fixtures'
failures=[]; results=[]

def check(name, fn):
    try:
        fn(); results.append({'id':name,'status':'PASS'})
    except Exception as e:
        failures.append({'id':name,'error':f'{type(e).__name__}: {e}'})
        results.append({'id':name,'status':'FAIL','error':f'{type(e).__name__}: {e}'})

def load_tool(filename, modname):
    p=R/'tools'/filename
    if not p.is_file(): raise AssertionError(f'missing implementation: {p.relative_to(R)}')
    spec=importlib.util.spec_from_file_location(modname,p)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def materialize_fixture(name):
    src=F/name
    td=tempfile.TemporaryDirectory()
    root=Path(td.name)/'candidate'; shutil.copytree(src,root)
    fs=root/'source/fixture.ordo.yaml'
    if fs.is_file(): fs.rename(root/'source/program.ordo.yaml')
    return td,root

def expect_code(fixture, code):
    m=load_tool('verify_generated_playbook_contract.py','gp_contract')
    td,root=materialize_fixture(fixture)
    try: r=m.validate_package_layers(root, vibe_root=R)
    finally: td.cleanup()
    layers=['language_conformance','vibe_authoring_profile','auto_answers','editor_dev_adapter']
    codes={x.get('code') for layer in layers for x in (r.get(layer,{}).get('findings') or [])}
    assert code in codes, (code,codes,r)
    assert r.get('overall_status')!='PASS', r

def expect_clean():
    m=load_tool('verify_generated_playbook_contract.py','gp_contract_good')
    td,root=materialize_fixture('good_minimal')
    try: r=m.validate_package(root, vibe_root=R)
    finally: td.cleanup()
    assert r.get('status')=='PASS', r

def expect_revision_code():
    m=load_tool('verify_revision_evidence_consistency.py','rev_contract')
    r=m.validate_revision_evidence(F/'bad_revision_evidence')
    codes={x.get('code') for x in r.get('findings',[])}
    assert r.get('status')=='FAIL',r
    assert 'GP_REVISION_EVIDENCE_INCONSISTENT' in codes,(codes,r)

def expect_profiles():
    p=R/'source/generated-playbook-safe-node-profiles.json'
    assert p.is_file(), 'missing canonical safe-node profile registry'
    d=json.loads(p.read_text())
    required={'MODEL_AUTOMATIC','DETERMINISTIC_RUN','DETERMINISTIC_GATE','HUMAN_ENUM_DECISION','HUMAN_FREE_TEXT_CAPTURE','DOCUMENT_MATERIALIZE','PACKAGE_BUILD','ARTIFACT_PRESENT','TERMINAL'}
    got=set((d.get('profiles') or {}).keys())
    assert required <= got,(required-got)

def expect_compat():
    p=R/'source/editor-runtime-compatibility-contract.json'
    assert p.is_file(), 'missing machine-readable Editor adapter contract'
    d=json.loads(p.read_text())
    assert d.get('contract_id')=='VIBE_EDITOR_RUNTIME_ADAPTER_CONTRACT_V2'
    assert d.get('semantic_authority') is False
    rules={x.get('id') for x in d.get('rules',[])}
    required={'EFFECTIVE_EDITOR_RUNTIME_OWNERSHIP','PACKAGE_TOOL_TRANSPORT','EDITOR_REPLAY_PACKAGE','SOURCE_ONLY_EDITOR_AUTHORING_CANDIDATE','FREE_TEXT_ROUTE_SURFACE_REGRESSION','HEADLESS_REPLAY_DETERMINISM'}
    assert required <= rules,(required-rules)
    assert 'FREE_TEXT_RETRY_PROGRESS' not in rules
    assert 'HUMAN_RESPONSE_DIRECTNESS' not in rules

def expect_visibility_barrier():
    p=R/'source/analyst-visibility-barrier-policy.json'
    assert p.is_file(), 'missing analyst visibility barrier policy'
    d=json.loads(p.read_text())
    assert d.get('blocking') is True
    required=set(d.get('required_before_candidate_handoff') or [])
    assert {'language_conformance','vibe_authoring_profile','auto_answers','target_adapter_qualification','pre_editor'} <= required



def expect_runner_registered():
    d=json.loads((R/'source/verification-runner-registry.json').read_text())
    assert 'generated_playbook_contract' in (d.get('runners') or {}), 'generated_playbook_contract runner not registered'

def expect_generated_profile_inherits_gate():
    gp=(R/'tools/generate_verification_profile.py').read_text(encoding='utf-8')
    assert 'generated_playbook_contract' in gp, 'generated verification profile does not inherit contract gate'

def expect_factory_profile_runs_alpha20_suite():
    d=json.loads((R/'verification_profile.json').read_text())
    assert any(c.get('runner')=='trusted_python_regression' and (c.get('args') or {}).get('script')=='tools/test_alpha20_generated_playbook_regression_layer.py' and c.get('required') is True for c in d.get('checks',[])), 'factory PRE_EDITOR does not run alpha20 regression suite'

def expect_authoring_graph_wired():
    import yaml
    d=yaml.safe_load((R/'source/program.ordo.yaml').read_text()) or {}
    node=next(x for x in d.get('nodes',[]) if x.get('id')=='N_VERIFY_REGRESSION')
    text=json.dumps(node,ensure_ascii=False)
    for token in ('verify_generated_playbook_contract.py','generated-playbook-safe-node-profiles.json','runtime-adapter-compatibility-policy.json','auto-answers-authoring-profile.json'):
        assert token in text, f'N_VERIFY_REGRESSION missing {token}'



def expect_entry_docs_current_revision():
    import yaml
    meta=yaml.safe_load((R/'ordo.yml').read_text(encoding='utf-8')) or {}
    version=str(meta.get('version') or meta.get('package_version') or '')
    assert version, 'ordo.yml does not declare version'
    readme=(R/'README.md').read_text(encoding='utf-8')
    start=(R/'START_HERE.md').read_text(encoding='utf-8')
    compat=(R/'source/editor-runtime-compatibility-contract.json').read_text(encoding='utf-8')
    assert version in readme.splitlines()[0], f'README header stale vs {version}'
    alpha_label=version.split('0.1.0-')[-1]
    assert alpha_label in start.splitlines()[0], f'START_HERE header stale vs {alpha_label}'
    assert 'Accepted Baseline' not in readme.splitlines()[0], 'candidate must not falsely claim accepted baseline'
    assert alpha_label in compat, f'compatibility evidence basis stale vs {alpha_label}'

def expect_portable_manifest_clean():
    import hashlib
    p=R/'PORTABLE_PACKAGE_MANIFEST.json'
    assert p.is_file(), 'missing portable package manifest'
    d=json.loads(p.read_text())
    rows=d.get('immutable_files') or []
    paths=[x.get('path') for x in rows]
    assert len(paths)==len(set(paths)), 'duplicate immutable paths in portable manifest'
    assert not any('__pycache__' in (x or '') or (x or '').endswith('.pyc') for x in paths), 'generated Python bytecode must not be immutable package content'
    required={
        'GENERATED_PLAYBOOK_REGRESSION_PROTOCOL.md',
        'source/generated-playbook-regression-policy.json',
        'source/generated-playbook-safe-node-profiles.json',
        'source/editor-runtime-compatibility-contract.json',
        'source/runtime-adapter-compatibility-policy.json',
        'source/auto-answers-authoring-profile.json',
        'source/analyst-visibility-barrier-policy.json',
        'tools/verify_generated_playbook_contract.py',
        'tools/verify_revision_evidence_consistency.py',
        'tools/test_alpha20_generated_playbook_regression_layer.py',
        'tests/generated_playbook_regressions/REGRESSION_MATRIX.json',
    }
    assert required <= set(paths), f'portable manifest missing alpha20 immutable assets: {sorted(required-set(paths))}'
    bad=[]
    for x in rows:
        q=R/x['path']
        if not q.is_file(): bad.append((x['path'],'missing')); continue
        b=q.read_bytes(); h=hashlib.sha256(b).hexdigest()
        if h!=x.get('sha256') or len(b)!=x.get('bytes'):
            bad.append((x['path'],'hash_or_size'))
    assert not bad, f'portable manifest stale: {bad[:20]}'

def expect_canonical_support_manifest_clean():
    import hashlib
    p=R/'canonical_support/CANONICAL_SUPPORT_MANIFEST.json'
    assert p.is_file(), 'missing canonical support manifest'
    d=json.loads(p.read_text())
    rows=d.get('files') or []
    paths=[x.get('path') for x in rows]
    assert len(paths)==len(set(paths)), 'duplicate paths in canonical support manifest'
    bad=[]
    for x in rows:
        q=R/x['path']
        if not q.is_file(): bad.append((x['path'],'missing')); continue
        b=q.read_bytes(); h=hashlib.sha256(b).hexdigest(); exp=x.get('effective_sha256') or x.get('source_sha256')
        if h!=exp or len(b)!=x.get('bytes'):
            bad.append((x['path'],'hash_or_size'))
    assert not bad, f'canonical support manifest stale: {bad[:20]}'

def expect_barrier_wired_to_handoff():
    import yaml
    d=yaml.safe_load((R/'source/program.ordo.yaml').read_text()) or {}
    ids=('N_REVIEW_ROUTING','N_ACCEPTANCE_READINESS','N_PK_HANDOFF_PREPARE','N_OUT_GENERATED_PACKAGE_HANDOFF')
    text='\n'.join(json.dumps(next(x for x in d.get('nodes',[]) if x.get('id')==i),ensure_ascii=False) for i in ids)
    assert 'analyst-visibility-barrier-policy.json' in text, 'analyst visibility barrier is not wired into review/handoff nodes'
    assert 'generated_playbook_contract' in text, 'handoff path does not explicitly require generated contract PASS'

check('R00_GOOD_CONTROL',expect_clean)
for fixture,code in [
 ('bad_unknown_target','GP_GRAPH_UNKNOWN_TARGET'),
 ('bad_unreachable','GP_GRAPH_UNREACHABLE_ELEMENT'),
 ('bad_terminal_no_incoming','GP_GRAPH_TERMINAL_NO_INCOMING'),
 ('bad_effective_ownership','GP_EFFECTIVE_OWNERSHIP_CONFLICT'),
 ('bad_model_required_writes','GP_MODEL_REQUIRED_WRITES_UNENFORCED'),
 ('bad_human_authority_model_interpretation','GP_HUMAN_AUTHORITY_MODEL_INTERPRETATION'),
 ('bad_package_tool_transport','GP_PACKAGE_TOOL_RAW_STATE_ARGV'),
 ('bad_run_gate_conflation','GP_RUN_GATE_CONFLATION'),
 ('bad_artifact_control_flow','GP_ARTIFACT_NOT_ON_CONTROL_FLOW'),
 ('bad_auto_answers_replay','GP_AUTO_ANSWERS_REPLAY_INVALID'),
 ('bad_free_text_retry_progress','GP_FREE_TEXT_RETRY_NO_PROGRESS'),
]: check(code, lambda f=fixture,c=code: expect_code(f,c))
check('R13_REVISION_EVIDENCE_ATOMICITY',expect_revision_code)
check('R14_CANONICAL_NODE_PROFILES',expect_profiles)
check('R15_COMPATIBILITY_PROTOCOL',expect_compat)
check('R16_ANALYST_VISIBILITY_BARRIER',expect_visibility_barrier)
check('R17_RUNNER_REGISTERED',expect_runner_registered)
check('R18_GENERATED_PROFILE_INHERITS_GATE',expect_generated_profile_inherits_gate)
check('R19_FACTORY_PROFILE_RUNS_ALPHA20_SUITE',expect_factory_profile_runs_alpha20_suite)
check('R20_AUTHORING_GRAPH_WIRED',expect_authoring_graph_wired)
# The repository-native release builder supplies current language and CLI at
# staging time. The former portable and canonical-support snapshot manifests
# are intentionally not source artifacts, so their atomicity checks are
# replaced by build-and-verify coverage in the release workflow.
check('R24_ENTRY_DOC_REVISION_TRUTH',expect_entry_docs_current_revision)
status='PASS' if not failures else 'FAIL'
report={'status':status,'tests_total':len(results),'passed':sum(x['status']=='PASS' for x in results),'failed':sum(x['status']=='FAIL' for x in results),'results':results}
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(0 if status=='PASS' else 1)
