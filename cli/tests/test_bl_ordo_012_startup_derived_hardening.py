from pathlib import Path
import shutil, yaml
from ordo.startup_artifact_reconcile import reconcile
ROOT=Path(__file__).resolve().parents[2]
PACKAGES=['history_event_guided_intake','ordo_applied_project_factory','ordo_hybrid_executor','ordo_project_builder']

def test_all_canonical_packages_reconcile():
    for name in PACKAGES:
        result=reconcile(ROOT/'packages'/name)
        assert result['status']=='passed', (name,result)

def _copy(tmp_path,name='ordo_hybrid_executor'):
    dst=tmp_path/name; shutil.copytree(ROOT/'packages'/name,dst); return dst

def _source(pkg):
    manifest=yaml.safe_load((pkg/'ordo.yml').read_text()); return pkg/manifest['source']

def test_path_traversal_is_blocked(tmp_path):
    pkg=_copy(tmp_path); p=_source(pkg); d=yaml.safe_load(p.read_text())
    d['artifact_sync']['derived_artifacts'][0]['path']='../../outside.txt'; p.write_text(yaml.safe_dump(d,sort_keys=False))
    r=reconcile(pkg); assert r['status']=='blocked'; assert any(x['check_id']=='sync_path_safe' for x in r['findings'])

def test_strict_artifact_without_sha_is_blocked(tmp_path):
    pkg=_copy(tmp_path); p=_source(pkg); d=yaml.safe_load(p.read_text())
    d['artifact_sync']['derived_artifacts'][0].pop('sha256'); p.write_text(yaml.safe_dump(d,sort_keys=False))
    r=reconcile(pkg); assert r['status']=='blocked'; assert any(x['check_id']=='derived_artifact_sha_required' for x in r['findings'])

def test_duplicate_derived_artifact_is_blocked(tmp_path):
    pkg=_copy(tmp_path); p=_source(pkg); d=yaml.safe_load(p.read_text())
    d['artifact_sync']['derived_artifacts'].append(dict(d['artifact_sync']['derived_artifacts'][0])); p.write_text(yaml.safe_dump(d,sort_keys=False))
    r=reconcile(pkg); assert r['status']=='blocked'; assert any(x['check_id']=='derived_artifact_unique' for x in r['findings'])

def test_source_derived_overlap_is_blocked(tmp_path):
    pkg=_copy(tmp_path); p=_source(pkg); d=yaml.safe_load(p.read_text())
    a=d['artifact_sync']['derived_artifacts'][0]; a['path']='source/program.ordo.yaml'; a['sha256']='0'*64; p.write_text(yaml.safe_dump(d,sort_keys=False))
    r=reconcile(pkg); assert r['status']=='blocked'; assert any(x['check_id']=='derived_not_source_of_truth' for x in r['findings'])
