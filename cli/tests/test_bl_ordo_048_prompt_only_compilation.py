from pathlib import Path
import json
import shutil
from ordo.prompt_compiler import compile_prompt_only, validate_prompt_compilation, assess_runtime_route

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'packages/history_event_guided_intake/source/program.ordo.yaml'

def test_compile_and_validate(tmp_path):
    m=compile_prompt_only(SOURCE,tmp_path,playbook_version='0.1.1',framework_version='0.5.0-rc.3')
    assert m['compilation_target']=='prompt_only'
    assert m['equivalent_to_engine_runtime'] is False
    assert m['guarantees_lost']
    assert validate_prompt_compilation(tmp_path,source_path=SOURCE)['status']=='passed'

def test_missing_guarantee_declaration_fails(tmp_path):
    compile_prompt_only(SOURCE,tmp_path)
    p=tmp_path/'PROMPT_COMPILATION_MANIFEST.json'; d=json.loads(p.read_text()); d['guarantees_lost']=[]; p.write_text(json.dumps(d))
    assert validate_prompt_compilation(tmp_path,source_path=SOURCE)['status']=='failed'

def test_source_drift_invalidates(tmp_path):
    src=tmp_path/'program.yaml'; src.write_bytes(SOURCE.read_bytes())
    out=tmp_path/'out'; compile_prompt_only(src,out)
    src.write_text(src.read_text()+'\n# mutation\n')
    codes={x['code'] for x in validate_prompt_compilation(out,source_path=src)['issues']}
    assert 'ORDO-PROMPT-008' in codes

def test_routing_prompt_only_when_thresholds_pass():
    r=assess_runtime_route({'runs':3,'composite_score':95,'branch_score':90,'backtrack_score':90})
    assert r['recommended_target']=='prompt_only'

def test_routing_escalates_on_branch_or_backtrack_failure():
    r=assess_runtime_route({'runs':3,'composite_score':95,'branch_score':70,'backtrack_score':90})
    assert r['recommended_target']=='engine_runtime'
    assert 'branch_score_below_threshold' in r['blocking_reasons']

def test_prompt_only_package_profile(tmp_path):
    from ordo.package_profiles import build_package_profile
    package=tmp_path/'history_event_guided_intake'
    shutil.copytree(ROOT/'packages/history_event_guided_intake',package)
    out=tmp_path/'prompt-only.zip'
    report=build_package_profile(package,profile='prompt_only',out=out)
    assert report['status']=='passed'
    assert report['canonical_release'] is False
    import zipfile
    with zipfile.ZipFile(out) as zf:
        names=zf.namelist()
    assert any(x.endswith('/MODEL_INSTRUCTIONS.md') for x in names)
    assert any(x.endswith('/PROMPT_COMPILATION_MANIFEST.json') for x in names)
    assert not any('/source/' in x for x in names)
