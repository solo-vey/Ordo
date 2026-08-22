#!/usr/bin/env python3
import argparse,json,hashlib
from pathlib import Path

def fp(x): return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def valid_field(v):
 return isinstance(v,dict) and v.get('state') in {'known','unknown','conflict','not_applicable'} and isinstance(v.get('provenance'),dict) and v['provenance'].get('source') and v['provenance'].get('ref')
def merge(base,patch):
 out=json.loads(json.dumps(base))
 changes=[]
 for k,nv in patch.items():
  if not valid_field(nv): raise ValueError(f'{k}: field-level provenance required')
  ov=out.get(k)
  if ov is None:
   out[k]=nv; changes.append({'field':k,'action':'append'}); continue
  if not valid_field(ov): raise ValueError(f'{k}: existing field lacks provenance')
  if ov.get('state')=='known' and nv.get('state')=='unknown': raise ValueError(f'{k}: KNOWN_TO_UNKNOWN_DOWNGRADE')
  if ov.get('state')=='known' and nv.get('state')=='known' and ov.get('value')!=nv.get('value'):
   # authoritative conflict must be explicit, never silent replacement
   raise ValueError(f'{k}: AUTHORITATIVE_VALUE_OVERWRITE_REQUIRES_CONFLICT')
  if ov==nv: changes.append({'field':k,'action':'preserve'}); continue
  # non-destructive state strengthening/metadata merge
  merged=dict(ov); merged.update(nv)
  hist=list(ov.get('provenance_history',[])); hist.append(ov['provenance'])
  merged['provenance_history']=hist
  out[k]=merged; changes.append({'field':k,'action':'merge'})
 return out,changes

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--base',required=True); ap.add_argument('--patch',required=True); ap.add_argument('--out',required=True); ap.add_argument('--report')
 a=ap.parse_args(); base=json.loads(Path(a.base).read_text()); patch=json.loads(Path(a.patch).read_text())
 try: out,changes=merge(base,patch)
 except Exception as e:
  print(json.dumps({'status':'FAIL','error':str(e),'base_fingerprint':fp(base),'patch_fingerprint':fp(patch)},indent=2)); return 2
 Path(a.out).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 rep={'status':'PASS','base_fingerprint':fp(base),'patch_fingerprint':fp(patch),'output_fingerprint':fp(out),'changes':changes}
 if a.report: Path(a.report).write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(rep,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
