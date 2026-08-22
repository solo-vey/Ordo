#!/usr/bin/env python3
import importlib.util
from pathlib import Path

SERVICE = Path(__file__).resolve().parents[1] / 'editor_service.py'
spec = importlib.util.spec_from_file_location('ordo_editor_service_retry_cov_test', SERVICE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Retry regression: an existing output collection mentioned only by normalize/update_state
# must never become a PRE-STATE dependency. generate.from remains authoritative.
state = {
    'risk_factor_identity': {'alias': 'X'},
    'trigger_logic': {'positive_condition': "status == 'closed'"},
    'functional_test_catalog': {'rows': [{'tc_id': 'OLD'}]},
}
record = {
    'id': 'N_GENERIC_GENERATOR',
    'action': 'AI.GENERATE_TESTS',
    'generate': {'from': ['risk_factor_identity', 'trigger_logic']},
    'normalize': {'functional_test_catalog.rows': '$generated.functional'},
    'update_state': {'functional_test_catalog.rows': '$normalized.functional_test_catalog.rows'},
    'next': 'N_NEXT',
}
proj = mod._project_runtime_state(state, record, 'node', 'enter')
assert 'risk_factor_identity' in proj, proj
assert 'trigger_logic' in proj, proj
assert 'functional_test_catalog' not in proj, proj

# Coverage regression: generic runtime accepts only playbook-declared structural covers.
gate = {
    'id': 'G_GENERIC_COVERAGE',
    'method': 'mechanical',
    'trust_class': 'deterministic',
    'coverage_requirements': ['alpha', 'beta'],
}
base = {
    'catalog_a': {'rows': [
        {'tc_id':'A-01','scenario':'one','short_input':'x','expected_result':'y','covers':['alpha']},
    ]},
    'catalog_b': {'rows': [
        {'tc_id':'B-01','scenario':'two','short_input':'x','expected_result':'y','covers':['alpha']},
    ]},
}
gate['coverage_catalogs'] = ['catalog_a.rows', 'catalog_b.rows']
result = mod._evaluate_test_coverage_gate(gate, base)
assert result and result[0] == 'fail', result
assert 'beta' in result[2].get('missing_coverage', []), result

complete = {k: {'rows': list(v['rows'])} for k,v in base.items()}
complete['catalog_b']['rows'].append({
    'tc_id':'B-02','scenario':'three','short_input':'x','expected_result':'y','covers':['beta']
})
result2 = mod._evaluate_test_coverage_gate(gate, complete)
assert result2 and result2[0] == 'pass', result2

print('COMPILED RETRY + COVERAGE REGRESSION: PASS')
