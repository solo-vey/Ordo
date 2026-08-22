#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, zipfile
from pathlib import Path

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('target', nargs='?', default=str(Path(__file__).resolve().parents[1]))
    args=ap.parse_args()
    t=Path(args.target).resolve()
    if t.is_file() and t.suffix.lower()=='.zip':
        with zipfile.ZipFile(t) as z:
            programs=sorted(n for n in z.namelist() if n.endswith('program.ordo.yaml'))
    else:
        programs=sorted(
            str(p.relative_to(t)).replace('\\','/')
            for p in t.rglob('program.ordo.yaml')
            if not p.is_relative_to(t/'canonical_support'/'language')
            and not p.is_relative_to(t/'cli_embedded')
        )
    checks={
        'exactly_one_program_ordo_yaml': len(programs)==1,
        'canonical_program_path': programs==['source/program.ordo.yaml'],
    }
    status='PASS' if all(checks.values()) else 'FAIL'
    print(json.dumps({'status':status,'program_files':programs,'checks':checks},indent=2))
    return 0 if status=='PASS' else 1
if __name__=='__main__':
    raise SystemExit(main())
