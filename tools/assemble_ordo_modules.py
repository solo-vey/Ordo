#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import yaml

def assemble(manifest_path: Path) -> dict:
    manifest=yaml.safe_load(manifest_path.read_text(encoding='utf-8'))
    out={}
    for entry in manifest.get('modules',[]):
        path=manifest_path.parent/entry['path']
        module=yaml.safe_load(path.read_text(encoding='utf-8')) or {}
        if not isinstance(module,dict): raise ValueError(f'module must be mapping: {path}')
        unexpected=set(module)-set(entry.get('owns_top_level_keys',[]))
        if unexpected: raise ValueError(f'undeclared keys in {path}: {sorted(unexpected)}')
        duplicate=set(out)&set(module)
        if duplicate: raise ValueError(f'duplicate top-level keys: {sorted(duplicate)}')
        out.update(module)
    return out

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('manifest')
    ap.add_argument('--out')
    ap.add_argument('--check',action='store_true')
    ns=ap.parse_args()
    mp=Path(ns.manifest)
    data=assemble(mp)
    text=yaml.safe_dump(data,sort_keys=False,allow_unicode=True,width=120)
    target=Path(ns.out) if ns.out else mp.parent/(yaml.safe_load(mp.read_text())['assembly_target'])
    if ns.check:
        current=yaml.safe_load(target.read_text(encoding='utf-8'))
        if current!=data:
            print('assembled source differs from target')
            return 1
        print('assembled source matches target')
        return 0
    target.write_text(text,encoding='utf-8')
    print(target)
    return 0
if __name__=='__main__': raise SystemExit(main())
