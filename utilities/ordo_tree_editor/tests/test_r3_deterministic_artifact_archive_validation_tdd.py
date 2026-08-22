from __future__ import annotations
import io, json, zipfile, hashlib
from pathlib import Path
import yaml
from utilities.ordo_tree_editor import editor_service as es


def _package_bytes(tmp_path: Path, *, archive=False, validator_fail=False, corrupt=False):
    root=tmp_path/'pkg'; (root/'source').mkdir(parents=True); (root/'tools').mkdir(); (root/'verification').mkdir()
    output='generated/out.zip' if archive else 'generated/out.md'
    state_path='archive_ref' if archive else 'artifact_ref'
    source={
      'graph_contract':{'entry_node':'N_BUILD','external_terminal_targets':['OUT_DONE']},
      'state':{'schema':{state_path:None}},
      'nodes':[{
        'id':'N_BUILD','type':'automatic','action':'PACKAGE.MATERIALIZE','writes':[state_path],
        'execution_contract':{'owner':'deterministic','runtime_executor':'package_tool'},
        'tool_ref':'tools/build.py','artifact':{'state_path':state_path,'expected_path':output},'output':output,'next':'G_VALID'
      }],
      'gates':[{'id':'G_VALID','method':'mechanical','trust_class':'deterministic','condition':'human prose not used for adapter','on_pass':'OUT_DONE','on_fail':'block','allowed_from':['N_BUILD']}]
    }
    (root/'source/program.ordo.yaml').write_text(yaml.safe_dump(source,sort_keys=False),encoding='utf-8')
    if archive:
      member=b'hello\n'; sha=hashlib.sha256(member).hexdigest()
      build=f'''import json,zipfile\nfrom pathlib import Path\nr=Path(__file__).resolve().parents[1]; p=r/'generated/out.zip'; p.parent.mkdir(exist_ok=True)\nwith zipfile.ZipFile(p,'w') as z: z.writestr('a.txt',b'hello\\n')\nprint(json.dumps({{'status':'PASS','route_key':'next','state_updates':{{'archive_ref':'generated/out.zip'}}}}))\n'''
      content={'required_members':['a.txt'],'member_hashes':{'a.txt':sha}}
      output_type='archive'
    else:
      build='''import json\nfrom pathlib import Path\nr=Path(__file__).resolve().parents[1]; p=r/'generated/out.md'; p.parent.mkdir(exist_ok=True); p.write_text('hello',encoding='utf-8')\nprint(json.dumps({'status':'PASS','route_key':'next','state_updates':{'artifact_ref':'generated/out.md'}}))\n'''
      content={'source':'state'}; output_type='document'
    (root/'tools/build.py').write_text(build,encoding='utf-8')
    (root/'tools/validate.py').write_text("import json,sys; print(json.dumps({'status':'FAIL' if %s else 'PASS'})); sys.exit(1 if %s else 0)\n"%(validator_fail,validator_fail),encoding='utf-8')
    registry={'schema_version':'1.0','artifacts':[{'artifact_id':'OUT_X','output_type':output_type,'output_path':output,'materialization_node_id':'N_BUILD','validators':['tools/validate.py'],'post_materialization_validation_required':True,'content_contract':content}]}
    (root/'verification/ARTIFACT_MATERIALIZATION_REGISTRY.json').write_text(json.dumps(registry),encoding='utf-8')
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
      for p in root.rglob('*'):
        if p.is_file(): z.write(p,p.relative_to(root).as_posix())
    return buf.getvalue(),source


def _run(tmp_path, archive=False, validator_fail=False, monkeypatch=None):
    raw,source=_package_bytes(tmp_path,archive=archive,validator_fail=validator_fail)
    parsed=es.parse_playbook_package('p.zip',raw); pid=parsed['id']
    if monkeypatch:
      monkeypatch.setattr(es,'_live_credentials',lambda payload:{'provider':'test','model':'none','base_url':'local'})
      monkeypatch.setattr(es,'_safe_semantic_model_recovery',lambda **kwargs: (_ for _ in ()).throw(AssertionError('mechanical gate called LLM recovery')))
    state={'archive_ref':None} if archive else {'artifact_ref':None}
    first=es._call_openai_live({'package_id':pid,'session_id':'s','run_id':'r','source':source,'current_id':'N_BUILD','phase':'enter','state':state,'state_revision':0,'history':[],'entry_mode':'root'})
    gate=es._call_openai_live({'package_id':pid,'session_id':'s','run_id':'r','source':source,'current_id':'G_VALID','phase':'enter','state':first['state'],'state_revision':1,'history':[],'previous_node_id':'N_BUILD','entry_mode':'transition'})
    return es.PLAYBOOK_PACKAGES[pid],first,gate


def test_artifact_gate_compiles_structured_validation_adapter_and_passes_without_model(tmp_path,monkeypatch):
    package,first,gate=_run(tmp_path,monkeypatch=monkeypatch)
    sem=package['semantic_plan']['elements']['G_VALID']
    assert sem['execution_adapter']['runtime_executor']=='artifact_validation'
    assert sem['execution_adapter']['artifact_validation']['state_path']=='artifact_ref'
    assert gate['route_key']=='on_pass' and gate['next_id']=='OUT_DONE'
    det=gate['debug']['runtime']['deterministic_gate']
    assert det['execution_class']=='deterministic_artifact_validation'
    assert all(x['status']=='pass' for x in det['checks'])


def test_artifact_validator_fail_routes_on_fail_without_model(tmp_path,monkeypatch):
    _,_,gate=_run(tmp_path,validator_fail=True,monkeypatch=monkeypatch)
    assert gate['route_key']=='on_fail'
    det=gate['debug']['runtime']['deterministic_gate']
    assert any(x['check_id']=='validator:tools/validate.py' and x['status']=='fail' for x in det['checks'])


def test_archive_gate_checks_readability_members_and_hashes_without_model(tmp_path,monkeypatch):
    _,_,gate=_run(tmp_path,archive=True,monkeypatch=monkeypatch)
    assert gate['route_key']=='on_pass'
    ids={x['check_id'] for x in gate['debug']['runtime']['deterministic_gate']['checks']}
    assert {'archive_readable','archive_crc_integrity','archive_required_members','archive_member_sha256:a.txt'} <= ids


def test_unsupported_mechanical_condition_never_calls_semantic_recovery(tmp_path,monkeypatch):
    source={'graph_contract':{'entry_node':'G','external_terminal_targets':['OUT']},'state':{'schema':{'x':'v'}},'nodes':[],'gates':[{'id':'G','method':'mechanical','trust_class':'deterministic','condition':'state.x has magical property','on_pass':'OUT','on_fail':'block'}]}
    root=tmp_path/'q'; (root/'source').mkdir(parents=True); (root/'source/program.ordo.yaml').write_text(yaml.safe_dump(source,sort_keys=False),encoding='utf-8')
    buf=io.BytesIO();
    with zipfile.ZipFile(buf,'w') as z:z.write(root/'source/program.ordo.yaml','source/program.ordo.yaml')
    parsed=es.parse_playbook_package('q.zip',buf.getvalue()); pid=parsed['id']
    monkeypatch.setattr(es,'_live_credentials',lambda payload:{'provider':'test','model':'none','base_url':'local'})
    monkeypatch.setattr(es,'_safe_semantic_model_recovery',lambda **kwargs: (_ for _ in ()).throw(AssertionError('mechanical gate called LLM recovery')))
    out=es._call_openai_live({'package_id':pid,'session_id':'s','run_id':'r','source':source,'current_id':'G','phase':'enter','state':{'x':'v'},'state_revision':0,'history':[],'entry_mode':'root','semantic_fallback_policy':'automatic_safe'})
    assert out['run_status']=='halted'
    assert out['completion_reason']=='deterministic_mechanical_validation_unresolved'
    assert out['debug']['runtime']['mechanical_model_calls']==0

def test_archive_without_declared_members_hashes_halts_as_profile_gap_not_model(tmp_path,monkeypatch):
    raw,source=_package_bytes(tmp_path,archive=True)
    # Remove structured archive membership/hash contract but keep archive producer.
    with zipfile.ZipFile(io.BytesIO(raw)) as zin:
        files={i.filename:zin.read(i.filename) for i in zin.infolist() if not i.is_dir()}
    reg=json.loads(files['verification/ARTIFACT_MATERIALIZATION_REGISTRY.json'])
    reg['artifacts'][0]['content_contract']={}
    files['verification/ARTIFACT_MATERIALIZATION_REGISTRY.json']=json.dumps(reg).encode()
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as zout:
        for name,data in files.items(): zout.writestr(name,data)
    parsed=es.parse_playbook_package('gap.zip',buf.getvalue()); pid=parsed['id']
    monkeypatch.setattr(es,'_live_credentials',lambda payload:{'provider':'test','model':'none','base_url':'local'})
    monkeypatch.setattr(es,'_safe_semantic_model_recovery',lambda **kwargs: (_ for _ in ()).throw(AssertionError('mechanical gate called LLM recovery')))
    first=es._call_openai_live({'package_id':pid,'session_id':'s','run_id':'r','source':source,'current_id':'N_BUILD','phase':'enter','state':{'archive_ref':None},'state_revision':0,'history':[],'entry_mode':'root'})
    gate=es._call_openai_live({'package_id':pid,'session_id':'s','run_id':'r','source':source,'current_id':'G_VALID','phase':'enter','state':first['state'],'state_revision':1,'history':[],'previous_node_id':'N_BUILD','entry_mode':'transition'})
    assert gate['run_status']=='halted'
    assert gate['completion_reason']=='generated_profile_validation_contract_incomplete'
    assert gate['failure_class']=='profile_contract_gap'
    det=gate['debug']['runtime']['deterministic_gate']
    assert det['profile_contract_gap'] is True
    assert 'archive_required_members_not_declared' in det['validation_contract_gaps']
    assert 'archive_hash_contract_not_declared' in det['validation_contract_gaps']


def test_canonical_field_present_assertion_executes_mechanically_without_model(tmp_path,monkeypatch):
    source={'graph_contract':{'entry_node':'G','external_terminal_targets':['OUT']},'state':{'schema':{'artifact_ref':None}},'nodes':[],'gates':[{'id':'G','method':'mechanical','trust_class':'deterministic','assert':'FIELD_PRESENT','source':'state.artifact_ref','on_pass':'OUT','on_fail':'block'}]}
    root=tmp_path/'assertpkg'; (root/'source').mkdir(parents=True); (root/'source/program.ordo.yaml').write_text(yaml.safe_dump(source,sort_keys=False),encoding='utf-8')
    buf=io.BytesIO();
    with zipfile.ZipFile(buf,'w') as z:z.write(root/'source/program.ordo.yaml','source/program.ordo.yaml')
    parsed=es.parse_playbook_package('assert.zip',buf.getvalue()); pid=parsed['id']
    monkeypatch.setattr(es,'_live_credentials',lambda payload:{'provider':'test','model':'none','base_url':'local'})
    monkeypatch.setattr(es,'_safe_semantic_model_recovery',lambda **kwargs: (_ for _ in ()).throw(AssertionError('mechanical gate called LLM recovery')))
    passed=es._call_openai_live({'package_id':pid,'session_id':'s','run_id':'r','source':source,'current_id':'G','phase':'enter','state':{'artifact_ref':'generated/x.md'},'state_revision':0,'history':[],'entry_mode':'root'})
    assert passed['route_key']=='on_pass'
    det=passed['debug']['runtime']['deterministic_gate']
    assert det['canonical_assertion'] is True
    assert det['checks'][0]['check_id']=='FIELD_PRESENT'
    failed=es._call_openai_live({'package_id':pid,'session_id':'s2','run_id':'r2','source':source,'current_id':'G','phase':'enter','state':{'artifact_ref':None},'state_revision':0,'history':[],'entry_mode':'root'})
    assert failed['route_key']=='on_fail'

def test_empty_artifact_fails_deterministically_without_model(tmp_path,monkeypatch):
    raw,source=_package_bytes(tmp_path,archive=False)
    parsed=es.parse_playbook_package('empty.zip',raw); pid=parsed['id']
    monkeypatch.setattr(es,'_live_credentials',lambda payload:{'provider':'test','model':'none','base_url':'local'})
    monkeypatch.setattr(es,'_safe_semantic_model_recovery',lambda **kwargs: (_ for _ in ()).throw(AssertionError('mechanical gate called LLM recovery')))
    first=es._call_openai_live({'package_id':pid,'session_id':'s','run_id':'r','source':source,'current_id':'N_BUILD','phase':'enter','state':{'artifact_ref':None},'state_revision':0,'history':[],'entry_mode':'root'})
    ws=es._runtime_workspace(package_id=pid,session_id='s',run_id='r'); (ws/'generated/out.md').write_bytes(b'')
    gate=es._call_openai_live({'package_id':pid,'session_id':'s','run_id':'r','source':source,'current_id':'G_VALID','phase':'enter','state':first['state'],'state_revision':1,'history':[],'previous_node_id':'N_BUILD','entry_mode':'transition'})
    assert gate['route_key']=='on_fail'
    assert any(x['check_id']=='artifact_non_empty' and x['status']=='fail' for x in gate['debug']['runtime']['deterministic_gate']['checks'])
    assert gate['debug']['runtime']['mechanical_model_calls']==0


def test_corrupt_zip_fails_deterministically_without_model(tmp_path,monkeypatch):
    raw,source=_package_bytes(tmp_path,archive=True)
    parsed=es.parse_playbook_package('corrupt.zip',raw); pid=parsed['id']
    monkeypatch.setattr(es,'_live_credentials',lambda payload:{'provider':'test','model':'none','base_url':'local'})
    monkeypatch.setattr(es,'_safe_semantic_model_recovery',lambda **kwargs: (_ for _ in ()).throw(AssertionError('mechanical gate called LLM recovery')))
    first=es._call_openai_live({'package_id':pid,'session_id':'s','run_id':'r','source':source,'current_id':'N_BUILD','phase':'enter','state':{'archive_ref':None},'state_revision':0,'history':[],'entry_mode':'root'})
    ws=es._runtime_workspace(package_id=pid,session_id='s',run_id='r'); (ws/'generated/out.zip').write_bytes(b'not-a-zip')
    gate=es._call_openai_live({'package_id':pid,'session_id':'s','run_id':'r','source':source,'current_id':'G_VALID','phase':'enter','state':first['state'],'state_revision':1,'history':[],'previous_node_id':'N_BUILD','entry_mode':'transition'})
    assert gate['route_key']=='on_fail'
    assert any(x['check_id']=='archive_readable' and x['status']=='fail' for x in gate['debug']['runtime']['deterministic_gate']['checks'])
    assert gate['debug']['runtime']['mechanical_model_calls']==0


def test_validator_crash_is_execution_error_not_model_recovery(tmp_path,monkeypatch):
    raw,source=_package_bytes(tmp_path,archive=False)
    with zipfile.ZipFile(io.BytesIO(raw)) as zin:
        files={i.filename:zin.read(i.filename) for i in zin.infolist() if not i.is_dir()}
    files['tools/validate.py']=b"raise RuntimeError('boom')\n"
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as zout:
        for name,data in files.items(): zout.writestr(name,data)
    parsed=es.parse_playbook_package('crash.zip',buf.getvalue()); pid=parsed['id']
    monkeypatch.setattr(es,'_live_credentials',lambda payload:{'provider':'test','model':'none','base_url':'local'})
    monkeypatch.setattr(es,'_safe_semantic_model_recovery',lambda **kwargs: (_ for _ in ()).throw(AssertionError('mechanical gate called LLM recovery')))
    first=es._call_openai_live({'package_id':pid,'session_id':'s','run_id':'r','source':source,'current_id':'N_BUILD','phase':'enter','state':{'artifact_ref':None},'state_revision':0,'history':[],'entry_mode':'root'})
    gate=es._call_openai_live({'package_id':pid,'session_id':'s','run_id':'r','source':source,'current_id':'G_VALID','phase':'enter','state':first['state'],'state_revision':1,'history':[],'previous_node_id':'N_BUILD','entry_mode':'transition'})
    assert gate['run_status']=='halted'
    assert gate['route_key'] is None
    assert gate['completion_reason']=='deterministic_validation_execution_error'
    assert gate['failure_class']=='deterministic_execution_error'
    assert gate['debug']['runtime']['mechanical_model_calls']==0
