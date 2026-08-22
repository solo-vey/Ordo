#!/usr/bin/env python3
from __future__ import annotations
import argparse,datetime,hashlib,json,shutil
from pathlib import Path

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('package_root'); ap.add_argument('--source-id',required=True); ap.add_argument('--purpose',required=True); ap.add_argument('--authority',required=True); ap.add_argument('--provided-by',default='analyst'); ap.add_argument('--retention-mode',choices=['embed_authoritative','embed_evaluator_only','summary_plus_refresh_record','metadata_only'],required=True); ap.add_argument('--file'); ap.add_argument('--summary'); ap.add_argument('--external-locator'); ap.add_argument('--volatile',action='store_true'); ap.add_argument('--large',action='store_true')
 a=ap.parse_args(); root=Path(a.package_root); d=root/'analyst_context'; d.mkdir(parents=True,exist_ok=True); cp=d/'context_catalog.json'; cat=json.loads(cp.read_text()) if cp.exists() else {'schema_version':'1.0','records':[]}
 raw=None; h=None; stored=None
 if a.file:
  p=Path(a.file); raw=p.read_bytes(); h=hashlib.sha256(raw).hexdigest()
  if a.retention_mode in ('embed_authoritative','embed_evaluator_only'):
   sub='evaluator_only' if a.retention_mode=='embed_evaluator_only' else 'embedded'; out=d/sub/a.source_id; out.mkdir(parents=True,exist_ok=True); dst=out/p.name; shutil.copy2(p,dst); stored=dst.relative_to(root).as_posix()
 if (a.volatile or a.large) and a.retention_mode in ('embed_authoritative','embed_evaluator_only'):
  print(json.dumps({'status':'FAIL','code':'VOLATILE_OR_LARGE_MUST_USE_SUMMARY_OR_METADATA'})); return 2
 rec={'source_id':a.source_id,'purpose':a.purpose,'authority_status':a.authority,'provided_by':a.provided_by,'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'retention_mode':a.retention_mode,'access_scope':'evaluator_only' if a.retention_mode=='embed_evaluator_only' else 'authoring','volatile':a.volatile,'large':a.large,'refresh_required':bool(a.volatile or a.large),'content_hash_or_external_fingerprint':h or a.external_locator,'external_locator':a.external_locator,'summary':a.summary,'stored_path':stored}
 cat['records']=[r for r in cat.get('records',[]) if r.get('source_id')!=a.source_id]+[rec]; cp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n'); print(json.dumps({'status':'PASS','record':rec},ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
