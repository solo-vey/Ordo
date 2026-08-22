#!/usr/bin/env python3
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1]; C=json.loads((R/'DISTRIBUTION_PACKAGE_CONTRACT.json').read_text()); P=json.loads((R/'source/generated-playbook-production-package-policy.json').read_text())
checks={
'profiles':set(C.get('profiles',{}))=={'EDIT','CLI_RUN','MODEL_RUN'},
'release_all_three':C.get('release_rule')=='all_three_profiles_required',
'candidate_subset':C.get('candidate_rule')=='requested_subset_or_all',
'sibling_projection':'sibling' in C.get('principle','').lower(),
'identity':C.get('source_identity_files')==['ordo.yml','ordo.lock.json','source/program.ordo.yaml'],
'model_forbids_cli':'cli_embedded/' in C['profiles']['MODEL_RUN']['forbidden_prefixes'],
'model_forbids_authoring':'authoring/' in C['profiles']['MODEL_RUN']['forbidden_prefixes'],
'model_start':C['profiles']['MODEL_RUN']['start_files']==['START_HERE_MODEL_MODE.md','START_PROMPT_MODEL_MODE.md'],
'cli_start':C['profiles']['CLI_RUN']['start_files']==['START_HERE_CLI_RUN.md','START_PROMPT_CLI_RUN.md'],
'policy_profiles':set(P.get('package_profiles',{}))>={'edit','cli_run','model_run'},
'policy_rule':P.get('distribution_rule')=='one_version_three_sibling_profiles',
'builder':(R/'tools/build_three_profile_playbook_distribution.py').is_file(),
'validator':(R/'tools/validate_distribution_package.py').is_file(),
'edit_start':(R/'START_HERE.md').is_file(),
'cli_start_file':(R/'START_HERE_CLI_RUN.md').is_file(),
'model_start_file':(R/'START_HERE_MODEL_MODE.md').is_file(),
'legacy_aliases':C.get('compatibility_aliases')=={'dev':'edit','debug':'edit','run':'cli_run','pair':'release'},
}
failed=[k for k,v in checks.items() if not v]; print(json.dumps({'status':'PASS' if not failed else 'FAIL','passed':sum(checks.values()),'total':len(checks),'failed':failed},indent=2)); raise SystemExit(0 if not failed else 1)
