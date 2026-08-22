from __future__ import annotations
import io, json, sys, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import editor_service as es


def _simple_yaml() -> bytes:
    return b"""playbook:
  id: generic-r3-integrated-smoke
  version: 0.1.0
graph_contract:
  entry_node: N_COLLECT_TITLE
  external_terminal_targets: [END_DONE]
state:
  schema:
    title: string
nodes:
  - id: N_COLLECT_TITLE
    question: \"Provide a title.\"
    answer_type: text
    on_answer:
      update_state:
        title: $answer
      next: G_TITLE_PRESENT
  - id: N_CONFIRM
    question: \"Confirm completion.\"
    answer_type: confirmation
    on_answer:
      confirmed:
        next: END_DONE
gates:
  - id: G_TITLE_PRESENT
    trust_class: deterministic
    method: mechanical
    required_inputs: [title]
    on_pass: N_CONFIRM
    on_fail: N_COLLECT_TITLE
"""



def test_direct_yaml_is_compiled_and_verified_internally():
    result=es.parse_playbook_package('simple.yaml',_simple_yaml())
    assert result['input_kind']=='yaml'
    assert result['semantic_plan_status']['valid'] is True
    assert result['semantic_plan_status']['generated'] is True
    assert result['preparation_report']['mode']=='integrated'
    assert result['preparation_report']['validation']['status']=='PASS'


def test_source_zip_without_runtime_plan_is_compiled_internally():
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('program.ordo.yaml',_simple_yaml())
        z.writestr('resources/note.md','# source resource\n')
    result=es.parse_playbook_package('source-only.zip',buf.getvalue())
    assert result['semantic_plan_status']['reason']=='integrated_compile_ok'
    assert result['text_resource_count'] >= 2
    assert result['entry_node']=='N_COLLECT_TITLE'


def test_invalid_yaml_fails_before_execution():
    try:
        es.parse_playbook_package('bad.yaml',b'not: [valid')
    except ValueError as e:
        assert 'could not be parsed' in str(e).lower()
    else:
        raise AssertionError('invalid YAML must fail closed')


def test_direct_yaml_with_external_resources_fails_closed():
    raw=_simple_yaml()+b"\nmetadata:\n  template: templates/doc.md\n"
    try:
        es.parse_playbook_package('resourceful.yaml',raw)
    except ValueError as e:
        assert 'external package resources' in str(e).lower()
        assert 'source zip' in str(e).lower()
    else:
        raise AssertionError('standalone YAML with external resources must fail closed')
