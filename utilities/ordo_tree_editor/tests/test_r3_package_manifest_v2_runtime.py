from __future__ import annotations
import hashlib, io, json, zipfile
from utilities.ordo_tree_editor import editor_service as es

SOURCE = b'''playbook:\n  entry_node: START\nnodes:\n  - id: START\n    question: go\n    on_answer:\n      ok:\n        next: END\nterminals:\n  - id: END\n'''

def package(*, required_caps=None, corrupt_file_hash=False):
    source_sha=hashlib.sha256(SOURCE).hexdigest()
    plan={
      'format':'ordo.runtime_semantic_plan','format_version':'1.0',
      'source':{'sha256':source_sha},'elements':{},
      'validation':{'structural_status':'PASS','semantic_status':'PASS','compilation_issues':[]}
    }
    plan_raw=json.dumps(plan,separators=(',',':')).encode()
    files={
      'program.ordo.yaml': source_sha,
      'compiled/runtime_semantic_plan.json': hashlib.sha256(plan_raw).hexdigest(),
    }
    if corrupt_file_hash:
        files['program.ordo.yaml']='0'*64
    manifest={
      'manifest_version':'2.0','package_id':'generic.demo','package_version':'0.1.0',
      'playbook_contract_version':'1','semantic_plan_format_version':'1.0',
      'entry_node':'START','terminal_nodes':['END'],
      'capabilities':{'required':required_caps or ['typed_state_patch','package_session_isolation'],'optional':[]},
      'integrity':{
        'hash_algorithm':'sha256','coverage':'all_files_except_manifest','source_sha256':source_sha,
        'semantic_plan_sha256':hashlib.sha256(plan_raw).hexdigest(),
      },
      'files':files,
    }
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('program.ordo.yaml',SOURCE)
        z.writestr('compiled/runtime_semantic_plan.json',plan_raw)
        z.writestr('manifest.json',json.dumps(manifest,separators=(',',':')).encode())
    return buf.getvalue()

def legacy_package_without_v2_manifest():
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('program.ordo.yaml',SOURCE)
    return buf.getvalue()

def test_r3_manifest_v2_valid_package_is_accepted():
    parsed=es.parse_playbook_package('demo.zip',package())
    status=parsed['package_manifest_v2_status']
    assert status['available'] and status['valid']
    assert status['package_id']=='generic.demo'

def test_r3_manifest_v2_unknown_required_capability_fails_closed():
    try:
        es.parse_playbook_package('demo.zip',package(required_caps=['domain_magic']))
    except ValueError as exc:
        assert 'unsupported runtime capability' in str(exc)
    else:
        raise AssertionError('unsupported mandatory capability must reject package')

def test_r3_manifest_v2_hash_mismatch_fails_closed():
    try:
        es.parse_playbook_package('demo.zip',package(corrupt_file_hash=True))
    except ValueError as exc:
        assert 'file SHA mismatch' in str(exc)
    else:
        raise AssertionError('corrupt package content must reject package')

def test_r3_release2_package_without_v2_manifest_remains_compatible():
    parsed=es.parse_playbook_package('legacy.zip',legacy_package_without_v2_manifest())
    assert parsed['package_manifest_v2_status']['reason']=='not_present'
