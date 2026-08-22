#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import yaml
FAMILIES=['core_identity','trigger','null_no_data','source_failure','lifecycle','output','history_transition']
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('package'); a=ap.parse_args(); root=Path(a.package).resolve(); src=root/'source/program.ordo.yaml'
    p=yaml.safe_load(src.read_text(encoding='utf-8')) or {}
    nodes=[x for x in p.get('nodes') or [] if isinstance(x,dict)]; gates=[x for x in p.get('gates') or [] if isinstance(x,dict)]
    scenarios=[
      {'id':'SC_HAPPY_PATH','families':['core_identity','trigger','output','history_transition'],'intent':'successful end-to-end path','status':'designed'},
      {'id':'SC_NULL_NO_DATA','families':['null_no_data'],'intent':'required/optional absence semantics','status':'designed'},
      {'id':'SC_SOURCE_FAILURE','families':['source_failure'],'intent':'source/tool/evidence failure and local recovery','status':'designed'},
      {'id':'SC_LIFECYCLE','families':['lifecycle'],'intent':'approval/stale/revalidation lifecycle','status':'designed'},
    ]
    out={'schema_version':'1.0','required_families':FAMILIES,'scenarios':scenarios,
         'derived_from':{'nodes':len(nodes),'gates':len(gates)},'rule':'coverage status is derived from executed scenario families'}
    ad=root/'authoring'; ad.mkdir(exist_ok=True); (ad/'scenario_matrix.yaml').write_text(yaml.safe_dump(out,sort_keys=False),encoding='utf-8')
    print(json.dumps({'status':'PASS','output':str(ad/'scenario_matrix.yaml'),'scenarios':len(scenarios)},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
