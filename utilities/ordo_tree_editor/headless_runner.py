#!/usr/bin/env python3
"""Headless Ordo runtime runner for CI/preflight and recorded-result regression.

Modes:
  preflight        Parse a playbook ZIP and validate that source + semantic plan are available.
  replay-evidence  Re-execute every recorded runtime step from a debug summary using the
                   recorded structured model result, then compare state/route/runtime outputs.

Replay is regression evidence only; it is never classified as live acceptance.
"""
from __future__ import annotations
import argparse, copy, json, re, sys
from pathlib import Path
from typing import Any

import editor_service as es


def _load_json(path: str | Path) -> dict[str, Any]:
    obj=json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(obj,dict):
        raise ValueError(f'{path}: root must be object')
    return obj


def _load_package(path: str | Path) -> dict[str, Any]:
    p=Path(path)
    public_view=es.parse_playbook_package(p.name,p.read_bytes())
    package_id=str(public_view.get('id') or '')
    if not package_id:
        raise ValueError('package parser did not produce package id')
    package=copy.deepcopy(es.PLAYBOOK_PACKAGES.get(package_id) or es.PLAYBOOK_PACKAGE)
    if not isinstance(package.get('source'),dict):
        raise ValueError('package registry did not retain parsed source')
    return package


def preflight(package_path: str) -> dict[str, Any]:
    package=_load_package(package_path)
    source=package.get('source')
    semantic=package.get('semantic_plan')
    checks={
        'package_id_present': bool(package.get('id')),
        'source_present': isinstance(source,dict),
        'semantic_plan_present': isinstance(semantic,dict),
        'semantic_plan_status_pass': bool((package.get('semantic_plan_status') or {}).get('valid')),
    }
    # Older valid fixture packages may not have a status wrapper. Presence remains mandatory.
    if checks['semantic_plan_present'] and not package.get('semantic_plan_status'):
        checks['semantic_plan_status_pass']=True
    status='PASS' if all(checks.values()) else 'FAIL'
    return {'status':status,'mode':'preflight','package':{'id':package.get('id'),'filename':package.get('filename'),'source_name':package.get('source_name')},'checks':checks}


_ISO_RUNTIME_CLOCK_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})$")

def _is_runtime_clock_field(key: str, value: Any) -> bool:
    """Identify replay-only clock noise without hiding ordinary business values.

    Runtime-generated timestamps are non-deterministic replay evidence.  We only
    drop fields whose names explicitly look timestamp-like *and* whose values
    have an ISO-8601 runtime-clock shape.  Business state under other names is
    retained and therefore still participates in replay equality.
    """
    name=str(key or "").lower()
    if not (name == "runtime_timestamp" or name.endswith("_timestamp") or name.endswith("_at")):
        return False
    return isinstance(value,str) and bool(_ISO_RUNTIME_CLOCK_RE.match(value.strip()))

def _strip_replay_clock_noise(value: Any) -> Any:
    if isinstance(value,dict):
        return {
            k:_strip_replay_clock_noise(v)
            for k,v in value.items()
            if not _is_runtime_clock_field(str(k),v)
        }
    if isinstance(value,list):
        return [_strip_replay_clock_noise(v) for v in value]
    return value

def _norm(x: Any) -> Any:
    canonical=es.canonicalize_runtime_state(x) if isinstance(x,dict) else x
    return _strip_replay_clock_noise(canonical)

def _actual_route_key(actual: dict[str,Any]) -> Any:
    # Public live result contract uses route_key.  Keep debug fallbacks for
    # historical evidence/contracts, but never rely on stale selected_route_key
    # at the top level.
    if actual.get("route_key") is not None:
        return actual.get("route_key")
    debug=actual.get("debug") if isinstance(actual.get("debug"),dict) else {}
    runtime=debug.get("runtime") if isinstance(debug.get("runtime"),dict) else {}
    if runtime.get("selected_route_key") is not None:
        return runtime.get("selected_route_key")
    normalized=runtime.get("normalized_execution_result") if isinstance(runtime.get("normalized_execution_result"),dict) else {}
    return normalized.get("route_key")


def replay_evidence(package_path: str, summary_path: str, max_steps: int | None=None) -> dict[str, Any]:
    package=_load_package(package_path)
    summary=_load_json(summary_path)
    calls=summary.get('calls') if isinstance(summary.get('calls'),list) else []
    source=package.get('source')
    if not isinstance(source,dict):
        raise ValueError('playbook source missing')
    # Dummy custom-provider config; recorded_model_result guarantees no provider call.
    sid='headless-replay'; rid='headless-replay-run'
    es.LIVE_RUNTIME.update({'provider':'custom','model':'recorded','base_url':'http://127.0.0.1:1/v1','structured_output_mode':'json_object'})
    es.LIVE_SESSIONS[sid]={'provider':'custom','model':'recorded','base_url':'http://127.0.0.1:1/v1','structured_output_mode':'json_object'}
    results=[]; failures=[]
    for c in calls[:max_steps] if max_steps else calls:
        runtime=c.get('runtime') if isinstance(c.get('runtime'),dict) else {}
        if not runtime or not c.get('current_id'):
            continue
        state_before=copy.deepcopy(runtime.get('state_before') if isinstance(runtime.get('state_before'),dict) else {})
        phase=str(c.get('phase') or 'enter')
        parsed=((c.get('output') or {}).get('parsed_result')) if isinstance(c.get('output'),dict) else None
        context=((c.get('input') or {}).get('context')) if isinstance(c.get('input'),dict) else {}
        analyst_input=str((context or {}).get('analyst_input') or '') if isinstance(context,dict) else ''
        if not analyst_input and c.get('step_class')=='human_or_auto_answer' and phase=='respond':
            normalized=(context or {}).get('normalized_execution_result') if isinstance(context,dict) else None
            decision=(normalized or {}).get('decision') if isinstance(normalized,dict) else None
            if isinstance(decision,dict):
                analyst_input=str(decision.get('raw_answer') or '')
        payload={
            'package_id':package['id'],'session_id':sid,'run_id':rid,'source':source,
            'current_id':str(c.get('current_id')),'phase':phase,'state':state_before,
            'state_revision':int(runtime.get('revision_before') or 0),'history':[],
            'analyst_input':analyst_input,
        }
        # Only model-executed steps need recorded result. Runtime/deterministic steps ignore it.
        if isinstance(parsed,dict) and c.get('step_class') in {'live_model_call','replayed_model_call'}:
            payload['recorded_model_result']=copy.deepcopy(parsed)
            payload['recorded_model_provenance']={'source':'headless_evidence_replay','original_index':c.get('index')}
        try:
            actual=es._call_openai_live(payload)
            expected_state=_norm(runtime.get('state_after') or state_before)
            actual_state=_norm(actual.get('state') or state_before)
            actual_route_key=_actual_route_key(actual)
            checks={
                'state_after': actual_state==expected_state,
                'next_id': actual.get('next_id')==runtime.get('next_id'),
                'await_analyst': bool(actual.get('await_analyst'))==bool(runtime.get('await_analyst')),
                'run_status': str(actual.get('run_status') or 'running')==str(runtime.get('run_status') or 'running'),
                'selected_route_key': actual_route_key==runtime.get('selected_route_key'),
            }
            ok=all(checks.values())
            rec={'index':c.get('index'),'node':c.get('current_id'),'phase':phase,'step_class':c.get('step_class'),'status':'PASS' if ok else 'FAIL','checks':checks}
            if not ok:
                rec['expected']={'next_id':runtime.get('next_id'),'await_analyst':runtime.get('await_analyst'),'run_status':runtime.get('run_status'),'selected_route_key':runtime.get('selected_route_key')}
                rec['actual']={'next_id':actual.get('next_id'),'await_analyst':actual.get('await_analyst'),'run_status':actual.get('run_status'),'selected_route_key':actual_route_key}
                failures.append(rec)
            results.append(rec)
        except Exception as exc:
            rec={'index':c.get('index'),'node':c.get('current_id'),'phase':phase,'step_class':c.get('step_class'),'status':'ERROR','error':str(exc)}
            results.append(rec); failures.append(rec)
    return {
        'status':'PASS' if not failures else 'FAIL','mode':'replay-evidence','acceptance_eligible':False,
        'package_id':package.get('id'),'source_evidence':str(summary_path),'steps_checked':len(results),
        'steps_failed':len(failures),'results':results,
    }



def run_deterministic(package_path: str, answers_path: str | None=None, max_steps: int=200) -> dict[str, Any]:
    package=_load_package(package_path)
    source=package.get('source') or {}
    answers_obj=_load_json(answers_path) if answers_path else {}
    raw_answers=answers_obj.get('answers') if isinstance(answers_obj.get('answers'),dict) else answers_obj
    queues={}
    for node,val in (raw_answers or {}).items():
        if isinstance(val,list): queues[str(node)]=[str(x) for x in val]
        else: queues[str(node)]=[str(val)]
    sid='headless-deterministic'; rid='headless-deterministic-run'
    es.LIVE_RUNTIME.update({'provider':'custom','model':'headless-no-model','base_url':'http://127.0.0.1:1/v1','structured_output_mode':'json_object'})
    es.LIVE_SESSIONS[sid]={'provider':'custom','model':'headless-no-model','base_url':'http://127.0.0.1:1/v1','structured_output_mode':'json_object'}
    state={}; revision=0; current=str(package.get('entry_node') or es._entry_id(source) or '')
    external=set(str(x) for x in ((source.get('graph_contract') or {}).get('external_terminal_targets') or []) if isinstance(x,str))
    trace=[]
    for seq in range(1,max_steps+1):
        if current in external:
            return {'status':'PASS','mode':'run-deterministic','acceptance_eligible':False,'outcome':{'status':'completed','reason':'external_terminal','nodeId':current},'steps':len(trace),'final_state':state,'trace':trace}
        if not current:
            return {'status':'FAIL','mode':'run-deterministic','acceptance_eligible':False,'error':'current node is empty','steps':len(trace),'final_state':state,'trace':trace}
        payload={'package_id':package['id'],'session_id':sid,'run_id':rid,'source':source,'current_id':current,'phase':'enter','state':state,'state_revision':revision,'history':[]}
        try:
            entered=es._call_openai_live(payload)
        except Exception as exc:
            return {'status':'FAIL','mode':'run-deterministic','acceptance_eligible':False,'error':str(exc),'current_id':current,'steps':len(trace),'final_state':state,'trace':trace}
        before=copy.deepcopy(state); state=copy.deepcopy(entered.get('state') or state); revision += 1 if state!=before else 0
        trace.append({'seq':seq,'node':current,'phase':'enter','await_analyst':bool(entered.get('await_analyst')),'next_id':entered.get('next_id'),'state_revision':revision})
        result=entered
        if entered.get('await_analyst'):
            q=queues.get(current) or []
            if not q:
                return {'status':'FAIL','mode':'run-deterministic','acceptance_eligible':False,'error':f'missing analyst answer for {current}','current_id':current,'steps':len(trace),'final_state':state,'trace':trace}
            answer=q.pop(0); queues[current]=q
            payload.update({'phase':'respond','state':state,'state_revision':revision,'analyst_input':answer})
            try:
                result=es._call_openai_live(payload)
            except Exception as exc:
                return {'status':'FAIL','mode':'run-deterministic','acceptance_eligible':False,'error':str(exc),'current_id':current,'steps':len(trace),'final_state':state,'trace':trace}
            before=copy.deepcopy(state); state=copy.deepcopy(result.get('state') or state); revision += 1 if state!=before else 0
            trace.append({'seq':seq,'node':current,'phase':'respond','answer':answer,'await_analyst':bool(result.get('await_analyst')),'next_id':result.get('next_id'),'state_revision':revision})
            if result.get('await_analyst'):
                return {'status':'FAIL','mode':'run-deterministic','acceptance_eligible':False,'error':f'node {current} still awaits analyst after supplied answer','current_id':current,'steps':len(trace),'final_state':state,'trace':trace}
        if result.get('terminal') or str(result.get('run_status') or '')=='completed':
            return {'status':'PASS','mode':'run-deterministic','acceptance_eligible':False,'outcome':{'status':'completed','reason':result.get('completion_reason') or 'terminal','nodeId':current},'steps':len(trace),'final_state':state,'trace':trace}
        nxt=result.get('next_id')
        if not nxt:
            return {'status':'FAIL','mode':'run-deterministic','acceptance_eligible':False,'error':f'no next_id from {current}','current_id':current,'steps':len(trace),'final_state':state,'trace':trace}
        current=str(nxt)
    return {'status':'FAIL','mode':'run-deterministic','acceptance_eligible':False,'error':'max_steps_exceeded','current_id':current,'steps':len(trace),'final_state':state,'trace':trace}

def main(argv=None)->int:
    ap=argparse.ArgumentParser(description='Ordo R3 headless runtime runner')
    sp=ap.add_subparsers(dest='cmd',required=True)
    p=sp.add_parser('preflight'); p.add_argument('--playbook',required=True); p.add_argument('--output')
    r=sp.add_parser('replay-evidence'); r.add_argument('--playbook',required=True); r.add_argument('--summary',required=True); r.add_argument('--max-steps',type=int); r.add_argument('--output')
    d=sp.add_parser('run-deterministic'); d.add_argument('--playbook',required=True); d.add_argument('--answers'); d.add_argument('--max-steps',type=int,default=200); d.add_argument('--output')
    a=ap.parse_args(argv)
    try:
        if a.cmd=='preflight': out=preflight(a.playbook)
        elif a.cmd=='replay-evidence': out=replay_evidence(a.playbook,a.summary,a.max_steps)
        else: out=run_deterministic(a.playbook,a.answers,a.max_steps)
    except Exception as exc:
        out={'status':'ERROR','mode':a.cmd,'error':str(exc)}
    text=json.dumps(out,ensure_ascii=False,indent=2)
    if a.output: Path(a.output).write_text(text+'\n',encoding='utf-8')
    else: print(text)
    return 0 if out.get('status')=='PASS' else 1

if __name__=='__main__': raise SystemExit(main())
