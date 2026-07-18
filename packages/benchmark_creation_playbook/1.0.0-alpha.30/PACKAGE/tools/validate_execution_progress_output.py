#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]; renderer=root/'tools/render_execution_progress_event.py'; reg=root/'EXECUTION_PROGRESS_STATUS_REGISTRY.yaml'; fx=root/'fixtures/execution_progress'
cases=[]
for p in sorted(fx.glob('*.json')):
 cp=subprocess.run([sys.executable,str(renderer),str(p),'--registry',str(reg)],capture_output=True,text=True)
 expected=0 if p.name.startswith('positive_') else 2
 cases.append({'fixture':p.name,'expected_exit':expected,'actual_exit':cp.returncode,'pass':cp.returncode==expected,'output':cp.stdout.strip()})
report={'schema_version':'ordo.execution_progress_acceptance.v1','tests':cases,'passed':sum(x['pass'] for x in cases),'total':len(cases),'status':'PASS' if all(x['pass'] for x in cases) else 'FAIL'}
out=root/'reports/EXECUTION_PROGRESS_OUTPUT_ACCEPTANCE_TESTS.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(0 if report['status']=='PASS' else 1)
