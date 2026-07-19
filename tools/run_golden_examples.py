#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'examples/golden_examples.json'
def load():
    data=json.loads(MANIFEST.read_text(encoding='utf-8'))
    if data.get('schema_version')!='ordo.golden_examples.v1': raise SystemExit('unsupported golden example manifest')
    return data['examples']
def run_example(example):
    source=ROOT/example['package']
    if not source.is_dir(): raise SystemExit(f"missing package: {source}")
    with tempfile.TemporaryDirectory(prefix='ordo-golden-') as tmp:
        package=Path(tmp)/source.name; shutil.copytree(source,package)
        for template in example['commands']:
            command=[part.replace('{package}',str(package)) for part in template]
            if command and command[0] == 'ordo':
                command = [sys.executable, '-m', 'ordo.cli', *command[1:]]
            print('+',' '.join(command),flush=True)
            proc=subprocess.run(command,cwd=ROOT)
            if proc.returncode: return proc.returncode
    return 0
def main():
    ap=argparse.ArgumentParser(); g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--example'); g.add_argument('--all',action='store_true'); g.add_argument('--list',action='store_true')
    args=ap.parse_args(); examples=load(); by_id={x['id']:x for x in examples}
    if args.list:
        print('\n'.join(by_id)); return 0
    selected=examples if args.all else [by_id.get(args.example)]
    if selected==[None]: ap.error(f'unknown example: {args.example}')
    for ex in selected:
        print(f"== {ex['id']} ==",flush=True)
        rc=run_example(ex)
        if rc: return rc
    print(f"golden examples: PASS ({len(selected)})")
    return 0
if __name__=='__main__': raise SystemExit(main())
