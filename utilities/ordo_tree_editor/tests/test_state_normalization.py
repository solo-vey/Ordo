#!/usr/bin/env python3
import copy, importlib.util, json
from pathlib import Path

SERVICE = Path(__file__).resolve().parents[1] / 'editor_service.py'
spec = importlib.util.spec_from_file_location('ordo_editor_service_state_norm_test', SERVICE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

mixed = {
    'risk_factor_identity': {'alias': 'COMPANY_TERMINATED'},
    'risk_factor_identity.alias': 'STALE_ALIAS',
    'source_data_definition.rows': [{'source_number': 1}],
    'source_attribute_mapping.rows': [{'field_path': 'statusCode'}],
    'output_payload_mapping.rows': [{'target_field': 'riskFound'}],
    'update_policy.rows': [{'mode': 'daily'}],
    'history_policy.bullets': ['keep history'],
    'functional_test_catalog.rows': [{'scenario_id': 'F1'}],
}
canon = mod._canonicalize_runtime_state(mixed)
assert canon['risk_factor_identity']['alias'] == 'COMPANY_TERMINATED', canon
for root in ('source_data_definition','source_attribute_mapping','output_payload_mapping','update_policy','history_policy','functional_test_catalog'):
    assert root in canon and isinstance(canon[root], dict), (root, canon)
assert canon['source_data_definition']['rows'][0]['source_number'] == 1
assert not any('.' in str(k) for k in canon.keys()), canon.keys()

updated = mod._apply_state_updates_canonical(canon, {
    'source_data_definition.rows': [{'source_number': 2}],
    'risk_factor_identity.alias': 'NEW_ALIAS',
    'risk_factor_identity.type': 'companyProfile',
})
assert updated['source_data_definition']['rows'][0]['source_number'] == 2
assert updated['risk_factor_identity']['alias'] == 'NEW_ALIAS'
assert updated['risk_factor_identity']['type'] == 'companyProfile'

required = ['risk_factor_identity','source_data_definition','source_attribute_mapping','output_payload_mapping','update_policy','history_policy','functional_test_catalog']
proj = mod._project_state_by_paths(updated, required)
for root in required:
    assert root in proj, (root, proj)

print('STATE NORMALIZATION REGRESSION: PASS')
print(json.dumps({'roots': sorted(proj.keys())}, ensure_ascii=False))
