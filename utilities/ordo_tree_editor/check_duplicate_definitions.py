#!/usr/bin/env python3
import ast, argparse, json
from pathlib import Path

def scan(path: Path):
    tree=ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
    seen={}; duplicates=[]
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
            name=node.name
            if name in seen:
                duplicates.append({'name':name,'first_line':seen[name],'duplicate_line':node.lineno,'kind':type(node).__name__})
            else: seen[name]=node.lineno
    return duplicates

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('paths',nargs='+'); args=ap.parse_args()
    findings=[]
    for raw in args.paths:
        p=Path(raw); findings += [{'file':str(p),**x} for x in scan(p)]
    out={'status':'PASS' if not findings else 'FAIL','duplicates':findings}
    print(json.dumps(out,ensure_ascii=False,indent=2)); raise SystemExit(0 if not findings else 1)
if __name__=='__main__': main()
