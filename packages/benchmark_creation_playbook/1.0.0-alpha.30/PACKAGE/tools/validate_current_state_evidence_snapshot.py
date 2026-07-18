#!/usr/bin/env python3
import argparse, hashlib, json, zipfile, tempfile, shutil
from pathlib import Path
FORBIDDEN=('version-history','__pycache__','.pyc','.bak','.tmp','.old','.orig','superseded')
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''): h.update(b)
 return h.hexdigest()
def validate(z):
 z=Path(z); errs=[]
 with zipfile.ZipFile(z) as q:
  bad=q.testzip();
  if bad: errs.append('ZIP_INTEGRITY:'+bad)
  names=q.namelist()
  for n in names:
   if any(x in n.lower() for x in FORBIDDEN): errs.append('FORBIDDEN_PATH:'+n)
  with tempfile.TemporaryDirectory() as td:
   q.extractall(td); roots=[p for p in Path(td).iterdir() if p.is_dir()]; root=roots[0] if len(roots)==1 else Path(td)
   req=['README.md','CURRENT_STATE_MANIFEST.json','SELECTION_REPORT.json','EXCLUSION_REPORT.json','LANGUAGE_AUDIT.json','SHA256SUMS.txt']
   for x in req:
    if not (root/x).exists(): errs.append('MISSING:'+x)
   if (root/'SHA256SUMS.txt').exists():
    for line in (root/'SHA256SUMS.txt').read_text().splitlines():
     digest,rel=line.split('  ',1); p=root/rel
     if not p.exists() or sha(p)!=digest: errs.append('CHECKSUM:'+rel)
   for j in root.rglob('*.json'):
    try: json.loads(j.read_text())
    except Exception as e: errs.append('JSON:'+str(j.relative_to(root)))
   if (root/'README.md').exists() and 'current-state-only evidence snapshot' not in (root/'README.md').read_text(): errs.append('MISSING_DECLARATION')
 return {'status':'PASS_RELEASE' if not errs else 'BLOCKED','green_light':not errs,'errors':errs,'zip_sha256':sha(z)}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('zip');x=a.parse_args();r=validate(x.zip);print(json.dumps(r,indent=2));raise SystemExit(0 if r['green_light'] else 2)
