import json,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
TOOL=ROOT/'utilities/playbook_lifecycle/manage_playbook_checkpoint.py'
def pkg(tmp):
 p=tmp/'p'; p.mkdir(); (p/'playbook_release.json').write_text(json.dumps({'playbook_id':'x','playbook_version':'1.0.0'})); (p/'ordo.yml').write_text('id: x\n'); return p
def test_create_and_verify_round_trip(tmp_path):
 p=pkg(tmp_path); a=tmp_path/'cp.zip'; r=json.loads(subprocess.check_output([sys.executable,str(TOOL),'create',str(p),str(a)],text=True)); assert r['restore_round_trip']=='passed'; assert json.loads(subprocess.check_output([sys.executable,str(TOOL),'verify',str(a)],text=True))['identity']=='passed'
def test_tamper_is_rejected(tmp_path):
 p=pkg(tmp_path); a=tmp_path/'cp.zip'; subprocess.check_call([sys.executable,str(TOOL),'create',str(p),str(a)]); b=tmp_path/'bad.zip';
 with zipfile.ZipFile(a) as z: z.extractall(tmp_path/'x')
 (tmp_path/'x/checkpoint/package/ordo.yml').write_text('id: changed\n')
 with zipfile.ZipFile(b,'w') as z:
  [z.write(f,f.relative_to(tmp_path/'x')) for f in (tmp_path/'x').rglob('*') if f.is_file()]
 r=subprocess.run([sys.executable,str(TOOL),'verify',str(b)],text=True,capture_output=True); assert r.returncode!=0
def test_all_release_records_require_verified_checkpoint():
 for p in (ROOT/'packages').iterdir():
  if (p/'playbook_release.json').is_file():
   r=json.loads((p/'playbook_release.json').read_text()); rb=r['rollback']; assert rb['supported'] is True; assert rb['checkpoint_required_before_version_bump'] is True; assert rb['verification_required'] is True
