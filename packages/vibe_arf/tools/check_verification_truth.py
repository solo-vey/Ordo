#!/usr/bin/env python3
from pathlib import Path
import json,yaml,sys
R=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('.').resolve()
findings=[]; warnings=[]
def load(rel):
 p=R/rel
 try: return json.loads(p.read_text()) if p.is_file() else None
 except Exception as e: findings.append({'code':'REPORT_INVALID_JSON','path':rel,'error':str(e)}); return None
tr=load('reports/test_report.json')
if tr:
 s=tr.get('summary') or {}
 if str(tr.get('status','')).lower() not in {'passed','pass'} or int(s.get('failed',0) or 0)>0 or int(s.get('errors',0) or 0)>0:
  findings.append({'code':'TEST_REPORT_NOT_GREEN','summary':s,'status':tr.get('status')})
# If a runtime output manifest exists, declared outputs must be generated or explicitly deferred.
manifest=load('generated_outputs/output_manifest.json')
if manifest:
 src=yaml.safe_load((R/'source/program.ordo.yaml').read_text()) or {}
 declared={o.get('id') for o in src.get('outputs',[]) if isinstance(o,dict) and o.get('id')}
 generated={a.get('id') for a in manifest.get('artifacts',[]) if isinstance(a,dict) and a.get('id')}
 deferred={a.get('id') for a in manifest.get('deferred_artifacts',[]) if isinstance(a,dict) and a.get('id') and a.get('reason') and a.get('status')}
 missing=sorted(declared-generated-deferred); extra=sorted((generated|deferred)-declared)
 if missing: findings.append({'code':'DECLARED_OUTPUT_EXECUTION_GAP','missing':missing})
 if extra: findings.append({'code':'UNDECLARED_OUTPUT_IN_MANIFEST','extra':extra})
 # Canonical artifact/consistency PASS can be vacuous. Require explicit non-vacuous alternative evidence when zero.
 vacuous=[]
 for rel in ['reports/artifact_validation_report.json','reports/CONSISTENCY_CHECK_REPORT.json']:
  d=load(rel)
  if d and int((d.get('summary') or {}).get('checked_artifacts',0) or 0)==0:
   vacuous.append(rel)
 if vacuous:
  alt=load('reports/runtime_output_closure.json') or load('reports/APPLIED_ARTIFACT_CONSISTENCY.json')
  if not alt or alt.get('status')!='PASS': findings.append({'code':'VACUOUS_PASS_WITHOUT_ALTERNATIVE_EVIDENCE','reports':vacuous})
  else: warnings.append({'code':'CANONICAL_PASS_VACUOUS_BUT_ALTERNATIVE_EVIDENCE_PRESENT','reports':vacuous})
status='PASS' if not findings else 'FAIL'
print(json.dumps({'status':status,'findings':findings,'warnings':warnings,'blocking_count':len(findings)},ensure_ascii=False,indent=2))
raise SystemExit(0 if status=='PASS' else 1)
