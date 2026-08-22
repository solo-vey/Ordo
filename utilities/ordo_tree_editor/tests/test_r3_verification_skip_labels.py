
import json
from utilities.ordo_tree_editor.verification import runner

def test_skip_kind_explicit_labels():
    cases={
        "needs_runtime_evidence":"Needs runtime evidence",
        "needs_selected_gate":"Needs selected gate",
        "needs_bindings_context":"Needs bindings context",
        "needs_template_context":"Needs template context",
        "needs_tree_module_context":"Needs tree-module context",
        "release_only":"Release-only",
        "toolkit_only":"Toolkit-only",
        "unsafe_one_click":"Not in safe one-click",
    }
    for kind,label in cases.items():
        got_kind,got_label=runner._skip_kind({"skip_kind":kind},"anything")
        assert (got_kind,got_label)==(kind,label)

def test_registry_contextual_checks_have_skip_kind():
    for p in runner.CHECKS_DIR.glob("*.json"):
        item=json.loads(p.read_text())
        if item.get("id") in {
            "validate_state","validate_journey","check_gate","validate_document_fields",
            "validate_provenance","validate_prompt","template_validate","template_registry",
            "template_review","template_diff","tree_module_instance","tree_module_diff",
            "go_no_go","quick_authoring_preflight","portable_bundle_integrity","validate_release"
        }:
            assert item.get("skip_kind")

def test_missing_optional_dependency_label_and_graphviz_descriptor(monkeypatch, tmp_path):
    kind,label=runner._skip_kind({"skip_kind":"missing_optional_dependency"},"dot missing")
    assert (kind,label)==("missing_optional_dependency","Missing optional dependency")
    item=json.loads((runner.CHECKS_DIR/'090_graph_render.json').read_text())
    assert item.get('requires_executables')==['dot']
    assert item.get('skip_kind')=='missing_optional_dependency'
    monkeypatch.setattr(runner.shutil,'which',lambda name: None if name=='dot' else '/usr/bin/'+name)
    source=tmp_path/'program.ordo.yaml'; source.write_text('nodes: []\n')
    applicable,reason=runner._applicable(item,tmp_path,source)
    assert applicable is False
    assert '`dot`' in reason
    assert 'not installed' in reason
