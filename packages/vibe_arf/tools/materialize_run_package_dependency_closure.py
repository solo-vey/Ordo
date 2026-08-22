#!/usr/bin/env python3
"""Compatibility wrapper: legacy RUN now means CLI_RUN."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from materialize_profile_dependency_closure import build_closure

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('--output',default='RUN_PACKAGE_DEPENDENCY_CLOSURE.json'); a=ap.parse_args(); d=build_closure(a.root,'CLI_RUN'); d['compatibility_alias']='RUN'; Path(a.root,a.output).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n'); print(json.dumps({'status':'PASS','files':d['file_count'],'output':a.output,'profile':'CLI_RUN'},indent=2))
if __name__=='__main__': main()
