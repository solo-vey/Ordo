#!/usr/bin/env python3
import argparse, hashlib, json, shutil, sys
from datetime import datetime, timezone
from pathlib import Path

RUNS=[f'RUN_{i:02d}' for i in range(1,6)]
VARIANTS=['yaml_playbook','structured_instructions','mixed_accumulated_instructions','domain_adapted_all_in_one']
CANONICAL={'CONFIRMED'}

def now(): return datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def load(p): return json.loads(Path(p).read_text())
def dump(p,obj): Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def root_dirs(root):
 for d in ['governance','task_classes','manifests','comparative_analysis','working_workspace']:(root/d).mkdir(parents=True,exist_ok=True)
 dump(root/'comparative_analysis/SCORE_LEDGER.json',{'schema_version':'benchmark.score_ledger.v1','evidence_base_version':'v1','records':[]})
 write_scoreboard(root)

def record_dir(root,variant,run,rev,canonical=False):
 base=root/'task_classes/default_test_class/default_test_case/04_runs'/variant
 bucket='confirmed_runs' if canonical else 'working_runs'
 return base/bucket/run/f'revision_{rev:02d}'
def records(root):
 for p in root.rglob('RUN_ACCEPTANCE_RECORD.json'):
  try: yield p,load(p)
  except Exception: continue

def next_rev(root,variant,run):
 vals=[r.get('revision',0) for _,r in records(root) if r.get('variant')==variant and r.get('run_id')==run]
 return max(vals,default=0)+1

def receive(a):
 root=Path(a.root); art=Path(a.artifact); rev=next_rev(root,a.variant,a.run); d=record_dir(root,a.variant,a.run,rev)
 d.mkdir(parents=True,exist_ok=False); target=d/art.name; shutil.copy2(art,target)
 rec={'schema_version':'benchmark.run_acceptance_record.v1','run_id':a.run,'variant':a.variant,'playbook_version':a.playbook_version,'revision':rev,'status':'RECEIVED_NOT_CONFIRMED','artifact_audited':False,'integrity_status':'UNRESOLVED','result_sha256':sha(target),'audit_sha256':None,'scores':{'process_quality':0,'document_quality':0,'final_quality':0},'confirmed_by_user':False,'confirmation_evidence':None,'supersedes_revision':None,'artifact_path':str(target.relative_to(root)),'history':[{'event':'RECEIVED','timestamp':now()}]}
 dump(d/'RUN_ACCEPTANCE_RECORD.json',rec); print(d)

def find_rec(root,variant,run,rev):
 for p,r in records(root):
  if r.get('variant')==variant and r.get('run_id')==run and r.get('revision')==rev:return p,r
 raise SystemExit('record not found')
def calc_doc(vals): return round(sum(vals)/4)
def audit(a):
 p,r=find_rec(Path(a.root),a.variant,a.run,a.revision)
 vals=[a.passport,a.jira,a.manual_qa,a.automation]; doc=calc_doc(vals); final=round((a.process+doc)/2)
 audit_path=Path(a.audit); r.update(status='AUDITED_AWAITING_CONFIRMATION',artifact_audited=True,integrity_status=a.integrity,result_sha256=r['result_sha256'],audit_sha256=sha(audit_path),scores={'process_quality':a.process,'document_quality':doc,'final_quality':final},document_components={'passport':a.passport,'jira':a.jira,'manual_qa':a.manual_qa,'automation':a.automation})
 r['history'].append({'event':'AUDITED','timestamp':now()}); shutil.copy2(audit_path,p.parent/audit_path.name); dump(p,r); print(json.dumps(r['scores']))
def promote(a):
 root=Path(a.root); p,r=find_rec(root,a.variant,a.run,a.revision)
 if r['status']!='AUDITED_AWAITING_CONFIRMATION' or not r['artifact_audited'] or r['integrity_status']!='PASS': raise SystemExit('fail-closed: audit/integrity incomplete')
 if not a.confirmation.strip(): raise SystemExit('fail-closed: explicit user confirmation required')
 r['status']='CONFIRMED';r['confirmed_by_user']=True;r['confirmation_evidence']=a.confirmation;r['history'].append({'event':'CONFIRMED','timestamp':now()})
 dest=record_dir(root,a.variant,a.run,a.revision,True); dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists(): raise SystemExit('silent overwrite forbidden')
 shutil.copytree(p.parent,dest); dump(dest/'RUN_ACCEPTANCE_RECORD.json',r); shutil.rmtree(p.parent)
 rebuild(root); print(dest)
def set_status(a,status):
 root=Path(a.root); p,r=find_rec(root,a.variant,a.run,a.revision);r['status']=status;r['history'].append({'event':status,'timestamp':now(),'note':a.reason});dump(p,r);rebuild(root)
def rebuild(root):
 active=[]
 for p,r in records(root):
  if r.get('status') in CANONICAL and r.get('confirmed_by_user'): active.append(r)
 dump(root/'comparative_analysis/SCORE_LEDGER.json',{'schema_version':'benchmark.score_ledger.v1','evidence_base_version':'v1','records':active})
 write_scoreboard(root)
def write_scoreboard(root):
 cells={(r,v):'—' for r in RUNS for v in VARIANTS}
 if (root/'comparative_analysis/SCORE_LEDGER.json').exists():
  for x in load(root/'comparative_analysis/SCORE_LEDGER.json').get('records',[]):
   s=x['scores'];cells[(x['run_id'],x['variant'])]=f"{s['process_quality']} / {s['document_quality']} / {s['final_quality']}"
 lines=['# Current Comparative Scoreboard','','| RUN | YAML playbook | Structured instructions | Mixed accumulated | Domain-adapted all-in-one |','|---|---:|---:|---:|---:|']
 for r in RUNS: lines.append('| '+r+' | '+' | '.join(cells[(r,v)] for v in VARIANTS)+' |')
 (root/'comparative_analysis').mkdir(parents=True,exist_ok=True);(root/'comparative_analysis/CURRENT_COMPARATIVE_SCOREBOARD.md').write_text('\n'.join(lines)+'\n')
def validate(a):
 root=Path(a.root); errs=[]
 for p,r in records(root):
  if r.get('status')=='CONFIRMED':
   if not r.get('confirmed_by_user'): errs.append(f'{p}: no confirmation')
   if not r.get('artifact_audited'): errs.append(f'{p}: not audited')
   if r.get('integrity_status')!='PASS': errs.append(f'{p}: integrity not PASS')
  s=r.get('scores',{}); exp=round((s.get('process_quality',0)+s.get('document_quality',0))/2)
  if s.get('final_quality')!=exp: errs.append(f'{p}: final formula mismatch')
 if errs: print('\n'.join(errs)); return 1
 print('PASS'); return 0

def main():
 ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest='cmd',required=True)
 q=sp.add_parser('init');q.add_argument('root')
 q=sp.add_parser('receive');q.add_argument('root');q.add_argument('--variant',choices=VARIANTS,required=True);q.add_argument('--run',choices=RUNS,required=True);q.add_argument('--playbook-version',required=True);q.add_argument('--artifact',required=True)
 q=sp.add_parser('audit');q.add_argument('root');q.add_argument('--variant',choices=VARIANTS,required=True);q.add_argument('--run',choices=RUNS,required=True);q.add_argument('--revision',type=int,required=True);q.add_argument('--audit',required=True);q.add_argument('--integrity',choices=['PASS','FAIL','UNRESOLVED','NOT_APPLICABLE'],required=True);q.add_argument('--process',type=int,required=True);q.add_argument('--passport',type=int,required=True);q.add_argument('--jira',type=int,required=True);q.add_argument('--manual-qa',type=int,required=True);q.add_argument('--automation',type=int,required=True)
 q=sp.add_parser('confirm');q.add_argument('root');q.add_argument('--variant',choices=VARIANTS,required=True);q.add_argument('--run',choices=RUNS,required=True);q.add_argument('--revision',type=int,required=True);q.add_argument('--confirmation',required=True)
 for name in ['reject','invalidate']:
  q=sp.add_parser(name);q.add_argument('root');q.add_argument('--variant',choices=VARIANTS,required=True);q.add_argument('--run',choices=RUNS,required=True);q.add_argument('--revision',type=int,required=True);q.add_argument('--reason',required=True)
 q=sp.add_parser('scoreboard');q.add_argument('root')
 q=sp.add_parser('validate');q.add_argument('root')
 a=ap.parse_args()
 if a.cmd=='init': root_dirs(Path(a.root))
 elif a.cmd=='receive': receive(a)
 elif a.cmd=='audit': audit(a)
 elif a.cmd=='confirm': promote(a)
 elif a.cmd=='reject': set_status(a,'REJECTED')
 elif a.cmd=='invalidate': set_status(a,'QUARANTINED')
 elif a.cmd=='scoreboard': rebuild(Path(a.root))
 elif a.cmd=='validate': sys.exit(validate(a))
if __name__=='__main__': main()
