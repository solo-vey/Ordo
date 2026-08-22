from pathlib import Path
from utilities.ordo_tree_editor import editor_service as es


def test_derived_output_resolves_producer_template_and_bindings():
    source = {
        "nodes": [{
            "id": "N_GEN",
            "action": "DOCUMENT.GENERATE",
            "template": "templates/DOC.md",
            "bindings": "bindings/DOC.yaml",
            "output": "generated_outputs/DOC.md",
            "inputs": ["state.x"],
        }],
        "gates": [],
    }
    package = {"resources": {
        "templates/DOC.md": "# {{ title }}\n",
        "bindings/DOC.yaml": "title: state.x\n",
    }}
    data = es._template_inspector_payload(package, source, "OUT::generated_outputs/DOC.md")
    assert data["entity_type"] == "output"
    assert data["output"] == "generated_outputs/DOC.md"
    assert data["producers"][0]["id"] == "N_GEN"
    assert data["template"]["available"] is True
    assert data["template"]["text"].startswith("# ")
    assert data["bindings"]["available"] is True
    assert data["parameters"]["inputs"] == ["state.x"]


def test_derived_output_without_producer_fails_closed():
    try:
        es._template_inspector_payload({"resources": {}}, {"nodes": [], "gates": []}, "OUT::generated_outputs/MISSING.md")
    except ValueError as exc:
        assert "no inspectable source/producer contract" in str(exc)
    else:
        raise AssertionError("Expected fail-closed output inspector")
