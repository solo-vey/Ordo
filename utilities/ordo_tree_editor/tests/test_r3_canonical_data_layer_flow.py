from pathlib import Path
from utilities.ordo_tree_editor import editor_service as es


def _package():
    return {
        "resources": {
            "design/editor_projection.yaml": """
schema: ordo.design.editor_projection.v1
playbook: demo
version: 1.0
entry_node: N1
data_layer: authoring/canonical_data_layer.yaml
nodes:
  - id: N1
    reads: [input_a]
    writes: [result_b]
gates:
  - id: G1
    on_pass: N1
    on_fail: N1
outputs: [A_REPORT]
""",
            "authoring/canonical_data_layer.yaml": """
schema: ordo.authoring.canonical_data_layer.v1
playbook: demo
version: 1.0
program_model:
  state:
    schema:
      input_a: null
      result_b: {}
  nodes:
    - id: N1
      title: Transform input
      execution_contract: {owner: deterministic}
  gates:
    - id: G1
      title: Validate
      allowed_from: [N1]
      on_pass: N1
      on_fail: N1
  outputs:
    - id: A_REPORT
      type: markdown
      producer: N1
""",
        }
    }


def test_canonical_data_layer_projection_is_preferred_and_adapted():
    result = es._discover_embedded_authoring_data_flow(_package())
    assert result["available"] is True
    assert result["bundle"]["adapter"] == "canonical_data_layer_projection_v1"
    assert result["bundle"]["data_layer"] == "authoring/canonical_data_layer.yaml"
    nodes = {n["id"]: n for n in result["graph"]["nodes"]}
    assert "N1" in nodes
    assert "VAR::input_a" in nodes
    assert "VAR::result_b" in nodes
    assert "G1" in nodes
    assert "ART::A_REPORT" in nodes
    edges = {(e["from"], e["to"], e["type"]) for e in result["graph"]["edges"]}
    assert ("VAR::input_a", "N1", "read") in edges
    assert ("N1", "VAR::result_b", "write") in edges
    assert ("N1", "ART::A_REPORT", "artifact_input") in edges


def test_canonical_data_layer_adapter_is_ui_only():
    package = _package()
    source = {"entry_node": "N1", "nodes": [{"id": "N1", "next": "END"}], "gates": []}
    baseline = es._build_data_lineage({"resources": {}}, source, {})
    with_layer = es._build_data_lineage(package, source, {})
    assert baseline["nodes"] == with_layer["nodes"]
    assert baseline["edges"] == with_layer["edges"]


def test_canonical_data_layer_variable_data_class_is_exposed_to_ui_graph():
    package = _package()
    package["resources"]["authoring/canonical_data_layer.yaml"] = package["resources"]["authoring/canonical_data_layer.yaml"].replace(
        "      result_b: {}\n",
        "      result_b: {}\n    variable_metadata:\n      input_a: {data_class: business}\n      result_b: {data_class: technical}\n",
    )
    result = es._discover_embedded_authoring_data_flow(package)
    nodes = {n["id"]: n for n in result["graph"]["nodes"]}
    assert nodes["VAR::input_a"]["variable_metadata"]["data_class"] == "business"
    assert nodes["VAR::result_b"]["variable_metadata"]["data_class"] == "technical"
    assert result["summary"]["data_classes"] == {"business": 1, "technical": 1}


def test_unknown_variable_data_class_is_preserved_as_unclassified_not_inferred():
    package = _package()
    package["resources"]["authoring/canonical_data_layer.yaml"] = package["resources"]["authoring/canonical_data_layer.yaml"].replace(
        "      result_b: {}\n",
        "      result_b: {}\n    variable_metadata:\n      input_a: {data_class: domain_magic}\n",
    )
    result = es._discover_embedded_authoring_data_flow(package)
    nodes = {n["id"]: n for n in result["graph"]["nodes"]}
    assert nodes["VAR::input_a"]["variable_metadata"]["data_class"] == "unclassified"
    assert nodes["VAR::input_a"]["variable_metadata"]["declared_data_class"] == "domain_magic"


def test_canonical_state_path_annotations_and_projection_classes_feed_ui_graph():
    package = _package()
    package["resources"]["authoring/canonical_data_layer.yaml"] = package["resources"]["authoring/canonical_data_layer.yaml"].replace(
        "  nodes:\n",
        "state_path_annotations:\n  input_a: {data_class: business}\n  result_b: {data_class: control}\n  nodes:\n",
    )
    package["resources"]["design/editor_projection.yaml"] += "\nstate_path_data_classes:\n  input_a: technical\n  result_b: control\n"
    result = es._discover_embedded_authoring_data_flow(package)
    nodes = {n["id"]: n for n in result["graph"]["nodes"]}
    # Canonical annotation wins over the derived Editor projection.
    assert nodes["VAR::input_a"]["variable_metadata"]["data_class"] == "business"
    assert nodes["VAR::input_a"]["variable_metadata"]["data_class_provenance"] == "canonical_data_layer.state_path_annotations"
    assert nodes["VAR::result_b"]["variable_metadata"]["data_class"] == "control"
    assert result["summary"]["data_classes"] == {"business": 1, "control": 1}


def test_projection_data_class_is_used_when_canonical_annotation_is_absent():
    package = _package()
    package["resources"]["design/editor_projection.yaml"] += "\nstate_path_data_classes:\n  input_a: metadata\n"
    result = es._discover_embedded_authoring_data_flow(package)
    nodes = {n["id"]: n for n in result["graph"]["nodes"]}
    assert nodes["VAR::input_a"]["variable_metadata"]["data_class"] == "metadata"
    assert nodes["VAR::input_a"]["variable_metadata"]["data_class_provenance"] == "editor_projection.state_path_data_classes"
