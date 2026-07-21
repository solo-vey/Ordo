import importlib.util, json, tempfile, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('release_integrity',ROOT/'tools/release_integrity.py')
ri=importlib.util.module_from_spec(spec); spec.loader.exec_module(ri)

def make_root(base:Path):
    root=base/'workspace'; (root/'manifests').mkdir(parents=True)
    identity={'schema_version':'ordo.release_identity.v1','release_id':'r1','archive_filename':'canonical.zip','internal_root':'CANONICAL_R1','language_version':'1.0.0','framework_version':'2.0.0'}
    (root/'manifests/RELEASE_IDENTITY.json').write_text(json.dumps(identity))
    state={'release_id':'r1','language':{'version':'1.0.0'},'framework':{'version':'2.0.0'}}
    (root/'manifests/VERSION_STATE.json').write_text(json.dumps(state))
    (root/'source.txt').write_text('stable')
    return root,identity

def reports(run='run-1',source='abc',stamp='2026-07-14T00:00:00Z'):
    gate={'run_id':run,'release_id':'r1','source_tree_hash':source,'generated_at':stamp}
    selfcheck={'run_id':run,'release_id':'r1','source_tree_hash':source,'generated_at':stamp}
    return {'reports/delivery/current/DELIVERY_GATE_REPORT.json':json.dumps(gate),'reports/self-check/current/FINAL_PACKAGE_SELF_CHECK_REPORT.json':json.dumps(selfcheck),'reports/self-check/current/FINAL_PACKAGE_SELF_CHECK_REPORT.md':'# current\n'}

def test_identity_controls_filename_and_internal_root():
    with tempfile.TemporaryDirectory() as td:
        root,identity=make_root(Path(td)); out=Path(td)/'wrong.zip'
        try: ri.build_verified_archive(root,out,reports(),'run-1')
        except ValueError as e: assert 'canonical.zip' in str(e)
        else: raise AssertionError('wrong filename accepted')

def test_verified_archive_uses_declared_root_and_fresh_evidence():
    with tempfile.TemporaryDirectory() as td:
        root,identity=make_root(Path(td)); out=Path(td)/'canonical.zip'
        result=ri.build_verified_archive(root,out,reports(),'run-1')
        assert result['status']=='passed'
        with zipfile.ZipFile(out) as zf:
            assert all(n.startswith('CANONICAL_R1/') for n in zf.namelist())

def test_post_checksum_mutation_is_detected():
    with tempfile.TemporaryDirectory() as td:
        root,identity=make_root(Path(td)); parent=Path(td)/'stage'; parent.mkdir()
        staged=ri.stage_candidate(root,parent,reports())
        (staged/'source.txt').write_text('mutated')
        result=ri.verify_extracted(staged,identity,'run-1')
        assert result['status']=='failed'
        assert any('checksum mismatch' in x for x in result['failures'])

def test_stale_or_mismatched_evidence_is_rejected():
    with tempfile.TemporaryDirectory() as td:
        root,identity=make_root(Path(td)); parent=Path(td)/'stage'; parent.mkdir()
        bad=reports(); bad['reports/self-check/current/FINAL_PACKAGE_SELF_CHECK_REPORT.json']=json.dumps({'run_id':'old','release_id':'r1','source_tree_hash':'old','generated_at':'old'})
        staged=ri.stage_candidate(root,parent,bad)
        result=ri.verify_extracted(staged,identity,'run-1')
        assert result['status']=='failed'
        assert any('run_id mismatch' in x or 'source hash mismatch' in x or 'timestamp mismatch' in x for x in result['failures'])

def test_version_state_must_match_release_identity():
    with tempfile.TemporaryDirectory() as td:
        root,identity=make_root(Path(td)); state=json.loads((root/'manifests/VERSION_STATE.json').read_text()); state['framework']['version']='9.9.9'; (root/'manifests/VERSION_STATE.json').write_text(json.dumps(state))
        parent=Path(td)/'stage'; parent.mkdir(); staged=ri.stage_candidate(root,parent,reports())
        result=ri.verify_extracted(staged,identity,'run-1')
        assert result['status']=='failed'
        assert 'framework version mismatch' in result['failures']
