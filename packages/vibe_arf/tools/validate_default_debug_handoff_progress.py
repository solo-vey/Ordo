#!/usr/bin/env python3
from pathlib import Path
import json,yaml,sys
R=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve(); errs=[]
def need(v,msg):
    if not v: errs.append(msg)
p=R/'source/default-debug-handoff-progress-policy.json'; need(p.exists(),'POLICY_MISSING')
if p.exists():
    d=json.loads(p.read_text()); need(d.get('default_mode')=='debug_handoff_visible','DEFAULT_MODE'); need(d.get('handoff_evidence',{}).get('start_at_bootstrap') is True,'BOOTSTRAP'); need(d.get('progress_visibility',{}).get('default_chat_visibility')=='visible','VISIBILITY')
sp=(R/'START_PROMPT_RUNTIME_MODE.md').read_text(); need('default debug/handoff' in sp.lower(),'START_PROMPT_BINDING')
entry=(R/'source/modules/10_entry_contract_state.ordo.module.yaml').read_text(); need('debug_handoff_bundle' in entry and 'progress_event_history' in entry,'STATE_FIELDS')
for f in ['tools/init_debug_handoff_bundle.py','tools/append_progress_event.py','tools/build_debug_handoff_package.py']: need((R/f).exists(),'TOOL:'+f)
print('PASS' if not errs else 'FAIL', 'default_debug_handoff_progress', ';'.join(errs))
sys.exit(0 if not errs else 1)
