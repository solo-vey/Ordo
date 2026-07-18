import json, subprocess, sys
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]
PACKAGES=['history_event_guided_intake','ordo_applied_project_factory','ordo_hybrid_executor','ordo_project_builder']
def test_all_packages_have_release_records():
 for p in PACKAGES:
  m=yaml.safe_load((ROOT/'packages'/p/'ordo.yml').read_text())
  r=json.loads((ROOT/'packages'/p/m['playbook_release']).read_text())
  assert r['schema_version']=='ordo.playbook_release.v1'
  current=json.loads((ROOT/'manifests/VERSION_STATE.json').read_text())['framework']['version']
  assert r['built_with']['framework_version']==current
  assert r['automatic_runtime_mutation'] is False
  assert r['rollback']['supported'] is True
def test_release_index_covers_all_packages():
 idx=json.loads((ROOT/'manifests/PLAYBOOK_RELEASE_INDEX.json').read_text())
 assert {x['playbook_id'] for x in idx['playbooks']}=={'history_event.guided_intake','ordo.applied_project_factory','ordo.hybrid_executor','ordo.project_builder'}
def run(active,new,tmp_path):
 a=tmp_path/'a.json'; n=tmp_path/'n.json'; a.write_text(json.dumps(active)); n.write_text(json.dumps(new))
 return json.loads(subprocess.check_output([sys.executable,str(ROOT/'tools/resolve_playbook_upgrade.py'),str(a),str(n)],text=True))
def base(v='1.0.0',mode='compatible'):
 return {'playbook_id':'x','playbook_version':v,'compatibility':{'previous_playbook':mode},'changes':{},'automatic_runtime_mutation':False}
def test_same_version_no_action(tmp_path): assert run(base(),base(),tmp_path)['decision']=='no_action'
def test_compatible_requires_revalidation(tmp_path): assert run(base(),base('1.1.0'),tmp_path)['decision']=='recommended_revalidation'
def test_migration_required(tmp_path): assert run(base(),base('2.0.0','migration_required'),tmp_path)['decision']=='migration_required'
def test_incompatible_blocked(tmp_path): assert run(base(),base('2.0.0','incompatible'),tmp_path)['decision']=='upgrade_blocked'
def test_id_mismatch_blocked(tmp_path):
 n=base('1.1.0'); n['playbook_id']='y'; assert run(base(),n,tmp_path)['decision']=='upgrade_blocked'
def test_never_mutates_runtime(tmp_path): assert run(base(),base('1.1.0'),tmp_path)['automatic_runtime_mutation'] is False
