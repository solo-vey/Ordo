#!/usr/bin/env python3
import json,sys
from pathlib import Path
p=Path(sys.argv[1]); r=json.loads((p/'BLACK_BOX_PRE_RELEASE_CAMPAIGN_REPORT.json').read_text())
checks=[len(r['runs'])==5,r['status']=='PASS',all(x['status']=='PASS' for x in r['runs']),any(x['correction_loop_used'] for x in r['runs']),len(list(p.glob('RUN_*_PRE_RELEASE_EVIDENCE.zip')))==5]
print(json.dumps({'status':'PASS' if all(checks) else 'FAIL','checks':checks},indent=2)); raise SystemExit(0 if all(checks) else 1)
