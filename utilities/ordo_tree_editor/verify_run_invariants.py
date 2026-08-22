#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any

from release1_runtime import scan_collection_shapes


def load(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding='utf-8'))


def value_schemas(plan: dict[str, Any]) -> dict[str, Any]:
    out={}
    for e in (plan.get('elements') or {}).values():
        if not isinstance(e,dict): continue
        vs=(((e.get('output_contract') or {}).get('state_patch') or {}).get('value_schema_by_path') or {})
        if isinstance(vs,dict): out.update(vs)
    return out


def calls_from_debug(debug: Any) -> list[dict[str, Any]]:
    if isinstance(debug,dict) and isinstance(debug.get('calls'),list): return [x for x in debug['calls'] if isinstance(x,dict)]
    return []


def verify(plan: dict[str,Any], debug: dict[str,Any], state: dict[str,Any]) -> dict[str,Any]:
    findings=[]
    collection=scan_collection_shapes(state,value_schemas(plan))
    findings.extend(collection['findings'])
    for call in calls_from_debug(debug):
        eid=str(call.get('current_id') or '')
        elem=(plan.get('elements') or {}).get(eid) if isinstance(plan.get('elements'),dict) else None
        if not isinstance(elem,dict) or not str(elem.get('kind') or '').endswith('_gate'): continue
        runtime=call.get('runtime') if isinstance(call.get('runtime'),dict) else {}
        output=call.get('output') if isinstance(call.get('output'),dict) else {}
        parsed=output.get('parsed_result') if isinstance(output.get('parsed_result'),dict) else {}
        accounting=parsed.get('gate_accounting') if isinstance(parsed.get('gate_accounting'),dict) else runtime.get('gate_accounting') if isinstance(runtime.get('gate_accounting'),dict) else None
        context=(call.get('input') or {}).get('context') if isinstance(call.get('input'),dict) else {}
        if isinstance(context,dict):
            cs=context.get('runtime_state',{}).get('__context_status__') if isinstance(context.get('runtime_state'),dict) else None
            if 'missing_preload' in context or (isinstance(cs,dict) and 'missing_preload' in cs):
                findings.append({'code':'UNTYPED_CONTEXT_MISSING','element_id':eid})
        declared=((elem.get('output_contract') or {}).get('declared_check_ids') or [])
        if declared:
            if not isinstance(accounting,dict):
                # Legacy traces prove the old defect explicitly.
                findings.append({'code':'GATE_CHECK_ACCOUNTING_MISSING','element_id':eid,'declared':len(declared)})
            else:
                executed=accounting.get('executed_check_ids') or []
                status=accounting.get('execution_status')
                if status!='evaluated' or set(executed)!=set(declared):
                    findings.append({'code':'GATE_CHECK_ACCOUNTING_INCOMPLETE','element_id':eid,'declared':declared,'executed':executed,'execution_status':status})
        if runtime.get('reason')=='context_incomplete' or runtime.get('completion_reason') in {'context_incomplete','contract_unsatisfiable_by_model','no_progress_recovery_loop','coverage_recovery_regression','coverage_recovery_round_limit'}:
            findings.append({'code':'TECHNICAL_STOP','element_id':eid,'reason':runtime.get('completion_reason') or runtime.get('reason')})
        progress=runtime.get('coverage_recovery_progress') if isinstance(runtime.get('coverage_recovery_progress'),dict) else None
        if isinstance(progress,dict) and progress.get('classification') in {'stall','regression','max_rounds_exceeded'}:
            findings.append({'code':'COVERAGE_RECOVERY_NOT_CONVERGED','element_id':eid,'classification':progress.get('classification'),'previous_missing':progress.get('previous_missing'),'current_missing':progress.get('current_missing')})
    return {'profile':'release1','status':'FAIL' if findings else 'PASS','finding_count':len(findings),'findings':findings,'collection_scan':collection}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--plan',required=True); ap.add_argument('--debug',required=True); ap.add_argument('--state',required=True); ap.add_argument('--out',required=True)
    a=ap.parse_args(); report=verify(load(a.plan),load(a.debug),load(a.state)); Path(a.out).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps({'status':report['status'],'findings':report['finding_count'],'out':a.out},ensure_ascii=False))
    raise SystemExit(0 if report['status']=='PASS' else 2)
if __name__=='__main__': main()
