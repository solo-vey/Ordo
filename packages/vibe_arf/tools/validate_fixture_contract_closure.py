#!/usr/bin/env python3
from pathlib import Path
import argparse
from _alpha26_validation_common import load_json,emit

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('package'); a=ap.parse_args(); root=Path(a.package); errors=[]; warnings=[]
 c=load_json(root/'reports/SIMULATION_CONTRACT.json'); u=load_json(root/'reports/FIXTURE_USAGE.json')
 if c is None or u is None: return emit('VIBE_FIXTURE_CONTRACT_CLOSURE',['simulation contract and fixture usage reports required'])
 req_a=set(map(str,c.get('analyst_fixture_points') or [])); req_m=set(map(str,c.get('model_fixture_points') or [])); req_r=set(map(str,c.get('dynamic_recovery_fixture_points') or []))
 got_a=set(map(str,u.get('provided_analyst') or [])); got_m=set(map(str,u.get('provided_model') or [])); got_r=set(map(str,u.get('provided_recovery') or []))
 if req_a-got_a: errors.append(f'missing analyst fixtures {sorted(req_a-got_a)}')
 if req_m-got_m: errors.append(f'missing model fixtures {sorted(req_m-got_m)}')
 if req_r-got_r: errors.append(f'missing recovery fixtures {sorted(req_r-got_r)}')
 if u.get('unused'): warnings.append(f'unused fixtures {u.get("unused")}')
 return emit('VIBE_FIXTURE_CONTRACT_CLOSURE',errors,warnings)
if __name__=='__main__': raise SystemExit(main())
