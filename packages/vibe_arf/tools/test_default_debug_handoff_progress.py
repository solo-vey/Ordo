from pathlib import Path
import json,yaml,sys
R=Path(__file__).resolve().parents[1]
checks={}
def ck(k,v): checks[k]=bool(v)
sp=(R/'START_PROMPT_RUNTIME_MODE.md').read_text()
sh=(R/'START_HERE_RUNTIME_MODE.md').read_text()
laws=(R/'PLAYBOOK_LAWS.md').read_text()
policy=R/'source/default-debug-handoff-progress-policy.json'
ck('policy_exists',policy.exists())
p={}
if policy.exists():
    p=json.loads(policy.read_text())
ck('default_on',p.get('default_mode')=='debug_handoff_visible')
ck('handoff_from_start',p.get('handoff_evidence',{}).get('start_at_bootstrap') is True)
ck('progress_default_visible',p.get('progress_visibility',{}).get('default_chat_visibility')=='visible')
req=set(p.get('progress_visibility',{}).get('event_types',[]))
ck('progress_events_cover_runtime',{'stage_start','node_enter','gate_result','repair_or_route','checkpoint'}<=req)
ck('handoff_has_intermediate_versions',p.get('handoff_evidence',{}).get('capture_intermediate_revisions') is True)
ck('handoff_has_problems_and_gates',p.get('handoff_evidence',{}).get('capture_gate_history') is True and p.get('handoff_evidence',{}).get('capture_problem_history') is True)
ck('prompt_bootstraps_handoff','default debug/handoff' in sp.lower() and 'handoff' in sp.lower())
ck('start_here_progress','progress event' in sh.lower() and 'handoff evidence' in sh.lower())
ck('law_present','DEFAULT_DEBUG_HANDOFF_PROGRESS' in laws)
# canonical information model must own the contract
objs=yaml.safe_load((R/'authoring/information_object_catalog.yaml').read_text())['objects']
ids={x['id'] for x in objs}
ck('aim_object','I_DEFAULT_DEBUG_HANDOFF_PROGRESS_CONTRACT' in ids)
groups=yaml.safe_load((R/'authoring/information_group_catalog.yaml').read_text())['groups']
ck('aim_group_member',any('I_DEFAULT_DEBUG_HANDOFF_PROGRESS_CONTRACT' in g.get('members',[]) for g in groups))
proj=yaml.safe_load((R/'authoring/ordo_projection.yaml').read_text())
b=next((x for x in proj.get('information_bindings',[]) if x.get('information_id')=='I_DEFAULT_DEBUG_HANDOFF_PROGRESS_CONTRACT'),None)
ck('projection_binding',bool(b and b.get('node_ids')))
# state must persist bundle/progress history
entry=(R/'source/modules/10_entry_contract_state.ordo.module.yaml').read_text()
ck('state_fields','debug_handoff_bundle' in entry and 'progress_event_history' in entry)
# deterministic helpers / validators
ck('init_tool',(R/'tools/init_debug_handoff_bundle.py').exists())
ck('progress_tool',(R/'tools/append_progress_event.py').exists())
ck('build_tool',(R/'tools/build_debug_handoff_package.py').exists())
ck('validator',(R/'tools/validate_default_debug_handoff_progress.py').exists())

# verification registration / dependency-aware FAST selection
vp=json.loads((R/'verification_profile.json').read_text())
ck('verification_profile_registered',any(c.get('id')=='default_debug_handoff_progress' and c.get('required') is True for c in vp.get('checks',[])))
im=json.loads((R/'verification_impact_map.json').read_text())
ck('fast_impact_rule',any('default_debug_handoff_progress' in r.get('checks',[]) for r in im.get('path_rules',[])))

passed=sum(checks.values()); total=len(checks)
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
print(f'SUMMARY {passed}/{total}')
sys.exit(0 if passed==total else 1)
