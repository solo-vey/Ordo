#!/usr/bin/env python3
from pathlib import Path
import json,yaml,sys
R=Path(__file__).resolve().parents[1]
source=yaml.safe_load((R/'source/program.ordo.yaml').read_text()) or {}
rules=set(((source.get('conversation_semantics') or {}).get('vibe_rules') or []))
laws={x.get('id') for x in ((source.get('playbook_laws') or {}).get('laws') or []) if isinstance(x,dict)}
reg=json.loads((R/'source/verification-runner-registry.json').read_text())
checks={
 'dry_check_rule': 'DRY_CHECK_NEVER_FABRICATES_LIVE_AUTHORITY_OR_EXTERNAL_EVIDENCE' in rules,
 'output_closure_rule':'DECLARED_OUTPUT_EXECUTION_CLOSURE_REQUIRED' in rules,
 'report_truth_rule':'VERIFICATION_READINESS_USES_REPORT_TRUTH_NOT_EXIT_CODE_ONLY' in rules,
 'vacuous_rule':'VACUOUS_PASS_REQUIRES_NONVACUOUS_ALTERNATIVE_EVIDENCE' in rules,
 'laws_promoted':{'E7_DRY_CHECK_AUTHORITY_SEPARATION','E8_DECLARED_OUTPUT_EXECUTION_CLOSURE'} <= laws,
 'verification_truth_runner':'verification_truth' in reg.get('runners',{}),
 'verification_truth_mandatory':'verification_truth' in (reg.get('mandatory_profile_contract',{}).get('PRE_EDITOR') or []),
 'truth_checker_exists':(R/'tools/check_verification_truth.py').is_file(),
 'materializer_emits_runtime_mode_contract':'RUNTIME_MODE_CONTRACT.json' in (R/'tools/materialize_generated_playbook_verification.py').read_text(),
}
status='PASS' if all(checks.values()) else 'FAIL'; print(json.dumps({'status':status,'checks':checks},ensure_ascii=False,indent=2)); raise SystemExit(0 if status=='PASS' else 1)
