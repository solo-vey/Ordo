from pathlib import Path
from ordo.startup_artifact_reconcile import reconcile
ROOT=Path(__file__).resolve().parents[2]

def test_real_package_reconciles():
    r=reconcile(ROOT/'packages/history_event_guided_intake')
    assert r['status']=='passed', r
    assert r['summary']['errors']==0

def test_missing_artifact_blocks(tmp_path):
    import shutil,yaml
    src=ROOT/'packages/history_event_guided_intake'; dst=tmp_path/'pkg'; shutil.copytree(src,dst)
    (dst/'PROMPT_MANIFEST.json').unlink()
    r=reconcile(dst)
    assert r['status']=='blocked'
    assert any(f['check_id']=='derived_artifact_exists' for f in r['findings'])
