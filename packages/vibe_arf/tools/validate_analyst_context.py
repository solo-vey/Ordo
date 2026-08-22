#!/usr/bin/env python3
import argparse,json
from pathlib import Path

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('package_root'); a=ap.parse_args(); root=Path(a.package_root); p=root/'analyst_context/context_catalog.json'
 if not p.exists(): print(json.dumps({'status':'FAIL','code':'CATALOG_MISSING'})); return 2
 d=json.loads(p.read_text()); errs=[]; ids=set()
 for i,r in enumerate(d.get('records',[])):
  sid=r.get('source_id');
  if not sid or sid in ids: errs.append(f'record[{i}]:source_id');
  ids.add(sid)
  for k in ['purpose','authority_status','provided_by','captured_at','retention_mode','access_scope','refresh_required','content_hash_or_external_fingerprint']:
   if r.get(k) in (None,''): errs.append(f'{sid}:{k}')
  if (r.get('volatile') or r.get('large')) and not r.get('refresh_required'): errs.append(f'{sid}:refresh_required')
  if r.get('retention_mode')=='embed_evaluator_only' and r.get('access_scope')!='evaluator_only': errs.append(f'{sid}:evaluator_access')
  if r.get('retention_mode')=='summary_plus_refresh_record' and not r.get('summary'): errs.append(f'{sid}:summary')
 print(json.dumps({'status':'PASS' if not errs else 'FAIL','records':len(d.get('records',[])),'errors':errs},indent=2)); return 0 if not errs else 1
if __name__=='__main__': raise SystemExit(main())
