#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, subprocess, sys, tempfile, time
R=Path(__file__).resolve().parents[1]
checks=[]
def ck(name, value): checks.append((name,bool(value)))

# 1) deterministic/package tool result contract
contract=R/'source/deterministic-tool-result-contract.json'
ck('STATE_UPDATES_POLICY_EXISTS', contract.is_file())
if contract.is_file():
    d=json.loads(contract.read_text())
    ck('STATE_UPDATES_V1_ID', d.get('result_contract_id')=='state_updates_v1')
    ck('EXECUTOR_MERGES_ONLY_STATE_UPDATES', d.get('executor',{}).get('merge_source')=='state_updates')
    ck('REPORT_NEVER_IMPLICIT_STATE', d.get('executor',{}).get('report_is_state') is False)
helper=R/'tools/state_updates_v1.py'
ck('STATE_UPDATES_HELPER_EXISTS', helper.is_file())
if helper.is_file():
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); state=td/'state.json'; result=td/'result.json'; out=td/'out.json'
        state.write_text(json.dumps({'keep':1,'nested':{'a':1}}))
        result.write_text(json.dumps({'contract':'state_updates_v1','status':'PASS','report':{'keep':999,'diagnostic':'x'},'state_updates':{'nested':{'b':2},'new':3}}))
        p=subprocess.run([sys.executable,str(helper),'merge','--state',str(state),'--result',str(result),'--output',str(out)],capture_output=True,text=True)
        merged=json.loads(out.read_text()) if out.exists() else {}
        ck('STATE_UPDATES_MERGE_PASS', p.returncode==0)
        ck('REPORT_NOT_MERGED', merged.get('keep')==1 and 'diagnostic' not in merged)
        ck('DIFF_MERGED', merged.get('nested')=={'a':1,'b':2} and merged.get('new')==3)

# 2) visible debug timing baseline
progress=R/'tools/append_progress_event.py'
policy=R/'source/visible-debug-timing-policy.json'
ck('VISIBLE_TIMING_POLICY_EXISTS', policy.is_file())
if policy.is_file():
    d=json.loads(policy.read_text())
    ck('HIDDEN_DOES_NOT_ADVANCE_BASELINE', d.get('hidden_events_advance_visible_baseline') is False)
with tempfile.TemporaryDirectory() as td:
    td=Path(td); w=td/'debug_handoff'/'working'; w.mkdir(parents=True); (w/'session_manifest.json').write_text('{}')
    def ev(vis):
        return subprocess.run([sys.executable,str(progress),str(td),'--event-type','node_enter','--current-element','N1','--summary','x','--next-action','y','--visibility',vis],capture_output=True,text=True)
    p1=ev('visible'); baseline=w/'visible_timing_state.json'; b1=json.loads(baseline.read_text()) if baseline.exists() else {}
    time.sleep(0.03); ph=ev('hidden'); b2=json.loads(baseline.read_text()) if baseline.exists() else {}
    time.sleep(0.03); p2=ev('visible'); b3=json.loads(baseline.read_text()) if baseline.exists() else {}
    e1=json.loads(p1.stdout) if p1.stdout.strip() else {}; eh=json.loads(ph.stdout) if ph.stdout.strip() else {}; e2=json.loads(p2.stdout) if p2.stdout.strip() else {}
    ck('FIRST_VISIBLE_NO_DELTA', e1.get('elapsed_since_previous_visible_seconds') is None)
    ck('HIDDEN_BASELINE_UNCHANGED', b1.get('last_visible_timestamp')==b2.get('last_visible_timestamp'))
    ck('HIDDEN_MARKED_NONADVANCING', eh.get('visible_baseline_advanced') is False)
    ck('SECOND_VISIBLE_ADVANCES', b3.get('last_visible_timestamp')!=b2.get('last_visible_timestamp'))
    ck('VISIBLE_DELTA_SPANS_HIDDEN', isinstance(e2.get('elapsed_since_previous_visible_seconds'),(int,float)) and e2['elapsed_since_previous_visible_seconds']>=0.04)

# 3) append-only self-repair log
sp=R/'source/self-repair-log-policy.json'; tool=R/'tools/append_self_repair_event.py'
ck('SELF_REPAIR_POLICY_EXISTS', sp.is_file()); ck('SELF_REPAIR_TOOL_EXISTS', tool.is_file())
if sp.is_file():
    d=json.loads(sp.read_text()); ck('SELF_REPAIR_APPEND_ONLY', d.get('append_only') is True); ck('SELF_REPAIR_NOT_BUSINESS_STATE', d.get('business_state_surface') is False)
if tool.is_file():
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        base=[sys.executable,str(tool),str(td),'--repair-id','R1','--problem','validator failed','--root-cause','missing generic contract','--files-changed','a.py,b.json','--repair','add generic contract','--validation','regression PASS','--continuation-point','N_NEXT']
        p=subprocess.run(base,capture_output=True,text=True)
        log=td/'runtime'/'evidence'/'SELF_REPAIR_LOG.jsonl'
        rows=[json.loads(x) for x in log.read_text().splitlines()] if log.exists() else []
        ck('SELF_REPAIR_APPEND_PASS', p.returncode==0 and len(rows)==1)
        ck('SELF_REPAIR_REQUIRED_FIELDS', bool(rows and all(k in rows[0] for k in ['problem','root_cause','files_changed','repair','validation','continuation_point','entry_sha256'])))
        p=subprocess.run([sys.executable,str(tool),str(td),'--repair-id','R2','--problem','second','--root-cause','second cause','--files-changed','c.py','--repair','second repair','--validation','PASS','--continuation-point','N_DONE'],capture_output=True,text=True)
        rows=[json.loads(x) for x in log.read_text().splitlines()] if log.exists() else []
        ck('SELF_REPAIR_CHAINED_APPEND', len(rows)==2 and rows[1].get('previous_entry_sha256')==rows[0].get('entry_sha256'))

laws=(R/'PLAYBOOK_LAWS.md').read_text() if (R/'PLAYBOOK_LAWS.md').exists() else ''
for lid in ['E82_DETERMINISTIC_TOOL_STATE_UPDATES_V1','E83_VISIBLE_DEBUG_TIMING_BASELINE','E84_APPEND_ONLY_SELF_REPAIR_LOG']:
    ck(lid, lid in laws)

failed=[n for n,v in checks if not v]
for n,v in checks: print(('PASS' if v else 'FAIL'),n)
print(f'ALPHA44_TOOL_RESULT_DEBUG_SELF_REPAIR: {len(checks)-len(failed)}/{len(checks)} PASS')
raise SystemExit(1 if failed else 0)
