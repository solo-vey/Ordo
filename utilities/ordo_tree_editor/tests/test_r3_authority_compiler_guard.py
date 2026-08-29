from __future__ import annotations
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import editor_service as es


def _yaml(*, derived_writable: bool, clarification_writable: bool=False) -> bytes:
    writes=[]
    if derived_writable:
        writes.append('derived_value')
    if clarification_writable:
        writes.append('target_module')
    writes.append('open_questions')
    writes_yaml='\n'.join(f'    - {w}' for w in writes)
    return f'''playbook:
  id: generic-authority-guard
  version: 0.1.0
graph_contract:
  entry_node: N_DERIVE
  external_terminal_targets: [END_DONE]
state:
  schema:
    source_contract:
    derived_value:
    target_module:
    open_questions: []
nodes:
  - id: N_DERIVE
    action: AI.DERIVE_CONTEXT
    inputs: [source_contract, target_module]
    writes:
{writes_yaml}
    authority_contract:
      derived_targets:
        derived_value:
          sources: [source_contract]
      clarification_only_fields: [target_module]
      open_questions_path: open_questions
    next: END_DONE
'''.encode('utf-8')


def test_authority_derived_target_loads_degraded_but_execution_remains_fail_closed():
    result=es.parse_playbook_package('bad-authority.yaml', _yaml(derived_writable=False))
    assert result['load_status']=='degraded'
    assert result['capabilities']['execute'] is False
    assert result['capabilities']['show_tree'] is True
    assert any('AUTHORITY_DERIVED_TARGET_NOT_WRITABLE' in str(item.get('message') or '') for item in result['load_diagnostics'])


def test_authority_clarification_only_field_loads_degraded_but_execution_remains_fail_closed():
    result=es.parse_playbook_package('bad-authority-clarification.yaml', _yaml(derived_writable=True, clarification_writable=True))
    assert result['load_status']=='degraded'
    assert result['capabilities']['execute'] is False
    assert result['capabilities']['package_files'] is True
    assert any('AUTHORITY_CLARIFICATION_FIELD_WRITABLE' in str(item.get('message') or '') for item in result['load_diagnostics'])


def test_authority_contract_with_grounded_sources_and_disjoint_roles_compiles():
    result=es.parse_playbook_package('good-authority.yaml', _yaml(derived_writable=True))
    assert result['semantic_plan_status']['valid'] is True
    assert result['preparation_report']['validation']['status']=='PASS'
