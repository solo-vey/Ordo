#!/usr/bin/env python3
import json,pathlib,subprocess,sys
root=pathlib.Path(__file__).resolve().parents[1]; tool=root/'tools/validate_representation_governance.py'; fd=root/'fixtures/representation_governance'
results=[]
for p in sorted(fd.glob('*.json')):
 expect=0 if p.name.startswith('positive_') else 2
 cp=subprocess.run([sys.executable,str(tool),'--root',str(root),'--candidate',str(p)],capture_output=True,text=True)
 results.append({'case':p.stem,'expected_exit':expect,'actual_exit':cp.returncode,'pass':cp.returncode==expect})
report={'status':'PASS' if all(x['pass'] for x in results) else 'FAIL','passed':sum(x['pass'] for x in results),'total':len(results),'results':results}
(root/'reports/REPRESENTATION_GOVERNANCE_ACCEPTANCE_TESTS.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2)); raise SystemExit(0 if report['status']=='PASS' else 1)
