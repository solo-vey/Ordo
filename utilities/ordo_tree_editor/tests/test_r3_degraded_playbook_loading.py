from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import editor_service as es

BAD=b'''playbook:\n  id: degraded-load-smoke\n  version: 0.1.0\ngraph_contract:\n  entry_node: N_START\n  external_terminal_targets: [END]\nstate:\n  schema:\n    protected_value:\n    open_questions: []\nnodes:\n  - id: N_START\n    action: AI.DERIVE_CONTEXT\n    writes: [open_questions]\n    authority_contract:\n      derived_targets:\n        protected_value:\n          sources: [open_questions]\n      open_questions_path: open_questions\n    next: END\n'''

def test_compile_error_keeps_package_inspectable_and_blocks_execute():
    parsed=es.parse_playbook_package('degraded.yaml',BAD)
    assert parsed['load_status']=='degraded'
    assert parsed['source']['playbook']['id']=='degraded-load-smoke'
    assert parsed['capabilities']['inspect_source'] is True
    assert parsed['capabilities']['package_files'] is True
    assert parsed['capabilities']['playbook_settings'] is True
    assert parsed['capabilities']['verification'] is True
    assert parsed['capabilities']['execute'] is False
    assert isinstance(parsed['load_diagnostics'],list) and parsed['load_diagnostics']
    try:
        es._managed_execute_run_start({'package_id':parsed['id'],'session_id':'test'})
    except ValueError as exc:
        assert 'degraded package' in str(exc).lower()
    else:
        raise AssertionError('degraded package execution must remain server-side fail-closed')
