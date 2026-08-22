#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, shutil
from pathlib import Path

FILES=[
 'information_object_catalog.yaml','information_group_catalog.yaml','artifact_catalog.yaml',
 'information_flow_graph.yaml','interaction_projection.yaml','ordo_projection.yaml',
 'review_bundle_catalog.yaml','proposal_canonicalization.yaml','approval_ledger.yaml','scenario_matrix.yaml'
]

def init_package(package:Path,vibe:Path,overwrite:bool=False)->dict:
    package=package.resolve(); vibe=vibe.resolve(); src=vibe/'authoring_templates/information_model'; dst=package/'authoring'
    dst.mkdir(parents=True,exist_ok=True); created=[]; preserved=[]
    for name in FILES:
        s=src/name; d=dst/name
        if d.exists() and not overwrite:
            preserved.append(name); continue
        shutil.copy2(s,d); created.append(name)
    status={
      'schema_version':'1.0','model':'VIBE_INFORMATION_FIRST_AUTHORING_V1','status':'DESIGN',
      'source_of_truth':'authoring YAML files in this directory',
      'ordo_relation':'authoring model projects to canonical Ordo; it does not extend Ordo syntax',
      'created':created,'preserved':preserved
    }
    (dst/'AUTHORING_MODEL_STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {'status':'PASS','authoring_dir':str(dst),'created':created,'preserved':preserved}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('package'); ap.add_argument('--vibe-root',default=str(Path(__file__).resolve().parents[1])); ap.add_argument('--overwrite',action='store_true'); a=ap.parse_args()
    r=init_package(Path(a.package),Path(a.vibe_root),a.overwrite); print(json.dumps(r,ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
