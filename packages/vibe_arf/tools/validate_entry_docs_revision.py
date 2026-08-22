#!/usr/bin/env python3
from pathlib import Path
import argparse,json,re,yaml

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('package'); a=ap.parse_args(); root=Path(a.package).resolve()
 src=root/'source/program.ordo.yaml'; findings=[]
 if not src.is_file(): findings.append({'code':'SOURCE_MISSING','path':'source/program.ordo.yaml'}); version=''
 else:
  d=yaml.safe_load(src.read_text()) or {}; version=str((d.get('ordo') or {}).get('package_version') or (d.get('module') or {}).get('version') or '')
 for rel in ['README.md','START_HERE.md']:
  p=root/rel
  if not p.is_file(): findings.append({'code':'ENTRY_DOC_MISSING','path':rel}); continue
  first='\n'.join(p.read_text(encoding='utf-8').splitlines()[:8])
  if version and version not in first and version.replace('0.1.0-','') not in first:
   findings.append({'code':'ENTRY_DOC_REVISION_STALE','path':rel,'expected':version})
 ok=not findings
 print(json.dumps({'status':'PASS' if ok else 'FAIL','package_version':version,'findings':findings},indent=2))
 return 0 if ok else 1
if __name__=='__main__': raise SystemExit(main())
