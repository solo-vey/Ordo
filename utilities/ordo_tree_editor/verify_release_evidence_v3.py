#!/usr/bin/env python3
import argparse, json
from pathlib import Path


def check(cond, code, detail, out):
    out.append({'id':code,'status':'PASS' if cond else 'FAIL','detail':detail})
    return bool(cond)


def weighted_attempts(hist):
    total=0
    for k,v in (hist or {}).items():
        try: total += int(k)*int(v)
        except Exception: pass
    return total


def verify(summary, state=None, expected_terminal=None, require_probe=True):
    checks=[]
    prov=summary.get('provenance') or {}
    run=summary.get('run') or {}
    retry=summary.get('retry_quality') or {}
    accounting=summary.get('accounting') or {}
    usage=summary.get('usage') or {}
    sc=run.get('step_class_counts') or {}
    terminal=expected_terminal or ((run.get('outcome') or {}).get('nodeId'))
    check(summary.get('evidence_profile')=='live','EVIDENCE_PROFILE_LIVE',summary.get('evidence_profile'),checks)
    check(int(prov.get('replayed_calls') or 0)==0,'ZERO_REPLAYED_CALLS',prov.get('replayed_calls'),checks)
    check(run.get('status')=='completed','RUN_COMPLETED',run.get('status'),checks)
    check((run.get('outcome') or {}).get('reason')=='terminal','TERMINAL_REASON',(run.get('outcome') or {}).get('reason'),checks)
    if expected_terminal:
        check((run.get('outcome') or {}).get('nodeId')==expected_terminal,'EXPECTED_TERMINAL',(run.get('outcome') or {}).get('nodeId'),checks)
    check(retry.get('acceptance_pass') is True,'RETRY_ACCEPTANCE',retry.get('acceptance_pass'),checks)
    check(int(retry.get('exhausted_retry_budget') or 0)==0,'RETRY_BUDGET_NOT_EXHAUSTED',retry.get('exhausted_retry_budget'),checks)
    # canonical logical-step agreement
    logical_live=int(sc.get('live_model_call') or 0)
    check(logical_live==int(prov.get('live_calls') or 0)==int(run.get('llm_calls') or 0),'LOGICAL_CALL_ACCOUNTING',{'step_class':logical_live,'provenance':prov.get('live_calls'),'run_llm_calls':run.get('llm_calls')},checks)
    expected_attempts=weighted_attempts(retry.get('retry_histogram'))
    if accounting:
        check(int(accounting.get('provider_attempts') or 0)==expected_attempts,'PROVIDER_ATTEMPT_ACCOUNTING',{'accounting':accounting.get('provider_attempts'),'retry_histogram_weighted':expected_attempts},checks)
        check(int(usage.get('calls') or 0)==int(accounting.get('token_baseline_attempts') or 0),'TOKEN_BASELINE_CALL_ACCOUNTING',{'usage.calls':usage.get('calls'),'token_baseline_attempts':accounting.get('token_baseline_attempts')},checks)
    else:
        check(False,'CANONICAL_ACCOUNTING_PRESENT','missing accounting object',checks)
    if require_probe:
        probe=summary.get('provider_capability_profile') or summary.get('capability_profile') or {}
        check(probe.get('status')=='recorded' and isinstance(probe.get('supports_json_schema'),bool),'PROVIDER_CAPABILITY_PROBE',probe or 'missing',checks)
    freshness=((run.get('run_journal') or {}).get('artifact_freshness') or [])
    # R3 artifact lifecycle: older materializations of the same logical path are
    # historical/superseded evidence. Release acceptance evaluates only the
    # latest active materialization per artifact path. Otherwise a correct
    # rematerialization could never clear an earlier stale draft.
    latest_by_path={}
    superseded=[]
    for idx,item in enumerate(freshness):
        path=str(item.get('path') or '')
        rev=int(item.get('materialized_from_revision') or 0)
        current=latest_by_path.get(path)
        if current is None or (rev,idx) >= (current[0],current[1]):
            if current is not None:
                superseded.append(current[2])
            latest_by_path[path]=(rev,idx,item)
        else:
            superseded.append(item)
    active=[triple[2] for triple in latest_by_path.values()]
    stale=[x for x in active if x.get('freshness_status')=='stale']
    unknown=[x for x in active if x.get('freshness_status')=='unknown_dependencies']
    check(not stale,'NO_STALE_ARTIFACTS',stale,checks)
    check(not unknown,'ARTIFACT_DEPENDENCIES_KNOWN',unknown,checks)
    check(True,'SUPERSEDED_ARTIFACT_HISTORY',{'superseded_count':len(superseded),'active_count':len(active)},checks)
    if state is not None:
        check(state.get('missing_test_coverage') in ([],None),'NO_MISSING_TEST_COVERAGE',state.get('missing_test_coverage'),checks)
    return {'status':'PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL','checks':checks,'expected_terminal':terminal}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('summary')
    ap.add_argument('--state')
    ap.add_argument('--expected-terminal')
    ap.add_argument('--allow-unprobed-provider',action='store_true')
    args=ap.parse_args()
    summary=json.loads(Path(args.summary).read_text(encoding='utf-8'))
    state=json.loads(Path(args.state).read_text(encoding='utf-8')) if args.state else None
    out=verify(summary,state,args.expected_terminal,not args.allow_unprobed_provider)
    print(json.dumps(out,ensure_ascii=False,indent=2))
    raise SystemExit(0 if out['status']=='PASS' else 1)

if __name__=='__main__': main()
