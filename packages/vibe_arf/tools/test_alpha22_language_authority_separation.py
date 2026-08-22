#!/usr/bin/env python3
from pathlib import Path
import json, importlib.util, tempfile, zipfile
R=Path(__file__).resolve().parents[1]
fail=[]; res=[]
def chk(i,fn):
  try: fn(); res.append({'id':i,'status':'PASS'})
  except Exception as e: fail.append((i,str(e))); res.append({'id':i,'status':'FAIL','error':str(e)})
def load(name):
  p=R/'tools'/name; s=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

def layered_policy():
  d=json.loads((R/'source/generated-playbook-regression-policy.json').read_text())
  assert 'language_blocking_contracts' in d
  assert 'vibe_profile_blocking_contracts' in d
  assert 'auto_answers_contracts' in d
  assert 'adapter_blocking_contracts' in d and 'editor_dev' in d['adapter_blocking_contracts']
  assert 'blocking_contracts' not in d

def language_authority():
  d=json.loads((R/'source/runtime-adapter-compatibility-policy.json').read_text())
  assert d['semantic_source_of_truth']=='canonical_ordo_language'
  assert d['adapter_failure_status']=='ORDO_VALID_ADAPTER_INCOMPATIBLE'

def editor_not_authority():
  d=json.loads((R/'source/editor-runtime-compatibility-contract.json').read_text())
  assert d['scope_type']=='runtime_adapter_contract'
  assert d['semantic_authority'] is False
  for x in d['rules']:
    assert x.get('authority_layer') in {'EDITOR_ADAPTER','EDITOR_REGRESSION'}

def auto_answer_retry_reclassified():
  d=json.loads((R/'source/auto-answers-authoring-profile.json').read_text())
  ids={x['id'] for x in d['rules']}
  assert 'RETRY_SCENARIO_PROGRESS' in ids
  assert 'EDITOR_REPLAY_PACKAGE_SHAPE' in ids

def verifier_layers():
  m=load('verify_generated_playbook_contract.py')
  assert hasattr(m,'validate_package_layers')
  with tempfile.TemporaryDirectory() as td:
    root=Path(td); (root/'source').mkdir()
    (root/'source/program.ordo.yaml').write_text('''ordo:\n  package_version: 0.0.1\n  execution_mode: chat_internal\n  control_level: guided\ngraph_contract:\n  entry_node: H\n  external_terminal_targets: [END]\nnodes:\n- id: H\n  type: human_decision\n  answer_type: enum\n  allowed_answers: [approve, reject]\n  on_answer:\n    approve:\n      update_state: {decision: "$answer.value"}\n      next: END\n    reject:\n      next: END\n''')
    r=m.validate_package_layers(root,R)
    assert r['language_conformance']['status']=='PASS',r
    assert r['overall_status'] in {'PASS','PROFILE_NONCONFORMANT','ADAPTER_INCOMPATIBLE'},r
    assert not any(f.get('code')=='GP_HUMAN_AUTHORITY_MODEL_INTERPRETATION' for f in r['language_conformance'].get('findings',[]))

def profile_status_separate():
  m=load('verify_generated_playbook_contract.py')
  assert 'ORDO_VALID_ADAPTER_INCOMPATIBLE' in getattr(m,'STATUS_VALUES',set())

def chat_internal_not_editor_bound():
  m=load('verify_generated_playbook_contract.py')
  td,root=materialize_fixture_local('bad_source_only_package')
  try:
    r=m.validate_package(root,R,target='chat_internal')
  finally: td.cleanup()
  assert r['status']=='PASS',r

def materialize_fixture_local(name):
  import shutil
  src=R/'tests/generated_playbook_regressions/fixtures'/name
  td=tempfile.TemporaryDirectory(); root=Path(td.name)/'candidate'; shutil.copytree(src,root)
  fs=root/'source/fixture.ordo.yaml'
  if fs.is_file(): fs.rename(root/'source/program.ordo.yaml')
  return td,root

def editor_target_is_explicit():
  gp=(R/'tools/generate_verification_profile.py').read_text()
  mat=(R/'tools/materialize_generated_playbook_verification.py').read_text()
  assert 'RUNTIME_ADAPTER_TARGETS.json' in gp and 'editor_dev' in gp
  assert 'RUNTIME_ADAPTER_TARGETS.json' in mat and '["chat_internal","editor_dev"]' in mat

for i,f in [('R31_LAYERED_REGRESSION_POLICY',layered_policy),('R32_LANGUAGE_IS_SEMANTIC_AUTHORITY',language_authority),('R33_EDITOR_IS_ADAPTER_NOT_AUTHORITY',editor_not_authority),('R34_AUTO_ANSWERS_OWN_RETRY_AND_REPLAY_RULES',auto_answer_retry_reclassified),('R35_LAYERED_VALIDATOR_DOES_NOT_REJECT_EDITOR_ONLY_SHAPE_AS_ORDO_INVALID',verifier_layers),('R36_DISTINCT_ADAPTER_INCOMPATIBILITY_STATUS',profile_status_separate),('R37_CHAT_INTERNAL_NOT_EDITOR_BOUND',chat_internal_not_editor_bound),('R38_EDITOR_DEV_IS_EXPLICIT_TARGET',editor_target_is_explicit)]: chk(i,f)
print(json.dumps({'status':'FAIL' if fail else 'PASS','tests_total':len(res),'passed':sum(x['status']=='PASS' for x in res),'failed':len(fail),'results':res},ensure_ascii=False,indent=2))
raise SystemExit(1 if fail else 0)
