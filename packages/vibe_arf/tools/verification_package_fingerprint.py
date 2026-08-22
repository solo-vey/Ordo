#!/usr/bin/env python3
from pathlib import Path
import hashlib

EXCLUDED_TOP={'reports','compiled','runtime','.verification_cache','.git','__pycache__'}
EXCLUDED_NAMES={'.dev_checkpoint.json'}

def package_fingerprint(root):
    root=Path(root).resolve(); h=hashlib.sha256(); count=0
    for p in sorted(root.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(root)
        if rel.parts and rel.parts[0] in EXCLUDED_TOP: continue
        if p.name in EXCLUDED_NAMES or '__pycache__' in rel.parts: continue
        data=p.read_bytes(); ph=hashlib.sha256(data).hexdigest()
        h.update(str(rel).replace('\\','/').encode()); h.update(b'\0'); h.update(str(len(data)).encode()); h.update(b'\0'); h.update(ph.encode()); h.update(b'\n'); count+=1
    return {'sha256':h.hexdigest(),'files':count}
